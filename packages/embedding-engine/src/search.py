from __future__ import annotations

import math
from typing import TYPE_CHECKING

try:
    import faiss
    import numpy as np
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

# Use FAISS when the candidate pool is large enough to benefit from ANN
FAISS_THRESHOLD = 500


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def _norm(v: list[float]) -> float:
    return math.sqrt(sum(x * x for x in v))


def cosine_similarity(a: list[float], b: list[float]) -> float:
    na, nb = _norm(a), _norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return _dot(a, b) / (na * nb)


def _search_cosine(
    query_vector: list[float],
    candidates: list[dict],
    k: int,
    filter_type: str,
) -> list[dict]:
    results = []
    for item in candidates:
        if filter_type != "any" and item.get("chunk_type") != filter_type:
            continue
        score = cosine_similarity(query_vector, item["vector"])
        results.append({**item, "score": round(score, 4)})
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:k]


def _search_faiss(
    query_vector: list[float],
    candidates: list[dict],
    k: int,
    filter_type: str,
) -> list[dict]:
    import numpy as np

    filtered = (
        candidates
        if filter_type == "any"
        else [c for c in candidates if c.get("chunk_type") == filter_type]
    )
    if not filtered:
        return []

    dim = len(query_vector)
    matrix = np.array([c["vector"] for c in filtered], dtype="float32")

    # L2-normalize for cosine similarity via inner product
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1
    matrix /= norms

    index = faiss.IndexFlatIP(dim)
    index.add(matrix)

    q = np.array([query_vector], dtype="float32")
    q /= max(np.linalg.norm(q), 1e-9)

    actual_k = min(k, len(filtered))
    scores, indices = index.search(q, actual_k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < 0:
            continue
        item = filtered[idx]
        results.append({**item, "score": round(float(score), 4)})
    return results


def semantic_search(
    query_vector: list[float],
    candidates: list[dict],
    k: int = 10,
    filter_type: str = "any",
) -> list[dict]:
    """
    Searches candidates semantically. Uses FAISS for large corpora,
    cosine similarity otherwise. Falls back to cosine if FAISS unavailable.

    candidates: list of dicts with keys: chunk_id, vector, content,
                chunk_type, name, path, start_line, end_line
    """
    use_faiss = FAISS_AVAILABLE and len(candidates) >= FAISS_THRESHOLD

    if use_faiss:
        results = _search_faiss(query_vector, candidates, k, filter_type)
    else:
        results = _search_cosine(query_vector, candidates, k, filter_type)

    # Strip internal vector field before returning
    return [
        {key: val for key, val in r.items() if key != "vector"}
        for r in results
    ]
