from __future__ import annotations

from core.adaptive.ppo_adapter import (
    select_agent_skill_heuristic,
    select_agent_skill_with_ppo,
)


class DummyPolicy:
    def __init__(self, logits):
        self._logits = logits

    def predict_logits(self, state_vector):
        return list(self._logits)


def _agent_state():
    return {
        "state_vector": [0.1, 0.2, 0.3, 0.4, 0.1, 0.0, 0.0, 1.0],
        "mastery_by_skill": {
            "integer_arithmetic": 0.4,
            "fraction_arithmetic": 0.7,
            "radical_arithmetic": 0.8,
            "polynomial_arithmetic": 0.9,
        },
        "frustration_index": 0,
        "same_skill_streak": 0,
        "system_skill_id": "jh_數學1上_FourArithmeticOperationsOfIntegers",
    }


def test_phase2_case1_ppo_selects_integer():
    selected, logits, action_idx, source = select_agent_skill_with_ppo(
        agent_state=_agent_state(),
        allowed_agent_skills=[
            "integer_arithmetic",
            "fraction_arithmetic",
            "radical_arithmetic",
            "polynomial_arithmetic",
        ],
        model=DummyPolicy([9.0, 1.0, 0.5, 0.2]),
    )
    assert source == "ppo"
    assert selected == "integer_arithmetic"
    assert action_idx == 0
    assert logits is not None


def test_phase2_case2_mask_forces_integer():
    selected, logits, action_idx, source = select_agent_skill_with_ppo(
        agent_state=_agent_state(),
        allowed_agent_skills=["integer_arithmetic"],
        model=DummyPolicy([0.1, 9.0, 7.0, 8.0]),
    )
    assert source == "ppo"
    assert selected == "integer_arithmetic"
    assert action_idx == 0
    assert logits is not None


def test_phase2_case3_ppo_error_fallback_to_heuristic():
    import os
    os.environ["ADAPTIVE_PPO_MODEL_PATH"] = "__missing_checkpoint__.pt"
    selected, logits, action_idx, source = select_agent_skill_with_ppo(
        agent_state=_agent_state(),
        allowed_agent_skills=["integer_arithmetic", "fraction_arithmetic"],
        model=None,  # simulate model missing/load failure path
    )
    assert selected is None
    assert logits is None
    assert action_idx is None
    assert source == "ppo_error"

    selected_h, debug_h = select_agent_skill_heuristic(
        agent_state=_agent_state(),
        allowed_agent_skills=["integer_arithmetic", "fraction_arithmetic"],
    )
    assert selected_h == "integer_arithmetic"
    assert debug_h["selection_mode"] == "weakest_mastery"
    os.environ.pop("ADAPTIVE_PPO_MODEL_PATH", None)
