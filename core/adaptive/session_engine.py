# -*- coding: utf-8 -*-
from __future__ import annotations

import importlib
import importlib.util
import json
import logging
import os
import re
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
from .micro_generators import generate_micro_question, has_micro_generator
from .script_dispatch import call_adaptive_script
from .policy_findings_mapping import build_policy_findings_hints
from .ppo_adapter import (
    IDX_TO_SKILL,
    IDX_TO_ROUTE,
    SKILL_LABELS,
    choose_next_family,
    choose_strategy,
    get_last_ppo_error,
    get_last_route_policy_debug,
    load_phase2_policy_model,
    map_route_action_by_mode,
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
from .remediation_retriever import retrieve_remediation_candidates
from .state_builder import build_agent_state
from .subskill_ontology import normalize_runtime_subskill
from .subskill_selector import load_family_subskill_map, select_subskill
from .skill_diagnostic_labels import get_family_diagnostic_info
from .textbook_progression import (
    get_completion_gate,
    get_next_family,
    get_previous_family,
    get_prerequisite_candidates,
    load_textbook_progression,
)


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
ADAPTIVE_DEMO_SAFE_MODE: bool = str(os.getenv("ADAPTIVE_DEMO_SAFE_MODE", "1")).strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}
ADAPTIVE_USE_FULL_CATALOG: bool = str(os.getenv("ADAPTIVE_USE_FULL_CATALOG", "0")).strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}
DEMO_SAFE_FAMILIES_BY_AGENT_SKILL: dict[str, set[str]] = {
    "integer_arithmetic": {"I1", "I2", "I3", "I4", "I5", "I7", "I9", "I10"},
    "fraction_arithmetic": {"F11", "F12", "F13"},
    "polynomial_arithmetic": {"F1", "F2", "F5", "F11"},
    "radical_arithmetic": set(),
}
ASSESSMENT_POLY_FAMILY_IDS: set[str] = {"F1", "F2", "F5", "F11", "F7", "F8", "F9", "F10"}
ASSESSMENT_POLY_STANDARDIZED_CORE_FAMILIES: tuple[str, ...] = ("F1", "F2", "F5", "F11", "F7", "F8", "F9", "F10")
DEMO_ALLOWED_FAMILY_IDS: set[str] = {
    family_id
    for family_ids in DEMO_SAFE_FAMILIES_BY_AGENT_SKILL.values()
    for family_id in family_ids
}
DEMO_SCENARIO_PRIMARY_START = "F1"
DEMO_SCENARIO_REMEDIATION_ENTRY = "I1"


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
    current_family: str,
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
            "current_family": str(current_family or ""),
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
            "timestamp": float(time.time()),
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
) -> tuple[list[CatalogEntry], bool, bool]:
    if not selected_agent_skill:
        return [], False, False
    filtered = [
        entry
        for entry in entries
        if resolve_agent_skill(entry.skill_id) == selected_agent_skill
    ]
    if not filtered:
        return [], False, bool(selected_subskill)
    if not selected_subskill:
        return filtered, False, False
    filtered_subskill = [
        entry
        for entry in filtered
        if selected_subskill in _entry_subskills(entry, family_subskill_map)
    ]
    subskill_filter_hit = bool(filtered_subskill)
    fallback_to_skill_only = bool(selected_subskill) and not subskill_filter_hit
    return filtered_subskill or filtered, subskill_filter_hit, fallback_to_skill_only


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


def _consecutive_wrong_on_family(rows: list[AdaptiveLearningLog], family_id: str) -> int:
    key = _normalize_family_id(family_id)
    if not key:
        return 0
    streak = 0
    for row in reversed(rows):
        row_family = _normalize_family_id(row.target_family_id)
        if row_family != key:
            break
        if bool(row.is_correct):
            break
        streak += 1
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


def _apply_demo_safe_family_filter(
    entries: list[CatalogEntry],
    *,
    mode: str = "teaching",
    system_skill_id: str = "",
) -> list[CatalogEntry]:
    if not ADAPTIVE_DEMO_SAFE_MODE or ADAPTIVE_USE_FULL_CATALOG:
        return entries
    normalized_mode = _normalize_mode(mode)
    is_poly_assessment = (
        normalized_mode == "assessment"
        and str(system_skill_id or "").strip().endswith("FourArithmeticOperationsOfPolynomial")
    )
    kept: list[CatalogEntry] = []
    removed: list[str] = []
    for entry in entries:
        agent_skill = resolve_agent_skill(entry.skill_id) or ""
        allowed = DEMO_SAFE_FAMILIES_BY_AGENT_SKILL.get(agent_skill)
        if is_poly_assessment and agent_skill == "polynomial_arithmetic":
            allowed = ASSESSMENT_POLY_FAMILY_IDS
        if allowed is None:
            kept.append(entry)
            continue
        if entry.family_id in allowed:
            kept.append(entry)
        else:
            removed.append(f"{entry.skill_id}:{entry.family_id}")
    if removed:
        POLICY_LOGGER.info(
            "[adaptive_demo_safe] enabled=%s removed_families=%s",
            ADAPTIVE_DEMO_SAFE_MODE,
            ",".join(removed),
        )
    return kept


def _clamp01(value: Any, default: float = 0.0) -> float:
    try:
        x = float(value)
    except Exception:
        x = float(default)
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


def _compute_remediation_mastery(
    *,
    routing_session: dict[str, Any],
    current_apr: float,
) -> tuple[float, str]:
    recent_results = list(routing_session.get("recent_results") or [])
    prior_mastery = _clamp01(routing_session.get("remediation_mastery", 0.45), 0.45)
    apr_component = _clamp01(current_apr, 0.45)
    if not recent_results:
        return prior_mastery, "routing_session_prior"
    recent_accuracy = sum(1 for x in recent_results if bool(x)) / float(len(recent_results))
    consecutive_correct = 0
    for result in reversed(recent_results):
        if bool(result):
            consecutive_correct += 1
        else:
            break
    streak_bonus = min(0.12, 0.03 * float(consecutive_correct))
    blended = 0.70 * recent_accuracy + 0.30 * apr_component + streak_bonus
    return _clamp01(blended, prior_mastery), "recent_results_blend"


def _pick_demo_entry(
    entries: list[CatalogEntry],
    *,
    selected_agent_skill: str | None,
    family_id: str,
) -> CatalogEntry | None:
    family_key = str(family_id or "").strip()
    if not family_key:
        return None
    for entry in entries:
        if entry.family_id != family_key:
            continue
        entry_agent_skill = resolve_agent_skill(entry.skill_id)
        if selected_agent_skill and entry_agent_skill != selected_agent_skill:
            continue
        return entry
    return None


def _load_question_from_skill_module(skill_id: str) -> dict[str, Any] | None:
    try:
        module = importlib.import_module(f"skills.{skill_id}")
    except Exception as exc:
        POLICY_LOGGER.info(
            "[adaptive_qgen] layer=skill_module_import skill_id=%s error=%s",
            skill_id,
            str(exc),
        )
        return None

    generator = getattr(module, "generate", None)
    if not callable(generator):
        POLICY_LOGGER.info(
            "[adaptive_qgen] layer=skill_module skill_id=%s error=generate_not_callable",
            skill_id,
        )
        return None

    try:
        payload = generator(level=1)
    except TypeError:
        try:
            payload = generator()
        except Exception as exc:
            POLICY_LOGGER.info(
                "[adaptive_qgen] layer=skill_module_generate skill_id=%s error=%s",
                skill_id,
                str(exc),
            )
            return None
    except Exception as exc:
        POLICY_LOGGER.info(
            "[adaptive_qgen] layer=skill_module_generate skill_id=%s error=%s",
            skill_id,
            str(exc),
        )
        return None

    return payload if isinstance(payload, dict) else None


def _load_question_from_script_path(script_path: str) -> dict[str, Any] | None:
    candidate = Path(script_path)
    if not candidate.is_absolute():
        candidate = PROJECT_ROOT / candidate
    if not candidate.exists():
        POLICY_LOGGER.info(
            "[adaptive_qgen] layer=manifest_script_path script_path=%s error=path_not_found",
            str(candidate),
        )
        return None

    try:
        spec = importlib.util.spec_from_file_location(f"adaptive_skill_{candidate.stem}", candidate)
        if not spec or not spec.loader:
            POLICY_LOGGER.info(
                "[adaptive_qgen] layer=manifest_script_load script_path=%s error=invalid_spec",
                str(candidate),
            )
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        generator = getattr(module, "generate", None)
        if not callable(generator):
            POLICY_LOGGER.info(
                "[adaptive_qgen] layer=manifest_script script_path=%s error=generate_not_callable",
                str(candidate),
            )
            return None
        payload = generator(level=1)
        return payload if isinstance(payload, dict) else None
    except Exception as exc:
        POLICY_LOGGER.info(
            "[adaptive_qgen] layer=manifest_script_generate script_path=%s error=%s",
            str(candidate),
            str(exc),
        )
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
    question_text = f"請作答：{entry.family_id} {entry.family_name}"
    hint = "、".join(entry.subskill_nodes[:3])
    answer = f"{entry.family_id}_fallback"
    return {
        "question": question_text,
        "question_text": question_text,
        "latex": question_text,
        "answer": answer,
        "correct_answer": answer,
        "context_string": f"提示子技能：{hint}",
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
        "explanation": payload.get("explanation") or payload.get("solution") or "",
        "solution": payload.get("solution") or payload.get("explanation") or "",
        "context_string": payload.get("context_string", ""),
        "image_base64": payload.get("image_base64", ""),
        "visual_aids": payload.get("visual_aids", []),
        "family_id": entry.family_id,
        "family": entry.family_id,
        "family_name": entry.family_name,
        "skill_id": entry.skill_id,
        "subskill_nodes": list(entry.subskill_nodes),
        "source": source,
    }


def _question_preview(raw: dict[str, Any] | None, *, max_len: int = 90) -> str:
    if not isinstance(raw, dict):
        return ""
    text = str(raw.get("question_text") or raw.get("question") or "").strip()
    if len(text) <= max_len:
        return text
    return text[:max_len] + "..."


def _generate_question_payload(entry: CatalogEntry, *, selected_subskill: str | None = None) -> dict[str, Any]:
    micro_status = "not_run"
    micro_generator_exists = has_micro_generator(entry)
    script_bridge_status = "not_run"
    script_bridge_resolve_source = "not_run"
    resolved_module_path = ""
    resolved_function_name = ""
    payload_schema_valid = False
    skill_module_status = "not_run"
    placeholder_used = False
    final_source = "catalog_fallback"
    resolved_generator_key = f"{entry.skill_id}:{entry.family_id}:{entry.family_name}"
    fallback_reason = "none"

    question: dict[str, Any] | None = None
    try:
        question = generate_micro_question(entry)
        if question and not _looks_like_stub_question(question):
            micro_status = "success"
            final_source = "micro_generator"
            POLICY_LOGGER.info(
                "[adaptive_qgen] skill_id=%s family_id=%s selected_subskill=%s family_name=%s resolved_generator_key=%s micro_generator_exists=%s micro_generator=%s resolved_module_path=%s resolved_function_name=%s generator_call_success=%s payload_schema_valid=%s skill_module=%s placeholder_used=%s final_source=%s fallback_reason=%s",
                entry.skill_id,
                entry.family_id,
                str(selected_subskill or ""),
                entry.family_name,
                resolved_generator_key,
                micro_generator_exists,
                micro_status,
                resolved_module_path,
                resolved_function_name,
                script_bridge_status,
                payload_schema_valid,
                skill_module_status,
                placeholder_used,
                final_source,
                fallback_reason,
            )
            return _normalize_question_payload(question, entry, final_source)
        micro_status = "fail"
        placeholder_used = bool(question)
        fallback_reason = "micro_generator_returned_stub_or_empty"
    except Exception as exc:
        micro_status = f"fail:{str(exc)}"
        fallback_reason = "micro_generator_exception"

    script_result = call_adaptive_script(entry.skill_id, entry.family_id, level=1)
    resolved_module_path = str(script_result.get("resolved_module_path") or "")
    resolved_function_name = str(script_result.get("resolved_function_name") or "")
    script_bridge_resolve_source = str(script_result.get("resolve_source") or "")
    payload_schema_valid = bool(script_result.get("payload_schema_valid", False))
    bridge_success = bool(script_result.get("generator_call_success", False))
    if bridge_success:
        question = script_result.get("payload")
        if isinstance(question, dict) and not _looks_like_stub_question(question):
            script_bridge_status = "success"
            final_source = "script_dispatch"
            POLICY_LOGGER.info(
                "[adaptive_qgen] skill_id=%s family_id=%s selected_subskill=%s family_name=%s resolved_generator_key=%s micro_generator_exists=%s micro_generator=%s resolved_module_path=%s resolved_function_name=%s generator_call_success=%s payload_schema_valid=%s skill_module=%s placeholder_used=%s final_source=%s fallback_reason=%s",
                entry.skill_id,
                entry.family_id,
                str(selected_subskill or ""),
                entry.family_name,
                resolved_generator_key,
                micro_generator_exists,
                micro_status,
                resolved_module_path,
                resolved_function_name,
                script_bridge_status,
                payload_schema_valid,
                skill_module_status,
                placeholder_used,
                final_source,
                fallback_reason,
            )
            return _normalize_question_payload(question, entry, final_source)
        script_bridge_status = "fail"
        placeholder_used = placeholder_used or bool(question)
        fallback_reason = "script_dispatch_placeholder_or_invalid_payload"
    else:
        script_bridge_status = f"fail:{script_result.get('error') or 'unknown'}"
        fallback_reason = "script_dispatch_error"

    try:
        question = _load_question_from_skill_module(entry.skill_id)
        if question and not _looks_like_stub_question(question):
            skill_module_status = "success"
            final_source = "skill_module"
            POLICY_LOGGER.info(
                "[adaptive_qgen] skill_id=%s family_id=%s selected_subskill=%s family_name=%s resolved_generator_key=%s micro_generator_exists=%s micro_generator=%s resolved_module_path=%s resolved_function_name=%s generator_call_success=%s payload_schema_valid=%s skill_module=%s placeholder_used=%s final_source=%s fallback_reason=%s",
                entry.skill_id,
                entry.family_id,
                str(selected_subskill or ""),
                entry.family_name,
                resolved_generator_key,
                micro_generator_exists,
                micro_status,
                resolved_module_path,
                resolved_function_name,
                script_bridge_status,
                payload_schema_valid,
                skill_module_status,
                placeholder_used,
                final_source,
                fallback_reason,
            )
            return _normalize_question_payload(question, entry, final_source)
        skill_module_status = "fail"
        placeholder_used = placeholder_used or bool(question)
        fallback_reason = "skill_module_returned_stub_or_empty"
    except Exception as exc:
        skill_module_status = f"fail:{str(exc)}"
        fallback_reason = "skill_module_exception"

    POLICY_LOGGER.info(
        "[adaptive_qgen] skill_id=%s family_id=%s selected_subskill=%s family_name=%s resolved_generator_key=%s micro_generator_exists=%s micro_generator=%s resolved_module_path=%s resolved_function_name=%s generator_call_success=%s payload_schema_valid=%s skill_module=%s placeholder_used=%s final_source=%s fallback_reason=%s",
        entry.skill_id,
        entry.family_id,
        str(selected_subskill or ""),
        entry.family_name,
        resolved_generator_key,
        micro_generator_exists,
        micro_status,
        resolved_module_path,
        resolved_function_name,
        script_bridge_status,
        payload_schema_valid,
        skill_module_status,
        True,
        "catalog_fallback",
        fallback_reason,
    )
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
        "add_sub": "加減運算",
        "mul_div": "乘除運算",
        "mixed_ops": "混合運算",
        "absolute_value": "絕對值",
        "parentheses": "括號處理",
        "divide_terms": "逐項相除",
        "conjugate_rationalize": "共軛有理化",
    }
    labels = [label_map.get(node, node.replace("_", " ")) for node in nodes]
    chips = "".join(f"<li>{label}</li>" for label in labels)
    focus = "、".join(labels[:2]) if labels else "核心子技能"
    return (
        "<div class='adaptive-hint'>"
        f"<p><strong>作答提示：</strong>先聚焦 {focus}，再逐步運算。</p>"
        "<p>先確認符號與括號範圍，再處理乘除與加減順序，可降低失誤率。</p>"
        f"<ul>{chips}</ul>"
        "<p>若仍不穩定，建議先回到對應基礎子技能練習再回主線。</p>"
        "</div>"
    )


def _normalize_mode(mode: Any) -> str:
    raw = str(mode or "").strip().lower()
    if raw in {"assessment", "teaching"}:
        return raw
    return "teaching"


def _sequence_for_mode(textbook_cfg: dict[str, Any] | None, mode: str) -> list[str]:
    if not isinstance(textbook_cfg, dict) or not textbook_cfg:
        return []
    normalized_mode = _normalize_mode(mode)
    if normalized_mode == "assessment":
        seq = textbook_cfg.get("assessment_sequence") or []
        if isinstance(seq, list):
            out = [str(x).strip() for x in seq if str(x).strip()]
            if out:
                return out
    main = textbook_cfg.get("mainline_sequence") or textbook_cfg.get("demo_mainline_sequence") or []
    if not isinstance(main, list):
        return []
    return [str(x).strip() for x in main if str(x).strip()]


def _family_performance(
    history_rows: list[AdaptiveLearningLog],
    *,
    current_family_id: str,
    last_is_correct: bool | None,
) -> dict[str, dict[str, int]]:
    perf: dict[str, dict[str, int]] = {}
    for row in history_rows:
        fid = _normalize_family_id(row.target_family_id)
        if not fid:
            continue
        slot = perf.setdefault(fid, {"attempts": 0, "correct": 0})
        slot["attempts"] += 1
        if bool(row.is_correct):
            slot["correct"] += 1
    if last_is_correct is not None and current_family_id:
        slot = perf.setdefault(current_family_id, {"attempts": 0, "correct": 0})
        slot["attempts"] += 1
        if bool(last_is_correct):
            slot["correct"] += 1
    return perf


def _evaluate_unit_completion(
    *,
    mode: str,
    system_skill_id: str,
    textbook_cfg: dict[str, Any] | None,
    history_rows: list[AdaptiveLearningLog],
    current_family_id: str,
    last_is_correct: bool | None,
    current_apr: float,
    answered_steps: int,
) -> dict[str, Any]:
    normalized_mode = _normalize_mode(mode)
    if not textbook_cfg:
        legacy_completed = bool(
            answered_steps >= MAX_DIAGNOSIS_STEPS
            or (answered_steps >= MIN_STEPS_BEFORE_EARLY_PASS and current_apr >= TARGET_APR)
        )
        return {
            "unit_completed": legacy_completed,
            "completion_reason": "legacy_default",
            "required_core_families": [],
            "covered_core_families": [],
            "passed_core_families": [],
            "minimum_covered_core_families": 0,
            "minimum_passed_core_families": 0,
            "require_integrative_family_pass": False,
            "integrative_family_id": "",
            "integrative_family_passed": False,
            "answered_steps": int(answered_steps),
            "mode": normalized_mode,
            "family_performance": _family_performance(
                history_rows,
                current_family_id=current_family_id,
                last_is_correct=last_is_correct,
            ),
            "local_remediation_completed": False,
        }

    completion_gate = get_completion_gate(system_skill_id) or dict(textbook_cfg.get("completion_gate") or {})
    mode_gate = completion_gate.get(normalized_mode, {}) if isinstance(completion_gate, dict) else {}
    if not isinstance(mode_gate, dict):
        mode_gate = {}
    required_core = [
        str(x).strip()
        for x in (mode_gate.get("required_core_families") or completion_gate.get("required_core_families") or [])
        if str(x).strip()
    ]
    if not required_core:
        required_core = [
            str(x).strip()
            for x in (textbook_cfg.get("mainline_sequence") or textbook_cfg.get("demo_mainline_sequence") or [])
            if str(x).strip()
        ]
    integrative_family_id = str(completion_gate.get("integrative_family_id") or "F11").strip()
    if normalized_mode == "assessment":
        default_min_cover = min(2, len(required_core)) if required_core else 1
        default_min_pass = min(2, len(required_core)) if required_core else 1
        default_require_integrative = False
    else:
        default_min_cover = len(required_core)
        default_min_pass = max(1, len(required_core) - 1) if required_core else 1
        default_require_integrative = True
    min_covered = int(mode_gate.get("minimum_covered_core_families", default_min_cover) or default_min_cover)
    min_passed = int(mode_gate.get("minimum_passed_core_families", default_min_pass) or default_min_pass)
    require_integrative = bool(mode_gate.get("require_integrative_family_pass", default_require_integrative))

    family_perf = _family_performance(
        history_rows,
        current_family_id=current_family_id,
        last_is_correct=last_is_correct,
    )
    covered_core = [fid for fid in required_core if int((family_perf.get(fid) or {}).get("attempts", 0)) > 0]
    passed_core = [fid for fid in required_core if int((family_perf.get(fid) or {}).get("correct", 0)) > 0]
    integrative_passed = int((family_perf.get(integrative_family_id) or {}).get("correct", 0)) > 0 if integrative_family_id else False

    coverage_ok = len(covered_core) >= max(1, min_covered)
    mastery_ok = len(passed_core) >= max(1, min_passed)
    integrative_ok = (not require_integrative) or integrative_passed
    unit_completed = bool(coverage_ok and mastery_ok and integrative_ok)
    if unit_completed:
        completion_reason = "unit_completion_gate_passed"
    elif not coverage_ok:
        completion_reason = "unit_completion_waiting_core_coverage"
    elif not mastery_ok:
        completion_reason = "unit_completion_waiting_core_mastery"
    else:
        completion_reason = "unit_completion_waiting_integrative_family"

    return {
        "unit_completed": unit_completed,
        "completion_reason": completion_reason,
        "required_core_families": required_core,
        "covered_core_families": covered_core,
        "passed_core_families": passed_core,
        "minimum_covered_core_families": min_covered,
        "minimum_passed_core_families": min_passed,
        "require_integrative_family_pass": require_integrative,
        "integrative_family_id": integrative_family_id,
        "integrative_family_passed": integrative_passed,
        "answered_steps": int(answered_steps),
        "mode": normalized_mode,
        "family_performance": family_perf,
        "local_remediation_completed": False,
    }


def _build_summary(
    *,
    answered_steps: int,
    current_apr: float,
    frustration_index: int,
    visited_family_ids: list[str],
    mode: str = "teaching",
    system_skill_id: str = "",
    unit_completed: bool = False,
    local_remediation_completed: bool = False,
    completion_reason: str = "",
    completion_stats: dict[str, Any] | None = None,
) -> dict[str, Any]:
    unique_families = list(dict.fromkeys(visited_family_ids))
    normalized_mode = _normalize_mode(mode)
    passed = bool(unit_completed)
    stats = dict(completion_stats or {})
    standardized_score: float | None = None
    if (
        normalized_mode == "assessment"
        and str(system_skill_id).strip() == "jh_?詨飛2銝FourArithmeticOperationsOfPolynomial"
    ):
        family_perf = stats.get("family_performance") if isinstance(stats, dict) else None
        if not isinstance(family_perf, dict):
            family_perf = {}
        mastery_values: list[float] = []
        for family_id in ASSESSMENT_POLY_STANDARDIZED_CORE_FAMILIES:
            slot = family_perf.get(family_id) if isinstance(family_perf.get(family_id), dict) else {}
            attempts = int(slot.get("attempts", 0) or 0)
            correct = int(slot.get("correct", 0) or 0)
            mastery = 0.0
            if attempts > 0:
                mastery = max(0.0, min(1.0, float(correct) / float(attempts)))
            mastery_values.append(mastery)
        if mastery_values:
            standardized_score = round((sum(mastery_values) / float(len(mastery_values))) * 100.0, 1)
    if passed:
        title = "本單元診斷完成"
        message = "你已完成本單元的核心題型檢核，整體掌握度表現穩定。"
        next_action = "可進入下一個單元，或回頭加強尚未達到滿分的題型。"
    elif local_remediation_completed:
        title = "補救完成，已返回主線"
        message = "你已完成這段補救練習，並回到主線繼續作答。"
        next_action = "建議繼續完成本單元診斷，確認補強後是否穩定掌握。"
    else:
        title = "本次診斷已完成，請先看補強建議。"
        message = "系統已根據你的作答表現整理出目前的學習卡點與掌握情況。"
        next_action = "建議先補強診斷書中的弱項，再回來完成主線題型。"

    return {
        "passed": passed,
        "title": title,
        "message": message,
        "next_action": next_action,
        "mode": normalized_mode,
        "unit_completed": bool(unit_completed),
        "local_remediation_completed": bool(local_remediation_completed),
        "completion_reason": str(completion_reason or ""),
        "completion_stats": stats,
        "answered_steps": answered_steps,
        "final_apr": round(current_apr, 4),
        "frustration_index": frustration_index,
        "visited_families": unique_families,
        "standardized_score": standardized_score,
        "standardized_score_percent": standardized_score,
    }


def _infer_skill_type(skill_id: str) -> str:
    text = str(skill_id or "")
    if "Polynomial" in text:
        return "polynomial"
    if "Radical" in text:
        return "radical"
    if "Fraction" in text or "Numbers" in text:
        return "fraction"
    if "Integer" in text or "Integers" in text:
        return "integer"
    return "generic"


def _build_generic_family_results(
    *,
    skill_type: str,
    family_perf: dict[str, Any],
    family_name_map: dict[str, str],
    preferred_order: list[str] | None = None,
) -> list[dict[str, Any]]:
    ordered: list[str] = []
    seen: set[str] = set()
    for family_id in (preferred_order or []):
        fid = str(family_id or "").strip()
        if fid and fid not in seen:
            seen.add(fid)
            ordered.append(fid)
    for family_id in family_perf.keys():
        fid = str(family_id or "").strip()
        if fid and fid not in seen:
            seen.add(fid)
            ordered.append(fid)

    out: list[dict[str, Any]] = []
    for family_id in ordered:
        slot = family_perf.get(family_id) if isinstance(family_perf.get(family_id), dict) else {}
        attempts = int(slot.get("attempts", 0) or 0)
        correct = int(slot.get("correct", 0) or 0)
        accuracy = max(0.0, min(1.0, (float(correct) / float(attempts)) if attempts > 0 else 0.0))
        if accuracy >= 0.7:
            status = "mastered"
        elif accuracy < 0.4:
            status = "weak"
        else:
            status = "incomplete"
        out.append(
            {
                "family": family_id,
                "family_id": family_id,
                "family_name": family_name_map.get(family_id) or family_id,
                "label_zh": get_family_diagnostic_info(skill_type, family_id).get("label_zh") or family_name_map.get(family_id) or family_id,
                "accuracy": round(accuracy, 4),
                "attempts": attempts,
                "mastery": round(accuracy, 4),
                "mastery_percent": round(accuracy * 100.0, 1),
                "status": status,
                "visited": bool(attempts > 0),
                "completed": bool(correct > 0),
            }
        )
    return out


def _detect_breakpoint(
    *,
    family_results: list[dict[str, Any]],
    preferred_family: str = "",
    fallback_reason: str = "low_accuracy",
    breakpoint_subskill: str = "",
    family_subskills_map: dict[str, list[str]] | None = None,
) -> dict[str, Any]:
    family_subskills_map = dict(family_subskills_map or {})
    preferred = str(preferred_family or "").strip()
    picked: dict[str, Any] | None = None

    if preferred:
        for row in family_results:
            if str(row.get("family_id") or "").strip() == preferred:
                picked = row
                break
    if picked is None:
        for row in family_results:
            if str(row.get("status") or "") == "weak" and int(row.get("attempts", 0) or 0) > 0:
                picked = row
                break
    if picked is None:
        for row in family_results:
            if str(row.get("status") or "") == "weak":
                picked = row
                break
    if picked is None:
        return {}

    family_id = str(picked.get("family_id") or "").strip()
    return {
        "family": family_id,
        "family_id": family_id,
        "label_zh": picked.get("label_zh") or family_id,
        "reason": str(fallback_reason or "low_accuracy"),
        "accuracy": float(picked.get("accuracy", 0.0) or 0.0),
        "attempts": int(picked.get("attempts", 0) or 0),
        "related_subskills": [x for x in [breakpoint_subskill] if str(x).strip()] or list(
            family_subskills_map.get(family_id) or []
        )[:3],
    }


def _skill_specific_recommendations(
    *,
    skill_type: str,
    breakpoint_obj: dict[str, Any],
    remediation_trace_ids: list[str],
) -> list[str]:
    if remediation_trace_ids:
        return [f"建議先補強：{fid}" for fid in remediation_trace_ids[:3]]

    if not breakpoint_obj:
        return ["建議回顧基礎概念"]

    family_id = str(breakpoint_obj.get("family") or breakpoint_obj.get("family_id") or "").strip()
    if skill_type == "polynomial":
        if family_id in {"F11", "F12"}:
            return [
                "建議先補強整數乘方（I9 / I10）",
                "再練習乘方法則與分配律",
                "最後回到多項式運算",
            ]
        return ["建議先補強目前卡住的 family，再回主線"]
    if skill_type == "fraction":
        return [
            "建議先練習約分與通分",
            "加強分數乘除法",
            "再回到進階分數運算",
        ]
    if skill_type == "integer":
        return [
            "建議加強正負號處理",
            "熟練四則運算順序",
            "避免符號錯誤",
        ]
    return ["建議回顧基礎概念"]


def _build_learning_trajectory(timeline: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    rows = _normalize_routing_timeline(timeline)
    out: list[dict[str, Any]] = []
    for row in rows[-10:]:
        action_raw = str(row.get("ppo_action") or "").strip().lower()
        if action_raw == "remediate":
            action = "remediate"
        elif action_raw == "return":
            action = "return"
        else:
            action = "stay"
        family = str(row.get("current_family") or row.get("selected_family_id") or "").strip()
        out.append(
            {
                "family": family or "-",
                "skill": str(row.get("current_skill") or row.get("selected_agent_skill") or "").strip(),
                "is_correct": bool(row.get("is_correct")) if row.get("is_correct") is not None else False,
                "action": action,
                "timestamp": float(row.get("timestamp", 0.0) or 0.0),
            }
        )
    return out


def _build_diagnostic_report(
    *,
    system_skill_id: str,
    unit_name: str,
    mode: str,
    summary: dict[str, Any],
    completion_stats: dict[str, Any] | None,
    family_name_by_id: dict[str, str] | None = None,
    family_subskills_by_id: dict[str, list[str]] | None = None,
    breakpoint_family_id: str = "",
    breakpoint_subskill: str = "",
    breakpoint_concept: str = "",
    remediation_trace: list[str] | None = None,
    routing_timeline: list[dict[str, Any]] | None = None,
) -> dict[str, Any] | None:
    normalized_mode = _normalize_mode(mode)
    if normalized_mode != "assessment":
        return None

    family_name_map = dict(family_name_by_id or {})
    family_subskills_map = dict(family_subskills_by_id or {})
    stats = dict(completion_stats or {})
    family_perf = stats.get("family_performance") if isinstance(stats.get("family_performance"), dict) else {}
    remediation_trace_ids = [str(x).strip() for x in (remediation_trace or []) if str(x).strip()]
    skill_type = _infer_skill_type(system_skill_id)

    preferred_order = [
        str(x).strip()
        for x in (stats.get("required_core_families") or [])
        if str(x).strip()
    ]
    if not preferred_order and skill_type == "polynomial":
        preferred_order = list(ASSESSMENT_POLY_STANDARDIZED_CORE_FAMILIES)

    family_results = _build_generic_family_results(
        skill_type=skill_type,
        family_perf=family_perf,
        family_name_map=family_name_map,
        preferred_order=preferred_order,
    )
    for row in family_results:
        family_id = str(row.get("family_id") or "").strip()
        info = get_family_diagnostic_info(skill_type, family_id)
        row["label_zh"] = info.get("label_zh") or row.get("label_zh") or family_id
        row["description_zh"] = info.get("description_zh") or ""
        row["common_error_zh"] = info.get("common_error_zh") or ""
        row["prerequisite_ids"] = list(info.get("prerequisite_ids") or [])
        row["prerequisite_labels_zh"] = list(info.get("prerequisite_labels_zh") or [])
        row["subskills"] = list(info.get("subskills") or row.get("subskills") or [])
        row["subskills_zh"] = list(info.get("subskills_zh") or [])

    stop_reason = str(summary.get("assessment_stop_reason") or stats.get("assessment_stop_reason") or "").strip()
    preferred_breakpoint = str(breakpoint_family_id or "").strip() or str(summary.get("display_family") or "").strip()
    breakpoint_obj = _detect_breakpoint(
        family_results=family_results,
        preferred_family=preferred_breakpoint,
        fallback_reason=breakpoint_concept or "low_accuracy",
        breakpoint_subskill=breakpoint_subskill,
        family_subskills_map=family_subskills_map,
    )
    bp_family = str(breakpoint_obj.get("family") or "").strip()
    if bp_family and breakpoint_obj:
        bp_info = get_family_diagnostic_info(skill_type, bp_family)
        breakpoint_obj["label_zh"] = bp_info.get("label_zh") or breakpoint_obj.get("label_zh") or bp_family
        breakpoint_obj["description_zh"] = bp_info.get("description_zh") or ""
        breakpoint_obj["common_error_zh"] = bp_info.get("common_error_zh") or breakpoint_obj.get("reason") or ""
        breakpoint_obj["prerequisite_ids"] = list(bp_info.get("prerequisite_ids") or [])
        breakpoint_obj["prerequisite_labels_zh"] = list(bp_info.get("prerequisite_labels_zh") or [])
        breakpoint_obj["subskills_zh"] = list(bp_info.get("subskills_zh") or [])
        if not breakpoint_obj.get("related_subskills"):
            breakpoint_obj["related_subskills"] = list(bp_info.get("subskills") or [])[:3]

    # Upgrade weak status to breakpoint for the chosen row.
    for row in family_results:
        if bp_family and str(row.get("family_id") or "").strip() == bp_family and float(row.get("accuracy", 0.0) or 0.0) < 0.4:
            row["status"] = "breakpoint"

    strengths = [str(row.get("family_id")) for row in family_results if str(row.get("status")) == "mastered"]
    weaknesses = [str(row.get("family_id")) for row in family_results if str(row.get("status")) != "mastered"]
    strengths_zh = [str(row.get("label_zh") or row.get("family_id")) for row in family_results if str(row.get("status")) == "mastered"]
    weaknesses_zh = [str(row.get("label_zh") or row.get("family_id")) for row in family_results if str(row.get("status")) != "mastered"]
    completed_families = list(strengths)
    failed_family = bp_family

    final_apr = float(summary.get("final_apr", 0.0) or 0.0)
    apr_mastery = round(max(0.0, min(1.0, final_apr)), 4)
    apr_percent = round(apr_mastery * 100.0, 1)
    standardized_score_raw = summary.get("standardized_score")
    if standardized_score_raw is None:
        standardized_score = apr_percent
    else:
        try:
            standardized_score = round(float(standardized_score_raw), 1)
        except Exception:
            standardized_score = apr_percent
    score = int(round(max(0.0, min(100.0, standardized_score))))

    if standardized_score >= 85.0:
        overall_level = "high"
    elif standardized_score >= 60.0:
        overall_level = "medium"
    else:
        overall_level = "needs_improvement"
    completion_status = "assessment_completed"
    if stop_reason == "stable_breakpoint_detected":
        completion_status = "stable_breakpoint_detected"
    elif stop_reason == "completed_all_core_families":
        completion_status = "completed_all_core_families"

    recommended_step_texts = _skill_specific_recommendations(
        skill_type=skill_type,
        breakpoint_obj=breakpoint_obj,
        remediation_trace_ids=remediation_trace_ids,
    )
    recommended_next_steps: list[dict[str, Any]] = []
    for idx, text in enumerate(recommended_step_texts, start=1):
        target_id = ""
        m = re.search(r"(F\d+|I\d+)", text)
        if m:
            target_id = m.group(1)
        target_type = "family" if target_id.startswith("F") else ("bridge_family" if target_id.startswith("I") else "skill")
        recommended_next_steps.append(
            {
                "priority": idx,
                "target_type": target_type,
                "target_id": target_id,
                "label_zh": (get_family_diagnostic_info(skill_type, target_id).get("label_zh") if target_id else "") or target_id or "摮貊?頝臬?",
                "reason": text,
            }
        )

    return {
        "skill_type": skill_type,
        "score": score,
        "apr_mastery": apr_mastery,
        "completed_families": completed_families,
        "failed_family": failed_family,
        "family_results": family_results,
        "breakpoint": breakpoint_obj,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "strengths_zh": strengths_zh,
        "weaknesses_zh": weaknesses_zh,
        "recommended_next_steps": recommended_next_steps,
        "trajectory": _build_learning_trajectory(routing_timeline),
        # backward-compatible fields
        "system_skill_id": system_skill_id,
        "unit_name": unit_name,
        "mode": normalized_mode,
        "overall": {
            "standardized_score": standardized_score,
            "apr_percent": apr_percent,
            "completion_status": completion_status,
            "assessment_stop_reason": stop_reason,
            "overall_level": overall_level,
            "overall_summary": f"score={score}/100, apr={apr_percent:.1f}%, level={overall_level}",
        },
        "breakpoints": [breakpoint_obj] if breakpoint_obj else [],
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


def _build_display_state(
    *,
    is_completed: bool,
    post_mode: str,
    return_to_mainline: bool,
    return_triggered_final: bool,
    selected_skill: str | None,
    selected_family: str | None,
    selected_subskill: str | None,
    scenario_stage: str | None,
) -> dict[str, Any]:
    normalized_post_mode = str(post_mode or "").strip().lower() or "mainline"
    if is_completed:
        display_mode = "completed"
    elif bool(return_to_mainline) or bool(return_triggered_final):
        display_mode = "mainline"
    elif normalized_post_mode == "remediation":
        display_mode = "remediation"
    else:
        display_mode = "mainline"
    return {
        "display_mode": display_mode,
        "display_family": _normalize_family_id(selected_family),
        "display_subskill": str(selected_subskill or "").strip(),
        "display_skill": str(selected_skill or "").strip(),
        "is_completed": bool(is_completed),
        "return_to_mainline": bool(return_to_mainline),
        "scenario_stage": str(scenario_stage or ""),
    }


def _derive_milestone_state(
    *,
    mode: str,
    unit_completed: bool,
    local_remediation_completed: bool,
    return_to_mainline: bool,
    return_triggered_final: bool,
    post_mode: str,
    scenario_stage: str | None,
    assessment_completed: bool = False,
    assessment_stop_reason: str = "",
) -> str:
    if _normalize_mode(mode) == "assessment":
        if bool(assessment_completed):
            if str(assessment_stop_reason or "") == "stable_breakpoint_detected":
                return "assessment_breakpoint_detected"
            return "assessment_completed"
        return "assessment_in_progress"
    if bool(unit_completed):
        return "unit_completed"
    if (
        bool(local_remediation_completed)
        or bool(return_to_mainline)
        or bool(return_triggered_final)
        or str(scenario_stage or "").strip() == "returned_to_origin_family"
    ):
        return "remediation_returned_success"
    if str(post_mode or "").strip().lower() == "remediation":
        return "remediation_in_progress"
    return "mainline_progress"


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
    rescue_recommended: bool = False,
    cross_skill_trigger: bool = False,
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

    missed_remediation_penalty = 0.0
    if (
        bool(rescue_recommended)
        and bool(cross_skill_trigger)
        and str(route_action) == "stay"
        and is_correct is False
    ):
        missed_remediation_penalty = -0.3

    final_route_reward = (
        correctness_reward
        + recovery_reward
        + return_success_reward
        + stagnation_penalty
        + unnecessary_route_penalty
        + missed_remediation_penalty
    )

    return {
        "correctness_reward": float(correctness_reward),
        "recovery_reward": float(recovery_reward),
        "return_success_reward": float(return_success_reward),
        "stagnation_penalty": float(stagnation_penalty),
        "unnecessary_route_penalty": float(unnecessary_route_penalty),
        "missed_remediation_penalty": float(missed_remediation_penalty),
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

    routing_session = dict(payload.get("routing_state") or {})
    mode = _normalize_mode(payload.get("mode") or routing_session.get("mode"))
    print(f"[DEBUG] mode={mode}", flush=True)
    system_skill_id = str(payload.get("skill_id", "") or "").strip()
    entries = _apply_demo_safe_family_filter(
        _select_entries(payload),
        mode=mode,
        system_skill_id=system_skill_id,
    )
    if not entries:
        raise ValueError("No catalog entries available for the requested adaptive scope")
    family_name_by_id = {
        str(entry.family_id).strip(): str(entry.family_name).strip()
        for entry in entries
        if str(entry.family_id).strip()
    }
    family_subskills_by_id = {
        str(entry.family_id).strip(): [str(node).strip() for node in (entry.subskill_nodes or []) if str(node).strip()]
        for entry in entries
        if str(entry.family_id).strip()
    }
    unit_name = str(payload.get("unit_name") or (entries[0].skill_name if entries else "") or "").strip()
    allowed_demo_families_display = (
        sorted({str(entry.family_id) for entry in entries if str(entry.family_id).strip()})
        if ADAPTIVE_USE_FULL_CATALOG
        else sorted(DEMO_ALLOWED_FAMILY_IDS)
    )

    if not system_skill_id:
        system_skill_id = str(entries[0].skill_id if entries else "").strip()
    textbook_cfg = load_textbook_progression(system_skill_id)
    progression_mode = "textbook_sequence" if bool(textbook_cfg) else "default"

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
    routing_session["mode"] = mode
    demo_start_forced = bool(routing_session.get("demo_start_forced", False))
    demo_first_remediation_forced = bool(routing_session.get("demo_first_remediation_forced", False))
    demo_first_return_forced = bool(routing_session.get("demo_first_return_forced", False))
    scenario_stage = str(routing_session.get("scenario_stage") or "init")
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
    if mode == "assessment" and bool(routing_session.get("in_remediation", False)):
        routing_session["in_remediation"] = False
        routing_session["steps_taken"] = 0
        routing_session["recent_results"] = []
        routing_session["remediation_skill"] = ""
        routing_session["remediation_subskill"] = ""
        routing_session["bridge_remaining"] = 0
    return_ready, return_reason = should_return_from_remediation(routing_session)
    local_remediation_completed = bool(
        payload.get("return_to_mainline", False)
        or payload.get("has_returned_to_main", False)
    )
    completion_eval = _evaluate_unit_completion(
        mode=mode,
        system_skill_id=system_skill_id,
        textbook_cfg=textbook_cfg,
        history_rows=history_rows,
        current_family_id=_normalize_family_id(payload.get("last_family_id")),
        last_is_correct=last_is_correct,
        current_apr=current_apr,
        answered_steps=answered_steps,
    )
    completion_eval["local_remediation_completed"] = local_remediation_completed
    completion_eval.setdefault("assessment_completed", False)
    completion_eval.setdefault("assessment_stop_reason", "")
    completion_eval.setdefault("assessment_breakpoint_detected", False)
    if mode == "assessment" and bool(completion_eval.get("unit_completed", False)):
        completion_eval["assessment_completed"] = True
        completion_eval["assessment_stop_reason"] = "completed_all_core_families"
    should_finish = bool(last_is_correct is not None and completion_eval.get("unit_completed", False))

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

    mainline_sequence = _sequence_for_mode(textbook_cfg, mode)
    progression_rules = dict(textbook_cfg.get("progression_rules") or {}) if textbook_cfg else {}
    remediation_rules = dict(textbook_cfg.get("remediation_rules") or {}) if textbook_cfg else {}
    return_mastery_threshold = float(remediation_rules.get("return_mastery_threshold", 0.85) or 0.85)
    return_mastery_with_recent_correct_threshold = float(
        remediation_rules.get("return_mastery_with_recent_correct_threshold", 0.75) or 0.75
    )
    repeat_failure_threshold = int(progression_rules.get("remediation_trigger_after_consecutive_wrong", 2) or 2)
    current_family_for_progression = _normalize_family_id(payload.get("last_family_id"))
    textbook_level_index = (
        mainline_sequence.index(current_family_for_progression)
        if current_family_for_progression in mainline_sequence
        else 0
    )
    if textbook_cfg and mode == "assessment":
        if current_family_for_progression in mainline_sequence:
            current_index = mainline_sequence.index(current_family_for_progression)
            next_family_candidate = (
                str(mainline_sequence[current_index + 1])
                if current_index + 1 < len(mainline_sequence)
                else None
            )
            previous_family_candidate = (
                str(mainline_sequence[current_index - 1])
                if current_index > 0
                else None
            )
        else:
            next_family_candidate = (str(mainline_sequence[0]) if mainline_sequence else None)
            previous_family_candidate = None
    else:
        next_family_candidate = get_next_family(system_skill_id, current_family_for_progression) if textbook_cfg else None
        previous_family_candidate = get_previous_family(system_skill_id, current_family_for_progression) if textbook_cfg else None
    remediation_retrieval: dict[str, Any] = {}
    remediation_candidates: list[dict[str, Any]] = []
    remediation_candidate_labels: list[str] = []
    candidate_source = ""
    error_type_hint = str(payload.get("error_type") or payload.get("last_error_type") or "").strip().lower()
    question_text_hint = str(payload.get("last_question_text", "") or "")
    sign_distribution_signal = bool(
        textbook_cfg
        and last_is_correct is False
        and (
            "sign_distribution" in [str(x).strip() for x in (last_subskills or [])]
            or "sign" in error_type_hint
            or "negative" in error_type_hint
            or "-(" in question_text_hint
        )
    )
    prior_consecutive_wrong_on_family = _consecutive_wrong_on_family(history_rows, current_family_for_progression)
    consecutive_wrong_on_family = prior_consecutive_wrong_on_family + (1 if last_is_correct is False else 0)
    remediation_review_ready = bool(
        textbook_cfg
        and last_is_correct is False
        and (
            consecutive_wrong_on_family >= repeat_failure_threshold
            or fail_streak >= repeat_failure_threshold
            or frustration_index >= 2
            or sign_distribution_signal
        )
    )
    remediation_triggered_final = False
    return_rule_ready = False
    return_triggered_final = False
    remediation_mastery = 0.0
    recent_correct = False
    why_remediate_masked = ""
    allowed_agent_skills = list(SKILL_LABELS)
    if textbook_cfg:
        routing_session["return_mastery_threshold"] = return_mastery_threshold
        routing_session["return_mastery_with_recent_correct_threshold"] = return_mastery_with_recent_correct_threshold
    if system_skill_id == "jh_?詨飛1銝FourArithmeticOperationsOfIntegers":
        allowed_agent_skills = ["integer_arithmetic"]
    if not allowed_agent_skills:
        print(
            "[adaptive_phase1_policy][WARNING] allowed_agent_skills is empty; fallback to full SKILL_LABELS",
            flush=True,
        )
        allowed_agent_skills = list(SKILL_LABELS)
    allowed_agent_skills_before_filter = list(allowed_agent_skills)
    allowed_agent_skills_after_filter = list(allowed_agent_skills)
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
            completed_observability["selection_debug"]["demo_mode"] = ADAPTIVE_DEMO_SAFE_MODE
            completed_observability["selection_debug"]["full_catalog_mode"] = ADAPTIVE_USE_FULL_CATALOG
            completed_observability["selection_debug"]["allowed_demo_families"] = allowed_demo_families_display
            completed_observability["selection_debug"]["selected_family"] = _normalize_family_id(payload.get("last_family_id"))
            completed_observability["selection_debug"]["return_to_mainline"] = bool(payload.get("has_returned_to_main", False))
            completed_observability["selection_debug"]["scenario_stage"] = scenario_stage
            completed_observability["selection_debug"]["routing_summary"] = routing_summary
            completed_observability["selection_debug"]["routing_timeline"] = routing_timeline
            completed_observability["selection_debug"]["routing_timeline_summary"] = routing_timeline_summary
            completed_observability["selection_debug"]["mode"] = mode
            completed_observability["selection_debug"]["unit_completed"] = bool(completion_eval.get("unit_completed", False))
            completed_observability["selection_debug"]["local_remediation_completed"] = bool(completion_eval.get("local_remediation_completed", False))
            completed_observability["selection_debug"]["assessment_completed"] = bool(completion_eval.get("assessment_completed", False))
            completed_observability["selection_debug"]["assessment_stop_reason"] = str(completion_eval.get("assessment_stop_reason", ""))
            completed_observability["selection_debug"]["completion_reason"] = str(completion_eval.get("completion_reason", ""))
            completed_observability["selection_debug"]["completion_stats"] = completion_eval
            completed_observability["selection_debug"]["milestone_state"] = _derive_milestone_state(
                mode=mode,
                unit_completed=bool(completion_eval.get("unit_completed", False)),
                local_remediation_completed=bool(completion_eval.get("local_remediation_completed", False)),
                return_to_mainline=bool(payload.get("has_returned_to_main", False)),
                return_triggered_final=bool(payload.get("has_returned_to_main", False)),
                post_mode="mainline",
                scenario_stage=scenario_stage,
                assessment_completed=bool(completion_eval.get("assessment_completed", False)),
                assessment_stop_reason=str(completion_eval.get("assessment_stop_reason", "")),
            )
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
            mode=mode,
            system_skill_id=system_skill_id,
            unit_completed=bool(completion_eval.get("unit_completed", False)),
            local_remediation_completed=bool(completion_eval.get("local_remediation_completed", False)),
            completion_reason=str(completion_eval.get("completion_reason", "")),
            completion_stats=completion_eval,
        )
        completed_return_to_mainline = bool(
            payload.get("return_to_mainline", False)
            or payload.get("has_returned_to_main", False)
            or (completed_observability.get("selection_debug", {}) or {}).get("return_to_mainline", False)
        )
        completed_display_state = _build_display_state(
            is_completed=True,
            post_mode="mainline" if completed_return_to_mainline else "mainline",
            return_to_mainline=completed_return_to_mainline,
            return_triggered_final=completed_return_to_mainline,
            selected_skill=(
                completed_observability.get("selected_agent_skill")
                or resolve_agent_skill(system_skill_id)
                or "integer_arithmetic"
            ),
            selected_family=_normalize_family_id(payload.get("last_family_id")),
            selected_subskill=(
                completed_observability.get("selected_subskill")
                or (last_subskills[0] if last_subskills else "")
            ),
            scenario_stage=scenario_stage,
        )
        completed_milestone_state = _derive_milestone_state(
            mode=mode,
            unit_completed=bool(completion_eval.get("unit_completed", False)),
            local_remediation_completed=bool(completion_eval.get("local_remediation_completed", False)),
            return_to_mainline=completed_return_to_mainline,
            return_triggered_final=completed_return_to_mainline,
            post_mode="mainline",
            scenario_stage=scenario_stage,
            assessment_completed=bool(completion_eval.get("assessment_completed", False)),
            assessment_stop_reason=str(completion_eval.get("assessment_stop_reason", "")),
        )
        summary.update(
            {
                "display_mode": completed_display_state["display_mode"],
                "display_family": completed_display_state["display_family"],
                "display_subskill": completed_display_state["display_subskill"],
                "display_skill": completed_display_state["display_skill"],
                "is_completed": True,
                "return_to_mainline": completed_display_state["return_to_mainline"],
                "scenario_stage": completed_display_state["scenario_stage"],
                "current_mode": "mainline",
                "post_mode": "mainline",
                "learning_mode": "returned" if completed_return_to_mainline else "main",
                "mode": mode,
                "milestone_state": completed_milestone_state,
                "assessment_completed": bool(completion_eval.get("assessment_completed", False)),
                "assessment_stop_reason": str(completion_eval.get("assessment_stop_reason", "")),
            }
        )
        diagnostic_report = _build_diagnostic_report(
            system_skill_id=system_skill_id,
            unit_name=unit_name,
            mode=mode,
            summary=summary,
            completion_stats=completion_eval,
            family_name_by_id=family_name_by_id,
            family_subskills_by_id=family_subskills_by_id,
            remediation_trace=[
                str((item or {}).get("selected_family_id") or "").strip()
                for item in (routing_timeline or [])
                if isinstance(item, dict) and str((item or {}).get("selected_family_id") or "").strip()
            ],
            routing_timeline=routing_timeline,
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
            "diagnostic_report": diagnostic_report,
            "routing_state": routing_session,
            "routing_summary": routing_summary,
            "routing_timeline": routing_timeline,
            "routing_timeline_summary": routing_timeline_summary,
            "demo_mode": ADAPTIVE_DEMO_SAFE_MODE,
            "full_catalog_mode": ADAPTIVE_USE_FULL_CATALOG,
            "allowed_demo_families": allowed_demo_families_display,
            "scenario_stage": scenario_stage,
            "display_mode": completed_display_state["display_mode"],
            "display_family": completed_display_state["display_family"],
            "display_subskill": completed_display_state["display_subskill"],
            "display_skill": completed_display_state["display_skill"],
            "is_completed": completed_display_state["is_completed"],
            "unit_completed": bool(completion_eval.get("unit_completed", False)),
            "local_remediation_completed": bool(completion_eval.get("local_remediation_completed", False)),
            "completion_reason": str(completion_eval.get("completion_reason", "")),
            "completion_stats": completion_eval,
            "mode": mode,
            "milestone_state": completed_milestone_state,
            "assessment_completed": bool(completion_eval.get("assessment_completed", False)),
            "assessment_stop_reason": str(completion_eval.get("assessment_stop_reason", "")),
            "allowed_actions": [],
            "action_mask": {"stay": True, "remediate": False, "return": False} if mode == "assessment" else {},
            "return_to_mainline": completed_display_state["return_to_mainline"],
            **completed_observability,
        }

    last_family_id = _normalize_family_id(payload.get("last_family_id"))
    selection_mode = "legacy_fallback"
    selected_agent_skill: str | None = None
    selected_subskill: str | None = None
    policy_debug: dict[str, Any] = {"reason": "legacy_fallback_default"}
    fallback_reason: str | None = None
    demo_override_reason: str | None = None
    mapping_candidates: list[str] = []
    policy_model_loaded = False
    route_action: str | None = None
    route_action_idx: int | None = None
    route_decision_source: str = "not_run"
    just_returned_from_remediation = False
    current_mode = "mainline"
    post_mode = "mainline"
    assessment_breakpoint_detected = False

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
            current_family_id=last_family_id,
            question_text=str(payload.get("last_question_text", "")),
            student_answer=str(payload.get("last_user_answer", "") or payload.get("user_answer", "")),
            expected_answer=str(payload.get("last_expected_answer", "")),
            is_correct=last_is_correct,
            fail_streak=fail_streak,
            frustration=frustration_norm,
            same_skill_streak=agent_state.get("same_skill_streak", 0),
            routing_session=routing_session,
            prerequisite_candidates=remediation_candidates,
            unit_skill_id=system_skill_id,
            enable_choice_diagnosis=bool((not textbook_cfg) and remediation_review_ready),
        )
        if isinstance(diagnosis.get("routing_session"), dict):
            routing_session = dict(diagnosis.get("routing_session") or routing_session)
        cross_skill_trigger = bool(
            remediation_review_ready
            and compute_cross_skill_trigger(
            fail_streak=fail_streak,
            frustration=frustration_norm,
            same_skill_streak=int(agent_state.get("same_skill_streak", 0) or 0),
            diagnosis=diagnosis,
            current_skill=current_skill,
            )
        )
        routing_state = build_routing_state(
            agent_state=agent_state,
            diagnosis=diagnosis,
            current_skill=current_skill,
            current_subskill=current_subskill,
            routing_session=routing_session,
        )
        remediation_mastery_source = "none"
        if routing_session.get("in_remediation", False):
            rem_mastery, rem_mastery_source = _compute_remediation_mastery(
                routing_session=routing_session,
                current_apr=current_apr,
            )
            routing_session["remediation_mastery"] = float(rem_mastery)
            remediation_mastery_source = str(rem_mastery_source)
            if last_is_correct is not None:
                routing_session["last_result"] = bool(last_is_correct)
        remediation_mastery = float(routing_session.get("remediation_mastery", 0.0) or 0.0)
        recent_correct = bool(routing_session.get("last_result", False))
        if textbook_cfg and bool(routing_session.get("in_remediation", False)):
            ready_by_mastery = remediation_mastery >= return_mastery_threshold
            ready_by_recent = (
                remediation_mastery >= return_mastery_with_recent_correct_threshold
                and recent_correct
            )
            return_rule_ready = bool(ready_by_mastery or ready_by_recent)
            return_ready = return_rule_ready
            if ready_by_mastery:
                return_reason = "ready_by_mastery_threshold"
            elif ready_by_recent:
                return_reason = "ready_by_mastery_recent_correct_threshold"
            else:
                return_reason = "not_ready_by_return_guardrails"
        else:
            return_ready, return_reason = should_return_from_remediation(routing_session)
            return_rule_ready = bool(return_ready)
        in_remediation = bool(routing_session.get("in_remediation", False))
        pre_bridge_remaining = int(routing_session.get("bridge_remaining", 0) or 0)
        lock_min_steps = int(routing_session.get("lock_min_steps", 2) or 2)
        rem_steps = int(routing_session.get("steps_taken", 0) or 0)
        action_mask = build_action_mask(
            in_remediation=in_remediation,
            remediation_step_count=rem_steps,
            lock_min_steps=lock_min_steps,
            cross_skill_trigger=cross_skill_trigger,
            return_ready=return_ready,
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
        allowed_agent_skills_before_filter = list(allowed_agent_skills)
        allowed_agent_skills_after_filter = list(allowed_agent_skills)
        allowed_actions = [k for k, v in action_mask.items() if v]
        teaching_trigger_ready = bool(
            current_mode == "mainline"
            and remediation_review_ready
            and action_mask.get("remediate", False)
        )
        if mode == "assessment":
            assessment_breakpoint_detected = bool(teaching_trigger_ready)
            completion_eval["assessment_breakpoint_detected"] = assessment_breakpoint_detected
            if assessment_breakpoint_detected:
                completion_eval["assessment_completed"] = True
                completion_eval["assessment_stop_reason"] = "stable_breakpoint_detected"
                completion_eval["unit_completed"] = False
            action_mask = {"stay": True, "remediate": False, "return": False}
            allowed_actions = ["stay"]
            allowed_agent_skills = [current_skill]
            allowed_agent_skills_before_filter = list(allowed_agent_skills)
            allowed_agent_skills_after_filter = list(allowed_agent_skills)

        print(
            "[ROUTING] "
            f"current_skill={current_skill} current_subskill={current_subskill} "
            f"fail_streak={fail_streak} frustration={frustration_norm:.2f} "
        f"diag_error_concept={diagnosis.get('error_concept')} "
        f"diag_confidence={diagnosis.get('diagnosis_confidence')} "
        f"selected_prereq_skill={diagnosis.get('selected_prereq_skill') or diagnosis.get('suggested_prereq_skill')} "
        f"selected_prereq_subskill={diagnosis.get('selected_prereq_subskill') or diagnosis.get('suggested_prereq_subskill')} "
        f"diagnostic_choice={diagnosis.get('diagnostic_choice')} "
            f"qwen_classifier_choice={diagnosis.get('diagnostic_choice')} "
            f"diagnostic_confidence={diagnosis.get('diagnostic_confidence')} "
            f"evidence_score={diagnosis.get('evidence_score')} "
            f"resolved_runtime_subskill={diagnosis.get('selected_runtime_subskill')} "
            f"remediation_triggered={diagnosis.get('remediation_triggered')} "
            f"suggested_prereq_skill={diagnosis.get('suggested_prereq_skill')} "
            f"remediation_review_ready={remediation_review_ready} "
            f"sign_distribution_signal={sign_distribution_signal} "
        f"cross_skill_trigger={cross_skill_trigger} "
        f"allowed_agent_skills_before_filter={allowed_agent_skills_before_filter} "
        f"allowed_agent_skills_after_filter={allowed_agent_skills_after_filter} "
        f"allowed_agent_skills={allowed_agent_skills} "
        f"allowed_actions={allowed_actions} "
            f"findings_enabled={ENABLE_POLICY_FINDINGS}",
            flush=True,
        )

        if mode == "assessment" and assessment_breakpoint_detected:
            scenario_stage = "assessment_stable_breakpoint_detected"
            routing_session["scenario_stage"] = scenario_stage
            breakpoint_subskill = str(
                diagnosis.get("selected_prereq_subskill")
                or diagnosis.get("suggested_prereq_subskill")
                or current_subskill
                or ""
            ).strip()
            breakpoint_concept = str(diagnosis.get("error_concept") or "").strip()
            completion_eval["assessment_completed"] = True
            completion_eval["assessment_stop_reason"] = "stable_breakpoint_detected"
            summary = _build_summary(
                answered_steps=answered_steps,
                current_apr=current_apr,
                frustration_index=frustration_index,
                visited_family_ids=visited + [_normalize_family_id(payload.get("last_family_id"))],
                mode=mode,
                system_skill_id=system_skill_id,
                unit_completed=False,
                local_remediation_completed=False,
                completion_reason="stable_breakpoint_detected",
                completion_stats=completion_eval,
            )
            summary.update(
                {
                    "passed": False,
                    "mode": mode,
                    "assessment_completed": True,
                    "assessment_stop_reason": "stable_breakpoint_detected",
                    "breakpoint_family": current_family_for_progression or _normalize_family_id(payload.get("last_family_id")),
                    "breakpoint_subskill": breakpoint_subskill,
                    "breakpoint_concept": breakpoint_concept,
                    "learning_recommendation": "建議先補強卡點子技能，再回主線練習。",
                    "title": "學習健檢：已偵測到穩定卡點",
                    "message": "系統已完成評量並找到主要卡點，建議先進入教學練習補強後再回測。",
                    "next_action": "建議切換到 teaching 模式，先補強目前卡點再回主線。",
                    "milestone_state": "assessment_breakpoint_detected",
                    "display_mode": "completed",
                    "display_family": current_family_for_progression or _normalize_family_id(payload.get("last_family_id")),
                    "display_subskill": breakpoint_subskill,
                    "display_skill": current_skill,
                    "is_completed": True,
                    "unit_completed": False,
                    "local_remediation_completed": False,
                    "current_mode": "mainline",
                    "post_mode": "mainline",
                    "learning_mode": "main",
                }
            )
            diagnostic_report = _build_diagnostic_report(
                system_skill_id=system_skill_id,
                unit_name=unit_name,
                mode=mode,
                summary=summary,
                completion_stats=completion_eval,
                family_name_by_id=family_name_by_id,
                family_subskills_by_id=family_subskills_by_id,
                breakpoint_family_id=current_family_for_progression or _normalize_family_id(payload.get("last_family_id")),
                breakpoint_subskill=breakpoint_subskill,
                breakpoint_concept=breakpoint_concept,
                remediation_trace=[
                    str((item or {}).get("selected_family_id") or "").strip()
                    for item in (routing_timeline or [])
                    if isinstance(item, dict) and str((item or {}).get("selected_family_id") or "").strip()
                ],
                routing_timeline=routing_timeline,
            )
            return {
                "session_id": session_id,
                "step_number": requested_step,
                "current_apr": current_apr,
                "ppo_strategy": strategy,
                "frustration_index": frustration_index,
                "execution_latency": 0,
                "target_family_id": current_family_for_progression or _normalize_family_id(payload.get("last_family_id")),
                "target_subskills": last_subskills,
                "new_question_data": {},
                "completed": True,
                "summary": summary,
                "diagnostic_report": diagnostic_report,
                "routing_state": routing_session,
                "routing_summary": routing_summary,
                "routing_timeline": routing_timeline,
                "routing_timeline_summary": routing_timeline_summary,
                "mode": mode,
                "assessment_completed": True,
                "assessment_stop_reason": "stable_breakpoint_detected",
                "unit_completed": False,
                "local_remediation_completed": False,
                "milestone_state": "assessment_breakpoint_detected",
                "return_to_mainline": False,
                "scenario_stage": scenario_stage,
                "display_mode": "completed",
                "display_family": current_family_for_progression or _normalize_family_id(payload.get("last_family_id")),
                "display_subskill": breakpoint_subskill,
                "display_skill": current_skill,
                "is_completed": True,
                "remediation_review_ready": remediation_review_ready,
                "cross_skill_trigger": cross_skill_trigger,
                "allowed_actions": allowed_actions,
                "diagnostic_choice": diagnosis.get("diagnostic_choice"),
                "diagnostic_confidence": diagnosis.get("diagnostic_confidence"),
                "evidence_score": diagnosis.get("evidence_score"),
                "resolved_runtime_subskill": diagnosis.get("selected_runtime_subskill"),
                "selected_prereq_skill": diagnosis.get("selected_prereq_skill") or diagnosis.get("suggested_prereq_skill"),
                "selected_prereq_subskill": diagnosis.get("selected_prereq_subskill") or diagnosis.get("suggested_prereq_subskill"),
                "completion_reason": "stable_breakpoint_detected",
                "completion_stats": completion_eval,
            }

        policy_model = load_phase2_policy_model()
        policy_model_loaded = policy_model is not None
        current_mode = "remediation" if in_remediation else "mainline"
        routing_ctx = routing_state.setdefault("routing_context", {})
        routing_ctx["current_mode"] = current_mode
        routing_ctx["cross_skill_trigger"] = 1 if cross_skill_trigger else 0
        routing_ctx["remediation_review_ready"] = 1 if remediation_review_ready else 0
        routing_ctx["consecutive_wrong_on_family"] = int(consecutive_wrong_on_family)
        routing_ctx["current_family_complexity"] = float(
            textbook_level_index / float(max(1, len(mainline_sequence) - 1))
        ) if textbook_cfg and mainline_sequence else 0.0
        route_action, route_logits, route_action_idx, route_decision_source = select_route_action_with_ppo(
            route_state=routing_state,
            action_mask=action_mask,
            model=policy_model,
        )
        route_policy_debug = get_last_route_policy_debug()
        route_action_raw = str(route_policy_debug.get("raw_action") or route_action or "")
        route_debug: dict[str, Any] = {"action_mask": action_mask, "route_policy_debug": route_policy_debug}
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
            route_action_raw = str(route_action_raw or route_action or "")
        final_route_action = map_route_action_by_mode(route_action, current_mode=current_mode)
        route_action = final_route_action
        if current_mode == "mainline" and not bool(action_mask.get("remediate", False)):
            why_remediate_masked = (
                "cross_skill_trigger_false"
                if not cross_skill_trigger
                else "action_mask_mainline_no_remediate"
            )
        if route_action == "remediate" and not remediation_review_ready:
            route_action = "stay"
            why_remediate_masked = "review_not_ready"
        if route_action == "return" and not return_rule_ready:
            route_action = "stay"
        if (
            not why_remediate_masked
            and current_mode == "mainline"
            and bool(action_mask.get("remediate", False))
            and route_action == "stay"
        ):
            why_remediate_masked = "ppo_chose_stay"

        if (
            textbook_cfg
            and current_mode == "mainline"
            and route_action == "remediate"
        ):
            remediation_retrieval = retrieve_remediation_candidates(
                skill_id=system_skill_id,
                family_id=current_family_for_progression,
                question_text=str(payload.get("last_question_text", "")),
                correct_answer=str(payload.get("last_expected_answer", "")),
                student_answer=str(payload.get("last_user_answer", "") or payload.get("user_answer", "")),
                top_k=3,
            )
            candidate_source = str(
                remediation_retrieval.get("candidate_source")
                or remediation_retrieval.get("retrieval_source")
                or ""
            )
            remediation_candidates = (
                list(remediation_retrieval.get("candidates") or [])
                if isinstance(remediation_retrieval, dict)
                else []
            )
            if not remediation_candidates:
                concept_hint = str(diagnosis.get("error_concept") or "").strip().lower()
                sign_scope_like = any(
                    token in concept_hint
                    for token in ("outer_minus_scope", "bracket_scope", "sign_distribution", "sign_flip")
                )
                power_like = any(
                    token in concept_hint
                    for token in ("power", "binomial_expansion", "special_identity", "product_power_distribution")
                )
                if power_like:
                    remediation_candidates = [
                        {
                            "code": "signed_power_interpretation",
                            "runtime_subskill": "signed_power_interpretation",
                            "prereq_skill": "integer_arithmetic",
                            "description": "?? (-a)^n ? -a^n ??????",
                        },
                        {
                            "code": "same_base_multiplication_rule",
                            "runtime_subskill": "same_base_multiplication_rule",
                            "prereq_skill": "fraction_arithmetic",
                            "description": "?????????????",
                        },
                        {
                            "code": "power_of_power_rule",
                            "runtime_subskill": "power_of_power_rule",
                            "prereq_skill": "fraction_arithmetic",
                            "description": "???????????",
                        },
                        {
                            "code": "product_power_distribution",
                            "runtime_subskill": "product_power_distribution",
                            "prereq_skill": "fraction_arithmetic",
                            "description": "????????",
                        },
                    ]
                else:
                    remediation_candidates = [
                        {
                            "code": "outer_minus_scope" if sign_scope_like else "like_term_combination",
                            "runtime_subskill": "outer_minus_scope" if sign_scope_like else "like_term_combination",
                            "prereq_skill": "linear_expression_arithmetic",
                            "description": "???????????????",
                        },
                        {
                            "code": "monomial_distribution" if sign_scope_like else "term_collection_with_constants",
                            "runtime_subskill": "monomial_distribution" if sign_scope_like else "term_collection_with_constants",
                            "prereq_skill": "linear_expression_arithmetic",
                            "description": "??????????????",
                        },
                        {
                            "code": "like_term_combination" if sign_scope_like else "add_sub",
                            "runtime_subskill": "like_term_combination" if sign_scope_like else "add_sub",
                            "prereq_skill": "linear_expression_arithmetic" if sign_scope_like else "integer_arithmetic",
                            "description": "???????????????",
                        },
                    ]
                candidate_source = "heuristic_fallback_candidates"
            remediation_candidate_labels = [
                str(item.get("runtime_subskill") or item.get("diagnosis_label") or "").strip()
                for item in remediation_candidates
                if isinstance(item, dict)
            ]
            diagnosis = rag_diagnose(
                current_skill=current_skill,
                current_subskill=current_subskill,
                current_family_id=last_family_id,
                question_text=str(payload.get("last_question_text", "")),
                student_answer=str(payload.get("last_user_answer", "") or payload.get("user_answer", "")),
                expected_answer=str(payload.get("last_expected_answer", "")),
                is_correct=last_is_correct,
                fail_streak=fail_streak,
                frustration=frustration_norm,
                same_skill_streak=agent_state.get("same_skill_streak", 0),
                routing_session=routing_session,
                prerequisite_candidates=remediation_candidates,
                unit_skill_id=system_skill_id,
                enable_choice_diagnosis=True,
            )
            if isinstance(diagnosis.get("routing_session"), dict):
                routing_session = dict(diagnosis.get("routing_session") or routing_session)
            if not diagnosis.get("suggested_prereq_skill"):
                diagnosis["suggested_prereq_skill"] = "integer_arithmetic"
            if not diagnosis.get("suggested_prereq_subskill"):
                fallback_runtime_subskill = (
                    str(remediation_candidates[0].get("runtime_subskill") or "").strip()
                    if remediation_candidates else ""
                )
                diagnosis["suggested_prereq_subskill"] = fallback_runtime_subskill or "add_sub"
            diagnosis["selected_prereq_skill"] = diagnosis.get("selected_prereq_skill") or diagnosis.get("suggested_prereq_skill")
            diagnosis["selected_prereq_subskill"] = diagnosis.get("selected_prereq_subskill") or diagnosis.get("suggested_prereq_subskill")
            suggested_after_diag = str(diagnosis.get("suggested_prereq_skill") or "").strip()
            if suggested_after_diag:
                allowed_agent_skills_after_filter = [current_skill, suggested_after_diag]
            else:
                allowed_agent_skills_after_filter = list(allowed_agent_skills_before_filter)
            allowed_agent_skills = list(allowed_agent_skills_after_filter)
            diagnosis["remediation_triggered"] = True

        remediation_triggered_final = bool(current_mode == "mainline" and route_action == "remediate")
        return_triggered_final = bool(current_mode == "remediation" and route_action == "return" and return_rule_ready)

        updated_routing, routed_skill, routed_subskill = apply_routing_action(
            action=route_action,
            current_skill=current_skill,
            current_subskill=current_subskill,
            current_family=current_family_for_progression,
            diagnosis=diagnosis,
            routing_session=routing_session,
        )
        routing_session = updated_routing
        selected_agent_skill = routed_skill
        route_subskill_override = routed_subskill
        post_in_remediation = bool(routing_session.get("in_remediation", False))
        post_mode = "remediation" if post_in_remediation else "mainline"
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
            rescue_recommended=bool((routing_state.get("diagnostic_signal") or {}).get("rescue_recommended", 0)),
            cross_skill_trigger=bool(cross_skill_trigger),
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
                + float(routing_reward["missed_remediation_penalty"])
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
            current_family=current_family_for_progression,
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
            f"ppo_action={route_action} ppo_route_action_raw={route_action_raw} decision_source={route_decision_source} "
            f"in_remediation={routing_session.get('in_remediation')} "
            f"origin_skill={routing_session.get('origin_skill')} "
            f"remediation_skill={routing_session.get('remediation_skill')} "
            f"steps_taken={routing_session.get('steps_taken')} "
            f"remediation_review_ready={remediation_review_ready} "
            f"why_remediate_masked={why_remediate_masked} "
            f"remediate_bias_applied={route_policy_debug.get('remediate_bias_applied')} "
            f"remediate_bias_value={route_policy_debug.get('remediate_bias_value')} "
            f"remediation_mastery={remediation_mastery:.4f} "
            f"recent_correct={recent_correct} "
            f"return_mastery_threshold={return_mastery_threshold:.2f} "
            f"return_mastery_with_recent_correct_threshold={return_mastery_with_recent_correct_threshold:.2f} "
            f"return_ready={return_ready} return_reason={return_reason} "
            f"remediation_mastery_source={remediation_mastery_source} "
            f"correctness_reward={routing_reward['correctness_reward']:.2f} "
            f"recovery_reward={routing_reward['recovery_reward']:.2f} "
            f"return_success_reward={routing_reward['return_success_reward']:.2f} "
            f"stagnation_penalty={routing_reward['stagnation_penalty']:.2f} "
            f"unnecessary_route_penalty={routing_reward['unnecessary_route_penalty']:.2f} "
            f"missed_remediation_penalty={routing_reward['missed_remediation_penalty']:.2f} "
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
                f"remediation_mastery={remediation_mastery:.4f} "
                f"recent_correct={recent_correct} "
                f"return_mastery_threshold={return_mastery_threshold:.2f} "
                f"return_mastery_with_recent_correct_threshold={return_mastery_with_recent_correct_threshold:.2f} "
                f"return_ready={return_ready} "
                f"remediation_mastery_source={remediation_mastery_source} "
                f"correctness_reward={routing_reward['correctness_reward']:.2f} "
                f"recovery_reward={routing_reward['recovery_reward']:.2f} "
                f"return_success_reward={routing_reward['return_success_reward']:.2f} "
                f"stagnation_penalty={routing_reward['stagnation_penalty']:.2f} "
                f"unnecessary_route_penalty={routing_reward['unnecessary_route_penalty']:.2f} "
                f"missed_remediation_penalty={routing_reward['missed_remediation_penalty']:.2f} "
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
        decision_trace["route_policy_logits_raw"] = route_policy_debug.get("raw_logits")
        decision_trace["route_policy_logits_biased"] = route_policy_debug.get("biased_logits")
        decision_trace["route_action_idx"] = route_action_idx
        decision_trace["route_action"] = route_action
        decision_trace["route_action_raw"] = route_action_raw
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
        normalized_runtime_subskill = normalize_runtime_subskill(
            selected_subskill,
            target_agent_skill=selected_agent_skill,
            origin_agent_skill=current_skill,
            error_concept=str(diagnosis.get("error_concept") or ""),
        )
        if normalized_runtime_subskill != selected_subskill:
            route_debug["subskill_normalized"] = {
                "raw": selected_subskill,
                "normalized": normalized_runtime_subskill,
            }
        selected_subskill = normalized_runtime_subskill
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
            "route_action_raw": route_action_raw,
            "route_action_idx": route_action_idx,
            "route_policy_logits": route_logits,
            "route_policy_logits_raw": route_policy_debug.get("raw_logits"),
            "route_policy_logits_biased": route_policy_debug.get("biased_logits"),
            "routing_state": routing_session,
            "diagnosis": diagnosis,
            "route_debug": route_debug,
            "why_remediate_masked": why_remediate_masked,
            "remediate_bias_applied": bool(route_policy_debug.get("remediate_bias_applied", False)),
            "remediate_bias_value": float(route_policy_debug.get("remediate_bias_value", 0.0) or 0.0),
            "cross_skill_trigger": cross_skill_trigger,
            "bridge_active": int(routing_session.get("bridge_remaining", 0) or 0) > 0,
            "correctness_reward": routing_reward["correctness_reward"],
            "recovery_reward": routing_reward["recovery_reward"],
            "return_success_reward": routing_reward["return_success_reward"],
            "stagnation_penalty": routing_reward["stagnation_penalty"],
            "unnecessary_route_penalty": routing_reward["unnecessary_route_penalty"],
            "missed_remediation_penalty": routing_reward["missed_remediation_penalty"],
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
        phase1_entries, subskill_filter_hit, fallback_to_skill_only = _filter_entries_for_agent_and_subskill(
            entries,
            selected_agent_skill=selected_agent_skill,
            selected_subskill=selected_subskill,
            family_subskill_map=family_subskill_map,
        )
        if (
            not phase1_entries
            and selected_agent_skill
            and selected_agent_skill != current_skill
        ):
            cross_skill_pool = _apply_demo_safe_family_filter(
                load_catalog(),
                mode=mode,
                system_skill_id=system_skill_id,
            )
            phase1_entries, subskill_filter_hit, fallback_to_skill_only = _filter_entries_for_agent_and_subskill(
                cross_skill_pool,
                selected_agent_skill=selected_agent_skill,
                selected_subskill=selected_subskill,
                family_subskill_map=family_subskill_map,
            )
            route_debug["cross_skill_pool"] = "global_catalog"
        route_debug["subskill_filter_hit"] = subskill_filter_hit
        route_debug["fallback_to_skill_only"] = fallback_to_skill_only
        mapping_candidates = [f"{entry.skill_id}:{entry.family_id}" for entry in phase1_entries]
        decision_trace["mapping_candidates"] = mapping_candidates
        next_entry = None
        if textbook_cfg and selected_agent_skill == "polynomial_arithmetic":
            target_family = None
            if not current_family_for_progression:
                target_family = str(mainline_sequence[0]) if mainline_sequence else "F1"
            elif just_returned_from_remediation:
                target_family = str(routing_session.get("origin_family") or current_family_for_progression or "")
                if target_family not in mainline_sequence:
                    target_family = current_family_for_progression or (str(mainline_sequence[0]) if mainline_sequence else "F1")
            elif last_is_correct is True:
                target_family = next_family_candidate or current_family_for_progression
            elif last_is_correct is False:
                target_family = current_family_for_progression
            else:
                target_family = current_family_for_progression

            next_entry = _pick_demo_entry(
                entries,
                selected_agent_skill=selected_agent_skill,
                family_id=str(target_family or ""),
            )
            if next_entry is not None:
                selection_mode = "textbook_sequence"
                fallback_reason = None
            else:
                fallback_reason = "textbook_sequence_target_missing"

        if next_entry is None:
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
        if ADAPTIVE_DEMO_SAFE_MODE:
            demo_pool = phase1_entries if phase1_entries else entries
            if (not demo_start_forced) and len(history_rows) == 0 and current_skill == "polynomial_arithmetic":
                forced_entry = _pick_demo_entry(
                    demo_pool,
                    selected_agent_skill=selected_agent_skill,
                    family_id=DEMO_SCENARIO_PRIMARY_START,
                )
                if forced_entry is not None:
                    next_entry = forced_entry
                    selection_mode = "demo_override_start"
                    demo_override_reason = "force_start_family_f1"
                    demo_start_forced = True
                    routing_session["demo_start_forced"] = True
                    scenario_stage = "forced_start_f1"
                    routing_session["scenario_stage"] = scenario_stage
            elif (not demo_first_remediation_forced) and entered_remediation and selected_agent_skill == "integer_arithmetic":
                forced_entry = _pick_demo_entry(
                    demo_pool,
                    selected_agent_skill=selected_agent_skill,
                    family_id=DEMO_SCENARIO_REMEDIATION_ENTRY,
                )
                if forced_entry is not None:
                    next_entry = forced_entry
                    selection_mode = "demo_override_remediation"
                    demo_override_reason = "force_first_remediation_i1"
                    demo_first_remediation_forced = True
                    routing_session["demo_first_remediation_forced"] = True
                    scenario_stage = "forced_first_remediation_i1"
                    routing_session["scenario_stage"] = scenario_stage
            elif just_returned_from_remediation and selected_agent_skill == "polynomial_arithmetic":
                # Do not override return target; keep textbook/mainline return behavior.
                demo_first_return_forced = True
                routing_session["demo_first_return_forced"] = True
                scenario_stage = "returned_to_origin_family"
                routing_session["scenario_stage"] = scenario_stage
            else:
                scenario_stage = "open_demo_pool"
                routing_session["scenario_stage"] = scenario_stage
            if demo_override_reason:
                policy_debug["demo_override_reason"] = demo_override_reason
            policy_debug["scenario_stage"] = scenario_stage
        entry_subskills = list(next_entry.subskill_nodes or [])
        if entry_subskills and (not selected_subskill or selected_subskill not in entry_subskills):
            policy_debug["family_subskill_alignment"] = {
                "family_id": next_entry.family_id,
                "before": selected_subskill,
                "after": entry_subskills[0],
                "entry_subskills": entry_subskills,
            }
            selected_subskill = entry_subskills[0]
            decision_trace["selected_subskill"] = selected_subskill
            subskill_source = "family_primary_subskill_override"
        else:
            subskill_source = "route_override" if route_subskill_override else str(subskill_debug.get("mode") or "unknown")
        print(
            "[adaptive_remediation_trace] "
            f"diag_error_concept={diagnosis.get('error_concept')} "
            f"diag_confidence={diagnosis.get('diagnosis_confidence')} "
            f"suggested_prereq_skill={diagnosis.get('suggested_prereq_skill')} "
            f"suggested_prereq_subskill={diagnosis.get('suggested_prereq_subskill')} "
            f"retrieved_candidates={len(diagnosis.get('retrieved_candidates') or [])} "
            f"diagnostic_choice={diagnosis.get('diagnostic_choice')} "
            f"qwen_classifier_choice={diagnosis.get('diagnostic_choice')} "
            f"diagnostic_confidence={diagnosis.get('diagnostic_confidence')} "
            f"evidence_score={diagnosis.get('evidence_score')} "
            f"resolved_runtime_subskill={diagnosis.get('selected_runtime_subskill')} "
            f"remediation_triggered={diagnosis.get('remediation_triggered')} "
            f"remediation_review_ready={remediation_review_ready} "
            f"remediation_triggered_final={remediation_triggered_final} "
            f"return_rule_ready={return_rule_ready} "
            f"return_triggered_final={return_triggered_final} "
            f"current_mode={current_mode} post_mode={post_mode} "
            f"normalized_runtime_subskill={selected_subskill} "
            f"subskill_filter_hit={subskill_filter_hit} "
            f"fallback_to_skill_only={fallback_to_skill_only} "
            f"cross_skill_trigger={cross_skill_trigger} "
            f"route_action={route_action} "
            f"why_remediate_masked={why_remediate_masked} "
            f"decision_source={route_decision_source} "
            f"in_remediation={routing_session.get('in_remediation')} "
            f"origin_family={routing_session.get('origin_family')} "
            f"selected_agent_skill={selected_agent_skill} "
            f"selected_subskill={selected_subskill} "
            f"selected_subskill_source={subskill_source} "
            f"selected_family={next_entry.family_id if next_entry is not None else None} "
            f"progression_mode={progression_mode} "
            f"current_family={current_family_for_progression} "
            f"next_family_candidate={next_family_candidate} "
            f"previous_family_candidate={previous_family_candidate} "
            f"remediation_candidates={','.join(remediation_candidate_labels)} "
            f"textbook_level_index={textbook_level_index} "
            f"consecutive_wrong_on_family={consecutive_wrong_on_family} "
            f"demo_mode={ADAPTIVE_DEMO_SAFE_MODE} "
            f"allowed_demo_families={','.join(allowed_demo_families_display)} "
            f"selection_mode={selection_mode} "
            f"fallback_reason={fallback_reason}",
            flush=True,
        )
        print(
            "[adaptive_demo_scenario] "
            f"scenario_stage={scenario_stage} "
            f"selected_family={next_entry.family_id if next_entry is not None else None} "
            f"allowed_demo_families={','.join(allowed_demo_families_display)}",
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
        observability["selection_debug"]["progression_mode"] = progression_mode
        observability["selection_debug"]["current_family"] = current_family_for_progression
        observability["selection_debug"]["next_family_candidate"] = next_family_candidate
        observability["selection_debug"]["previous_family_candidate"] = previous_family_candidate
        observability["selection_debug"]["remediation_candidates"] = remediation_candidates
        observability["selection_debug"]["candidate_source"] = candidate_source
        observability["selection_debug"]["textbook_level_index"] = textbook_level_index
        observability["selection_debug"]["consecutive_wrong_on_family"] = consecutive_wrong_on_family
        observability["selection_debug"]["retrieved_candidates"] = diagnosis.get("retrieved_candidates", [])
        observability["selection_debug"]["selected_prereq_skill"] = diagnosis.get("selected_prereq_skill") or diagnosis.get("suggested_prereq_skill")
        observability["selection_debug"]["selected_prereq_subskill"] = diagnosis.get("selected_prereq_subskill") or diagnosis.get("suggested_prereq_subskill")
        observability["selection_debug"]["allowed_agent_skills_before_filter"] = allowed_agent_skills_before_filter
        observability["selection_debug"]["allowed_agent_skills_after_filter"] = allowed_agent_skills_after_filter
        observability["selection_debug"]["diagnostic_choice"] = diagnosis.get("diagnostic_choice")
        observability["selection_debug"]["qwen_classifier_choice"] = diagnosis.get("diagnostic_choice")
        observability["selection_debug"]["diagnostic_confidence"] = diagnosis.get("diagnostic_confidence")
        observability["selection_debug"]["evidence_score"] = diagnosis.get("evidence_score")
        observability["selection_debug"]["resolved_runtime_subskill"] = diagnosis.get("selected_runtime_subskill")
        observability["selection_debug"]["current_mode"] = current_mode
        observability["selection_debug"]["post_mode"] = post_mode
        observability["selection_debug"]["local_apr"] = current_apr
        observability["selection_debug"]["remediation_mastery"] = remediation_mastery
        observability["selection_debug"]["remediation_mastery_source"] = remediation_mastery_source
        observability["selection_debug"]["recent_correct"] = recent_correct
        observability["selection_debug"]["return_mastery_threshold"] = return_mastery_threshold
        observability["selection_debug"]["return_mastery_with_recent_correct_threshold"] = (
            return_mastery_with_recent_correct_threshold
        )
        observability["selection_debug"]["why_remediate_masked"] = why_remediate_masked
        observability["selection_debug"]["in_remediation"] = bool(routing_session.get("in_remediation", False))
        observability["selection_debug"]["origin_family"] = str(routing_session.get("origin_family") or "")
        observability["selection_debug"]["remediation_family"] = (
            next_entry.family_id if post_mode == "remediation" else ""
        )
        observability["selection_debug"]["selected_family_for_render"] = next_entry.family_id
        observability["selection_debug"]["remediation_review_ready"] = remediation_review_ready
        observability["selection_debug"]["sign_distribution_signal"] = sign_distribution_signal
        observability["selection_debug"]["f2_sign_distribution_signal"] = sign_distribution_signal
        observability["selection_debug"]["ppo_route_action"] = route_action
        observability["selection_debug"]["ppo_route_action_raw"] = route_action_raw
        observability["selection_debug"]["ppo_route_logits_raw"] = route_policy_debug.get("raw_logits")
        observability["selection_debug"]["ppo_route_logits_biased"] = route_policy_debug.get("biased_logits")
        observability["selection_debug"]["remediate_bias_applied"] = bool(
            route_policy_debug.get("remediate_bias_applied", False)
        )
        observability["selection_debug"]["remediate_bias_value"] = float(
            route_policy_debug.get("remediate_bias_value", 0.0) or 0.0
        )
        observability["selection_debug"]["final_route_action"] = route_action
        observability["selection_debug"]["remediation_triggered"] = remediation_triggered_final
        observability["selection_debug"]["remediation_triggered_final"] = remediation_triggered_final
        observability["selection_debug"]["return_rule_ready"] = return_rule_ready
        observability["selection_debug"]["return_triggered_final"] = return_triggered_final
        observability["selection_debug"]["demo_mode"] = ADAPTIVE_DEMO_SAFE_MODE
        observability["selection_debug"]["full_catalog_mode"] = ADAPTIVE_USE_FULL_CATALOG
        observability["selection_debug"]["allowed_demo_families"] = allowed_demo_families_display
        observability["selection_debug"]["selected_family"] = next_entry.family_id
        observability["selection_debug"]["return_to_mainline"] = just_returned_from_remediation
        observability["selection_debug"]["missed_remediation_penalty"] = routing_reward["missed_remediation_penalty"]
        observability["selection_debug"]["scenario_stage"] = scenario_stage
        if demo_override_reason:
            observability["selection_debug"]["demo_override_reason"] = demo_override_reason
        observability["selection_debug"]["routing_summary"] = routing_summary
        observability["selection_debug"]["routing_timeline"] = _normalize_routing_timeline(
            routing_session.get("routing_timeline")
        )
        observability["selection_debug"]["routing_timeline_summary"] = summarize_routing_timeline(
            routing_session.get("routing_timeline")
        )
        observability["selection_debug"]["mode"] = mode
        observability["selection_debug"]["unit_completed"] = False
        observability["selection_debug"]["local_remediation_completed"] = bool(just_returned_from_remediation)
        observability["selection_debug"]["completion_reason"] = str(completion_eval.get("completion_reason", ""))
        observability["selection_debug"]["completion_stats"] = completion_eval
        observability["selection_debug"]["assessment_completed"] = bool(completion_eval.get("assessment_completed", False))
        observability["selection_debug"]["assessment_stop_reason"] = str(completion_eval.get("assessment_stop_reason", ""))
        observability["selection_debug"]["milestone_state"] = _derive_milestone_state(
            mode=mode,
            unit_completed=False,
            local_remediation_completed=bool(just_returned_from_remediation),
            return_to_mainline=bool(just_returned_from_remediation),
            return_triggered_final=bool(return_triggered_final),
            post_mode=post_mode,
            scenario_stage=scenario_stage,
            assessment_completed=bool(completion_eval.get("assessment_completed", False)),
            assessment_stop_reason=str(completion_eval.get("assessment_stop_reason", "")),
        )

    started = time.perf_counter()
    question_payload = _generate_question_payload(next_entry, selected_subskill=selected_subskill)
    latency_ms = int((time.perf_counter() - started) * 1000)

    resolved_target_subskills = list(next_entry.subskill_nodes)
    if selected_subskill and selected_subskill not in resolved_target_subskills:
        resolved_target_subskills = [selected_subskill] + resolved_target_subskills

    print(
        "[adaptive_policy_observability] "
        f"model_loaded={policy_model_loaded} "
        f"decision_source={route_decision_source} "
        f"ppo_raw_action_idx={route_action_idx} "
        f"ppo_raw_action={route_action_raw} "
        f"final_route_action={route_action} "
        f"ppo_route_logits_raw={route_policy_debug.get('raw_logits')} "
        f"remediate_bias_applied={route_policy_debug.get('remediate_bias_applied')} "
        f"remediate_bias_value={route_policy_debug.get('remediate_bias_value')} "
        f"current_mode={current_mode} "
        f"resolved_agent_skill={selected_agent_skill} "
        f"resolved_family={next_entry.family_id} "
        f"resolved_subskill={selected_subskill} "
        f"selected_prereq_skill={diagnosis.get('selected_prereq_skill') or diagnosis.get('suggested_prereq_skill')} "
        f"selected_prereq_subskill={diagnosis.get('selected_prereq_subskill') or diagnosis.get('suggested_prereq_subskill')} "
        f"candidate_source={candidate_source} "
        f"allowed_agent_skills_before_filter={allowed_agent_skills_before_filter} "
        f"allowed_agent_skills_after_filter={allowed_agent_skills_after_filter} "
        f"progression_mode={progression_mode} "
        f"mode={mode} "
        f"unit_completed={completion_eval.get('unit_completed')} "
        f"completion_reason={completion_eval.get('completion_reason')} "
        f"current_family={current_family_for_progression} "
        f"next_family_candidate={next_family_candidate} "
        f"previous_family_candidate={previous_family_candidate} "
        f"remediation_candidates={','.join(remediation_candidate_labels)} "
        f"textbook_level_index={textbook_level_index} "
        f"consecutive_wrong_on_family={consecutive_wrong_on_family} "
        f"remediation_review_ready={remediation_review_ready} "
        f"missed_remediation_penalty={routing_reward['missed_remediation_penalty']:.2f} "
        f"why_remediate_masked={why_remediate_masked} "
        f"remediation_mastery={remediation_mastery:.4f} "
        f"remediation_mastery_source={remediation_mastery_source} "
        f"recent_correct={recent_correct} "
        f"return_mastery_threshold={return_mastery_threshold:.2f} "
        f"return_mastery_with_recent_correct_threshold={return_mastery_with_recent_correct_threshold:.2f} "
        f"remediation_triggered_final={remediation_triggered_final} "
        f"return_rule_ready={return_rule_ready} "
        f"return_triggered_final={return_triggered_final} "
        f"demo_mode={ADAPTIVE_DEMO_SAFE_MODE} "
        f"full_catalog_mode={ADAPTIVE_USE_FULL_CATALOG} "
        f"allowed_demo_families={','.join(allowed_demo_families_display)} "
        f"scenario_stage={scenario_stage} "
        f"origin_family={routing_session.get('origin_family')} "
        f"return_to_mainline={just_returned_from_remediation}",
        flush=True,
    )

    display_state = _build_display_state(
        is_completed=False,
        post_mode=post_mode,
        return_to_mainline=just_returned_from_remediation,
        return_triggered_final=return_triggered_final,
        selected_skill=selected_agent_skill,
        selected_family=next_entry.family_id,
        selected_subskill=selected_subskill,
        scenario_stage=scenario_stage,
    )
    if isinstance(observability.get("selection_debug"), dict):
        observability["selection_debug"]["display_mode"] = display_state["display_mode"]
        observability["selection_debug"]["display_family"] = display_state["display_family"]
        observability["selection_debug"]["display_subskill"] = display_state["display_subskill"]
        observability["selection_debug"]["display_skill"] = display_state["display_skill"]
        observability["selection_debug"]["is_completed"] = False

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
        "demo_mode": ADAPTIVE_DEMO_SAFE_MODE,
        "full_catalog_mode": ADAPTIVE_USE_FULL_CATALOG,
        "allowed_demo_families": allowed_demo_families_display,
        "scenario_stage": scenario_stage,
        "display_mode": display_state["display_mode"],
        "display_family": display_state["display_family"],
        "display_subskill": display_state["display_subskill"],
        "display_skill": display_state["display_skill"],
        "is_completed": False,
        "unit_completed": False,
        "local_remediation_completed": bool(just_returned_from_remediation),
        "completion_reason": str(completion_eval.get("completion_reason", "")),
        "completion_stats": completion_eval,
        "mode": mode,
        "allowed_actions": allowed_actions,
        "action_mask": action_mask,
        "milestone_state": _derive_milestone_state(
            mode=mode,
            unit_completed=False,
            local_remediation_completed=bool(just_returned_from_remediation),
            return_to_mainline=bool(just_returned_from_remediation),
            return_triggered_final=bool(return_triggered_final),
            post_mode=post_mode,
            scenario_stage=scenario_stage,
            assessment_completed=bool(completion_eval.get("assessment_completed", False)),
            assessment_stop_reason=str(completion_eval.get("assessment_stop_reason", "")),
        ),
        "assessment_completed": bool(completion_eval.get("assessment_completed", False)),
        "assessment_stop_reason": str(completion_eval.get("assessment_stop_reason", "")),
        "retrieved_candidates": diagnosis.get("retrieved_candidates", []),
        "diagnostic_choice": diagnosis.get("diagnostic_choice"),
        "qwen_classifier_choice": diagnosis.get("diagnostic_choice"),
        "diagnostic_confidence": diagnosis.get("diagnostic_confidence"),
        "evidence_score": diagnosis.get("evidence_score"),
        "resolved_runtime_subskill": diagnosis.get("selected_runtime_subskill"),
        "selected_prereq_skill": diagnosis.get("selected_prereq_skill") or diagnosis.get("suggested_prereq_skill"),
        "selected_prereq_subskill": diagnosis.get("selected_prereq_subskill") or diagnosis.get("suggested_prereq_subskill"),
        "candidate_source": candidate_source,
        "current_mode": post_mode,
        "mode_before_decision": current_mode,
        "post_mode": post_mode,
        "remediation_review_ready": remediation_review_ready,
        "sign_distribution_signal": sign_distribution_signal,
        "f2_sign_distribution_signal": sign_distribution_signal,
        "remediation_mastery": remediation_mastery,
        "remediation_mastery_source": remediation_mastery_source,
        "recent_correct": recent_correct,
        "return_mastery_threshold": return_mastery_threshold,
        "return_mastery_with_recent_correct_threshold": return_mastery_with_recent_correct_threshold,
        "why_remediate_masked": why_remediate_masked,
        "ppo_route_action_raw": route_action_raw,
        "ppo_route_logits_raw": route_policy_debug.get("raw_logits"),
        "ppo_route_logits_biased": route_policy_debug.get("biased_logits"),
        "remediate_bias_applied": bool(route_policy_debug.get("remediate_bias_applied", False)),
        "remediate_bias_value": float(route_policy_debug.get("remediate_bias_value", 0.0) or 0.0),
        "final_route_action": route_action,
        "ppo_route_action": route_action,
        "remediation_triggered": remediation_triggered_final,
        "remediation_triggered_final": remediation_triggered_final,
        "return_rule_ready": return_rule_ready,
        "return_triggered_final": return_triggered_final,
        "return_to_mainline": just_returned_from_remediation,
        "progression_mode": progression_mode,
        "current_family": current_family_for_progression,
        "origin_family": str(routing_session.get("origin_family") or ""),
        "remediation_family": (next_entry.family_id if post_mode == "remediation" else ""),
        "selected_family_for_render": next_entry.family_id,
        "next_family_candidate": next_family_candidate,
        "previous_family_candidate": previous_family_candidate,
        "remediation_candidates": remediation_candidates,
        "allowed_agent_skills_before_filter": allowed_agent_skills_before_filter,
        "allowed_agent_skills_after_filter": allowed_agent_skills_after_filter,
        "textbook_level_index": textbook_level_index,
        "consecutive_wrong_on_family": consecutive_wrong_on_family,
        "missed_remediation_penalty": routing_reward["missed_remediation_penalty"],
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

