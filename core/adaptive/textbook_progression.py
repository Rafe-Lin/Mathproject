# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_POLY_PATH = PROJECT_ROOT / "configs" / "adaptive" / "textbook_progression_polynomial.yaml"
POLY_SKILL_ID = "jh_\u6578\u5b782\u4e0a_FourArithmeticOperationsOfPolynomial"
_CACHE: dict[str, dict[str, Any]] = {}

DEFAULT_POLY_PROGRESSION: dict[str, Any] = {
    "unit_skill_id": POLY_SKILL_ID,
    "mainline_sequence": ["F1", "F2", "F5", "F11", "F9", "F10"],
    "assessment_sequence": ["F1", "F2", "F5", "F11", "F7", "F8", "F9", "F10"],
    "families": {
        "F1": {
            "family_name": "poly_add_sub_flat",
            "difficulty_level": 1,
            "textbook_examples": ["P.6 例1", "P.7 例2", "P.8 例3"],
            "main_subskills": ["combine_like_terms", "normalize_terms"],
            "prerequisite_candidates": ["add_sub", "sign_handling", "mul_div", "order_of_operations"],
            "prerequisite_candidate_descriptions": {
                "add_sub": "基礎整數加減流程不穩，常在係數或常數項運算時出錯",
                "sign_handling": "正負號處理不穩，常在異號合併或去括號時出錯",
                "mul_div": "基礎乘除概念薄弱，影響係數運算",
                "order_of_operations": "整理與合併步驟常顛倒，導致中間式失真",
            },
            "next_on_success": "F2",
            "fallback_on_repeat_failure": "F1",
        },
        "F2": {
            "family_name": "poly_add_sub_nested",
            "difficulty_level": 2,
            "textbook_examples": ["P.9 例4", "P.9 例5"],
            "main_subskills": ["sign_distribution", "combine_like_terms"],
            "prerequisite_candidates": [
                "outer_minus_scope",
                "monomial_distribution",
                "like_term_combination",
                "nested_bracket_scope",
                "order_of_operations",
                "structure_isomorphism",
                "combine_after_distribution",
            ],
            "prerequisite_candidate_descriptions": {
                "outer_minus_scope": "括號前有負號時，拆括號後每一項都要變號，常只改到第一項。",
                "monomial_distribution": "分配律展開不完整，常漏乘括號內某些項目。",
                "like_term_combination": "去括號後同類項判斷錯，常把不同項誤合併。",
                "nested_bracket_scope": "巢狀括號層次辨識不穩，常在中途漏改符號。",
                "order_of_operations": "括號與展開後的步驟順序混亂，常跳步。",
                "structure_isomorphism": "題目外觀改變後，無法辨識其實是同一種去括號結構。",
                "combine_after_distribution": "分配律做完後，無法穩定接續同類項合併。",
            },
            "next_on_success": "F5",
            "fallback_on_repeat_failure": "F1",
        },
        "F5": {
            "family_name": "poly_mul_poly",
            "difficulty_level": 3,
            "textbook_examples": ["P.36 例題1", "P.37 例題2", "P.38 例題3", "P.39 例題4"],
            "main_subskills": ["expand_binomial", "sign_distribution", "combine_like_terms"],
            "prerequisite_candidates": [
                "power_notation_basics",
                "signed_power_interpretation",
                "power_precedence_in_mixed_ops",
                "same_base_multiplication_rule",
                "power_of_power_rule",
                "product_power_distribution",
                "mul_div",
                "expand_structure",
                "sign_handling",
                "add_sub",
                "order_of_operations",
                "combine_after_distribution",
            ],
            "prerequisite_candidate_descriptions": {
                "mul_div": "展開時係數乘法、符號乘法與約簡常出錯。",
                "expand_structure": "雙括號展開會漏項或重複乘，結構骨架不穩。",
                "sign_handling": "異號項相乘後符號判斷不穩，正負常反。",
                "add_sub": "展開後合併同類項時，整數加減容易失分。",
                "order_of_operations": "展開與合併的先後順序混亂，步驟銜接不順。",
                "combine_after_distribution": "已展開但未正確整理同類項，化簡收斂失敗。",
            },
            "next_on_success": "F11",
            "fallback_on_repeat_failure": "F2",
        },
        "F11": {
            "family_name": "poly_mixed_simplify",
            "difficulty_level": 4,
            "textbook_examples": ["P.47 例題10", "P.48 例題11", "P.50 自我評量5"],
            "main_subskills": ["expand_binomial", "combine_like_terms", "family_isomorphism"],
            "prerequisite_candidates": [
                "power_notation_basics",
                "signed_power_interpretation",
                "power_precedence_in_mixed_ops",
                "same_base_multiplication_rule",
                "power_of_power_rule",
                "product_power_distribution",
                "nested_bracket_scope",
                "structure_isomorphism",
                "outer_minus_scope",
                "monomial_distribution",
                "like_term_combination",
                "order_of_operations",
                "bracket_scope",
                "sign_handling",
                "mul_div",
                "add_sub",
                "combine_after_distribution",
                "expand_structure",
            ],
            "prerequisite_candidate_descriptions": {
                "nested_bracket_scope": "多層括號巢狀結構拆解不穩，常在中層就失焦。",
                "structure_isomorphism": "題型變形後無法對齊已學過的解題骨架。",
                "outer_minus_scope": "外層負號跨括號作用錯誤，常只改部分項目。",
                "monomial_distribution": "分配律展開不完整，遺漏乘到某些項目。",
                "like_term_combination": "多步驟後同類項辨識不穩，合併對象常配錯。",
                "order_of_operations": "混合化簡時先後次序不穩，常在中途偏題。",
                "bracket_scope": "多層括號作用範圍判斷錯，導致整串變號失真。",
                "sign_handling": "多步驟中符號持續追蹤失誤，最後答案正負反轉。",
                "mul_div": "展開或係數運算中的乘除流程不穩，造成中間項錯誤。",
                "add_sub": "最後收斂同類項時，加減運算不穩定。",
                "combine_after_distribution": "分配律後續合併流程卡住，無法完成整理。",
                "expand_structure": "需要先展開再化簡時，展開架構掌握不足。",
            },
            "next_on_success": "F9",
            "fallback_on_repeat_failure": "F5",
        },
        "F9": {
            "family_name": "poly_div_poly_qr",
            "difficulty_level": 5,
            "textbook_examples": [],
            "main_subskills": ["quotient_remainder_format"],
            "prerequisite_candidates": [],
            "prerequisite_candidate_descriptions": {},
            "next_on_success": "F10",
            "fallback_on_repeat_failure": "F11",
        },
        "F10": {
            "family_name": "poly_div_reverse",
            "difficulty_level": 6,
            "textbook_examples": [],
            "main_subskills": ["reverse_division_reconstruction"],
            "prerequisite_candidates": [],
            "prerequisite_candidate_descriptions": {},
            "next_on_success": None,
            "fallback_on_repeat_failure": "F9",
        },
    },
    "completion_gate": {
        "required_core_families": ["F1", "F2", "F5", "F11"],
        "optional_extension_families": ["F6", "F7", "F8", "F9", "F10"],
        "integrative_family_id": "F11",
        "assessment": {
            "required_core_families": ["F1", "F2", "F5", "F11", "F7", "F8", "F9", "F10"],
            "minimum_covered_core_families": 8,
            "minimum_passed_core_families": 8,
            "require_integrative_family_pass": False,
        },
        "teaching": {
            "required_core_families": ["F1", "F2", "F5", "F11", "F9", "F10"],
            "minimum_covered_core_families": 6,
            "minimum_passed_core_families": 6,
            "require_integrative_family_pass": True,
            "integrative_family_id": "F10",
        },
    },
}


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




def _is_polynomial_skill_id(skill_id: str) -> bool:
    key = str(skill_id or "").strip()
    if not key:
        return False
    return key == POLY_SKILL_ID or key.endswith("FourArithmeticOperationsOfPolynomial")


def _families(cfg: dict[str, Any]) -> dict[str, dict[str, Any]]:
    raw = cfg.get("families", {})
    if not isinstance(raw, dict):
        return {}
    out: dict[str, dict[str, Any]] = {}
    for family_id, payload in raw.items():
        if isinstance(payload, dict):
            out[str(family_id)] = dict(payload)
    return out


def load_textbook_progression(skill_id: str) -> dict[str, Any]:
    key = str(skill_id or "").strip()
    if not key:
        return {}
    if key in _CACHE:
        return dict(_CACHE[key])
    if not _is_polynomial_skill_id(key):
        _CACHE[key] = {}
        return {}
    payload = _load_yaml(DEFAULT_POLY_PATH)
    if not payload:
        payload = dict(DEFAULT_POLY_PROGRESSION)
    unit_skill_id = str(payload.get("unit_skill_id", "")).strip()
    if unit_skill_id and not _is_polynomial_skill_id(unit_skill_id):
        _CACHE[key] = {}
        return {}
    if "mainline_sequence" not in payload and "demo_mainline_sequence" in payload:
        payload["mainline_sequence"] = list(payload.get("demo_mainline_sequence") or [])
    _CACHE[key] = payload
    return dict(payload)


def get_mainline_sequence(skill_id: str) -> list[str]:
    cfg = load_textbook_progression(skill_id)
    seq = cfg.get("mainline_sequence", [])
    if not isinstance(seq, list):
        return []
    return [str(x).strip() for x in seq if str(x).strip()]


def get_family_config(skill_id: str, family_id: str) -> dict[str, Any]:
    families = _families(load_textbook_progression(skill_id))
    return dict(families.get(str(family_id or "").strip(), {}))


def get_next_family(skill_id: str, current_family: str) -> str | None:
    row = get_family_config(skill_id, current_family)
    value = str(row.get("next_on_success", "")).strip()
    return value or None


def get_previous_family(skill_id: str, current_family: str) -> str | None:
    row = get_family_config(skill_id, current_family)
    value = str(row.get("fallback_on_repeat_failure", "")).strip()
    return value or None


def get_prerequisite_candidates(skill_id: str, current_family: str) -> list[dict[str, Any]]:
    row = get_family_config(skill_id, current_family)
    codes = row.get("prerequisite_candidates", [])
    desc_map = row.get("prerequisite_candidate_descriptions", {})
    if not isinstance(codes, list):
        return []
    if not isinstance(desc_map, dict):
        desc_map = {}
    out: list[dict[str, Any]] = []
    for code in codes:
        key = str(code or "").strip()
        if not key:
            continue
        out.append(
            {
                "diagnosis_label": key,
                "runtime_subskill": key,
                "code": key,
                "description": str(desc_map.get(key, "") or ""),
            }
        )
    return out


def get_completion_gate(skill_id: str) -> dict[str, Any]:
    cfg = load_textbook_progression(skill_id)
    gate = cfg.get("completion_gate", {})
    if not isinstance(gate, dict):
        return {}
    return dict(gate)
