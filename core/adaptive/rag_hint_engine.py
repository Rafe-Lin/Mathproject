# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import csv
import html
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from .schema import CatalogEntry


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = PROJECT_ROOT / "docs" / "自適應實作" / "skill_breakpoint_catalog.csv"
AGENT_SKILL_DIR = PROJECT_ROOT / "agent_skills"
SKILLS_DIR = PROJECT_ROOT / "skills"


@dataclass(frozen=True)
class HintBlock:
    title: str
    explanation: str
    mistakes: tuple[str, ...]
    example: str
    next_step: str


NODE_LABELS: dict[str, str] = {
    "sign_handling": "正負號判讀",
    "add_sub": "整數加減",
    "mul_div": "整數乘除",
    "mixed_ops": "四則混合運算",
    "order_of_operations": "運算順序",
    "bracket_scope": "括號範圍",
    "absolute_value": "絕對值",
    "exact_divisibility": "整除判斷",
    "isomorphic_structure": "題型結構",
    "proper_improper_fraction": "真分數與假分數",
    "mixed_numbers": "帶分數",
    "sign_normalization": "正負號整理",
    "decimal_to_fraction_exact_conversion": "小數轉分數",
    "simplest_form_reduction": "約分化簡",
    "equivalent_fraction_scaling": "等值分數",
    "reciprocal_transform": "倒數",
    "preserve_value_invariance": "保持數值不變",
    "positive_fraction_comparison": "正分數比較",
    "negative_fraction_comparison": "負分數比較",
    "mixed_number_comparison": "帶分數比較",
    "multiply": "分數乘法",
    "divide": "分數除法",
    "nested_parentheses": "巢狀括號",
    "decimal_fraction_mixed_arithmetic": "小數分數混合運算",
    "telescoping_products": "連乘約分",
    "remaining_amount": "剩餘量",
    "container_weight": "容器重量",
    "before_after_ratio": "前後比較",
    "share_comparison": "份量比較",
    "normalize_terms": "整理同類項",
    "combine_like_terms": "合併同類項",
    "sign_distribution": "分配律展開",
    "expand_monomial": "單項式展開",
    "expand_binomial": "二項式展開",
    "special_identity": "特殊乘法公式",
    "long_division": "多項式除法",
    "quotient_remainder_format": "商與餘式",
    "reverse_division_reconstruction": "反推除式",
    "geometry_formula": "幾何公式",
    "composite_region_modeling": "複合區域",
    "family_isomorphism": "題型結構",
    "simplify": "化簡",
    "multiply_terms": "根式乘法",
    "divide_terms": "根式除法",
    "distribute": "分配律",
    "binomial_expand": "展開公式",
    "conjugate_rationalize": "分母有理化",
    "fractional_radical": "根式分數混合",
    "mixed_number_radical": "帶分數根式",
    "structure_isomorphism": "結構對應",
}


NODE_HINTS: dict[str, HintBlock] = {
    "sign_handling": HintBlock(
        title="先看正負號",
        explanation="這類題最先做的，不是急著算，而是先把每個數字前面的正負號看清楚。",
        mistakes=("把減號看成負號", "忽略前面括號裡的負號", "算到最後才補正負號"),
        example="例如：14 + (-7) 先想成 14 減 7。",
        next_step="先圈出所有負號，再開始算。",
    ),
    "add_sub": HintBlock(
        title="先整理加減",
        explanation="加減題先把符號整理好，減法可以想成加上相反數。",
        mistakes=("看到減法直接當成負數亂算", "同號異號沒有先分清楚", "步驟中途漏掉符號"),
        example="例如：5 - 7 可以先看成 5 + (-7)。",
        next_step="先把所有減法改寫成加負數，再算。",
    ),
    "mul_div": HintBlock(
        title="先算乘除",
        explanation="有乘除時，先決定正負，再算絕對值大小。",
        mistakes=("乘法和加法一起亂算", "負負得正忘記", "除號方向看錯"),
        example="例如：(-6) × 4 先看正負，再算 6 × 4。",
        next_step="先算乘除，再處理加減。",
    ),
    "mixed_ops": HintBlock(
        title="注意運算順序",
        explanation="四則混合題要先乘除、後加減；有括號時，先算括號裡。",
        mistakes=("從左到右硬算", "忽略括號", "先算加減再算乘除"),
        example="例如：3 + 2 × 5 要先算 2 × 5。",
        next_step="先找出哪一段要先算，再下手。",
    ),
    "order_of_operations": HintBlock(
        title="先看運算順序",
        explanation="有括號、乘除、加減時，要照規則一步一步來，不能跳步。",
        mistakes=("想直接把整題一起算完", "先算加減", "漏看括號"),
        example="例如：8 - 3 × 2 要先算 3 × 2。",
        next_step="先從最裡面或最前面的規則開始算。",
    ),
    "bracket_scope": HintBlock(
        title="先算括號裡",
        explanation="括號就是提醒你：這一段要先處理完，不能拆開亂算。",
        mistakes=("把括號直接拿掉", "括號裡外一起算", "括號前的負號沒處理"),
        example="例如：(4 - 9) × 2 要先算 4 - 9。",
        next_step="先把括號裡整理好，再算外面。",
    ),
    "absolute_value": HintBlock(
        title="先看絕對值",
        explanation="絕對值表示距離，結果一定是非負數。先把裡面的數字算好，再去掉絕對值。",
        mistakes=("把絕對值算成負數", "只看外面的號碼不看裡面", "裡面還沒算完就直接拿掉"),
        example="例如：|-7 + 2| 先算裡面，再看結果。",
        next_step="先算絕對值裡面的部分。",
    ),
    "exact_divisibility": HintBlock(
        title="先看能不能整除",
        explanation="如果題目要求整數答案，要先確認除得盡不盡。",
        mistakes=("把不能整除的題目硬寫成整數", "分子分母還沒整理就下結論", "忽略餘數"),
        example="例如：18 ÷ 3 可以整除，答案是 6。",
        next_step="先判斷能不能整除，再寫答案。",
    ),
    "simplest_form_reduction": HintBlock(
        title="先約分",
        explanation="分數題常常要先約成最簡分數，這是基本檢查步驟。",
        mistakes=("沒有先約分", "分子分母同除數字後又算錯", "負號位置寫錯"),
        example="例如：8/12 先約成 2/3。",
        next_step="先找共同因數，再約分。",
    ),
    "equivalent_fraction_scaling": HintBlock(
        title="等值分數",
        explanation="分子分母要同乘或同除，分數值才會一樣。",
        mistakes=("只改分子不改分母", "同乘同除搞混", "忘記負號規則"),
        example="例如：2/3 = 4/6。",
        next_step="先看要放大還是縮小，再同時改分子分母。",
    ),
    "reciprocal_transform": HintBlock(
        title="倒數",
        explanation="倒數就是分子分母對調，但 0 沒有倒數。",
        mistakes=("把 0 當成有倒數", "倒數寫成原來的分數", "正負號放錯"),
        example="例如：3/4 的倒數是 4/3。",
        next_step="先把分子分母交換，再檢查正負號。",
    ),
    "sign_normalization": HintBlock(
        title="先整理正負號",
        explanation="分數或根式先把正負號放到最前面，寫法會更清楚。",
        mistakes=("寫成 a/-b", "正負號分散在上下", "算完才補號"),
        example="例如：-3/5 比 3/-5 更標準。",
        next_step="先把負號統一整理好，再開始算。",
    ),
    "multiply": HintBlock(
        title="分數乘法",
        explanation="乘法先算分子乘分子、分母乘分母，再看能不能約分。",
        mistakes=("先亂交叉相加", "忘記先約分", "乘完沒整理成最簡"),
        example="例如：2/3 × 3/4 = 1/2。",
        next_step="先找可以約分的地方，再相乘。",
    ),
    "divide": HintBlock(
        title="分數除法",
        explanation="除以分數時，要改成乘倒數。",
        mistakes=("直接分子除分子、分母除分母", "忘記倒數", "混合數沒有先化成分數"),
        example="例如：2/3 ÷ 4/5 = 2/3 × 5/4。",
        next_step="先把除法改成乘倒數，再算。",
    ),
    "nested_parentheses": HintBlock(
        title="巢狀括號",
        explanation="有多層括號時，先算最裡面，外面再跟著處理。",
        mistakes=("先拆外層", "把括號順序搞反", "漏掉括號前的負號"),
        example="例如：(2 - (3 - 1)) 先算裡層。",
        next_step="先從最裡層開始拆。",
    ),
    "decimal_fraction_mixed_arithmetic": HintBlock(
        title="小數和分數混合",
        explanation="小數和分數一起出現時，先統一成同一種形式，會比較不容易算錯。",
        mistakes=("小數直接亂乘分數", "沒有轉成同一格式", "四捨五入太早"),
        example="例如：0.5 可以先看成 1/2。",
        next_step="先統一格式，再開始算。",
    ),
    "combine_like_terms": HintBlock(
        title="先找同類項",
        explanation="代數式先找同類項，只有同類項才可以相加。",
        mistakes=("不同類項直接合併", "符號沒先整理", "項數太多就亂掉"),
        example="例如：2x + 3x = 5x。",
        next_step="先圈出同類項，再合併。",
    ),
    "expand_binomial": HintBlock(
        title="先展開",
        explanation="乘法或公式題先把括號展開，再整理同類項。",
        mistakes=("漏乘", "符號錯位", "展開後沒有再整理"),
        example="例如：(x+2)(x+3) 要先展開。",
        next_step="先每一項都乘到，再整理。",
    ),
    "special_identity": HintBlock(
        title="特殊乘法公式",
        explanation="像平方差、完全平方這類題，要先辨認公式，再代入。",
        mistakes=("把公式硬展開算", "看錯正負號", "忘了中間項"),
        example="例如：(a+b)^2 = a^2 + 2ab + b^2。",
        next_step="先判斷是不是公式型題目。",
    ),
    "long_division": HintBlock(
        title="多項式除法",
        explanation="多項式除法先看最高次項，再一步一步做。",
        mistakes=("直接亂消掉", "次方順序錯", "商與餘式沒分清楚"),
        example="例如：先看 x^2 能不能被 x 整除。",
        next_step="先比最高次項，再繼續往下算。",
    ),
    "simplify": HintBlock(
        title="先化簡",
        explanation="根式題先化簡，能提出來的就先提出來。",
        mistakes=("根號裡外混著算", "沒有先拆因數", "化簡後還沒整理"),
        example="例如：√12 = 2√3。",
        next_step="先把根號裡的數拆一拆。",
    ),
    "conjugate_rationalize": HintBlock(
        title="分母有理化",
        explanation="分母有根號時，通常要乘共軛把根號消掉。",
        mistakes=("直接約掉根號", "只乘一邊", "共軛符號寫反"),
        example="例如：1/(√3 - 1) 要乘 (√3 + 1)。",
        next_step="先找共軛，再把分母整理成整數或整式。",
    ),
    "fractional_radical": HintBlock(
        title="根式和分數混合",
        explanation="有分數又有根號時，先看哪一部分能先化簡，再統一處理。",
        mistakes=("根號和分數混在一起亂算", "約分順序錯", "忽略正負號"),
        example="例如：√8 / 2 可以先化成 2√2 / 2。",
        next_step="先化簡，再看要不要約分。",
    ),
    "mixed_number_radical": HintBlock(
        title="帶分數根式",
        explanation="遇到帶分數或根式混合時，先把格式看清楚，再一步一步算。",
        mistakes=("把帶分數直接當整數", "根號外面的整數漏掉", "先算錯順序"),
        example="例如：1 1/2 × √3 先把 1 1/2 看清楚。",
        next_step="先辨認數字格式，再開始計算。",
    ),
}


DOMAIN_HINTS: dict[str, dict[str, Any]] = {
    "integer": {
        "title": "整數四則重點",
        "intro": "這題重點是先看符號，再看順序。整數題常錯在把負號看錯，或是乘除、加減順序搞反。",
        "next": "先圈出所有負號與括號，再照運算順序算。",
    },
    "fraction": {
        "title": "分數四則重點",
        "intro": "這題重點是先統一格式，再做運算。分數題常錯在約分沒做、倒數忘記、或正負號整理錯。",
        "next": "先檢查是不是要約分、通分或乘倒數。",
    },
    "polynomial": {
        "title": "多項式重點",
        "intro": "這題重點是先找同類項，再看要不要展開或除法。多項式題常錯在漏項、符號錯、或沒有先整理。",
        "next": "先把每一項整理清楚，再做合併或展開。",
    },
    "radical": {
        "title": "根式重點",
        "intro": "這題重點是先化簡，再看要不要有理化。根式題常錯在根號裡外混算，或分母還沒清掉就停下來。",
        "next": "先化簡根式，分母有根號再考慮乘共軛。",
    },
}


@lru_cache(maxsize=1)
def _load_catalog() -> tuple[CatalogEntry, ...]:
    if not CATALOG_PATH.exists():
        return tuple()
    last_error: Exception | None = None
    for encoding in ("utf-8-sig", "utf-8", "cp950"):
        try:
            with CATALOG_PATH.open("r", encoding=encoding, newline="") as fh:
                reader = csv.DictReader(fh)
                return tuple(CatalogEntry.from_row(dict(row)) for row in reader)
        except Exception as exc:  # pragma: no cover
            last_error = exc
    raise RuntimeError(f"Failed to load adaptive catalog: {last_error}")


@lru_cache(maxsize=16)
def _load_skill_doc(skill_id: str) -> str:
    skill_id = str(skill_id or "").strip()
    if not skill_id:
        return ""

    candidates = [
        AGENT_SKILL_DIR / skill_id / "SKILL.md",
        SKILLS_DIR / skill_id / "SKILL.md",
    ]
    for path in candidates:
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
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return []
        if text.startswith("["):
            try:
                data = json.loads(text)
                if isinstance(data, list):
                    return [str(item).strip() for item in data if str(item).strip()]
            except Exception:
                pass
        return [part.strip() for part in text.replace(",", ";").split(";") if part.strip()]
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return []


def _label_for_node(node: str) -> str:
    return NODE_LABELS.get(node, node.replace("_", " "))


def _domain_for_skill(skill_id: str, family_id: str) -> str:
    skill_id = skill_id or ""
    family_id = family_id or ""
    if "FourArithmeticOperationsOfIntegers" in skill_id or family_id.startswith("I"):
        return "integer"
    if "FourArithmeticOperationsOfNumbers" in skill_id or family_id.startswith("F"):
        return "fraction"
    if "Polynomial" in skill_id or family_id.startswith("poly"):
        return "polynomial"
    if "Radicals" in skill_id or family_id.startswith("p"):
        return "radical"
    return "integer"


def _find_matching_entries(
    *,
    nodes: list[str],
    skill_id: str,
    family_id: str,
    unit_skill_ids: list[str] | None = None,
) -> list[CatalogEntry]:
    entries = list(_load_catalog())
    if unit_skill_ids:
        allowed = {item.strip() for item in unit_skill_ids if item.strip()}
        if allowed:
            entries = [entry for entry in entries if entry.skill_id in allowed]
    if skill_id:
        skill_matches = [entry for entry in entries if entry.skill_id == skill_id]
        if skill_matches:
            entries = skill_matches
    if family_id:
        family_matches = [entry for entry in entries if entry.family_id == family_id]
        if family_matches:
            entries = family_matches

    if nodes:
        weighted: list[tuple[int, CatalogEntry]] = []
        for entry in entries:
            overlap = len(set(entry.subskill_nodes) & set(nodes))
            score = overlap * 3
            if entry.skill_id == skill_id:
                score += 4
            if entry.family_id == family_id:
                score += 4
            weighted.append((score, entry))
        weighted.sort(key=lambda item: (-item[0], item[1].skill_id, item[1].family_id))
        ranked = [entry for score, entry in weighted if score > 0]
        if ranked:
            return ranked
    return entries


def _extract_doc_snippet(skill_id: str, family_id: str) -> str:
    doc = _load_skill_doc(skill_id)
    if not doc:
        return ""

    patterns = [
        rf"^###\s+{re.escape(family_id)}\b.*?(?=^###\s+|\Z)",
        rf"^\|\s*`?{re.escape(family_id)}(?:`?)\s*\|.*?(?=^\||\Z)",
        rf"^\s*{re.escape(family_id)}\b.*?(?=^\s*$|\Z)",
    ]
    for pattern in patterns:
        match = re.search(pattern, doc, flags=re.M | re.S)
        if match:
            snippet = re.sub(r"\s+", " ", match.group(0)).strip()
            return _clean_doc_snippet(snippet)
    return ""


def _clean_doc_snippet(snippet: str) -> str:
    text = re.sub(r"\s+", " ", snippet).strip()
    text = text.replace("`", "").replace("###", "").replace("|", "")
    for marker in ("Definition:", "Definition", "定義：", "定義:"):
        if marker in text:
            text = text.split(marker, 1)[1]
            break
    for stopper in (
        "Representative forms:",
        "Representative subfamilies:",
        "Typical examples:",
        "Quality gate:",
        "Expected answer type:",
        "Sub-skill Graph",
        "Structural Schema",
        "Family Catalogue",
    ):
        if stopper in text:
            text = text.split(stopper, 1)[0]
    text = re.sub(r"\s+", " ", text).strip(" -;，,")
    return text[:160]


def _domain_hint(domain: str) -> dict[str, str]:
    return dict(DOMAIN_HINTS.get(domain, DOMAIN_HINTS["integer"]))


def _compose_family_context(entry: CatalogEntry | None, question_context: str, question_text: str) -> str:
    parts: list[str] = []
    if question_context.strip():
        parts.append(question_context.strip())
    if question_text.strip() and question_text.strip() not in parts:
        parts.append(question_text.strip())
    return "；".join(parts)


def _build_mistake_notes(nodes: list[str]) -> list[str]:
    notes: list[str] = []
    for node in nodes:
        block = NODE_HINTS.get(node)
        if block:
            notes.extend(block.mistakes)
    if not notes:
        notes.append("先不要急著直接算答案，先看題目要求的是哪一種運算。")
    deduped: list[str] = []
    seen: set[str] = set()
    for note in notes:
        if note not in seen:
            seen.add(note)
            deduped.append(note)
    return deduped[:4]


def _build_examples(domain: str, nodes: list[str], family_id: str) -> list[str]:
    examples: list[str] = []
    joined = set(nodes)
    if domain == "integer":
        if "absolute_value" in joined:
            examples.append("例如：|-7 + 2|，先算裡面再去掉絕對值。")
        if "bracket_scope" in joined:
            examples.append("例如：(4 - 9) × 2，先算括號裡。")
        if "mul_div" in joined:
            examples.append("例如：(-6) × 4，先決定正負，再算 6 × 4。")
        if "add_sub" in joined:
            examples.append("例如：14 - 7，可以先看成 14 + (-7)。")
        if not examples:
            examples.append("例如：8 - 3 × 2，先算乘法。")
    elif domain == "fraction":
        if "divide" in joined:
            examples.append("例如：2/3 ÷ 4/5，要先改成乘倒數。")
        if "multiply" in joined:
            examples.append("例如：2/3 × 3/4，可以先約分再乘。")
        if "simplest_form_reduction" in joined:
            examples.append("例如：8/12 先約成 2/3。")
        if "conjugate_rationalize" in joined:
            examples.append("例如：1/(√3 - 1) 要乘共軛。")
        if not examples:
            examples.append("例如：1/2 + 1/3，先通分再加。")
    elif domain == "polynomial":
        if "combine_like_terms" in joined:
            examples.append("例如：2x + 3x = 5x。")
        if "expand_binomial" in joined:
            examples.append("例如：(x+2)(x+3) 先展開再整理。")
        if "long_division" in joined:
            examples.append("例如：先看最高次項能不能整除。")
        if not examples:
            examples.append("例如：2x + x 先找同類項。")
    else:
        if "conjugate_rationalize" in joined:
            examples.append("例如：1/(√5 + 1) 先乘共軛。")
        if "multiply_terms" in joined:
            examples.append("例如：√2 × √8，先化簡再乘。")
        if "simplify" in joined:
            examples.append("例如：√12 = 2√3。")
        if not examples:
            examples.append("例如：先把根號裡外分清楚，再開始算。")
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
        "<div class='hint-section-title'>可參考的例子</div>"
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
    domain_hint = _domain_hint(domain)
    labels = [_label_for_node(node) for node in nodes]
    mistakes = _build_mistake_notes(nodes)
    examples = _build_examples(domain, nodes, family_id)

    doc_snippet = ""
    if matched_entry:
        doc_snippet = _extract_doc_snippet(matched_entry.skill_id, matched_entry.family_id)
    if not doc_snippet and skill_id:
        doc_snippet = _extract_doc_snippet(skill_id, family_id)

    if doc_snippet:
        intro = f"{domain_hint['intro']} 這一題已對應到課本規格與題型目錄。"
        source_note = "資料來源：題型目錄、SKILL.md 與目前這一題的 subskill_nodes。"
    else:
        intro = domain_hint["intro"]
        source_note = "資料來源：題型目錄與目前這一題的 subskill_nodes。"

    family_context = _compose_family_context(matched_entry, question_context, question_text)
    if family_context:
        intro = f"{intro} 現在這題是：{family_context}"

    next_step = domain_hint["next"]
    if matched_entry and matched_entry.notes:
        next_step = f"{next_step} 另外，這一類題目常見提醒是：{matched_entry.notes.strip()}"

    html_hint = _compose_hint_html(
        title=domain_hint["title"],
        intro=intro,
        next_step=next_step,
        labels=labels,
        mistakes=mistakes,
        examples=examples,
        source_note=source_note,
    )

    summary = "、".join(labels[:3]) if labels else "這一題的核心觀念"

    return {
        "subskill_nodes": nodes,
        "subskill_labels": labels,
        "hint_html": html_hint,
        "hint_summary": summary,
        "common_mistakes": mistakes,
        "example_items": examples,
        "matched_skill_id": matched_entry.skill_id if matched_entry else skill_id,
        "matched_family_id": matched_entry.family_id if matched_entry else family_id,
        "source": "hybrid_rag",
    }
