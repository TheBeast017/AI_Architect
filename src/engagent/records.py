"""One record per candidate x simulation (doc 11, 17.3). JSONL store + CSV export."""
from __future__ import annotations
import csv, hashlib, json, platform, time
from pathlib import Path
from pydantic import BaseModel, Field
from .verify import Outcome


class CostModel:
    """ILLUSTRATIVE cost proxy: stock block material + machining volume removed. Replace with real quotes."""
    machining_per_cm3 = 0.05

    @classmethod
    def cost(cls, p, mat, mass_kg: float) -> float:
        stock_cm3 = p.width_mm * (p.thickness_mm + p.rib_height_mm) * p.arm_length_mm / 1e3
        part_cm3 = mass_kg / mat.density_kg_m3 * 1e6
        stock_kg = stock_cm3 * 1e-6 * mat.density_kg_m3
        return stock_kg * mat.price_per_kg + max(stock_cm3 - part_cm3, 0) * cls.machining_per_cm3


class SimulationRecord(BaseModel):
    # identity & provenance
    design_id: str
    parent_design_id: str | None = None
    method: str                       # lhs | differential_evolution | ...
    timestamp: float = Field(default_factory=time.time)
    python: str = platform.python_version()
    solver: str = ""
    solver_version: str = ""
    fidelity: str = ""
    # geometry / parameters
    component_family: str = "wall_bracket"
    params: dict
    stl_path: str | None = None
    geometry_issues: list[str] = []
    # material & setup
    material_key: str = ""
    spec_hash: str = ""
    load_N: float | None = None
    # performance labels
    mass_kg: float | None = None
    max_von_mises_mpa: float | None = None
    max_deflection_mm: float | None = None
    factor_of_safety: float | None = None
    cost_proxy: float | None = None
    # decision
    outcome: Outcome
    violations: list[str] = []
    feasible: bool = False
    pareto_rank: int | None = None


def make_design_id(params: dict, spec_hash: str) -> str:
    raw = json.dumps(params, sort_keys=True) + spec_hash
    return "D" + hashlib.sha1(raw.encode()).hexdigest()[:10]


class RecordStore:
    def __init__(self, path: str | None = None):
        self.records: list[SimulationRecord] = []
        self.path = Path(path) if path else None
        self._seen: dict[str, SimulationRecord] = {}

    def add(self, rec: SimulationRecord) -> SimulationRecord:
        if rec.design_id in self._seen:      # same params + same spec => reuse, don't duplicate
            return self._seen[rec.design_id]
        self.records.append(rec)
        self._seen[rec.design_id] = rec
        return rec

    def save(self) -> None:
        if not self.path:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w") as f:
            for r in self.records:
                f.write(r.model_dump_json() + "\n")

    def to_csv(self, path: str) -> None:
        rows = []
        for r in self.records:
            d = r.model_dump(mode="json")
            d.update({f"p_{k}": v for k, v in d.pop("params").items()})
            d["violations"] = "; ".join(d["violations"])
            d["geometry_issues"] = "; ".join(d["geometry_issues"])
            rows.append(d)
        if not rows:
            return
        keys = sorted({k for r in rows for k in r})
        with open(path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            w.writerows(rows)
