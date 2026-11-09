"""Emit a FreeCAD Python script for a candidate (doc 12.1).
UNVERIFIED against a real FreeCAD install (plan.md Phase 3): run `freecadcmd script.py` to test."""
from __future__ import annotations
from ..design_space import BracketParams


def freecad_script(p: BracketParams, step_path: str, fcstd_path: str) -> str:
    return f'''import FreeCAD as App, Part
doc = App.newDocument("bracket")
L, w, t = {p.arm_length_mm}, {p.width_mm}, {p.thickness_mm}
rt, rh, rl = {p.rib_thickness_mm}, {p.rib_height_mm}, {p.rib_length_mm}
solid = Part.makeBox(L, w, t, App.Vector(0, -w/2, 0))
if rh > 0:
    pts = [App.Vector(0,-rt/2,0), App.Vector(rl,-rt/2,0), App.Vector(0,-rt/2,-rh), App.Vector(0,-rt/2,0)]
    face = Part.Face(Part.makePolygon(pts))
    solid = solid.fuse(face.extrude(App.Vector(0, rt, 0)))
plate = Part.makeBox(10, w, t + rh, App.Vector(-10, -w/2, -rh))
solid = solid.fuse(plate).removeSplitter()
obj = doc.addObject("Part::Feature", "Bracket"); obj.Shape = solid
doc.recompute()
assert solid.isValid() and solid.Volume > 0
Part.export([obj], "{step_path}")
doc.saveAs("{fcstd_path}")
'''
