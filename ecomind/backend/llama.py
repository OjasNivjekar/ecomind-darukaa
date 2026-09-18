"""Cloud Llama adapter using Groq."""

import json
import os
from typing import Any

import requests


def generate_recommendations(context: dict[str, Any]) -> dict[str, Any] | None:
    """Ask hosted Llama for constrained JSON."""

    system = """You are EcoMind, a biodiversity intelligence advisor.

The structured_reasoning object is the approved causal reasoning layer and retrieved_evidence is the only scientific grounding.

Return JSON only with keys:
assessment, recommendations, confidence

Return no more than three meaningfully different recommendations.

Each recommendation must contain:
category, action, why_it_works, impacted_metrics, time_horizon, confidence, citations.

Use distinct categories such as soil_water, crop_diversification, and habitat_restoration when supported.

For each recommendation, cite only evidence IDs supplied in retrieved_evidence and only when that evidence supports the action.

If scientific support is insufficient, omit the recommendation.

Never invent sources, statistics, percentages, measurements, relationships, or benefits.

Do not give generic sustainability advice.

Explain a causal chain across at least three supplied environmental variables whenever the structured reasoning supports it.

Keep explanations concise."""

    try:
        api_key = os.getenv("GROQ_API_KEY")

        # Diagnostic: confirms the key exists without exposing it.
        print(
            f"GROQ_API_KEY present: {bool(api_key)}, "
            f"model: {os.getenv('LLAMA_MODEL', 'openai/gpt-oss-20b')}",
            flush=True,
        )

        if not api_key:
            print(
                "LLAMA/GROQ ERROR: GROQ_API_KEY is missing",
                flush=True,
            )
            return None

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": os.getenv(
                    "LLAMA_MODEL",
                    "llama-3.1-8b-instant"
                ),
                "messages": [
                    {
                        "role": "system",
                        "content": system,
                    },
                    {
                        "role": "user",
                        "content": json.dumps(context),
                    },
                ],
                "temperature": 0.1,
                "response_format": {
                    "type": "json_object"
                },
            },
            timeout=float(
                os.getenv("LLAMA_TIMEOUT_SECONDS", "45")
            ),
        )

        response.raise_for_status()

        data = response.json()

        content = data["choices"][0]["message"]["content"]

        result = json.loads(content)

        print(
            "LLAMA/GROQ: response received successfully",
            flush=True,
        )

        return result if isinstance(result, dict) else None

    except Exception as e:
        print(
            f"LLAMA/GROQ ERROR: {type(e).__name__}: {e}",
            flush=True,
        )
        return None