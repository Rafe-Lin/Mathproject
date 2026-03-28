# -*- coding: utf-8 -*-
from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from typing import Any
import codecs


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CATALOG_CSV_PATH = PROJECT_ROOT / "docs" / "自適應實作" / "skill_breakpoint_catalog.csv"
TEMPLATE_PATH = PROJECT_ROOT / "templates" / "adaptive_practice_v2.html"
OUTPUT_CATALOG_JSON = PROJECT_ROOT / "configs" / "skill_breakpoint_catalog.json"
OUTPUT_UI_MAP_JSON = PROJECT_ROOT / "configs" / "skill_breakpoint_ui_map.json"




def _decode_js_unicode_escapes(text: str) -> str:
    value = str(text or "")
    if "\\u" not in value:
        return value
    try:
        return codecs.decode(value, "unicode_escape")
    except Exception:
        return value

def _friendly_subskill_label(key: str) -> str:
    text = str(key or "").strip()
    if not text:
        return ""
    short = text.split(".")[-1]
    return short.replace("_", " ")


def _parse_subskill_ui_map_from_template(template_text: str) -> dict[str, dict[str, str]]:
    match = re.search(r"const\s+SUBSKILL_UI_MAP\s*=\s*\{(.*?)\};", template_text, re.S)
    if not match:
        return {}
    body = match.group(1)
    pattern = re.compile(
        r'([A-Za-z0-9_\.]+)\s*:\s*\{\s*label\s*:\s*"([^"]*)"\s*,\s*hint\s*:\s*"([^"]*)"\s*\}',
        re.S,
    )
    out: dict[str, dict[str, str]] = {}
    for key, label, hint in pattern.findall(body):
        out[str(key).strip()] = {
            "label": _decode_js_unicode_escapes(str(label)),
            "hint": _decode_js_unicode_escapes(str(hint)),
        }
    return out


def _load_subskill_ui_map() -> dict[str, dict[str, str]]:
    if not TEMPLATE_PATH.exists():
        return {}
    template_text = TEMPLATE_PATH.read_text(encoding="utf-8")
    return _parse_subskill_ui_map_from_template(template_text)


def _normalize_skill_catalog(records: list[dict[str, Any]], subskill_ui_map: dict[str, dict[str, str]]) -> dict[str, Any]:
    skills: dict[str, Any] = {}
    flat_subskills: dict[str, dict[str, str]] = {}

    for row in records:
        skill_id = str(row.get("skill_id") or "").strip()
        skill_label = str(row.get("skill_name") or "").strip() or skill_id
        family_id = str(row.get("family_id") or "").strip()
        family_name_en = str(row.get("family_name") or "").strip()
        family_label = str(row.get("theme") or "").strip() or family_name_en or family_id
        subskill_nodes_raw = str(row.get("subskill_nodes") or "")
        subskill_nodes = [part.strip() for part in subskill_nodes_raw.split(";") if part.strip()]
        if not skill_id or not family_id:
            continue

        skill_bucket = skills.setdefault(
            skill_id,
            {
                "label": skill_label,
                "families": {},
                "subskills": {},
            },
        )
        skill_bucket["label"] = skill_label

        subskill_labels: list[str] = []
        for subskill_key in subskill_nodes:
            ui = subskill_ui_map.get(subskill_key) or subskill_ui_map.get(subskill_key.split(".")[-1]) or {}
            label = str(ui.get("label") or _friendly_subskill_label(subskill_key))
            hint = str(ui.get("hint") or "先把這個子技能的規則看清楚。")
            display_text = f"偵測學習斷點：{label}｜提示：{hint}"
            skill_bucket["subskills"][subskill_key] = {
                "label": label,
                "hint": hint,
                "display_text": display_text,
            }
            flat_subskills[subskill_key] = {"label": label, "hint": hint}
            subskill_labels.append(label)

        skill_bucket["families"][family_id] = {
            "family_id": family_id,
            "family_name_en": family_name_en,
            "label": family_label,
            "subskills": subskill_nodes,
            "subskill_labels": subskill_labels,
        }

    return {"skills": skills}, flat_subskills


def _load_catalog_records() -> list[dict[str, Any]]:
    with CATALOG_CSV_PATH.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        return list(reader)


def _dump_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def main() -> None:
    records = _load_catalog_records()
    subskill_ui_map = _load_subskill_ui_map()
    catalog_json, flat_ui_map = _normalize_skill_catalog(records, subskill_ui_map)
    _dump_json(OUTPUT_CATALOG_JSON, catalog_json)
    _dump_json(OUTPUT_UI_MAP_JSON, flat_ui_map)
    print(
        f"[ok] generated {OUTPUT_CATALOG_JSON} and {OUTPUT_UI_MAP_JSON} "
        f"(skills={len(catalog_json.get('skills', {}))}, subskills={len(flat_ui_map)})"
    )


if __name__ == "__main__":
    main()

