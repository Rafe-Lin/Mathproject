# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import math
import random
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Protocol

import matplotlib.pyplot as plt
import pandas as pd


SKILLS = ("integer", "fraction", "radical", "polynomial")
TARGET_SKILL = "polynomial"
REMEDIATION_SKILL = "integer"
STATE_KEYS = (
    "int_sign_handling",
    "int_mul_div",
    "fraction",
    "radical",
    "polynomial_core",
    "poly_sign_distribution_mastery",
    "poly_expand_binomial_mastery",
)


@dataclass
class AbilityVector:
    int_sign_handling: float
    int_mul_div: float
    fraction: float
    radical: float
    polynomial_core: float
    poly_sign_distribution_mastery: float
    poly_expand_binomial_mastery: float

    def copy(self) -> "AbilityVector":
        return AbilityVector(**asdict(self))

    def to_dict(self) -> dict[str, float]:
        return {
            "int_sign_handling": self.int_sign_handling,
            "int_mul_div": self.int_mul_div,
            "fraction": self.fraction,
            "radical": self.radical,
            "polynomial_core": self.polynomial_core,
            "poly_sign_distribution_mastery": self.poly_sign_distribution_mastery,
            "poly_expand_binomial_mastery": self.poly_expand_binomial_mastery,
        }

    def get(self, state_key: str) -> float:
        return float(getattr(self, state_key))

    def apply_delta(self, deltas: dict[str, float]) -> None:
        for state_key, delta in deltas.items():
            current = self.get(state_key)
            setattr(self, state_key, max(0.0, min(1.0, current + float(delta))))


@dataclass(frozen=True)
class Prototype:
    name: str
    base_abilities: AbilityVector


@dataclass
class ExperimentConfig:
    episodes_per_prototype: int = 100
    max_steps_per_episode: int = 30
    success_polynomial_threshold: float = 0.8
    success_consecutive_polynomial_correct: int = 2
    perturbation: float = 0.03
    random_seed: int = 42
    output_dir: str = "outputs"
    subskill_config_path: str = str(Path("configs") / "adaptive" / "subskill_remediation.yaml")
    difficulty_by_skill: dict[str, float] = field(
        default_factory=lambda: {
            "integer": 0.55,
            "fraction": 0.60,
            "radical": 0.65,
            "polynomial": 0.68,
        }
    )
    difficulty_jitter: float = 0.05
    update_scale: float = 0.08
    correct_reward: float = 1.0
    incorrect_reward: float = 0.3
    primary_weight: float = 1.0
    transfer_weight_integer_to_polynomial: float = 0.2
    ab3_min_remediation_steps: int = 2
    ab3_recent_correct_streak_threshold: int = 2
    ab3_mastery_growth_delta_threshold: float = 0.04
    prototypes: list[Prototype] = field(
        default_factory=lambda: [
            Prototype(
                "A",
                AbilityVector(
                    int_sign_handling=0.70,
                    int_mul_div=0.70,
                    fraction=0.30,
                    radical=0.10,
                    polynomial_core=0.50,
                    poly_sign_distribution_mastery=0.50,
                    poly_expand_binomial_mastery=0.50,
                ),
            ),
            Prototype(
                "B",
                AbilityVector(
                    int_sign_handling=0.25,
                    int_mul_div=0.35,
                    fraction=0.30,
                    radical=0.10,
                    polynomial_core=0.50,
                    poly_sign_distribution_mastery=0.50,
                    poly_expand_binomial_mastery=0.50,
                ),
            ),
            Prototype(
                "C",
                AbilityVector(
                    int_sign_handling=0.50,
                    int_mul_div=0.55,
                    fraction=0.30,
                    radical=0.10,
                    polynomial_core=0.50,
                    poly_sign_distribution_mastery=0.50,
                    poly_expand_binomial_mastery=0.50,
                ),
            ),
        ]
    )

    def to_serializable(self) -> dict[str, Any]:
        data = asdict(self)
        data["prototypes"] = [
            {
                "name": prototype.name,
                "base_abilities": prototype.base_abilities.to_dict(),
            }
            for prototype in self.prototypes
        ]
        return data


@dataclass
class StudentState:
    abilities: AbilityVector
    fail_streak_polynomial: int = 0
    polynomial_correct_streak: int = 0
    remediation_active: bool = False
    remediation_steps_taken: int = 0
    remediation_entry_ability: float | None = None
    remediation_target_subskill: str | None = None
    remediation_target_domain: str | None = None
    failed_subskill: str | None = None
    remediation_recent_results: list[int] = field(default_factory=list)

    def register_result(self, skill: str, correct: bool) -> None:
        if skill == TARGET_SKILL:
            self.fail_streak_polynomial = 0 if correct else self.fail_streak_polynomial + 1
            self.polynomial_correct_streak = self.polynomial_correct_streak + 1 if correct else 0
        if self.remediation_active and skill != TARGET_SKILL:
            self.remediation_recent_results.append(1 if correct else 0)
            self.remediation_recent_results = self.remediation_recent_results[-3:]


@dataclass(frozen=True)
class DiagnosisResult:
    route_type: str
    suggested_skill: str | None
    failed_subskill: str | None
    remediation_target_subskill: str | None
    reason: str
    confidence: float


@dataclass(frozen=True)
class Decision:
    next_skill: str
    phase: str
    action: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Question:
    question_id: str
    domain_skill: str
    subskill_tag: str | None
    difficulty: float
    error_tag: str | None = None


@dataclass
class StepRecord:
    controller: str
    prototype: str
    episode_id: int
    step: int
    phase: str
    action: str
    question_id: str
    domain_skill: str
    subskill_tag: str | None
    error_tag: str | None
    diagnosed_skill: str | None
    failed_subskill: str | None
    remediation_target_subskill: str | None
    question_skill: str
    difficulty: float
    a_eff: float
    p_correct: float
    correct: int
    fail_streak_polynomial: int
    polynomial_correct_streak: int
    remediation_active: int
    remediation_steps_taken: int
    remediation_recent_results: str
    ability_int_sign_handling: float
    ability_int_mul_div: float
    ability_fraction: float
    ability_radical: float
    ability_polynomial_core: float
    ability_poly_sign_distribution_mastery: float
    ability_poly_expand_binomial_mastery: float
    delta_int_sign_handling: float
    delta_int_mul_div: float
    delta_fraction: float
    delta_radical: float
    delta_polynomial_core: float
    delta_poly_sign_distribution_mastery: float
    delta_poly_expand_binomial_mastery: float
    terminated: int
    termination_reason: str


@dataclass
class EpisodeOutcome:
    controller: str
    prototype: str
    episode_id: int
    success: int
    total_steps: int
    max_polynomial_fail_streak: int
    remediation_entries: int
    final_int_sign_handling: float
    final_int_mul_div: float
    final_polynomial_core: float
    final_poly_sign_distribution_mastery: float
    final_poly_expand_binomial_mastery: float
    initial_int_sign_handling: float
    initial_int_mul_div: float
    initial_polynomial_core: float
    initial_poly_sign_distribution_mastery: float
    initial_poly_expand_binomial_mastery: float
    termination_reason: str


class SubskillKnowledgeBase:
    def __init__(self, config_path: str | Path):
        self.config_path = Path(config_path)
        self._raw = self._load_yaml(self.config_path)
        self.subskills = dict(self._raw.get("subskills") or {})
        self.diagnosis_map = dict(self._raw.get("diagnosis_map") or {})
        self.remediation_map = dict(self._raw.get("remediation_map") or {})
        self.subskill_to_error_tag = {str(v): str(k) for k, v in self.diagnosis_map.items()}
        if not self.subskills:
            raise ValueError("subskills config is empty")

    @staticmethod
    def _load_yaml(path: Path) -> dict[str, Any]:
        try:
            import yaml  # type: ignore
        except Exception as exc:
            raise RuntimeError("PyYAML is required to load subskill remediation config") from exc
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}

    def get_domain(self, subskill: str | None) -> str | None:
        if not subskill:
            return None
        node = self.subskills.get(subskill) or {}
        return str(node.get("domain") or "").strip() or None

    def diagnose_failed_subskill(self, error_tag: str | None) -> str | None:
        if not error_tag:
            return None
        return str(self.diagnosis_map.get(error_tag) or "").strip() or None

    def remediation_target_for(self, failed_subskill: str | None) -> str | None:
        if not failed_subskill:
            return None
        mapping = self.remediation_map.get(failed_subskill) or {}
        return str(mapping.get("target") or "").strip() or None

    def error_tag_for(self, subskill: str | None) -> str | None:
        if not subskill:
            return None
        return self.subskill_to_error_tag.get(subskill)

    def to_serializable(self) -> dict[str, Any]:
        return {
            "config_path": str(self.config_path),
            "subskills": self.subskills,
            "diagnosis_map": self.diagnosis_map,
            "remediation_map": self.remediation_map,
        }


def map_subskill_to_state_key(subskill_tag: str | None) -> str | None:
    mapping = {
        "int.sign_handling": "int_sign_handling",
        "int.mul_div": "int_mul_div",
        "poly.sign_distribution": "poly_sign_distribution_mastery",
        "poly.expand_binomial": "poly_expand_binomial_mastery",
        "poly.combine_like_terms": "polynomial_core",
    }
    return mapping.get(str(subskill_tag or "").strip())


def map_question_to_state_key(question: Question) -> str | None:
    mapped = map_subskill_to_state_key(question.subskill_tag)
    if mapped:
        return mapped
    if question.domain_skill == "polynomial":
        return "polynomial_core"
    if question.domain_skill in ("fraction", "radical"):
        return question.domain_skill
    return None


class DiagnosisStrategy(Protocol):
    def diagnose(
        self,
        state: StudentState,
        last_question: Question | None,
        last_correct: bool | None,
    ) -> DiagnosisResult:
        ...


class DecisionPolicy(Protocol):
    name: str

    def decide(
        self,
        state: StudentState,
        diagnosis: DiagnosisResult | None,
        step: int,
    ) -> Decision:
        ...

    def observe_result(self, state: StudentState, decision: Decision, correct: bool) -> None:
        ...


class FixedSubskillDiagnosis:
    def __init__(self, knowledge_base: SubskillKnowledgeBase):
        self.knowledge_base = knowledge_base

    def diagnose(
        self,
        state: StudentState,
        last_question: Question | None,
        last_correct: bool | None,
    ) -> DiagnosisResult:
        if state.fail_streak_polynomial < 2 or not last_question or last_correct is not False:
            return DiagnosisResult(
                route_type="stay",
                suggested_skill=None,
                failed_subskill=None,
                remediation_target_subskill=None,
                reason="no_trigger",
                confidence=0.0,
            )

        failed_subskill = self.knowledge_base.diagnose_failed_subskill(last_question.error_tag)
        remediation_target = self.knowledge_base.remediation_target_for(failed_subskill)
        remediation_domain = self.knowledge_base.get_domain(remediation_target)
        return DiagnosisResult(
            route_type="remediate" if remediation_target else "stay",
            suggested_skill=remediation_domain,
            failed_subskill=failed_subskill,
            remediation_target_subskill=remediation_target,
            reason="two_consecutive_polynomial_failures",
            confidence=1.0 if remediation_target else 0.0,
        )


class RuleBasedPolicyBase:
    name = "base"

    def _start_remediation(
        self,
        state: StudentState,
        target_subskill: str | None = None,
        target_domain: str | None = None,
    ) -> None:
        state.remediation_active = True
        state.remediation_steps_taken = 0
        target_state_key = map_subskill_to_state_key(target_subskill)
        if target_state_key:
            state.remediation_entry_ability = state.abilities.get(target_state_key)
        else:
            state.remediation_entry_ability = None
        state.remediation_target_subskill = target_subskill
        state.remediation_target_domain = target_domain
        state.remediation_recent_results = []
        state.fail_streak_polynomial = 0
        state.polynomial_correct_streak = 0

    def _finish_remediation(self, state: StudentState) -> None:
        state.remediation_active = False
        state.remediation_steps_taken = 0
        state.remediation_entry_ability = None
        state.remediation_target_subskill = None
        state.remediation_target_domain = None

    def observe_result(self, state: StudentState, decision: Decision, correct: bool) -> None:
        return None


class AB1Policy(RuleBasedPolicyBase):
    name = "AB1"

    def decide(self, state: StudentState, diagnosis: DiagnosisResult | None, step: int) -> Decision:
        return Decision(next_skill=TARGET_SKILL, phase="target", action="target_only")


class AB2Policy(RuleBasedPolicyBase):
    name = "AB2"

    def decide(self, state: StudentState, diagnosis: DiagnosisResult | None, step: int) -> Decision:
        if state.remediation_active:
            if state.remediation_steps_taken >= 3:
                self._finish_remediation(state)
                return Decision(next_skill=TARGET_SKILL, phase="target", action="return_after_fixed_remediation")
            return Decision(
                next_skill=REMEDIATION_SKILL,
                phase="remediation",
                action="fixed_remediation",
                metadata={"fixed_difficulty": 0.6},
            )

        if diagnosis and diagnosis.route_type == "remediate":
            self._start_remediation(
                state,
                target_subskill=diagnosis.remediation_target_subskill,
                target_domain=diagnosis.suggested_skill,
            )
            return Decision(
                next_skill=diagnosis.suggested_skill or REMEDIATION_SKILL,
                phase="diagnosis",
                action="diagnose_and_enter_remediation",
                metadata={
                    "fixed_difficulty": 0.6,
                    "target_subskill": diagnosis.remediation_target_subskill,
                },
            )
        return Decision(next_skill=TARGET_SKILL, phase="target", action="target_only")


class AB3Policy(RuleBasedPolicyBase):
    name = "AB3"

    def __init__(
        self,
        *,
        min_remediation_steps: int = 2,
        recent_correct_streak_threshold: int = 2,
        mastery_growth_delta_threshold: float = 0.04,
    ):
        self.min_remediation_steps = int(min_remediation_steps)
        self.recent_correct_streak_threshold = int(recent_correct_streak_threshold)
        self.mastery_growth_delta_threshold = float(mastery_growth_delta_threshold)

    def _recent_correct_streak(self, recent: list[int]) -> int:
        streak = 0
        for result in reversed(recent):
            if result != 1:
                break
            streak += 1
        return streak

    def _has_early_probe_signal(self, state: StudentState) -> bool:
        if state.remediation_steps_taken < self.min_remediation_steps:
            return False
        recent = state.remediation_recent_results[-3:]
        if not recent:
            return False
        target_state_key = map_subskill_to_state_key(state.remediation_target_subskill)
        current_ability = state.abilities.get(target_state_key) if target_state_key else 0.0
        entry_ability = state.remediation_entry_ability if state.remediation_entry_ability is not None else current_ability
        gain = current_ability - entry_ability
        return (
            self._recent_correct_streak(recent) >= self.recent_correct_streak_threshold
            and gain >= self.mastery_growth_delta_threshold
        )

    def _is_ready_to_return(self, state: StudentState) -> bool:
        recent = state.remediation_recent_results[-3:]
        target_state_key = map_subskill_to_state_key(state.remediation_target_subskill)
        current_ability = state.abilities.get(target_state_key) if target_state_key else 0.0
        entry_ability = state.remediation_entry_ability if state.remediation_entry_ability is not None else current_ability
        gain = current_ability - entry_ability
        return (
            state.remediation_steps_taken >= self.min_remediation_steps
            and current_ability >= 0.72
            and gain >= 0.08
            and len(recent) >= 3
            and sum(recent) >= 2
            and recent[-1] == 1
        )

    def decide(self, state: StudentState, diagnosis: DiagnosisResult | None, step: int) -> Decision:
        if state.remediation_active:
            if state.remediation_steps_taken >= 4:
                return Decision(
                    next_skill=TARGET_SKILL,
                    phase="probe",
                    action="probe_polynomial",
                    metadata={"fixed_difficulty": 0.6},
                )
            if self._is_ready_to_return(state):
                self._finish_remediation(state)
                return Decision(next_skill=TARGET_SKILL, phase="target", action="return_ready")
            if state.remediation_steps_taken == 0:
                return Decision(
                    next_skill=state.remediation_target_domain or REMEDIATION_SKILL,
                    phase="remediation",
                    action="continue_until_ready",
                    metadata={"ready": False, "fixed_difficulty": 0.4},
                )
            if state.remediation_steps_taken == 1:
                return Decision(
                    next_skill=state.remediation_target_domain or REMEDIATION_SKILL,
                    phase="remediation",
                    action="continue_until_ready",
                    metadata={"ready": False, "fixed_difficulty": 0.6},
                )
            target_state_key = map_subskill_to_state_key(state.remediation_target_subskill)
            current_ability = state.abilities.get(target_state_key) if target_state_key else 0.0
            if current_ability >= 0.72 or self._has_early_probe_signal(state):
                return Decision(
                    next_skill=TARGET_SKILL,
                    phase="probe",
                    action="probe_polynomial",
                    metadata={
                        "fixed_difficulty": 0.6,
                        "probe_reason": "early_signal" if current_ability < 0.72 else "threshold",
                    },
                )
            return Decision(
                next_skill=state.remediation_target_domain or REMEDIATION_SKILL,
                phase="remediation",
                action="continue_until_ready",
                metadata={"ready": False, "fixed_difficulty": 0.6},
            )

        if diagnosis and diagnosis.route_type == "remediate":
            target_subskill = diagnosis.remediation_target_subskill
            target_domain = diagnosis.suggested_skill
            state.failed_subskill = diagnosis.failed_subskill
            self._start_remediation(
                state,
                target_subskill=target_subskill,
                target_domain=target_domain,
            )
            return Decision(
                next_skill=target_domain or REMEDIATION_SKILL,
                phase="diagnosis",
                action="diagnose_and_enter_remediation",
                metadata={"fixed_difficulty": 0.4, "target_subskill": target_subskill},
            )
        return Decision(next_skill=TARGET_SKILL, phase="target", action="target_only")

    def observe_result(self, state: StudentState, decision: Decision, correct: bool) -> None:
        if decision.action != "probe_polynomial":
            return
        state.fail_streak_polynomial = 0
        state.polynomial_correct_streak = 0
        if correct:
            self._finish_remediation(state)
        else:
            state.remediation_steps_taken = 1


def compute_effective_ability(abilities: AbilityVector, question: Question) -> float:
    if question.subskill_tag == "poly.sign_distribution":
        return (0.65 * abilities.poly_sign_distribution_mastery) + (0.35 * abilities.int_sign_handling)
    if question.subskill_tag == "poly.expand_binomial":
        return (0.6 * abilities.poly_expand_binomial_mastery) + (0.4 * abilities.int_mul_div)
    if question.subskill_tag == "poly.combine_like_terms":
        return (0.8 * abilities.polynomial_core) + (0.2 * abilities.int_sign_handling)
    if question.subskill_tag == "int.sign_handling":
        return abilities.int_sign_handling
    if question.subskill_tag == "int.mul_div":
        return abilities.int_mul_div
    if question.domain_skill == "fraction":
        return abilities.fraction
    if question.domain_skill == "radical":
        return abilities.radical
    if question.domain_skill == "polynomial":
        return abilities.polynomial_core
    state_key = map_question_to_state_key(question)
    return abilities.get(state_key) if state_key else abilities.polynomial_core


def probability_correct(a_eff: float, difficulty: float) -> float:
    return 1.0 / (1.0 + math.exp(-6.0 * (a_eff - difficulty)))


def update_deltas(
    question: Question,
    difficulty: float,
    correct: bool,
    config: ExperimentConfig,
) -> dict[str, float]:
    reward = config.correct_reward if correct else config.incorrect_reward
    base_delta = config.update_scale * (0.8 + 0.4 * difficulty) * reward
    deltas = {state_key: 0.0 for state_key in STATE_KEYS}
    if question.subskill_tag == "int.sign_handling":
        deltas["int_sign_handling"] = base_delta * 1.0
        deltas["poly_sign_distribution_mastery"] = base_delta * 0.2
        deltas["polynomial_core"] = base_delta * 0.05
    elif question.subskill_tag == "int.mul_div":
        deltas["int_mul_div"] = base_delta * 1.0
        deltas["poly_expand_binomial_mastery"] = base_delta * 0.2
        deltas["polynomial_core"] = base_delta * 0.05
    elif question.subskill_tag in ("poly.sign_distribution", "poly.expand_binomial"):
        if question.subskill_tag == "poly.sign_distribution":
            deltas["poly_sign_distribution_mastery"] = base_delta * 1.0
        else:
            deltas["poly_expand_binomial_mastery"] = base_delta * 1.0
        deltas["polynomial_core"] = base_delta * 0.2
    elif question.subskill_tag == "poly.combine_like_terms":
        deltas["polynomial_core"] = base_delta * 1.0
    else:
        target_state_key = map_question_to_state_key(question)
        if target_state_key:
            deltas[target_state_key] = base_delta * 1.0
    return deltas


def sample_difficulty(skill: str, rng: random.Random, config: ExperimentConfig) -> float:
    center = float(config.difficulty_by_skill[skill])
    return max(0.0, min(1.0, center + rng.uniform(-config.difficulty_jitter, config.difficulty_jitter)))


def perturb_abilities(base: AbilityVector, rng: random.Random, perturbation: float) -> AbilityVector:
    return AbilityVector(
        int_sign_handling=max(0.0, min(1.0, base.int_sign_handling + rng.uniform(-perturbation, perturbation))),
        int_mul_div=max(0.0, min(1.0, base.int_mul_div + rng.uniform(-perturbation, perturbation))),
        fraction=max(0.0, min(1.0, base.fraction + rng.uniform(-perturbation, perturbation))),
        radical=max(0.0, min(1.0, base.radical + rng.uniform(-perturbation, perturbation))),
        polynomial_core=max(0.0, min(1.0, base.polynomial_core + rng.uniform(-perturbation, perturbation))),
        poly_sign_distribution_mastery=max(
            0.0,
            min(1.0, base.poly_sign_distribution_mastery + rng.uniform(-perturbation, perturbation)),
        ),
        poly_expand_binomial_mastery=max(
            0.0,
            min(1.0, base.poly_expand_binomial_mastery + rng.uniform(-perturbation, perturbation)),
        ),
    )


POLYNOMIAL_QUESTION_BANK = (
    ("poly.sign_distribution", "polynomial_sign_error"),
    ("poly.expand_binomial", "polynomial_expand_error"),
    ("poly.combine_like_terms", "polynomial_like_terms_error"),
)


def build_question(
    *,
    knowledge_base: SubskillKnowledgeBase,
    controller_name: str,
    prototype_name: str,
    episode_id: int,
    step: int,
    decision: Decision,
    difficulty: float,
    rng: random.Random,
    state: StudentState,
) -> Question:
    if decision.action == "probe_polynomial":
        subskill_tag = state.failed_subskill or "poly.sign_distribution"
        error_tag = knowledge_base.error_tag_for(subskill_tag)
        domain_skill = TARGET_SKILL
    elif decision.next_skill == TARGET_SKILL:
        subskill_tag, error_tag = rng.choice(list(POLYNOMIAL_QUESTION_BANK))
        domain_skill = TARGET_SKILL
    else:
        subskill_tag = state.remediation_target_subskill or str(decision.metadata.get("target_subskill") or "").strip() or None
        error_tag = None
        domain_skill = decision.next_skill

    return Question(
        question_id=f"{controller_name}-{prototype_name}-ep{episode_id}-step{step}",
        domain_skill=domain_skill,
        subskill_tag=subskill_tag,
        difficulty=difficulty,
        error_tag=error_tag,
    )


def is_episode_success(
    state: StudentState,
    skill: str,
    correct: bool,
    config: ExperimentConfig,
    action: str | None = None,
) -> bool:
    return (
        action != "probe_polynomial"
        and skill == TARGET_SKILL
        and correct
        and state.abilities.polynomial_core >= config.success_polynomial_threshold
        and state.polynomial_correct_streak >= config.success_consecutive_polynomial_correct
    )


def run_episode(
    controller: DecisionPolicy,
    diagnosis_strategy: DiagnosisStrategy,
    knowledge_base: SubskillKnowledgeBase,
    prototype: Prototype,
    episode_id: int,
    rng: random.Random,
    config: ExperimentConfig,
) -> tuple[list[StepRecord], EpisodeOutcome]:
    state = StudentState(abilities=perturb_abilities(prototype.base_abilities, rng, config.perturbation))
    initial = state.abilities.copy()
    records: list[StepRecord] = []
    max_fail_streak = 0
    remediation_entries = 0
    diagnosis: DiagnosisResult | None = None
    last_question: Question | None = None
    last_correct: bool | None = None
    success = 0
    termination_reason = "max_steps"

    for step in range(1, config.max_steps_per_episode + 1):
        diagnosis = diagnosis_strategy.diagnose(state, last_question=last_question, last_correct=last_correct)
        entering_remediation = bool(
            diagnosis.route_type == "remediate" and not state.remediation_active and controller.name != "AB1"
        )
        if entering_remediation:
            remediation_entries += 1

        decision = controller.decide(state=state, diagnosis=diagnosis, step=step)
        question_skill = decision.next_skill
        difficulty = float(decision.metadata.get("fixed_difficulty", sample_difficulty(question_skill, rng, config)))
        question = build_question(
            knowledge_base=knowledge_base,
            controller_name=controller.name,
            prototype_name=prototype.name,
            episode_id=episode_id,
            step=step,
            decision=decision,
            difficulty=difficulty,
            rng=rng,
            state=state,
        )
        a_eff = compute_effective_ability(state.abilities, question)
        p_correct = probability_correct(a_eff, difficulty)
        correct = rng.random() < p_correct

        deltas = update_deltas(question, difficulty, correct, config)
        state.abilities.apply_delta(deltas)
        state.register_result(question_skill, correct)
        if state.remediation_active and question_skill != TARGET_SKILL:
            state.remediation_steps_taken += 1
        controller.observe_result(state, decision, bool(correct))

        max_fail_streak = max(max_fail_streak, state.fail_streak_polynomial)
        step_success = is_episode_success(state, question_skill, correct, config, action=decision.action)
        if step_success:
            success = 1
            termination_reason = "success_threshold"

        record = StepRecord(
            controller=controller.name,
            prototype=prototype.name,
            episode_id=episode_id,
            step=step,
            phase=decision.phase,
            action=decision.action,
            question_id=question.question_id,
            domain_skill=question.domain_skill,
            subskill_tag=question.subskill_tag,
            error_tag=question.error_tag,
            diagnosed_skill=diagnosis.suggested_skill if diagnosis.route_type == "remediate" else None,
            failed_subskill=diagnosis.failed_subskill,
            remediation_target_subskill=state.remediation_target_subskill,
            question_skill=question_skill,
            difficulty=difficulty,
            a_eff=a_eff,
            p_correct=p_correct,
            correct=int(correct),
            fail_streak_polynomial=state.fail_streak_polynomial,
            polynomial_correct_streak=state.polynomial_correct_streak,
            remediation_active=int(state.remediation_active),
            remediation_steps_taken=state.remediation_steps_taken,
            remediation_recent_results="".join(str(v) for v in state.remediation_recent_results),
            ability_int_sign_handling=state.abilities.int_sign_handling,
            ability_int_mul_div=state.abilities.int_mul_div,
            ability_fraction=state.abilities.fraction,
            ability_radical=state.abilities.radical,
            ability_polynomial_core=state.abilities.polynomial_core,
            ability_poly_sign_distribution_mastery=state.abilities.poly_sign_distribution_mastery,
            ability_poly_expand_binomial_mastery=state.abilities.poly_expand_binomial_mastery,
            delta_int_sign_handling=deltas["int_sign_handling"],
            delta_int_mul_div=deltas["int_mul_div"],
            delta_fraction=deltas["fraction"],
            delta_radical=deltas["radical"],
            delta_polynomial_core=deltas["polynomial_core"],
            delta_poly_sign_distribution_mastery=deltas["poly_sign_distribution_mastery"],
            delta_poly_expand_binomial_mastery=deltas["poly_expand_binomial_mastery"],
            terminated=int(step_success),
            termination_reason=termination_reason if step_success else "",
        )
        records.append(record)
        last_question = question
        last_correct = bool(correct)
        if step_success:
            break

    outcome = EpisodeOutcome(
        controller=controller.name,
        prototype=prototype.name,
        episode_id=episode_id,
        success=success,
        total_steps=len(records),
        max_polynomial_fail_streak=max_fail_streak,
        remediation_entries=remediation_entries,
        final_int_sign_handling=state.abilities.int_sign_handling,
        final_int_mul_div=state.abilities.int_mul_div,
        final_polynomial_core=state.abilities.polynomial_core,
        final_poly_sign_distribution_mastery=state.abilities.poly_sign_distribution_mastery,
        final_poly_expand_binomial_mastery=state.abilities.poly_expand_binomial_mastery,
        initial_int_sign_handling=initial.int_sign_handling,
        initial_int_mul_div=initial.int_mul_div,
        initial_polynomial_core=initial.polynomial_core,
        initial_poly_sign_distribution_mastery=initial.poly_sign_distribution_mastery,
        initial_poly_expand_binomial_mastery=initial.poly_expand_binomial_mastery,
        termination_reason=termination_reason,
    )
    if not success and records:
        records[-1].termination_reason = termination_reason
        records[-1].terminated = 1
    return records, outcome


def _ensure_dirs(output_dir: Path) -> None:
    (output_dir / "plots").mkdir(parents=True, exist_ok=True)


def _write_config(output_dir: Path, config: ExperimentConfig, knowledge_base: SubskillKnowledgeBase) -> None:
    path = output_dir / "config_used.json"
    payload = config.to_serializable()
    payload["subskill_knowledge"] = knowledge_base.to_serializable()
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _build_summary(outcomes_df: pd.DataFrame) -> pd.DataFrame:
    gain_df = outcomes_df.assign(
        int_sign_gain=outcomes_df["final_int_sign_handling"] - outcomes_df["initial_int_sign_handling"],
        int_mul_div_gain=outcomes_df["final_int_mul_div"] - outcomes_df["initial_int_mul_div"],
        polynomial_gain=outcomes_df["final_polynomial_core"] - outcomes_df["initial_polynomial_core"],
        poly_sign_distribution_gain=(
            outcomes_df["final_poly_sign_distribution_mastery"] - outcomes_df["initial_poly_sign_distribution_mastery"]
        ),
        poly_expand_binomial_gain=(
            outcomes_df["final_poly_expand_binomial_mastery"] - outcomes_df["initial_poly_expand_binomial_mastery"]
        ),
    )
    grouped = (
        gain_df.groupby(["controller", "prototype"], as_index=False)
        .agg(
            success_rate=("success", "mean"),
            avg_total_steps=("total_steps", "mean"),
            median_total_steps=("total_steps", "median"),
            avg_max_polynomial_fail_streak=("max_polynomial_fail_streak", "mean"),
            avg_remediation_entries=("remediation_entries", "mean"),
            avg_int_sign_gain=("int_sign_gain", "mean"),
            avg_int_mul_div_gain=("int_mul_div_gain", "mean"),
            avg_polynomial_gain=("polynomial_gain", "mean"),
            avg_poly_sign_distribution_gain=("poly_sign_distribution_gain", "mean"),
            avg_poly_expand_binomial_gain=("poly_expand_binomial_gain", "mean"),
        )
    )
    return grouped


def _plot_bar(
    summary_df: pd.DataFrame,
    value_col: str,
    title: str,
    ylabel: str,
    output_path: Path,
) -> None:
    plot_df = summary_df.copy()
    plot_df["label"] = plot_df["controller"] + "-" + plot_df["prototype"]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(plot_df["label"], plot_df[value_col], color="#2f6db2")
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.set_xlabel("controller-prototype")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


def _plot_sample_trajectory(logs_df: pd.DataFrame, output_path: Path) -> None:
    ordered = logs_df.sort_values(["controller", "prototype", "episode_id", "step"])
    first_episode_keys = (
        ordered.groupby(["controller", "prototype"], as_index=False)["episode_id"]
        .min()
        .rename(columns={"episode_id": "sample_episode_id"})
    )
    sample = ordered.merge(first_episode_keys, on=["controller", "prototype"], how="inner")
    sample = sample[sample["episode_id"] == sample["sample_episode_id"]]
    fig, ax = plt.subplots(figsize=(10, 6))
    for (controller, prototype), group in sample.groupby(["controller", "prototype"]):
        ax.plot(
            group["step"],
            group["ability_polynomial_core"],
            marker="o",
            label=f"{controller}-{prototype}",
        )
    ax.axhline(0.8, color="#c44e52", linestyle="--", linewidth=1, label="poly success threshold")
    ax.set_title("Sample Polynomial Trajectory")
    ax.set_xlabel("step")
    ax.set_ylabel("polynomial ability")
    ax.legend()
    plt.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


def generate_plots(summary_df: pd.DataFrame, logs_df: pd.DataFrame, output_dir: Path) -> None:
    plots_dir = output_dir / "plots"
    _plot_bar(summary_df, "success_rate", "Success Rate by Controller and Prototype", "success rate", plots_dir / "success_rate.png")
    _plot_bar(summary_df, "avg_total_steps", "Average Total Steps", "steps", plots_dir / "total_steps.png")
    _plot_bar(
        summary_df,
        "avg_max_polynomial_fail_streak",
        "Average Max Polynomial Fail Streak",
        "max fail streak",
        plots_dir / "fail_streak.png",
    )
    _plot_sample_trajectory(logs_df, plots_dir / "sample_trajectory.png")


def run_experiment(config: ExperimentConfig) -> dict[str, Path]:
    rng = random.Random(config.random_seed)
    output_dir = Path(config.output_dir)
    _ensure_dirs(output_dir)

    knowledge_base = SubskillKnowledgeBase(config.subskill_config_path)
    diagnosis = FixedSubskillDiagnosis(knowledge_base)
    controllers: list[DecisionPolicy] = [
        AB1Policy(),
        AB2Policy(),
        AB3Policy(
            min_remediation_steps=config.ab3_min_remediation_steps,
            recent_correct_streak_threshold=config.ab3_recent_correct_streak_threshold,
            mastery_growth_delta_threshold=config.ab3_mastery_growth_delta_threshold,
        ),
    ]
    all_logs: list[dict[str, Any]] = []
    all_outcomes: list[dict[str, Any]] = []

    for controller in controllers:
        for prototype in config.prototypes:
            for episode in range(1, config.episodes_per_prototype + 1):
                logs, outcome = run_episode(
                    controller=controller,
                    diagnosis_strategy=diagnosis,
                    knowledge_base=knowledge_base,
                    prototype=prototype,
                    episode_id=episode,
                    rng=rng,
                    config=config,
                )
                all_logs.extend(asdict(record) for record in logs)
                all_outcomes.append(asdict(outcome))

    logs_df = pd.DataFrame(all_logs)
    outcomes_df = pd.DataFrame(all_outcomes)
    summary_df = _build_summary(outcomes_df)

    logs_path = output_dir / "experiment_logs.csv"
    summary_path = output_dir / "summary_metrics.csv"
    logs_df.to_csv(logs_path, index=False, encoding="utf-8")
    summary_df.to_csv(summary_path, index=False, encoding="utf-8")
    _write_config(output_dir, config, knowledge_base)
    generate_plots(summary_df, logs_df, output_dir)

    return {
        "logs": logs_path,
        "summary": summary_path,
        "config": output_dir / "config_used.json",
        "success_rate_plot": output_dir / "plots" / "success_rate.png",
        "total_steps_plot": output_dir / "plots" / "total_steps.png",
        "fail_streak_plot": output_dir / "plots" / "fail_streak.png",
        "sample_trajectory_plot": output_dir / "plots" / "sample_trajectory.png",
    }


def run_ab3_timing_sweep(
    *,
    base_config: ExperimentConfig,
    output_csv: str | Path,
    min_steps_values: list[int],
    streak_values: list[int],
    delta_values: list[float],
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for min_steps in min_steps_values:
        for streak_threshold in streak_values:
            for delta_threshold in delta_values:
                config = ExperimentConfig(**base_config.to_serializable())
                config.prototypes = [
                    Prototype(item.name, AbilityVector(**item.base_abilities.to_dict()))
                    for item in base_config.prototypes
                ]
                config.ab3_min_remediation_steps = int(min_steps)
                config.ab3_recent_correct_streak_threshold = int(streak_threshold)
                config.ab3_mastery_growth_delta_threshold = float(delta_threshold)
                config.output_dir = str(Path(base_config.output_dir) / f"tmp_m{min_steps}_s{streak_threshold}_d{delta_threshold:.2f}")
                run_experiment(config)
                summary = pd.read_csv(Path(config.output_dir) / "summary_metrics.csv")
                ab2 = summary[summary["controller"] == "AB2"].set_index("prototype")
                ab3 = summary[summary["controller"] == "AB3"].set_index("prototype")
                for prototype in sorted(ab2.index):
                    rows.append(
                        {
                            "min_remediation_steps": min_steps,
                            "recent_correct_streak_threshold": streak_threshold,
                            "mastery_growth_delta_threshold": delta_threshold,
                            "prototype": prototype,
                            "ab2_success_rate": float(ab2.loc[prototype, "success_rate"]),
                            "ab3_success_rate": float(ab3.loc[prototype, "success_rate"]),
                            "ab2_avg_total_steps": float(ab2.loc[prototype, "avg_total_steps"]),
                            "ab3_avg_total_steps": float(ab3.loc[prototype, "avg_total_steps"]),
                            "ab2_avg_polynomial_gain": float(ab2.loc[prototype, "avg_polynomial_gain"]),
                            "ab3_avg_polynomial_gain": float(ab3.loc[prototype, "avg_polynomial_gain"]),
                            "delta_success_rate": float(ab3.loc[prototype, "success_rate"] - ab2.loc[prototype, "success_rate"]),
                            "delta_avg_total_steps": float(ab3.loc[prototype, "avg_total_steps"] - ab2.loc[prototype, "avg_total_steps"]),
                            "delta_avg_polynomial_gain": float(
                                ab3.loc[prototype, "avg_polynomial_gain"] - ab2.loc[prototype, "avg_polynomial_gain"]
                            ),
                        }
                    )
    df = pd.DataFrame(rows)
    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    return df
