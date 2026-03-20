from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

# Silence unnecessary warnings from transformers/torch
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

try:
    from sentence_transformers import SentenceTransformer
    ST_AVAILABLE = True
except ImportError:
    ST_AVAILABLE = False

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer as STModel

DEFAULT_MODEL = "all-MiniLM-L6-v2"
MODELS_DIR = Path.home() / ".context-pilot" / "models"

_model_cache: dict[str, "STModel"] = {}


def load_model(model_name: str = DEFAULT_MODEL) -> "STModel":
    if model_name in _model_cache:
        return _model_cache[model_name]

    if not ST_AVAILABLE:
        raise RuntimeError(
            "sentence-transformers is not installed. "
            "Run: pip install sentence-transformers"
        )

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    model = SentenceTransformer(model_name, cache_folder=str(MODELS_DIR))
    _model_cache[model_name] = model
    return model


def embed_texts(texts: list[str], model_name: str = DEFAULT_MODEL) -> list[list[float]]:
    """Embed a batch of texts. Returns list of float vectors."""
    model = load_model(model_name)
    vectors = model.encode(texts, batch_size=32, show_progress_bar=False, convert_to_numpy=True)
    return [v.tolist() for v in vectors]


def embed_single(text: str, model_name: str = DEFAULT_MODEL) -> list[float]:
    return embed_texts([text], model_name)[0]
