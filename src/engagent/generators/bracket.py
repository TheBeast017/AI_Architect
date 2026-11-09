"""Geometry validation (doc 8.2) for the parametric bracket."""
from __future__ import annotations
from ..design_space import BracketParams
from ..schemas import EngineeringSpec


def validate_geometry(p: BracketParams, spec: EngineeringSpec) -> list[str]:
    issues: list[str] = []
    if p.thickness_mm < spec.min_wall_mm:
        issues.append(f"thickness {p.thickness_mm:.2f} < min wall {spec.min_wall_mm}")
    if p.width_mm > spec.max_width_mm:
        issues.append("width exceeds envelope")
    if p.thickness_mm + p.rib_height_mm > spec.max_height_mm + 1e-9:
        issues.append("arm+rib height exceeds envelope")
    if p.rib_height_mm > 0:
        if p.rib_thickness_mm > p.width_mm:
            issues.append("rib thicker than arm width")
        if p.rib_thickness_mm < spec.min_wall_mm:
            issues.append("rib below min wall")
        if p.rib_length_mm > p.arm_length_mm + 1e-9:
            issues.append("rib longer than arm")
        # The 1D beam model cannot represent local plate buckling or out-of-plane
        # twisting of the gusset.  Reject very thin, tall ribs before optimisation
        # can exploit their fictitious bending stiffness.  This is a screening
        # constraint, not a substitute for the planned eigenvalue FEA check.
        slenderness = p.rib_height_mm / p.rib_thickness_mm
        if (spec.max_rib_slenderness is not None
                and slenderness > spec.max_rib_slenderness + 1e-9):
            issues.append(
                f"rib slenderness {slenderness:.2f} exceeds limit "
                f"{spec.max_rib_slenderness:.2f} (height/thickness)"
            )
    return issues
