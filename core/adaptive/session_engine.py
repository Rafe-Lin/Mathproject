# -*- coding: utf-8 -*-
from __future__ import annotations

import importlib
import importlib.util
import json
import time
import uuid
from pathlib import Path
from typing import Any

from models import AdaptiveLearningLog, db

from .akt_adapter import bootstrap_local_apr, update_local_apr
from .catalog_loader import load_catalog
from .rag_hint_engine import build_rag_hint
from .manifest_registry import resolve_script_path
from .micro_generators import generate_micro_question
from .ppo_adapter import choose_next_family, choose_strategy
from .schema import CatalogEntry


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MAX_DIAGNOSIS_STEPS = 8
MIN_STEPS_BEFORE_EARLY_PASS = 5
TARGET_APR = 0.65


def _normalize_family_id(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _normalize_subskills(value: Any) -> list[str]:
    if value is None:
        return []
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
        return [part.strip() for part in text.replace(",", ";").split(";") if part.strip()]
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return []


def _select_entries(payload: dict[str, Any]) -> list[CatalogEntry]:
    entries = load_catalog()
    unit_skill_ids = {
        str(item).strip()
        for item in (payload.get("unit_skill_ids") or [])
        if str(item).strip()
    }
    skill_id = str(payload.get("skill_id", "") or "").strip()
    family_scope = {
        _normalize_family_id(item)
        for item in (payload.get("family_scope") or [])
        if _normalize_family_id(item)
    }

    if unit_skill_ids:
        entries = [entry for entry in entries if entry.skill_id in unit_skill_ids]
    elif skill_id:
        entries = [entry for entry in entries if entry.skill_id == skill_id]

    if family_scope:
        entries = [entry for entry in entries if entry.family_id in family_scope]

    return entries


def _load_question_from_skill_module(skill_id: str) -> dict[str, Any] | None:
    try:
        module = importlib.import_module(f"skills.{skill_id}")
    except Exception:
        return None

    generator = getattr(module, "generate", None)
    if not callable(generator):
        return None

    try:
        payload = generator(level=1)
    except TypeError:
        payload = generator()
    except Exception:
        return None

    return payload if isinstance(payload, dict) else None


def _load_question_from_script_path(script_path: str) -> dict[str, Any] | None:
    candidate = Path(script_path)
    if not candidate.is_absolute():
        candidate = PROJECT_ROOT / candidate
    if not candidate.exists():
        return None

    try:
        spec = importlib.util.spec_from_file_location(f"adaptive_skill_{candidate.stem}", candidate)
        if not spec or not spec.loader:
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        generator = getattr(module, "generate", None)
        if not callable(generator):
            return None
        payload = generator(level=1)
        return payload if isinstance(payload, dict) else None
    except Exception:
        return None


def _looks_like_stub_question(payload: dict[str, Any] | None) -> bool:
    if not isinstance(payload, dict):
        return True

    question_text = str(
        payload.get("question_text")
        or payload.get("question")
        or payload.get("latex")
        or ""
    ).strip()
    answer = str(payload.get("correct_answer") or payload.get("answer") or "").strip()

    if not question_text or not answer:
        return True
    if answer.endswith("_answer"):
        return True
    if question_text.startswith("【") and "level=" in question_text:
        return True
    lowered = question_text.lower()
    if "int_" in lowered or "fraction" in lowered or "poly_" in lowered:
        return True
    return False


def _build_fallback_question(entry: CatalogEntry) -> dict[str, Any]:
    question_text = f"請完成 {entry.family_id} 題型：{entry.family_name}"
    hint = "、".join(entry.subskill_nodes[:3])
    answer = f"{entry.family_id}_fallback"
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": question_text,
        "answer": answer,
        "correct_answer": answer,
        "context_string": f"本題聚焦：{hint}",
        "render_mode": "text",
    }


def _normalize_question_payload(raw: dict[str, Any] | None, entry: CatalogEntry, source: str) -> dict[str, Any]:
    payload = dict(raw or {})
    question_text = (
        payload.get("question_text")
        or payload.get("question")
        or payload.get("problem_text")
        or f"{entry.family_id} {entry.family_name}"
    )
    correct_answer = payload.get("correct_answer") or payload.get("answer") or ""
    latex = payload.get("latex") or question_text

    return {
        "question": question_text,
        "question_text": question_text,
        "latex": latex,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "context_string": payload.get("context_string", ""),
        "image_base64": payload.get("image_base64", ""),
        "visual_aids": payload.get("visual_aids", []),
        "family_id": entry.family_id,
        "family_name": entry.family_name,
        "skill_id": entry.skill_id,
        "subskill_nodes": list(entry.subskill_nodes),
        "source": source,
    }


def _generate_question_payload(entry: CatalogEntry) -> dict[str, Any]:
    question = generate_micro_question(entry)
    if question and not _looks_like_stub_question(question):
        return _normalize_question_payload(question, entry, "micro_generator")

    script_path = resolve_script_path(entry.family_id, skill_id=entry.skill_id)
    if script_path:
        question = _load_question_from_script_path(script_path)
        if question and not _looks_like_stub_question(question):
            return _normalize_question_payload(question, entry, "manifest_script")

    question = _load_question_from_skill_module(entry.skill_id)
    if question and not _looks_like_stub_question(question):
        return _normalize_question_payload(question, entry, "skill_module")

    return _normalize_question_payload(_build_fallback_question(entry), entry, "catalog_fallback")


def _get_previous_log(student_id: int, session_id: str) -> AdaptiveLearningLog | None:
    return (
        db.session.query(AdaptiveLearningLog)
        .filter_by(student_id=student_id, session_id=session_id)
        .order_by(AdaptiveLearningLog.step_number.desc(), AdaptiveLearningLog.log_id.desc())
        .first()
    )


def _compute_frustration(previous_log: AdaptiveLearningLog | None, is_correct: bool | None) -> int:
    if is_correct is None:
        return previous_log.frustration_index if previous_log else 0
    if is_correct:
        return 0
    return (previous_log.frustration_index if previous_log else 0) + 1


def _build_hint_html(nodes: list[str]) -> str:
    label_map = {
        "sign_handling": "正負號判讀",
        "add_sub": "整數加減",
        "mul_div": "整數乘除",
        "mixed_ops": "四則混合運算",
        "absolute_value": "絕對值",
        "parentheses": "括號運算",
        "divide_terms": "分項整理",
        "conjugate_rationalize": "分母有理化",
    }
    labels = [label_map.get(node, node.replace("_", " ")) for node in nodes]
    chips = "".join(f"<li>{label}</li>" for label in labels)
    focus = "、".join(labels[:2]) if labels else "目前這一題"
    return (
        "<div class='adaptive-hint'>"
        f"<p><strong>系統提醒：</strong>你現在比較需要加強的是「{focus}」。</p>"
        "<p>先不要急著算，先看清楚題目裡的數字、正負號和運算順序。</p>"
        f"<ul>{chips}</ul>"
        "<p>建議先把第一步寫出來，再決定要先算哪一部分。</p>"
        "</div>"
    )


def _build_summary(
    *,
    answered_steps: int,
    current_apr: float,
    frustration_index: int,
    visited_family_ids: list[str],
) -> dict[str, Any]:
    unique_families = list(dict.fromkeys(visited_family_ids))
    passed = current_apr >= TARGET_APR
    if passed:
        title = "本次診斷完成：已達本單元目標"
        message = "你目前在這個單元的 Local APR 已達到目標線，可以先進入下一個單元，或回頭複習剛才容易猶豫的題型。"
        next_action = "建議進入下一個單元，或挑 1 到 2 題再複習一次加深穩定度。"
    else:
        title = "本次診斷完成：仍有幾個重點要補強"
        message = "這次診斷已經抓到你目前比較容易卡住的地方，建議先看補救提示，再回頭加強相同 family 的題型。"
        next_action = "建議先複習補救提示，再做一次相同單元的總結診斷。"

    return {
        "passed": passed,
        "title": title,
        "message": message,
        "next_action": next_action,
        "answered_steps": answered_steps,
        "final_apr": round(current_apr, 4),
        "frustration_index": frustration_index,
        "visited_families": unique_families,
    }


def submit_and_get_next(payload: dict[str, Any]) -> dict[str, Any]:
    student_id = int(payload["student_id"])
    session_id = str(payload.get("session_id") or uuid.uuid4())
    requested_step = int(payload.get("step_number", 0) or 0)
    last_is_correct = payload.get("is_correct", None)
    if last_is_correct is not None:
        last_is_correct = bool(last_is_correct)

    entries = _select_entries(payload)
    if not entries:
        raise ValueError("No catalog entries available for the requested adaptive scope")

    previous_log = _get_previous_log(student_id, session_id)
    previous_apr = previous_log.current_apr if previous_log else bootstrap_local_apr()
    frustration_index = _compute_frustration(previous_log, last_is_correct)
    last_subskills = _normalize_subskills(payload.get("last_subskills"))
    latency_ms = 0

    if last_is_correct is None:
        current_apr = previous_apr
        strategy = 1
    else:
        current_apr = update_local_apr(
            previous_apr=previous_apr,
            is_correct=last_is_correct,
            frustration_index=frustration_index,
            subskill_count=len(last_subskills) or 1,
        )
        strategy = choose_strategy(current_apr, frustration_index, requested_step)

    visited = [
        row.target_family_id
        for row in (
            db.session.query(AdaptiveLearningLog.target_family_id)
            .filter_by(student_id=student_id, session_id=session_id)
            .order_by(AdaptiveLearningLog.step_number.asc())
            .all()
        )
    ]
    answered_steps = requested_step if last_is_correct is not None else 0
    should_finish = False
    if last_is_correct is not None:
        if answered_steps >= MAX_DIAGNOSIS_STEPS:
            should_finish = True
        elif answered_steps >= MIN_STEPS_BEFORE_EARLY_PASS and current_apr >= TARGET_APR:
            should_finish = True

    next_step_number = requested_step + 1
    if last_is_correct is not None:
        logged_family_id = _normalize_family_id(payload.get("last_family_id"))
        log = AdaptiveLearningLog(
            student_id=student_id,
            session_id=session_id,
            step_number=next_step_number,
            target_family_id=logged_family_id,
            target_subskills=json.dumps(last_subskills, ensure_ascii=False),
            is_correct=last_is_correct,
            current_apr=current_apr,
            ppo_strategy=strategy,
            frustration_index=frustration_index,
            execution_latency=latency_ms,
        )
        db.session.add(log)
        db.session.commit()

    if should_finish:
        summary = _build_summary(
            answered_steps=answered_steps,
            current_apr=current_apr,
            frustration_index=frustration_index,
            visited_family_ids=visited + [_normalize_family_id(payload.get("last_family_id"))],
        )
        return {
            "session_id": session_id,
            "step_number": requested_step,
            "current_apr": current_apr,
            "ppo_strategy": strategy,
            "frustration_index": frustration_index,
            "execution_latency": 0,
            "target_family_id": _normalize_family_id(payload.get("last_family_id")),
            "target_subskills": last_subskills,
            "new_question_data": {},
            "completed": True,
            "summary": summary,
        }

    next_entry = choose_next_family(
        entries=entries,
        visited_family_ids=visited,
        strategy=strategy,
        last_family_id=_normalize_family_id(payload.get("last_family_id")),
    )

    started = time.perf_counter()
    question_payload = _generate_question_payload(next_entry)
    latency_ms = int((time.perf_counter() - started) * 1000)

    return {
        "session_id": session_id,
        "step_number": next_step_number,
        "current_apr": current_apr,
        "ppo_strategy": strategy,
        "frustration_index": frustration_index,
        "execution_latency": latency_ms,
        "target_family_id": next_entry.family_id,
        "target_subskills": list(next_entry.subskill_nodes),
        "new_question_data": question_payload,
        "completed": False,
    }


def get_rag_hint(
    subskill_nodes: list[str] | str | None,
    *,
    skill_id: str = "",
    family_id: str = "",
    question_context: str = "",
    question_text: str = "",
    unit_skill_ids: list[str] | None = None,
) -> dict[str, Any]:
    return build_rag_hint(
        subskill_nodes=subskill_nodes,
        skill_id=skill_id,
        family_id=family_id,
        question_context=question_context,
        question_text=question_text,
        unit_skill_ids=unit_skill_ids,
    )
