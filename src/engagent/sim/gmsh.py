"""Gmsh STEP-to-tetrahedral mesh support for the FEA pipeline.

Meshes are written in legacy MSH 2.2 format because its node and element blocks are
straightforward to translate into a CalculiX input deck in the next Phase 4 step.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import subprocess


@dataclass(frozen=True)
class MeshStats:
    nodes: int
    elements: int
    tetrahedra: int


def find_gmsh(explicit: str | None = None) -> str | None:
    """Return an explicit executable or a PATH-resolved Gmsh executable."""
    return explicit or shutil.which("gmsh") or shutil.which("gmsh.exe")


def msh2_stats(path: str | Path) -> MeshStats:
    """Read counts from an ASCII MSH 2.2 file; tetrahedra are element type 4."""
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    try:
        node_at, element_at = lines.index("$Nodes"), lines.index("$Elements")
        nodes = int(lines[node_at + 1])
        elements = int(lines[element_at + 1])
    except (ValueError, IndexError) as exc:
        raise ValueError(f"{path} is not a readable MSH 2.2 mesh") from exc
    tetrahedra = sum(
        1 for line in lines[element_at + 2: element_at + 2 + elements]
        if len(line.split()) >= 2 and line.split()[1] == "4"
    )
    return MeshStats(nodes=nodes, elements=elements, tetrahedra=tetrahedra)


def mesh_step(step_path: str | Path, mesh_path: str | Path, *, gmsh: str | None = None,
              min_size_mm: float = 3.0, max_size_mm: float = 6.0) -> MeshStats:
    """Mesh a STEP solid as 3D tetrahedra and return verified mesh statistics."""
    step, mesh = Path(step_path), Path(mesh_path)
    if not step.is_file():
        raise FileNotFoundError(step)
    if min_size_mm <= 0 or max_size_mm <= 0 or min_size_mm > max_size_mm:
        raise ValueError("mesh sizes must be positive and min_size_mm <= max_size_mm")
    executable = find_gmsh(gmsh)
    if not executable:
        raise FileNotFoundError("Gmsh executable not found; provide --gmsh or add it to PATH")
    mesh.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        executable, "-3", str(step), "-format", "msh2", "-o", str(mesh),
        "-clmin", str(min_size_mm), "-clmax", str(max_size_mm), "-v", "2",
    ], check=True, capture_output=True, text=True)
    stats = msh2_stats(mesh)
    if not stats.nodes or not stats.tetrahedra:
        raise ValueError(f"Gmsh produced no 3D tetrahedra: {mesh}")
    return stats
