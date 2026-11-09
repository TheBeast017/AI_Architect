"""Structured engineering specification (doc sections 3.2-3.3).

The spec is the authoritative problem description. Anything not supplied by the user
stays in `unresolved` unless defaults are explicitly allowed, in which case every
default is recorded in `assumptions` with provenance ASSUMED.
Units: mm, N, MPa, kg.
"""
from __future__ import annotations
from enum import Enum
from pydantic import BaseModel, Field


class Provenance(str, Enum):
    EXPLICIT = "explicit"   # stated by the user
    INFERRED = "inferred"   # derived from user text (e.g. generic "aluminium" -> 6061-T6)
    ASSUMED = "assumed"     # default injected by the system - must be reviewed


class EngineeringSpec(BaseModel):
    component_type: str = "wall_bracket"
    raw_request: str = ""
    payload_mass_kg: float | None = None
    load_offset_mm: float | None = None        # wall -> load line (lever arm)
    dynamic_factor: float | None = None        # multiplies static weight (accelerations)
    material_key: str | None = None
    max_deflection_mm: float | None = None
    safety_factor: float | None = None
    max_width_mm: float | None = None          # envelope
    max_height_mm: float | None = None
    min_wall_mm: float | None = None
    max_rib_slenderness: float | None = None  # unsupported gusset height / thickness
    manufacturing: str = "machined"
    objectives: list[str] = Field(default_factory=lambda: ["minimize_mass"])
    provenance: dict[str, Provenance] = Field(default_factory=dict)
    assumptions: list[str] = Field(default_factory=list)
    unresolved: list[str] = Field(default_factory=list)

    # fields that may never be silently invented
    NEVER_DEFAULT: tuple[str, ...] = ("payload_mass_kg", "load_offset_mm")

    def critical_missing(self) -> list[str]:
        need = ["payload_mass_kg", "load_offset_mm", "max_deflection_mm", "material_key"]
        return [f for f in need if getattr(self, f) is None]

    def is_complete(self) -> bool:
        return not self.critical_missing()

    def with_defaults(self) -> "EngineeringSpec":
        """Fill non-critical gaps, recording each as an assumption. Never fills payload / offset."""
        s = self.model_copy(deep=True)

        def put(field: str, value, why: str):
            if getattr(s, field) is None:
                setattr(s, field, value)
                s.provenance[field] = Provenance.ASSUMED
                s.assumptions.append(f"{field} = {value} (assumed: {why})")

        put("material_key", "AL6061-T6", "common machinable aluminium; confirm grade")
        if s.load_offset_mm is not None:
            put("max_deflection_mm", round(s.load_offset_mm / 500, 3), "L/500 rule of thumb; confirm with function")
        put("dynamic_factor", 1.5, "allowance for arm acceleration; confirm load case")
        put("safety_factor", 2.0, "generic factor on yield; confirm with applicable standard")
        put("max_width_mm", 150.0, "placeholder envelope")
        put("max_height_mm", 120.0, "placeholder envelope")
        put("min_wall_mm", 3.0, "placeholder machining limit")
        put("max_rib_slenderness", 15.0,
            "conservative screening cap on unsupported gusset height/thickness; verify by FEA")
        s.unresolved = s.critical_missing()
        return s
