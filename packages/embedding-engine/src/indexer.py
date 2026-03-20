import hashlib
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

try:
    import tree_sitter_python as tspython
    import tree_sitter_javascript as tsjavascript
    import tree_sitter_typescript as tstypescript
    from tree_sitter import Language, Parser
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False

SUPPORTED_EXTENSIONS = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
}

IGNORED_DIRS = {
    "node_modules", ".git", "__pycache__", ".venv", "venv",
    "dist", "build", ".next", ".cache", "coverage",
}

IGNORED_FILES = {".env", ".env.local", ".env.production"}


@dataclass
class Chunk:
    id: str
    file_id: str
    chunk_type: str  # 'function' | 'class' | 'module'
    name: Optional[str]
    content: str
    start_line: int
    end_line: int
    token_count: int
    metadata: dict = field(default_factory=dict)


def _estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def _sha256(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()


def _get_parser(language: str) -> Optional["Parser"]:
    if not TREE_SITTER_AVAILABLE:
        return None
    try:
        if language == "python":
            lang = Language(tspython.language())
        elif language == "javascript":
            lang = Language(tsjavascript.language())
        elif language == "typescript":
            lang = Language(tstypescript.language_typescript())
        else:
            return None
        parser = Parser(lang)
        return parser
    except Exception:
        return None


def _extract_chunks_tree_sitter(
    source: str, language: str, file_id: str
) -> list[Chunk]:
    parser = _get_parser(language)
    if parser is None:
        return _fallback_chunks(source, file_id)

    tree = parser.parse(source.encode())
    lines = source.splitlines()
    chunks: list[Chunk] = []

    node_types = {
        "python": ["function_definition", "class_definition"],
        "javascript": ["function_declaration", "function_expression",
                       "arrow_function", "class_declaration", "method_definition"],
        "typescript": ["function_declaration", "function_expression",
                       "arrow_function", "class_declaration", "method_definition"],
    }

    target_types = set(node_types.get(language, []))

    def visit(node):
        if node.type in target_types:
            start = node.start_point[0]
            end = node.end_point[0]
            content = "\n".join(lines[start:end + 1])

            name = None
            for child in node.children:
                if child.type in ("identifier", "name"):
                    name = child.text.decode() if child.text else None
                    break

            chunk_type = "class" if "class" in node.type else "function"
            chunks.append(Chunk(
                id=str(uuid.uuid4()),
                file_id=file_id,
                chunk_type=chunk_type,
                name=name,
                content=content,
                start_line=start + 1,
                end_line=end + 1,
                token_count=_estimate_tokens(content),
            ))
            # Don't recurse into found nodes to avoid nested duplicates
            return

        for child in node.children:
            visit(child)

    visit(tree.root_node)

    # Always add a module-level chunk with imports and top-level code
    module_lines = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(("import ", "from ", "require(", "export ")):
            module_lines.append(line)

    if module_lines:
        module_content = "\n".join(module_lines)
        chunks.insert(0, Chunk(
            id=str(uuid.uuid4()),
            file_id=file_id,
            chunk_type="module",
            name=None,
            content=module_content,
            start_line=1,
            end_line=len(lines),
            token_count=_estimate_tokens(module_content),
        ))

    return chunks if chunks else _fallback_chunks(source, file_id)


def _fallback_chunks(source: str, file_id: str) -> list[Chunk]:
    """Simple line-based chunking for unsupported languages."""
    lines = source.splitlines()
    chunk_size = 50
    chunks = []
    for i in range(0, len(lines), chunk_size):
        block = lines[i:i + chunk_size]
        content = "\n".join(block)
        chunks.append(Chunk(
            id=str(uuid.uuid4()),
            file_id=file_id,
            chunk_type="module",
            name=None,
            content=content,
            start_line=i + 1,
            end_line=i + len(block),
            token_count=_estimate_tokens(content),
        ))
    return chunks


def index_file(file_path: Path, project_root: Path) -> tuple[str, str, str, list[Chunk]]:
    """
    Returns (file_id, relative_path, file_hash, chunks).
    """
    relative = str(file_path.relative_to(project_root))
    language = SUPPORTED_EXTENSIONS.get(file_path.suffix.lower(), "unknown")
    source = file_path.read_text(encoding="utf-8", errors="ignore")
    file_hash = _sha256(source)
    file_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{project_root}/{relative}"))

    if language == "unknown" or not source.strip():
        chunks = _fallback_chunks(source, file_id) if source.strip() else []
    else:
        chunks = _extract_chunks_tree_sitter(source, language, file_id)

    return file_id, relative, file_hash, chunks


def discover_files(project_root: Path) -> list[Path]:
    files = []
    for path in project_root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        if path.name in IGNORED_FILES:
            continue
        if path.suffix.lower() in SUPPORTED_EXTENSIONS:
            files.append(path)
    return files
