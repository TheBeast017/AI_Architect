"""Design space + parametric bracket representation (doc 3.4, 4.1)."""
from __future__ import annotations
from dataclasses import dataclass, asdict
import numpy as np
from scipy.stats import qmc
from .schemas import EngineeringSpec


@dataclass(frozen=True)
class BracketParams:
    """Wall-mounted cantilever arm with a tapered under-rib (gusset).
    Back plate is fixed (not optimised or analysed) - see docs/limitations.md."""
    arm_length_mm: float
    width_mm: float
    thickness_mm: float
    rib_thickness_mm: float
    rib_height_mm: float      # 0 => no rib
    rib_length_mm: float

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class Variable:
    name: str
    low: float
    high: float
    unit: str = "mm"


class DesignSpace:
    def __init__(self, spec: EngineeringSpec, variables: list[Variable]):
        self.spec, self.variables = spec, variables

    @property
    def bounds(self) -> list[tuple[float, float]]:
        return [(v.low, v.high) for v in self.variables]

    @property
    def names(self) -> list[str]:
        return [v.name for v in self.variables]

    def to_params(self, x) -> BracketParams:
        w, t, rt, hf, lf = (float(v) for v in x)
        env_h = self.spec.max_height_mm
        rib_h = max(0.0, hf * (env_h - t))
        L = float(self.spec.load_offset_mm)
        return BracketParams(arm_length_mm=L, width_mm=w, thickness_mm=t, rib_thickness_mm=rt,
                             rib_height_mm=rib_h if hf > 0.02 else 0.0, rib_length_mm=lf * L)

    def sample(self, n: int, seed: int = 0) -> np.ndarray:
        """Latin-hypercube / space-filling sample (doc 6.3)."""
        s = qmc.LatinHypercube(d=len(self.variables), seed=seed).random(n)
        lo, hi = np.array(self.bounds).T
        return qmc.scale(s, lo, hi)


def build_bracket_space(spec: EngineeringSpec) -> DesignSpace:
    tw = spec.min_wall_mm or 3.0
    mw = spec.max_width_mm or 150.0
    return DesignSpace(spec, [
        Variable("width_mm", 20.0, spec.max_width_mm),
        Variable("thickness_mm", tw, 25.0),
        Variable("rib_thickness_mm", tw, 20.0),
        Variable("rib_height_frac", 0.0, 1.0, "-"),
        Variable("rib_length_frac", 0.2, 1.0, "-"),
    ])
