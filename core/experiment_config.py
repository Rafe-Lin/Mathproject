from __future__ import annotations

from typing import Any

EXP1_SUCCESS_THRESHOLD = 0.80

STUDENT_GROUP_CONFIG: dict[str, dict[str, Any]] = {
    "careless": {
        "display_name": "Careless (B+,B++)",
        "mastery_range": (0.68, 0.80),
        "description": "High-start learners with unstable performance due to slips or minor errors.",
        "narrative": "Push near-threshold learners across the mastery boundary",
    },
    "average": {
        "display_name": "Average (B)",
        "mastery_range": (0.50, 0.68),
        "description": "Mid-level learners with partially formed knowledge structures.",
        "narrative": "Stabilize and strengthen core understanding",
    },
    "weak": {
        "display_name": "Weak (C)",
        "mastery_range": (0.20, 0.50),
        "description": "Low-start learners lacking prerequisite skills.",
        "narrative": "Lift foundational skills through remediation",
    },
}

GROUP_ORDER = ["careless", "average", "weak"]
CANONICAL_STUDENT_TYPES = ["Careless", "Average", "Weak"]
_CANONICAL_TO_KEY = {"Careless": "careless", "Average": "average", "Weak": "weak"}
_KEY_TO_CANONICAL = {v: k for k, v in _CANONICAL_TO_KEY.items()}


def normalize_group_key(value: str) -> str:
    raw = str(value).strip().lower()
    mapping = {
        "careless": "careless",
        "average": "average",
        "weak": "weak",
        "high": "careless",
        "mid": "average",
        "low": "weak",
        "weak foundation": "weak",
        "weak_foundation": "weak",
    }
    if raw in mapping:
        return mapping[raw]
    if value in _CANONICAL_TO_KEY:
        return _CANONICAL_TO_KEY[str(value)]
    return raw


def canonical_student_type(value: str) -> str:
    key = normalize_group_key(value)
    return _KEY_TO_CANONICAL.get(key, str(value))


def display_student_group(value: str) -> str:
    key = normalize_group_key(value)
    cfg = STUDENT_GROUP_CONFIG.get(key)
    if cfg:
        return str(cfg["display_name"])
    return str(value)


def get_group_mastery_range(value: str) -> tuple[float, float]:
    key = normalize_group_key(value)
    cfg = STUDENT_GROUP_CONFIG.get(key)
    if not cfg:
        return (0.50, 0.68)
    low, high = cfg["mastery_range"]
    return float(low), float(high)


def get_group_narrative(group_key: str) -> str:
    key = normalize_group_key(group_key)
    cfg = STUDENT_GROUP_CONFIG.get(key, {})
    return str(cfg.get("narrative", ""))


def student_group_display_order() -> list[str]:
    return [display_student_group(k) for k in GROUP_ORDER]


def validate_group_config() -> None:
    for g in GROUP_ORDER:
        assert g in STUDENT_GROUP_CONFIG
        min_val, max_val = STUDENT_GROUP_CONFIG[g]["mastery_range"]
        assert 0 <= float(min_val) < float(max_val) <= 1
    assert EXP1_SUCCESS_THRESHOLD == 0.80
