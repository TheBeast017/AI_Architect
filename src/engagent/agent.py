"""Orchestrator: requirements -> spec -> design space -> candidates -> simulate -> optimise -> report."""
from __future__ import annotations
from enum import Enum
from pathlib import Path
import json
import numpy as np
from pydantic import BaseModel
from .cad.stl import write_stl
from .design_space import BracketParams, build_bracket_space
from .evaluate import Evaluator
from .optimize import run_de, sample_candidates
from .pareto import pareto_ranks
from .records import RecordStore
from .report import build_report
from .requirements import parse_requirements
from .schemas import EngineeringSpec, Provenance
from .verify import Outcome
from .llm.design_reasoner import extract_spec as llm1_extract_spec, reason_about_design, LLMExtractionResult, DesignReasonResult
from .llm.anthropic_extractor import extract_spec as anthropic_extract_spec
from .llm.gemini_extractor import extract_spec as gemini_extract_spec


class RunStatus(str, Enum):
    NEEDS_INPUT = "needs_input"
    NO_FEASIBLE = "no_feasible_found"
    FEASIBLE_FOUND = "feasible_found"


class RunResult(BaseModel):
    status: RunStatus
    spec: EngineeringSpec
    questions: list[str] = []
    metrics: dict = {}
    best_id: str | None = None
    best_params: dict | None = None  # parametric geometry for display; not a CAD/FEA result
    best_feasible: dict | None = None  # full evaluation results including stress, deflection, safety factor
    pareto_ids: list[str] = []
    report_md: str = ""
    out_dir: str | None = None
    llm_step: dict | None = None  # tracks LLM integration steps; fields: step_name, success, model_used, messages


def _apply_overrides(spec: EngineeringSpec, overrides: dict) -> EngineeringSpec:
    """Apply structured field overrides from the UI directly onto the spec.

    Only sets a field when the override value is a non-empty string or a real number.
    Provenance is marked ASSUMED so assumptions appear in the result report.
    """
    numeric_fields = {
        "payload_mass_kg", "load_offset_mm", "max_deflection_mm",
        "safety_factor", "dynamic_factor",
        "max_width_mm", "max_height_mm", "min_wall_mm", "max_rib_slenderness",
    }
    string_fields = {"material_key", "manufacturing"}

    for field, raw in overrides.items():
        if not hasattr(spec, field):
            continue
        if field in numeric_fields:
            # Accept numeric string or actual number; skip empty/zero/None
            try:
                val = float(raw)
                if val <= 0:
                    continue
            except (TypeError, ValueError):
                continue
            if getattr(spec, field) is None:  # only fill if not already parsed from text
                setattr(spec, field, val)
                spec.provenance[field] = Provenance.ASSUMED
                if field not in [a.split(" =")[0] for a in spec.assumptions]:
                    spec.assumptions.append(f"{field} = {val} (from defaults panel)")
        elif field in string_fields:
            val = str(raw).strip() if raw else ""
            if val and getattr(spec, field) is None:
                setattr(spec, field, val)
                spec.provenance[field] = Provenance.ASSUMED
    return spec


def run_design(request: str | None = None, spec: EngineeringSpec | None = None, *,
               allow_defaults: bool = False, spec_overrides: dict | None = None,
               n_samples: int = 1500, seed: int = 0, de_maxiter: int = 40,
               out_dir: str | None = None) -> RunResult:
    llm_step = {}

    # 1. Start with rule-based parser as baseline (works offline always)
    if spec is None:
        spec = parse_requirements(request or "")
        spec.unresolved = spec.critical_missing()

    # 2. LLM Step 1: Interpret the user request into an EngineeringSpec
    if request and request.strip():
        try:
            llm1_result = llm1_extract_spec(request)
            if llm1_result.spec is not None:
                # Merge LLM fill-ins onto rule-based spec
                for k, v in llm1_result.spec.model_dump().items():
                    if v is not None and hasattr(spec, k) and getattr(spec, k) is None:
                        setattr(spec, k, v)
                        spec.provenance[k] = Provenance.INFERRED
                spec.unresolved = spec.critical_missing()
                llm_step["step_1_extraction"] = {
                    "success": True,
                    "model_used": llm1_result.model_used,
                    "raw_output_note": llm1_result.raw_output[:100] if llm1_result.raw_output else None
                }
        except Exception as e:
            llm_step["step_1_extraction"] = {
                "success": False,
                "error": str(e),
                "model_used": "none"
            }

    # 3. LLM Step 2: Reason about structural design constraints
    if request and request.strip() and spec.is_complete():
        try:
            llm2_result = reason_about_design(spec)
            reason = llm2_result.reason or {}
            if reason and isinstance(reason, dict):
                recommended_geom = reason.get("recommended_geometry")
                if recommended_geom and isinstance(recommended_geom, dict):
                    for k in ["arm_length_mm", "width_mm", "thickness_mm", "rib_thickness_mm", "rib_height_mm", "rib_length_mm"]:
                        if k in recommended_geom and recommended_geom[k] is not None and getattr(spec, k) is None:
                            setattr(spec, k, recommended_geom[k])
                            spec.provenance[k] = Provenance.INFERRED
                llm_step["step_2_design_reasoning"] = {
                    "success": True,
                    "model_used": llm2_result.model_used,
                    "design_notes": reason.get("design_notes", []) or [],
                    "safety_margin": reason.get("safety_margin"),
                    "constraint_violations": reason.get("constraint_violations", []) or []
                }
            else:
                llm_step["step_2_design_reasoning"] = {"success": True, "model_used": llm2_result.model_used, "design_notes": [], "safety_margin": None, "constraint_violations": []}
        except Exception as e:
            llm_step["step_2_design_reasoning"] = {
                "success": False,
                "error": str(e),
                "model_used": "none"
            }

    # 4. Apply explicit UI overrides (structured values from the defaults panel).
    #    This happens BEFORE with_defaults() so user values take priority over system defaults.
    if spec_overrides:
        spec = _apply_overrides(spec, spec_overrides)

    # 5. Fill remaining gaps with engineering defaults if the caller permits it.
    if allow_defaults:
        spec = spec.with_defaults()

    # 6. Gate: payload and offset can never be defaulted - they define the problem.
    miss = spec.critical_missing()
    if miss:
        qs = [f"Please provide: {m}" for m in miss]
        spec.unresolved = miss
        llm_step["final_status"] = "needs_input"
        return RunResult(status=RunStatus.NEEDS_INPUT, spec=spec, questions=qs, llm_step=llm_step)

    out = Path(out_dir) if out_dir else None
    store = RecordStore(str(out / "records.jsonl") if out else None)
    space = build_bracket_space(spec)
    ev = Evaluator(spec, store)

    sample_candidates(space, ev, n_samples, seed)
    de_info = run_de(space, ev, "mass", seed=seed, maxiter=de_maxiter)
    de_cost = run_de(space, ev, "cost", seed=seed + 1, maxiter=de_maxiter)

    recs = store.records
    feas = [r for r in recs if r.feasible]
    n = len(recs)
    n_geom_ok = sum(r.outcome != Outcome.GEOMETRY_INVALID for r in recs)
    n_sim_ok = sum(r.outcome not in (Outcome.GEOMETRY_INVALID, Outcome.SOLVER_FAILED) for r in recs)
    metrics = {"unique designs evaluated": n,
               "geometry validity rate": f"{n_geom_ok / n:.1%}",
               "simulation completion rate": f"{n_sim_ok / max(n_geom_ok, 1):.1%}",
               "constraint satisfaction rate": f"{len(feas) / n:.1%}",
               "feasible designs": len(feas)}

    front, best = [], None
    if feas:
        pts = np.array([[r.mass_kg, r.cost_proxy, r.max_deflection_mm] for r in feas])
        ranks = pareto_ranks(pts)
        for r, k in zip(feas, ranks):
            r.pareto_rank = int(k)
        front = sorted((r for r in feas if r.pareto_rank == 0), key=lambda r: r.mass_kg)
        best = min(feas, key=lambda r: r.mass_kg)
        if len(front) > 25:                                   # thin for the report only
            front = [front[i] for i in np.linspace(0, len(front) - 1, 25).astype(int)]

    limits = sorted({l for r in recs[:1] for l in ["1D beam theory (analytical-1D fidelity)",
                     "no stress concentration at wall interface or bolts", "no shear deflection, buckling or fatigue",
                     "back plate and bolts not designed or analysed", "cost is an illustrative proxy, not a quote",
                     "material values are typical handbook numbers, not design allowables",
                     "stochastic search: a feasible design is not proven globally optimal"]})
    status = RunStatus.FEASIBLE_FOUND if best else RunStatus.NO_FEASIBLE
    report = build_report(spec, status.value, metrics, front, best, de_info, limits)

    if out:
        (out / "cad").mkdir(parents=True, exist_ok=True)
        for r in front[:10] + ([best] if best else []):
            r.stl_path = write_stl(BracketParams(**r.params), str(out / "cad" / f"{r.design_id}.stl"), r.design_id)
        store.save()
        store.to_csv(str(out / "records.csv"))
        (out / "report.md").write_text(report)
        (out / "spec.json").write_text(spec.model_dump_json(indent=2))

    llm_step["final_status"] = status.value

    # Build best_feasible dict with full evaluation results
    best_feasible = None
    if best:
        best_feasible = {
            "id": best.design_id,
            "mass_kg": best.mass_kg,
            "max_stress_mpa": best.max_von_mises_mpa,
            "max_deflection_mm": best.max_deflection_mm,
            "fos_yield": best.factor_of_safety,
            "feasible": True,
            "cost_proxy": best.cost_proxy
        }

    return RunResult(
        status=status,
        spec=spec,
        metrics=metrics,
        best_id=best.design_id if best else None,
        best_params=best.params if best else None,
        best_feasible=best_feasible,
        pareto_ids=[r.design_id for r in front],
        report_md=report,
        out_dir=str(out) if out else None,
        llm_step=llm_step
    )