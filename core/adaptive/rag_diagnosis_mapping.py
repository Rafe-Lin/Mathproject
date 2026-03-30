from __future__ import annotations

import os
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "configs" / "adaptive" / "rag_diagnosis_mapping.yaml"
LEGACY_CONFIG_PATH = PROJECT_ROOT / "configs" / "rag_diagnosis_mapping.yaml"
CONFIG_ENV_KEY = "ADAPTIVE_RAG_DIAGNOSIS_MAPPING_CONFIG"

DEFAULT_CONCEPT_TO_PREREQ: dict[str, dict[str, Any]] = {
    "negative_sign_handling": {
        "suggested_prereq_skill": "integer_arithmetic",
        "suggested_prereq_subskill": "signed_arithmetic",
        "concept_weight": 0.95,
    },
    "division_misconception": {
        "suggested_prereq_skill": "integer_arithmetic",
        "suggested_prereq_subskill": "division",
        "concept_weight": 0.9,
    },
    "basic_arithmetic_instability": {
        "suggested_prereq_skill": "integer_arithmetic",
        "suggested_prereq_subskill": "basic_operations",
        "concept_weight": 0.85,
    },
    "outer_minus_scope": {
        "suggested_prereq_skill": "integer_arithmetic",
        "suggested_prereq_subskill": "outer_minus_scope",
        "concept_weight": 0.96,
    },
    "bracket_scope_error": {
        "suggested_prereq_skill": "integer_arithmetic",
        "suggested_prereq_subskill": "outer_minus_scope",
        "concept_weight": 0.93,
    },
    "sign_distribution": {
        "suggested_prereq_skill": "integer_arithmetic",
        "suggested_prereq_subskill": "sign_distribution",
        "concept_weight": 0.92,
    },
    "sign_flip_after_distribution": {
        "suggested_prereq_skill": "integer_arithmetic",
        "suggested_prereq_subskill": "sign_handling",
        "concept_weight": 0.94,
    },
    "combine_like_terms_after_distribution": {
        "suggested_prereq_skill": "integer_arithmetic",
        "suggested_prereq_subskill": "combine_after_distribution",
        "concept_weight": 0.90,
    },
    "coefficient_arithmetic_error": {
        "suggested_prereq_skill": "integer_arithmetic",
        "suggested_prereq_subskill": "coefficient_arithmetic",
        "concept_weight": 0.91,
    },
    "nested_grouping_structure_error": {
        "suggested_prereq_skill": "integer_arithmetic",
        "suggested_prereq_subskill": "bracket_scope",
        "concept_weight": 0.89,
    },
    "binomial_expansion_structure_error": {
        "suggested_prereq_skill": "integer_arithmetic",
        "suggested_prereq_subskill": "expand_structure",
        "concept_weight": 0.90,
    },
    "mixed_simplify_transition_error": {
        "suggested_prereq_skill": "integer_arithmetic",
        "suggested_prereq_subskill": "order_of_operations",
        "concept_weight": 0.88,
    },
    "family_isomorphism_confusion": {
        "suggested_prereq_skill": "integer_arithmetic",
        "suggested_prereq_subskill": "structure_isomorphism",
        "concept_weight": 0.86,
    },
    "power_sign_parentheses_confusion": {
        "suggested_prereq_skill": "integer_arithmetic",
        "suggested_prereq_subskill": "signed_power_interpretation",
        "concept_weight": 0.90,
    },
    "power_precedence_confusion": {
        "suggested_prereq_skill": "integer_arithmetic",
        "suggested_prereq_subskill": "power_precedence_in_mixed_ops",
        "concept_weight": 0.88,
    },
    "same_base_power_rule_error": {
        "suggested_prereq_skill": "fraction_arithmetic",
        "suggested_prereq_subskill": "same_base_multiplication_rule",
        "concept_weight": 0.90,
    },
    "power_of_power_rule_error": {
        "suggested_prereq_skill": "fraction_arithmetic",
        "suggested_prereq_subskill": "power_of_power_rule",
        "concept_weight": 0.90,
    },
    "product_power_distribution_error": {
        "suggested_prereq_skill": "fraction_arithmetic",
        "suggested_prereq_subskill": "product_power_distribution",
        "concept_weight": 0.90,
    },
}
DEFAULT_SCORING: dict[str, float] = {
    "base": 0.25,
    "retrieval_weight": 0.55,
    "concept_weight": 0.20,
    "unknown_concept_weight": 0.40,
}
_CONFIG_CACHE: dict[str, Any] | None = None


def _clip01(value: Any, default: float = 0.0) -> float:
    try:
        return max(0.0, min(1.0, float(value)))
    except Exception:
        return default


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml  # type: ignore
    except Exception:
        return {}
    try:
        if not path.exists():
            return {}
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _resolve_config_path() -> Path:
    override = str(os.getenv(CONFIG_ENV_KEY, "") or "").strip()
    if override:
        return Path(override)
    if DEFAULT_CONFIG_PATH.exists():
        return DEFAULT_CONFIG_PATH
    return LEGACY_CONFIG_PATH


def _load_config() -> dict[str, Any]:
    global _CONFIG_CACHE
    if _CONFIG_CACHE is not None:
        return _CONFIG_CACHE
    raw = _load_yaml(_resolve_config_path())
    concept_map = raw.get("concept_to_prereq", {})
    scoring = raw.get("scoring", {})
    _CONFIG_CACHE = {
        "concept_to_prereq": concept_map if isinstance(concept_map, dict) else {},
        "scoring": scoring if isinstance(scoring, dict) else {},
    }
    return _CONFIG_CACHE


def _merged_concept_map() -> dict[str, dict[str, Any]]:
    cfg = _load_config().get("concept_to_prereq", {})
    merged: dict[str, dict[str, Any]] = {
        key: dict(value) for key, value in DEFAULT_CONCEPT_TO_PREREQ.items()
    }
    for key, value in cfg.items():
        if not isinstance(value, dict):
            continue
        base = dict(merged.get(str(key), {}))
        base.update(value)
        merged[str(key)] = base
    return merged


def _merged_scoring() -> dict[str, float]:
    cfg = _load_config().get("scoring", {})
    merged = dict(DEFAULT_SCORING)
    if isinstance(cfg, dict):
        for key in merged.keys():
            if key in cfg:
                merged[key] = float(cfg.get(key))
    return merged


def _reset_config_cache_for_tests() -> None:
    global _CONFIG_CACHE
    _CONFIG_CACHE = None


def _resolve_top_concept(retrieval_result: Any) -> str:
    if isinstance(retrieval_result, dict):
        if retrieval_result.get("top_concept"):
            return str(retrieval_result.get("top_concept")).strip()
        concepts = retrieval_result.get("concepts")
        if isinstance(concepts, list) and concepts:
            first = concepts[0]
            if isinstance(first, dict):
                return str(first.get("concept") or "").strip()
            return str(first).strip()
        return str(retrieval_result.get("error_concept") or "").strip()
    return ""


def _resolve_retrieval_confidence(retrieval_result: Any) -> float:
    if not isinstance(retrieval_result, dict):
        return 0.0
    if "retrieval_confidence" in retrieval_result:
        return _clip01(retrieval_result.get("retrieval_confidence"), 0.0)
    concepts = retrieval_result.get("concepts")
    if isinstance(concepts, list) and concepts:
        first = concepts[0]
        if isinstance(first, dict):
            return _clip01(first.get("score"), 0.0)
    return 0.0


def map_retrieval_to_diagnosis(
    retrieval_result: Any,
    current_skill: str,
    current_subskill: str,
) -> dict[str, Any]:
    concept_to_prereq = _merged_concept_map()
    scoring = _merged_scoring()
    top_concept = _resolve_top_concept(retrieval_result)
    retrieval_confidence = _resolve_retrieval_confidence(retrieval_result)
    mapping = concept_to_prereq.get(top_concept, {})

    suggested_prereq_skill = mapping.get("suggested_prereq_skill")
    suggested_prereq_subskill = mapping.get("suggested_prereq_subskill")
    concept_weight = _clip01(
        mapping.get("concept_weight", scoring.get("unknown_concept_weight", 0.4)),
        scoring.get("unknown_concept_weight", 0.4),
    )

    diagnosis_confidence = _clip01(
        float(scoring.get("base", 0.25))
        + (float(scoring.get("retrieval_weight", 0.55)) * retrieval_confidence)
        + (float(scoring.get("concept_weight", 0.20)) * concept_weight),
        0.0,
    )

    route_type = "stay"
    if suggested_prereq_skill and str(suggested_prereq_skill) != str(current_skill):
        route_type = "rescue"

    return {
        "version": "1.0",
        "current_skill": str(current_skill or ""),
        "current_subskill": str(current_subskill or ""),
        "top_concept": top_concept or "unknown",
        "error_concept": top_concept or "unknown",
        "retrieval_confidence": retrieval_confidence,
        "diagnosis_confidence": diagnosis_confidence,
        "suggested_prereq_skill": suggested_prereq_skill,
        "suggested_prereq_subskill": suggested_prereq_subskill,
        "route_type": route_type,
    }


