from __future__ import annotations

from pathlib import Path

import pytest

from core.adaptive.ablation_experiment import (
    AB1Policy,
    AB2Policy,
    AB3Policy,
    AbilityVector,
    DiagnosisResult,
    ExperimentConfig,
    FixedSubskillDiagnosis,
    Question,
    SubskillKnowledgeBase,
    StudentState,
    compute_effective_ability,
    map_subskill_to_state_key,
    probability_correct,
    update_deltas,
)


def test_polynomial_effective_ability_uses_integer_transfer():
    abilities = AbilityVector(
        int_sign_handling=0.4,
        int_mul_div=0.6,
        fraction=0.2,
        radical=0.1,
        polynomial_core=0.8,
        poly_sign_distribution_mastery=0.7,
        poly_expand_binomial_mastery=0.5,
    )
    sign_q = Question("q1", "polynomial", "poly.sign_distribution", 0.6, "polynomial_sign_error")
    expand_q = Question("q2", "polynomial", "poly.expand_binomial", 0.6, "polynomial_expand_error")
    like_q = Question("q3", "polynomial", "poly.combine_like_terms", 0.6, "polynomial_like_terms_error")
    assert compute_effective_ability(abilities, sign_q) == pytest.approx(0.595)
    assert compute_effective_ability(abilities, expand_q) == pytest.approx(0.54)
    assert compute_effective_ability(abilities, like_q) == pytest.approx(0.72)


def test_probability_correct_matches_irt_formula():
    probability = probability_correct(a_eff=0.7, difficulty=0.5)
    assert round(probability, 6) == round(1.0 / (1.0 + 2.718281828459045 ** (-1.2)), 6)


def test_update_deltas_apply_primary_and_transfer_weights():
    config = ExperimentConfig()
    deltas = update_deltas(
        Question("q1", "integer", "int.sign_handling", 0.5),
        difficulty=0.5,
        correct=True,
        config=config,
    )
    expected_base = 0.08 * (0.8 + 0.4 * 0.5) * 1.0
    assert deltas["int_sign_handling"] == expected_base
    assert deltas["poly_sign_distribution_mastery"] == expected_base * 0.2
    assert deltas["polynomial_core"] == expected_base * 0.05
    assert deltas["fraction"] == 0.0
    assert deltas["radical"] == 0.0


def test_ab1_always_targets_polynomial():
    policy = AB1Policy()
    state = StudentState(
        abilities=AbilityVector(0.5, 0.5, 0.3, 0.1, 0.5, 0.5, 0.5)
    )
    diagnosis = DiagnosisResult(
        route_type="remediate",
        suggested_skill="integer",
        failed_subskill="poly.sign_distribution",
        remediation_target_subskill="int.sign_handling",
        reason="two_consecutive_polynomial_failures",
        confidence=1.0,
    )
    decision = policy.decide(state=state, diagnosis=diagnosis, step=3)
    assert decision.next_skill == "polynomial"
    assert decision.action == "target_only"


def test_ab2_enters_fixed_three_step_remediation_then_returns():
    policy = AB2Policy()
    state = StudentState(abilities=AbilityVector(0.4, 0.4, 0.3, 0.1, 0.5, 0.5, 0.5), fail_streak_polynomial=2)
    diagnosis = DiagnosisResult(
        route_type="remediate",
        suggested_skill="integer",
        failed_subskill="poly.sign_distribution",
        remediation_target_subskill="int.sign_handling",
        reason="two_consecutive_polynomial_failures",
        confidence=1.0,
    )
    first = policy.decide(state=state, diagnosis=diagnosis, step=1)
    assert first.next_skill == "integer"
    assert first.metadata["fixed_difficulty"] == 0.6
    assert state.remediation_active is True

    state.remediation_steps_taken = 1
    second = policy.decide(state=state, diagnosis=diagnosis, step=2)
    assert second.next_skill == "integer"
    assert second.metadata["fixed_difficulty"] == 0.6

    state.remediation_steps_taken = 2
    third = policy.decide(state=state, diagnosis=diagnosis, step=3)
    assert third.next_skill == "integer"
    assert third.metadata["fixed_difficulty"] == 0.6

    state.remediation_steps_taken = 3
    fourth = policy.decide(state=state, diagnosis=diagnosis, step=4)
    assert fourth.next_skill == "polynomial"
    assert state.remediation_active is False


def test_ab3_returns_only_when_readiness_rule_is_satisfied():
    policy = AB3Policy()
    state = StudentState(
        abilities=AbilityVector(0.71, 0.55, 0.3, 0.1, 0.5, 0.5, 0.5),
        fail_streak_polynomial=2,
        remediation_active=True,
        remediation_steps_taken=1,
        remediation_entry_ability=0.62,
        remediation_target_subskill="int.sign_handling",
        remediation_target_domain="integer",
        remediation_recent_results=[1, 1, 0],
    )
    stay = policy.decide(state=state, diagnosis=None, step=2)
    assert stay.next_skill == "integer"
    assert stay.action == "continue_until_ready"
    assert stay.metadata["fixed_difficulty"] == 0.6

    state.remediation_steps_taken = 2
    state.abilities.int_sign_handling = 0.69
    state.remediation_recent_results = [1, 0, 1]
    still_not_ready = policy.decide(state=state, diagnosis=None, step=3)
    assert still_not_ready.next_skill == "integer"
    assert still_not_ready.metadata["fixed_difficulty"] == 0.6

    state.abilities.int_sign_handling = 0.74
    state.remediation_recent_results = [1, 1]
    probe = policy.decide(state=state, diagnosis=None, step=4)
    assert probe.next_skill == "polynomial"
    assert probe.action == "probe_polynomial"
    assert probe.metadata["fixed_difficulty"] == 0.6
    assert state.remediation_active is True


def test_ab3_uses_easy_then_standard_integer_difficulties():
    policy = AB3Policy()
    state = StudentState(
        abilities=AbilityVector(0.5, 0.5, 0.3, 0.1, 0.5, 0.5, 0.5),
        fail_streak_polynomial=2,
    )
    diagnosis = DiagnosisResult(
        route_type="remediate",
        suggested_skill="integer",
        failed_subskill="poly.sign_distribution",
        remediation_target_subskill="int.sign_handling",
        reason="two_consecutive_polynomial_failures",
        confidence=1.0,
    )
    first = policy.decide(state=state, diagnosis=diagnosis, step=1)
    assert first.next_skill == "integer"
    assert first.metadata["fixed_difficulty"] == 0.4

    state.remediation_active = True
    state.remediation_steps_taken = 1
    second = policy.decide(state=state, diagnosis=None, step=2)
    assert second.next_skill == "integer"
    assert second.metadata["fixed_difficulty"] == 0.6

    state.remediation_steps_taken = 2
    state.abilities.int_sign_handling = 0.73
    third = policy.decide(state=state, diagnosis=None, step=3)
    assert third.next_skill == "polynomial"
    assert third.action == "probe_polynomial"


def test_ab3_can_probe_early_when_recent_remediation_is_strong():
    policy = AB3Policy(
        min_remediation_steps=2,
        recent_correct_streak_threshold=2,
        mastery_growth_delta_threshold=0.04,
    )
    state = StudentState(
        abilities=AbilityVector(0.46, 0.5, 0.3, 0.1, 0.5, 0.5, 0.5),
        remediation_active=True,
        remediation_steps_taken=2,
        remediation_entry_ability=0.40,
        remediation_target_subskill="int.sign_handling",
        remediation_target_domain="integer",
        remediation_recent_results=[1, 1],
    )
    decision = policy.decide(state=state, diagnosis=None, step=3)
    assert decision.next_skill == "polynomial"
    assert decision.action == "probe_polynomial"
    assert decision.metadata["probe_reason"] == "early_signal"


def test_ab3_does_not_probe_early_when_recent_remediation_is_weak():
    policy = AB3Policy(
        min_remediation_steps=2,
        recent_correct_streak_threshold=2,
        mastery_growth_delta_threshold=0.04,
    )
    state = StudentState(
        abilities=AbilityVector(0.46, 0.5, 0.3, 0.1, 0.5, 0.5, 0.5),
        remediation_active=True,
        remediation_steps_taken=2,
        remediation_entry_ability=0.40,
        remediation_target_subskill="int.sign_handling",
        remediation_target_domain="integer",
        remediation_recent_results=[1, 0],
    )
    decision = policy.decide(state=state, diagnosis=None, step=3)
    assert decision.next_skill == "integer"
    assert decision.action == "continue_until_ready"


def test_ab3_timing_parameters_can_be_set_explicitly():
    policy = AB3Policy(
        min_remediation_steps=1,
        recent_correct_streak_threshold=3,
        mastery_growth_delta_threshold=0.02,
    )
    assert policy.min_remediation_steps == 1
    assert policy.recent_correct_streak_threshold == 3
    assert policy.mastery_growth_delta_threshold == pytest.approx(0.02)


def test_yaml_can_load_and_map_subskills():
    kb = SubskillKnowledgeBase(Path("configs") / "subskill_remediation.yaml")
    assert kb.get_domain("int.sign_handling") == "integer"
    assert kb.remediation_target_for("poly.sign_distribution") == "int.sign_handling"
    assert kb.remediation_target_for("poly.expand_binomial") == "int.mul_div"


def test_fixed_subskill_diagnosis_uses_yaml_mapping():
    kb = SubskillKnowledgeBase(Path("configs") / "subskill_remediation.yaml")
    diagnosis = FixedSubskillDiagnosis(kb).diagnose(
        state=StudentState(abilities=AbilityVector(0.4, 0.4, 0.3, 0.1, 0.5, 0.5, 0.5), fail_streak_polynomial=2),
        last_question=Question(
            question_id="q1",
            domain_skill="polynomial",
            subskill_tag="poly.sign_distribution",
            difficulty=0.6,
            error_tag="polynomial_sign_error",
        ),
        last_correct=False,
    )
    assert diagnosis.failed_subskill == "poly.sign_distribution"
    assert diagnosis.remediation_target_subskill == "int.sign_handling"
    assert diagnosis.suggested_skill == "integer"


def test_ab3_uses_subskill_target_not_coarse_skill_only():
    policy = AB3Policy()
    state = StudentState(abilities=AbilityVector(0.4, 0.4, 0.3, 0.1, 0.5, 0.5, 0.5), fail_streak_polynomial=2)
    diagnosis = DiagnosisResult(
        route_type="remediate",
        suggested_skill="integer",
        failed_subskill="poly.expand_binomial",
        remediation_target_subskill="int.mul_div",
        reason="two_consecutive_polynomial_failures",
        confidence=1.0,
    )
    first = policy.decide(state=state, diagnosis=diagnosis, step=1)
    assert first.next_skill == "integer"
    assert first.metadata["target_subskill"] == "int.mul_div"
    assert state.remediation_target_subskill == "int.mul_div"


def test_six_dim_state_initializes_and_maps_subskills():
    abilities = AbilityVector(0.7, 0.6, 0.3, 0.1, 0.5, 0.4, 0.45)
    assert abilities.int_sign_handling == 0.7
    assert abilities.int_mul_div == 0.6
    assert map_subskill_to_state_key("int.sign_handling") == "int_sign_handling"
    assert map_subskill_to_state_key("poly.expand_binomial") == "poly_expand_binomial_mastery"


def test_int_sign_remediation_updates_sign_state_only():
    config = ExperimentConfig()
    deltas = update_deltas(Question("q4", "integer", "int.sign_handling", 0.4), 0.4, True, config)
    assert deltas["int_sign_handling"] > 0.0
    assert deltas["int_mul_div"] == 0.0


def test_int_mul_div_remediation_updates_mul_div_state():
    config = ExperimentConfig()
    deltas = update_deltas(Question("q5", "integer", "int.mul_div", 0.6), 0.6, True, config)
    assert deltas["int_mul_div"] > 0.0
    assert deltas["int_sign_handling"] == 0.0


def test_ab3_forces_probe_after_four_remediation_steps():
    policy = AB3Policy()
    state = StudentState(
        abilities=AbilityVector(0.7, 0.6, 0.3, 0.1, 0.5, 0.5, 0.5),
        remediation_active=True,
        remediation_steps_taken=4,
        remediation_entry_ability=0.6,
        remediation_target_subskill="int.sign_handling",
        remediation_target_domain="integer",
        remediation_recent_results=[1, 0, 1],
    )
    decision = policy.decide(state=state, diagnosis=None, step=5)
    assert decision.next_skill == "polynomial"
    assert decision.action == "probe_polynomial"
    assert decision.metadata["fixed_difficulty"] == 0.6

    policy.observe_result(state, decision, correct=False)
    assert state.remediation_active is True
    assert state.remediation_steps_taken == 1

    policy.observe_result(state, decision, correct=True)
    assert state.remediation_active is False
