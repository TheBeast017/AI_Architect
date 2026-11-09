"""Create a verified 3D tetrahedral Gmsh mesh from a STEP file."""
from __future__ import annotations

import argparse

from engagent.sim.gmsh import mesh_step


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("step")
    parser.add_argument("mesh")
    parser.add_argument("--gmsh", help="path to gmsh executable (otherwise use PATH)")
    parser.add_argument("--min-size-mm", type=float, default=3.0)
    parser.add_argument("--max-size-mm", type=float, default=6.0)
    args = parser.parse_args()
    stats = mesh_step(args.step, args.mesh, gmsh=args.gmsh,
                      min_size_mm=args.min_size_mm, max_size_mm=args.max_size_mm)
    print(f"Mesh verified: {stats.nodes} nodes, {stats.elements} elements, {stats.tetrahedra} tetrahedra")


if __name__ == "__main__":
    main()
