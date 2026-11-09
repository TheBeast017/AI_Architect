"""Small, explicit decision aid for comparing two screening-model candidates."""
from __future__ import annotations


def _winner(left: dict, right: dict, field: str) -> str:
    """Return the material key of the lower-valued candidate, or ``tie``."""
    a, b = left[field], right[field]
    if abs(a - b) < 1e-12:
        return "tie"
    return left["material"] if a < b else right["material"]


def material_comparison_markdown(aluminium: dict, steel: dict) -> str:
    """Produce a transparent comparison; never label a screening result certified."""
    rows = [
        ("Mass (kg)", "mass_kg", 4),
        ("Deflection (mm)", "max_deflection_mm", 3),
        ("von Mises stress (MPa)", "max_von_mises_mpa", 1),
        ("Yield factor of safety", "factor_of_safety", 2),
        ("Cost proxy", "cost_proxy", 2),
    ]
    out = [
        "# Aluminium vs Steel Bracket Comparison",
        "",
        "Both candidates use the same 25 kg payload, 300 mm cantilever reach, 1 mm deflection limit, "
        "and the analytical 1D screening model.",
        "",
        "| Metric | Aluminium 6061-T6 | Steel A36 | Lower is better? |",
        "|---|---:|---:|---|",
    ]
    for label, field, digits in rows:
        lower = "yes" if field != "factor_of_safety" else "no"
        out.append(f"| {label} | {aluminium[field]:.{digits}f} | {steel[field]:.{digits}f} | {lower} |")
    out += [
        "",
        "## Best candidates",
        "",
        f"- Aluminium: `{aluminium['design_id']}` — width {aluminium['width_mm']:.1f} mm, "
        f"arm thickness {aluminium['thickness_mm']:.1f} mm, rib {aluminium['rib_thickness_mm']:.1f} x "
        f"{aluminium['rib_height_mm']:.1f} mm.",
        f"- Steel: `{steel['design_id']}` — width {steel['width_mm']:.1f} mm, "
        f"arm thickness {steel['thickness_mm']:.1f} mm, rib {steel['rib_thickness_mm']:.1f} x "
        f"{steel['rib_height_mm']:.1f} mm.",
        "",
        "## Recommendation",
        "",
    ]
    mass_winner = _winner(aluminium, steel, "mass_kg")
    deflection_winner = _winner(aluminium, steel, "max_deflection_mm")
    cost_winner = _winner(aluminium, steel, "cost_proxy")
    out.append(
        f"For the stated **lightweight** objective, select **{mass_winner}**: it has the lower predicted mass. "
        f"For stiffness, {deflection_winner} has lower predicted deflection; for the illustrative cost proxy, "
        f"{cost_winner} is lower."
    )
    out += [
        "",
        "## Important limits",
        "",
        "- This compares analytical 1D screening results, not CalculiX FEA.",
        "- Bolt holes, wall mounting, support stress concentrations, and buckling are not modelled.",
        "- The material price and machining values are illustrative; obtain supplier quotes.",
        "- A qualified engineer must validate a real part before manufacture or use.",
    ]
    return "\n".join(out)
