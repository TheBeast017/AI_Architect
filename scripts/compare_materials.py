"""Run and report a fair aluminium-vs-steel bracket screening comparison."""
from __future__ import annotations

import json
from pathlib import Path

from engagent.agent import run_design
from engagent.comparison import material_comparison_markdown

BASE = "lightweight wall bracket, 25 kg payload, 300 mm from the wall, max deflection 1 mm"


def best_candidate(run_dir: Path, material: str) -> dict:
    result = run_design(f"{BASE}, {material}", allow_defaults=True, n_samples=150,
                        out_dir=str(run_dir))
    if result.best_id is None:
        raise RuntimeError(f"no feasible {material} candidate")
    for line in (run_dir / "records.jsonl").read_text().splitlines():
        record = json.loads(line)
        if record["design_id"] == result.best_id:
            params = record["params"]
            return {
                "material": record["material_key"], "design_id": record["design_id"],
                "mass_kg": record["mass_kg"], "max_deflection_mm": record["max_deflection_mm"],
                "max_von_mises_mpa": record["max_von_mises_mpa"],
                "factor_of_safety": record["factor_of_safety"], "cost_proxy": record["cost_proxy"],
                "width_mm": params["width_mm"], "thickness_mm": params["thickness_mm"],
                "rib_thickness_mm": params["rib_thickness_mm"], "rib_height_mm": params["rib_height_mm"],
            }
    raise RuntimeError(f"best design {result.best_id} was not recorded")


def main() -> None:
    root = Path("runs/material-comparison")
    aluminium = best_candidate(root / "aluminium", "Aluminium 6061-T6")
    steel = best_candidate(root / "steel", "Steel A36")
    report = material_comparison_markdown(aluminium, steel)
    path = root / "comparison.md"
    path.write_text(report, encoding="utf-8")
    print(path.resolve())
    print(report)


if __name__ == "__main__":
    main()
