# -*- coding: utf-8 -*-
from __future__ import annotations

from flask import jsonify, request, session
from flask_login import current_user, login_required

from core.adaptive.judge import judge_answer
from . import practice_bp
from core.adaptive.session_engine import get_rag_hint, submit_and_get_next


def _adaptive_runtime_store() -> dict:
    store = session.get("adaptive_runtime", {})
    if not isinstance(store, dict):
        store = {}
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

        if runtime:
            payload["last_family_id"] = runtime.get("family_id", payload.get("last_family_id"))
            payload["last_subskills"] = runtime.get("subskill_nodes", payload.get("last_subskills"))
            if "user_answer" in payload and "is_correct" not in payload:
                payload["is_correct"] = judge_answer(payload.get("user_answer"), runtime.get("correct_answer"))

        response = submit_and_get_next(payload)
        next_session_id = response["session_id"]
        if response.get("completed"):
            runtime_store.pop(next_session_id, None)
        else:
            runtime_store[next_session_id] = {
                "family_id": response["target_family_id"],
                "subskill_nodes": response["target_subskills"],
                "correct_answer": response["new_question_data"].get("correct_answer") or response["new_question_data"].get("answer") or "",
                "question_text": response["new_question_data"].get("question_text") or response["new_question_data"].get("question") or "",
            }
        session["adaptive_runtime"] = runtime_store
        session.modified = True
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": f"adaptive engine failure: {exc}"}), 500
    return jsonify(_response_for_frontend(response))


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
