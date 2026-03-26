# -*- coding: utf-8 -*-
from __future__ import annotations

import importlib
import importlib.util
import json
import logging
import os
import sys
import time
import uuid
from pathlib import Path
from typing import Any

from models import AdaptiveLearningLog, db

from .agent_skill_schema import resolve_agent_skill
from .akt_adapter import bootstrap_local_apr, update_local_apr
from .catalog_loader import load_catalog
from .rag_hint_engine import build_rag_hint
from .manifest_registry import resolve_script_path
from .micro_generators import generate_micro_question
from .policy_findings_mapping import build_policy_findings_hints
from .ppo_adapter import (
    IDX_TO_SKILL,
    IDX_TO_ROUTE,
    SKILL_LABELS,
    choose_next_family,
    choose_strategy,
    get_last_ppo_error,
    load_phase2_policy_model,
    select_route_action_heuristic,
    select_route_action_with_ppo,
)
from .routing import (
    apply_routing_action,
    build_action_mask,
    build_routing_state,
    compute_cross_skill_trigger,
    rag_diagnose,
    should_return_from_remediation,
)
from .schema import CatalogEntry
from .state_builder import build_agent_state
from .subskill_selector import load_family_subskill_map, select_subskill


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MAX_DIAGNOSIS_STEPS = 8
MIN_STEPS_BEFORE_EARLY_PASS = 5
TARGET_APR = 0.65

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
    force=True,
)
POLICY_LOGGER = logging.getLogger("adaptive_phase1_policy")
ADAPTIVE_DEBUG: bool = True
ROUTING_SUMMARY_LOG: bool = str(os.getenv("ADAPTIVE_ROUTING_SUMMARY_LOG", "0")).strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}
ENABLE_POLICY_FINDINGS: bool = str(os.getenv("ADAPTIVE_ENABLE_POLICY_FINDINGS", "1")).strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}


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


def _empty_routing_summary() -> dict[str, Any]:
    return {
        "total_routing_decisions": 0,
        "ppo_routing_decisions": 0,
        "fallback_routing_decisions": 0,
        "remediation_entries": 0,
        "successful_returns": 0,
        "bridge_completions": 0,
        "ppo_usage_rate": 0.0,
        "return_success_rate": 0.0,
    }


def _safe_rate(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round(float(numerator) / float(denominator), 4)


def _normalize_routing_summary(raw: Any) -> dict[str, Any]:
    summary = _empty_routing_summary()
    if not isinstance(raw, dict):
        return summary
    for key in [
        "total_routing_decisions",
        "ppo_routing_decisions",
        "fallback_routing_decisions",
        "remediation_entries",
        "successful_returns",
        "bridge_completions",
    ]:
        try:
            summary[key] = max(0, int(raw.get(key, 0) or 0))
        except Exception:
            summary[key] = 0
    summary["ppo_usage_rate"] = _safe_rate(
        summary["ppo_routing_decisions"],
        summary["total_routing_decisions"],
    )
    summary["return_success_rate"] = _safe_rate(
        summary["successful_returns"],
        summary["remediation_entries"],
    )
    return summary


def _update_routing_summary(
    routing_session: dict[str, Any],
    *,
    decision_source: str | None,
    entered_remediation: bool,
    successful_return: bool,
    bridge_completed: bool,
) -> dict[str, Any]:
    summary = _normalize_routing_summary(routing_session.get("routing_summary"))
    summary["total_routing_decisions"] += 1
    if str(decision_source) == "ppo":
        summary["ppo_routing_decisions"] += 1
    else:
        summary["fallback_routing_decisions"] += 1
    if entered_remediation:
        summary["remediation_entries"] += 1
    if successful_return:
        summary["successful_returns"] += 1
    if bridge_completed:
        summary["bridge_completions"] += 1
    summary["ppo_usage_rate"] = _safe_rate(
        summary["ppo_routing_decisions"],
        summary["total_routing_decisions"],
    )
    summary["return_success_rate"] = _safe_rate(
        summary["successful_returns"],
        summary["remediation_entries"],
    )
    routing_session["routing_summary"] = summary
    return summary


def _normalize_routing_timeline(raw: Any) -> list[dict[str, Any]]:
    if not isinstance(raw, list):
        return []
    out: list[dict[str, Any]] = []
    for item in raw:
        if isinstance(item, dict):
            out.append(dict(item))
    return out


def _append_routing_timeline(
    routing_session: dict[str, Any],
    *,
    step: int,
    current_skill: str,
    selected_agent_skill: str | None,
    is_correct: bool | None,
    fail_streak: int,
    frustration: float,
    cross_skill_trigger: bool,
    allowed_actions: list[str],
    ppo_action: str | None,
    decision_source: str | None,
    in_remediation: bool,
    remediation_step_count: int,
    bridge_active: bool,
    final_route_reward: float,
) -> list[dict[str, Any]]:
    timeline = _normalize_routing_timeline(routing_session.get("routing_timeline"))
    timeline.append(
        {
            "step": int(step),
            "current_skill": str(current_skill),
            "selected_agent_skill": selected_agent_skill,
            "is_correct": is_correct,
            "fail_streak": int(fail_streak),
            "frustration": float(frustration),
            "cross_skill_trigger": bool(cross_skill_trigger),
            "allowed_actions": list(allowed_actions),
            "ppo_action": ppo_action,
            "decision_source": decision_source,
            "in_remediation": bool(in_remediation),
            "remediation_step_count": int(remediation_step_count),
            "bridge_active": bool(bridge_active),
            "final_route_reward": float(final_route_reward),
        }
    )
    routing_session["routing_timeline"] = timeline
    return timeline


def summarize_routing_timeline(timeline: Any) -> dict[str, Any]:
    rows = _normalize_routing_timeline(timeline)
    total_steps = len(rows)
    visited_skills: set[str] = set()
    ppo_decision_count = 0
    fallback_decision_count = 0
    total_route_reward = 0.0

    remediation_count = 0
    return_count = 0
    bridge_count = 0
    remediation_entered = False

    first_remediation_step: int | None = None
    first_return_step: int | None = None
    first_bridge_step: int | None = None

    prev_in_remediation = False
    prev_bridge_active = False

    for row in rows:
        current_skill = str(row.get("current_skill") or "").strip()
        selected_skill = str(row.get("selected_agent_skill") or "").strip()
        resolved_skill = selected_skill or current_skill
        if resolved_skill:
            visited_skills.add(resolved_skill)

        decision_source = str(row.get("decision_source") or "").strip()
        if decision_source == "ppo":
            ppo_decision_count += 1
        else:
            fallback_decision_count += 1

        try:
            total_route_reward += float(row.get("final_route_reward", 0.0) or 0.0)
        except Exception:
            pass

        in_remediation = bool(row.get("in_remediation", False))
        bridge_active = bool(row.get("bridge_active", False))
        step_value = row.get("step")
        try:
            step_num = int(step_value) if step_value is not None else None
        except Exception:
            step_num = None

        if in_remediation and not prev_in_remediation:
            remediation_count += 1
            remediation_entered = True
            if first_remediation_step is None and step_num is not None:
                first_remediation_step = step_num

        explicit_return = str(row.get("ppo_action") or "").strip() == "return"
        transitioned_return = prev_in_remediation and not in_remediation
        if explicit_return or transitioned_return:
            return_count += 1
            if first_return_step is None and step_num is not None:
                first_return_step = step_num

        if bridge_active and not prev_bridge_active:
            bridge_count += 1
            if first_bridge_step is None and step_num is not None:
                first_bridge_step = step_num

        prev_in_remediation = in_remediation
        prev_bridge_active = bridge_active

    final_skill = ""
    if rows:
        last = rows[-1]
        final_skill = str(last.get("selected_agent_skill") or last.get("current_skill") or "").strip()

    avg_route_reward = (total_route_reward / float(total_steps)) if total_steps > 0 else 0.0

    return {
        "total_steps": total_steps,
        "unique_skills_visited": sorted(visited_skills),
        "remediation_entered": remediation_entered,
        "remediation_count": remediation_count,
        "return_count": return_count,
        "bridge_count": bridge_count,
        "final_skill": final_skill,
        "ppo_decision_count": ppo_decision_count,
        "fallback_decision_count": fallback_decision_count,
        "total_route_reward": round(total_route_reward, 4),
        "avg_route_reward": round(avg_route_reward, 4),
        "first_remediation_step": first_remediation_step,
        "first_return_step": first_return_step,
        "first_bridge_step": first_bridge_step,
    }


def _entry_subskills(entry: CatalogEntry, family_subskill_map: dict[str, list[str]]) -> list[str]:
    key = f"{entry.skill_id}:{entry.family_id}"
    if key in family_subskill_map and family_subskill_map[key]:
        return family_subskill_map[key]
    if entry.family_id in family_subskill_map and family_subskill_map[entry.family_id]:
        return family_subskill_map[entry.family_id]
    return list(entry.subskill_nodes or [])


def _filter_entries_for_agent_and_subskill(
    entries: list[CatalogEntry],
    *,
    selected_agent_skill: str | None,
    selected_subskill: str | None,
    family_subskill_map: dict[str, list[str]],
) -> list[CatalogEntry]:
    if not selected_agent_skill:
        return []
    filtered = [
        entry
        for entry in entries
        if resolve_agent_skill(entry.skill_id) == selected_agent_skill
    ]
    if not filtered:
        return []
    if not selected_subskill:
        return filtered
    filtered_subskill = [
        entry
        for entry in filtered
        if selected_subskill in _entry_subskills(entry, family_subskill_map)
    ]
    return filtered_subskill or filtered


def _same_subskill_streak(rows: list[AdaptiveLearningLog], last_subskill: str) -> int:
    if not last_subskill:
        return 0
    streak = 0
    for row in reversed(rows):
        row_subskills = _normalize_subskills(row.target_subskills)
        if last_subskill in row_subskills:
            streak += 1
        else:
            break
    return streak


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


def _build_observability_payload(
    *,
    selected_agent_skill: str | None,
    selected_subskill: str | None,
    selected_family_id: str | None,
    selection_mode: str | None,
    selection_debug: dict[str, Any] | None,
    fail_streak: int | None,
    frustration_index: int | None,
) -> dict[str, Any]:
    mode = (selection_mode or "").strip() or "legacy_fallback"
    debug = selection_debug if isinstance(selection_debug, dict) else {}
    if not debug:
        debug = {"reason": "policy_debug_not_available"}
    return {
        "selected_agent_skill": selected_agent_skill,
        "selected_subskill": selected_subskill,
        "selected_family_id": selected_family_id or "",
        "selection_mode": mode,
        "selection_debug": debug,
        "fail_streak": int(fail_streak or 0),
        "frustration_index": int(frustration_index or 0),
    }


def _safe(value: Any) -> Any:
    return value if value is not None else None


def _policy_trace(
    *,
    system_skill_id: Any = None,
    selected_agent_skill: Any = None,
    selected_subskill: Any = None,
    allowed_agent_skills: Any = None,
    mapping_candidates: Any = None,
    selected_family_id: Any = None,
    selection_mode: Any = None,
    fallback_reason: Any = None,
    frustration_index: Any = None,
    fail_streak: Any = None,
    tag: str = "",
) -> None:
    line = (
        "[adaptive_phase1_policy] "
        f"tag={tag or None} "
        f"system_skill_id={_safe(system_skill_id)} "
        f"selected_agent_skill={_safe(selected_agent_skill)} "
        f"selected_subskill={_safe(selected_subskill)} "
        f"allowed_agent_skills={_safe(allowed_agent_skills)} "
        f"mapping_candidates={_safe(mapping_candidates)} "
        f"selected_family_id={_safe(selected_family_id)} "
        f"selection_mode={_safe(selection_mode)} "
        f"fallback_reason={_safe(fallback_reason)} "
        f"frustration_index={_safe(frustration_index)} "
        f"fail_streak={_safe(fail_streak)}"
    )
    print(line, flush=True)
    POLICY_LOGGER.info(line)


def _emit_decision_trace(trace: dict[str, Any]) -> None:
    if not ADAPTIVE_DEBUG:
        return
    print(
        "[adaptive_phase1_policy] decision_trace=" + json.dumps(trace, ensure_ascii=False, default=str),
        flush=True,
    )


def _compute_routing_reward_components(
    *,
    is_correct: bool | None,
    previous_fail_streak: int,
    same_skill_streak: int,
    route_action: str,
    diagnosis_confidence: float,
    just_returned_from_remediation: bool,
) -> dict[str, float]:
    correctness_reward = 0.0
    if is_correct is not None:
        correctness_reward = 1.0 if bool(is_correct) else -0.5

    recovery_reward = 0.0
    if bool(is_correct) and int(previous_fail_streak) >= 2:
        recovery_reward = 0.5

    return_success_reward = 0.0
    if bool(is_correct) and bool(just_returned_from_remediation):
        return_success_reward = 0.8

    stagnation_penalty = -0.2 * max(0, int(same_skill_streak) - 3)

    unnecessary_route_penalty = 0.0
    if str(route_action) == "remediate" and float(diagnosis_confidence) < 0.8:
        unnecessary_route_penalty = -0.5

    final_route_reward = (
        correctness_reward
        + recovery_reward
        + return_success_reward
        + stagnation_penalty
        + unnecessary_route_penalty
    )

    return {
        "correctness_reward": float(correctness_reward),
        "recovery_reward": float(recovery_reward),
        "return_success_reward": float(return_success_reward),
        "stagnation_penalty": float(stagnation_penalty),
        "unnecessary_route_penalty": float(unnecessary_route_penalty),
        "final_route_reward": float(final_route_reward),
    }


def submit_and_get_next(payload: dict[str, Any]) -> dict[str, Any]:
    print("[adaptive_phase1_policy] enter submit_and_get_next", flush=True)
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

    history_rows = (
        db.session.query(AdaptiveLearningLog)
        .filter_by(student_id=student_id, session_id=session_id)
        .order_by(AdaptiveLearningLog.step_number.asc())
        .all()
    )
    fail_streak = 0
    for row in reversed(history_rows):
        if row.is_correct:
            break
        fail_streak += 1

    visited = [row.target_family_id for row in history_rows]
    answered_steps = requested_step if last_is_correct is not None else 0
    routing_session = dict(payload.get("routing_state") or {})
    routing_summary = _normalize_routing_summary(routing_session.get("routing_summary"))
    routing_session["routing_summary"] = routing_summary
    routing_timeline = _normalize_routing_timeline(routing_session.get("routing_timeline"))
    routing_session["routing_timeline"] = routing_timeline
    routing_timeline_summary = summarize_routing_timeline(routing_timeline)
    routing_session["routing_timeline_summary"] = routing_timeline_summary
    if last_is_correct is not None and routing_session.get("in_remediation", False):
        recent_results = list(routing_session.get("recent_results") or [])
        recent_results.append(bool(last_is_correct))
        routing_session["recent_results"] = recent_results[-4:]
        routing_session["steps_taken"] = int(routing_session.get("steps_taken", 0) or 0) + 1
    return_ready, return_reason = should_return_from_remediation(routing_session)
    should_finish = False
    if last_is_correct is not None:
        if routing_session.get("in_remediation", False):
            should_finish = False
        elif answered_steps >= MAX_DIAGNOSIS_STEPS:
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

    system_skill_id = str(payload.get("skill_id") or (entries[0].skill_id if entries else "")).strip()
    allowed_agent_skills = list(SKILL_LABELS)
    if system_skill_id == "jh_數學1上_FourArithmeticOperationsOfIntegers":
        allowed_agent_skills = ["integer_arithmetic"]
    if not allowed_agent_skills:
        print(
            "[adaptive_phase1_policy][WARNING] allowed_agent_skills is empty; fallback to full SKILL_LABELS",
            flush=True,
        )
        allowed_agent_skills = list(SKILL_LABELS)
    decision_trace: dict[str, Any] = {
        "system_skill_id": system_skill_id or None,
        "agent_state": None,
        "allowed_agent_skills": allowed_agent_skills,
        "allowed_actions": None,
        "routing_state": routing_session,
        "diagnosis": None,
        "policy_logits": None,
        "action_idx": None,
        "route_policy_logits": None,
        "route_action_idx": None,
        "route_action": None,
        "selected_agent_skill": None,
        "selected_subskill": None,
        "mapping_candidates": [],
        "selected_family_id": None,
        "selection_mode": None,
        "fallback_reason": None,
        "decision_source": None,
        "ppo_error_type": None,
        "ppo_error_message": None,
        "return_ready": return_ready,
        "return_reason": return_reason,
        "cross_skill_trigger": False,
        "bridge_active": int(routing_session.get("bridge_remaining", 0) or 0) > 0,
        "routing_reward": None,
        "routing_summary": routing_summary,
        "routing_timeline": routing_timeline,
        "routing_timeline_summary": routing_timeline_summary,
    }

    if should_finish:
        completed_observability = _build_observability_payload(
            selected_agent_skill=payload.get("selected_agent_skill"),
            selected_subskill=(
                payload.get("selected_subskill")
                or (last_subskills[0] if last_subskills else None)
            ),
            selected_family_id=_normalize_family_id(payload.get("last_family_id")),
            selection_mode=payload.get("selection_mode") or "legacy_fallback",
            selection_debug=(
                payload.get("selection_debug")
                if isinstance(payload.get("selection_debug"), dict)
                else {"reason": "completed_before_next_selection"}
            ),
            fail_streak=fail_streak,
            frustration_index=frustration_index,
        )
        _policy_trace(
            tag="completed",
            system_skill_id=payload.get("skill_id"),
            selected_agent_skill=completed_observability.get("selected_agent_skill"),
            selected_subskill=completed_observability.get("selected_subskill"),
            allowed_agent_skills=allowed_agent_skills,
            mapping_candidates=[],
            selected_family_id=completed_observability.get("selected_family_id"),
            selection_mode=completed_observability.get("selection_mode"),
            fallback_reason=completed_observability.get("selection_debug", {}).get("reason"),
            frustration_index=completed_observability.get("frustration_index"),
            fail_streak=completed_observability.get("fail_streak"),
        )
        decision_trace.update(
            {
                "selected_agent_skill": completed_observability.get("selected_agent_skill"),
                "selected_subskill": completed_observability.get("selected_subskill"),
                "selected_family_id": completed_observability.get("selected_family_id"),
                "selection_mode": completed_observability.get("selection_mode"),
                "fallback_reason": completed_observability.get("selection_debug", {}).get("reason"),
                "decision_source": completed_observability.get("selection_debug", {}).get("decision_source"),
                "routing_summary": routing_summary,
                "routing_timeline": routing_timeline,
                "routing_timeline_summary": routing_timeline_summary,
            }
        )
        completed_observability.setdefault("selection_debug", {})
        if isinstance(completed_observability["selection_debug"], dict):
            completed_observability["selection_debug"]["routing_summary"] = routing_summary
            completed_observability["selection_debug"]["routing_timeline"] = routing_timeline
            completed_observability["selection_debug"]["routing_timeline_summary"] = routing_timeline_summary
        _emit_decision_trace(decision_trace)
        if ROUTING_SUMMARY_LOG:
            print(
                f"[ROUTING_SUMMARY] session_id={session_id} summary={json.dumps(routing_summary, ensure_ascii=False)}",
                flush=True,
            )
        if (
            decision_trace["selected_agent_skill"] is not None
            and decision_trace["selected_agent_skill"] not in allowed_agent_skills
        ):
            print(
                f"[adaptive_phase1_policy][ERROR] selected_agent_skill_not_allowed selected_agent_skill={decision_trace['selected_agent_skill']} allowed_agent_skills={allowed_agent_skills}",
                flush=True,
            )
        if (
            decision_trace["selected_subskill"] is not None
            and not decision_trace["mapping_candidates"]
        ):
            print(
                f"[adaptive_phase1_policy][ERROR] selected_subskill_without_mapping_candidates selected_subskill={decision_trace['selected_subskill']}",
                flush=True,
            )
        if decision_trace["selection_mode"] == "legacy_fallback":
            print(
                f"[adaptive_phase1_policy][WARNING] legacy_fallback_selected_family selected_family_id={decision_trace['selected_family_id']} fallback_reason={decision_trace['fallback_reason']}",
                flush=True,
            )
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
            "frustration_index": completed_observability["frustration_index"],
            "execution_latency": 0,
            "target_family_id": _normalize_family_id(payload.get("last_family_id")),
            "target_subskills": last_subskills,
            "new_question_data": {},
            "completed": True,
            "summary": summary,
            "routing_state": routing_session,
            "routing_summary": routing_summary,
            "routing_timeline": routing_timeline,
            "routing_timeline_summary": routing_timeline_summary,
            **completed_observability,
        }

    last_family_id = _normalize_family_id(payload.get("last_family_id"))
    selection_mode = "legacy_fallback"
    selected_agent_skill: str | None = None
    selected_subskill: str | None = None
    policy_debug: dict[str, Any] = {"reason": "legacy_fallback_default"}
    fallback_reason: str | None = None
    mapping_candidates: list[str] = []

    try:
        family_subskill_map = load_family_subskill_map()
        agent_state = build_agent_state(
            session={
                "session_id": session_id,
                "skill_id": system_skill_id,
                "last_family_id": last_family_id,
                "last_subskills": last_subskills,
            },
            history=history_rows,
            system_skill_id=system_skill_id,
            current_apr=current_apr,
            frustration_index=frustration_index,
            last_is_correct=last_is_correct,
        )
        decision_trace["agent_state"] = agent_state
        _policy_trace(
            tag="state_built",
            system_skill_id=system_skill_id,
            selected_agent_skill=selected_agent_skill,
            selected_subskill=selected_subskill,
            allowed_agent_skills=allowed_agent_skills,
            mapping_candidates=mapping_candidates,
            selected_family_id=None,
            selection_mode=selection_mode,
            fallback_reason=fallback_reason,
            frustration_index=frustration_index,
            fail_streak=fail_streak,
        )
        current_skill = resolve_agent_skill(system_skill_id) or "integer_arithmetic"
        current_subskill = (last_subskills[0] if last_subskills else "")
        frustration_norm = max(0.0, min(1.0, float(frustration_index) / 3.0))
        diagnosis = rag_diagnose(
            current_skill=current_skill,
            current_subskill=current_subskill,
            student_answer=str(payload.get("last_user_answer", "") or payload.get("user_answer", "")),
            expected_answer=str(payload.get("last_expected_answer", "")),
            is_correct=last_is_correct,
            fail_streak=fail_streak,
            frustration=frustration_norm,
            same_skill_streak=agent_state.get("same_skill_streak", 0),
        )
        cross_skill_trigger = compute_cross_skill_trigger(
            fail_streak=fail_streak,
            frustration=frustration_norm,
            same_skill_streak=int(agent_state.get("same_skill_streak", 0) or 0),
            diagnosis=diagnosis,
            current_skill=current_skill,
        )

        routing_state = build_routing_state(
            agent_state=agent_state,
            diagnosis=diagnosis,
            current_skill=current_skill,
            current_subskill=current_subskill,
            routing_session=routing_session,
        )
        in_remediation = bool(routing_session.get("in_remediation", False))
        pre_bridge_remaining = int(routing_session.get("bridge_remaining", 0) or 0)
        lock_min_steps = int(routing_session.get("lock_min_steps", 2) or 2)
        rem_steps = int(routing_session.get("steps_taken", 0) or 0)
        action_mask = build_action_mask(
            in_remediation=in_remediation,
            remediation_step_count=rem_steps,
            lock_min_steps=lock_min_steps,
            cross_skill_trigger=cross_skill_trigger,
        )
        allowed_actions = [k for k, v in action_mask.items() if v]
        policy_findings_hints: dict[str, Any] = {}
        if ENABLE_POLICY_FINDINGS:
            policy_findings_hints = build_policy_findings_hints(
                fail_streak=fail_streak,
                frustration=frustration_norm,
                same_skill_streak=int(agent_state.get("same_skill_streak", 0) or 0),
                cross_skill_trigger=cross_skill_trigger,
                allowed_actions=allowed_actions,
            )
            if (
                not cross_skill_trigger
                and bool(policy_findings_hints.get("trigger_hints", {}).get("effective_cross_skill_trigger", False))
            ):
                cross_skill_trigger = True
                action_mask = build_action_mask(
                    in_remediation=in_remediation,
                    remediation_step_count=rem_steps,
                    lock_min_steps=lock_min_steps,
                    cross_skill_trigger=cross_skill_trigger,
                )
                allowed_actions = [k for k, v in action_mask.items() if v]
        if in_remediation and return_ready:
            action_mask["return"] = True
            allowed_actions = [k for k, v in action_mask.items() if v]

        if in_remediation:
            rem_skill = str(routing_session.get("remediation_skill") or current_skill)
            if rem_steps < lock_min_steps:
                allowed_agent_skills = [rem_skill]
            else:
                allowed_agent_skills = [rem_skill, str(routing_session.get("origin_skill") or current_skill)]
        else:
            allowed_agent_skills = [current_skill]
            if cross_skill_trigger and diagnosis.get("suggested_prereq_skill"):
                allowed_agent_skills = [current_skill, str(diagnosis.get("suggested_prereq_skill"))]
        allowed_actions = [k for k, v in action_mask.items() if v]

        print(
            "[ROUTING] "
            f"current_skill={current_skill} current_subskill={current_subskill} "
            f"fail_streak={fail_streak} frustration={frustration_norm:.2f} "
            f"diag_error_concept={diagnosis.get('error_concept')} "
            f"diag_confidence={diagnosis.get('diagnosis_confidence')} "
            f"suggested_prereq_skill={diagnosis.get('suggested_prereq_skill')} "
            f"cross_skill_trigger={cross_skill_trigger} "
            f"allowed_agent_skills={allowed_agent_skills} "
            f"allowed_actions={allowed_actions} "
            f"findings_enabled={ENABLE_POLICY_FINDINGS}",
            flush=True,
        )

        policy_model = load_phase2_policy_model()
        route_action, route_logits, route_action_idx, route_decision_source = select_route_action_with_ppo(
            route_state=routing_state,
            action_mask=action_mask,
            model=policy_model,
        )
        route_debug: dict[str, Any] = {"action_mask": action_mask}
        if route_action is None:
            route_action, route_debug = select_route_action_heuristic(
                route_state=routing_state,
                action_mask=action_mask,
            )
            if route_decision_source == "ppo_error":
                route_decision_source = "ppo_error_fallback"
            else:
                route_decision_source = "heuristic_fallback"
            fallback_reason = route_decision_source

        updated_routing, routed_skill, routed_subskill = apply_routing_action(
            action=route_action,
            current_skill=current_skill,
            current_subskill=current_subskill,
            diagnosis=diagnosis,
            routing_session=routing_session,
        )
        routing_session = updated_routing
        selected_agent_skill = routed_skill
        route_subskill_override = routed_subskill
        post_in_remediation = bool(routing_session.get("in_remediation", False))
        post_bridge_remaining = int(routing_session.get("bridge_remaining", 0) or 0)
        entered_remediation = (not bool(in_remediation)) and post_in_remediation
        bridge_completed = pre_bridge_remaining > 0 and post_bridge_remaining <= 0
        just_returned_from_remediation = (
            bool(in_remediation)
            and str(route_action) == "return"
            and not bool(routing_session.get("in_remediation", False))
        )
        routing_reward = _compute_routing_reward_components(
            is_correct=last_is_correct,
            previous_fail_streak=fail_streak,
            same_skill_streak=int(agent_state.get("same_skill_streak", 0) or 0),
            route_action=str(route_action),
            diagnosis_confidence=float(diagnosis.get("diagnosis_confidence", 0.0) or 0.0),
            just_returned_from_remediation=just_returned_from_remediation,
        )
        if ENABLE_POLICY_FINDINGS and policy_findings_hints:
            reward_hints = policy_findings_hints.get("reward_hints", {})
            routing_reward["stagnation_penalty"] = float(routing_reward["stagnation_penalty"]) + float(
                reward_hints.get("stagnation_penalty_bonus", 0.0) or 0.0
            )
            if bool(last_is_correct):
                routing_reward["recovery_reward"] = float(routing_reward["recovery_reward"]) + float(
                    reward_hints.get("recovery_bonus", 0.0) or 0.0
                )
            routing_reward["final_route_reward"] = (
                float(routing_reward["correctness_reward"])
                + float(routing_reward["recovery_reward"])
                + float(routing_reward["return_success_reward"])
                + float(routing_reward["stagnation_penalty"])
                + float(routing_reward["unnecessary_route_penalty"])
            )
        routing_summary = _update_routing_summary(
            routing_session,
            decision_source=route_decision_source,
            entered_remediation=entered_remediation,
            successful_return=just_returned_from_remediation,
            bridge_completed=bridge_completed,
        )
        routing_timeline = _append_routing_timeline(
            routing_session,
            step=next_step_number,
            current_skill=current_skill,
            selected_agent_skill=selected_agent_skill,
            is_correct=last_is_correct,
            fail_streak=fail_streak,
            frustration=frustration_norm,
            cross_skill_trigger=cross_skill_trigger,
            allowed_actions=allowed_actions,
            ppo_action=(str(route_action) if route_action is not None else None),
            decision_source=route_decision_source,
            in_remediation=post_in_remediation,
            remediation_step_count=int(routing_session.get("steps_taken", 0) or 0),
            bridge_active=(int(routing_session.get("bridge_remaining", 0) or 0) > 0),
            final_route_reward=float(routing_reward["final_route_reward"]),
        )
        routing_timeline_summary = summarize_routing_timeline(routing_timeline)
        routing_session["routing_timeline_summary"] = routing_timeline_summary

        if route_action_idx is not None and route_action_idx not in IDX_TO_ROUTE:
            print(
                f"[adaptive_phase1_policy][ERROR] invalid_route_action_idx action_idx={route_action_idx} idx_to_route={IDX_TO_ROUTE}",
                flush=True,
            )
        if selected_agent_skill not in allowed_agent_skills:
            print(
                f"[adaptive_phase1_policy][ERROR] routed skill not allowed selected_agent_skill={selected_agent_skill} allowed_agent_skills={allowed_agent_skills}",
                flush=True,
            )
            selected_agent_skill = allowed_agent_skills[0]
            fallback_reason = fallback_reason or "routed_skill_not_allowed"
            route_decision_source = "heuristic_fallback"

        print(
            "[ROUTING] "
            f"ppo_action={route_action} decision_source={route_decision_source} "
            f"in_remediation={routing_session.get('in_remediation')} "
            f"origin_skill={routing_session.get('origin_skill')} "
            f"remediation_skill={routing_session.get('remediation_skill')} "
            f"steps_taken={routing_session.get('steps_taken')} "
            f"return_ready={return_ready} return_reason={return_reason} "
            f"correctness_reward={routing_reward['correctness_reward']:.2f} "
            f"recovery_reward={routing_reward['recovery_reward']:.2f} "
            f"return_success_reward={routing_reward['return_success_reward']:.2f} "
            f"stagnation_penalty={routing_reward['stagnation_penalty']:.2f} "
            f"unnecessary_route_penalty={routing_reward['unnecessary_route_penalty']:.2f} "
            f"final_route_reward={routing_reward['final_route_reward']:.2f}",
            flush=True,
        )
        if ROUTING_SUMMARY_LOG:
            print(
                f"[ROUTING_SUMMARY] session_id={session_id} summary={json.dumps(routing_summary, ensure_ascii=False)}",
                flush=True,
            )
        if routing_session.get("in_remediation", False):
            recent_results = list(routing_session.get("recent_results") or [])
            recent_acc = (
                sum(1 for x in recent_results if bool(x)) / float(len(recent_results))
                if recent_results else 0.0
            )
            print(
                "[REMEDIATION] "
                f"origin_skill={routing_session.get('origin_skill')} "
                f"remediation_skill={routing_session.get('remediation_skill')} "
                f"steps_taken={routing_session.get('steps_taken')} "
                f"recent_accuracy={recent_acc:.2f} "
                f"return_ready={return_ready} "
                f"correctness_reward={routing_reward['correctness_reward']:.2f} "
                f"recovery_reward={routing_reward['recovery_reward']:.2f} "
                f"return_success_reward={routing_reward['return_success_reward']:.2f} "
                f"stagnation_penalty={routing_reward['stagnation_penalty']:.2f} "
                f"unnecessary_route_penalty={routing_reward['unnecessary_route_penalty']:.2f} "
                f"final_route_reward={routing_reward['final_route_reward']:.2f}",
                flush=True,
            )

        ppo_error = get_last_ppo_error()
        decision_trace["diagnosis"] = diagnosis
        decision_trace["cross_skill_trigger"] = cross_skill_trigger
        decision_trace["routing_state"] = routing_state
        decision_trace["allowed_agent_skills"] = allowed_agent_skills
        decision_trace["allowed_actions"] = allowed_actions
        decision_trace["ppo_error_type"] = ppo_error.get("type")
        decision_trace["ppo_error_message"] = ppo_error.get("message")
        decision_trace["route_policy_logits"] = route_logits
        decision_trace["route_action_idx"] = route_action_idx
        decision_trace["route_action"] = route_action
        decision_trace["decision_source"] = route_decision_source
        decision_trace["selected_agent_skill"] = selected_agent_skill
        decision_trace["routing_reward"] = routing_reward
        decision_trace["policy_findings_hints"] = policy_findings_hints
        decision_trace["policy_logits"] = route_logits
        decision_trace["action_idx"] = route_action_idx
        decision_trace["routing_summary"] = routing_summary
        decision_trace["routing_timeline"] = routing_timeline
        decision_trace["routing_timeline_summary"] = routing_timeline_summary
        _policy_trace(
            tag="selected_agent_skill",
            system_skill_id=system_skill_id,
            selected_agent_skill=selected_agent_skill,
            selected_subskill=selected_subskill,
            allowed_agent_skills=allowed_agent_skills,
            mapping_candidates=mapping_candidates,
            selected_family_id=None,
            selection_mode=selection_mode,
            fallback_reason=fallback_reason,
            frustration_index=frustration_index,
            fail_streak=fail_streak,
        )
        selected_subskill, subskill_debug = select_subskill(
            selected_agent_skill or "",
            session={
                "session_id": session_id,
                "last_subskill": (last_subskills[0] if last_subskills else ""),
            },
            history=history_rows,
            diagnostics={
                "last_error_type": payload.get("error_type", ""),
                "last_subskill": (last_subskills[0] if last_subskills else ""),
                "same_subskill_streak": _same_subskill_streak(
                    history_rows, last_subskills[0] if last_subskills else ""
                ),
            },
        )
        if route_subskill_override:
            selected_subskill = route_subskill_override
            route_debug["subskill_override"] = route_subskill_override
        decision_trace["selected_subskill"] = selected_subskill
        _policy_trace(
            tag="selected_subskill",
            system_skill_id=system_skill_id,
            selected_agent_skill=selected_agent_skill,
            selected_subskill=selected_subskill,
            allowed_agent_skills=allowed_agent_skills,
            mapping_candidates=mapping_candidates,
            selected_family_id=None,
            selection_mode=selection_mode,
            fallback_reason=fallback_reason,
            frustration_index=frustration_index,
            fail_streak=fail_streak,
        )
        policy_debug = {
            **policy_debug,
            "decision_source": route_decision_source,
            "policy_logits": route_logits,
            "action_idx": route_action_idx,
            "route_action": route_action,
            "route_action_idx": route_action_idx,
            "route_policy_logits": route_logits,
            "routing_state": routing_session,
            "diagnosis": diagnosis,
            "route_debug": route_debug,
            "cross_skill_trigger": cross_skill_trigger,
            "bridge_active": int(routing_session.get("bridge_remaining", 0) or 0) > 0,
            "correctness_reward": routing_reward["correctness_reward"],
            "recovery_reward": routing_reward["recovery_reward"],
            "return_success_reward": routing_reward["return_success_reward"],
            "stagnation_penalty": routing_reward["stagnation_penalty"],
            "unnecessary_route_penalty": routing_reward["unnecessary_route_penalty"],
            "final_route_reward": routing_reward["final_route_reward"],
            "ppo_error_type": decision_trace.get("ppo_error_type"),
            "ppo_error_message": decision_trace.get("ppo_error_message"),
            "agent_debug": {"source": "route_policy"},
            "subskill_debug": subskill_debug,
            "routing_summary": routing_summary,
            "routing_timeline": routing_timeline,
            "routing_timeline_summary": routing_timeline_summary,
            "policy_findings_hints": policy_findings_hints,
        }
        policy_debug["system_skill_id"] = system_skill_id
        policy_debug["allowed_agent_skills"] = allowed_agent_skills
        policy_debug["action_index_mapping_check"] = {
            "idx_to_skill": IDX_TO_SKILL,
            "selected_agent_skill_index": (
                SKILL_LABELS.index(selected_agent_skill)
                if selected_agent_skill in SKILL_LABELS
                else None
            ),
            "note": "phase2 uses explicit IDX_TO_SKILL mapping",
        }
        phase1_entries = _filter_entries_for_agent_and_subskill(
            entries,
            selected_agent_skill=selected_agent_skill,
            selected_subskill=selected_subskill,
            family_subskill_map=family_subskill_map,
        )
        mapping_candidates = [f"{entry.skill_id}:{entry.family_id}" for entry in phase1_entries]
        decision_trace["mapping_candidates"] = mapping_candidates
        if phase1_entries:
            next_entry = choose_next_family(
                entries=phase1_entries,
                visited_family_ids=visited,
                strategy=strategy,
                last_family_id=last_family_id,
            )
            selection_mode = "phase1_agent_skill_policy"
            fallback_reason = None
        else:
            next_entry = choose_next_family(
                entries=entries,
                visited_family_ids=visited,
                strategy=strategy,
                last_family_id=last_family_id,
            )
            selection_mode = "legacy_fallback"
            fallback_reason = "phase1_no_matching_family_mapping"
            policy_debug = {
                **policy_debug,
                "reason": fallback_reason,
            }
        if selection_mode == "legacy_fallback":
            print(
                f"[adaptive_phase1_policy] fallback reason={fallback_reason if fallback_reason is not None else None}",
                flush=True,
            )
        decision_trace["selected_family_id"] = next_entry.family_id if next_entry is not None else None
        decision_trace["selection_mode"] = selection_mode
        decision_trace["fallback_reason"] = fallback_reason
        _policy_trace(
            tag="selected_family",
            system_skill_id=system_skill_id,
            selected_agent_skill=selected_agent_skill,
            selected_subskill=selected_subskill,
            allowed_agent_skills=allowed_agent_skills,
            mapping_candidates=mapping_candidates,
            selected_family_id=(next_entry.family_id if next_entry is not None else None),
            selection_mode=selection_mode,
            fallback_reason=fallback_reason,
            frustration_index=frustration_index,
            fail_streak=fail_streak,
        )
    except Exception as exc:
        next_entry = choose_next_family(
            entries=entries,
            visited_family_ids=visited,
            strategy=strategy,
            last_family_id=last_family_id,
        )
        selection_mode = "legacy_fallback"
        fallback_reason = "phase1_policy_error"
        policy_debug = {"reason": fallback_reason, "error": str(exc)}
        print(
            f"[adaptive_phase1_policy] fallback reason={fallback_reason if fallback_reason is not None else None}",
            flush=True,
        )
        _policy_trace(
            tag="exception_fallback",
            system_skill_id=system_skill_id,
            selected_agent_skill=selected_agent_skill,
            selected_subskill=selected_subskill,
            allowed_agent_skills=allowed_agent_skills,
            mapping_candidates=mapping_candidates,
            selected_family_id=(next_entry.family_id if next_entry is not None else None),
            selection_mode=selection_mode,
            fallback_reason=fallback_reason,
            frustration_index=frustration_index,
            fail_streak=fail_streak,
        )
        decision_trace["selected_family_id"] = next_entry.family_id if next_entry is not None else None
        decision_trace["selection_mode"] = selection_mode
        decision_trace["fallback_reason"] = fallback_reason

    _emit_decision_trace(decision_trace)
    if (
        decision_trace["selected_agent_skill"] is not None
        and decision_trace["selected_agent_skill"] not in allowed_agent_skills
    ):
        print(
            f"[adaptive_phase1_policy][ERROR] selected_agent_skill_not_allowed selected_agent_skill={decision_trace['selected_agent_skill']} allowed_agent_skills={allowed_agent_skills}",
            flush=True,
        )
    if (
        decision_trace["selected_subskill"] is not None
        and not decision_trace["mapping_candidates"]
    ):
        print(
            f"[adaptive_phase1_policy][ERROR] selected_subskill_without_mapping_candidates selected_subskill={decision_trace['selected_subskill']}",
            flush=True,
        )
    if decision_trace["selection_mode"] == "legacy_fallback":
        print(
            f"[adaptive_phase1_policy][WARNING] legacy_fallback_selected_family selected_family_id={decision_trace['selected_family_id']} fallback_reason={decision_trace['fallback_reason']}",
            flush=True,
        )

    observability = _build_observability_payload(
        selected_agent_skill=selected_agent_skill,
        selected_subskill=selected_subskill,
        selected_family_id=next_entry.family_id,
        selection_mode=selection_mode,
        selection_debug=policy_debug,
        fail_streak=fail_streak,
        frustration_index=frustration_index,
    )
    if isinstance(observability.get("selection_debug"), dict):
        observability["selection_debug"]["routing_summary"] = routing_summary
        observability["selection_debug"]["routing_timeline"] = _normalize_routing_timeline(
            routing_session.get("routing_timeline")
        )
        observability["selection_debug"]["routing_timeline_summary"] = summarize_routing_timeline(
            routing_session.get("routing_timeline")
        )

    started = time.perf_counter()
    question_payload = _generate_question_payload(next_entry)
    latency_ms = int((time.perf_counter() - started) * 1000)

    resolved_target_subskills = list(next_entry.subskill_nodes)
    if selected_subskill and selected_subskill not in resolved_target_subskills:
        resolved_target_subskills = [selected_subskill] + resolved_target_subskills

    return {
        "session_id": session_id,
        "step_number": next_step_number,
        "current_apr": current_apr,
        "ppo_strategy": strategy,
        "frustration_index": observability["frustration_index"],
        "execution_latency": latency_ms,
        "target_family_id": next_entry.family_id,
        "target_subskills": resolved_target_subskills,
        "new_question_data": question_payload,
        "completed": False,
        "routing_state": routing_session,
        "routing_summary": routing_summary,
        "routing_timeline": _normalize_routing_timeline(routing_session.get("routing_timeline")),
        "routing_timeline_summary": summarize_routing_timeline(routing_session.get("routing_timeline")),
        **observability,
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
