from __future__ import annotations

import os
from pathlib import Path
from typing import Any


# Centralized placeholder mapping for PPO research findings integration.
# Keep all threshold/bias knobs in this module (single source of truth).
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "configs" / "adaptive" / "policy_findings_mapping.yaml"
LEGACY_CONFIG_PATH = PROJECT_ROOT / "configs" / "policy_findings_mapping.yaml"
CONFIG_ENV_KEY = "ADAPTIVE_POLICY_FINDINGS_MAPPING_CONFIG"

DEFAULT_POLICY_FINDINGS_CONFIG: dict[str, Any] = {
    "trigger_hints": {
        "fail_streak_cross_skill_threshold": 2,
        "frustration_cross_skill_threshold": 0.70,
        "same_skill_cross_skill_threshold": 6,
    },
    "reward_hints": {
        "same_skill_streak_penalty_start": 3,
        "stagnation_penalty_scale": 0.05,
        "frustration_recovery_bonus_threshold": 0.70,
        "frustration_recovery_bonus": 0.10,
    },
    "action_prior_hints": {
        "frustration_remediate_threshold": 0.70,
        "remediate_bias": 0.20,
        "stay_bias": 0.0,
        "return_bias": 0.10,
    },
}
_CONFIG_CACHE: dict[str, Any] | None = None


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _to_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
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


def _merge_section(default_section: dict[str, Any], override_section: Any) -> dict[str, Any]:
    merged = dict(default_section)
    if isinstance(override_section, dict):
        merged.update(override_section)
    return merged


def _load_config() -> dict[str, Any]:
    global _CONFIG_CACHE
    if _CONFIG_CACHE is not None:
        return _CONFIG_CACHE
    raw = _load_yaml(_resolve_config_path())
    merged = {
        "trigger_hints": _merge_section(
            DEFAULT_POLICY_FINDINGS_CONFIG["trigger_hints"],
            raw.get("trigger_hints"),
        ),
        "reward_hints": _merge_section(
            DEFAULT_POLICY_FINDINGS_CONFIG["reward_hints"],
            raw.get("reward_hints"),
        ),
        "action_prior_hints": _merge_section(
            DEFAULT_POLICY_FINDINGS_CONFIG["action_prior_hints"],
            raw.get("action_prior_hints"),
        ),
    }
    _CONFIG_CACHE = merged
    return _CONFIG_CACHE


def _reset_config_cache_for_tests() -> None:
    global _CONFIG_CACHE
    _CONFIG_CACHE = None


def build_policy_findings_hints(
    *,
    fail_streak: int,
    frustration: float,
    same_skill_streak: int,
    cross_skill_trigger: bool,
    allowed_actions: list[str],
) -> dict[str, Any]:
    cfg = _load_config()
    trigger_cfg = cfg["trigger_hints"]
    reward_cfg = cfg["reward_hints"]
    prior_cfg = cfg["action_prior_hints"]

    fs = _to_int(fail_streak, 0)
    fr = _to_float(frustration, 0.0)
    ss = _to_int(same_skill_streak, 0)

    allow_cross_skill_by_finding = (
        fs >= _to_int(trigger_cfg["fail_streak_cross_skill_threshold"], 2)
        or fr >= _to_float(trigger_cfg["frustration_cross_skill_threshold"], 0.7)
        or ss >= _to_int(trigger_cfg["same_skill_cross_skill_threshold"], 6)
    )

    reward_hint = {
        "stagnation_penalty_bonus": 0.0,
        "recovery_bonus": 0.0,
    }
    penalty_start = _to_int(reward_cfg["same_skill_streak_penalty_start"], 3)
    penalty_scale = _to_float(reward_cfg["stagnation_penalty_scale"], 0.05)
    if ss > penalty_start:
        reward_hint["stagnation_penalty_bonus"] = -penalty_scale * float(ss - penalty_start)
    if fr >= _to_float(reward_cfg["frustration_recovery_bonus_threshold"], 0.7):
        reward_hint["recovery_bonus"] = _to_float(reward_cfg["frustration_recovery_bonus"], 0.10)

    action_prior = {
        "stay": _to_float(prior_cfg["stay_bias"], 0.0),
        "remediate": _to_float(prior_cfg["remediate_bias"], 0.0),
        "return": _to_float(prior_cfg["return_bias"], 0.0),
        "prefer_remediate": bool(
            ("remediate" in allowed_actions)
            and fr >= _to_float(prior_cfg["frustration_remediate_threshold"], 0.7)
        ),
    }

    return {
        "trigger_hints": {
            "base_cross_skill_trigger": bool(cross_skill_trigger),
            "allow_cross_skill_by_finding": bool(allow_cross_skill_by_finding),
            "effective_cross_skill_trigger": bool(cross_skill_trigger or allow_cross_skill_by_finding),
        },
        "reward_hints": reward_hint,
        "action_prior_hints": action_prior,
    }
