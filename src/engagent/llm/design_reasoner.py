"""LLM design reasoner (doc 7.2). Takes interpreted spec and reasons about design constraints.

Called LLM2 in the two-stage pipeline:
  Stage 1 (LLM1): extract_spec() - interpret user request into EngineeringSpec
  Stage 2 (LLM2): reason_about_design() - take spec and produce design decisions

Install: pip install -e ".[llm]"
Set ANTHROPIC_API_KEY or GEMINI_API_KEY, model via ENGAGENT_LLM_MODEL.
"""
from __future__ import annotations
import json
import os
from typing import Literal
from ..schemas import EngineeringSpec


# Primary choice: try Gemini first (more reliable for structured JSON), then Anthropic
try:
    from google import genai
    from google.genai import types
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False


# LLM1: Requirement extraction prompt (for reference)
EXTRACTOR_SYSTEM = (
    "Extract a mechanical-design specification from the user's request. "
    "Return ONLY JSON with keys: payload_mass_kg, load_offset_mm, max_deflection_mm, material_key, "
    "safety_factor, dynamic_factor, max_width_mm, max_height_mm, min_wall_mm. "
    "Units: kg for mass, mm for all lengths. Use null for anything not explicitly stated. "
    "NEVER guess or invent values. material_key must be one of: AL6061-T6, AL7075-T6, STEEL-A36, TI-6AL-4V or null."
)

# LLM2: Design reasoning prompt
DESIGN_REASONER_SYSTEM = (
    "You are a senior mechanical design engineer. Given a bracket design specification, "
    "analyze it and output a JSON object with design decisions. Be conservative and professional. "
    "Return ONLY valid JSON with these exact keys:\n"
    "- recommended_geometry: object with 'arm_length_mm', 'width_mm', 'thickness_mm', 'rib_thickness_mm', 'rib_height_mm', 'rib_length_mm'\n"
    "- constraint_violations: array of strings describing any constraints that would be violated\n"
    "- design_notes: array of strings with engineering rationale\n"
    "- safety_margin: float (recommended safety factor adjustment from spec if different)\n"
    "- manufacturing_considerations: array of strings\n\n"
    "Do NOT invent material properties - use the spec's material. "
    "For geometry, be conservative (higher safety margin). "
    "Numbers must be between 0 and 1000 mm. Return null for any field you cannot determine."
)


class LLMExtractionResult:
    """Result of LLM-based requirement extraction."""
    def __init__(self, spec: EngineeringSpec, raw_output: str, model_used: str):
        self.spec = spec
        self.raw_output = raw_output
        self.model_used = model_used


class DesignReasonResult:
    """Result of LLM-based design reasoning."""
    def __init__(self, reason: dict, raw_output: str, model_used: str):
        self.reason = reason
        self.raw_output = raw_output
        self.model_used = model_used


def _get_model_name() -> str:
    """Get the model name from environment or default."""
    return os.getenv("ENGAGENT_LLM_MODEL", "gemini-2.0-flash" if HAS_GEMINI else "claude-sonnet-5-5")


def extract_spec(text: str, model: str | None = None) -> LLMExtractionResult:
    """LLM1: Extract spec from natural language using LLM.

    Falls back to rule-based parser if API fails.
    Returns LLMExtractionResult with the spec and metadata.
    """
    model_name = model or _get_model_name()

    # Try Gemini first if available
    if HAS_GEMINI:
        try:
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model=model_name,
                    contents=text,
                    config=types.GenerateContentConfig(
                        system_instruction=EXTRACTOR_SYSTEM,
                        temperature=0.0,
                        max_output_tokens=512,
                    ),
                )
                raw = response.text.strip()
                # Extract JSON
                if raw.startswith("```"):
                    raw = raw.split("```")[1]
                    if raw.startswith("json"):
                        raw = raw[4:]
                raw = raw.strip()
                start, end = raw.find("{"), raw.rfind("}")
                if start != -1 and end != -1:
                    data = json.loads(raw[start:end+1])
                    # Use gemini_extractor's merge logic
                    from ..requirements import parse_requirements
                    spec = parse_requirements(text)
                    from ..schemas import Provenance
                    for k, v in data.items():
                        if v is not None and hasattr(spec, k) and getattr(spec, k) is None:
                            setattr(spec, k, v)
                            spec.provenance[k] = Provenance.INFERRED
                    spec.unresolved = spec.critical_missing()
                    return LLMExtractionResult(spec, raw, model_name)
        except Exception as e:
            pass  # Fall through to try Anthropic or rule-based

    # Try Anthropic if available
    if HAS_ANTHROPIC:
        try:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                client = anthropic.Anthropic()
                msg = client.messages.create(
                    model=model_name,
                    max_tokens=500,
                    system=EXTRACTOR_SYSTEM,
                    messages=[{"role": "user", "content": text}]
                )
                raw = "".join(b.text for b in msg.content if b.type == "text").strip().strip("`")
                start = raw.find("{")
                end = raw.rfind("}") + 1
                if start != -1 and end > start:
                    data = json.loads(raw[start:end])
                    from ..requirements import parse_requirements
                    spec = parse_requirements(text)
                    from ..schemas import Provenance
                    for k, v in data.items():
                        if v is not None and hasattr(spec, k) and getattr(spec, k) is None:
                            setattr(spec, k, v)
                            spec.provenance[k] = Provenance.INFERRED
                    spec.unresolved = spec.critical_missing()
                    return LLMExtractionResult(spec, raw, model_name)
        except Exception as e:
            pass

    # Fall back to rule-based
    from ..requirements import parse_requirements
    spec = parse_requirements(text)
    return LLMExtractionResult(spec, "FALLBACK: rule-based parsing", "rule-based")


def reason_about_design(spec: EngineeringSpec, model: str | None = None) -> DesignReasonResult:
    """LLM2: Take interpreted spec and produce design decisions.

    This is the "design reasoning" step that happens before optimization.
    The LLM reasons about geometry, constraints, and safety margins.
    """
    model_name = model or _get_model_name()

    # Build the prompt with spec data
    prompt = f"""
Engineering Specification:
- Payload: {spec.payload_mass_kg} kg
- Load offset (lever arm): {spec.load_offset_mm} mm
- Max deflection: {spec.max_deflection_mm} mm
- Material: {spec.material_key}
- Safety factor: {spec.safety_factor}
- Dynamic factor: {spec.dynamic_factor}

Output ONLY valid JSON with the requested fields.
"""

    # Try Gemini first
    if HAS_GEMINI:
        try:
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=DESIGN_REASONER_SYSTEM,
                        temperature=0.0,
                        max_output_tokens=512,
                    ),
                )
                raw = response.text.strip()
                if raw.startswith("```"):
                    raw = raw.split("```")[1]
                    if raw.startswith("json"):
                        raw = raw[4:]
                raw = raw.strip()
                start, end = raw.find("{"), raw.rfind("}")
                if start != -1 and end != -1:
                    data = json.loads(raw[start:end+1])
                    return DesignReasonResult(data, raw, model_name)
        except Exception as e:
            pass

    # Try Anthropic if available
    if HAS_ANTHROPIC:
        try:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                client = anthropic.Anthropic()
                msg = client.messages.create(
                    model=model_name,
                    max_tokens=500,
                    system=DESIGN_REASONER_SYSTEM,
                    messages=[{"role": "user", "content": prompt}]
                )
                raw = "".join(b.text for b in msg.content if b.type == "text").strip().strip("`")
                start = raw.find("{")
                end = raw.rfind("}") + 1
                if start != -1 and end > start:
                    data = json.loads(raw[start:end])
                    return DesignReasonResult(data, raw, model_name)
        except Exception as e:
            pass

    # Return empty result if no LLM available
    return DesignReasonResult(
        {
            "recommended_geometry": None,
            "constraint_violations": [],
            "design_notes": ["LLM not configured - using default parameters"],
            "safety_margin": None,
            "manufacturing_considerations": []
        },
        "FALLBACK: no LLM available",
        "none"
    )