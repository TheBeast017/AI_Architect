"""Emit a representative FreeCAD bracket export script for Phase 3 validation.

Run this first, then execute the emitted script with ``freecadcmd``.  The FreeCAD
script asserts a valid, non-zero-volume solid before exporting STEP and FCStd.
"""
from __future__ import annotations

from pathlib import Path

from engagent.cad.freecad_script import freecad_script
from engagent.design_space import BracketParams


def main() -> None:
    output_dir = Path("runs/freecad-validation")
    output_dir.mkdir(parents=True, exist_ok=True)
    params = BracketParams(
        arm_length_mm=300,
        width_mm=60,
        thickness_mm=12,
        rib_thickness_mm=8,
        rib_height_mm=60,
        rib_length_mm=220,
    )
    script_path = output_dir / "bracket.py"
    script_path.write_text(
        freecad_script(
            params,
            (output_dir / "bracket.step").resolve().as_posix(),
            (output_dir / "bracket.FCStd").resolve().as_posix(),
        ),
        encoding="utf-8",
    )
    print(script_path.resolve())


if __name__ == "__main__":
    main()
