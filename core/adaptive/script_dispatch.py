# -*- coding: utf-8 -*-
from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

from .manifest_registry import load_manifest, resolve_script_path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ADAPTIVE_SCRIPT_ROOT = PROJECT_ROOT / "skills" / "adaptive"
DEFAULT_ENTRYPOINTS = ("generate", "generate_question", "build_question")


def _normalize_path(script_path: str) -> Path:
    p = Path(script_path)
    return p if p.is_absolute() else (PROJECT_ROOT / p)


def _scan_adaptive_scripts() -> dict[tuple[str, str], Path]:
    out: dict[tuple[str, str], Path] = {}
    if not ADAPTIVE_SCRIPT_ROOT.exists():
        return out
    for path in ADAPTIVE_SCRIPT_ROOT.glob("*.py"):
        parts = path.stem.split("__")
        if len(parts) < 3:
            continue
        skill_id = str(parts[0]).strip()
        family_id = str(parts[1]).strip()
        if not skill_id or not family_id:
            continue
        out[(skill_id, family_id)] = path
    return out


def resolve_adaptive_script(skill_id: str, family_id: str) -> tuple[Path | None, str]:
    skill_key = str(skill_id or "").strip()
    family_key = str(family_id or "").strip()
    if not skill_key or not family_key:
        return None, "invalid_key"

    manifest_path = resolve_script_path(family_key, skill_id=skill_key)
    if manifest_path:
        path = _normalize_path(manifest_path)
        if path.exists():
            return path, "manifest"

    try:
        # Load once to respect explicit registry entries where path may be relative/custom.
        for entry in load_manifest():
            if entry.skill_id == skill_key and entry.family_id == family_key:
                path = _normalize_path(entry.script_path)
                if path.exists():
                    return path, "manifest_scan"
                return None, "manifest_path_missing"
    except Exception:
        pass

    scanned = _scan_adaptive_scripts()
    path = scanned.get((skill_key, family_key))
    if path and path.exists():
        return path, "filesystem_registry"
    return None, "not_found"


def call_adaptive_script(skill_id: str, family_id: str, *, level: int = 1) -> dict[str, Any]:
    path, source = resolve_adaptive_script(skill_id, family_id)
    out: dict[str, Any] = {
        "resolved_module_path": str(path) if path else "",
        "resolve_source": source,
        "resolved_function_name": "",
        "generator_call_success": False,
        "payload_schema_valid": False,
        "payload": None,
        "error": "",
    }
    if not path:
        out["error"] = "module_not_found"
        return out

    try:
        spec = importlib.util.spec_from_file_location(f"adaptive_script_{path.stem}", path)
        if not spec or not spec.loader:
            out["error"] = "invalid_module_spec"
            return out
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except Exception as exc:
        out["error"] = f"module_import_error:{exc}"
        return out

    fn = None
    fn_name = ""
    for candidate in DEFAULT_ENTRYPOINTS:
        target = getattr(module, candidate, None)
        if callable(target):
            fn = target
            fn_name = candidate
            break
    if fn is None:
        out["error"] = "entrypoint_not_found"
        return out

    out["resolved_function_name"] = fn_name
    try:
        try:
            payload = fn(level=level)
        except TypeError:
            payload = fn()
    except Exception as exc:
        out["error"] = f"generator_call_error:{exc}"
        return out

    out["generator_call_success"] = True
    out["payload"] = payload
    out["payload_schema_valid"] = isinstance(payload, dict) and bool(
        (payload.get("question_text") or payload.get("question"))
    ) and bool(payload.get("answer") or payload.get("correct_answer"))
    return out
