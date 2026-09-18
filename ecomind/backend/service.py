"""Orchestrates extraction, transparent reasoning, retrieval, and local Llama."""

from collections import defaultdict
from typing import Any

from backend.extractor import extract_environmental_data
from backend.llama import generate_recommendations
from backend.schemas import AnalyzeResponse, RecommendationResponse, Source
from rag.ingest import load_corpus
from rag.retriever import retrieve_for_assessment
from reasoning.analyzer import analyze

# Each session stores:
#   "profile"          – the accumulated environmental data dict
#   "initial_complete" – True once the first assessment returned without missing fields
#   "original_query"   – the text of the first user message (used for RAG context on follow-ups)
_sessions: dict[str, dict[str, Any]] = defaultdict(dict)


def _source(item: Any, index: int) -> Source:
    return Source(id=item.id, label=f"[{index}]", title=item.title, organization=item.organization, year=item.year, url=item.url, topic=item.topic, excerpt=item.text)


def _clarification(missing: list[str]) -> str:
    shown = ", ".join(missing[:3])
    return f"To assess biodiversity risk, please share your approximate {shown}."


def run_assessment(query: str, supplied_data: dict[str, Any], session_id: str) -> AnalyzeResponse:
    session = _sessions[session_id]
    # On the very first call for this session, "profile" won't exist yet.
    profile: dict[str, Any] = session.setdefault("profile", {})
    is_followup = session.get("initial_complete", False)

    # Merge newly extracted values into the accumulated profile.
    profile.update({key: value for key, value in extract_environmental_data(query).items() if value not in (None, "")})
    profile.update({key: value for key, value in supplied_data.items() if value not in (None, "")})

    # Remember the original query for RAG context on follow-ups.
    if not is_followup:
        session["original_query"] = query

    assessment = analyze(profile)

    # Build the RAG query.  On follow-ups, prepend the original query so retrieval
    # still covers the full environmental context, not just the short follow-up text.
    base_rag = " ".join(str(value) for value in profile.values() if value) + " " + " ".join(assessment.risk_factors)
    if is_followup:
        rag_query = session.get("original_query", "") + " " + query + " " + base_rag
    else:
        rag_query = base_rag

    evidence = retrieve_for_assessment(profile, assessment.risk_factors, limit=5)
    required_sources = {source_id for recommendation in assessment.recommendations for source_id in recommendation.evidence_ids}
    retrieved_ids = {item.id for item in evidence}
    evidence.extend(item for item in load_corpus() if item.id in required_sources and item.id not in retrieved_ids)
    sources = [_source(item, index + 1) for index, item in enumerate(evidence)]
    source_ids = {item.id for item in evidence}
    deterministic = []
    for item in assessment.recommendations[:3]:
        citations = [source_id for source_id in item.evidence_ids if source_id in source_ids]
        deterministic.append(RecommendationResponse(action=item.action, why_it_works=item.why, impacted_metrics=item.impacted_metrics, time_horizon=item.time_horizon, confidence=item.confidence, citations=citations))

    # On follow-ups, never fall back to the clarification flow — the initial
    # assessment already gathered enough context.  Only check missing fields
    # when this is the first (or a still-incomplete initial) interaction.
    if is_followup:
        is_incomplete = False
    else:
        is_incomplete = bool(assessment.missing_fields)
        if not is_incomplete:
            session["initial_complete"] = True

    context = {"environmental_data": profile, "structured_reasoning": assessment.to_dict(), "retrieved_evidence": [{"id": item.id, "title": item.title, "organization": item.organization, "year": item.year, "excerpt": item.text} for item in evidence]}
    llama_output = generate_recommendations(context) if evidence and not is_incomplete else None
    recommendations = deterministic
    llm_used = False
    if llama_output and isinstance(llama_output.get("recommendations"), list):
        safe: list[RecommendationResponse] = []
        seen_categories: set[str] = set()
        for candidate in llama_output["recommendations"][:3]:
            citations = [cite for cite in candidate.get("citations", []) if cite in source_ids]
            category = str(candidate.get("category", "")).strip().lower()
            if citations and category and category not in seen_categories and all(key in candidate for key in ("action", "why_it_works", "impacted_metrics", "time_horizon", "confidence")):
                safe.append(RecommendationResponse(action=str(candidate["action"]), why_it_works=str(candidate["why_it_works"]), impacted_metrics=[str(metric) for metric in candidate["impacted_metrics"]], time_horizon=str(candidate["time_horizon"]), confidence=str(candidate["confidence"]), citations=citations))
                seen_categories.add(category)
        if safe:
            recommendations, llm_used = safe, True

    if is_incomplete:
        reply = _clarification(assessment.missing_fields)
    elif is_followup:
        reply = "I updated the assessment with your additional constraints and the existing environmental context."
    else:
        reply = "I combined your environmental profile, structured relationships, and retrieved scientific evidence into this assessment."

    return AnalyzeResponse(session_id=session_id, reply=reply, needs_clarification=is_incomplete, clarification_question=_clarification(assessment.missing_fields) if is_incomplete else None, environmental_data=dict(profile), assessment="Elevated biodiversity risk" if assessment.risk_factors else "Preliminary biodiversity assessment", key_interactions=assessment.interactions, recommendations=recommendations, impacted_metrics=assessment.impacted_metrics, confidence=assessment.confidence, sources=sources, rag_query=rag_query.strip(), llm_used=llm_used)
