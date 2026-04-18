# -*- coding: utf-8 -*-
"""AI settings helpers for admin control center and runtime model resolution."""

from __future__ import annotations

import json
from typing import Any

from flask import current_app, has_app_context

from config import Config

AI_ROLE_KEYS = ("coder", "tutor", "vision_analyzer", "classifier", "default")

SETTING_AI_GLOBAL_STRATEGY = "ai_global_strategy"
SETTING_AI_DEFAULT_PROVIDER = "ai_default_provider"
SETTING_AI_MODEL_ROLES = "ai_model_roles"
SETTING_AI_RAG_NAIVE_THRESHOLD = "ai_rag_naive_threshold"
SETTING_AI_ENABLE_TUTOR_RESPONSE = "ai_enable_tutor_response"
SETTING_AI_ENABLE_HIGH_PRECISION_VISION = "ai_enable_high_precision_vision"

DEFAULT_AI_GLOBAL_STRATEGY = "hybrid_balanced"
DEFAULT_AI_DEFAULT_PROVIDER = str(getattr(Config, "DEFAULT_PROVIDER", "local") or "local").lower()
DEFAULT_AI_RAG_NAIVE_THRESHOLD = float(getattr(Config, "ADVANCED_RAG_NAIVE_THRESHOLD", 0.35))
DEFAULT_AI_ENABLE_TUTOR_RESPONSE = True
DEFAULT_AI_ENABLE_HIGH_PRECISION_VISION = False


def _safe_json_loads(raw: str | None) -> dict[str, Any]:
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
    except Exception:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _parse_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return bool(value)
    text = str(value).strip().lower()
    if text in ("true", "1", "yes", "on"):
        return True
    if text in ("false", "0", "no", "off"):
        return False
    return default


def _parse_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _normalize_provider(provider: Any) -> str:
    p = str(provider or "").strip().lower()
    return p if p in ("local", "google") else DEFAULT_AI_DEFAULT_PROVIDER


def _normalize_strategy(strategy: Any) -> str:
    s = str(strategy or "").strip().lower()
    if s in ("local_first", "cloud_first", "hybrid_balanced"):
        return s
    return DEFAULT_AI_GLOBAL_STRATEGY


def _get_system_setting_value(key: str) -> str | None:
    if not has_app_context():
        return None
    from models import SystemSetting

    row = SystemSetting.query.filter_by(key=key).first()
    return row.value if row else None


def set_system_setting_value(key: str, value: Any, description: str = "") -> None:
    """Upsert one SystemSetting row. Caller controls commit/rollback."""
    from models import SystemSetting

    text_value = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    row = SystemSetting.query.filter_by(key=key).first()
    if row:
        row.value = text_value
        if description:
            row.description = description
    else:
        row = SystemSetting(key=key, value=text_value, description=description)
        from models import db

        db.session.add(row)


def get_available_model_presets() -> list[dict[str, Any]]:
    options: list[dict[str, Any]] = []
    for key, cfg in Config.CODER_PRESETS.items():
        options.append(
            {
                "key": key,
                "provider": cfg.get("provider", ""),
                "model": cfg.get("model", ""),
                "description": cfg.get("description", ""),
            }
        )
    return options


def _config_role_to_preset_key(role: str) -> str | None:
    cfg = Config.MODEL_ROLES.get(role) or Config.MODEL_ROLES.get("default")
    if not isinstance(cfg, dict):
        return None
    provider = cfg.get("provider")
    model = cfg.get("model")
    for key, preset in Config.CODER_PRESETS.items():
        if preset.get("provider") == provider and preset.get("model") == model:
            return key
    return None


def _fallback_preset_for_provider(role: str, provider: str) -> str | None:
    provider = _normalize_provider(provider)
    local_pref = {
        "coder": "qwen3-8b",
        "tutor": "qwen3-8b",
        "vision_analyzer": "qwen3-vl-8b",
        "classifier": "qwen2.5-3b",
        "default": "qwen2.5-3b",
    }
    cloud_pref = {
        "coder": "gemini-3-flash",
        "tutor": "gemini-3-flash",
        "vision_analyzer": "gemini-3-flash",
        "classifier": "gemini-3-flash",
        "default": "gemini-3-flash",
    }

    if provider == "google":
        key = cloud_pref.get(role, "gemini-3-flash")
        if key in Config.CODER_PRESETS:
            return key
    else:
        key = local_pref.get(role, local_pref["default"])
        if key in Config.CODER_PRESETS:
            return key

    for k, cfg in Config.CODER_PRESETS.items():
        if str(cfg.get("provider", "")).lower() == provider:
            return k
    return None


def get_ai_settings_snapshot() -> dict[str, Any]:
    model_roles_raw = _get_system_setting_value(SETTING_AI_MODEL_ROLES)
    role_overrides = _safe_json_loads(model_roles_raw)

    sanitized_roles: dict[str, str] = {}
    for role in AI_ROLE_KEYS:
        chosen = role_overrides.get(role)
        if isinstance(chosen, str) and chosen in Config.CODER_PRESETS:
            sanitized_roles[role] = chosen

    strategy = _normalize_strategy(_get_system_setting_value(SETTING_AI_GLOBAL_STRATEGY))
    default_provider = _normalize_provider(_get_system_setting_value(SETTING_AI_DEFAULT_PROVIDER))
    rag_threshold = _parse_float(
        _get_system_setting_value(SETTING_AI_RAG_NAIVE_THRESHOLD),
        DEFAULT_AI_RAG_NAIVE_THRESHOLD,
    )
    enable_tutor = _parse_bool(
        _get_system_setting_value(SETTING_AI_ENABLE_TUTOR_RESPONSE),
        DEFAULT_AI_ENABLE_TUTOR_RESPONSE,
    )
    enable_vision = _parse_bool(
        _get_system_setting_value(SETTING_AI_ENABLE_HIGH_PRECISION_VISION),
        DEFAULT_AI_ENABLE_HIGH_PRECISION_VISION,
    )

    return {
        "ai_global_strategy": strategy,
        "ai_default_provider": default_provider,
        "ai_model_roles": sanitized_roles,
        "ai_rag_naive_threshold": rag_threshold,
        "ai_enable_tutor_response": enable_tutor,
        "ai_enable_high_precision_vision": enable_vision,
    }


def _resolve_role_preset_from_strategy(role: str, strategy: str, default_provider: str) -> str | None:
    if strategy == "local_first":
        return _fallback_preset_for_provider(role, "local")
    if strategy == "cloud_first":
        return _fallback_preset_for_provider(role, "google")

    # hybrid_balanced:
    if strategy == "hybrid_balanced" and role == "tutor":
        # Hybrid 模式下，tutor 必須是 Gemini
        return _fallback_preset_for_provider(role, "google")

    # keep current config tendency first, then provider fallback
    cfg_key = _config_role_to_preset_key(role)
    if cfg_key and cfg_key in Config.CODER_PRESETS:
        return cfg_key
    return _fallback_preset_for_provider(role, default_provider)


def get_effective_model_config(role: str) -> dict[str, Any]:
    normalized_role = role if role in AI_ROLE_KEYS else "default"
    settings = get_ai_settings_snapshot()
    ai_mode = settings.get("ai_global_strategy", "unknown")
    role_overrides = settings.get("ai_model_roles", {})

    preset_key = None
    source = "unknown"

    # Step 1: Check DB override
    override = role_overrides.get(normalized_role)
    if override in Config.CODER_PRESETS:
        preset_key = override
        source = "db_override"

    # Step 2: Strategy fallback
    if not preset_key:
        strategy_key = _resolve_role_preset_from_strategy(
            normalized_role,
            ai_mode,
            settings.get("ai_default_provider", "local"),
        )
        if strategy_key in Config.CODER_PRESETS:
            preset_key = strategy_key
            source = "global_strategy"

    # Step 3: Hardcoded defaults in config.py
    if not preset_key:
        cfg_key = _config_role_to_preset_key(normalized_role)
        if cfg_key in Config.CODER_PRESETS:
            preset_key = cfg_key
            source = "config_hardcoded"

    # Step 4: System default preset fallback
    if not preset_key:
        if Config.DEFAULT_CODER_PRESET in Config.CODER_PRESETS:
            preset_key = Config.DEFAULT_CODER_PRESET
            source = "system_default"
        else:
            preset_key = next(iter(Config.CODER_PRESETS.keys()), None)
            source = "random_fallback"

    if preset_key and preset_key in Config.CODER_PRESETS:
        cfg = dict(Config.CODER_PRESETS[preset_key])
        cfg["preset_key"] = preset_key
        
        provider = cfg.get("provider", "unknown")
        model_name = cfg.get("model", "unknown")
        
        if has_app_context():
            current_app.logger.info(
                f"[AI CONFIG RESOLVE] role={role} mode={ai_mode} source={source} "
                f"provider={provider} model={model_name}"
            )
            
        return cfg

    # Extreme fallback
    base = Config.MODEL_ROLES.get(role) or Config.MODEL_ROLES.get("default") or {}
    
    if has_app_context():
        current_app.logger.info(
            f"[AI CONFIG RESOLVE] role={role} mode={ai_mode} source=extreme_fallback "
            f"provider={base.get('provider', 'unknown')} model={base.get('model', 'unknown')}"
        )
        
    return dict(base)


def apply_ai_runtime_settings() -> None:
    """Load DB settings into current Flask app config for runtime usage."""
    if not has_app_context():
        return

    snapshot = get_ai_settings_snapshot()
    current_app.config["ADVANCED_RAG_NAIVE_THRESHOLD"] = snapshot["ai_rag_naive_threshold"]
    current_app.config["AI_GLOBAL_STRATEGY"] = snapshot["ai_global_strategy"]
    current_app.config["AI_DEFAULT_PROVIDER"] = snapshot["ai_default_provider"]
    current_app.config["AI_ENABLE_TUTOR_RESPONSE"] = snapshot["ai_enable_tutor_response"]
    current_app.config["AI_ENABLE_HIGH_PRECISION_VISION"] = snapshot["ai_enable_high_precision_vision"]
