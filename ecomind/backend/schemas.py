from typing import Any

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    query: str = ""
    environmental_data: dict[str, Any] = Field(default_factory=dict)
    session_id: str = "default"


class Source(BaseModel):
    id: str
    label: str
    title: str
    organization: str
    year: str
    url: str
    topic: str
    excerpt: str


class RecommendationResponse(BaseModel):
    action: str
    why_it_works: str
    impacted_metrics: list[str]
    time_horizon: str
    confidence: str
    citations: list[str]


class AnalyzeResponse(BaseModel):
    session_id: str
    reply: str
    needs_clarification: bool
    clarification_question: str | None = None
    environmental_data: dict[str, Any]
    assessment: str
    key_interactions: list[str]
    recommendations: list[RecommendationResponse]
    impacted_metrics: list[str]
    confidence: str
    sources: list[Source]
    rag_query: str
    llm_used: bool
