"""Constraint verification + failure classification (doc 7.5, 8.4-8.5, 9.2)."""
from __future__ import annotations
from enum import Enum
from pydantic import BaseModel
from .materials import Material
from .schemas import EngineeringSpec
from .sim.base import SimResult


class Outcome(str, Enum):
    GEOMETRY_INVALID = "geometry_invalid"
    SOLVER_FAILED = "solver_failed"          # calculation unreliable - NOT a structural failure
    CONSTRAINT_VIOLATED = "constraint_violated"
    FEASIBLE = "feasible"


class ConstraintReport(BaseModel):
    outcome: Outcome
    violations: list[str] = []
    stress_ratio: float | None = None        # vm / allowable (<=1 ok)
    deflection_ratio: float | None = None    # delta / limit (<=1 ok)
    factor_of_safety: float | None = None

    @property
    def penalty(self) -> float:
        p = 0.0
        for r in (self.stress_ratio, self.deflection_ratio):
            if r is not None and r > 1:
                p += r - 1
        return p


def check_constraints(geom_issues: list[str], sim: SimResult | None,
                      spec: EngineeringSpec, mat: Material) -> ConstraintReport:
    if geom_issues:
        return ConstraintReport(outcome=Outcome.GEOMETRY_INVALID, violations=geom_issues)
    if sim is None or not sim.completed:
        return ConstraintReport(outcome=Outcome.SOLVER_FAILED,
                                violations=[sim.message if sim else "no simulation result"])
    allow = mat.yield_strength_mpa / spec.safety_factor
    sr = sim.max_von_mises_mpa / allow
    dr = sim.max_deflection_mm / spec.max_deflection_mm
    v = []
    if sr > 1:
        v.append(f"von Mises {sim.max_von_mises_mpa:.1f} MPa > allowable {allow:.1f} MPa")
    if dr > 1:
        v.append(f"deflection {sim.max_deflection_mm:.3f} mm > limit {spec.max_deflection_mm} mm")
    fos = mat.yield_strength_mpa / sim.max_von_mises_mpa if sim.max_von_mises_mpa > 0 else None
    return ConstraintReport(outcome=Outcome.CONSTRAINT_VIOLATED if v else Outcome.FEASIBLE,
                            violations=v, stress_ratio=sr, deflection_ratio=dr, factor_of_safety=fos)
