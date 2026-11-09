import numpy as np
import pytest
from engagent.agent import RunStatus, run_design
from engagent.design_space import BracketParams, build_bracket_space
from engagent.generators.bracket import validate_geometry
from engagent.sim.gmsh import msh2_stats
from engagent.comparison import material_comparison_markdown
from engagent.materials import MATERIALS
from engagent.pareto import pareto_front
from engagent.requirements import parse_requirements
from engagent.schemas import EngineeringSpec, Provenance
from engagent.sim.analytical_beam import AnalyticalBeamBackend, G

PROMPT = ("I need a lightweight aluminium wall bracket for a robotic arm, 25 kg payload, "
          "300 mm from the wall, max deflection 1 mm")


def test_parse_extracts_only_stated_values():
    s = parse_requirements(PROMPT)
    assert s.payload_mass_kg == 25 and s.load_offset_mm == 300 and s.max_deflection_mm == 1
    assert s.material_key == "AL6061-T6" and s.provenance["material_key"] == Provenance.INFERRED
    assert s.safety_factor is None and "minimize_mass" in s.objectives


def test_missing_critical_not_invented():
    s = parse_requirements("make me a light bracket")
    assert set(s.critical_missing()) >= {"payload_mass_kg", "load_offset_mm"}
    d = s.with_defaults()
    assert d.payload_mass_kg is None and d.load_offset_mm is None   # never defaulted
    r = run_design("make me a light bracket", allow_defaults=True)
    assert r.status == RunStatus.NEEDS_INPUT


def test_defaults_are_flagged():
    s = parse_requirements("25 kg payload, 300 mm from the wall").with_defaults()
    assert s.provenance["safety_factor"] == Provenance.ASSUMED
    assert any("max_deflection_mm" in a for a in s.assumptions)


def test_beam_matches_closed_form():
    """Constant rectangular cantilever: delta = P L^3/(3EI), sigma = 6 P L/(w t^2)."""
    spec = parse_requirements(PROMPT).with_defaults()
    mat = MATERIALS[spec.material_key]
    p = BracketParams(300, 60, 12, 5, 0.0, 100)
    r = AnalyticalBeamBackend().evaluate(p, spec, mat)
    P = 25 * G * spec.dynamic_factor
    I = 60 * 12**3 / 12
    assert r.completed
    assert r.max_deflection_mm == pytest.approx(P * 300**3 / (3 * mat.youngs_modulus_mpa * I), rel=1e-4)
    sig = 6 * P * 300 / (60 * 12**2)
    tau = 1.5 * P / (60 * 12)
    assert r.max_von_mises_mpa == pytest.approx(np.sqrt(sig**2 + 3 * tau**2), rel=1e-3)
    assert r.mass_kg == pytest.approx(300 * 60 * 12 * 1e-9 * mat.density_kg_m3, rel=1e-6)


def test_rib_stiffens():
    spec = parse_requirements(PROMPT).with_defaults()
    mat = MATERIALS[spec.material_key]
    b = AnalyticalBeamBackend()
    a = b.evaluate(BracketParams(300, 60, 8, 8, 0.0, 300), spec, mat)
    c = b.evaluate(BracketParams(300, 60, 8, 8, 60.0, 300), spec, mat)
    assert c.max_deflection_mm < a.max_deflection_mm and c.mass_kg > a.mass_kg


def test_pareto_mask():
    pts = np.array([[1, 5], [2, 2], [5, 1], [3, 3], [6, 6]], float)
    assert pareto_front(pts).tolist() == [True, True, True, False, False]


def test_design_space_sampling_in_bounds():
    spec = parse_requirements(PROMPT).with_defaults()
    sp = build_bracket_space(spec)
    x = sp.sample(50, seed=1)
    lo, hi = np.array(sp.bounds).T
    assert (x >= lo).all() and (x <= hi).all()


def test_thin_tall_rib_is_rejected_by_slenderness_screen():
    spec = parse_requirements(PROMPT).with_defaults()
    unsafe = BracketParams(300, 60, 8, 3, 90, 250)
    safe = BracketParams(300, 60, 8, 6, 90, 250)
    assert any("rib slenderness" in issue for issue in validate_geometry(unsafe, spec))
    assert not any("rib slenderness" in issue for issue in validate_geometry(safe, spec))


def test_msh2_stats_counts_tetrahedra(tmp_path):
    mesh = tmp_path / "one-tet.msh"
    mesh.write_text("""$MeshFormat\n2.2 0 8\n$EndMeshFormat\n$Nodes\n4\n1 0 0 0\n2 1 0 0\n3 0 1 0\n4 0 0 1\n$EndNodes\n$Elements\n2\n1 2 0 1 2 3\n2 4 0 1 2 3 4\n$EndElements\n""")
    stats = msh2_stats(mesh)
    assert (stats.nodes, stats.elements, stats.tetrahedra) == (4, 2, 1)


def test_material_comparison_recommends_lighter_candidate():
    aluminium = {"material": "AL6061-T6", "design_id": "A", "mass_kg": 1.0,
                 "max_deflection_mm": 0.8, "max_von_mises_mpa": 100.0,
                 "factor_of_safety": 2.5, "cost_proxy": 10.0, "width_mm": 30.0,
                 "thickness_mm": 5.0, "rib_thickness_mm": 5.0, "rib_height_mm": 50.0}
    steel = {**aluminium, "material": "STEEL-A36", "design_id": "S", "mass_kg": 2.0,
             "max_deflection_mm": 0.4, "cost_proxy": 5.0}
    report = material_comparison_markdown(aluminium, steel)
    assert "select **AL6061-T6**" in report


def test_end_to_end_and_reproducible(tmp_path):
    r1 = run_design(PROMPT, allow_defaults=True, n_samples=300, de_maxiter=10, out_dir=str(tmp_path / "a"))
    r2 = run_design(PROMPT, allow_defaults=True, n_samples=300, de_maxiter=10, out_dir=str(tmp_path / "b"))
    assert r1.status == RunStatus.FEASIBLE_FOUND
    assert r1.best_id == r2.best_id                      # same seed => same result
    assert r1.best_params is not None and r1.best_params["arm_length_mm"] == 300
    assert (tmp_path / "a" / "report.md").exists() and (tmp_path / "a" / "records.jsonl").exists()
    assert "not** a safety certification" in r1.report_md
    stls = list((tmp_path / "a" / "cad").glob("*.stl"))
    assert stls and stls[0].read_text().startswith("solid")


def test_infeasible_reported_honestly():
    r = run_design("500 kg payload, 1500 mm from the wall, aluminium, max deflection 0.1 mm",
                   allow_defaults=True, n_samples=200, de_maxiter=5)
    assert r.status == RunStatus.NO_FEASIBLE and "No feasible candidate" in r.report_md
