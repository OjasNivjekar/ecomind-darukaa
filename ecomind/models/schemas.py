"""Small, serializable data models used across EcoMind."""

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class Evidence:
    id: str
    title: str
    organization: str
    year: str
    topic: str
    url: str
    text: str
    score: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Recommendation:
    action: str
    why: str
    impacted_metrics: list[str]
    time_horizon: str
    evidence_ids: list[str]
    confidence: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Assessment:
    risk_factors: list[str] = field(default_factory=list)
    interactions: list[str] = field(default_factory=list)
    impacted_metrics: list[str] = field(default_factory=list)
    recommendations: list[Recommendation] = field(default_factory=list)
    missing_fields: list[str] = field(default_factory=list)
    confidence: str = "Low"

    def to_dict(self) -> dict[str, Any]:
        return {**asdict(self), "recommendations": [item.to_dict() for item in self.recommendations]}
