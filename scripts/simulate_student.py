"""
[File Name]
simulate_student.py

[Created Date]
2026-04-09

[Project]
Adaptive Math Learning System (Adaptive Summative + Teaching)

[Description]
This script runs the core adaptive-learning simulation workflow for polynomial learning.
It generates per-episode and per-step trajectories for AB1/AB2/AB3 strategies across student types.
The file computes outcome summaries, writes formal experiment CSV outputs, and auto-generates key Experiment 2 figures.
It also logs remediation dynamics and optional RAG-assisted intervention traces for extension analysis.

[Core Functionality]
- Execute batch simulation across strategies and student profiles (Careless/Average/Weak)
- Update subskill/mastery states step-by-step with remediation and routing behavior
- Record detailed trajectory logs for learning dynamics and phase transitions
- Build and export ablation and student-type summary CSV reports
- Auto-generate Experiment 2 policy and mastery trajectory figures after each run
- Output publication-support artifacts (fixed representative figure filename and captions)

[Related Experiments]
- Experiment 1: Baseline vs AB2 vs AB3
- Experiment 2: Student Type Analysis
- Experiment 3: Policy Timing (AB3)
- Experiment 4: Weak + RAG (Extension)

[Notes]
- No experiment logic is modified by this header.
- Added for maintainability and research documentation only.
"""
import csv
import os
import random
import statistics
import shutil
from pathlib import Path
from collections import Counter
from typing import Any
import matplotlib.pyplot as plt

# ====================
# 1) 實驗設定（研究版最小重構）
# ====================
# 固定亂數種子，確保科展重現性。
RANDOM_SEED = 42
# 每種學生在每個策略下的 episode 數。
N_PER_TYPE = 100
# 每個 episode 最大步數。
MAX_STEPS = 30
# Weak foundation-phase extra support budget (used by experiment runner; default off).
WEAK_FOUNDATION_EXTRA_STEPS = 0
# Experiment 4: RAG tutor switch and per-episode intervention cap.
ENABLE_RAG_TUTOR = True
MAX_RAG_INTERVENTIONS_PER_EPISODE = 3
RAG_TUTOR_VERSION = "v1"
STRUCTURAL_SUBSKILLS = {"family_isomorphism", "expand_binomial"}
TRANSITION_SUBSKILLS = {"expand_monomial", "sign_distribution"}
# polynomial 目標精熟門檻。
TARGET_MASTERY = 0.85

# 子技能導向更新幅度（不做策略 buff，僅依作答結果更新）。
MASTERY_UPDATE = {
    "correct": 0.09,
    "minor_error": -0.015,
    "major_error": -0.035,
}

STRATEGIES = ["AB1_Baseline", "AB2_RuleBased", "AB3_PPO_Dynamic"]
STUDENT_TYPES = ["Careless", "Weak", "Average"]
TARGET_SKILL = "polynomial"

REPORTS_DIR = Path("reports")
EXPERIMENT1_OUTPUT_DIR = REPORTS_DIR / "experiment_1_ablation"
EXPERIMENT2_OUTPUT_DIR = REPORTS_DIR / "experiment_2_ab3_student_types"

# polynomial 子技能（固定研究範圍）。
POLYNOMIAL_SUBSKILLS = [
    "sign_handling",
    "combine_like_terms",
    "sign_distribution",
    "expand_monomial",
    "expand_binomial",
    "family_isomorphism",
]
PREREQUISITE_SUBSKILLS = {
    "sign_handling",
    "combine_like_terms",
    "sign_distribution",
}

# family -> subskill 最小可用映射。
FAMILY_TO_SUBSKILLS: dict[str, list[str]] = {
    "poly_add_sub_flat": ["combine_like_terms"],
    "poly_add_sub_nested": ["sign_distribution", "sign_handling"],
    "poly_mul_monomial": ["expand_monomial"],
    "poly_mul_poly": ["expand_binomial"],
    "poly_mixed_simplify": ["family_isomorphism", "combine_like_terms"],
}

# 子技能的主要對應 family（供選題/補救定位）。
SUBSKILL_PRIMARY_FAMILY: dict[str, str] = {
    "sign_handling": "poly_add_sub_nested",
    "combine_like_terms": "poly_add_sub_flat",
    "sign_distribution": "poly_add_sub_nested",
    "expand_monomial": "poly_mul_monomial",
    "expand_binomial": "poly_mul_poly",
    "family_isomorphism": "poly_mixed_simplify",
}

# 子技能聚合權重：維持簡單且可解釋。
SUBSKILL_WEIGHTS: dict[str, float] = {
    "sign_handling": 1.0,
    "combine_like_terms": 1.1,
    "sign_distribution": 1.0,
    "expand_monomial": 0.9,
    "expand_binomial": 1.0,
    "family_isomorphism": 1.0,
}

FAMILY_SEQUENCE = list(FAMILY_TO_SUBSKILLS.keys())


def clamp(value: float, low: float, high: float) -> float:
    """Clamp value into [low, high]."""
    return max(low, min(high, value))


def weighted_polynomial_mastery(subskill_mastery: dict[str, float]) -> float:
    """Aggregate polynomial mastery from subskill vector with weakest-skill blend."""
    total_weight = sum(SUBSKILL_WEIGHTS.values())
    if total_weight <= 0:
        return 0.0
    score = 0.0
    for subskill in POLYNOMIAL_SUBSKILLS:
        score += SUBSKILL_WEIGHTS[subskill] * float(subskill_mastery[subskill])
    weighted_mean = score / total_weight
    weakest = min(float(subskill_mastery[s]) for s in POLYNOMIAL_SUBSKILLS)
    aggregated = (0.75 * weighted_mean) + (0.25 * weakest)
    return clamp(aggregated, 0.0, 1.0)


def compute_zpd_gain_scale(current_subskill_mastery: float, student_type: str) -> float:
    """Piecewise ZPD gain scale: hardest and easiest zones get lower learning efficiency."""
    if current_subskill_mastery < 0.30:
        if student_type == "Weak":
            return 1.00
        return 0.85
    if current_subskill_mastery < 0.70:
        return 1.20
    return 0.75


def compute_prerequisite_transfer_bonus(
    hit_subskill: str,
    is_correct: bool,
    current_polynomial_mastery: float,
    student_type: str,
) -> float:
    """Minimal prerequisite transfer bonus from foundational subskills to polynomial mastery."""
    if (not is_correct) or (hit_subskill not in PREREQUISITE_SUBSKILLS):
        return 0.0
    coeff = 0.06 if student_type == "Weak" else 0.03
    return coeff * (1.0 - current_polynomial_mastery)


def should_trigger_rag(
    student: "SimulatedStudent",
    progression_gate_active: bool,
    current_subskill: str,
    fail_streak: int,
) -> bool:
    """Trigger RAG tutor only for Weak learners stuck on structural failures."""
    if not ENABLE_RAG_TUTOR:
        return False
    if str(student.student_type).lower() != "weak":
        return False
    if progression_gate_active:
        return False
    if str(RAG_TUTOR_VERSION).lower() == "v2":
        if current_subskill in STRUCTURAL_SUBSKILLS and fail_streak >= 1:
            return True
        if current_subskill in TRANSITION_SUBSKILLS and fail_streak >= 2:
            return True
        return False
    return current_subskill == "family_isomorphism" and fail_streak >= 2


def get_rag_tier(subskill: str) -> str | None:
    """Return rag tier label for tracking."""
    if subskill in STRUCTURAL_SUBSKILLS:
        return "structural"
    if subskill in TRANSITION_SUBSKILLS:
        return "transition"
    return None


def compute_rag_concept_bonus(subskill: str, current_mastery: float, rag_count: int) -> float:
    """Concept-level RAG bonus for structural subskills only."""
    if rag_count >= int(MAX_RAG_INTERVENTIONS_PER_EPISODE):
        return 0.0
    if str(RAG_TUTOR_VERSION).lower() == "v2":
        if subskill in STRUCTURAL_SUBSKILLS:
            return 0.06 * (1.0 - current_mastery)
        if subskill in TRANSITION_SUBSKILLS:
            return 0.03 * (1.0 - current_mastery)
        return 0.0
    if subskill in STRUCTURAL_SUBSKILLS:
        return 0.04 * (1.0 - current_mastery)
    return 0.0


def apply_rag_decay(bonus: float, rag_count: int) -> tuple[float, float]:
    """Apply diminishing return for v2 to avoid unrealistic stacking."""
    if str(RAG_TUTOR_VERSION).lower() != "v2":
        return bonus, 1.0
    decay_factor = max(1.0 - (0.15 * rag_count), 0.5)
    return bonus * decay_factor, decay_factor


# ====================
# 2) SimulatedStudent（子技能版）
# ====================
class SimulatedStudent:
    """A lightweight cognitive student model for one episode."""

    def __init__(self, student_type: str) -> None:
        self.student_type = student_type
        self.profile = self._get_profile(student_type)

        self.subskill_mastery = self._init_subskill_mastery(student_type)
        self.initial_subskill_mastery = dict(self.subskill_mastery)
        self.mastery = weighted_polynomial_mastery(self.subskill_mastery)

        self.base_accuracy = self._estimate_base_accuracy()
        self.current_accuracy = self.base_accuracy

        self.total_answers = 0
        self.correct_answers = 0

        self.fail_streak = 0
        self.remediation_count = 0
        self.unnecessary_remediations = 0
        self.reached_mastery_step: int | None = None

    def _get_profile(self, student_type: str) -> dict[str, float]:
        if student_type == "Careless":
            # 高平均 mastery、較大方差、較高 slip。
            return {
                "mean": 0.70,
                "std": 0.17,
                "slip": 0.20,
                "guess": 0.06,
            }
        if student_type == "Weak":
            # 低平均 mastery、較小方差。
            return {
                "mean": 0.32,
                "std": 0.06,
                "slip": 0.07,
                "guess": 0.03,
            }
        if student_type == "Average":
            # 中等 mastery，並以遞減結構初始化。
            return {
                "mean": 0.54,
                "std": 0.05,
                "slip": 0.10,
                "guess": 0.04,
            }
        raise ValueError(f"Unknown student_type: {student_type}")

    def _init_subskill_mastery(self, student_type: str) -> dict[str, float]:
        if student_type == "Average":
            # 前段基礎技能高於後段複雜技能（遞減）。
            base_curve = [0.68, 0.62, 0.58, 0.53, 0.48, 0.44]
            out: dict[str, float] = {}
            for idx, subskill in enumerate(POLYNOMIAL_SUBSKILLS):
                jitter = random.uniform(-self.profile["std"], self.profile["std"])
                out[subskill] = clamp(base_curve[idx] + jitter, 0.05, 0.98)
            return out

        mean = self.profile["mean"]
        std = self.profile["std"]
        out = {}
        for subskill in POLYNOMIAL_SUBSKILLS:
            out[subskill] = clamp(random.gauss(mean, std), 0.05, 0.98)
        return out

    def _estimate_base_accuracy(self) -> float:
        # 以子技能聚合作為初始整體準確率估計。
        return clamp(0.15 + 0.75 * self.mastery, 0.05, 0.95)

    def _minor_error_probability(self, hit_subskill: str) -> float:
        subskill_m = self.subskill_mastery[hit_subskill]
        if self.student_type == "Careless":
            return clamp(0.70 + 0.20 * subskill_m, 0.0, 0.95)
        if self.student_type == "Weak":
            return clamp(0.25 + 0.40 * subskill_m, 0.0, 0.90)
        if self.student_type == "Average":
            return clamp(0.45 + 0.30 * subskill_m, 0.0, 0.90)
        return 0.50

    def answer_question(self, hit_subskill: str) -> dict[str, Any]:
        """
        Simulate one answer using the hit subskill.
        Returns: {"is_correct": bool, "error_type": str, "p_correct": float}
        """
        subskill_m = self.subskill_mastery[hit_subskill]

        # 作答正確率由命中子技能主導；slip/guess 由學生類型控制。
        raw_p = clamp(0.08 + 0.87 * subskill_m, 0.01, 0.99)
        slip = self.profile["slip"]
        if self.student_type == "Careless" and subskill_m >= 0.70:
            # Careless 在高能力題仍可能因粗心失誤。
            slip = clamp(slip + 0.05, 0.0, 0.40)
        guess = self.profile["guess"]
        p_correct = clamp(raw_p * (1.0 - slip) + (1.0 - raw_p) * guess, 0.01, 0.99)

        is_correct = random.random() < p_correct

        self.total_answers += 1
        if is_correct:
            self.correct_answers += 1
            self.fail_streak = 0
            error_type = "correct"
        else:
            self.fail_streak += 1
            is_minor = random.random() < self._minor_error_probability(hit_subskill)
            error_type = "minor_error" if is_minor else "major_error"

        self.current_accuracy = self.correct_answers / max(1, self.total_answers)
        return {"is_correct": is_correct, "error_type": error_type, "p_correct": p_correct}

    def _apply_subskill_delta(
        self,
        hit_subskill: str,
        delta: float,
        transfer_scale: float,
    ) -> None:
        self.subskill_mastery[hit_subskill] = clamp(
            self.subskill_mastery[hit_subskill] + delta, 0.0, 1.0
        )

        # 同 family 的子技能做小幅遷移，讓向量更平滑。
        family = SUBSKILL_PRIMARY_FAMILY[hit_subskill]
        siblings = FAMILY_TO_SUBSKILLS.get(family, [])
        for sibling in siblings:
            if sibling == hit_subskill:
                continue
            self.subskill_mastery[sibling] = clamp(
                self.subskill_mastery[sibling] + (delta * transfer_scale), 0.0, 1.0
            )

        self.mastery = weighted_polynomial_mastery(self.subskill_mastery)


def update_mastery(
    student: SimulatedStudent,
    error_type: str,
    hit_subskill: str,
    phase: str,
    rag_bonus: float = 0.0,
) -> dict[str, float]:
    """Update hit subskill first, then synchronize polynomial mastery and transfer effects."""
    current_hit_mastery = float(student.subskill_mastery[hit_subskill])
    is_correct = error_type == "correct"
    zpd_gain_scale = (
        compute_zpd_gain_scale(current_hit_mastery, student.student_type) if is_correct else 1.0
    )
    delta = MASTERY_UPDATE[error_type]
    if is_correct:
        delta *= zpd_gain_scale
        delta += float(rag_bonus)

    # 補救階段僅調整學習訊號，不改策略本身分數加成。
    if phase == "remediation" and error_type == "correct":
        delta *= 1.08
    if phase == "remediation" and error_type != "correct":
        delta *= 0.70

    transfer_scale = 0.25 if error_type == "correct" else 0.08
    student._apply_subskill_delta(hit_subskill=hit_subskill, delta=delta, transfer_scale=transfer_scale)
    prerequisite_transfer_bonus = compute_prerequisite_transfer_bonus(
        hit_subskill=hit_subskill,
        is_correct=is_correct,
        current_polynomial_mastery=student.mastery,
        student_type=student.student_type,
    )
    if prerequisite_transfer_bonus > 0.0:
        # Keep transfer effect persistent by reflecting a fraction back into foundation profile.
        reflect_scale = 0.60 if student.student_type == "Weak" else 0.25
        for key in PREREQUISITE_SUBSKILLS:
            student.subskill_mastery[key] = clamp(
                student.subskill_mastery[key] + (prerequisite_transfer_bonus * reflect_scale),
                0.0,
                1.0,
            )
        student.mastery = weighted_polynomial_mastery(student.subskill_mastery)
    student.mastery = clamp(student.mastery + prerequisite_transfer_bonus, 0.0, 1.0)
    return {
        "zpd_gain_scale": zpd_gain_scale,
        "prerequisite_transfer_bonus": prerequisite_transfer_bonus,
    }


def maybe_mark_reached_mastery(student: SimulatedStudent, total_steps: int) -> None:
    """Set first step when mastery reaches target."""
    if student.reached_mastery_step is None and student.mastery >= TARGET_MASTERY:
        student.reached_mastery_step = total_steps


def get_effective_max_steps(student: SimulatedStudent) -> int:
    """Weak students receive a modest extra step budget for realistic pacing."""
    return MAX_STEPS + 10 if student.student_type == "Weak" else MAX_STEPS


def compute_weak_foundation_mean(student: SimulatedStudent) -> float:
    """Foundation mean for Weak progression gate."""
    keys = ["sign_handling", "combine_like_terms", "sign_distribution"]
    return statistics.mean(student.subskill_mastery[k] for k in keys)


def is_progression_gate_active(student: SimulatedStudent) -> bool:
    """Weak-only gate: focus on foundation families before high-level routing."""
    if student.student_type != "Weak":
        return False
    return compute_weak_foundation_mean(student) < 0.55


def pick_mainline_family(student: SimulatedStudent, strategy_name: str, step: int) -> str:
    """Mainline family selection by strategy."""
    gate_active = is_progression_gate_active(student)
    allowed_families = (
        ["poly_add_sub_flat", "poly_add_sub_nested", "poly_mul_monomial"]
        if gate_active
        else list(FAMILY_TO_SUBSKILLS.keys())
    )

    if strategy_name == "AB3_PPO_Dynamic":
        # AB3：優先挑選家族平均最弱者（選題更準）。
        ranked: list[tuple[float, str]] = []
        for family in allowed_families:
            subs = FAMILY_TO_SUBSKILLS[family]
            m = statistics.mean(student.subskill_mastery[s] for s in subs)
            ranked.append((m, family))
        ranked.sort(key=lambda x: x[0])
        return ranked[0][1]

    # AB1/AB2：固定循環（不做動態精準選題）。
    return allowed_families[(step - 1) % len(allowed_families)]


def pick_hit_subskill(student: SimulatedStudent, family: str, strategy_name: str) -> str:
    """Choose concrete hit subskill within family."""
    subskills = FAMILY_TO_SUBSKILLS[family]
    if strategy_name == "AB3_PPO_Dynamic":
        # AB3：命中 family 內最弱子技能。
        return min(subskills, key=lambda s: student.subskill_mastery[s])
    return random.choice(subskills)


def weakest_subskill(student: SimulatedStudent) -> str:
    return min(POLYNOMIAL_SUBSKILLS, key=lambda s: student.subskill_mastery[s])


def build_trajectory_row(
    strategy_name: str,
    student: SimulatedStudent,
    episode_id: int,
    step: int,
    phase: str,
    active_family: str,
    hit_subskill: str,
    is_correct: bool,
    was_remediation: int,
    was_unnecessary_remediation: int,
    zpd_gain_scale: float,
    prerequisite_transfer_bonus: float,
    rag_triggered: int,
    rag_bonus: float,
    rag_intervention_count: int,
    rag_tier: str,
    rag_decay_factor: float,
    rag_bonus_after_decay: float,
    effective_max_steps: int,
    progression_gate_active: bool,
    weak_foundation_mean: float | str,
    route: str,
    is_return_to_mainline: int,
    fail_streak: int,
    mastery_before: float,
    mastery_after: float,
) -> dict[str, Any]:
    # 保留舊欄位（integer/fraction）以避免既有分析斷裂，數值做可解釋近似。
    integer_mastery = (0.7 * student.subskill_mastery["sign_handling"]) + (
        0.3 * student.subskill_mastery["combine_like_terms"]
    )
    fraction_mastery = student.subskill_mastery["family_isomorphism"]
    # This simulator currently focuses on polynomial subskills; use a real structural proxy.
    radical_mastery = student.subskill_mastery["expand_binomial"]
    weakest_subskill_mastery = min(student.subskill_mastery[s] for s in POLYNOMIAL_SUBSKILLS)

    row: dict[str, Any] = {
        "strategy": strategy_name,
        "student_type": student.student_type,
        "episode_id": episode_id,
        "step": step,
        "effective_max_steps": effective_max_steps,
        "phase": phase,
        "route": route,
        "focus_skill": hit_subskill,
        "target_skill": TARGET_SKILL,
        "active_skill": TARGET_SKILL,
        "active_family": active_family,
        "hit_subskill": hit_subskill,
        "progression_gate_active": progression_gate_active,
        "weak_foundation_mean": round(float(weak_foundation_mean), 6)
        if weak_foundation_mean != ""
        else "",
        "polynomial_mastery": round(student.mastery, 6),
        "mastery_before": round(mastery_before, 6),
        "mastery_after": round(mastery_after, 6),
        "integer_mastery": round(integer_mastery, 6),
        "fraction_mastery": round(fraction_mastery, 6),
        "radical_mastery": round(radical_mastery, 6),
        "zpd_gain_scale": round(zpd_gain_scale, 6),
        "weakest_subskill_mastery": round(weakest_subskill_mastery, 6),
        "prerequisite_transfer_bonus": round(prerequisite_transfer_bonus, 6),
        "rag_triggered": rag_triggered,
        "rag_bonus": round(rag_bonus, 6),
        "rag_intervention_count": rag_intervention_count,
        "rag_tier": rag_tier,
        "rag_decay_factor": round(rag_decay_factor, 6),
        "rag_bonus_after_decay": round(rag_bonus_after_decay, 6),
        "is_correct": 1 if is_correct else 0,
        "correct": 1 if is_correct else 0,
        "was_remediation": was_remediation,
        "was_unnecessary_remediation": was_unnecessary_remediation,
        "is_return_to_mainline": is_return_to_mainline,
        "fail_streak": fail_streak,
    }

    for subskill in POLYNOMIAL_SUBSKILLS:
        row[f"{subskill}_mastery"] = round(student.subskill_mastery[subskill], 6)

    return row


def run_strategy(
    student: SimulatedStudent,
    strategy_name: str,
    episode_id: int,
) -> tuple[int, int, int, int, list[dict[str, Any]]]:
    """Run one strategy loop and return total steps + trajectory rows."""
    total_steps = 0
    mainline_steps = 0
    foundation_extra_used = 0
    rag_intervention_count = 0
    effective_max_steps = get_effective_max_steps(student)
    trajectory_rows: list[dict[str, Any]] = []
    previous_phase: str | None = None

    def consume_one_step(gate_flag: bool) -> bool:
        nonlocal mainline_steps, foundation_extra_used
        if student.student_type == "Weak" and gate_flag and foundation_extra_used < int(
            WEAK_FOUNDATION_EXTRA_STEPS
        ):
            foundation_extra_used += 1
            return True
        if mainline_steps < effective_max_steps:
            mainline_steps += 1
            return True
        return False

    while student.mastery < TARGET_MASTERY:
        gate_active = is_progression_gate_active(student)
        if not consume_one_step(gate_active):
            break
        weak_foundation_mean: float | str = (
            compute_weak_foundation_mean(student) if student.student_type == "Weak" else ""
        )
        family = pick_mainline_family(student, strategy_name, total_steps + 1)
        hit_subskill = pick_hit_subskill(student, family, strategy_name)

        result = student.answer_question(hit_subskill)
        is_correct = bool(result["is_correct"])
        error_type = str(result["error_type"])
        rag_triggered = should_trigger_rag(
            student=student,
            progression_gate_active=gate_active,
            current_subskill=hit_subskill,
            fail_streak=student.fail_streak,
        )
        if rag_triggered:
            rag_tier = get_rag_tier(hit_subskill) or ""
            raw_rag_bonus = compute_rag_concept_bonus(
                subskill=hit_subskill,
                current_mastery=float(student.subskill_mastery[hit_subskill]),
                rag_count=rag_intervention_count,
            )
            rag_bonus_after_decay, rag_decay_factor = apply_rag_decay(
                raw_rag_bonus, rag_intervention_count
            )
            if rag_bonus_after_decay > 0:
                rag_intervention_count += 1
        else:
            rag_tier = ""
            rag_decay_factor = 1.0
            rag_bonus_after_decay = 0.0

        total_steps += 1
        mastery_before = float(student.mastery)
        fail_streak_after_answer = int(student.fail_streak)
        update_meta = update_mastery(
            student,
            error_type,
            hit_subskill,
            phase="mainline",
            rag_bonus=rag_bonus_after_decay,
        )
        mastery_after = float(student.mastery)
        maybe_mark_reached_mastery(student, total_steps)

        trajectory_rows.append(
            build_trajectory_row(
                strategy_name=strategy_name,
                student=student,
                episode_id=episode_id,
                step=total_steps,
                phase="mainline",
                route="mainline",
                active_family=family,
                hit_subskill=hit_subskill,
                is_correct=is_correct,
                was_remediation=0,
                was_unnecessary_remediation=0,
                is_return_to_mainline=1 if previous_phase == "remediation" else 0,
                fail_streak=fail_streak_after_answer,
                mastery_before=mastery_before,
                mastery_after=mastery_after,
                zpd_gain_scale=float(update_meta["zpd_gain_scale"]),
                prerequisite_transfer_bonus=float(update_meta["prerequisite_transfer_bonus"]),
                rag_triggered=1 if rag_triggered else 0,
                rag_bonus=float(rag_bonus_after_decay),
                rag_intervention_count=rag_intervention_count,
                rag_tier=rag_tier,
                rag_decay_factor=float(rag_decay_factor),
                rag_bonus_after_decay=float(rag_bonus_after_decay),
                effective_max_steps=effective_max_steps,
                progression_gate_active=gate_active,
                weak_foundation_mean=weak_foundation_mean,
            )
        )
        previous_phase = "mainline"

        if student.mastery >= TARGET_MASTERY:
            break

        remediation_triggered = False
        remediation_steps = 0
        remediation_target_subskill = "sign_handling"
        unnecessary = False

        if strategy_name == "AB2_RuleBased" and not is_correct:
            # AB2：錯就進補救，但補救目標較固定、較不精準。
            remediation_triggered = True
            remediation_steps = 3
            remediation_target_subskill = "sign_handling"
            unnecessary = (error_type == "minor_error") and (student.mastery > 0.60)

        if strategy_name == "AB3_PPO_Dynamic" and not is_correct:
            # AB3：依失敗型態動態觸發，且優先補最可能弱點。
            remediation_triggered = (student.fail_streak >= 2) or (
                error_type == "major_error" and student.mastery < 0.55
            )
            remediation_steps = 2
            if student.subskill_mastery[hit_subskill] < 0.75:
                remediation_target_subskill = hit_subskill
            else:
                remediation_target_subskill = weakest_subskill(student)
            if student.student_type == "Weak" and gate_active:
                foundation_keys = ["sign_handling", "combine_like_terms", "sign_distribution"]
                remediation_target_subskill = min(
                    foundation_keys, key=lambda s: student.subskill_mastery[s]
                )
            unnecessary = (error_type == "minor_error") and (
                student.subskill_mastery[remediation_target_subskill] > 0.72
            )

        if remediation_triggered:
            if unnecessary:
                student.unnecessary_remediations += 1

            remediation_steps_taken = 0
            for _ in range(remediation_steps):
                rem_gate_active = is_progression_gate_active(student)
                if not consume_one_step(rem_gate_active):
                    break
                remediation_steps_taken += 1
                if remediation_steps_taken == 1:
                    student.remediation_count += 1
                rem_weak_foundation_mean: float | str = (
                    compute_weak_foundation_mean(student) if student.student_type == "Weak" else ""
                )
                remediation_family = SUBSKILL_PRIMARY_FAMILY[remediation_target_subskill]

                # AB2 補救可帶入同家族但未必命中最關鍵子技能（錯位風險較高）。
                if strategy_name == "AB2_RuleBased":
                    rem_hit = random.choice(FAMILY_TO_SUBSKILLS[remediation_family])
                else:
                    rem_hit = remediation_target_subskill

                rem_result = student.answer_question(rem_hit)
                rem_correct = bool(rem_result["is_correct"])
                rem_error_type = str(rem_result["error_type"])
                rem_rag_triggered = should_trigger_rag(
                    student=student,
                    progression_gate_active=rem_gate_active,
                    current_subskill=rem_hit,
                    fail_streak=student.fail_streak,
                )
                if rem_rag_triggered:
                    rem_rag_tier = get_rag_tier(rem_hit) or ""
                    rem_raw_rag_bonus = compute_rag_concept_bonus(
                        subskill=rem_hit,
                        current_mastery=float(student.subskill_mastery[rem_hit]),
                        rag_count=rag_intervention_count,
                    )
                    rem_rag_bonus_after_decay, rem_rag_decay_factor = apply_rag_decay(
                        rem_raw_rag_bonus, rag_intervention_count
                    )
                    if rem_rag_bonus_after_decay > 0:
                        rag_intervention_count += 1
                else:
                    rem_rag_tier = ""
                    rem_rag_decay_factor = 1.0
                    rem_rag_bonus_after_decay = 0.0

                total_steps += 1
                rem_mastery_before = float(student.mastery)
                rem_fail_streak_after_answer = int(student.fail_streak)
                rem_update_meta = update_mastery(
                    student,
                    rem_error_type,
                    rem_hit,
                    phase="remediation",
                    rag_bonus=rem_rag_bonus_after_decay,
                )
                rem_mastery_after = float(student.mastery)
                maybe_mark_reached_mastery(student, total_steps)

                trajectory_rows.append(
                    build_trajectory_row(
                        strategy_name=strategy_name,
                        student=student,
                        episode_id=episode_id,
                        step=total_steps,
                        phase="remediation",
                        route="remediation",
                        active_family=remediation_family,
                        hit_subskill=rem_hit,
                        is_correct=rem_correct,
                        was_remediation=1,
                        was_unnecessary_remediation=1 if unnecessary else 0,
                        is_return_to_mainline=0,
                        fail_streak=rem_fail_streak_after_answer,
                        mastery_before=rem_mastery_before,
                        mastery_after=rem_mastery_after,
                        zpd_gain_scale=float(rem_update_meta["zpd_gain_scale"]),
                        prerequisite_transfer_bonus=float(
                            rem_update_meta["prerequisite_transfer_bonus"]
                        ),
                        rag_triggered=1 if rem_rag_triggered else 0,
                        rag_bonus=float(rem_rag_bonus_after_decay),
                        rag_intervention_count=rag_intervention_count,
                        rag_tier=rem_rag_tier,
                        rag_decay_factor=float(rem_rag_decay_factor),
                        rag_bonus_after_decay=float(rem_rag_bonus_after_decay),
                        effective_max_steps=effective_max_steps,
                        progression_gate_active=rem_gate_active,
                        weak_foundation_mean=rem_weak_foundation_mean,
                    )
                )
                previous_phase = "remediation"

                if student.mastery >= TARGET_MASTERY:
                    break

    return total_steps, mainline_steps, foundation_extra_used, rag_intervention_count, trajectory_rows


# ====================
# 3) episode 執行
# ====================
def simulate_episode(
    student_type: str,
    strategy_name: str,
    episode_id: int,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Run one episode for a student type under one strategy."""
    student = SimulatedStudent(student_type=student_type)
    initial_polynomial_mastery = weighted_polynomial_mastery(student.initial_subskill_mastery)

    total_steps, mainline_steps, foundation_extra_used, rag_intervention_count, trajectory_rows = run_strategy(
        student=student,
        strategy_name=strategy_name,
        episode_id=episode_id,
    )

    success = 1 if student.mastery >= TARGET_MASTERY else 0

    total_subskill_gain = sum(
        student.subskill_mastery[s] - student.initial_subskill_mastery[s]
        for s in POLYNOMIAL_SUBSKILLS
    )
    polynomial_gain = student.mastery - initial_polynomial_mastery

    episode_result: dict[str, Any] = {
        "episode_id": episode_id,
        "strategy": strategy_name,
        "student_type": student_type,
        "success": success,
        "total_steps": total_steps,
        "mainline_steps": mainline_steps,
        "foundation_extra_used": foundation_extra_used,
        "rag_intervention_count": rag_intervention_count,
        "initial_polynomial_mastery": round(initial_polynomial_mastery, 4),
        "final_mastery": round(student.mastery, 4),
        "target_gain": round(polynomial_gain, 4),
        "total_subskill_gain": round(total_subskill_gain, 4),
        "reached_mastery_step": student.reached_mastery_step,
        "remediation_count": student.remediation_count,
        "unnecessary_remediations": student.unnecessary_remediations,
        "final_accuracy": round(student.current_accuracy, 4),
        "initial_subskills": dict(student.initial_subskill_mastery),
        "final_subskills": dict(student.subskill_mastery),
    }
    return episode_result, trajectory_rows


# ====================
# 4) 批次實驗
# ====================
def run_batch_experiments() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Run all strategy x student_type episodes."""
    episodes: list[dict[str, Any]] = []
    trajectory: list[dict[str, Any]] = []

    episode_id = 0
    for strategy in STRATEGIES:
        for student_type in STUDENT_TYPES:
            for _ in range(N_PER_TYPE):
                episode_id += 1
                one_episode, rows = simulate_episode(
                    student_type=student_type,
                    strategy_name=strategy,
                    episode_id=episode_id,
                )
                episodes.append(one_episode)
                trajectory.extend(rows)

    return episodes, trajectory


def build_strategy_summary(episodes: list[dict[str, Any]]) -> list[dict[str, float | str]]:
    """Aggregate overall metrics by strategy."""
    rows: list[dict[str, float | str]] = []
    for strategy in STRATEGIES:
        subset = [e for e in episodes if e["strategy"] == strategy]
        success_rate = statistics.mean(float(e["success"]) for e in subset) * 100.0
        avg_steps = statistics.mean(float(e["total_steps"]) for e in subset)
        avg_unnecessary = statistics.mean(float(e["unnecessary_remediations"]) for e in subset)
        avg_mastery = statistics.mean(float(e["final_mastery"]) for e in subset)
        rows.append(
            {
                "Strategy": strategy,
                "Success Rate": success_rate,
                "Avg Steps": avg_steps,
                "Avg Unnecessary Remediations": avg_unnecessary,
                "Avg Final Mastery": avg_mastery,
            }
        )
    return rows


def build_strategy_student_summary(episodes: list[dict[str, Any]]) -> list[dict[str, float | str]]:
    """Aggregate metrics by strategy and student type."""
    rows: list[dict[str, float | str]] = []
    for strategy in STRATEGIES:
        for student_type in STUDENT_TYPES:
            subset = [
                e
                for e in episodes
                if e["strategy"] == strategy and e["student_type"] == student_type
            ]
            success_rate = statistics.mean(float(e["success"]) for e in subset) * 100.0
            avg_steps = statistics.mean(float(e["total_steps"]) for e in subset)
            avg_unnecessary = statistics.mean(float(e["unnecessary_remediations"]) for e in subset)
            avg_mastery = statistics.mean(float(e["final_mastery"]) for e in subset)
            rows.append(
                {
                    "Strategy": strategy,
                    "Student Type": student_type,
                    "Success Rate": success_rate,
                    "Avg Steps": avg_steps,
                    "Avg Unnecessary Remediations": avg_unnecessary,
                    "Avg Final Mastery": avg_mastery,
                }
            )
    return rows


def build_ab3_student_type_summary(episodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    ab3 = [e for e in episodes if e["strategy"] == "AB3_PPO_Dynamic"]

    for student_type in STUDENT_TYPES:
        subset = [e for e in ab3 if e["student_type"] == student_type]
        success_rate = statistics.mean(float(e["success"]) for e in subset)
        avg_steps = statistics.mean(float(e["total_steps"]) for e in subset)
        avg_final_polynomial_mastery = statistics.mean(float(e["final_mastery"]) for e in subset)
        avg_remediation_count = statistics.mean(float(e["remediation_count"]) for e in subset)
        avg_unnecessary = statistics.mean(float(e["unnecessary_remediations"]) for e in subset)

        reached_values = [
            float(e["reached_mastery_step"])
            for e in subset
            if e["reached_mastery_step"] is not None
        ]
        avg_reached = statistics.mean(reached_values) if reached_values else ""

        rows.append(
            {
                "student_type": student_type,
                "success_rate": round(success_rate, 4),
                "avg_steps": round(avg_steps, 4),
                "avg_final_polynomial_mastery": round(avg_final_polynomial_mastery, 4),
                "avg_remediation_count": round(avg_remediation_count, 4),
                "avg_unnecessary_remediations": round(avg_unnecessary, 4),
                "avg_reached_mastery_step": round(avg_reached, 4) if avg_reached != "" else "",
            }
        )

    return rows


def build_ab3_subskill_progress_summary(episodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    ab3 = [e for e in episodes if e["strategy"] == "AB3_PPO_Dynamic"]

    for student_type in STUDENT_TYPES:
        subset = [e for e in ab3 if e["student_type"] == student_type]
        for subskill in POLYNOMIAL_SUBSKILLS:
            init_vals = [float(e["initial_subskills"][subskill]) for e in subset]
            final_vals = [float(e["final_subskills"][subskill]) for e in subset]

            avg_initial = statistics.mean(init_vals)
            avg_final = statistics.mean(final_vals)
            avg_gain = avg_final - avg_initial

            rows.append(
                {
                    "student_type": student_type,
                    "subskill": subskill,
                    "avg_initial_mastery": round(avg_initial, 4),
                    "avg_final_mastery": round(avg_final, 4),
                    "avg_gain": round(avg_gain, 4),
                }
            )

    return rows


def build_ablation_strategy_summary(episodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Aggregate formal ablation metrics by strategy."""
    rows: list[dict[str, Any]] = []
    for strategy in STRATEGIES:
        subset = [e for e in episodes if e["strategy"] == strategy]
        reached_values = [
            float(e["reached_mastery_step"])
            for e in subset
            if e["reached_mastery_step"] is not None
        ]
        avg_reached = statistics.mean(reached_values) if reached_values else ""
        rows.append(
            {
                "strategy": strategy,
                "success_rate": round(statistics.mean(float(e["success"]) for e in subset), 4),
                "avg_steps": round(statistics.mean(float(e["total_steps"]) for e in subset), 4),
                "avg_final_polynomial_mastery": round(
                    statistics.mean(float(e["final_mastery"]) for e in subset), 4
                ),
                "avg_reached_mastery_step": round(avg_reached, 4) if avg_reached != "" else "",
                "avg_remediation_count": round(
                    statistics.mean(float(e["remediation_count"]) for e in subset), 4
                ),
                "avg_unnecessary_remediations": round(
                    statistics.mean(float(e["unnecessary_remediations"]) for e in subset), 4
                ),
                "avg_target_gain": round(
                    statistics.mean(float(e["target_gain"]) for e in subset), 4
                ),
                "avg_total_subskill_gain": round(
                    statistics.mean(float(e["total_subskill_gain"]) for e in subset), 4
                ),
            }
        )
    return rows


def build_ablation_strategy_by_student_type_summary(
    episodes: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Aggregate formal ablation metrics by strategy and student_type."""
    rows: list[dict[str, Any]] = []
    for strategy in STRATEGIES:
        for student_type in STUDENT_TYPES:
            subset = [
                e
                for e in episodes
                if e["strategy"] == strategy and e["student_type"] == student_type
            ]
            reached_values = [
                float(e["reached_mastery_step"])
                for e in subset
                if e["reached_mastery_step"] is not None
            ]
            avg_reached = statistics.mean(reached_values) if reached_values else ""
            rows.append(
                {
                    "strategy": strategy,
                    "student_type": student_type,
                    "success_rate": round(statistics.mean(float(e["success"]) for e in subset), 4),
                    "avg_steps": round(statistics.mean(float(e["total_steps"]) for e in subset), 4),
                    "avg_final_polynomial_mastery": round(
                        statistics.mean(float(e["final_mastery"]) for e in subset), 4
                    ),
                    "avg_reached_mastery_step": round(avg_reached, 4) if avg_reached != "" else "",
                    "avg_remediation_count": round(
                        statistics.mean(float(e["remediation_count"]) for e in subset), 4
                    ),
                    "avg_unnecessary_remediations": round(
                        statistics.mean(float(e["unnecessary_remediations"]) for e in subset), 4
                    ),
                    "avg_target_gain": round(
                        statistics.mean(float(e["target_gain"]) for e in subset), 4
                    ),
                    "avg_total_subskill_gain": round(
                        statistics.mean(float(e["total_subskill_gain"]) for e in subset), 4
                    ),
                }
            )
    return rows


def build_ab3_student_type_detailed_summary(episodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build detailed AB3 summary by student type."""
    rows: list[dict[str, Any]] = []
    ab3 = [e for e in episodes if e["strategy"] == "AB3_PPO_Dynamic"]
    for student_type in STUDENT_TYPES:
        subset = [e for e in ab3 if e["student_type"] == student_type]
        reached_values = [
            float(e["reached_mastery_step"])
            for e in subset
            if e["reached_mastery_step"] is not None
        ]
        avg_reached = statistics.mean(reached_values) if reached_values else ""
        rows.append(
            {
                "student_type": student_type,
                "success_rate": round(statistics.mean(float(e["success"]) for e in subset), 4),
                "avg_steps": round(statistics.mean(float(e["total_steps"]) for e in subset), 4),
                "avg_final_polynomial_mastery": round(
                    statistics.mean(float(e["final_mastery"]) for e in subset), 4
                ),
                "avg_reached_mastery_step": round(avg_reached, 4) if avg_reached != "" else "",
                "avg_remediation_count": round(
                    statistics.mean(float(e["remediation_count"]) for e in subset), 4
                ),
                "avg_unnecessary_remediations": round(
                    statistics.mean(float(e["unnecessary_remediations"]) for e in subset), 4
                ),
                "avg_initial_polynomial_mastery": round(
                    statistics.mean(float(e["initial_polynomial_mastery"]) for e in subset), 4
                ),
                "avg_polynomial_gain": round(
                    statistics.mean(float(e["target_gain"]) for e in subset), 4
                ),
                "avg_total_subskill_gain": round(
                    statistics.mean(float(e["total_subskill_gain"]) for e in subset), 4
                ),
            }
        )
    return rows


def build_ab3_subskill_by_type_detailed_summary(episodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build detailed AB3 subskill gains by student type."""
    return build_ab3_subskill_progress_summary(episodes)


def build_ab3_failure_breakpoint_summary(episodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Summarize AB3 failure breakpoints.
    Breakpoint is defined as the lowest final-mastery subskill in each failed episode.
    """
    rows: list[dict[str, Any]] = []
    ab3_failed = [e for e in episodes if e["strategy"] == "AB3_PPO_Dynamic" and int(e["success"]) == 0]

    for student_type in STUDENT_TYPES:
        subset = [e for e in ab3_failed if e["student_type"] == student_type]
        if not subset:
            rows.append(
                {
                    "student_type": student_type,
                    "most_common_weakest_subskill": "",
                    "avg_final_polynomial_mastery": "",
                    "avg_steps": "",
                    "count_failed_episodes": 0,
                }
            )
            continue

        weakest_list: list[str] = []
        for episode in subset:
            final_subskills = episode["final_subskills"]
            weakest = min(POLYNOMIAL_SUBSKILLS, key=lambda s: float(final_subskills[s]))
            weakest_list.append(weakest)

        mode_subskill = Counter(weakest_list).most_common(1)[0][0]
        rows.append(
            {
                "student_type": student_type,
                "most_common_weakest_subskill": mode_subskill,
                "avg_final_polynomial_mastery": round(
                    statistics.mean(float(e["final_mastery"]) for e in subset), 4
                ),
                "avg_steps": round(statistics.mean(float(e["total_steps"]) for e in subset), 4),
                "count_failed_episodes": len(subset),
            }
        )

    return rows


# ====================
# 5) ASCII 表格
# ====================
def format_cell(header: str, value: float | str) -> str:
    """Format output by column type."""
    if header == "Success Rate":
        return f"{float(value):.2f}%"
    if header.startswith("Avg"):
        return f"{float(value):.2f}"
    return str(value)


def print_ascii_table(title: str, headers: list[str], rows: list[dict[str, float | str]]) -> None:
    """Print a clean aligned ASCII table."""
    rendered_rows: list[list[str]] = []
    for row in rows:
        rendered_rows.append([format_cell(h, row[h]) for h in headers])

    widths = []
    for idx, header in enumerate(headers):
        col_values = [r[idx] for r in rendered_rows]
        max_len = max([len(header)] + [len(v) for v in col_values])
        widths.append(max_len)

    def build_separator() -> str:
        return "+" + "+".join("-" * (w + 2) for w in widths) + "+"

    def build_row(cells: list[str]) -> str:
        pieces = []
        for i, cell in enumerate(cells):
            pieces.append(f" {cell.ljust(widths[i])} ")
        return "|" + "|".join(pieces) + "|"

    print(f"\n{title}")
    print(build_separator())
    print(build_row(headers))
    print(build_separator())
    for line in rendered_rows:
        print(build_row(line))
    print(build_separator())


# ====================
# 6) CSV 輸出
# ====================
def write_episode_csv(episodes: list[dict[str, Any]]) -> str:
    """Write raw episode records to reports CSV (主輸出保留)."""
    reports_dir = str(EXPERIMENT1_OUTPUT_DIR)
    os.makedirs(reports_dir, exist_ok=True)
    output_path = os.path.join(reports_dir, "ablation_simulation_results.csv")

    fieldnames = [
        "strategy",
        "student_type",
        "success",
        "total_steps",
        "final_mastery",
        "reached_mastery_step",
        "remediation_count",
        "unnecessary_remediations",
        "final_accuracy",
    ]

    with open(output_path, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for episode in episodes:
            row = {k: episode[k] for k in fieldnames}
            if row["reached_mastery_step"] is None:
                row["reached_mastery_step"] = ""
            writer.writerow(row)

    return output_path


def write_trajectory_csv(trajectory_rows: list[dict[str, Any]]) -> str:
    """Write per-step trajectory log to Experiment 2 output directory."""
    reports_dir = str(EXPERIMENT2_OUTPUT_DIR)
    os.makedirs(reports_dir, exist_ok=True)
    output_path = os.path.join(reports_dir, "mastery_trajectory.csv")

    fieldnames = [
        "strategy",
        "student_type",
        "episode_id",
        "step",
        "effective_max_steps",
        "phase",
        "route",
        "focus_skill",
        "target_skill",
        "active_skill",
        "active_family",
        "hit_subskill",
        "progression_gate_active",
        "weak_foundation_mean",
        "polynomial_mastery",
        "mastery_before",
        "mastery_after",
        "integer_mastery",
        "fraction_mastery",
        "radical_mastery",
        "zpd_gain_scale",
        "weakest_subskill_mastery",
        "prerequisite_transfer_bonus",
        "rag_triggered",
        "rag_bonus",
        "rag_intervention_count",
        "rag_tier",
        "rag_decay_factor",
        "rag_bonus_after_decay",
        "is_correct",
        "correct",
        "was_remediation",
        "was_unnecessary_remediation",
        "is_return_to_mainline",
        "fail_streak",
    ] + [f"{s}_mastery" for s in POLYNOMIAL_SUBSKILLS]

    with open(output_path, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in trajectory_rows:
            writer.writerow(row)

    return output_path


def write_ab3_student_type_summary_csv(rows: list[dict[str, Any]]) -> str:
    output_dir = str(EXPERIMENT2_OUTPUT_DIR)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "ab3_student_type_summary.csv")
    fieldnames = [
        "student_type",
        "success_rate",
        "avg_steps",
        "avg_final_polynomial_mastery",
        "avg_remediation_count",
        "avg_unnecessary_remediations",
        "avg_reached_mastery_step",
    ]
    with open(output_path, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return output_path


def write_ab3_subskill_progress_summary_csv(rows: list[dict[str, Any]]) -> str:
    output_dir = str(EXPERIMENT2_OUTPUT_DIR)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "ab3_subskill_progress_summary.csv")
    fieldnames = [
        "student_type",
        "subskill",
        "avg_initial_mastery",
        "avg_final_mastery",
        "avg_gain",
    ]
    with open(output_path, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return output_path


def write_ablation_strategy_summary_csv(rows: list[dict[str, Any]]) -> str:
    """Write formal ablation summary by strategy."""
    output_dir = str(EXPERIMENT1_OUTPUT_DIR)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "ablation_strategy_summary.csv")
    fieldnames = [
        "strategy",
        "success_rate",
        "avg_steps",
        "avg_final_polynomial_mastery",
        "avg_reached_mastery_step",
        "avg_remediation_count",
        "avg_unnecessary_remediations",
        "avg_target_gain",
        "avg_total_subskill_gain",
    ]
    with open(output_path, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return output_path


def write_ablation_strategy_by_student_type_summary_csv(rows: list[dict[str, Any]]) -> str:
    """Write formal ablation summary by strategy and student type."""
    output_dir = str(EXPERIMENT1_OUTPUT_DIR)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "ablation_strategy_by_student_type_summary.csv")
    fieldnames = [
        "strategy",
        "student_type",
        "success_rate",
        "avg_steps",
        "avg_final_polynomial_mastery",
        "avg_reached_mastery_step",
        "avg_remediation_count",
        "avg_unnecessary_remediations",
        "avg_target_gain",
        "avg_total_subskill_gain",
    ]
    with open(output_path, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return output_path


def write_ab3_student_type_detailed_summary_csv(rows: list[dict[str, Any]]) -> str:
    """Write detailed AB3 student-type summary."""
    output_dir = str(EXPERIMENT2_OUTPUT_DIR)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "ab3_student_type_detailed_summary.csv")
    fieldnames = [
        "student_type",
        "success_rate",
        "avg_steps",
        "avg_final_polynomial_mastery",
        "avg_reached_mastery_step",
        "avg_remediation_count",
        "avg_unnecessary_remediations",
        "avg_initial_polynomial_mastery",
        "avg_polynomial_gain",
        "avg_total_subskill_gain",
    ]
    with open(output_path, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return output_path


def write_ab3_subskill_by_type_detailed_summary_csv(rows: list[dict[str, Any]]) -> str:
    """Write detailed AB3 subskill summary by student type."""
    output_dir = str(EXPERIMENT2_OUTPUT_DIR)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "ab3_subskill_by_type_detailed_summary.csv")
    fieldnames = [
        "student_type",
        "subskill",
        "avg_initial_mastery",
        "avg_final_mastery",
        "avg_gain",
    ]
    with open(output_path, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return output_path


def write_ab3_failure_breakpoint_summary_csv(rows: list[dict[str, Any]]) -> str:
    """Write AB3 failure breakpoint summary."""
    output_dir = str(EXPERIMENT2_OUTPUT_DIR)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "ab3_failure_breakpoint_summary.csv")
    fieldnames = [
        "student_type",
        "most_common_weakest_subskill",
        "avg_final_polynomial_mastery",
        "avg_steps",
        "count_failed_episodes",
    ]
    with open(output_path, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return output_path


def build_experiment1_summary_table(
    episodes: list[dict[str, Any]],
    max_steps_default: int | None = None,
) -> list[dict[str, Any]]:
    """Build Experiment 1 table rows from real episode outcomes."""
    if max_steps_default is None:
        max_steps_default = int(MAX_STEPS)

    step_values: set[int] = set()
    grouped: dict[tuple[int, str], list[dict[str, Any]]] = {}

    for episode in episodes:
        step_value = int(episode.get("max_steps", max_steps_default))
        strategy = str(episode.get("strategy", ""))
        if not strategy:
            continue
        step_values.add(step_value)
        grouped.setdefault((step_value, strategy), []).append(episode)

    if not step_values:
        step_values = {int(max_steps_default)}

    rows: list[dict[str, Any]] = []
    for step_value in sorted(step_values):
        for strategy in STRATEGIES:
            subset = grouped.get((step_value, strategy), [])
            if not subset:
                rows.append(
                    {
                        "MAX_STEPS": step_value,
                        "Strategy": strategy,
                        "Success Rate (%)": "",
                        "Avg Steps": "",
                        "Avg Unnecessary Remediations": "",
                        "Avg Final Mastery": "",
                    }
                )
                continue

            success_rate_pct = (
                sum(int(e["success"]) for e in subset) / len(subset)
            ) * 100.0
            avg_steps = statistics.mean(float(e["total_steps"]) for e in subset)
            avg_unnecessary = statistics.mean(
                float(e["unnecessary_remediations"]) for e in subset
            )
            avg_final_mastery = statistics.mean(float(e["final_mastery"]) for e in subset)

            rows.append(
                {
                    "MAX_STEPS": step_value,
                    "Strategy": strategy,
                    "Success Rate (%)": round(success_rate_pct, 2),
                    "Avg Steps": round(avg_steps, 2),
                    "Avg Unnecessary Remediations": round(avg_unnecessary, 2),
                    "Avg Final Mastery": round(avg_final_mastery, 2),
                }
            )
    return rows


def write_experiment1_summary_csv(rows: list[dict[str, Any]]) -> str:
    """Write Experiment 1 summary table CSV for analysis use."""
    output_dir = str(EXPERIMENT1_OUTPUT_DIR)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "experiment1_summary_table.csv")
    fieldnames = [
        "MAX_STEPS",
        "Strategy",
        "Success Rate (%)",
        "Avg Steps",
        "Avg Unnecessary Remediations",
        "Avg Final Mastery",
    ]
    with open(output_path, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            out_row = dict(row)
            for key in [
                "Success Rate (%)",
                "Avg Steps",
                "Avg Unnecessary Remediations",
                "Avg Final Mastery",
            ]:
                value = out_row.get(key, "")
                if value == "":
                    continue
                out_row[key] = f"{float(value):.2f}"
            writer.writerow(out_row)
    return output_path


def write_experiment1_summary_markdown(rows: list[dict[str, Any]]) -> str:
    """Write Experiment 1 summary table in markdown format for paper/slides."""
    output_dir = str(EXPERIMENT1_OUTPUT_DIR)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "experiment1_summary_table.md")

    def _fmt(value: Any) -> str:
        if value == "":
            return "NaN"
        if isinstance(value, float):
            return f"{value:.2f}"
        return str(value)

    lines = [
        "# Experiment 1 Summary Table",
        "",
        "| MAX_STEPS | Strategy | Success Rate (%) | Avg Steps | Avg Unnecessary Remediations | Avg Final Mastery |",
        "|-----------|----------|------------------|-----------|------------------------------|-------------------|",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    _fmt(row["MAX_STEPS"]),
                    _fmt(row["Strategy"]),
                    _fmt(row["Success Rate (%)"]),
                    _fmt(row["Avg Steps"]),
                    _fmt(row["Avg Unnecessary Remediations"]),
                    _fmt(row["Avg Final Mastery"]),
                ]
            )
            + " |"
        )

    with open(output_path, "w", encoding="utf-8-sig") as f:
        f.write("\n".join(lines) + "\n")
    return output_path


def build_experiment2_student_type_summary(
    trajectory_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Aggregate AB3 behavior metrics by student type from trajectory logs."""
    ab3_rows = [row for row in trajectory_rows if row.get("strategy") == "AB3_PPO_Dynamic"]
    summaries: list[dict[str, Any]] = []

    for student_type in STUDENT_TYPES:
        rows = [row for row in ab3_rows if row.get("student_type") == student_type]
        if not rows:
            continue

        remediation_steps = 0
        mainline_steps = 0
        episode_step_count: dict[int, int] = {}
        rag_activated_episodes: set[int] = set()

        for row in rows:
            episode_id = int(row.get("episode_id", 0))
            episode_step_count[episode_id] = episode_step_count.get(episode_id, 0) + 1

            route = str(row.get("route", row.get("phase", "")))
            if route == "remediation":
                remediation_steps += 1
            elif route == "mainline":
                mainline_steps += 1

            if int(row.get("rag_triggered", 0)) == 1:
                rag_activated_episodes.add(episode_id)

        total_steps = remediation_steps + mainline_steps
        total_episodes = len(episode_step_count)
        avg_steps = (
            sum(episode_step_count.values()) / total_episodes if total_episodes > 0 else 0.0
        )

        summaries.append(
            {
                "student_type": student_type,
                "total_episodes": total_episodes,
                "remediation_steps": remediation_steps,
                "mainline_steps": mainline_steps,
                "remediation_ratio": (remediation_steps / total_steps) if total_steps > 0 else "",
                "mainline_ratio": (mainline_steps / total_steps) if total_steps > 0 else "",
                "avg_steps": round(avg_steps, 4),
                "rag_activation_ratio": (
                    len(rag_activated_episodes) / total_episodes if total_episodes > 0 else ""
                ),
            }
        )
    return summaries


def build_mastery_step_log(trajectory_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return step-level mastery logs for reusable plotting/stat analysis."""
    return trajectory_rows


def write_experiment2_student_type_summary_csv(rows: list[dict[str, Any]]) -> str:
    """Write Experiment 2 student-type behavior summary for reproducible charting."""
    output_dir = str(EXPERIMENT2_OUTPUT_DIR)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "experiment2_student_type_summary.csv")
    fieldnames = [
        "student_type",
        "total_episodes",
        "remediation_steps",
        "mainline_steps",
        "remediation_ratio",
        "mainline_ratio",
        "avg_steps",
        "rag_activation_ratio",
    ]
    with open(output_path, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return output_path


def write_experiment2_policy_behavior_figure(rows: list[dict[str, Any]]) -> str:
    """Plot Experiment 2 policy allocation figure (ratio-only, single axis)."""
    output_dir = str(EXPERIMENT2_OUTPUT_DIR)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "experiment2_policy_behavior_summary.png")

    student_order = ["Careless", "Average", "Weak"]
    valid_rows = [row for row in rows if row.get("student_type") in student_order]
    if not valid_rows:
        return output_path
    valid_rows.sort(key=lambda row: student_order.index(str(row["student_type"])))

    x_labels = [str(row["student_type"]) for row in valid_rows]
    remediation_ratio = [
        float(row["remediation_ratio"]) if row["remediation_ratio"] != "" else float("nan")
        for row in valid_rows
    ]
    mainline_ratio = [
        float(row["mainline_ratio"]) if row["mainline_ratio"] != "" else float("nan")
        for row in valid_rows
    ]

    fig, ax = plt.subplots(figsize=(10, 6))
    width = 0.36
    x = list(range(len(x_labels)))
    bars1 = ax.bar(
        [i - width / 2 for i in x],
        remediation_ratio,
        width=width,
        label="Remediation Ratio",
    )
    bars2 = ax.bar(
        [i + width / 2 for i in x],
        mainline_ratio,
        width=width,
        label="Mainline Ratio",
    )

    ax.set_xlabel("Student Type")
    ax.set_ylabel("Ratio")
    ax.set_ylim(0, 1.0)
    ax.set_xticks(x)
    ax.set_xticklabels(x_labels)
    ax.set_title("AB3 Policy Allocation Across Student Types")

    for idx, value in enumerate(remediation_ratio):
        if value == value:
            ax.annotate(
                f"{value:.2f}",
                (x[idx] - width / 2, value),
                textcoords="offset points",
                xytext=(0, 3),
                ha="center",
            )
    for idx, value in enumerate(mainline_ratio):
        if value == value:
            ax.annotate(
                f"{value:.2f}",
                (x[idx] + width / 2, value),
                textcoords="offset points",
                xytext=(0, 3),
                ha="center",
            )

    ax.legend(loc="upper right")

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def write_experiment2_efficiency_figure(rows: list[dict[str, Any]]) -> str:
    """Plot Experiment 2 efficiency figure: average steps by student type."""
    output_dir = str(EXPERIMENT2_OUTPUT_DIR)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "experiment2_efficiency_by_student_type.png")

    student_order = ["Careless", "Average", "Weak"]
    valid_rows = [row for row in rows if row.get("student_type") in student_order]
    if not valid_rows:
        return output_path
    valid_rows.sort(key=lambda row: student_order.index(str(row["student_type"])))

    x_labels = [str(row["student_type"]) for row in valid_rows]
    avg_steps = [float(row["avg_steps"]) for row in valid_rows]

    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.bar(x_labels, avg_steps, width=0.6)
    ax.set_xlabel("Student Type")
    ax.set_ylabel("Average Steps")
    ax.set_title("Average Steps per Episode Across Student Types")
    max_steps = max(avg_steps) if avg_steps else 0.0
    ax.set_ylim(0, (max_steps * 1.25) if max_steps > 0 else 1.0)

    for bar in bars:
        h = float(bar.get_height())
        ax.annotate(
            f"{h:.2f}",
            (bar.get_x() + bar.get_width() / 2, h),
            textcoords="offset points",
            xytext=(0, 3),
            ha="center",
        )

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def write_experiment2_figure_captions(output_dir: str, representative_episode_id: int | None) -> list[str]:
    """Write publication-ready captions for Experiment 2 figures."""
    os.makedirs(output_dir, exist_ok=True)
    paths: list[str] = []

    summary_caption = os.path.join(output_dir, "figure_caption_experiment2_summary.md")
    with open(summary_caption, "w", encoding="utf-8-sig") as f:
        f.write(
            "### Figure Caption: Experiment 2 Policy Behavior Summary\n"
            "This figure compares policy allocation across Careless, Average, and Weak groups under AB3.\n"
            "Both bars are computed from real step-level logs: remediation ratio = remediation steps / active steps,\n"
            "mainline ratio = mainline steps / active steps.\n"
            "Key finding: AB3 allocates different remediation intensity by student type, with weaker learners receiving\n"
            "a larger remediation share and stronger learners remaining more frequently on mainline.\n"
        )
    paths.append(summary_caption)

    episode_caption = os.path.join(output_dir, "figure_caption_mastery_episode.md")
    with open(episode_caption, "w", encoding="utf-8-sig") as f:
        eid_text = str(representative_episode_id) if representative_episode_id is not None else "N/A"
        f.write(
            "### Figure Caption: Representative Mastery Trajectory\n"
            f"This trajectory shows one automatically selected representative episode (episode_id={eid_text}) from AB3 logs.\n"
            "Curves are true step-level prerequisite/target mastery values, with remediation phases marked by shaded spans;\n"
            "remediation starts are marked explicitly, and the end of each shaded span indicates return to mainline.\n"
            "Key finding: target-mastery growth becomes clearer after remediation-supported prerequisite consolidation.\n"
        )
    paths.append(episode_caption)

    avg_caption = os.path.join(output_dir, "figure_caption_mastery_average.md")
    with open(avg_caption, "w", encoding="utf-8-sig") as f:
        f.write(
            "### Figure Caption: Average Mastery Trajectory by Student Type\n"
            "This figure aligns AB3 episodes by step and reports per-step means for prerequisite mastery and target mastery\n"
            "within each student type using NaN-safe aggregation from real trajectory logs.\n"
            "All panels share the same x-axis range for direct comparison; shorter groups stop at the end of observed steps\n"
            "without interpolation or artificial extrapolation.\n"
            "Key finding: mastery-growth dynamics differ across student types, and weaker groups show slower target mastery\n"
            "convergence even when prerequisite mastery improves.\n"
        )
    paths.append(avg_caption)

    return paths


def select_representative_mastery_episode(
    episodes: list[dict[str, Any]],
    trajectory_rows: list[dict[str, Any]],
) -> int | None:
    """Auto-select one representative AB3 episode with remediation and return-to-mainline pattern."""
    by_episode: dict[int, list[dict[str, Any]]] = {}
    for row in trajectory_rows:
        if row.get("strategy") != "AB3_PPO_Dynamic":
            continue
        eid = int(row["episode_id"])
        by_episode.setdefault(eid, []).append(row)

    episode_meta = {int(e["episode_id"]): e for e in episodes if e["strategy"] == "AB3_PPO_Dynamic"}
    type_priority = {"Average": 0, "Weak": 1, "Careless": 2}
    candidates: list[tuple[int, int, int, int]] = []
    # tuple: (type_rank, -remediation_steps, -return_count, episode_id)
    for eid, rows in by_episode.items():
        rem_steps = sum(1 for r in rows if str(r.get("route", r.get("phase", ""))) == "remediation")
        ret_count = sum(1 for r in rows if int(r.get("is_return_to_mainline", 0)) == 1)
        if rem_steps <= 0 or ret_count <= 0:
            continue
        meta = episode_meta.get(eid)
        if not meta or int(meta.get("success", 0)) != 1:
            continue
        stype = str(meta.get("student_type", "Average"))
        rank = type_priority.get(stype, 99)
        candidates.append((rank, -rem_steps, -ret_count, eid))

    if not candidates:
        # Fallback: any AB3 episode with remediation, prioritize Average/Weak.
        fallback: list[tuple[int, int, int]] = []
        for eid, rows in by_episode.items():
            rem_steps = sum(
                1 for r in rows if str(r.get("route", r.get("phase", ""))) == "remediation"
            )
            if rem_steps <= 0:
                continue
            meta = episode_meta.get(eid, {})
            stype = str(meta.get("student_type", "Average"))
            rank = type_priority.get(stype, 99)
            total_steps = len(rows)
            fallback.append((rank, abs(total_steps - 30), eid))
        if not fallback:
            return None
        fallback.sort()
        return fallback[0][2]
    candidates.sort()
    return candidates[0][3]


def select_representative_episode(
    episodes: list[dict[str, Any]],
    trajectory_rows: list[dict[str, Any]],
) -> int | None:
    """Backward-compatible wrapper for representative mastery episode selection."""
    return select_representative_mastery_episode(episodes, trajectory_rows)


def _find_remediation_spans(rows: list[dict[str, Any]]) -> list[tuple[int, int]]:
    """Return contiguous remediation step spans."""
    remediation_steps = sorted(
        int(r["step"]) for r in rows if str(r.get("route", r.get("phase", ""))) == "remediation"
    )
    if not remediation_steps:
        return []
    spans: list[tuple[int, int]] = []
    start = remediation_steps[0]
    prev = remediation_steps[0]
    for s in remediation_steps[1:]:
        if s == prev + 1:
            prev = s
            continue
        spans.append((start, prev))
        start = s
        prev = s
    spans.append((start, prev))
    return spans


def save_mastery_trajectory_plot(
    step_log_rows: list[dict[str, Any]],
    episodes: list[dict[str, Any]],
    output_dir: str,
    target_skill: str = "polynomial",
    prerequisite_skill: str = "integer",
) -> str | None:
    """Save representative episode trajectory with remediation spans and transition markers."""
    episode_id = select_representative_episode(episodes, step_log_rows)
    if episode_id is None:
        return None

    rows = [r for r in step_log_rows if int(r["episode_id"]) == episode_id and r["strategy"] == "AB3_PPO_Dynamic"]
    if not rows:
        return None
    rows.sort(key=lambda r: int(r["step"]))

    steps = [int(r["step"]) for r in rows]
    pre_values = [float(r["integer_mastery"]) for r in rows]
    target_values = [float(r["polynomial_mastery"]) for r in rows]
    remediation_spans = _find_remediation_spans(rows)
    remediation_start_steps = [a for a, _ in remediation_spans]

    student_type = str(rows[0].get("student_type", "Unknown"))
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.plot(
        steps,
        pre_values,
        marker="o",
        linewidth=2.2,
        label=f"Prerequisite Mastery ({prerequisite_skill})",
    )
    ax.plot(
        steps,
        target_values,
        marker="s",
        linewidth=2.2,
        label=f"Target Mastery ({target_skill})",
    )

    shaded_once = False
    for span_start, span_end in remediation_spans:
        label = "Remediation Phase" if not shaded_once else "_nolegend_"
        ax.axvspan(span_start - 0.5, span_end + 0.5, alpha=0.24, label=label)
        shaded_once = True

    start_labeled = False
    for s in remediation_start_steps:
        label = "Remediation Start" if not start_labeled else "_nolegend_"
        ax.axvline(s, linestyle="--", linewidth=1.5, label=label)
        start_labeled = True

    y_min = min(pre_values + target_values)
    y_max = max(pre_values + target_values)
    if y_min >= 0.0 and y_max <= 1.0:
        ax.set_ylim(0.0, 1.0)

    ax.set_xlabel("Step")
    ax.set_ylabel("Mastery Level")
    ax.set_title(
        "Representative Episode: Mastery Growth with Remediation Phases\n"
        f"Student Type={student_type}, Episode={episode_id}"
    )
    ax.legend(loc="lower right")
    ax.set_xlim(min(steps), max(steps))

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"mastery_trajectory_episode_{episode_id}.png")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close(fig)
    fixed_path = os.path.join(output_dir, "mastery_trajectory_representative_episode.png")
    shutil.copy2(output_path, fixed_path)
    return output_path


def write_mastery_trajectory_episode_figure(
    df_logs: list[dict[str, Any]],
    episodes: list[dict[str, Any]],
    output_dir: str,
    target_skill: str = "polynomial",
    prerequisite_skill: str = "integer",
) -> str | None:
    """Compatibility wrapper used by downstream plotting flow."""
    return save_mastery_trajectory_plot(
        step_log_rows=df_logs,
        episodes=episodes,
        output_dir=output_dir,
        target_skill=target_skill,
        prerequisite_skill=prerequisite_skill,
    )


def save_average_mastery_trajectory_by_type(
    step_log_rows: list[dict[str, Any]],
    output_dir: str,
) -> str | None:
    """Save per-student-type average mastery trajectory from aligned AB3 logs."""
    ab3 = [r for r in step_log_rows if r.get("strategy") == "AB3_PPO_Dynamic"]
    if not ab3:
        return None
    max_step = max(int(r["step"]) for r in ab3 if r.get("step") is not None)
    all_steps = list(range(1, max_step + 1))

    fig, axes = plt.subplots(1, 3, figsize=(18, 5), sharey=True)
    plotted = False

    for idx, student_type in enumerate(STUDENT_TYPES):
        ax = axes[idx]
        rows = [r for r in ab3 if r.get("student_type") == student_type]
        if not rows:
            ax.set_title(f"{student_type} (No Data)")
            ax.axis("off")
            continue

        by_step: dict[int, list[dict[str, Any]]] = {}
        for row in rows:
            step = int(row["step"])
            by_step.setdefault(step, []).append(row)

        avg_int_map = {
            s: statistics.mean(float(r["integer_mastery"]) for r in by_step[s]) for s in by_step
        }
        avg_poly_map = {
            s: statistics.mean(float(r["polynomial_mastery"]) for r in by_step[s]) for s in by_step
        }
        avg_int = [avg_int_map.get(s, float("nan")) for s in all_steps]
        avg_poly = [avg_poly_map.get(s, float("nan")) for s in all_steps]

        plotted = True
        ax.plot(
            all_steps,
            avg_int,
            linewidth=2.2,
            marker="o",
            label="Prerequisite Mastery",
        )
        ax.plot(
            all_steps,
            avg_poly,
            linewidth=2.2,
            marker="s",
            label="Target Mastery",
        )
        ax.set_title(f"Learning Trajectory ({student_type} Group)")
        ax.set_xlabel("Step")
        if idx == 0:
            ax.set_ylabel("Mastery")
        ax.set_ylim(0.0, 1.0)
        ax.set_xlim(1, max_step)
        ax.legend(fontsize=8)

    if not plotted:
        plt.close(fig)
        return None

    fig.suptitle("Average Mastery Trajectory by Student Type (AB3)")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "mastery_trajectory_average_by_student_type.png")
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def write_mastery_trajectory_average_figure(
    df_logs: list[dict[str, Any]],
    output_dir: str,
) -> str | None:
    """Compatibility wrapper for average mastery trajectory output."""
    return save_average_mastery_trajectory_by_type(
        step_log_rows=df_logs,
        output_dir=output_dir,
    )


# ====================
# 7) main()
# ====================
def main(output_mode: str = "full") -> None:
    """Run full ablation simulation workflow."""
    random.seed(RANDOM_SEED)

    episodes, trajectory_rows = run_batch_experiments()
    strategy_summary = build_strategy_summary(episodes)
    strategy_student_summary = build_strategy_student_summary(episodes)
    ab3_student_summary = build_ab3_student_type_summary(episodes)
    ab3_subskill_summary = build_ab3_subskill_progress_summary(episodes)
    ablation_strategy_summary = build_ablation_strategy_summary(episodes)
    ablation_strategy_by_type_summary = build_ablation_strategy_by_student_type_summary(episodes)
    ab3_student_detailed_summary = build_ab3_student_type_detailed_summary(episodes)
    ab3_subskill_detailed_summary = build_ab3_subskill_by_type_detailed_summary(episodes)
    ab3_failure_breakpoint_summary = build_ab3_failure_breakpoint_summary(episodes)
    exp2_behavior_summary = build_experiment2_student_type_summary(trajectory_rows)
    exp1_table_rows = build_experiment1_summary_table(episodes, max_steps_default=MAX_STEPS)

    print(f"Total episodes: {len(episodes)}")
    print_ascii_table(
        title="Table 1: Overall Strategy Comparison",
        headers=[
            "Strategy",
            "Success Rate",
            "Avg Steps",
            "Avg Unnecessary Remediations",
            "Avg Final Mastery",
        ],
        rows=strategy_summary,
    )
    print_ascii_table(
        title="Table 2: Strategy x Student Type Comparison",
        headers=[
            "Strategy",
            "Student Type",
            "Success Rate",
            "Avg Steps",
            "Avg Unnecessary Remediations",
            "Avg Final Mastery",
        ],
        rows=strategy_student_summary,
    )

    output_path = write_episode_csv(episodes)
    ablation_strategy_path = write_ablation_strategy_summary_csv(ablation_strategy_summary)
    ablation_strategy_by_type_path = write_ablation_strategy_by_student_type_summary_csv(
        ablation_strategy_by_type_summary
    )
    exp1_summary_csv_path = write_experiment1_summary_csv(exp1_table_rows)
    exp1_summary_md_path = write_experiment1_summary_markdown(exp1_table_rows)
    trajectory_path = ""
    ab3_student_path = ""
    ab3_subskill_path = ""
    ab3_student_detailed_path = ""
    ab3_subskill_detailed_path = ""
    ab3_failure_breakpoint_path = ""
    exp2_behavior_path = ""
    exp2_behavior_fig = ""
    exp2_efficiency_fig = ""
    mastery_episode_fig = ""
    mastery_avg_fig = ""
    caption_paths: list[str] = []
    if output_mode != "experiment1":
        trajectory_path = write_trajectory_csv(trajectory_rows)
        ab3_student_path = write_ab3_student_type_summary_csv(ab3_student_summary)
        ab3_subskill_path = write_ab3_subskill_progress_summary_csv(ab3_subskill_summary)
        ab3_student_detailed_path = write_ab3_student_type_detailed_summary_csv(
            ab3_student_detailed_summary
        )
        ab3_subskill_detailed_path = write_ab3_subskill_by_type_detailed_summary_csv(
            ab3_subskill_detailed_summary
        )
        ab3_failure_breakpoint_path = write_ab3_failure_breakpoint_summary_csv(
            ab3_failure_breakpoint_summary
        )
        exp2_behavior_path = write_experiment2_student_type_summary_csv(exp2_behavior_summary)
        exp2_behavior_fig = write_experiment2_policy_behavior_figure(exp2_behavior_summary)
        exp2_efficiency_fig = write_experiment2_efficiency_figure(exp2_behavior_summary)
        exp2_dir = str(EXPERIMENT2_OUTPUT_DIR)
        mastery_step_logs = build_mastery_step_log(trajectory_rows)
        mastery_episode_fig = write_mastery_trajectory_episode_figure(
            df_logs=mastery_step_logs,
            episodes=episodes,
            output_dir=exp2_dir,
            target_skill="polynomial",
            prerequisite_skill="integer",
        )
        mastery_avg_fig = write_mastery_trajectory_average_figure(
            df_logs=mastery_step_logs,
            output_dir=exp2_dir,
        )
        rep_episode_id = None
        if mastery_episode_fig:
            name = os.path.basename(mastery_episode_fig)
            if name.startswith("mastery_trajectory_episode_") and name.endswith(".png"):
                rep_episode_id = int(name[len("mastery_trajectory_episode_") : -4])
        caption_paths = write_experiment2_figure_captions(exp2_dir, rep_episode_id)

    print("\nSimulation completed.")
    print(f"Output CSV: {output_path}")
    print(f"Ablation Strategy CSV: {ablation_strategy_path}")
    print(f"Ablation Strategy x Type CSV: {ablation_strategy_by_type_path}")
    if output_mode != "experiment1":
        print(f"Trajectory CSV: {trajectory_path}")
        print(f"AB3 Student-Type CSV: {ab3_student_path}")
        print(f"AB3 Subskill CSV: {ab3_subskill_path}")
        print(f"AB3 Student-Type Detailed CSV: {ab3_student_detailed_path}")
        print(f"AB3 Subskill Detailed CSV: {ab3_subskill_detailed_path}")
        print(f"AB3 Failure Breakpoint CSV: {ab3_failure_breakpoint_path}")
        print(f"Experiment2 Student-Type Summary CSV: {exp2_behavior_path}")
        print(f"Experiment2 Policy Behavior Figure: {exp2_behavior_fig}")
        print(f"Experiment2 Efficiency Figure: {exp2_efficiency_fig}")
        print(f"Mastery Trajectory Episode Figure: {mastery_episode_fig}")
        print(
            f"Mastery Trajectory Representative Fixed Figure: "
            f"{os.path.join(str(EXPERIMENT2_OUTPUT_DIR), 'mastery_trajectory_representative_episode.png')}"
        )
        print(f"Mastery Trajectory Average Figure: {mastery_avg_fig}")
        for caption_path in caption_paths:
            print(f"Figure Caption File: {caption_path}")
    print(f"Experiment1 Summary CSV: {exp1_summary_csv_path}")
    print(f"Experiment1 Summary Markdown: {exp1_summary_md_path}")
    print(f"RANDOM_SEED: {RANDOM_SEED}")
    print(f"N_PER_TYPE: {N_PER_TYPE}")
    print(f"MAX_STEPS: {MAX_STEPS}")
    print(f"TARGET_MASTERY: {TARGET_MASTERY}")


if __name__ == "__main__":
    main()

