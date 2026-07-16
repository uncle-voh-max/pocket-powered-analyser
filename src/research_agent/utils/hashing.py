from __future__ import annotations

import hashlib


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def url_hash(url: str) -> str:
    return hashlib.md5(url.encode("utf-8")).hexdigest()


def title_similarity(a: str, b: str) -> float:
    """Jaccard similarity on word sets."""
    words_a = set(a.lower().split())
    words_b = set(b.lower().split())
    if not words_a or not words_b:
        return 0.0
    intersection = words_a & words_b
    union = words_a | words_b
    return len(intersection) / len(union)
