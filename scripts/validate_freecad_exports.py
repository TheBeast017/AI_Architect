"""Run inside FreeCAD to validate the Phase 3 STEP export after re-import."""
from __future__ import annotations

from pathlib import Path

import Part


step_path = Path("runs/freecad-validation/bracket.step").resolve()
shape = Part.read(str(step_path))
assert shape.isValid(), "re-imported STEP shape is invalid"
assert shape.Volume > 0, "re-imported STEP has zero volume"
print(f"STEP valid; volume={shape.Volume:.3f} mm^3; solids={len(shape.Solids)}")
