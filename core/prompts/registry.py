# -*- coding: utf-8 -*-
"""Prompt registry with DB-first lookup and safe rendering."""

from core.prompts.default_templates import DEFAULT_PROMPT_TEMPLATES


def get_prompt_with_source(prompt_key, system_setting_fallback_key=None):
    """
    Get prompt text by key and return (content, source).
    Lookup chain:
    1. PromptTemplate (DB)
    2. SystemSetting (Legacy DB, if system_setting_fallback_key provided)
    3. DEFAULT_PROMPT_TEMPLATES
    """
    key = str(prompt_key or "").strip()
    if not key:
        raise ValueError("prompt_key is required")

    try:
        from core.models.prompt_template import PromptTemplate

        row = (
            PromptTemplate.query.filter_by(prompt_key=key, is_active=True)
            .first()
        )
        if row and isinstance(row.content, str) and row.content.strip():
            return row.content, "db_prompt_template"
    except Exception:
        pass

    if system_setting_fallback_key:
        try:
            from models import SystemSetting
            setting = SystemSetting.query.filter_by(key=system_setting_fallback_key).first()
            if setting and isinstance(setting.value, str) and setting.value.strip():
                return setting.value, "db_system_setting"
        except Exception:
            pass

    default_item = DEFAULT_PROMPT_TEMPLATES.get(key)
    if isinstance(default_item, dict):
        default_content = default_item.get("content")
        if isinstance(default_content, str) and default_content.strip():
            return default_content, "default_template"

    raise KeyError(f"Prompt template not found: {key}")


def get_prompt_template(prompt_key, system_setting_fallback_key=None):
    """Get prompt text by key. DB active template first, then defaults."""
    content, _ = get_prompt_with_source(prompt_key, system_setting_fallback_key)
    return content


def render_prompt(prompt_key, **kwargs):
    """Render prompt by key with strict variable checks."""
    template = get_prompt_template(prompt_key)
    try:
        return template.format(**kwargs)
    except KeyError as e:
        missing = str(e).strip("'")
        raise ValueError(
            f"Missing required format variable '{missing}' for prompt '{prompt_key}'"
        ) from e
    except Exception as e:
        raise ValueError(f"Failed to render prompt '{prompt_key}': {e}") from e
