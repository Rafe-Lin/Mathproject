from __future__ import annotations

from core.adaptive.skill_policy_trainer import AdaptiveSkillPolicyEnv, SKILL_LABELS


def _seed_student(env: AdaptiveSkillPolicyEnv) -> None:
    env.reset()
    assert env.student is not None
    env.student.mastery_by_skill = {skill: 0.4 for skill in SKILL_LABELS}
    env.student.fail_streak = 2.0
    env.student.same_skill_streak = 1.0
    env.student.last_skill_idx = 3
    env.student.last_is_correct = 0.0


def _install_deterministic_step(env: AdaptiveSkillPolicyEnv, delta: float = 0.03) -> None:
    def fake_step_direct(action_idx: int) -> tuple[bool, float]:
        assert env.student is not None
        skill = SKILL_LABELS[action_idx]
        env.student.mastery_by_skill[skill] = min(1.0, env.student.mastery_by_skill[skill] + delta)
        env.student.last_skill_idx = action_idx
        env.student.last_is_correct = 1.0
        env.student.fail_streak = 0.0
        env.student.same_skill_streak = 1.0
        return True, 0.5

    env.step_direct = fake_step_direct  # type: ignore[method-assign]


def test_ab2_uses_fixed_remediation_length_then_returns_to_parent():
    env = AdaptiveSkillPolicyEnv(
        max_steps=5,
        seed=7,
        return_mode="ab2",
        fixed_remediation_steps=2,
    )
    _seed_student(env)
    _install_deterministic_step(env)

    _, _, _, first_info = env.step(0)
    assert first_info["entered_remediation"] is True
    assert first_info["in_remediation"] is True
    assert first_info["parent_skill"] == 3
    assert first_info["remediation_skill"] == 0
    assert first_info["final_target_skill"] == 0
    assert first_info["remediation_step_count"] == 1

    _, _, _, second_info = env.step(2)
    assert second_info["in_remediation"] is True
    assert second_info["final_target_skill"] == 0
    assert second_info["remediation_step_count"] == 2

    _, _, _, third_info = env.step(1)
    assert third_info["returned_to_parent"] is True
    assert third_info["in_remediation"] is False
    assert third_info["final_target_skill"] == 3


def test_ab3_returns_early_after_recent_correct_streak_and_mastery_growth():
    env = AdaptiveSkillPolicyEnv(
        max_steps=5,
        seed=11,
        return_mode="ab3",
        min_remediation_steps=1,
        recent_correct_streak_threshold=2,
        mastery_growth_delta_threshold=0.0,
    )
    _seed_student(env)
    _install_deterministic_step(env)

    _, _, _, first_info = env.step(0)
    assert first_info["entered_remediation"] is True
    assert first_info["recent_correct_streak"] == 1
    assert first_info["mastery_growth_delta"] > 0.0

    _, _, _, second_info = env.step(2)
    assert second_info["in_remediation"] is True
    assert second_info["final_target_skill"] == 0
    assert second_info["recent_correct_streak"] == 2

    _, _, _, third_info = env.step(1)
    assert third_info["returned_to_parent"] is True
    assert third_info["parent_skill"] == 3
    assert third_info["remediation_skill"] == 0
    assert third_info["final_target_skill"] == 3
    assert third_info["return_mode"] == "ab3"
