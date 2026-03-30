# -*- coding: utf-8 -*-
from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from .catalog_loader import load_catalog
from .schema import CatalogEntry


PROJECT_ROOT = Path(__file__).resolve().parents[2]
AGENT_SKILL_DIR = PROJECT_ROOT / "agent_skills"
SKILLS_DIR = PROJECT_ROOT / "skills"


@dataclass(frozen=True)
class HintBlock:
    title: str
    intro: str
    mistakes: tuple[str, ...]
    example: str
    next_step: str


NODE_LABELS: dict[str, str] = {
    "sign_handling": "正負號判讀",
    "add_sub": "整數加減",
    "mul_div": "整數乘除",
    "mixed_ops": "四則混合",
    "order_of_operations": "運算順序",
    "bracket_scope": "括號範圍",
    "absolute_value": "絕對值",
    "exact_divisibility": "整除判斷",
    "isomorphic_structure": "結構對應",
    "proper_improper_fraction": "真分數與假分數",
    "mixed_numbers": "帶分數",
    "sign_normalization": "符號整理",
    "decimal_to_fraction_exact_conversion": "小數轉分數",
    "simplest_form_reduction": "最簡分數",
    "equivalent_fraction_scaling": "等值分數",
    "reciprocal_transform": "倒數",
    "preserve_value_invariance": "值不變原則",
    "positive_fraction_comparison": "正分數比較",
    "negative_fraction_comparison": "負分數比較",
    "mixed_number_comparison": "帶分數比較",
    "multiply": "乘法",
    "divide": "除法",
    "nested_parentheses": "多層括號",
    "decimal_fraction_mixed_arithmetic": "小數分數混合運算",
    "remaining_amount": "剩餘量",
    "container_weight": "容器重量",
    "before_after_ratio": "前後比",
    "share_comparison": "份數比較",
    "normalize_terms": "項目整理",
    "combine_like_terms": "合併同類項",
    "sign_distribution": "負號分配",
    "expand_monomial": "單項式展開",
    "expand_binomial": "二項式展開",
    "special_identity": "特殊乘法公式",
    "long_division": "長除法",
    "quotient_remainder_format": "商與餘數",
    "reverse_division_reconstruction": "反推除法",
    "geometry_formula": "幾何公式",
    "composite_region_modeling": "複合圖形建模",
    "family_isomorphism": "題型同構",
    "simplify": "化簡",
    "multiply_terms": "項乘項",
    "divide_terms": "因式約分",
    "distribute": "分配律",
    "binomial_expand": "展開公式",
    "conjugate_rationalize": "共軛有理化",
    "fractional_radical": "根式分數",
    "mixed_number_radical": "根式帶分數",
    "structure_isomorphism": "結構同構",
    "power_notation_basics": "????",
    "signed_power_interpretation": "??????",
    "parenthesized_negative_base": "?????",
    "minus_outside_power": "???????",
    "power_precedence_in_mixed_ops": "??????",
    "signed_power_evaluation": "???????",
    "mixed_power_arithmetic": "??????",
    "same_base_multiplication_rule": "???????????",
    "power_building_from_repetition": "???????",
    "power_of_power_rule": "???",
    "product_power_distribution": "?????",
    "fraction_power_distribution": "???????",
}


DOMAIN_HINTS: dict[str, HintBlock] = {
    "integer": HintBlock(
        title="整數單元提示",
        intro="先看正負號，再看運算順序。整數題常見問題都是看錯號、算錯順序或漏掉括號。",
        mistakes=("先加後減", "把負號當成減號", "忽略括號中的正負號"),
        example="例如：4 + (-7) 先看成 4 再減 7。",
        next_step="先把題目中的數字和符號圈出來，再一項一項算。",
    ),
    "fraction": HintBlock(
        title="分數單元提示",
        intro="先看分母是否一樣，再決定要不要通分。分數題常卡在約分、通分、倒數和符號整理。",
        mistakes=("先亂乘分子分母", "忘記先約分", "分子分母的符號放錯"),
        example="例如：1/3 + 1/6 要先通分成 2/6 + 1/6。",
        next_step="先想：這題是加減、乘除，還是要先通分？",
    ),
    "polynomial": HintBlock(
        title="多項式單元提示",
        intro="先看每一項的次數和符號，再決定要合併同類項、展開，還是化簡。",
        mistakes=("直接把不同次方的項合併", "展開時漏掉負號", "先算後忘記整理"),
        example="例如：x + 3x = 4x。",
        next_step="先把同類項標出來，再做整理。",
    ),
    "radical": HintBlock(
        title="根式單元提示",
        intro="先看根號裡能不能化簡，再看要不要有理化。根式題最常錯在乘法展開和有理化。",
        mistakes=("把根號和外面的數字亂合", "忘記共軛式", "化簡後沒有整理成最終答案"),
        example="例如：(√3 + 1)(√3 - 1) 會用到平方差公式。",
        next_step="先確認這題是化簡、展開，還是有理化。",
    ),
}


@lru_cache(maxsize=1)
def _load_catalog_entries() -> tuple[CatalogEntry, ...]:
    try:
        return tuple(load_catalog())
    except Exception:
        return tuple()


@lru_cache(maxsize=1)
def _load_skill_doc(skill_id: str) -> str:
    skill_id = str(skill_id or "").strip()
    if not skill_id:
        return ""

    for base in (AGENT_SKILL_DIR, SKILLS_DIR):
        path = base / skill_id / "SKILL.md"
        if not path.exists():
            continue
        for encoding in ("utf-8-sig", "utf-8", "cp950"):
            try:
                return path.read_text(encoding=encoding)
            except Exception:
                continue
    return ""


def _normalize(value: Any) -> str:
    return str(value or "").strip()


def _normalize_nodes(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return []
        if text.startswith("["):
            try:
                payload = json.loads(text)
                if isinstance(payload, list):
                    return [str(item).strip() for item in payload if str(item).strip()]
            except Exception:
                pass
        return [item.strip() for item in text.replace(",", ";").split(";") if item.strip()]
    return []


def _label_for_node(node: str) -> str:
    return NODE_LABELS.get(node, node.replace("_", " "))


def _domain_for_skill(skill_id: str, family_id: str) -> str:
    if "FourArithmeticOperationsOfIntegers" in skill_id or family_id.startswith("I"):
        return "integer"
    if "FourArithmeticOperationsOfNumbers" in skill_id or family_id.startswith("F"):
        return "fraction"
    if "Polynomial" in skill_id or family_id.startswith("poly"):
        return "polynomial"
    if "Radicals" in skill_id or family_id.startswith("p"):
        return "radical"
    return "integer"


def _table_rows() -> list[dict[str, Any]]:
    try:
        from models import db

        row = db.session.execute(
            db.text("SELECT name FROM sqlite_master WHERE type='table' AND name='skill_family_bridge'")
        ).first()
        if not row:
            return []
        rows = db.session.execute(
            db.text(
                """
                SELECT
                    b.skill_id,
                    b.family_id,
                    b.skill_name,
                    COALESCE(si.skill_ch_name, b.skill_ch_name, b.skill_name) AS skill_ch_name,
                    COALESCE(si.skill_en_name, b.skill_en_name, '') AS skill_en_name,
                    b.family_name,
                    b.theme,
                    b.subskill_nodes,
                    b.notes,
                    b.curriculum,
                    b.grade,
                    b.volume,
                    b.chapter,
                    b.section,
                    b.paragraph
                FROM skill_family_bridge b
                LEFT JOIN skills_info si ON si.skill_id = b.skill_id
                WHERE COALESCE(si.is_active, 1) = 1
                ORDER BY b.skill_id, b.family_id
                """
            )
        ).mappings().all()
        return [dict(row) for row in rows]
    except Exception:
        return []


def _bridge_entries() -> list[CatalogEntry]:
    rows = _table_rows()
    entries: list[CatalogEntry] = []
    for row in rows:
        try:
            entries.append(
                CatalogEntry(
                    skill_id=str(row.get("skill_id", "") or "").strip(),
                    skill_name=str(row.get("skill_name") or row.get("skill_ch_name") or "").strip(),
                    family_id=str(row.get("family_id", "") or "").strip(),
                    family_name=str(row.get("family_name", "") or "").strip(),
                    theme=str(row.get("theme", "") or "").strip(),
                    subskill_nodes=_normalize_nodes(row.get("subskill_nodes")),
                    notes=str(row.get("notes", "") or "").strip(),
                )
            )
        except Exception:
            continue
    return entries


def _find_matching_entries(
    *,
    nodes: list[str],
    skill_id: str,
    family_id: str,
    unit_skill_ids: list[str] | None = None,
) -> list[CatalogEntry]:
    bridge_entries = _bridge_entries()
    catalog_entries = list(_load_catalog_entries())
    entries = bridge_entries if bridge_entries else catalog_entries

    if unit_skill_ids:
        allowed = {item.strip() for item in unit_skill_ids if item.strip()}
        if allowed:
            filtered = [entry for entry in entries if entry.skill_id in allowed]
            if filtered:
                entries = filtered

    if skill_id:
        exact = [entry for entry in entries if entry.skill_id == skill_id]
        if exact:
            entries = exact

    if family_id:
        exact = [entry for entry in entries if entry.family_id == family_id]
        if exact:
            entries = exact

    if nodes:
        ranked = []
        for entry in entries:
            overlap = len(set(entry.subskill_nodes) & set(nodes))
            ranked.append((overlap, 1 if entry.skill_id == skill_id else 0, 1 if entry.family_id == family_id else 0, entry))
        ranked.sort(key=lambda item: (-item[0], -item[1], -item[2], item[3].skill_id, item[3].family_id))
        if ranked and ranked[0][0] > 0:
            return [item[3] for item in ranked if item[0] > 0]

    return entries


def _extract_doc_snippet(skill_id: str, family_id: str) -> str:
    doc = _load_skill_doc(skill_id)
    if not doc:
        return ""

    if family_id:
        patterns = [
            rf"^###\s+{re.escape(family_id)}\b.*?(?=^###\s+|\Z)",
            rf"^\|\s*`?{re.escape(family_id)}(?:`?)\s*\|.*?(?=^\||\Z)",
            rf"^\s*{re.escape(family_id)}\b.*?(?=^\s*$|\Z)",
        ]
        for pattern in patterns:
            match = re.search(pattern, doc, flags=re.MULTILINE | re.DOTALL)
            if match:
                return match.group(0).strip()

    return doc[:900].strip()


def _build_mistake_notes(nodes: list[str]) -> list[str]:
    notes = []
    for node in nodes[:3]:
        label = _label_for_node(node)
        if node == "sign_handling":
            notes.append(f"先檢查正負號，不要把減號和負號混在一起。")
        elif node == "add_sub":
            notes.append(f"整數加減時先看符號，再看是否要同號相加、異號相減。")
        elif node == "mul_div":
            notes.append(f"乘除題先確認符號規則，不要直接只看數字。")
        elif node == "conjugate_rationalize":
            notes.append(f"有理化時要記得乘共軛，才能把根號消掉。")
        else:
            notes.append(f"先把「{label}」這個重點看清楚。")
    return notes or ["先從題目的關鍵符號與運算順序開始。"]


def _build_examples(domain: str, nodes: list[str], family_id: str) -> list[str]:
    joined = " ".join(nodes)
    examples: list[str] = []
    if domain == "integer":
        examples.append("例如：-4 + 7 先看異號相減。")
        if "mixed_ops" in joined or "order_of_operations" in joined:
            examples.append("例如：2 + 3 × 4 先算乘法。")
    elif domain == "fraction":
        examples.append("例如：1/3 + 1/6 先通分。")
        if "divide_terms" in joined:
            examples.append("例如：1/2 ÷ 3/4 要改成乘倒數。")
    elif domain == "polynomial":
        examples.append("例如：x + 3x = 4x。")
        if "expand_binomial" in joined or "special_identity" in joined:
            examples.append("例如：(x + 2)(x + 3) 先展開再合併。")
    elif domain == "radical":
        examples.append("例如：√8 = 2√2。")
        if "conjugate_rationalize" in joined:
            examples.append("例如：1/(√3 + 1) 乘共軛。")
    return examples[:3]


def _compose_hint_html(
    *,
    title: str,
    intro: str,
    next_step: str,
    labels: list[str],
    mistakes: list[str],
    examples: list[str],
    source_note: str,
) -> str:
    label_html = "".join(f"<span class='hint-chip'>{html.escape(label)}</span>" for label in labels)
    mistake_html = "".join(f"<li>{html.escape(item)}</li>" for item in mistakes)
    example_html = "".join(f"<li>{html.escape(item)}</li>" for item in examples)
    return (
        "<div class='adaptive-hint adaptive-hint-rag'>"
        f"<div class='hint-title'>{html.escape(title)}</div>"
        f"<p>{html.escape(intro)}</p>"
        f"<div class='hint-chips'>{label_html}</div>"
        "<div class='hint-section'>"
        "<div class='hint-section-title'>常見錯誤</div>"
        f"<ul>{mistake_html}</ul>"
        "</div>"
        "<div class='hint-section'>"
        "<div class='hint-section-title'>小例子</div>"
        f"<ul>{example_html}</ul>"
        "</div>"
        "<div class='hint-section'>"
        "<div class='hint-section-title'>下一步</div>"
        f"<p>{html.escape(next_step)}</p>"
        "</div>"
        f"<div class='hint-source'>{html.escape(source_note)}</div>"
        "</div>"
    )


def build_rag_hint(
    *,
    subskill_nodes: list[str] | str | None,
    skill_id: str = "",
    family_id: str = "",
    question_context: str = "",
    question_text: str = "",
    unit_skill_ids: list[str] | None = None,
) -> dict[str, Any]:
    nodes = _normalize_nodes(subskill_nodes)
    if not nodes:
        raise ValueError("subskill_nodes cannot be empty")

    skill_id = _normalize(skill_id)
    family_id = _normalize(family_id)
    question_context = _normalize(question_context)
    question_text = _normalize(question_text)

    matched_entries = _find_matching_entries(
        nodes=nodes,
        skill_id=skill_id,
        family_id=family_id,
        unit_skill_ids=unit_skill_ids,
    )
    matched_entry = matched_entries[0] if matched_entries else None

    domain = _domain_for_skill(skill_id, family_id)
    domain_hint = DOMAIN_HINTS[domain]
    labels = [_label_for_node(node) for node in nodes]
    mistakes = _build_mistake_notes(nodes)
    examples = _build_examples(domain, nodes, family_id)

    doc_snippet = ""
    if matched_entry:
        doc_snippet = _extract_doc_snippet(matched_entry.skill_id, matched_entry.family_id)
    if not doc_snippet and skill_id:
        doc_snippet = _extract_doc_snippet(skill_id, family_id)

    intro = domain_hint.intro
    if doc_snippet:
        intro = f"{intro} 依據課程資料：{doc_snippet[:180].strip()}"
    if question_context or question_text:
        context = " ".join(item for item in (question_context, question_text) if item).strip()
        if context:
            intro = f"{intro} 目前題目：{context[:120]}"

    if matched_entry and matched_entry.notes:
        next_step = f"{domain_hint.next_step} 另外可注意：{matched_entry.notes.strip()[:120]}"
    else:
        next_step = domain_hint.next_step

    html_hint = _compose_hint_html(
        title=domain_hint.title,
        intro=intro,
        next_step=next_step,
        labels=labels,
        mistakes=mistakes,
        examples=examples,
        source_note="資料來源：skill_family_bridge、SKILL.md 與目前題目脈絡。",
    )

    html_hint = f"{html_hint}<!-- subskill_nodes:{','.join(nodes)} -->"

    summary = "、".join(labels[:3]) if labels else "目前題目重點"

    return {
        "subskill_nodes": nodes,
        "subskill_labels": labels,
        "hint_html": html_hint,
        "hint_summary": summary,
        "common_mistakes": mistakes,
        "example_items": examples,
        "matched_skill_id": matched_entry.skill_id if matched_entry else skill_id,
        "matched_family_id": matched_entry.family_id if matched_entry else family_id,
        "source": "bridge_rag",
    }
