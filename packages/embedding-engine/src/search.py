from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import sqlite3


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def _norm(v: list[float]) -> float:
    return math.sqrt(sum(x * x for x in v))


def cosine_similarity(a: list[float], b: list[float]) -> float:
    na, nb = _norm(a), _norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return _dot(a, b) / (na * nb)


def semantic_search(
    query_vector: list[float],
    candidates: list[dict],
    k: int = 10,
    filter_type: str = "any",
) -> list[dict]:
    """
    candidates: list of dicts with keys: chunk_id, vector, content, chunk_type, name, path, start_line, end_line
    Returns top-k results sorted by cosine similarity, highest first.
    """
    results = []
    for item in candidates:
        if filter_type != "any" and item.get("chunk_type") != filter_type:
            continue
        score = cosine_similarity(query_vector, item["vector"])
        results.append({
            "chunk_id": item["chunk_id"],
            "score": round(score, 4),
            "content": item["content"],
            "chunk_type": item["chunk_type"],
            "name": item["name"],
            "path": item["path"],
            "start_line": item["start_line"],
            "end_line": item["end_line"],
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:k]
