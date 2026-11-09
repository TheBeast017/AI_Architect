"""Optional LLM requirement extractor (doc 7.1). UNTESTED against the live API (plan.md Phase 6).

The LLM only fills the schema; it must leave unknown fields null. Output is validated by pydantic and
provenance is forced to INFERRED so a human sees it. Numbers are never computed by the LLM.
Install: pip install -e ".[llm]" ; set ANTHROPIC_API_KEY. Model via ENGAGENT_LLM_MODEL.
"""
from __future__ import annotations
import json, os
from ..requirements import parse_requirements
from ..schemas import EngineeringSpec, Provenance

SYSTEM = ("Extract a mechanical-design specification from the user's request. Return ONLY JSON with keys: "
          "payload_mass_kg, load_offset_mm, max_deflection_mm, material_key, safety_factor, dynamic_factor, "
          "max_width_mm, max_height_mm, min_wall_mm. Units: kg, mm. Use null for anything not stated. "
          "NEVER guess or invent values. material_key must be one of AL6061-T6, AL7075-T6, STEEL-A36, TI-6AL-4V or null.")


def extract_spec(text: str, model: str | None = None) -> EngineeringSpec:
    import anthropic  # lazy import
    client = anthropic.Anthropic()
    msg = client.messages.create(model=model or os.getenv("ENGAGENT_LLM_MODEL", "claude-sonnet-5-5"),
                                 max_tokens=500, system=SYSTEM, messages=[{"role": "user", "content": text}])
    raw = "".join(b.text for b in msg.content if b.type == "text").strip().strip("`")
    raw = raw[raw.find("{"): raw.rfind("}") + 1]
    data = json.loads(raw)
    spec = parse_requirements(text)          # keep rule-based values as the cross-check baseline
    for k, v in data.items():
        if v is not None and hasattr(spec, k) and getattr(spec, k) is None:
            setattr(spec, k, v)
            spec.provenance[k] = Provenance.INFERRED
    spec.unresolved = spec.critical_missing()
    return spec
