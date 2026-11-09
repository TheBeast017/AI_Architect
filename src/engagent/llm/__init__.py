"""LLM modules for requirement extraction and design reasoning."""
from .design_reasoner import (
    extract_spec as llm1_extract_spec,
    reason_about_design,
    LLMExtractionResult,
    DesignReasonResult,
    HAS_GEMINI,
    HAS_ANTHROPIC,
    _get_model_name,
)

__all__ = [
    "llm1_extract_spec",
    "reason_about_design",
    "LLMExtractionResult",
    "DesignReasonResult",
    "HAS_GEMINI",
    "HAS_ANTHROPIC",
    "_get_model_name",
]