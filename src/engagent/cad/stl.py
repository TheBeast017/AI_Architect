"""Dependency-free ASCII STL export for visualisation (Three.js). NOT editable CAD (doc 10.4)."""
from __future__ import annotations
import numpy as np
from ..design_space import BracketParams

BACK_PLATE_T = 10.0  # fixed, unanalysed


def _tri_normal(a, b, c):
    n = np.cross(b - a, c - a)
    l = np.linalg.norm(n)
    return n / l if l else n


def _box(x0, x1, y0, y1, z0, z1):
    v = np.array([[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0],
                  [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]], float)
    f = [(0, 2, 1), (0, 3, 2), (4, 5, 6), (4, 6, 7), (0, 1, 5), (0, 5, 4),
         (1, 2, 6), (1, 6, 5), (2, 3, 7), (2, 7, 6), (3, 0, 4), (3, 4, 7)]
    return [(v[a], v[b], v[c]) for a, b, c in f]


def _wedge(x1, y0, y1, h):
    """Triangular prism: x-z triangle (0,0),(x1,0),(0,-h) extruded along y."""
    P = lambda x, y, z: np.array([x, y, z], float)
    a0, b0, c0 = P(0, y0, 0), P(x1, y0, 0), P(0, y0, -h)
    a1, b1, c1 = P(0, y1, 0), P(x1, y1, 0), P(0, y1, -h)
    return [(a0, c0, b0), (a1, b1, c1), (a0, b0, b1), (a0, b1, a1),
            (a0, a1, c1), (a0, c1, c0), (b0, c0, c1), (b0, c1, b1)]


def bracket_triangles(p: BracketParams):
    """Overlapping solids (no boolean union): fine for display, not for meshing."""
    w, t = p.width_mm, p.thickness_mm
    tris = _box(0, p.arm_length_mm, -w / 2, w / 2, 0, t)
    if p.rib_height_mm > 0:
        tris += _wedge(p.rib_length_mm, -p.rib_thickness_mm / 2, p.rib_thickness_mm / 2, p.rib_height_mm)
    tris += _box(-BACK_PLATE_T, 0, -w / 2, w / 2, -p.rib_height_mm, t)
    return tris


def write_stl(p: BracketParams, path: str, name: str = "bracket") -> str:
    with open(path, "w") as f:
        f.write(f"solid {name}\n")
        for a, b, c in bracket_triangles(p):
            n = _tri_normal(a, b, c)
            f.write(f" facet normal {n[0]:.6e} {n[1]:.6e} {n[2]:.6e}\n  outer loop\n")
            for v in (a, b, c):
                f.write(f"   vertex {v[0]:.6e} {v[1]:.6e} {v[2]:.6e}\n")
            f.write("  endloop\n endfacet\n")
        f.write(f"endsolid {name}\n")
    return path
