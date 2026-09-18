"""Local retrieval with a dependable lexical fallback and optional embeddings."""

import re
from collections import Counter

from models.schemas import Evidence
from rag.ingest import load_corpus


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z]{3,}", text.lower()))


def retrieve(query: str, limit: int = 4) -> list[Evidence]:
    """Rank local evidence by token overlap; works offline and without model downloads."""
    terms = _tokens(query)
    ranked: list[Evidence] = []
    for item in load_corpus():
        document_terms = _tokens(f"{item.title} {item.topic} {item.text}")
        item.score = len(terms & document_terms) / max(len(terms), 1)
        ranked.append(item)
    return sorted(ranked, key=lambda item: item.score, reverse=True)[:limit]


def retrieve_for_assessment(data: dict, risks: list[str], limit: int = 4) -> list[Evidence]:
    values = " ".join(str(value) for value in data.values() if value)
    return retrieve(f"{values} {' '.join(risks)}", limit)


def evidence_lookup(items: list[Evidence]) -> dict[str, Evidence]:
    return {item.id: item for item in items + load_corpus()}
