"""Load EcoMind's small curated, local evidence corpus."""

import json
from pathlib import Path

from models.schemas import Evidence

CORPUS_PATH = Path(__file__).parents[1] / "data" / "documents" / "curated_evidence.json"


def load_corpus() -> list[Evidence]:
    records = json.loads(CORPUS_PATH.read_text(encoding="utf-8"))
    return [Evidence(**record) for record in records]
