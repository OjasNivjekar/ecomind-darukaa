"""Conservative extraction of environmental values from a user message."""

import json
import re
from typing import Any


def extract_environmental_data(query: str) -> dict[str, Any]:
    query = query.strip()

    # Allow structured JSON input
    if query.startswith("{"):
        try:
            value = json.loads(query)
            return value if isinstance(value, dict) else {}
        except json.JSONDecodeError:
            return {}

    text = query.lower()
    values: dict[str, Any] = {}

    # ---------------------------------------------------------
    # Numeric environmental values
    # ---------------------------------------------------------
    number_patterns = {
        "soil_organic_carbon": (
            r"(?:soc|soil organic carbon|organic carbon)\s*"
            r"(?:=|:|is|of)?\s*"
            r"(\d+(?:\.\d+)?)\s*%?"
        ),
        "soil_ph": (
            r"(?:soil )?p\s*h\s*"
            r"(?:=|:|is|of)?\s*"
            r"(\d+(?:\.\d+)?)"
        ),
    }

    for field, pattern in number_patterns.items():
        match = re.search(pattern, text)
        if match:
            values[field] = float(match.group(1))

    # ---------------------------------------------------------
    # Rainfall
    # ---------------------------------------------------------
    rainfall_patterns = (
        r"(?:annual )?rainfall\s+"
        r"(?:is\s+)?(?:around\s+|of\s+)?"
        r"(\d+(?:\.\d+)?)\s*mm",

        r"(\d+(?:\.\d+)?)\s*mm\s+"
        r"(?:annual )?rainfall",
    )

    for pattern in rainfall_patterns:
        match = re.search(pattern, text)
        if match:
            values["rainfall_amount_mm"] = float(match.group(1))
            values["rainfall"] = "reported"
            break

    # ---------------------------------------------------------
    # Temperature
    # ---------------------------------------------------------
    temperature_match = re.search(
        r"(?:temperature(?:s)?|temp(?:eratures)?)"
        r"\D{0,18}"
        r"(\d+(?:\.\d+)?)"
        r"\s*(?:°\s*c|celsius|c)?",
        text,
    )

    if temperature_match:
        celsius = float(temperature_match.group(1))
        values["temperature"] = (
            "high"
            if celsius >= 30
            else "low"
            if celsius <= 10
            else "moderate"
        )

    # ---------------------------------------------------------
    # Explicit categorical values
    # ---------------------------------------------------------
    categorical_patterns = {
        "rainfall": (
            r"rainfall\s*(?:is|=|:)?\s*"
            r"(low|moderate|high)"
        ),
        "soil_moisture": (
            r"(?:soil )?moisture\s*(?:is|=|:)?\s*"
            r"(low|moderate|high)"
        ),
        "temperature": (
            r"temperature\s*(?:is|=|:)?\s*"
            r"(low|moderate|high)"
        ),
        "pollution_impact": (
            r"pollution(?: impact)?\s*(?:is|=|:)?\s*"
            r"(low|moderate|high)"
        ),
        "habitat_diversity": (
            r"habitat diversity\s*(?:is|=|:)?\s*"
            r"(low|moderate|high)"
        ),
        "habitat_connectivity": (
            r"habitat connectivity\s*(?:is|=|:)?\s*"
            r"(low|moderate|high)"
        ),
        "biodiversity_status": (
            r"biodiversity\s*(?:is|=|:)?\s*"
            r"(low|moderate|high|declining)"
        ),
    }

    for field, expression in categorical_patterns.items():
        match = re.search(expression, text)
        if match:
            values[field] = (
                "low"
                if match.group(1) == "declining"
                else match.group(1)
            )

    # ---------------------------------------------------------
    # Land use
    #
    # Important:
    # "farming" is land use.
    # "bare soil" is a land-cover condition.
    # They should not overwrite each other.
    # ---------------------------------------------------------
    land_use_options = [
        "monoculture",
        "intensive agriculture",
        "deforestation",
        "urban",
        "mixed agriculture",
        "forest",
        "farming",
        "farm",
        "cropland",
        "crop land",
        "agricultural land",
        "agriculture",
    ]

    for option in land_use_options:
        if option in text:
            if option in {
                "farming",
                "farm",
                "cropland",
                "crop land",
                "agricultural land",
                "agriculture",
            }:
                values["land_use"] = "farming"
            else:
                values["land_use"] = option
            break

    # ---------------------------------------------------------
    # Region
    # ---------------------------------------------------------
    for option in [
        "semi-arid",
        "arid",
        "temperate",
        "tropical",
    ]:
        if option in text:
            values["region"] = option
            break

    # ---------------------------------------------------------
    # Orchard
    # ---------------------------------------------------------
    if re.search(
        r"\b(?:\d+(?:\.\d+)?[-\s]hectare\s+)?"
        r"(?:[a-z-]+\s+)?orchard\b",
        text,
    ):
        values["land_use"] = "orchard"

    # ---------------------------------------------------------
    # Farm / field vegetation and bare soil
    # ---------------------------------------------------------
    if (
        "very little vegetation" in text
        or "little surrounding vegetation" in text
        or "very few flowering plants" in text
        or "no vegetation along the field boundaries" in text
        or "limited vegetation" in text
        or "little vegetation" in text
    ):
        values["habitat_diversity"] = "low"

    if (
        "bare soil" in text
        or "mostly bare soil" in text
        or "bare ground" in text
        or "mostly bare" in text
    ):
        values["bare_soil_between_rows"] = True

    # ---------------------------------------------------------
    # River / aquatic ecosystem
    # ---------------------------------------------------------
    if (
        "river" in text
        or "riparian" in text
        or "aquatic" in text
    ):
        values["ecosystem_type"] = "river"
        values["land_use"] = "river"

    # ---------------------------------------------------------
    # Water availability
    # ---------------------------------------------------------
    if (
        "declining water levels" in text
        or "water levels during summer" in text
    ):
        values["water_level_trend"] = "declining"
        values["water_availability"] = "limited"

    if (
        "irrigation water is limited" in text
        or "limited irrigation" in text
        or "water is limited" in text
    ):
        values["water_availability"] = "limited"

    # ---------------------------------------------------------
    # Flow / riparian conditions
    # ---------------------------------------------------------
    if (
        "intermittent flow" in text
        or "flow is now intermittent" in text
    ):
        values["flow_regime"] = "intermittent"
        values["habitat_connectivity"] = "low"

    if (
        "riparian vegetation has been cleared" in text
        or "riparian vegetation cleared" in text
    ):
        values["riparian_vegetation"] = "cleared"
        values["habitat_diversity"] = "low"

    if (
        "exposed soil along the banks" in text
        or "exposed riverbanks" in text
    ):
        values["bank_exposure"] = "high"

    # ---------------------------------------------------------
    # Pollution / runoff
    # ---------------------------------------------------------
    if (
        "agricultural runoff" in text
        or "farm runoff" in text
    ):
        values["pollution_impact"] = "high"
        values["runoff_pressure"] = "agricultural"

    # ---------------------------------------------------------
    # Biodiversity indicators
    # ---------------------------------------------------------
    if re.search(
        r"fewer\s+(?:fish|frogs|aquatic insects)"
        r"|fewer fish.*aquatic insects",
        text,
    ):
        values["biodiversity_status"] = "low"

    if (
        "biodiversity has been declining" in text
        or "biodiversity is declining" in text
        or "biodiversity declining" in text
        or "bee populations have declined" in text
        or "butterfly populations have declined" in text
        or "fewer bees" in text
        or "fewer butterflies" in text
    ):
        values["biodiversity_status"] = "low"
        values["pollinator_decline"] = True

    # ---------------------------------------------------------
    # Construction constraints
    # ---------------------------------------------------------
    if (
        "construction cannot be completely stopped" in text
        or "development is already approved" in text
    ):
        values["construction_constraint"] = "active"

    # ---------------------------------------------------------
    # Moisture trends
    # ---------------------------------------------------------
    if (
        "moisture is moderate but declining" in text
        or "soil moisture is moderate but declining" in text
    ):
        values["seasonal_moisture_trend"] = "declining"

    # ---------------------------------------------------------
    # Crops / vegetation
    # ---------------------------------------------------------
    for crop in (
        "wheat",
        "maize",
        "rice",
        "soy",
        "cotton",
        "mango",
        "native vegetation",
    ):
        if crop in text:
            values["crop_vegetation"] = crop

    return values