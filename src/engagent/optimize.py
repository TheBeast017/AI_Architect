"""Optimisation (doc 6). SciPy differential evolution + LHS sampling. Penalty handles hard constraints."""
from __future__ import annotations
import numpy as np
from scipy.optimize import differential_evolution
from .design_space import DesignSpace
from .evaluate import Evaluator
from .verify import Outcome

BIG = 1e3


def sample_candidates(space: DesignSpace, ev: Evaluator, n: int, seed: int = 0) -> int:
    for x in space.sample(n, seed):
        ev(space.to_params(x), method="lhs")
    return n


def run_de(space: DesignSpace, ev: Evaluator, objective: str = "mass", seed: int = 0,
           maxiter: int = 60, popsize: int = 15) -> dict:
    """Single-objective DE. objective: 'mass' | 'cost'. Returns termination info (doc 8.8)."""
    def f(x):
        rec, rep = ev(space.to_params(x), method="differential_evolution")
        if rep.outcome in (Outcome.GEOMETRY_INVALID, Outcome.SOLVER_FAILED):
            return 10 * BIG
        base = rec.mass_kg if objective == "mass" else rec.cost_proxy
        return base + BIG * rep.penalty
    res = differential_evolution(f, space.bounds, seed=seed, maxiter=maxiter, popsize=popsize,
                                 tol=1e-6, polish=False, updating="immediate")
    return {"success": bool(res.success), "message": str(res.message), "nit": int(res.nit),
            "nfev": int(res.nfev), "x": res.x.tolist(),
            "note": "Local/stochastic search result. Global optimality is NOT proven."}
