import csv
import os
import random
import statistics
from dataclasses import dataclass
from typing import Literal

# ====================
# 1) 常數區
# ====================
RANDOM_SEED = 42
N_PER_TYPE = 100
MAX_STEPS = 50
TARGET_MASTERY = 0.85

STRATEGIES = ["AB1_Baseline", "AB2_RuleBased", "AB3_PPO_Dynamic"]
STUDENT_TYPES = ["Careless", "Weak", "Average"]
LAST_TRAJECTORY_LOGS: list[dict[str, int | float | str]] = []

# ====================
# Skill-based model 設定
# ====================
SkillId = Literal[
    "integer_sign",
    "integer_order",
    "poly_combine",
    "poly_expand",
    "poly_division",
]

POLY_SKILLS: tuple[SkillId, ...] = ("poly_combine", "poly_expand", "poly_division")
PREREQ_SKILLS: tuple[SkillId, ...] = ("integer_sign", "integer_order")
ALL_SKILLS: tuple[SkillId, ...] = PREREQ_SKILLS + POLY_SKILLS

PREREQ_MAP: dict[SkillId, list[SkillId]] = {
    "poly_combine": ["integer_sign"],
    "poly_expand": ["integer_order"],
    "poly_division": ["integer_order"],
    "integer_sign": [],
    "integer_order": [],
}

MAINLINE_FAMILY_BY_SKILL: dict[SkillId, str] = {
    "poly_combine": "poly_combine_mainline",
    "poly_expand": "poly_expand_mainline",
    "poly_division": "poly_division_mainline",
    "integer_sign": "integer_sign_mainline",
    "integer_order": "integer_order_mainline",
}

REMEDIATION_FAMILY_BY_SKILL: dict[SkillId, str] = {
    "integer_sign": "remed_integer_sign",
    "integer_order": "remed_integer_order",
    "poly_combine": "remed_poly_combine",
    "poly_expand": "remed_poly_expand",
    "poly_division": "remed_poly_division",
}

Mode = Literal["mainline", "remediation"]
ErrorType = Literal["correct", "minor_error", "major_error"]


@dataclass(frozen=True)
class Question:
    family: str
    target_skill: SkillId
    prereq_skills: list[SkillId]
    difficulty: float  # 0..1
    mode: Mode


@dataclass(frozen=True)
class AnswerResult:
    is_correct: bool
    error_type: ErrorType
    p_correct: float
    attributed_to_prereq: SkillId | None


def clamp(value: float, low: float, high: float) -> float:
    """Clamp value into [low, high]."""
    return max(low, min(high, value))


# ====================
# 2) SimulatedStudent 類別
# ====================
class SimulatedStudent:
    """A lightweight skill-based cognitive student model for one episode."""

    def __init__(self, student_type: str, initial_mastery: float = 0.35) -> None:
        self.student_type = student_type

        base = self._get_base_masteries(student_type, initial_mastery)
        self.mastery_by_skill: dict[SkillId, float] = {k: clamp(v, 0.0, 1.0) for k, v in base.items()}

        self.fail_streak = 0
        self.remediation_count = 0
        self.unnecessary_remediations = 0
        self.reached_mastery_step: int | None = None

    def _get_minor_error_probability(self) -> float:
        if self.student_type == "Careless":
            return 0.90
        if self.student_type == "Weak":
            return 0.20
        if self.student_type == "Average":
            return 0.50
        raise ValueError(f"Unknown student_type: {self.student_type}")

    def _get_base_masteries(self, student_type: str, initial_mastery: float) -> dict[SkillId, float]:
        """
        用「多技能」取代單一 accuracy/mastery。

        - Careless：概念多半會，但容易 slip（答錯更多是 minor）
        - Weak：前置與多項式技能都弱，且重大錯誤更常見
        - Average：中等、可隨練習穩定提升
        """
        m = clamp(initial_mastery, 0.0, 1.0)
        if student_type == "Careless":
            return {
                "integer_sign": clamp(m + 0.25, 0.0, 1.0),
                "integer_order": clamp(m + 0.20, 0.0, 1.0),
                "poly_combine": clamp(m + 0.15, 0.0, 1.0),
                "poly_expand": clamp(m + 0.10, 0.0, 1.0),
                "poly_division": clamp(m + 0.05, 0.0, 1.0),
            }
        if student_type == "Weak":
            return {
                "integer_sign": clamp(m - 0.10, 0.0, 1.0),
                "integer_order": clamp(m - 0.05, 0.0, 1.0),
                "poly_combine": clamp(m - 0.10, 0.0, 1.0),
                "poly_expand": clamp(m - 0.12, 0.0, 1.0),
                "poly_division": clamp(m - 0.15, 0.0, 1.0),
            }
        if student_type == "Average":
            return {
                "integer_sign": clamp(m + 0.10, 0.0, 1.0),
                "integer_order": clamp(m + 0.08, 0.0, 1.0),
                "poly_combine": clamp(m + 0.05, 0.0, 1.0),
                "poly_expand": clamp(m + 0.03, 0.0, 1.0),
                "poly_division": clamp(m + 0.00, 0.0, 1.0),
            }
        raise ValueError(f"Unknown student_type: {student_type}")

    def _careless_slip_probability(self, q: Question) -> float:
        if self.student_type != "Careless":
            return 0.0
        base = 0.08
        return clamp(base + 0.10 * q.difficulty, 0.0, 0.25)

    def _guess_probability(self, q: Question) -> float:
        if self.student_type == "Weak":
            return clamp(0.12 - 0.04 * q.difficulty, 0.02, 0.12)
        return clamp(0.05 - 0.02 * q.difficulty, 0.01, 0.05)

    def compute_p_correct(self, q: Question) -> tuple[float, SkillId | None]:
        """
        用 target mastery + prereq mastery + difficulty 決定答對機率。

        回傳 (p_correct, attributed_weak_prereq) 供錯誤診斷使用。
        """
        t = self.mastery_by_skill[q.target_skill]
        prereqs = q.prereq_skills
        if prereqs:
            prereq_vals = [self.mastery_by_skill[s] for s in prereqs]
            prereq_mean = sum(prereq_vals) / len(prereq_vals)
            weak_prereq = prereqs[prereq_vals.index(min(prereq_vals))]
        else:
            prereq_mean = 1.0
            weak_prereq = None

        # 較平滑且可解釋的成功率：target 與 prereq 加權後，扣除難度
        # - polynomial 題更依賴 prereq（但不應該把成功率壓到接近猜測）
        if q.target_skill in POLY_SKILLS:
            combined = 0.62 * t + 0.38 * prereq_mean
            difficulty_penalty = 0.22 * q.difficulty
        else:
            combined = 0.80 * t + 0.20 * prereq_mean
            difficulty_penalty = 0.15 * q.difficulty

        p = 0.06 + 0.92 * combined - difficulty_penalty
        p = clamp(p, 0.03, 0.97)

        # 猜對下限（尤其弱學生）
        p = max(p, self._guess_probability(q))
        return p, weak_prereq

    def answer_question(self, q: Question) -> AnswerResult:
        p_correct, weak_prereq = self.compute_p_correct(q)

        # Careless 的 slip：即使會做也可能寫錯（偏 minor）
        slip = self._careless_slip_probability(q)
        slipped = random.random() < slip

        if (not slipped) and random.random() < p_correct:
            self.fail_streak = 0
            return AnswerResult(
                is_correct=True,
                error_type="correct",
                p_correct=p_correct,
                attributed_to_prereq=None,
            )

        self.fail_streak += 1

        if slipped:
            return AnswerResult(
                is_correct=False,
                error_type="minor_error",
                p_correct=p_correct,
                attributed_to_prereq=None,
            )

        # 非 slip 的錯誤：若前置弱且題目是多項式主線，較容易 major
        is_minor = random.random() < self._get_minor_error_probability()
        if q.target_skill in POLY_SKILLS and weak_prereq is not None:
            if self.mastery_by_skill[weak_prereq] < 0.45 and not is_minor:
                error_type: ErrorType = "major_error"
            else:
                error_type = "minor_error" if is_minor else "major_error"
        else:
            error_type = "minor_error" if is_minor else "major_error"

        return AnswerResult(
            is_correct=False,
            error_type=error_type,
            p_correct=p_correct,
            attributed_to_prereq=weak_prereq if q.target_skill in POLY_SKILLS else None,
        )

    def apply_learning(
        self,
        q: Question,
        result: AnswerResult,
        gain_scale: float = 1.0,
        opportunity_cost_target: SkillId | None = None,
        opportunity_cost: float = 0.0,
    ) -> None:
        """
        題目作答後更新技能 mastery。

        - mainline：主要更新 polynomial 技能，錯誤會有輕微退步
        - remediation：主要更新前置技能，並對依賴該 prereq 的 polynomial 技能有小幅 transfer
        """
        t = q.target_skill
        current = self.mastery_by_skill[t]

        # 學習率：30 steps 的 episode 中，需要足夠的正向學習幅度才可能達到 TARGET_MASTERY
        base_lr = 0.35 if q.mode == "mainline" else 0.50
        lr = base_lr * (1.0 - 0.30 * q.difficulty)

        if result.is_correct:
            gain = lr * (1.0 - current) * clamp(gain_scale, 0.0, 1.2)
            self.mastery_by_skill[t] = clamp(current + gain, 0.0, 1.0)
            # 主線題同時會練到一點點前置（弱連結），讓「只走主線」也能有合理學習
            if q.mode == "mainline" and q.prereq_skills:
                prereq_lr = 0.10 * (1.0 - 0.40 * q.difficulty)
                for ps in q.prereq_skills:
                    pm = self.mastery_by_skill[ps]
                    self.mastery_by_skill[ps] = clamp(pm + prereq_lr * (1.0 - pm), 0.0, 1.0)
        else:
            # 錯誤造成的退步不宜太大，但 major 比 minor 更傷
            if result.error_type == "major_error":
                drop = 0.030 + 0.020 * q.difficulty
            else:
                drop = 0.012 + 0.012 * q.difficulty
            self.mastery_by_skill[t] = clamp(current - drop, 0.0, 1.0)

        if q.mode == "remediation":
            self.remediation_count += 1
            self._apply_prereq_transfer(prereq_skill=t)
            # mismatch 時間成本：補救不對位時，主線 target 會有極小停滯/折損
            if opportunity_cost_target is not None and opportunity_cost > 0:
                cur = self.mastery_by_skill[opportunity_cost_target]
                self.mastery_by_skill[opportunity_cost_target] = clamp(
                    cur - opportunity_cost, 0.0, 1.0
                )

    def _apply_prereq_transfer(self, prereq_skill: SkillId) -> None:
        """
        prerequisite transfer：補強前置技能後，對相關 polynomial 技能有小幅正向遷移。
        """
        if prereq_skill not in PREREQ_SKILLS:
            return
        prereq_m = self.mastery_by_skill[prereq_skill]
        # calibration：整體下調約 15%，保留 transfer 但降低「補量即無敵」
        transfer_strength = (
            0.0425
            if self.student_type == "Careless"
            else 0.068
            if self.student_type == "Average"
            else 0.085
        )

        for poly in POLY_SKILLS:
            if prereq_skill in PREREQ_MAP[poly]:
                cur = self.mastery_by_skill[poly]
                # transfer 是「小幅推進」，且越接近 1 越飽和
                bump = transfer_strength * (prereq_m - 0.35) * (1.0 - cur)
                if bump > 0:
                    self.mastery_by_skill[poly] = clamp(cur + bump, 0.0, 1.0)

    def reset_episode_state(self) -> None:
        """Reset counters if caller wants to reuse one object."""
        base = self._get_base_masteries(self.student_type, 0.35)
        self.mastery_by_skill = {k: clamp(v, 0.0, 1.0) for k, v in base.items()}
        self.fail_streak = 0
        self.remediation_count = 0
        self.unnecessary_remediations = 0
        self.reached_mastery_step = None


def aggregate_final_mastery(student: SimulatedStudent) -> float:
    """以 polynomial 主技能聚合整體 mastery。"""
    vals = [student.mastery_by_skill[s] for s in POLY_SKILLS]
    return sum(vals) / len(vals)


def aggregate_integer_mastery(student: SimulatedStudent) -> float:
    """Aggregate prerequisite integer-related mastery."""
    vals = [student.mastery_by_skill[s] for s in PREREQ_SKILLS]
    return sum(vals) / len(vals)


def build_trajectory_row(
    *,
    strategy: str,
    student_type: str,
    episode_id: int,
    step: int,
    phase: Mode,
    active_skill: SkillId,
    student: SimulatedStudent,
    result: AnswerResult,
    was_remediation: bool,
    was_unnecessary_remediation: bool,
) -> dict[str, int | float | str]:
    integer_mastery = aggregate_integer_mastery(student)
    # 目前模型沒有獨立 fraction skill，先以 integer mastery proxy 對應輸出欄位。
    fraction_mastery = integer_mastery
    return {
        "strategy": strategy,
        "student_type": student_type,
        "episode_id": episode_id,
        "step": step,
        "phase": phase,
        "active_skill": active_skill,
        "polynomial_mastery": round(aggregate_final_mastery(student), 6),
        "integer_mastery": round(integer_mastery, 6),
        "fraction_mastery": round(fraction_mastery, 6),
        "is_correct": 1 if result.is_correct else 0,
        "was_remediation": 1 if was_remediation else 0,
        "was_unnecessary_remediation": 1 if was_unnecessary_remediation else 0,
    }


def maybe_mark_reached_mastery(student: SimulatedStudent, total_steps: int) -> None:
    """Set first step when mastery reaches target."""
    if student.reached_mastery_step is None and aggregate_final_mastery(student) >= TARGET_MASTERY:
        student.reached_mastery_step = total_steps


# ====================
# 3) 三種策略函式 / 邏輯
# ====================
def build_mainline_question(step_idx: int) -> Question:
    """
    產生簡化版 mainline 題目（family-aware）。

    - family/target_skill/prereq_skills/difficulty/mode 皆具備
    - step_idx 用來讓主線在 3 個 polynomial skill 間循環且逐步變難
    """
    skill_cycle: list[SkillId] = ["poly_combine", "poly_expand", "poly_division"]
    target = skill_cycle[step_idx % len(skill_cycle)]
    # calibration：後段再微幅提高挑戰，增加策略區分力
    difficulty = clamp(0.18 + 0.019 * step_idx, 0.15, 0.74)
    prereqs = list(PREREQ_MAP[target])
    return Question(
        family=MAINLINE_FAMILY_BY_SKILL[target],
        target_skill=target,
        prereq_skills=prereqs,
        difficulty=difficulty,
        mode="mainline",
    )


def build_remediation_question(target_skill: SkillId, difficulty: float) -> Question:
    prereqs = list(PREREQ_MAP[target_skill])
    return Question(
        family=REMEDIATION_FAMILY_BY_SKILL[target_skill],
        target_skill=target_skill,
        prereq_skills=prereqs,
        difficulty=clamp(difficulty, 0.10, 0.70),
        mode="remediation",
    )


def compute_final_accuracy_proxy(student: SimulatedStudent) -> float:
    """
    為了維持 CSV 欄位 `final_accuracy`，提供一個可解釋的 proxy：
    - 以三個 mainline polynomial skill 在「中等難度」下的預期答對率做平均。
    """
    ps: list[float] = []
    for s in POLY_SKILLS:
        q = Question(
            family=MAINLINE_FAMILY_BY_SKILL[s],
            target_skill=s,
            prereq_skills=list(PREREQ_MAP[s]),
            difficulty=0.55,
            mode="mainline",
        )
        p, _ = student.compute_p_correct(q)
        ps.append(p)
    return sum(ps) / len(ps)


def count_unnecessary_remediation(student: SimulatedStudent, triggering_q: Question, result: AnswerResult) -> int:
    """
    用較合理的定義估計「不必要補救」：
    - 主要在 minor slip/小失誤，且相關前置技能不弱、且整體已接近熟練時觸發 remediation
    """
    if result.is_correct:
        return 0
    if result.error_type != "minor_error":
        return 0
    if aggregate_final_mastery(student) < 0.70:
        return 0
    prereqs = triggering_q.prereq_skills
    if not prereqs:
        return 0
    if min(student.mastery_by_skill[s] for s in prereqs) >= 0.60:
        return 1
    return 0


def remediation_mismatch_penalty(
    student: SimulatedStudent,
    mainline_q: Question,
    mainline_result: AnswerResult,
    remed_skill: SkillId,
) -> tuple[float, float]:
    """
    校準用：補救若不對位，施加小幅收益折扣與機會成本。

    回傳 (gain_scale, opportunity_cost)
    - gain_scale：remediation 該步學習增益縮放
    - opportunity_cost：對當前 mainline polynomial target 的小幅折損
    """
    if mainline_q.target_skill not in POLY_SKILLS:
        return 1.0, 0.0

    weakest_prereq = (
        min(mainline_q.prereq_skills, key=lambda s: student.mastery_by_skill[s])
        if mainline_q.prereq_skills
        else None
    )
    expected_prereq = (
        mainline_result.attributed_to_prereq
        if mainline_result.attributed_to_prereq is not None
        else weakest_prereq
    )

    mismatch = False
    if expected_prereq is not None and remed_skill != expected_prereq:
        mismatch = True
    # 若該次錯誤像是 slip（沒有前置歸因），硬做 prereq remed 視為部分不對位
    if (
        mainline_result.attributed_to_prereq is None
        and mainline_result.error_type == "minor_error"
    ):
        mismatch = True

    if mismatch:
        return 0.78, 0.010
    return 1.0, 0.0


def run_ab1_baseline(
    student: SimulatedStudent,
    trajectory_logs: list[dict[str, int | float | str]] | None = None,
    strategy_name: str = "",
    student_type: str = "",
    episode_id: int = 0,
) -> int:
    """AB1: mainline only, no remediation."""
    total_steps = 0
    while total_steps < MAX_STEPS and aggregate_final_mastery(student) < TARGET_MASTERY:
        q = build_mainline_question(step_idx=total_steps)
        result = student.answer_question(q)
        student.apply_learning(q, result)
        total_steps += 1
        if trajectory_logs is not None:
            trajectory_logs.append(
                build_trajectory_row(
                    strategy=strategy_name,
                    student_type=student_type,
                    episode_id=episode_id,
                    step=total_steps,
                    phase="mainline",
                    active_skill=q.target_skill,
                    student=student,
                    result=result,
                    was_remediation=False,
                    was_unnecessary_remediation=False,
                )
            )
        maybe_mark_reached_mastery(student, total_steps)
    return total_steps


def run_ab2_rule_based(
    student: SimulatedStudent,
    trajectory_logs: list[dict[str, int | float | str]] | None = None,
    strategy_name: str = "",
    student_type: str = "",
    episode_id: int = 0,
) -> int:
    """AB2: any wrong answer triggers 3-step remediation."""
    total_steps = 0
    remediation_steps = 3  # 固定 block，比 AB3 更長、較不精準

    while total_steps < MAX_STEPS and aggregate_final_mastery(student) < TARGET_MASTERY:
        q = build_mainline_question(step_idx=total_steps)
        result = student.answer_question(q)
        total_steps += 1
        student.apply_learning(q, result)
        if trajectory_logs is not None:
            trajectory_logs.append(
                build_trajectory_row(
                    strategy=strategy_name,
                    student_type=student_type,
                    episode_id=episode_id,
                    step=total_steps,
                    phase="mainline",
                    active_skill=q.target_skill,
                    student=student,
                    result=result,
                    was_remediation=False,
                    was_unnecessary_remediation=False,
                )
            )
        maybe_mark_reached_mastery(student, total_steps)

        if aggregate_final_mastery(student) >= TARGET_MASTERY or total_steps >= MAX_STEPS:
            break

        if not result.is_correct:
            unnecessary_flag = count_unnecessary_remediation(student, q, result)
            student.unnecessary_remediations += unnecessary_flag

            # 規則式：不診斷，固定補「該題的第一個 prereq」；若沒有 prereq 就補 target
            if q.prereq_skills:
                remed_skill = q.prereq_skills[0]
            else:
                remed_skill = q.target_skill

            remaining = MAX_STEPS - total_steps
            consumed = min(remediation_steps, remaining)
            # 用 consumed 次 remediation 題目去消耗步數（每步都是一題）
            for _ in range(consumed):
                gain_scale, opp_cost = remediation_mismatch_penalty(
                    student=student,
                    mainline_q=q,
                    mainline_result=result,
                    remed_skill=remed_skill,
                )
                rq = build_remediation_question(target_skill=remed_skill, difficulty=max(0.15, q.difficulty - 0.10))
                rr = student.answer_question(rq)
                student.apply_learning(
                    rq,
                    rr,
                    gain_scale=gain_scale,
                    opportunity_cost_target=q.target_skill,
                    opportunity_cost=opp_cost,
                )
                total_steps += 1
                if trajectory_logs is not None:
                    trajectory_logs.append(
                        build_trajectory_row(
                            strategy=strategy_name,
                            student_type=student_type,
                            episode_id=episode_id,
                            step=total_steps,
                            phase="remediation",
                            active_skill=rq.target_skill,
                            student=student,
                            result=rr,
                            was_remediation=True,
                            was_unnecessary_remediation=bool(unnecessary_flag),
                        )
                    )
                if total_steps >= MAX_STEPS or aggregate_final_mastery(student) >= TARGET_MASTERY:
                    break

    return total_steps


def run_ab3_ppo_dynamic(
    student: SimulatedStudent,
    trajectory_logs: list[dict[str, int | float | str]] | None = None,
    strategy_name: str = "",
    student_type: str = "",
    episode_id: int = 0,
) -> int:
    """AB3: dynamic remediation trigger with 2-step remediation."""
    total_steps = 0
    remediation_steps = 2  # 更短、更對位（與 AB2 形成研究差異）

    # 簡化版「診斷證據」：追蹤前置技能造成的錯誤訊號（EMA）
    weakness_evidence: dict[SkillId, float] = {s: 0.0 for s in ALL_SKILLS}

    def update_evidence(q: Question, r: AnswerResult) -> None:
        decay = 0.85
        for s in weakness_evidence:
            weakness_evidence[s] *= decay
        if (not r.is_correct) and q.mode == "mainline" and r.attributed_to_prereq is not None:
            bump = 0.40 if r.error_type == "major_error" else 0.20
            weakness_evidence[r.attributed_to_prereq] = clamp(weakness_evidence[r.attributed_to_prereq] + bump, 0.0, 3.0)

    while total_steps < MAX_STEPS and aggregate_final_mastery(student) < TARGET_MASTERY:
        q = build_mainline_question(step_idx=total_steps)
        result = student.answer_question(q)
        student.apply_learning(q, result)
        total_steps += 1
        if trajectory_logs is not None:
            trajectory_logs.append(
                build_trajectory_row(
                    strategy=strategy_name,
                    student_type=student_type,
                    episode_id=episode_id,
                    step=total_steps,
                    phase="mainline",
                    active_skill=q.target_skill,
                    student=student,
                    result=result,
                    was_remediation=False,
                    was_unnecessary_remediation=False,
                )
            )
        update_evidence(q, result)
        maybe_mark_reached_mastery(student, total_steps)

        if aggregate_final_mastery(student) >= TARGET_MASTERY or total_steps >= MAX_STEPS:
            break

        if not result.is_correct:
            # dynamic trigger：連錯、重大錯誤、或前置弱點證據累積
            prereqs = q.prereq_skills
            weakest_prereq = None
            if prereqs:
                weakest_prereq = min(prereqs, key=lambda s: student.mastery_by_skill[s])
            prereq_is_weak = weakest_prereq is not None and student.mastery_by_skill[weakest_prereq] < 0.55
            evidence_high = weakest_prereq is not None and weakness_evidence[weakest_prereq] >= 0.55

            streak_threshold = 3 if student.student_type == "Careless" else 2
            trigger = (student.fail_streak >= streak_threshold) or (
                result.error_type == "major_error" and prereq_is_weak
            ) or evidence_high

            # minor + 前置不弱時，AB3 傾向先續走主線避免過度補救
            if (
                result.error_type == "minor_error"
                and not prereq_is_weak
                and student.fail_streak < 3
            ):
                trigger = False

            if trigger:
                unnecessary_flag = count_unnecessary_remediation(student, q, result)
                student.unnecessary_remediations += unnecessary_flag

                # 更精準：補最弱的 prereq；若沒有 prereq，才補 target
                remed_skill: SkillId = weakest_prereq if weakest_prereq is not None else q.target_skill

                remaining = MAX_STEPS - total_steps
                # AB3 補救步數依嚴重度動態調整：一般 1 步，重大錯誤/連錯才到 2 步
                dynamic_steps = 2 if (result.error_type == "major_error" or student.fail_streak >= 3) else 1
                consumed = min(dynamic_steps, remaining)
                for _ in range(consumed):
                    # remediation 題目難度略低、對位更強
                    rq = build_remediation_question(target_skill=remed_skill, difficulty=max(0.12, q.difficulty - 0.18))
                    rr = student.answer_question(rq)
                    gain_scale, opp_cost = remediation_mismatch_penalty(
                        student=student,
                        mainline_q=q,
                        mainline_result=result,
                        remed_skill=remed_skill,
                    )
                    student.apply_learning(
                        rq,
                        rr,
                        gain_scale=gain_scale * 1.06,
                        opportunity_cost_target=q.target_skill,
                        opportunity_cost=opp_cost * 0.6,
                    )
                    total_steps += 1
                    if trajectory_logs is not None:
                        trajectory_logs.append(
                            build_trajectory_row(
                                strategy=strategy_name,
                                student_type=student_type,
                                episode_id=episode_id,
                                step=total_steps,
                                phase="remediation",
                                active_skill=rq.target_skill,
                                student=student,
                                result=rr,
                                was_remediation=True,
                                was_unnecessary_remediation=bool(unnecessary_flag),
                            )
                        )
                    if total_steps >= MAX_STEPS or aggregate_final_mastery(student) >= TARGET_MASTERY:
                        break

    return total_steps


# ====================
# 4) 單次 episode 模擬函式
# ====================
def simulate_episode(
    student_type: str,
    strategy_name: str,
    episode_id: int = 0,
    trajectory_logs: list[dict[str, int | float | str]] | None = None,
) -> dict[str, int | float | str | None]:
    """Run one episode for a student type under one strategy."""
    student = SimulatedStudent(student_type=student_type, initial_mastery=0.35)

    if strategy_name == "AB1_Baseline":
        total_steps = run_ab1_baseline(
            student,
            trajectory_logs=trajectory_logs,
            strategy_name=strategy_name,
            student_type=student_type,
            episode_id=episode_id,
        )
    elif strategy_name == "AB2_RuleBased":
        total_steps = run_ab2_rule_based(
            student,
            trajectory_logs=trajectory_logs,
            strategy_name=strategy_name,
            student_type=student_type,
            episode_id=episode_id,
        )
    elif strategy_name == "AB3_PPO_Dynamic":
        total_steps = run_ab3_ppo_dynamic(
            student,
            trajectory_logs=trajectory_logs,
            strategy_name=strategy_name,
            student_type=student_type,
            episode_id=episode_id,
        )
    else:
        raise ValueError(f"Unknown strategy_name: {strategy_name}")

    final_mastery = aggregate_final_mastery(student)
    success = 1 if final_mastery >= TARGET_MASTERY else 0
    return {
        "strategy": strategy_name,
        "student_type": student_type,
        "success": success,
        "total_steps": total_steps,
        "final_mastery": round(final_mastery, 4),
        "reached_mastery_step": student.reached_mastery_step,
        "remediation_count": student.remediation_count,
        "unnecessary_remediations": student.unnecessary_remediations,
        "final_accuracy": round(compute_final_accuracy_proxy(student), 4),
    }


# ====================
# 5) 批次實驗函式
# ====================
def run_batch_experiments() -> list[dict[str, int | float | str | None]]:
    """Run all strategy x student_type episodes."""
    global LAST_TRAJECTORY_LOGS
    LAST_TRAJECTORY_LOGS = []
    episode_id = 0
    episodes: list[dict[str, int | float | str | None]] = []
    for strategy in STRATEGIES:
        for student_type in STUDENT_TYPES:
            for _ in range(N_PER_TYPE):
                episode_id += 1
                episodes.append(
                    simulate_episode(
                        student_type,
                        strategy,
                        episode_id=episode_id,
                        trajectory_logs=LAST_TRAJECTORY_LOGS,
                    )
                )
    return episodes


def build_strategy_summary(
    episodes: list[dict[str, int | float | str | None]]
) -> list[dict[str, float | str]]:
    """Aggregate overall metrics by strategy."""
    rows: list[dict[str, float | str]] = []
    for strategy in STRATEGIES:
        subset = [e for e in episodes if e["strategy"] == strategy]
        success_rate = statistics.mean(float(e["success"]) for e in subset) * 100.0
        avg_steps = statistics.mean(float(e["total_steps"]) for e in subset)
        avg_unnecessary = statistics.mean(
            float(e["unnecessary_remediations"]) for e in subset
        )
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


def build_strategy_student_summary(
    episodes: list[dict[str, int | float | str | None]]
) -> list[dict[str, float | str]]:
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
            avg_unnecessary = statistics.mean(
                float(e["unnecessary_remediations"]) for e in subset
            )
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


# ====================
# 6) ASCII 統計表輸出函式
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
# 7) CSV 輸出函式
# ====================
def write_episode_csv(episodes: list[dict[str, int | float | str | None]]) -> str:
    """Write raw episode records to reports CSV."""
    reports_dir = "reports"
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
            row = dict(episode)
            if row["reached_mastery_step"] is None:
                row["reached_mastery_step"] = ""
            writer.writerow(row)

    return output_path


def write_trajectory_csv(trajectory_logs: list[dict[str, int | float | str]]) -> str:
    """Write per-step mastery trajectory records to reports CSV."""
    reports_dir = "reports"
    os.makedirs(reports_dir, exist_ok=True)
    output_path = os.path.join(reports_dir, "mastery_trajectory.csv")

    fieldnames = [
        "strategy",
        "student_type",
        "episode_id",
        "step",
        "phase",
        "active_skill",
        "polynomial_mastery",
        "integer_mastery",
        "fraction_mastery",
        "is_correct",
        "was_remediation",
        "was_unnecessary_remediation",
    ]

    with open(output_path, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in trajectory_logs:
            writer.writerow(row)

    return output_path


# ====================
# 8) main()
# ====================
def main() -> None:
    """Run full ablation simulation workflow."""
    random.seed(RANDOM_SEED)

    episodes = run_batch_experiments()
    strategy_summary = build_strategy_summary(episodes)
    strategy_student_summary = build_strategy_student_summary(episodes)

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
    trajectory_path = write_trajectory_csv(LAST_TRAJECTORY_LOGS)
    print("\nSimulation completed.")
    print(f"Output CSV: {output_path}")
    print(f"Trajectory CSV: {trajectory_path}")
    print(f"RANDOM_SEED: {RANDOM_SEED}")
    print(f"N_PER_TYPE: {N_PER_TYPE}")
    print(f"MAX_STEPS: {MAX_STEPS}")
    print(f"TARGET_MASTERY: {TARGET_MASTERY}")


if __name__ == "__main__":
    main()
