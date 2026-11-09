"""Simulation backend interface (doc 3.6). Solver failure != structural failure."""
from __future__ import annotations
from typing import Protocol
from pydantic import BaseModel, Field
from ..design_space import BracketParams
from ..materials import Material
from ..schemas import EngineeringSpec


class SimResult(BaseModel):
    completed: bool
    message: str = ""
    solver: str
    solver_version: str
    fidelity: str                       # e.g. "analytical-1D", "FEA-3D"
    mass_kg: float | None = None
    max_von_mises_mpa: float | None = None
    max_deflection_mm: float | None = None
    compliance_nmm: float | None = None
    verification: dict[str, bool] = Field(default_factory=dict)
    limitations: list[str] = Field(default_factory=list)


class SimBackend(Protocol):
    name: str
    def evaluate(self, p: BracketParams, spec: EngineeringSpec, mat: Material) -> SimResult: ...
