from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.adaptive.agent_skill_schema import (
    AGENT_SKILL_FRACTION_ARITHMETIC,
    AGENT_SKILL_INTEGER_ARITHMETIC,
)
from core.adaptive.ppo_adapter import select_agent_skill
from core.adaptive.state_builder import build_agent_state
from core.adaptive.subskill_selector import select_subskill


def test_build_agent_state_fixed_vector_length():
    state = build_agent_state(
        session={"session_id": "s1"},
        history=[],
        system_skill_id="jh_數學1上_FourArithmeticOperationsOfIntegers",
        current_apr=0.52,
        frustration_index=1,
        last_is_correct=True,
    )
    assert "state_vector" in state
    assert len(state["state_vector"]) == 8
    assert state["mastery_by_skill"][AGENT_SKILL_INTEGER_ARITHMETIC] == 0.52


def test_select_agent_skill_prefers_weaker_mastery():
    agent_state = {
        "mastery_by_skill": {
            "integer_arithmetic": 0.7,
            "fraction_arithmetic": 0.2,
            "radical_arithmetic": 0.5,
            "polynomial_arithmetic": 0.6,
        },
        "frustration_index": 0,
        "same_skill_streak": 0,
        "system_skill_id": "jh_數學1上_FourArithmeticOperationsOfIntegers",
    }
    selected, debug = select_agent_skill(agent_state)
    assert selected == AGENT_SKILL_FRACTION_ARITHMETIC
    assert debug["selection_mode"] == "weakest_mastery"


def test_select_subskill_error_mapping():
    subskill, debug = select_subskill(
        AGENT_SKILL_INTEGER_ARITHMETIC,
        session={},
        history=[],
        diagnostics={"last_error_type": "sign_error"},
    )
    assert subskill == "sign_handling"
    assert debug["mode"] == "error_type_mapping"
