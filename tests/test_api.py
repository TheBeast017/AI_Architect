from fastapi.testclient import TestClient
from engagent.api.main import app

c = TestClient(app)


def test_health():
    assert c.get("/health").json() == {"ok": True}


def test_presentation_ui_is_served():
    page = c.get("/")
    assert page.status_code == 200
    assert "prosBuilder" in page.text


def test_parse_and_run():
    t = "25 kg payload, 300 mm from the wall, aluminium, max deflection 1 mm"
    assert c.post("/spec/parse", json={"text": t}).json()["payload_mass_kg"] == 25
    r = c.post("/design/run", json={"text": t, "allow_defaults": True, "n_samples": 150}).json()
    assert r["status"] == "feasible_found"
