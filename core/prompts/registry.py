# -*- coding: utf-8 -*-
"""Prompt registry with DB-first lookup and safe rendering."""

from core.prompts.default_templates import DEFAULT_PROMPT_TEMPLATES


def get_prompt_template(prompt_key):
    """Get prompt text by key. DB active template first, then defaults."""
    key = str(prompt_key or "").strip()
    if not key:
        raise ValueError("prompt_key is required")

    try:
        from models import PromptTemplate

        row = (
            PromptTemplate.query.filter_by(prompt_key=key, is_active=True)
            .first()
        )
        if row and isinstance(row.content, str) and row.content.strip():
            return row.content
    except Exception:
        # No app context / DB unavailable: continue to default fallback.
        pass

    default_item = DEFAULT_PROMPT_TEMPLATES.get(key)
    if isinstance(default_item, dict):
        default_content = default_item.get("content")
        if isinstance(default_content, str) and default_content.strip():
            return default_content

    raise KeyError(f"Prompt template not found: {key}")


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
