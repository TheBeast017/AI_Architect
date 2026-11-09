"""FastAPI surface (doc 12.5). Long jobs should move to a worker queue (plan.md Phase 7)."""
from __future__ import annotations
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Any
from pathlib import Path
from ..agent import RunResult, run_design
from ..requirements import parse_requirements
from ..schemas import EngineeringSpec, Provenance

app = FastAPI(title="AI Engineering Agent", version="0.1.0")
STATIC_DIR = Path(__file__).with_name("static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class ParseIn(BaseModel):
    text: str
    allow_defaults: bool = False


class RunIn(BaseModel):
    text: str
    allow_defaults: bool = False
    n_samples: int = 800
    seed: int = 0
    spec_overrides: dict = {}


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/", include_in_schema=False)
def presentation_ui():
    """Presentation-oriented interface; API documentation remains at /docs."""
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/spec/parse", response_model=EngineeringSpec)
def parse(body: ParseIn):
    s = parse_requirements(body.text)
    return s.with_defaults() if body.allow_defaults else s


@app.post("/design/run")
def run(body: RunIn):
    result = run_design(
        body.text,
        allow_defaults=body.allow_defaults,
        n_samples=body.n_samples,
        seed=body.seed,
        spec_overrides=body.spec_overrides,
    )
    return result.model_dump()


@app.get("/llm/status")
def llm_status():
    """Check which LLM providers are available."""
    status = {"gemini": False, "anthropic": False, "using": "rule-based"}
    try:
        from ..llm.design_reasoner import HAS_GEMINI, HAS_ANTHROPIC, _get_model_name
        status["gemini"] = HAS_GEMINI
        status["anthropic"] = HAS_ANTHROPIC
        status["default_model"] = _get_model_name()
    except Exception:
        pass
    return status