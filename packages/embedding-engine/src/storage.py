import sqlite3
import json
import struct
from pathlib import Path
from typing import Optional


def open_db(db_path: str) -> sqlite3.Connection:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    _apply_schema(conn)
    return conn


def _apply_schema(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS projects (
            id          TEXT PRIMARY KEY,
            name        TEXT NOT NULL,
            root_path   TEXT NOT NULL UNIQUE,
            config      TEXT,
            indexed_at  INTEGER,
            created_at  INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS files (
            id            TEXT PRIMARY KEY,
            project_id    TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            path          TEXT NOT NULL,
            language      TEXT,
            hash          TEXT NOT NULL,
            last_modified INTEGER,
            UNIQUE(project_id, path)
        );

        CREATE TABLE IF NOT EXISTS chunks (
            id          TEXT PRIMARY KEY,
            file_id     TEXT NOT NULL REFERENCES files(id) ON DELETE CASCADE,
            chunk_type  TEXT NOT NULL,
            name        TEXT,
            content     TEXT NOT NULL,
            start_line  INTEGER NOT NULL,
            end_line    INTEGER NOT NULL,
            token_count INTEGER NOT NULL,
            metadata    TEXT
        );

        CREATE TABLE IF NOT EXISTS embeddings (
            chunk_id   TEXT PRIMARY KEY REFERENCES chunks(id) ON DELETE CASCADE,
            model      TEXT NOT NULL,
            vector     BLOB NOT NULL,
            dims       INTEGER NOT NULL,
            created_at INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS graph_edges (
            id         TEXT PRIMARY KEY,
            project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            from_chunk TEXT NOT NULL REFERENCES chunks(id) ON DELETE CASCADE,
            to_chunk   TEXT NOT NULL REFERENCES chunks(id) ON DELETE CASCADE,
            edge_type  TEXT NOT NULL,
            weight     REAL DEFAULT 1.0
        );

        CREATE TABLE IF NOT EXISTS memories (
            id              TEXT PRIMARY KEY,
            project_id      TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            session_id      TEXT,
            memory_type     TEXT NOT NULL,
            content         TEXT NOT NULL,
            relevance_score REAL DEFAULT 1.0,
            created_at      INTEGER NOT NULL,
            expires_at      INTEGER
        );

        CREATE INDEX IF NOT EXISTS idx_chunks_file      ON chunks(file_id);
        CREATE INDEX IF NOT EXISTS idx_files_project    ON files(project_id);
        CREATE INDEX IF NOT EXISTS idx_edges_from       ON graph_edges(from_chunk);
        CREATE INDEX IF NOT EXISTS idx_edges_to         ON graph_edges(to_chunk);
        CREATE INDEX IF NOT EXISTS idx_memories_project ON memories(project_id, created_at DESC);
    """)
    conn.commit()


def vector_to_blob(vector: list[float]) -> bytes:
    return struct.pack(f"{len(vector)}f", *vector)


def blob_to_vector(blob: bytes) -> list[float]:
    n = len(blob) // 4
    return list(struct.unpack(f"{n}f", blob))


def upsert_project(conn: sqlite3.Connection, project_id: str, name: str, root_path: str) -> None:
    import time
    conn.execute("""
        INSERT INTO projects (id, name, root_path, created_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(root_path) DO UPDATE SET name=excluded.name
    """, (project_id, name, root_path, int(time.time())))
    conn.commit()


def upsert_file(
    conn: sqlite3.Connection,
    file_id: str,
    project_id: str,
    path: str,
    language: str,
    file_hash: str,
    last_modified: int,
) -> None:
    conn.execute("""
        INSERT INTO files (id, project_id, path, language, hash, last_modified)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(project_id, path) DO UPDATE SET
            hash=excluded.hash,
            last_modified=excluded.last_modified,
            language=excluded.language
    """, (file_id, project_id, path, language, file_hash, last_modified))
    conn.commit()


def get_file_hash(conn: sqlite3.Connection, project_id: str, path: str) -> Optional[str]:
    row = conn.execute(
        "SELECT hash FROM files WHERE project_id=? AND path=?", (project_id, path)
    ).fetchone()
    return row["hash"] if row else None


def delete_file_chunks(conn: sqlite3.Connection, file_id: str) -> None:
    conn.execute("DELETE FROM chunks WHERE file_id=?", (file_id,))
    conn.commit()


def insert_chunk(
    conn: sqlite3.Connection,
    chunk_id: str,
    file_id: str,
    chunk_type: str,
    name: Optional[str],
    content: str,
    start_line: int,
    end_line: int,
    token_count: int,
    metadata: Optional[dict] = None,
) -> None:
    conn.execute("""
        INSERT INTO chunks (id, file_id, chunk_type, name, content, start_line, end_line, token_count, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        chunk_id, file_id, chunk_type, name, content,
        start_line, end_line, token_count,
        json.dumps(metadata) if metadata else None,
    ))


def insert_embedding(
    conn: sqlite3.Connection,
    chunk_id: str,
    model: str,
    vector: list[float],
) -> None:
    import time
    conn.execute("""
        INSERT OR REPLACE INTO embeddings (chunk_id, model, vector, dims, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (chunk_id, model, vector_to_blob(vector), len(vector), int(time.time())))


def get_all_embeddings(
    conn: sqlite3.Connection, project_id: str
) -> list[dict]:
    rows = conn.execute("""
        SELECT e.chunk_id, e.vector, c.content, c.chunk_type, c.name,
               c.start_line, c.end_line, f.path
        FROM embeddings e
        JOIN chunks c ON c.id = e.chunk_id
        JOIN files f ON f.id = c.file_id
        WHERE f.project_id = ?
    """, (project_id,)).fetchall()
    return [
        {
            "chunk_id": r["chunk_id"],
            "vector": blob_to_vector(r["vector"]),
            "content": r["content"],
            "chunk_type": r["chunk_type"],
            "name": r["name"],
            "start_line": r["start_line"],
            "end_line": r["end_line"],
            "path": r["path"],
        }
        for r in rows
    ]
