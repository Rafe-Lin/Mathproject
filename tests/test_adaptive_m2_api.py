# -*- coding: utf-8 -*-

import os
import sys
import uuid

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from app import create_app
from models import AdaptiveLearningLog, User, db


TARGET_SKILL_ID = "jh_數學1上_FourArithmeticOperationsOfIntegers"


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

        row = (
            db.session.query(AdaptiveLearningLog)
            .filter_by(student_id=user.id, session_id=first["session_id"])
            .order_by(AdaptiveLearningLog.log_id.desc())
            .first()
        )
        assert row is not None
        assert row.step_number == 2
        assert row.is_correct is True


def test_rag_hint_returns_html():
    app = create_app()
    with app.app_context():
        user = _ensure_test_user()
        client = app.test_client()
        _login(client, user.id)

        response = client.get("/api/adaptive/rag_hint?subskill_nodes=divide_terms&subskill_nodes=conjugate_rationalize")
        assert response.status_code == 200
        payload = response.get_json()
        assert "hint_html" in payload
        assert "divide_terms" in payload["hint_html"]
