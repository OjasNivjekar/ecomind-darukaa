"""Deterministic multi-metric biodiversity analysis."""

from typing import Any

from models.schemas import Assessment, Recommendation
from reasoning.rules import matching_rules

CORE_FIELDS = ["soil_organic_carbon", "rainfall", "land_use"]
FIELD_LABELS = {"soil_organic_carbon": "soil organic carbon", "rainfall": "rainfall", "land_use": "land use / land cover", "soil_ph": "soil pH", "soil_moisture": "soil moisture", "temperature": "temperature", "crop_vegetation": "crop / vegetation", "region": "region", "pollution_impact": "pollution / human impact"}


def missing_information(data: dict[str, Any]) -> list[str]:
    if data.get("ecosystem_type") == "river":
        aquatic_signals = ("water_level_trend", "flow_regime", "riparian_vegetation", "pollution_impact", "biodiversity_status", "temperature")
        # Multiple qualitative stressors are sufficient to form a defensible river assessment.
        if sum(bool(data.get(signal)) for signal in aquatic_signals) >= 2:
            return []
    return [FIELD_LABELS[key] for key in CORE_FIELDS if data.get(key) in (None, "")]


def analyze(data: dict[str, Any]) -> Assessment:
    rules = matching_rules(data)
    # Prefer the most multi-variable relationships in the user-facing assessment.
    ranked_rules = sorted(rules, key=lambda rule: (len(rule["conditions"]), bool(rule.get("chain"))), reverse=True)
    missing = missing_information(data)
    metrics = list(dict.fromkeys(metric for rule in rules for metric in rule["metrics"]))
    recommendations: list[Recommendation] = []
    selected_categories: set[str] = set()
    for rule in ranked_rules:
        category = rule.get("category", rule["id"])
        if category in selected_categories:
            continue
        selected_categories.add(category)
        horizon = "Short–medium term" if any(key in rule["id"] for key in ("pollution", "heat", "moisture", "rain")) else "Medium–long term"
        confidence = "High" if len(rule["conditions"]) >= 2 else "Medium"
        recommendations.append(Recommendation(action=rule["intervention"], why=rule["risk"], impacted_metrics=rule["metrics"], time_horizon=horizon, evidence_ids=rule["sources"], confidence=confidence))
        if len(recommendations) == 3:
            break
    if not rules:
        recommendations.append(Recommendation(action="Protect and diversify existing native habitat.", why="The available values do not trigger a specific relationship yet; habitat diversity and connectivity remain useful biodiversity indicators.", impacted_metrics=["Habitat quality", "Species resources", "Habitat connectivity"], time_horizon="Medium–long term", evidence_ids=["ipbes_assessment"], confidence="Low"))
    confidence = "High" if len(rules) >= 3 and not missing else "Medium" if rules else "Low"
    interactions: list[str] = []
    interaction_categories: set[str] = set()
    for rule in ranked_rules:
        category = rule.get("category", rule["id"])
        if category in interaction_categories:
            continue
        interaction_categories.add(category)
        interactions.append(rule.get("chain", rule["risk"]))
        if len(interactions) == 3:
            break
    return Assessment(risk_factors=[rule["risk"] for rule in rules], interactions=interactions, impacted_metrics=metrics, recommendations=recommendations, missing_fields=missing, confidence=confidence)
