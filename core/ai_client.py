# -*- coding: utf-8 -*-
"""Unified AI entrypoint controlled by config.py MODEL_ROLES."""

from config import Config
from core.ai_wrapper import (
    GoogleAIClient,
    LocalAIClient,
    call_ai_with_retry,
)


def _get_role_config(role: str) -> dict:
    cfg = Config.MODEL_ROLES.get(role)
    if not isinstance(cfg, dict):
        raise ValueError(f"Unknown role: {role}")
    return cfg


def call_local_model(cfg: dict, prompt: str, image_path=None, **kwargs):
    client = LocalAIClient(
        cfg.get("model"),
        cfg.get("temperature", 0.7),
        max_tokens=cfg.get("max_tokens", 4096),
        extra_body=cfg.get("extra_body", {}),
    )
    return call_ai_with_retry(client, prompt, image_path=image_path, **kwargs)


def call_google_model(cfg: dict, prompt: str, image_path=None, **kwargs):
    client = GoogleAIClient(
        cfg.get("model"),
        cfg.get("temperature", 0.7),
        max_tokens=cfg.get("max_tokens", 4096),
        safety_settings=cfg.get("safety_settings"),
    )
    return call_ai_with_retry(client, prompt, image_path=image_path, **kwargs)


def call_ai(role: str, prompt: str, image_path=None, **kwargs):
    """
    Single AI call entrypoint.
    Role->provider/model must come from Config.MODEL_ROLES only.
    """
    cfg = _get_role_config(role)
    provider = str(cfg.get("provider", "")).strip().lower()

    if provider == "local":
        return call_local_model(cfg, prompt, image_path=image_path, **kwargs)
    if provider in ("google", "gemini"):
        return call_google_model(cfg, prompt, image_path=image_path, **kwargs)

    raise ValueError(f"Unsupported provider: {provider} (role={role})")

