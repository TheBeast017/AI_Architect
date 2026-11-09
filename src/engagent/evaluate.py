"""Glue: params -> validate -> simulate -> check -> record. Single evaluation entry point."""
from __future__ import annotations
import hashlib, json
from .design_space import BracketParams
from .generators.bracket import validate_geometry
from .materials import MATERIALS
from .records import CostModel, RecordStore, SimulationRecord, make_design_id
from .schemas import EngineeringSpec
from .sim.analytical_beam import AnalyticalBeamBackend, G
from .sim.base import SimBackend
from .verify import ConstraintReport, Outcome, check_constraints


def spec_hash(spec: EngineeringSpec) -> str:
    d = spec.model_dump(mode="json", exclude={"raw_request", "provenance", "assumptions", "unresolved"})
    return hashlib.sha1(json.dumps(d, sort_keys=True).encode()).hexdigest()[:8]


class Evaluator:
    def __init__(self, spec: EngineeringSpec, store: RecordStore,
                 backend: SimBackend | None = None, method: str = "lhs"):
        self.spec, self.store = spec, store
        self.backend = backend or AnalyticalBeamBackend()
        self.mat = MATERIALS[spec.material_key]
        self.method = method
        self.sh = spec_hash(spec)

    def __call__(self, p: BracketParams, parent: str | None = None, method: str | None = None
                 ) -> tuple[SimulationRecord, ConstraintReport]:
        issues = validate_geometry(p, self.spec)
        sim = None if issues else self.backend.evaluate(p, self.spec, self.mat)
        rep = check_constraints(issues, sim, self.spec, self.mat)
        did = make_design_id(p.as_dict(), self.sh)
        cost = CostModel.cost(p, self.mat, sim.mass_kg) if sim and sim.completed else None
        rec = SimulationRecord(
            design_id=did, parent_design_id=parent, method=method or self.method,
            solver=getattr(sim, "solver", ""), solver_version=getattr(sim, "solver_version", ""),
            fidelity=getattr(sim, "fidelity", ""), params=p.as_dict(), geometry_issues=issues,
            material_key=self.spec.material_key, spec_hash=self.sh,
            load_N=self.spec.payload_mass_kg * G * self.spec.dynamic_factor,
            mass_kg=getattr(sim, "mass_kg", None), max_von_mises_mpa=getattr(sim, "max_von_mises_mpa", None),
            max_deflection_mm=getattr(sim, "max_deflection_mm", None),
            factor_of_safety=rep.factor_of_safety, cost_proxy=cost, outcome=rep.outcome,
            violations=rep.violations, feasible=rep.outcome == Outcome.FEASIBLE)
        return self.store.add(rec), rep
