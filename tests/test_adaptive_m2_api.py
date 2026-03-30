# -*- coding: utf-8 -*-

import os
import sys
import uuid

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from app import create_app
from core.adaptive.agent_skill_schema import SYSTEM_SKILL_TO_AGENT_SKILL
from core.adaptive.textbook_progression import load_textbook_progression
from models import AdaptiveLearningLog, User, db


TARGET_SKILL_ID = "jh_數學1上_FourArithmeticOperationsOfIntegers"
DEBUG_KEYS = [
    "selected_agent_skill",
    "selected_subskill",
    "selected_family_id",
    "selection_mode",
    "selection_debug",
    "fail_streak",
    "frustration_index",
]
ROUTING_SUMMARY_KEYS = [
    "total_routing_decisions",
    "ppo_routing_decisions",
    "fallback_routing_decisions",
    "remediation_entries",
    "successful_returns",
    "bridge_completions",
    "ppo_usage_rate",
    "return_success_rate",
]
ROUTING_TIMELINE_KEYS = [
    "step",
    "current_skill",
    "selected_agent_skill",
    "is_correct",
    "fail_streak",
    "frustration",
    "cross_skill_trigger",
    "allowed_actions",
    "ppo_action",
    "decision_source",
    "in_remediation",
    "remediation_step_count",
    "bridge_active",
    "final_route_reward",
]
ROUTING_TIMELINE_SUMMARY_KEYS = [
    "total_steps",
    "unique_skills_visited",
    "remediation_entered",
    "remediation_count",
    "return_count",
    "bridge_count",
    "final_skill",
    "ppo_decision_count",
    "fallback_decision_count",
    "total_route_reward",
    "avg_route_reward",
]


def _ensure_test_user():
    username = f"adaptive_m2_{uuid.uuid4().hex[:8]}"
    user = User(username=username, password_hash="test-hash", role="student")
    db.session.add(user)
    db.session.commit()
    return user


def _login(client, user_id: int):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True


def _assert_debug_fields(payload: dict):
    for key in DEBUG_KEYS:
        assert key in payload
    assert isinstance(payload["selection_debug"], dict)


def _assert_routing_summary_fields(summary: dict):
    for key in ROUTING_SUMMARY_KEYS:
        assert key in summary
    assert summary["total_routing_decisions"] >= 0
    assert summary["ppo_routing_decisions"] >= 0
    assert summary["fallback_routing_decisions"] >= 0
    assert summary["remediation_entries"] >= 0
    assert summary["successful_returns"] >= 0
    assert summary["bridge_completions"] >= 0
    assert 0.0 <= float(summary["ppo_usage_rate"]) <= 1.0
    assert 0.0 <= float(summary["return_success_rate"]) <= 1.0
    assert (
        int(summary["ppo_routing_decisions"]) + int(summary["fallback_routing_decisions"])
        == int(summary["total_routing_decisions"])
    )


def _assert_timeline_row_fields(row: dict):
    for key in ROUTING_TIMELINE_KEYS:
        assert key in row


def _assert_timeline_summary_fields(summary: dict):
    for key in ROUTING_TIMELINE_SUMMARY_KEYS:
        assert key in summary
    assert int(summary["total_steps"]) >= 0
    assert isinstance(summary["unique_skills_visited"], list)
    assert int(summary["remediation_count"]) >= 0
    assert int(summary["return_count"]) >= 0
    assert int(summary["bridge_count"]) >= 0
    assert int(summary["ppo_decision_count"]) >= 0
    assert int(summary["fallback_decision_count"]) >= 0
    assert (
        int(summary["ppo_decision_count"]) + int(summary["fallback_decision_count"])
        == int(summary["total_steps"])
    )


class _HistoryRow:
    def __init__(self, family_id: str, is_correct: bool):
        self.target_family_id = family_id
        self.is_correct = is_correct


def test_submit_bootstrap_returns_first_question():
    app = create_app()
    with app.app_context():
        user = _ensure_test_user()
        client = app.test_client()
        _login(client, user.id)

        response = client.post(
            "/api/adaptive/submit_and_get_next",
            json={"step_number": 0, "skill_id": TARGET_SKILL_ID},
        )
        assert response.status_code == 200
        payload = response.get_json()
        assert payload["session_id"]
        assert payload["step_number"] == 1
        assert payload["new_question_data"]["family_id"]
        assert payload["new_question_data"]["skill_id"] == TARGET_SKILL_ID


def test_assessment_completion_requires_all_polynomial_core_families():
    import core.adaptive.session_engine as engine

    poly_skill_id = next(
        key for key in SYSTEM_SKILL_TO_AGENT_SKILL.keys()
        if "FourArithmeticOperationsOfPolynomial" in key
    )
    textbook_cfg = load_textbook_progression(poly_skill_id)

    partial = engine._evaluate_unit_completion(
        mode="assessment",
        system_skill_id=poly_skill_id,
        textbook_cfg=textbook_cfg,
        history_rows=[_HistoryRow("F1", True), _HistoryRow("F2", True)],
        current_family_id="F2",
        last_is_correct=None,
        current_apr=0.98,
        answered_steps=6,
    )
    assert partial["unit_completed"] is False
    assert partial["used_apr_for_completion"] is False
    assert partial["required_core_families"] == ["F1", "F2", "F5", "F11", "F7", "F8", "F9", "F10"]
    assert partial["completed_core_families"] == ["F1", "F2"]

    still_incomplete = engine._evaluate_unit_completion(
        mode="assessment",
        system_skill_id=poly_skill_id,
        textbook_cfg=textbook_cfg,
        history_rows=[
            _HistoryRow("F1", True),
            _HistoryRow("F2", True),
            _HistoryRow("F5", True),
            _HistoryRow("F11", True),
        ],
        current_family_id="F11",
        last_is_correct=None,
        current_apr=0.98,
        answered_steps=8,
    )
    assert still_incomplete["unit_completed"] is False
    assert still_incomplete["completion_reason"] == "unit_completion_waiting_core_coverage"

    complete = engine._evaluate_unit_completion(
        mode="assessment",
        system_skill_id=poly_skill_id,
        textbook_cfg=textbook_cfg,
        history_rows=[
            _HistoryRow("F1", True),
            _HistoryRow("F2", True),
            _HistoryRow("F5", True),
            _HistoryRow("F11", True),
            _HistoryRow("F7", True),
            _HistoryRow("F8", True),
            _HistoryRow("F9", True),
            _HistoryRow("F10", True),
        ],
        current_family_id="F10",
        last_is_correct=None,
        current_apr=0.98,
        answered_steps=12,
    )
    assert complete["unit_completed"] is True
    assert complete["completion_reason"] == "completed_all_core_families"
    assert complete["used_apr_for_completion"] is False


def test_polynomial_assessment_all_correct_advances_past_f11(monkeypatch):
    import core.adaptive.session_engine as engine

    poly_skill_id = next(
        key for key in SYSTEM_SKILL_TO_AGENT_SKILL.keys()
        if "FourArithmeticOperationsOfPolynomial" in key
    )

    monkeypatch.setattr(
        engine,
        "_generate_question_payload",
        lambda entry, selected_subskill=None: {
            "skill_id": entry.skill_id,
            "family_id": entry.family_id,
            "question": f"{entry.family_id} question",
            "correct_answer": "1",
            "choices": ["1", "2", "3", "4"],
        },
    )

    app = create_app()
    with app.app_context():
        user = _ensure_test_user()
        client = app.test_client()
        _login(client, user.id)

        response = client.post(
            "/api/adaptive/submit_and_get_next",
            json={"step_number": 0, "skill_id": poly_skill_id, "mode": "assessment"},
        )
        assert response.status_code == 200
        payload = response.get_json()
        sid = payload["session_id"]
        seen_families = [payload["target_family_id"]]

        step = 1
        while not payload.get("completed", False) and step <= 12:
            response = client.post(
                "/api/adaptive/submit_and_get_next",
                json={
                    "session_id": sid,
                    "step_number": step,
                    "skill_id": poly_skill_id,
                    "mode": "assessment",
                    "is_correct": True,
                },
            )
            assert response.status_code == 200
            payload = response.get_json()
            if not payload.get("completed", False):
                seen_families.append(payload["target_family_id"])
            step += 1

        assert seen_families[:8] == ["F1", "F2", "F5", "F11", "F7", "F8", "F9", "F10"]
        assert payload["completed"] is True
        assert payload["assessment_completed"] is True
        assert payload["assessment_stop_reason"] == "completed_all_core_families"
        assert payload["completed_core_families"] == ["F1", "F2", "F5", "F11", "F7", "F8", "F9", "F10"]


def test_assessment_stops_at_teaching_remediation_trigger_without_entering_remediation(monkeypatch):
    import core.adaptive.session_engine as engine

    poly_skill_id = next(
        key for key in SYSTEM_SKILL_TO_AGENT_SKILL.keys()
        if "FourArithmeticOperationsOfPolynomial" in key
    )

    def _route_action(route_state, action_mask, model=None):
        if action_mask.get("remediate", False):
            return "remediate", [0.0, 1.0, -1.0], 1, "ppo"
        return "stay", [1.0, 0.0, -1.0], 0, "ppo"

    monkeypatch.setattr(engine, "select_route_action_with_ppo", _route_action)

    app = create_app()
    with app.app_context():
        user = _ensure_test_user()
        client = app.test_client()
        _login(client, user.id)

        first = client.post(
            "/api/adaptive/submit_and_get_next",
            json={"step_number": 0, "skill_id": poly_skill_id, "mode": "assessment"},
        )
        assert first.status_code == 200
        sid = first.get_json()["session_id"]

        client.post(
            "/api/adaptive/submit_and_get_next",
            json={"session_id": sid, "step_number": 1, "skill_id": poly_skill_id, "mode": "assessment", "user_answer": "__wrong__"},
        )
        final_response = client.post(
            "/api/adaptive/submit_and_get_next",
            json={"session_id": sid, "step_number": 2, "skill_id": poly_skill_id, "mode": "assessment", "user_answer": "__wrong__"},
        )
        assert final_response.status_code == 200
        payload = final_response.get_json()
        assert payload["completed"] is True
        assert payload["assessment_completed"] is True
        assert payload["assessment_stop_reason"] == "stable_breakpoint_detected"
        assert payload["stable_breakpoint_detected"] is True
        assert payload["used_apr_for_completion"] is False
        assert payload["unit_completed"] is False
        assert payload["local_remediation_completed"] is False
        assert bool((payload.get("routing_state") or {}).get("in_remediation", False)) is False
        assert "correct_answer" not in payload["new_question_data"]
        assert "answer" not in payload["new_question_data"]


def test_submit_second_step_autojudges_and_writes_log():
    app = create_app()
    with app.app_context():
        user = _ensure_test_user()
        client = app.test_client()
        _login(client, user.id)

        first = client.post(
            "/api/adaptive/submit_and_get_next",
            json={"step_number": 0, "skill_id": TARGET_SKILL_ID},
        ).get_json()

        with client.session_transaction() as sess:
            runtime = sess["adaptive_runtime"][first["session_id"]]
            correct_answer = runtime["correct_answer"]

        second = client.post(
            "/api/adaptive/submit_and_get_next",
            json={
                "session_id": first["session_id"],
                "step_number": 1,
                "user_answer": correct_answer,
                "skill_id": TARGET_SKILL_ID,
            },
        )
        assert second.status_code == 200
        payload = second.get_json()
        assert payload["frustration_index"] == 0
        assert payload["ppo_strategy"] in [0, 1, 2, 3]
        _assert_debug_fields(payload)

        row = (
            db.session.query(AdaptiveLearningLog)
            .filter_by(student_id=user.id, session_id=first["session_id"])
            .order_by(AdaptiveLearningLog.log_id.desc())
            .first()
        )
        assert row is not None
        assert row.step_number == 2
        assert row.is_correct is True


def test_submit_completed_branch_also_contains_debug_fields():
    app = create_app()
    with app.app_context():
        user = _ensure_test_user()
        client = app.test_client()
        _login(client, user.id)

        response = client.post(
            "/api/adaptive/submit_and_get_next",
            json={
                "session_id": f"s_{uuid.uuid4().hex[:8]}",
                "step_number": 8,
                "is_correct": True,
                "skill_id": TARGET_SKILL_ID,
                "last_family_id": "I1",
                "last_subskills": ["sign_handling"],
            },
        )
        assert response.status_code == 200
        payload = response.get_json()
        assert payload["completed"] is True
        _assert_debug_fields(payload)


def test_submit_review_branch_contains_debug_fields():
    app = create_app()
    with app.app_context():
        user = _ensure_test_user()
        client = app.test_client()
        _login(client, user.id)

        session_id = f"s_{uuid.uuid4().hex[:8]}"
        existing = AdaptiveLearningLog(
            student_id=user.id,
            session_id=session_id,
            step_number=1,
            target_family_id="I1",
            target_subskills='["sign_handling"]',
            is_correct=False,
            current_apr=0.42,
            ppo_strategy=1,
            frustration_index=2,
            execution_latency=1,
        )
        db.session.add(existing)
        db.session.commit()

        response = client.post(
            "/api/adaptive/submit_and_get_next",
            json={
                "session_id": session_id,
                "step_number": 1,
                "is_correct": False,
                "skill_id": TARGET_SKILL_ID,
                "last_family_id": "I1",
                "last_subskills": ["sign_handling"],
            },
        )
        assert response.status_code == 200
        payload = response.get_json()
        _assert_debug_fields(payload)
        assert payload["ppo_strategy"] == 3


def test_submit_policy_log_with_none_values_does_not_crash(monkeypatch):
    import core.adaptive.session_engine as engine

    monkeypatch.setattr(
        engine,
        "select_route_action_with_ppo",
        lambda route_state, action_mask, model=None: (None, None, None, "ppo_error"),
    )
    monkeypatch.setattr(
        engine,
        "select_route_action_heuristic",
        lambda route_state, action_mask: ("stay", {"mode": "mock_none"}),
    )

    app = create_app()
    with app.app_context():
        user = _ensure_test_user()
        client = app.test_client()
        _login(client, user.id)
        response = client.post(
            "/api/adaptive/submit_and_get_next",
            json={"step_number": 0, "skill_id": TARGET_SKILL_ID},
        )
        assert response.status_code == 200
        payload = response.get_json()
        _assert_debug_fields(payload)


def test_rag_hint_returns_html():
    app = create_app()
    with app.app_context():
        user = _ensure_test_user()
        client = app.test_client()
        _login(client, user.id)

        response = client.get(
            "/api/adaptive/rag_hint?subskill_nodes=divide_terms&subskill_nodes=conjugate_rationalize"
        )
        assert response.status_code == 200
        payload = response.get_json()
        assert "hint_html" in payload
        assert "divide_terms" in payload["hint_html"]


def test_e2e_cross_skill_remediation_return_bridge_then_normal(monkeypatch):
    import core.adaptive.session_engine as engine

    poly_skill_id = next(
        key for key in SYSTEM_SKILL_TO_AGENT_SKILL.keys()
        if "FourArithmeticOperationsOfPolynomial" in key
    )

    def _mock_route_action(route_state, action_mask, model=None):
        ctx = dict(route_state.get("routing_context") or {})
        in_remediation = bool(ctx.get("in_remediation", 0))
        rem_steps = int(ctx.get("remediation_step_count", 0) or 0)
        if (not in_remediation) and action_mask.get("remediate", False):
            return "remediate", [0.1, 0.9, -0.2], 1, "ppo"
        if in_remediation and action_mask.get("return", False) and rem_steps >= 2:
            return "return", [0.0, -0.5, 1.0], 2, "ppo"
        return "stay", [1.0, -0.1, -0.2], 0, "ppo"

    monkeypatch.setattr(engine, "select_route_action_with_ppo", _mock_route_action)

    app = create_app()
    with app.app_context():
        user = _ensure_test_user()
        client = app.test_client()
        _login(client, user.id)

        # Step 0 bootstrap: polynomial start
        first = client.post(
            "/api/adaptive/submit_and_get_next",
            json={"step_number": 0, "skill_id": poly_skill_id},
        )
        assert first.status_code == 200
        p0 = first.get_json()
        sid = p0["session_id"]

        # Step 1 wrong
        s1 = client.post(
            "/api/adaptive/submit_and_get_next",
            json={
                "session_id": sid,
                "step_number": 1,
                "skill_id": poly_skill_id,
                "user_answer": "__wrong__",
            },
        )
        assert s1.status_code == 200

        # Step 2 wrong -> trigger diagnosis/remediate
        s2 = client.post(
            "/api/adaptive/submit_and_get_next",
            json={
                "session_id": sid,
                "step_number": 2,
                "skill_id": poly_skill_id,
                "user_answer": "__wrong__",
            },
        )
        assert s2.status_code == 200
        p2 = s2.get_json()
        dbg2 = p2["selection_debug"]
        assert dbg2.get("cross_skill_trigger") is True
        assert "remediate" in (dbg2.get("route_debug", {}).get("action_mask", ["remediate"]) or ["remediate"])
        assert p2["selected_agent_skill"] == "integer_arithmetic"
        assert p2["routing_state"]["in_remediation"] is True
        assert int(p2["routing_state"]["steps_taken"]) == 0

        # Step 3 correct in remediation
        s3 = client.post(
            "/api/adaptive/submit_and_get_next",
            json={
                "session_id": sid,
                "step_number": 3,
                "skill_id": poly_skill_id,
                "is_correct": True,
                "user_answer": "__mock_correct__",
            },
        )
        assert s3.status_code == 200
        p3 = s3.get_json()
        assert p3["routing_state"]["in_remediation"] is True
        assert int(p3["routing_state"]["steps_taken"]) == 1
        assert p3["selected_agent_skill"] == "integer_arithmetic"

        # Step 4 correct in remediation -> return
        s4 = client.post(
            "/api/adaptive/submit_and_get_next",
            json={
                "session_id": sid,
                "step_number": 4,
                "skill_id": poly_skill_id,
                "is_correct": True,
                "user_answer": "__mock_correct__",
            },
        )
        assert s4.status_code == 200
        p4 = s4.get_json()
        assert p4["routing_state"]["in_remediation"] is False
        assert int(p4["routing_state"]["bridge_remaining"]) >= 1
        assert p4["selected_agent_skill"] == "polynomial_arithmetic"

        # Step 5 bridge active
        s5 = client.post(
            "/api/adaptive/submit_and_get_next",
            json={
                "session_id": sid,
                "step_number": 5,
                "skill_id": poly_skill_id,
                "is_correct": True,
                "user_answer": "__mock_correct__",
            },
        )
        assert s5.status_code == 200
        p5 = s5.get_json()
        assert p5["selection_debug"].get("bridge_active") is True
        assert p5["selected_agent_skill"] == "polynomial_arithmetic"

        # Step 6 bridge end -> normal progression restored
        s6 = client.post(
            "/api/adaptive/submit_and_get_next",
            json={
                "session_id": sid,
                "step_number": 6,
                "skill_id": poly_skill_id,
                "is_correct": True,
                "user_answer": "__mock_correct__",
            },
        )
        assert s6.status_code == 200
        p6 = s6.get_json()
        assert p6["selected_agent_skill"] == "polynomial_arithmetic"
        assert int(p6["routing_state"].get("bridge_remaining", 0) or 0) == 0
        assert p6["selection_debug"].get("bridge_active") in [False, None]


def test_no_cross_skill_when_trigger_not_met(monkeypatch):
    import core.adaptive.session_engine as engine

    poly_skill_id = next(
        key for key in SYSTEM_SKILL_TO_AGENT_SKILL.keys()
        if "FourArithmeticOperationsOfPolynomial" in key
    )

    monkeypatch.setattr(
        engine,
        "rag_diagnose",
        lambda **kwargs: {
            "error_concept": "basic_arithmetic_instability",
            "retrieval_confidence": 0.55,
            "diagnosis_confidence": 0.60,  # below threshold
            "suggested_prereq_skill": "integer_arithmetic",
            "suggested_prereq_subskill": "add_sub",
            "route_type": "rescue",
        },
    )

    app = create_app()
    with app.app_context():
        user = _ensure_test_user()
        client = app.test_client()
        _login(client, user.id)

        # bootstrap
        first = client.post(
            "/api/adaptive/submit_and_get_next",
            json={"step_number": 0, "skill_id": poly_skill_id},
        ).get_json()
        sid = first["session_id"]
        # low trigger inputs: first wrong only
        resp = client.post(
            "/api/adaptive/submit_and_get_next",
            json={
                "session_id": sid,
                "step_number": 1,
                "skill_id": poly_skill_id,
                "user_answer": "__wrong__",
            },
        )
        assert resp.status_code == 200
        payload = resp.get_json()
        dbg = payload["selection_debug"]
        assert dbg.get("cross_skill_trigger") is False
        action_mask = (dbg.get("route_debug", {}).get("action_mask", {}) or {})
        assert action_mask.get("remediate") in [False, None]
        assert payload["selected_agent_skill"] == "polynomial_arithmetic"


def test_remediation_lock_blocks_extra_routing(monkeypatch):
    import core.adaptive.session_engine as engine

    poly_skill_id = next(
        key for key in SYSTEM_SKILL_TO_AGENT_SKILL.keys()
        if "FourArithmeticOperationsOfPolynomial" in key
    )

    def _always_try_remediate(route_state, action_mask, model=None):
        if action_mask.get("remediate", False):
            return "remediate", [0.1, 0.9, -0.1], 1, "ppo"
        return "stay", [1.0, -1.0, -1.0], 0, "ppo"

    monkeypatch.setattr(engine, "select_route_action_with_ppo", _always_try_remediate)

    app = create_app()
    with app.app_context():
        user = _ensure_test_user()
        client = app.test_client()
        _login(client, user.id)

        first = client.post(
            "/api/adaptive/submit_and_get_next",
            json={"step_number": 0, "skill_id": poly_skill_id},
        ).get_json()
        sid = first["session_id"]

        # wrong, wrong => remediation entry
        client.post(
            "/api/adaptive/submit_and_get_next",
            json={"session_id": sid, "step_number": 1, "skill_id": poly_skill_id, "user_answer": "__wrong__"},
        )
        r2 = client.post(
            "/api/adaptive/submit_and_get_next",
            json={"session_id": sid, "step_number": 2, "skill_id": poly_skill_id, "user_answer": "__wrong__"},
        )
        p2 = r2.get_json()
        assert p2["routing_state"]["in_remediation"] is True
        assert int(p2["routing_state"]["steps_taken"]) == 0

        # in remediation step1: lock should force stay only
        r3 = client.post(
            "/api/adaptive/submit_and_get_next",
            json={"session_id": sid, "step_number": 3, "skill_id": poly_skill_id, "is_correct": True},
        )
        p3 = r3.get_json()
        action_mask = p3["selection_debug"]["route_debug"]["action_mask"]
        assert action_mask.get("stay") is True
        assert action_mask.get("return") in [False, None]
        assert action_mask.get("remediate") in [False, None]
        assert p3["selected_agent_skill"] == "integer_arithmetic"
        assert int(p3["routing_state"]["steps_taken"]) == 1


def test_forced_return_at_lock_max_steps(monkeypatch):
    import core.adaptive.session_engine as engine
    from core.adaptive import routing as routing_mod

    poly_skill_id = next(
        key for key in SYSTEM_SKILL_TO_AGENT_SKILL.keys()
        if "FourArithmeticOperationsOfPolynomial" in key
    )

    # force return only when mask allows; otherwise stay
    def _route_action(route_state, action_mask, model=None):
        if action_mask.get("return", False):
            return "return", [0.0, -0.5, 1.0], 2, "ppo"
        if action_mask.get("remediate", False):
            return "remediate", [0.0, 1.0, -1.0], 1, "ppo"
        return "stay", [1.0, 0.0, -1.0], 0, "ppo"

    # force return readiness by lock max
    monkeypatch.setattr(
        engine,
        "should_return_from_remediation",
        lambda s: (int((s or {}).get("steps_taken", 0) or 0) >= 4, "forced_by_lock_max" if int((s or {}).get("steps_taken", 0) or 0) >= 4 else "not_ready"),
    )
    monkeypatch.setattr(engine, "select_route_action_with_ppo", _route_action)

    app = create_app()
    with app.app_context():
        user = _ensure_test_user()
        client = app.test_client()
        _login(client, user.id)

        first = client.post(
            "/api/adaptive/submit_and_get_next",
            json={"step_number": 0, "skill_id": poly_skill_id},
        ).get_json()
        sid = first["session_id"]

        client.post("/api/adaptive/submit_and_get_next", json={"session_id": sid, "step_number": 1, "skill_id": poly_skill_id, "user_answer": "__wrong__"})
        p2 = client.post("/api/adaptive/submit_and_get_next", json={"session_id": sid, "step_number": 2, "skill_id": poly_skill_id, "user_answer": "__wrong__"}).get_json()
        assert p2["routing_state"]["in_remediation"] is True

        # advance remediation steps to lock_max
        final_payload = None
        for step in range(3, 11):
            final_payload = client.post(
                "/api/adaptive/submit_and_get_next",
                json={"session_id": sid, "step_number": step, "skill_id": poly_skill_id, "is_correct": False},
            ).get_json()
            if final_payload["routing_state"]["in_remediation"] is False:
                break

        assert final_payload is not None
        assert final_payload["routing_state"]["in_remediation"] is False
        assert final_payload["selected_agent_skill"] == "polynomial_arithmetic"
        assert final_payload["selection_debug"]["decision_source"] in ["ppo", "ppo_error_fallback", "heuristic_fallback"]


def test_bridge_state_clears_after_completion(monkeypatch):
    import core.adaptive.session_engine as engine

    poly_skill_id = next(
        key for key in SYSTEM_SKILL_TO_AGENT_SKILL.keys()
        if "FourArithmeticOperationsOfPolynomial" in key
    )

    def _route_action(route_state, action_mask, model=None):
        ctx = dict(route_state.get("routing_context") or {})
        in_remediation = bool(ctx.get("in_remediation", 0))
        rem_steps = int(ctx.get("remediation_step_count", 0) or 0)
        if (not in_remediation) and action_mask.get("remediate", False):
            return "remediate", [0.0, 1.0, -1.0], 1, "ppo"
        if in_remediation and action_mask.get("return", False) and rem_steps >= 2:
            return "return", [0.0, -1.0, 1.0], 2, "ppo"
        return "stay", [1.0, -1.0, -1.0], 0, "ppo"

    monkeypatch.setattr(engine, "select_route_action_with_ppo", _route_action)

    app = create_app()
    with app.app_context():
        user = _ensure_test_user()
        client = app.test_client()
        _login(client, user.id)

        sid = client.post("/api/adaptive/submit_and_get_next", json={"step_number": 0, "skill_id": poly_skill_id}).get_json()["session_id"]
        client.post("/api/adaptive/submit_and_get_next", json={"session_id": sid, "step_number": 1, "skill_id": poly_skill_id, "user_answer": "__wrong__"})
        client.post("/api/adaptive/submit_and_get_next", json={"session_id": sid, "step_number": 2, "skill_id": poly_skill_id, "user_answer": "__wrong__"})
        client.post("/api/adaptive/submit_and_get_next", json={"session_id": sid, "step_number": 3, "skill_id": poly_skill_id, "is_correct": True})
        p4 = client.post("/api/adaptive/submit_and_get_next", json={"session_id": sid, "step_number": 4, "skill_id": poly_skill_id, "is_correct": True}).get_json()
        assert p4["selection_debug"].get("bridge_active") is True

        p5 = client.post("/api/adaptive/submit_and_get_next", json={"session_id": sid, "step_number": 5, "skill_id": poly_skill_id, "is_correct": True}).get_json()
        p6 = client.post("/api/adaptive/submit_and_get_next", json={"session_id": sid, "step_number": 6, "skill_id": poly_skill_id, "is_correct": True}).get_json()
        assert int(p6["routing_state"].get("bridge_remaining", 0) or 0) == 0
        assert p6["selection_debug"].get("bridge_active") in [False, None]
        assert p6["selected_agent_skill"] == "polynomial_arithmetic"


def test_routing_summary_available_in_ongoing_and_completed_response():
    app = create_app()
    with app.app_context():
        user = _ensure_test_user()
        client = app.test_client()
        _login(client, user.id)

        first = client.post(
            "/api/adaptive/submit_and_get_next",
            json={"step_number": 0, "skill_id": TARGET_SKILL_ID},
        )
        assert first.status_code == 200
        p1 = first.get_json()
        assert "routing_summary" in p1
        _assert_routing_summary_fields(p1["routing_summary"])
        assert p1["selection_debug"].get("routing_summary") == p1["routing_summary"]

        sid = p1["session_id"]
        second = client.post(
            "/api/adaptive/submit_and_get_next",
            json={
                "session_id": sid,
                "step_number": 1,
                "skill_id": TARGET_SKILL_ID,
                "user_answer": "__wrong__",
            },
        )
        assert second.status_code == 200
        p2 = second.get_json()
        _assert_routing_summary_fields(p2["routing_summary"])
        assert p2["routing_summary"]["total_routing_decisions"] >= 2
        assert p2["selection_debug"].get("routing_summary") == p2["routing_summary"]

        done = client.post(
            "/api/adaptive/submit_and_get_next",
            json={
                "session_id": sid,
                "step_number": 8,
                "skill_id": TARGET_SKILL_ID,
                "is_correct": True,
            },
        )
        assert done.status_code == 200
        p_done = done.get_json()
        assert p_done["completed"] is True
        _assert_routing_summary_fields(p_done["routing_summary"])
        assert p_done["selection_debug"].get("routing_summary") == p_done["routing_summary"]


def test_routing_timeline_export_contains_required_fields():
    app = create_app()
    with app.app_context():
        user = _ensure_test_user()
        client = app.test_client()
        _login(client, user.id)

        first = client.post(
            "/api/adaptive/submit_and_get_next",
            json={"step_number": 0, "skill_id": TARGET_SKILL_ID},
        )
        assert first.status_code == 200
        p1 = first.get_json()
        assert "routing_timeline" in p1
        assert isinstance(p1["routing_timeline"], list)
        assert len(p1["routing_timeline"]) >= 1
        _assert_timeline_row_fields(p1["routing_timeline"][-1])

        sid = p1["session_id"]
        second = client.post(
            "/api/adaptive/submit_and_get_next",
            json={
                "session_id": sid,
                "step_number": 1,
                "skill_id": TARGET_SKILL_ID,
                "user_answer": "__wrong__",
            },
        )
        assert second.status_code == 200
        p2 = second.get_json()
        assert isinstance(p2.get("routing_timeline"), list)
        assert len(p2["routing_timeline"]) >= len(p1["routing_timeline"])
        _assert_timeline_row_fields(p2["routing_timeline"][-1])
        assert p2["selection_debug"].get("routing_timeline") == p2["routing_timeline"]


def test_routing_timeline_summary_exists_and_is_reasonable():
    app = create_app()
    with app.app_context():
        user = _ensure_test_user()
        client = app.test_client()
        _login(client, user.id)

        first = client.post(
            "/api/adaptive/submit_and_get_next",
            json={"step_number": 0, "skill_id": TARGET_SKILL_ID},
        )
        assert first.status_code == 200
        p1 = first.get_json()
        assert "routing_timeline_summary" in p1
        _assert_timeline_summary_fields(p1["routing_timeline_summary"])
        assert p1["selection_debug"].get("routing_timeline_summary") == p1["routing_timeline_summary"]

        sid = p1["session_id"]
        second = client.post(
            "/api/adaptive/submit_and_get_next",
            json={
                "session_id": sid,
                "step_number": 1,
                "skill_id": TARGET_SKILL_ID,
                "user_answer": "__wrong__",
            },
        )
        assert second.status_code == 200
        p2 = second.get_json()
        _assert_timeline_summary_fields(p2["routing_timeline_summary"])
        assert int(p2["routing_timeline_summary"]["total_steps"]) >= int(
            p1["routing_timeline_summary"]["total_steps"]
        )
