"""Gemini-based requirement extractor (replaces anthropic_extractor.py).

Reads GEMINI_API_KEY from the environment (set it in a .env file or your shell).
Model is configurable via ENGAGENT_LLM_MODEL env var (defaults to gemini-2.0-flash).

Install the extra:  pip install -e ".[llm]"
Set your key:       set GEMINI_API_KEY=your_key_here   (Windows)
                    export GEMINI_API_KEY=your_key_here (Linux/Mac)
"""
from __future__ import annotations
import json
import os

from ..requirements import parse_requirements
from ..schemas import EngineeringSpec, Provenance

SYSTEM_PROMPT = (
    "Extract a mechanical-design specification from the user's request. "
    "Return ONLY a valid JSON object with these keys: "
    "payload_mass_kg, load_offset_mm, max_deflection_mm, material_key, "
    "safety_factor, dynamic_factor, max_width_mm, max_height_mm, min_wall_mm. "
    "Units: kg for mass, mm for all lengths. "
    "Use null for anything not explicitly stated. "
    "NEVER guess or invent values. "
    "material_key must be one of: AL6061-T6, AL7075-T6, STEEL-A36, TI-6AL-4V, or null."
)


def extract_spec(text: str, model: str | None = None) -> EngineeringSpec:
    """Use Gemini to extract an EngineeringSpec from free-text.

    Falls back gracefully to the rule-based parser if the API call fails
    or returns unparseable JSON.
    """
    try:
        from google import genai  # lazy import — only needed for LLM path
        from google.genai import types
    except ImportError as e:
        raise ImportError(
            "google-genai is not installed. Run: pip install -e '.[llm]'"
        ) from e

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GEMINI_API_KEY environment variable is not set. "
            "Get a free key at https://aistudio.google.com/apikey"
        )

    model_name = model or os.getenv("ENGAGENT_LLM_MODEL", "gemini-2.0-flash")

    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model=model_name,
        contents=text,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.0,          # deterministic — we want exact JSON
            max_output_tokens=512,
        ),
    )

    raw = response.text.strip()

    # Strip markdown code fences if Gemini wraps in ```json ... ```
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    # Extract the JSON object
    start, end = raw.find("{"), raw.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"No JSON object found in Gemini response: {raw!r}")
    data = json.loads(raw[start: end + 1])

    # Merge onto rule-based spec: LLM only fills fields the regex missed
    spec = parse_requirements(text)
    for key, val in data.items():
        if val is not None and hasattr(spec, key) and getattr(spec, key) is None:
            setattr(spec, key, val)
            spec.provenance[key] = Provenance.INFERRED

    spec.unresolved = spec.critical_missing()
    return spec
