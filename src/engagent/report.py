"""Traceable engineering report (doc 3.8, 14). Keeps individual objectives; states limits plainly."""
from __future__ import annotations
from .schemas import EngineeringSpec


def _fmt(v, nd=3):
    return "-" if v is None else f"{v:.{nd}f}"


def build_report(spec: EngineeringSpec, status: str, metrics: dict, front: list, best, de_info: dict | None,
                 limitations: list[str]) -> str:
    L = ["# Engineering Design Report", "", f"**Status:** `{status}`", "",
         "## 1. Specification", "", "| Field | Value | Provenance |", "|---|---|---|"]
    for k in ("component_type", "payload_mass_kg", "load_offset_mm", "dynamic_factor", "material_key",
              "max_deflection_mm", "safety_factor", "max_width_mm", "max_height_mm", "min_wall_mm"):
        prov = spec.provenance.get(k)
        L.append(f"| {k} | {getattr(spec, k)} | {prov.value if prov else 'n/a'} |")
    if spec.assumptions:
        L += ["", "### Assumptions (review before use)", *[f"- {a}" for a in spec.assumptions]]
    if spec.unresolved:
        L += ["", "### Unresolved", *[f"- {u}" for u in spec.unresolved]]
    L += ["", "## 2. Search statistics", "", "| Metric | Value |", "|---|---|"]
    L += [f"| {k} | {v} |" for k, v in metrics.items()]
    if de_info:
        L += ["", f"Differential evolution: nit={de_info['nit']}, nfev={de_info['nfev']}, "
                  f"message: {de_info['message']}. {de_info['note']}"]
    L += ["", "## 3. Result", ""]
    if best is None:
        L.append("**No feasible candidate was found in the explored design space.** "
                 "This does not prove infeasibility; widen the envelope/limits or increase the budget.")
    else:
        L += [f"Best feasible (min mass): `{best.design_id}` - mass {_fmt(best.mass_kg, 4)} kg, "
              f"von Mises {_fmt(best.max_von_mises_mpa, 1)} MPa, deflection {_fmt(best.max_deflection_mm, 3)} mm, "
              f"FoS(yield) {_fmt(best.factor_of_safety, 2)}, cost proxy {_fmt(best.cost_proxy, 2)}.", "",
              "### Pareto set (mass, cost proxy, deflection)", "",
              "| design_id | mass kg | cost proxy | defl mm | vM MPa | width | t | rib t | rib h | rib L |",
              "|---|---|---|---|---|---|---|---|---|---|"]
        for r in front:
            p = r.params
            L.append(f"| {r.design_id} | {_fmt(r.mass_kg,4)} | {_fmt(r.cost_proxy,2)} | {_fmt(r.max_deflection_mm)} | "
                     f"{_fmt(r.max_von_mises_mpa,1)} | {p['width_mm']:.1f} | {p['thickness_mm']:.1f} | "
                     f"{p['rib_thickness_mm']:.1f} | {p['rib_height_mm']:.1f} | {p['rib_length_mm']:.1f} |")
    L += ["", "## 4. Limitations", *[f"- {x}" for x in limitations], "",
          "> Satisfying the encoded constraints is **not** a safety certification. Verify with FEA, "
          "testing and qualified engineering review before real-world use."]
    return "\n".join(L)
