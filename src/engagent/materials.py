"""Material library.

Values are typical handbook numbers for a *first prototype*. They are NOT design
allowables. Verify against your supplier / standard before relying on them
(see doc section 5.2: a label like "aluminum" is not a material model).
Units: MPa, kg/m^3. price_per_kg is ILLUSTRATIVE only.
"""
from __future__ import annotations
from pydantic import BaseModel


class Material(BaseModel):
    key: str
    name: str
    youngs_modulus_mpa: float
    poisson: float
    density_kg_m3: float
    yield_strength_mpa: float
    price_per_kg: float  # illustrative placeholder, replace with real quotes
    source: str = "typical handbook value - verify"


MATERIALS: dict[str, Material] = {
    m.key: m
    for m in [
        Material(key="AL6061-T6", name="Aluminium 6061-T6", youngs_modulus_mpa=68_900, poisson=0.33,
                 density_kg_m3=2700, yield_strength_mpa=276, price_per_kg=4.0),
        Material(key="AL7075-T6", name="Aluminium 7075-T6", youngs_modulus_mpa=71_700, poisson=0.33,
                 density_kg_m3=2810, yield_strength_mpa=503, price_per_kg=7.0),
        Material(key="STEEL-A36", name="Structural steel A36", youngs_modulus_mpa=200_000, poisson=0.26,
                 density_kg_m3=7850, yield_strength_mpa=250, price_per_kg=1.2),
        Material(key="TI-6AL-4V", name="Titanium Ti-6Al-4V", youngs_modulus_mpa=113_800, poisson=0.34,
                 density_kg_m3=4430, yield_strength_mpa=880, price_per_kg=35.0),
    ]
}

_ALIASES = {
    "aluminium": "AL6061-T6", "aluminum": "AL6061-T6", "alu": "AL6061-T6",
    "6061": "AL6061-T6", "7075": "AL7075-T6",
    "steel": "STEEL-A36", "a36": "STEEL-A36",
    "titanium": "TI-6AL-4V", "ti-6al-4v": "TI-6AL-4V",
}


def resolve_material(text: str) -> tuple[str | None, bool]:
    """Return (material_key, grade_was_explicit). Generic names map to a default grade (not explicit)."""
    t = text.lower()
    for alias in ("7075", "6061", "a36", "ti-6al-4v"):
        if alias in t:
            return _ALIASES[alias], True
    for alias in ("aluminium", "aluminum", "steel", "titanium"):
        if alias in t:
            return _ALIASES[alias], False
    return None, False
