from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from flask import current_app

from core.models.prompt_template import PromptTemplate
from models import db


class PromptSyncError(Exception):
    """Prompt 同步流程的可預期錯誤。"""


class _LiteralStr(str):
    """強制 YAML 以 block scalar 輸出多行字串。"""


class _PromptRegistryDumper(yaml.SafeDumper):
    pass


def _literal_representer(dumper: yaml.Dumper, value: _LiteralStr):
    return dumper.represent_scalar("tag:yaml.org,2002:str", value, style="|")


_PromptRegistryDumper.add_representer(_LiteralStr, _literal_representer)


def _registry_path() -> Path:
    root = Path(current_app.root_path)
    direct = root / "configs" / "prompts" / "prompt_registry.yaml"
    if direct.exists():
        return direct
    # 相容某些執行環境 root_path 在子目錄的情況
    return root.parent / "configs" / "prompts" / "prompt_registry.yaml"


def _isoformat(dt: datetime | None) -> str | None:
    if not dt:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_iso_datetime(raw: Any) -> datetime | None:
    if not raw:
        return None
    text = str(raw).strip()
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except Exception:
        return None


def _normalize_required_variables(raw_value: Any) -> list[str]:
    if raw_value is None:
        return []
    if isinstance(raw_value, list):
        return [str(item).strip() for item in raw_value if str(item).strip()]
    if isinstance(raw_value, str):
        val_str = raw_value.strip()
        if not val_str or val_str == "[]":
            return []
        try:
            if val_str.startswith("[") and val_str.endswith("]"):
                parsed = json.loads(val_str)
                if isinstance(parsed, list):
                    return [str(item).strip() for item in parsed if str(item).strip()]
        except Exception:
            pass
        return [item.strip() for item in val_str.split(",") if item and item.strip()]
    return []


def _normalize_role(raw_value: Any) -> str:
    return str(raw_value or "").strip()


def _normalize_content(raw_value: Any) -> str:
    text = str(raw_value or "")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in text.split("\n")]
    return "\n".join(lines).rstrip("\n")


def _to_yaml_safe_payload(data: Any) -> Any:
    if isinstance(data, dict):
        return {k: _to_yaml_safe_payload(v) for k, v in data.items()}
    if isinstance(data, list):
        return [_to_yaml_safe_payload(item) for item in data]
    if isinstance(data, str) and "\n" in data:
        return _LiteralStr(data)
    return data


def load_prompt_registry_yaml() -> dict[str, Any]:
    registry_path = _registry_path()
    if not registry_path.exists():
        raise FileNotFoundError(f"找不到 YAML 檔案：{registry_path}")

    try:
        raw = yaml.safe_load(registry_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise PromptSyncError(f"YAML 格式錯誤：{exc}") from exc

    if not isinstance(raw, dict):
        raise PromptSyncError("YAML 根節點必須是 dict")
    prompts = raw.get("prompts")
    if prompts is None:
        raw["prompts"] = {}
    elif not isinstance(prompts, dict):
        raise PromptSyncError("YAML prompts 欄位必須是 dict")
    return raw


def save_prompt_registry_yaml(data: dict[str, Any]) -> None:
    if not isinstance(data, dict):
        raise PromptSyncError("寫入 YAML 的資料必須是 dict")
    prompts = data.get("prompts")
    if not isinstance(prompts, dict):
        raise PromptSyncError("寫入 YAML 需包含 prompts dict")

    registry_path = _registry_path()
    if not registry_path.parent.exists():
        raise FileNotFoundError(f"YAML 目錄不存在：{registry_path.parent}")

    yaml_payload = _to_yaml_safe_payload(data)
    rendered = yaml.dump(
        yaml_payload,
        Dumper=_PromptRegistryDumper,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
        width=120,
    )
    registry_path.write_text(rendered, encoding="utf-8", newline="\n")


def export_single_prompt_to_yaml(prompt_key: str) -> dict[str, Any]:
    prompt = PromptTemplate.query.filter_by(prompt_key=prompt_key).first()
    if not prompt:
        raise PromptSyncError(f"找不到 DB prompt：{prompt_key}")

    registry = load_prompt_registry_yaml()
    prompts = registry.setdefault("prompts", {})
    existing_prompt = prompts.get(prompt_key) if isinstance(prompts.get(prompt_key), dict) else {}
    existing_metadata = existing_prompt.get("metadata", {}) if isinstance(existing_prompt.get("metadata"), dict) else {}

    updated_at = datetime.utcnow().replace(microsecond=0).isoformat()
    prev_version = existing_metadata.get("version")
    try:
        version = int(prev_version) + 1
    except Exception:
        version = 1

    prompts[prompt_key] = {
        "role": str(prompt.category or "tutor").strip() or "tutor",
        "required_variables": _normalize_required_variables(prompt.required_variables),
        "content": str(prompt.content or ""),
        "metadata": {
            "version": version,
            "updated_at": updated_at,
            "updated_by": "ui_publish",
        },
    }

    save_prompt_registry_yaml(registry)
    return {
        "success": True,
        "prompt_key": prompt_key,
        "yaml_updated_at": updated_at,
        "message": "已將目前 prompt 發布為 YAML 公版",
    }


def import_single_prompt_from_yaml(prompt_key: str) -> dict[str, Any]:
    registry = load_prompt_registry_yaml()
    prompts = registry.get("prompts", {})
    prompt_data = prompts.get(prompt_key)
    if not isinstance(prompt_data, dict):
        raise PromptSyncError(f"YAML 找不到 prompt_key：{prompt_key}")

    role = str(prompt_data.get("role", "")).strip()
    content = str(prompt_data.get("content", ""))
    required_variables = _normalize_required_variables(prompt_data.get("required_variables"))
    required_variables_str = json.dumps(required_variables, ensure_ascii=False)

    prompt = PromptTemplate.query.filter_by(prompt_key=prompt_key).first()
    is_new = False
    if not prompt:
        prompt = PromptTemplate(
            prompt_key=prompt_key,
            title=prompt_key,
            category=role or "tutor",
            description="",
            content=content,
            default_content=content,
            required_variables=required_variables_str,
            usage_context="",
            used_in="",
            example_trigger="",
            is_active=True,
        )
        db.session.add(prompt)
        is_new = True
    else:
        if role:
            prompt.category = role
        prompt.content = content
        prompt.required_variables = required_variables_str
        if not prompt.default_content:
            prompt.default_content = content
        prompt.updated_at = datetime.utcnow()

    db.session.commit()
    return {
        "success": True,
        "prompt_key": prompt_key,
        "db_updated_at": _isoformat(prompt.updated_at),
        "message": "已用 YAML 公版覆蓋資料庫版本" if not is_new else "已由 YAML 公版建立並寫入資料庫版本",
    }


def compare_prompt_db_vs_yaml(prompt_key: str) -> dict[str, Any]:
    registry = load_prompt_registry_yaml()
    prompt_yaml = (registry.get("prompts") or {}).get(prompt_key)
    yaml_exists = isinstance(prompt_yaml, dict)

    db_prompt = PromptTemplate.query.filter_by(prompt_key=prompt_key).first()
    db_exists = db_prompt is not None

    db_role = _normalize_role(db_prompt.category if db_prompt else "")
    db_required = _normalize_required_variables(db_prompt.required_variables if db_prompt else [])
    db_content = _normalize_content(db_prompt.content if db_prompt else "")

    yaml_role = _normalize_role((prompt_yaml or {}).get("role", "") if yaml_exists else "")
    yaml_required = _normalize_required_variables((prompt_yaml or {}).get("required_variables", [])) if yaml_exists else []
    yaml_content = _normalize_content((prompt_yaml or {}).get("content", "") if yaml_exists else "")

    is_different = (
        db_role != yaml_role
        or db_required != yaml_required
        or db_content != yaml_content
    )

    db_updated_at = _isoformat(db_prompt.updated_at if db_prompt else None)
    yaml_meta = (prompt_yaml or {}).get("metadata", {}) if yaml_exists else {}
    yaml_updated_at = None
    if isinstance(yaml_meta, dict):
        yaml_updated_at = str(yaml_meta.get("updated_at") or "").strip() or None
    yaml_dt = _parse_iso_datetime(yaml_updated_at)
    yaml_updated_at = _isoformat(yaml_dt)

    # 內容一致時一律視為同步，避免 ORM 更新 updated_at 造成誤判
    if not is_different:
        return {
            "prompt_key": prompt_key,
            "db_exists": db_exists,
            "yaml_exists": yaml_exists,
            "db_updated_at": db_updated_at,
            "yaml_updated_at": yaml_updated_at,
            "has_yaml_update": False,
            "has_db_update": False,
            "is_different": False,
            "status": "synced",
        }

    db_dt = _parse_iso_datetime(db_updated_at)
    has_yaml_update = False
    has_db_update = False
    status = "different"
    if db_exists and yaml_exists and db_dt and yaml_dt:
        has_yaml_update = yaml_dt > db_dt
        has_db_update = db_dt > yaml_dt
        if has_yaml_update:
            status = "yaml_newer"
        elif has_db_update:
            status = "db_newer"

    return {
        "prompt_key": prompt_key,
        "db_exists": db_exists,
        "yaml_exists": yaml_exists,
        "db_updated_at": db_updated_at,
        "yaml_updated_at": yaml_updated_at,
        "has_yaml_update": has_yaml_update,
        "has_db_update": has_db_update,
        "is_different": is_different,
        "status": status,
    }
