# -*- coding: utf-8 -*-
from __future__ import annotations

import json

from flask import jsonify, request, session
from flask_login import current_user, login_required

from core.adaptive.judge import judge_answer_with_feedback
from . import practice_bp
from core.adaptive.session_engine import get_rag_hint, submit_and_get_next


_MAX_RUNTIME_SESSIONS = 2
_MAX_TEXT_LEN = 240
_MAX_ANSWER_LEN = 80
_MAX_SUBSKILLS = 6
_MAX_RECENT_RESULTS = 4
_ROUTING_STATE_ALLOWLIST = {
    "mode",
    "current_skill",
    "current_mode",
    "in_remediation",
    "origin_skill",
    "origin_family",
    "remediation_skill",
    "remediation_subskill",
    "bridge_remaining",
    "lock_min_steps",
    "steps_taken",
    "recent_results",
    "remediation_mastery",
    "last_result",
    "return_to_mainline",
    "scenario_stage",
    "demo_start_forced",
    "demo_first_remediation_forced",
    "demo_first_return_forced",
    "milestone_event",
    "milestone_flash_available",
    "unit_completed",
    "local_remediation_completed",
    "assessment_completed",
}


def _trim_text(value: object, *, max_len: int) -> str:
    text = str(value or "").strip()
    if len(text) <= max_len:
        return text
    return text[:max_len]


def _to_bool_list(value: object, *, max_len: int) -> list[bool]:
    if not isinstance(value, list):
        return []
    out: list[bool] = []
    for item in value:
        out.append(bool(item))
    return out[-max_len:]


def _to_float(value: object, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return float(default)


def _to_int(value: object, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return int(default)


def _slim_routing_state(raw: object) -> dict:
    if not isinstance(raw, dict):
        return {}
    slim: dict = {}
    for key in _ROUTING_STATE_ALLOWLIST:
        if key not in raw:
            continue
        value = raw.get(key)
        if key in {"mode", "current_skill", "origin_skill", "remediation_skill", "remediation_subskill", "origin_family", "scenario_stage", "current_mode", "milestone_event"}:
            slim[key] = _trim_text(value, max_len=96)
        elif key in {"in_remediation", "last_result", "return_to_mainline", "demo_start_forced", "demo_first_remediation_forced", "demo_first_return_forced", "milestone_flash_available", "unit_completed", "local_remediation_completed", "assessment_completed"}:
            slim[key] = bool(value)
        elif key in {"bridge_remaining", "lock_min_steps", "steps_taken"}:
            slim[key] = _to_int(value, 0)
        elif key == "recent_results":
            slim[key] = _to_bool_list(value, max_len=_MAX_RECENT_RESULTS)
        elif key == "remediation_mastery":
            slim[key] = _to_float(value, 0.0)
    return slim


def _slim_subskills(raw: object) -> list[str]:
    if not isinstance(raw, list):
        return []
    out: list[str] = []
    for item in raw:
        text = _trim_text(item, max_len=64)
        if text:
            out.append(text)
        if len(out) >= _MAX_SUBSKILLS:
            break
    return out


def _prune_runtime_store(runtime_store: dict, *, current_session_id: str) -> dict:
    if len(runtime_store) <= _MAX_RUNTIME_SESSIONS:
        return runtime_store
    pruned: dict = {}
    if current_session_id and current_session_id in runtime_store:
        pruned[current_session_id] = runtime_store[current_session_id]
    for key in reversed(list(runtime_store.keys())):
        if key in pruned:
            continue
        pruned[key] = runtime_store[key]
        if len(pruned) >= _MAX_RUNTIME_SESSIONS:
            break
    return pruned


def _adaptive_runtime_store() -> dict:
    store = session.get("adaptive_runtime", {})
    if not isinstance(store, dict):
        store = {}
    else:
        store = _prune_runtime_store(store, current_session_id="")
    return store


def _response_for_frontend(response: dict) -> dict:
    sanitized = dict(response)
    q = dict(sanitized.get("new_question_data", {}) or {})
    q.pop("answer", None)
    q.pop("correct_answer", None)
    sanitized["new_question_data"] = q
    return sanitized


@practice_bp.route("/api/adaptive/submit_and_get_next", methods=["POST"])
@login_required
def adaptive_submit_and_get_next():
    payload = request.get_json(silent=True) or {}
    if "student_id" not in payload:
        payload["student_id"] = current_user.id

    try:
        runtime_store = _adaptive_runtime_store()
        session_id = str(payload.get("session_id") or "")
        runtime = runtime_store.get(session_id, {}) if session_id else {}

        grading_analysis = None
        if runtime:
            payload["last_family_id"] = runtime.get("family_id", payload.get("last_family_id"))
            payload["last_subskills"] = runtime.get("subskill_nodes", payload.get("last_subskills"))
            payload["routing_state"] = _slim_routing_state(runtime.get("routing_state", payload.get("routing_state")))
            payload["last_expected_answer"] = runtime.get("correct_answer", payload.get("last_expected_answer"))
            payload["last_question_text"] = runtime.get("question_text", payload.get("last_question_text"))
            if "user_answer" in payload and "is_correct" not in payload:
                judged = judge_answer_with_feedback(
                    payload.get("user_answer"),
                    runtime.get("correct_answer"),
                    question_text=runtime.get("question_text", ""),
                    family_id=runtime.get("family_id"),
                )
                payload["is_correct"] = bool(judged.get("is_correct", False))
                payload["answer_feedback"] = str(judged.get("feedback") or "")
                fam = _trim_text(runtime.get("family_id"), max_len=24)
                grading_analysis = {
                    "family_id": fam,
                    "error_mechanism": "unknown",
                    "step_focus": "",
                    "main_issue": str(payload.get("answer_feedback") or ""),
                    "status": "correct" if payload["is_correct"] else "incorrect",
                    "expected_answer": _trim_text(runtime.get("correct_answer"), max_len=_MAX_ANSWER_LEN),
                    "answer_feedback": str(payload.get("answer_feedback") or ""),
                    "analysis_source": str(judged.get("analysis_source") or "generic_text_answer_judge"),
                    "is_correct": bool(payload["is_correct"]),
                    "grading_step": int(payload.get("step_number") or 0),
                }
            payload["last_user_answer"] = payload.get("user_answer", payload.get("last_user_answer"))
        else:
            payload["routing_state"] = _slim_routing_state(payload.get("routing_state"))

        response = submit_and_get_next(payload)
        if grading_analysis is not None:
            response["grading_analysis"] = grading_analysis
            try:
                print(
                    f"[adaptive_submit] grading_analysis_source={grading_analysis.get('analysis_source')} "
                    f"family_id={grading_analysis.get('family_id')} status={grading_analysis.get('status')}",
                    flush=True,
                )
            except Exception:
                pass
        if payload.get("answer_feedback"):
            response["answer_feedback"] = str(payload.get("answer_feedback"))
        next_session_id = response["session_id"]
        if response.get("completed"):
            runtime_store.pop(next_session_id, None)
        else:
            runtime_store[next_session_id] = {
                "family_id": _trim_text(response.get("target_family_id"), max_len=24),
                "subskill_nodes": _slim_subskills(response.get("target_subskills")),
                "correct_answer": _trim_text(
                    response["new_question_data"].get("correct_answer") or response["new_question_data"].get("answer") or "",
                    max_len=_MAX_ANSWER_LEN,
                ),
                "question_text": _trim_text(
                    response["new_question_data"].get("question_text") or response["new_question_data"].get("question") or "",
                    max_len=_MAX_TEXT_LEN,
                ),
                "routing_state": _slim_routing_state(response.get("routing_state", {})),
            }
            runtime_store = _prune_runtime_store(runtime_store, current_session_id=next_session_id)
        session["adaptive_runtime"] = runtime_store
        try:
            runtime_size = len(json.dumps(runtime_store, ensure_ascii=False))
            print(
                f"[adaptive_runtime_session] entries={len(runtime_store)} approx_json_bytes={runtime_size}",
                flush=True,
            )
        except Exception:
            pass
        session.modified = True
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": f"adaptive engine failure: {exc}"}), 500
    return jsonify(_response_for_frontend(response))


@practice_bp.route("/api/adaptive/rag_settings", methods=["GET"])
@login_required
def api_adaptive_rag_settings():
    import os
    rag_path = os.path.join(current_app.root_path, '..', 'configs', 'rag_settings.json')
    if os.path.exists(rag_path):
        try:
            with open(rag_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Sync memory threshold when loading if it differs
                if 'threshold' in data:
                    current_app.config['ADVANCED_RAG_NAIVE_THRESHOLD'] = data['threshold']
                return jsonify(data)
        except Exception as e:
            print(f"Error reading rag_settings: {e}")
            pass
    return jsonify({
        'threshold': current_app.config.get('ADVANCED_RAG_NAIVE_THRESHOLD', 0.35),
        'target_type': 'practice'
    })


@practice_bp.route("/api/adaptive/rag_hint", methods=["GET"])
@login_required
def adaptive_rag_hint():
    nodes = request.args.getlist("subskill_nodes")
    if not nodes:
        raw = request.args.get("subskill_nodes", "")
        nodes = [part.strip() for part in raw.replace(",", ";").split(";") if part.strip()]
    skill_id = request.args.get("skill_id", "").strip()
    family_id = request.args.get("family_id", "").strip()
    question_context = request.args.get("question_context", "").strip()
    question_text = request.args.get("question_text", "").strip()
    unit_skill_ids = request.args.getlist("unit_skill_ids")
    if not unit_skill_ids:
        raw_unit_skill_ids = request.args.get("unit_skill_ids", "")
        unit_skill_ids = [part.strip() for part in raw_unit_skill_ids.replace(",", ";").split(";") if part.strip()]

    try:
        response = get_rag_hint(
            nodes,
            skill_id=skill_id,
            family_id=family_id,
            question_context=question_context,
            question_text=question_text,
            unit_skill_ids=unit_skill_ids,
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": f"rag hint failure: {exc}"}), 500
    return jsonify(response)


@practice_bp.route('/api/adaptive/adv_rag_search', methods=['POST'])
@login_required
def api_adv_rag_search():
    """Advanced RAG hybrid search API."""
    data = request.get_json(silent=True) or {}
    query = (data.get('query') or '').strip()
    
    if not query:
        return jsonify({"results": [], "error": "請輸入問題"}), 400
        
    try:
        from core.advanced_rag_engine import adv_rag_search
        results = adv_rag_search(query, top_k=5)
        return jsonify({"results": results})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"results": [], "error": str(e)}), 500


@practice_bp.route('/api/adaptive/adv_rag_chat', methods=['POST'])
@login_required
def api_adv_rag_chat():
    """RAG + LLM chat API for generating hints/short lessons from retrieved materials."""
    data = request.get_json(silent=True) or {}
    query = (data.get('query') or '').strip()
    retrieved_skills = data.get('retrieved_skills') or []

    if not query:
        return jsonify({"reply": "請提供問題"}), 400

    try:
        from core.advanced_rag_engine import adv_rag_chat
        result = adv_rag_chat(query, retrieved_skills)
        return jsonify(result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"reply": f"AI 發生錯誤: {e}"}), 500
