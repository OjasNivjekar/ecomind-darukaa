"""Conservative extraction of environmental values from a user message."""

import json
import re
from typing import Any


def extract_environmental_data(query: str) -> dict[str, Any]:
    query = query.strip()
    if query.startswith("{"):
        try:
            value = json.loads(query)
            return value if isinstance(value, dict) else {}
        except json.JSONDecodeError:
            return {}
    text = query.lower()
    values: dict[str, Any] = {}
    number_patterns = {
        "soil_organic_carbon": r"(?:soc|soil organic carbon)\s*(?:=|:|is|of)?\s*(\d+(?:\.\d+)?)\s*%?",
        "soil_ph": r"(?:soil )?p\s*h\s*(?:=|:|is|of)?\s*(\d+(?:\.\d+)?)",
    }
    for field, pattern in number_patterns.items():
        match = re.search(pattern, text)
        if match:
            values[field] = float(match.group(1))
    rainfall_patterns = (
        r"(?:annual )?rainfall\s+(?:is\s+)?(?:around\s+|of\s+)?(\d+(?:\.\d+)?)\s*mm",
        r"(\d+(?:\.\d+)?)\s*mm\s+(?:annual )?rainfall",
    )
    for pattern in rainfall_patterns:
        match = re.search(pattern, text)
        if match:
            values["rainfall_amount_mm"] = float(match.group(1))
            # A measured amount is valid input, but is not forced into a climate category without regional context.
            values["rainfall"] = "reported"
            break
    temperature_match = re.search(r"(?:temperature(?:s)?|temp(?:eratures)?)\D{0,18}(\d+(?:\.\d+)?)\s*(?:°\s*c|celsius|c)?", text)
    if temperature_match:
        celsius = float(temperature_match.group(1))
        values["temperature"] = "high" if celsius >= 30 else "low" if celsius <= 10 else "moderate"
    for field, expression in {
        "rainfall": r"rainfall\s*(?:is|=|:)?\s*(low|moderate|high)",
        "soil_moisture": r"(?:soil )?moisture\s*(?:is|=|:)?\s*(low|moderate|high)",
        "temperature": r"temperature\s*(?:is|=|:)?\s*(low|moderate|high)",
        "pollution_impact": r"pollution(?: impact)?\s*(?:is|=|:)?\s*(low|moderate|high)",
        "habitat_diversity": r"habitat diversity\s*(?:is|=|:)?\s*(low|moderate|high)",
        "habitat_connectivity": r"habitat connectivity\s*(?:is|=|:)?\s*(low|moderate|high)",
        "biodiversity_status": r"biodiversity\s*(?:is|=|:)?\s*(low|moderate|high|declining)",
    }.items():
        match = re.search(expression, text)
        if match:
            values[field] = "low" if match.group(1) == "declining" else match.group(1)
    for field, options in {
        "land_use": ["monoculture", "intensive agriculture", "deforestation", "bare land", "urban", "mixed agriculture", "forest"],
        "region": ["semi-arid", "arid", "temperate", "tropical"],
    }.items():
        for option in options:
            if option in text:
                values[field] = option
                break
    if re.search(r"\b(?:\d+(?:\.\d+)?[-\s]hectare\s+)?(?:[a-z-]+\s+)?orchard\b", text):
        values["land_use"] = "orchard"
    if "river" in text or "riparian" in text or "aquatic" in text:
        values["ecosystem_type"] = "river"
        values["land_use"] = "river"
    if "declining water levels" in text or "water levels during summer" in text:
        values["water_level_trend"] = "declining"
        values["water_availability"] = "limited"
    if "intermittent flow" in text or "flow is now intermittent" in text:
        values["flow_regime"] = "intermittent"
        values["habitat_connectivity"] = "low"
    if "riparian vegetation has been cleared" in text or "riparian vegetation cleared" in text:
        values["riparian_vegetation"] = "cleared"
        values["habitat_diversity"] = "low"
    if "exposed soil along the banks" in text or "exposed riverbanks" in text:
        values["bank_exposure"] = "high"
    if "agricultural runoff" in text or "farm runoff" in text:
        values["pollution_impact"] = "high"
        values["runoff_pressure"] = "agricultural"
    if re.search(r"fewer\s+(?:fish|frogs|aquatic insects)|fewer fish.*aquatic insects", text):
        values["biodiversity_status"] = "low"
    if "construction cannot be completely stopped" in text or "development is already approved" in text:
        values["construction_constraint"] = "active"
    if "bare soil between rows" in text or "bare ground between rows" in text:
        values["bare_soil_between_rows"] = True
    if "irrigation water is limited" in text or "limited irrigation" in text or "water is limited" in text:
        values["water_availability"] = "limited"
    if "moisture is moderate but declining" in text or "soil moisture is moderate but declining" in text:
        values["seasonal_moisture_trend"] = "declining"
    if "very little vegetation" in text or "little surrounding vegetation" in text or "very few flowering plants" in text or "no vegetation along the field boundaries" in text:
        values["habitat_diversity"] = "low"
    if "biodiversity has been declining" in text or "biodiversity is declining" in text or "biodiversity declining" in text:
        values["biodiversity_status"] = "low"
    for crop in ("wheat", "maize", "rice", "soy", "cotton", "mango", "native vegetation"):
        if crop in text:
            values["crop_vegetation"] = crop
    return values
