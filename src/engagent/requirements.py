"""Requirement interpretation (doc 3.2). Rule-based baseline that works offline.

Only extracts what the text states. Anything absent stays None -> reported as unresolved.
An LLM extractor (engagent.llm) can replace this but must return the same EngineeringSpec.
"""
from __future__ import annotations
import re
from .materials import resolve_material
from .schemas import EngineeringSpec, Provenance

_UNIT_MM = {"mm": 1.0, "cm": 10.0, "m": 1000.0}
_NUM = r"(\d+(?:\.\d+)?)"
_LEN = rf"{_NUM}\s*(mm|cm|m)\b"


def _to_mm(val: str, unit: str) -> float:
    return float(val) * _UNIT_MM[unit]


def parse_requirements(text: str) -> EngineeringSpec:
    spec = EngineeringSpec(raw_request=text)
    t = text.lower()

    m = re.search(rf"{_NUM}\s*(?:kg|kilograms?)\b", t)
    if m:
        spec.payload_mass_kg = float(m.group(1))
        spec.provenance["payload_mass_kg"] = Provenance.EXPLICIT

    # lever arm: "300 mm from the wall", "reach of 300 mm", "extends 0.3 m"
    for pat in (rf"{_LEN}\s*(?:from the wall|away|reach|out|long|offset)",
                rf"(?:reach|distance|offset|extends?|projects?|arm length)\D{{0,25}}?{_LEN}"):
        m = re.search(pat, t)
        if m:
            spec.load_offset_mm = _to_mm(m.group(1), m.group(2))
            spec.provenance["load_offset_mm"] = Provenance.EXPLICIT
            break

    m = re.search(rf"(?:deflect\w*|bend\w*|sag\w*)\D{{0,30}}?{_LEN}", t) or \
        re.search(rf"{_LEN}\s*(?:max(?:imum)?\s*)?(?:deflection|bending)", t)
    if m:
        spec.max_deflection_mm = _to_mm(m.group(1), m.group(2))
        spec.provenance["max_deflection_mm"] = Provenance.EXPLICIT

    key, explicit = resolve_material(t)
    if key:
        spec.material_key = key
        spec.provenance["material_key"] = Provenance.EXPLICIT if explicit else Provenance.INFERRED
        if not explicit:
            spec.assumptions.append(f"material grade not stated; {key} inferred from generic name - confirm")

    m = re.search(rf"(?:safety factor|factor of safety|fos)\D{{0,10}}?{_NUM}", t)
    if m:
        spec.safety_factor = float(m.group(1))
        spec.provenance["safety_factor"] = Provenance.EXPLICIT

    objs = []
    if any(w in t for w in ("light", "weight", "mass")):
        objs.append("minimize_mass")
    if any(w in t for w in ("cheap", "cost", "budget")):
        objs.append("minimize_cost")
    if objs:
        spec.objectives = objs

    spec.unresolved = spec.critical_missing()
    return spec
