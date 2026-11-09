"""Low-fidelity Euler-Bernoulli cantilever with variable T-section (arm + tapered rib).

Purpose: fast, deterministic evaluator so the whole agent loop runs without a mesher/solver.
It is NOT a substitute for FEA: no stress concentrations, no wall interface, no shear
deflection, no buckling. Use it to pre-screen / seed surrogate data; verify with CalculiX.
"""
from __future__ import annotations
import numpy as np
from ..design_space import BracketParams
from ..materials import Material
from ..schemas import EngineeringSpec
from .base import SimResult

G = 9.81
_trapz = getattr(np, "trapezoid", None) or np.trapz


def _section(p: BracketParams, x: np.ndarray):
    """Area, second moment I, extreme-fibre distance c at stations x (mm). Rib hangs below the arm."""
    h_rib = np.where(x < p.rib_length_mm, p.rib_height_mm * (1 - x / max(p.rib_length_mm, 1e-9)), 0.0)
    a1 = p.width_mm * p.thickness_mm
    a2 = p.rib_thickness_mm * h_rib
    y1 = p.thickness_mm / 2
    y2 = p.thickness_mm + h_rib / 2
    A = a1 + a2
    yb = (a1 * y1 + a2 * y2) / A
    I = (p.width_mm * p.thickness_mm**3 / 12 + a1 * (y1 - yb) ** 2
         + p.rib_thickness_mm * h_rib**3 / 12 + a2 * (y2 - yb) ** 2)
    depth = p.thickness_mm + h_rib
    c = np.maximum(yb, depth - yb)
    return A, I, c


def _solve(p: BracketParams, P: float, E: float, n: int):
    x = np.linspace(0.0, p.arm_length_mm, n)
    A, I, c = _section(p, x)
    M = P * (p.arm_length_mm - x)
    sigma = M * c / I
    tau = 1.5 * P / A
    vm = np.sqrt(sigma**2 + 3 * tau**2)
    delta = P * _trapz((p.arm_length_mm - x) ** 2 / (E * I), x)   # unit-load method
    return vm.max(), delta, P * delta, A, x


class AnalyticalBeamBackend:
    name = "analytical_beam"
    version = "0.1"

    def evaluate(self, p: BracketParams, spec: EngineeringSpec, mat: Material) -> SimResult:
        P = spec.payload_mass_kg * G * spec.dynamic_factor
        try:
            vm, delta, comp, A, x = _solve(p, P, mat.youngs_modulus_mpa, 400)
            vm2, delta2, *_ = _solve(p, P, mat.youngs_modulus_mpa, 800)
        except Exception as e:  # solver-level failure, NOT a structural result
            return SimResult(completed=False, message=str(e), solver=self.name,
                             solver_version=self.version, fidelity="analytical-1D")
        mass = float(_trapz(A, x)) * 1e-9 * mat.density_kg_m3
        ver = {
            "finite_results": bool(np.isfinite([vm, delta, mass]).all()),
            "discretisation_converged": abs(delta2 - delta) / max(delta2, 1e-12) < 1e-3
                                        and abs(vm2 - vm) / max(vm2, 1e-12) < 5e-3,
            "positive_mass": mass > 0,
        }
        ok = all(ver.values())
        return SimResult(
            completed=ok, message="ok" if ok else "verification failed",
            solver=self.name, solver_version=self.version, fidelity="analytical-1D",
            mass_kg=mass, max_von_mises_mpa=float(vm), max_deflection_mm=float(delta),
            compliance_nmm=float(comp), verification=ver,
            limitations=["1D beam theory", "no stress concentration at wall/bolts",
                         "no shear deflection", "no buckling/fatigue", "back plate not modelled",
                         "mass = arm + rib only"],
        )
