# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import re
from typing import Any

from core.ai_wrapper import call_ai_with_retry, get_ai_client


EVIDENCE_THRESHOLD = 2.0
SUPPORTED_POLY_FAMILIES = {"F1", "F2", "F5", "F11"}

CHOICE_TO_INDEX = {"A": 0, "B": 1, "C": 2}
INDEX_TO_CHOICE = {0: "A", 1: "B", 2: "C"}


FAMILY_CANDIDATES: dict[str, list[dict[str, str]]] = {
    "F1": [
        {
            "diagnosis_label": "signed_arithmetic",
            "runtime_subskill": "sign_handling",
            "error_concept": "negative_sign_handling",
            "symptom": "合併同類項時，正負號常出現相反或遺漏。",
            "basis": "整數加減與負號處理是多項式加減的前置。",
        },
        {
            "diagnosis_label": "basic_operations",
            "runtime_subskill": "add_sub",
            "error_concept": "basic_arithmetic_instability",
            "symptom": "同類項可辨識，但常數或係數加減常算錯。",
            "basis": "同類項合併依賴整數加減穩定度。",
        },
        {
            "diagnosis_label": "division",
            "runtime_subskill": "mul_div",
            "error_concept": "division_misconception",
            "symptom": "係數化簡或約分步驟經常錯置。",
            "basis": "係數運算涉及乘除基本概念。",
        },
    ],
    "F2": [
        {
            "diagnosis_label": "bracket_scope",
            "runtime_subskill": "parentheses",
            "error_concept": "outer_minus_scope",
            "symptom": "括號前有負號時，只改了第一項，沒有整組變號。",
            "basis": "去括號負號的作用範圍需對整個括號生效。",
        },
        {
            "diagnosis_label": "combine_after_distribution",
            "runtime_subskill": "add_sub",
            "error_concept": "combine_like_terms_after_distribution",
            "symptom": "去括號後同類項合併時，加減流程容易斷掉。",
            "basis": "分配後還要正確接續合併同類項。",
        },
        {
            "diagnosis_label": "order_of_operations",
            "runtime_subskill": "mul_div",
            "error_concept": "nested_grouping_structure_error",
            "symptom": "多層括號與展開順序混亂，常跳步導致錯誤。",
            "basis": "巢狀結構先後次序不穩，會連鎖影響符號與係數。",
        },
    ],
    "F5": [
        {
            "diagnosis_label": "coefficient_arithmetic",
            "runtime_subskill": "mul_div",
            "error_concept": "coefficient_arithmetic_error",
            "symptom": "展開時係數乘法常算錯或漏乘。",
            "basis": "多項式乘法核心依賴整數乘除能力。",
        },
        {
            "diagnosis_label": "expand_structure",
            "runtime_subskill": "sign_handling",
            "error_concept": "binomial_expansion_structure_error",
            "symptom": "雙括號展開常漏項或配對錯，結構骨架不穩。",
            "basis": "展開結構錯會直接造成後續同類項無法收斂。",
        },
        {
            "diagnosis_label": "combine_after_distribution",
            "runtime_subskill": "add_sub",
            "error_concept": "combine_like_terms_after_distribution",
            "symptom": "展開後合併同類項常出現加減錯誤。",
            "basis": "展開結果最終仍需加減整合。",
        },
    ],
    "F11": [
        {
            "diagnosis_label": "order_of_operations",
            "runtime_subskill": "mixed_ops",
            "error_concept": "mixed_simplify_transition_error",
            "symptom": "混合化簡多步驟切換時，常在順序與銜接出錯。",
            "basis": "步驟轉換不穩會造成中間式失真，最終答案偏差。",
        },
        {
            "diagnosis_label": "bracket_scope",
            "runtime_subskill": "parentheses",
            "error_concept": "bracket_scope_error",
            "symptom": "多層括號作用範圍判斷失誤，符號連動出錯。",
            "basis": "混合題裡括號範圍錯誤會放大成整題錯誤。",
        },
        {
            "diagnosis_label": "structure_isomorphism",
            "runtime_subskill": "add_sub",
            "error_concept": "family_isomorphism_confusion",
            "symptom": "題型變形後抓不到對應做法，解題策略失焦。",
            "basis": "結構同構辨識不足會讓正確流程無法啟動。",
        },
    ],
}


def _clip01(value: Any, default: float = 0.0) -> float:
    try:
        return max(0.0, min(1.0, float(value)))
    except Exception:
        return default


def _build_choice_prompt(
    *,
    family_id: str,
    question_text: str,
    expected_answer: str,
    student_answer: str,
    candidates: list[dict[str, str]],
) -> str:
    lines = [
        "你是數學錯誤診斷器，只能在 A/B/C 三個候選中選一個最可能斷點。",
        "請優先根據學生答案與正解差異判斷，不要輸出解題步驟。",
        "輸出格式只允許 JSON：{\"choice\":\"A|B|C\",\"confidence\":0~1}",
        f"family_id: {family_id}",
        f"題目: {question_text}",
        f"正確答案: {expected_answer}",
        f"學生錯誤答案: {student_answer}",
        "候選：",
    ]
    for idx, candidate in enumerate(candidates):
        choice = INDEX_TO_CHOICE[idx]
        lines.append(
            f"{choice}. {candidate['runtime_subskill']} | 症狀: {candidate['symptom']} | 依據: {candidate['basis']}"
        )
    return "\n".join(lines)


def _parse_choice_response(raw_text: str) -> tuple[str | None, float]:
    text = str(raw_text or "").strip()
    if not text:
        return None, 0.0
    try:
        payload = json.loads(text)
        if isinstance(payload, dict):
            choice = str(payload.get("choice", "")).strip().upper()
            confidence = _clip01(payload.get("confidence", 0.0), 0.0)
            if choice in CHOICE_TO_INDEX:
                return choice, confidence
    except Exception:
        pass
    match = re.search(r"\b([ABC])\b", text.upper())
    if match:
        return match.group(1), 0.65
    return None, 0.0


def _heuristic_choice(
    *,
    question_text: str,
    expected_answer: str,
    student_answer: str,
    candidates: list[dict[str, str]],
) -> tuple[str, float]:
    q = str(question_text or "")
    expected = str(expected_answer or "")
    student = str(student_answer or "")
    if "-" in expected or "-" in student or "-" in q:
        return "A", 0.72
    if "÷" in q or "/" in q or "×" in q:
        return "B", 0.68
    return "C", 0.62


def _call_qwen_choice(prompt: str) -> tuple[str | None, float, str]:
    try:
        client = get_ai_client("classifier")
        response = call_ai_with_retry(client, prompt, max_retries=1, retry_delay=0, verbose=False, timeout=45)
        raw = str(getattr(response, "text", "") or "")
        choice, conf = _parse_choice_response(raw)
        if choice in CHOICE_TO_INDEX:
            return choice, conf if conf > 0 else 0.7, "qwen_choice"
        return None, 0.0, "qwen_invalid_output"
    except Exception as exc:
        return None, 0.0, f"qwen_error:{exc}"


def diagnose_polynomial_with_choice(
    *,
    family_id: str,
    question_text: str,
    expected_answer: str,
    student_answer: str,
    routing_session: dict[str, Any] | None,
    candidates_override: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    family_key = str(family_id or "").strip()
    candidates = list(candidates_override or FAMILY_CANDIDATES.get(family_key, []))
    if family_key not in SUPPORTED_POLY_FAMILIES or not candidates:
        return {"applied": False}

    prompt = _build_choice_prompt(
        family_id=family_key,
        question_text=question_text,
        expected_answer=expected_answer,
        student_answer=student_answer,
        candidates=candidates,
    )
    choice, confidence, source = _call_qwen_choice(prompt)
    if choice not in CHOICE_TO_INDEX:
        choice, confidence = _heuristic_choice(
            question_text=question_text,
            expected_answer=expected_answer,
            student_answer=student_answer,
            candidates=candidates,
        )
        source = "heuristic_choice"

    idx = CHOICE_TO_INDEX.get(choice, 2)
    selected = dict(candidates[min(idx, len(candidates) - 1)])
    selected_runtime = str(selected["runtime_subskill"])
    selected_diag = str(selected["diagnosis_label"])
    selected_error_concept = str(selected["error_concept"])

    state = dict(routing_session or {})
    evidence = dict(state.get("diagnostic_evidence") or {})
    next_score = float(evidence.get(selected_runtime, 0.0) or 0.0) + 1.0
    evidence[selected_runtime] = next_score
    state["diagnostic_evidence"] = evidence

    remediation_triggered = bool(next_score >= EVIDENCE_THRESHOLD)
    diagnosis_confidence = 0.9 if remediation_triggered else min(0.79, 0.45 + 0.12 * next_score)

    return {
        "applied": True,
        "routing_session": state,
        "version": "rag_choice_v1",
        "current_family": family_key,
        "error_concept": selected_error_concept,
        "top_concept": selected_error_concept,
        "retrieval_confidence": _clip01(confidence, 0.6),
        "diagnosis_confidence": _clip01(diagnosis_confidence, 0.55),
        "suggested_prereq_skill": "integer_arithmetic" if remediation_triggered else None,
        "suggested_prereq_subskill": selected_diag if remediation_triggered else None,
        "route_type": "rescue" if remediation_triggered else "stay",
        "retrieved_candidates": candidates,
        "diagnostic_choice": choice,
        "diagnostic_confidence": _clip01(confidence, 0.6),
        "evidence_score": round(next_score, 3),
        "remediation_triggered": remediation_triggered,
        "diagnosis_source": source,
        "selected_runtime_subskill": selected_runtime,
    }
