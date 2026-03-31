# -*- coding: utf-8 -*-
from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = PROJECT_ROOT / "docs"
TEMPLATE_PATH = PROJECT_ROOT / "templates" / "adaptive_practice_v2.html"
OUTPUT_CATALOG_JSON = PROJECT_ROOT / "configs" / "skill_breakpoint_catalog.json"
OUTPUT_UI_MAP_JSON = PROJECT_ROOT / "configs" / "skill_breakpoint_ui_map.json"

SKILL_ID_FALLBACKS: dict[str, str] = {
    "FourArithmeticOperationsOfIntegers": "jh_數學1上_FourArithmeticOperationsOfIntegers",
    "FourArithmeticOperationsOfNumbers": "jh_數學1上_FourArithmeticOperationsOfNumbers",
    "FourArithmeticOperationsOfPolynomial": "jh_數學2上_FourArithmeticOperationsOfPolynomial",
    "FourOperationsOfRadicals": "jh_數學2上_FourOperationsOfRadicals",
    "OperationsOnLinearExpressions": "jh_數學1上_OperationsOnLinearExpressions",
}

SUBSKILL_FALLBACKS: dict[str, dict[str, str]] = {
    "power_notation_basics": {"label": "乘方記法（底數與次方）", "hint": "先看底數是誰，再看幾次方。"},
    "signed_power_interpretation": {"label": "負數乘方判讀（括號內外）", "hint": "(-a)^n 與 -a^n 意義不同。"},
    "parenthesized_negative_base": {"label": "負底數乘方（含括號）", "hint": "負號在括號內，整體一起做次方。"},
    "minus_outside_power": {"label": "外層負號與次方", "hint": "先做次方，再處理外面的負號。"},
    "power_precedence_in_mixed_ops": {"label": "乘方優先順序", "hint": "先次方，再乘除，最後加減。"},
    "signed_power_evaluation": {"label": "正負乘方值計算", "hint": "先判斷符號位置，再算數值。"},
    "mixed_power_arithmetic": {"label": "乘方混合運算", "hint": "每一步都依運算順序完成。"},
    "same_base_multiplication_rule": {"label": "同底數相乘（指數相加）", "hint": "同底數相乘，指數直接相加。"},
    "power_building_from_repetition": {"label": "重複乘法轉次方", "hint": "觀察相同因數重複幾次。"},
    "power_of_power_rule": {"label": "冪的冪（指數相乘）", "hint": "外次方乘上內次方。"},
    "product_power_distribution": {"label": "積的冪分配", "hint": "把次方分配到每個因數。"},
    "fraction_power_distribution": {"label": "分數積的冪分配", "hint": "分子分母都要同次方。"},
}


def _find_catalog_csv() -> Path:
    for path in DOCS_ROOT.glob("*/skill_breakpoint_catalog.csv"):
        return path
    raise FileNotFoundError("docs/*/skill_breakpoint_catalog.csv not found")


def _read_csv_records() -> list[dict[str, Any]]:
    path = _find_catalog_csv()
    with path.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def _canonical_skill_id(raw_skill_id: str) -> str:
    key = str(raw_skill_id or "").strip()
    for suffix, canonical in SKILL_ID_FALLBACKS.items():
        if key.endswith(suffix):
            return canonical
    return key


def _friendly_label(key: str) -> str:
    short = str(key or "").split(".")[-1].strip()
    return short.replace("_", " ").strip()


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
            "label": str(label).strip(),
            "hint": str(hint).strip(),
        }
    return out


def _load_template_subskill_map() -> dict[str, dict[str, str]]:
    if not TEMPLATE_PATH.exists():
        return {}
    text = TEMPLATE_PATH.read_text(encoding="utf-8")
    return _parse_subskill_ui_map_from_template(text)


def _resolve_subskill_ui(subskill_key: str, template_map: dict[str, dict[str, str]]) -> dict[str, str]:
    key = str(subskill_key or "").strip()
    short = key.split(".")[-1]
    ui = template_map.get(key) or template_map.get(short) or SUBSKILL_FALLBACKS.get(short) or {}
    label = str(ui.get("label") or _friendly_label(short))
    hint = str(ui.get("hint") or "先確認觀念，再一步一步計算。")
    return {"label": label, "hint": hint}


def _build_payload(records: list[dict[str, Any]], template_map: dict[str, dict[str, str]]) -> tuple[dict[str, Any], dict[str, Any]]:
    skills: dict[str, Any] = {}
    flat: dict[str, Any] = {}

    for row in records:
        skill_id = _canonical_skill_id(str(row.get("skill_id") or ""))
        if not skill_id:
            continue
        family_id = str(row.get("family_id") or "").strip()
        if not family_id:
            continue
        family_name = str(row.get("family_name") or "").strip()
        skill_label = str(row.get("skill_name") or "").strip() or skill_id
        family_label = str(row.get("theme") or "").strip() or family_name or family_id
        subskills_raw = str(row.get("subskill_nodes") or "")
        subskills = [part.strip() for part in subskills_raw.split(";") if part.strip()]

        skill_bucket = skills.setdefault(
            skill_id,
            {"label": skill_label, "families": {}, "subskills": {}},
        )

        subskill_labels: list[str] = []
        for subskill_key in subskills:
            ui = _resolve_subskill_ui(subskill_key, template_map)
            label = ui["label"]
            hint = ui["hint"]
            display_text = f"偵測學習斷點：{label}｜提示：{hint}"
            skill_bucket["subskills"][subskill_key] = {
                "label": label,
                "hint": hint,
                "display_text": display_text,
            }
            flat[subskill_key] = {"label": label, "hint": hint}
            subskill_labels.append(label)

        skill_bucket["families"][family_id] = {
            "family_id": family_id,
            "family_name_en": family_name,
            "label": family_label,
            "subskills": subskills,
            "subskill_labels": subskill_labels,
        }

    return {"skills": skills}, flat


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    # Keep UTF-8 + ensure_ascii=False so Chinese labels/hints remain human-readable.
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def main() -> None:
    # Pipeline: docs/*/skill_breakpoint_catalog.csv -> configs/skill_breakpoint_*.json
    records = _read_csv_records()
    template_map = _load_template_subskill_map()
    catalog_json, ui_map_json = _build_payload(records, template_map)
    _write_json(OUTPUT_CATALOG_JSON, catalog_json)
    _write_json(OUTPUT_UI_MAP_JSON, ui_map_json)
    print(
        f"[ok] wrote {OUTPUT_CATALOG_JSON} + {OUTPUT_UI_MAP_JSON} "
        f"(skills={len(catalog_json.get('skills', {}))}, subskills={len(ui_map_json)})"
    )


if __name__ == "__main__":
    main()
