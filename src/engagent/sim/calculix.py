"""CalculiX adapter - PLACEHOLDER (plan.md Phase 4).

To implement: CAD(STEP) -> Gmsh tet mesh -> write .inp (*NODE/*ELEMENT/*MATERIAL/*BOUNDARY/*CLOAD)
-> run `ccx` -> parse .frd/.dat -> SimResult(fidelity="FEA-3D") with a mesh-refinement check.
Docs: https://www.calculix.de/   Gmsh: https://gmsh.info/doc/texinfo/gmsh.html
"""
from __future__ import annotations
import shutil
from ..design_space import BracketParams
from ..materials import Material
from ..schemas import EngineeringSpec
from .base import SimResult


class CalculiXBackend:
    name = "calculix"

    @staticmethod
    def available() -> bool:
        return shutil.which("ccx") is not None

    def evaluate(self, p: BracketParams, spec: EngineeringSpec, mat: Material) -> SimResult:
        raise NotImplementedError("CalculiX backend not implemented yet - see plan.md Phase 4")
