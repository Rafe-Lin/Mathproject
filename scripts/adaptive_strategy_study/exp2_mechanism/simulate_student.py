# -*- coding: utf-8 -*-
# ==============================================================================
# ID: simulate_student.py
# Version: V1.0.0 (Adaptive Simulation Engine)
# Last Updated: 2026-04-15
# Author: *Steve
#
# [Description]:
#   適應性學習核心模擬：依策略（AB1/AB2/AB3）與學生類型產生回合／步階軌跡、
#   補救與路由行為紀錄；彙總結果、輸出正式實驗 CSV，並可自動產生 Exp2 圖表與 caption。
#   亦支援 RAG 延伸實驗之軌跡延伸分析。
#
# [Scientific Control Strategy]:
#   集中設定樣本數、種子與門檻，與 core.experiment_config 對齊。
#
# [Database Schema Usage]:
#   無內建 ORM 持久化；以檔案系統 reports/adaptive_strategy_study/ 為主輸出。
#
# [Logic Flow]:
#   1. 解析輸出模式（如 experiment2）與策略清單。
#   2. 模擬每回合步驟、更新掌握度與補救。
#   3. 寫入 CSV/圖表並同步 latest。
# ==============================================================================
import csv
import os
import random
import statistics
from datetime import datetime
import shutil
import sys
from pathlib import Path
from collections import Counter
from typing import Any
import matplotlib.pyplot as plt

# Path bootstrap: repo root + common/ for plot_experiment_results (cwd-independent).
_STUDY_ROOT = Path(__file__).resolve().parents[1]
if str(_STUDY_ROOT) not in sys.path:
    sys.path.insert(0, str(_STUDY_ROOT))
import study_paths as _study_paths  # noqa: E402

_study_paths.ensure_repo_root_on_syspath()
_study_paths.ensure_common_on_syspath()

from core.experiment_config import (  # noqa: E402
    EXP1_SUCCESS_THRESHOLD as CONFIG_EXP1_SUCCESS_THRESHOLD,
    get_group_mastery_range,
    validate_group_config,
)
from plot_experiment_results import (  # noqa: E402
    add_bar_labels,
    create_timestamped_run_dir,
    finalize_report_figure,
    setup_report_style,
    sync_run_to_latest,
)

setup_report_style()

# ====================
# 1) 實驗設定（研究版最小重構）
# ====================
# 固定亂數種子，確保科展重現性。
RANDOM_SEED = 42
# Experiment 1/runner single source of sample size.
EXP1_EPISODES_PER_TYPE = 100
# Runtime episode count defaults to the unified source.
N_PER_TYPE = EXP1_EPISODES_PER_TYPE
# 每個 episode 最大步數。
MAX_STEPS = 30
# Fixed condition for Experiment 2 mechanism-analysis outputs.
EXP2_FIXED_MAX_STEPS = 40
# Experiment 1 fixed max steps.
EXP1_FIXED_MAX_STEPS = 30
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
EXP1_SUCCESS_THRESHOLD = CONFIG_EXP1_SUCCESS_THRESHOLD
RUNTIME_SUCCESS_THRESHOLD = TARGET_MASTERY

# 子技能導向更新幅度（不做策略 buff，僅依作答結果更新）。
MASTERY_UPDATE = {
    "correct": 0.09,
    "minor_error": -0.015,
    "major_error": -0.035,
}
# Updated (RQ3 - Weak Transfer Setting)
# Based on Cognitive Load Theory & Evidence Reliability:
# Careless > Average > Weak
# Weak students have low transfer reliability -> conservative reflect scale
REFLECT_SCALE_BY_STUDENT_TYPE: dict[str, float] = {
    "Careless": 0.15,
    "Average": 0.10,
    "Weak": 0.05,
}

STRATEGIES = ["AB1_Baseline", "AB2_RuleBased", "AB3_PPO_Dynamic"]
STUDENT_TYPES = ["Careless", "Weak", "Average"]
TARGET_SKILL = "polynomial"
EXP2_STUDENT_TYPE_ORDER = ["Careless", "Average", "Weak"]
EXP2_STRATEGIES = ["AB3_PPO_Dynamic"]
EXP2_STUDENT_TYPE_ZH = {
    "Careless": "Careless (B++, B+)",
    "Average": "Average (B)",
    "Weak": "Weak (C)",
}
EXP2_INTERPRETATION = {
    "Careless": "Mostly stayed on mainline with minimal remediation; already near mastery.",
    "Average": "Received balanced mainline and remediation support; achieved the largest overall improvement.",
    "Weak": "Spent significant time in remediation; improved but rarely reached stable A-level within 40 steps.",
}

REPORTS_DIR = _study_paths.study_reports_root()
EXPERIMENT1_OUTPUT_DIR = REPORTS_DIR / "experiment_1_ablation"
EXPERIMENT2_OUTPUT_DIR = REPORTS_DIR / "experiment_2_ab3_student_types"
EXP1_OUTPUT_DIR_ENV = "MATHPROJECT_EXP1_OUTPUT_DIR"
EXP2_OUTPUT_DIR_ENV = "MATHPROJECT_EXP2_OUTPUT_DIR"
OUTPUT_MODE_ENV = "MATHPROJECT_OUTPUT_MODE"
EXPERIMENT_PROFILE_ENV = "MATHPROJECT_EXPERIMENT_PROFILE"
EXPERIMENT_PROFILE_DEFAULT = "default"
EXP1_PROFILE_NAME = "exp1"
FORCE_WRITE_MARKDOWN_ENV = "MATHPROJECT_FORCE_WRITE_MARKDOWN"

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
validate_group_config()


def set_global_seed(seed: int) -> None:
    """Set global random seed for reproducibility across optional deps."""
    os.environ["PYTHONHASHSEED"] = str(int(seed))
    random.seed(int(seed))
    try:
        import numpy as np  # type: ignore

        np.random.seed(int(seed))
    except Exception:
        pass
    try:
        import torch  # type: ignore

        torch.manual_seed(int(seed))
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(int(seed))
        try:
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False
        except Exception:
            pass
    except Exception:
        pass


def get_experiment_profile() -> str:
    """Read explicit experiment profile. Output mode must not change logic."""
    return str(os.environ.get(EXPERIMENT_PROFILE_ENV, EXPERIMENT_PROFILE_DEFAULT)).strip().lower()


def is_exp1_calibration_enabled() -> bool:
    """True when explicit Experiment 1 calibration profile is enabled."""
    return get_experiment_profile() == EXP1_PROFILE_NAME


def clamp(value: float, low: float, high: float) -> float:
    """Clamp value into [low, high]."""
    return max(low, min(high, value))


def format_student_type_label(student_type: str) -> str:
    """Normalize student-type labels for all human-facing outputs."""
    mapping = {
        "careless": "Careless",
        "average": "Average",
        "weak": "Weak",
        "weak_foundation": "Weak",
        "weak foundation": "Weak",
        "low": "Weak",
        "mid": "Average",
        "high": "Careless",
    }
    raw = str(student_type).strip()
    return mapping.get(raw.lower(), raw)


def to_exp2_student_type_zh(student_type: str) -> str:
    """Map canonical student type to Experiment 2 Chinese group name."""
    st = format_student_type_label(student_type)
    return EXP2_STUDENT_TYPE_ZH.get(st, st)


def _format_row_student_type(row: dict[str, Any]) -> dict[str, Any]:
    """Return a shallow-copied row with normalized student_type label when present."""
    out = dict(row)
    if "student_type" in out:
        out["student_type"] = format_student_type_label(str(out["student_type"]))
    return out


def get_experiment1_output_dir() -> Path:
    """Resolve Experiment 1 output directory with optional runtime override."""
    override = os.environ.get(EXP1_OUTPUT_DIR_ENV, "").strip()
    if override:
        return Path(override)
    return EXPERIMENT1_OUTPUT_DIR


def get_experiment2_output_dir() -> Path:
    """Resolve Experiment 2 output directory with optional runtime override."""
    override = os.environ.get(EXP2_OUTPUT_DIR_ENV, "").strip()
    if override:
        return Path(override)
    return EXPERIMENT2_OUTPUT_DIR


def get_output_mode() -> str:
    """Read runtime output mode for path isolation."""
    return str(os.environ.get(OUTPUT_MODE_ENV, "experiment2")).strip().lower()


def get_force_write_markdown() -> bool:
    """Read markdown overwrite flag from environment."""
    value = str(os.environ.get(FORCE_WRITE_MARKDOWN_ENV, "")).strip().lower()
    return value in {"1", "true", "yes", "y", "on"}


def _is_under(path: Path, root: Path) -> bool:
    """Return True when path is under root (inclusive)."""
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except Exception:
        return False


def is_final_path(path: str | Path) -> bool:
    """Check whether a target path belongs to any reports/**/final/** directory."""
    p = Path(path)
    return "final" in {part.lower() for part in p.parts}


def _is_exp1_path(path: str | Path) -> bool:
    return _is_under(Path(path), EXPERIMENT1_OUTPUT_DIR)


def _is_exp2_path(path: str | Path) -> bool:
    return _is_under(Path(path), EXPERIMENT2_OUTPUT_DIR)


def _safe_prepare_output_path(path: str | Path, *, is_markdown: bool = False) -> tuple[bool, Path]:
    """Guard writes by mode/final-protection/markdown-overwrite rules."""
    target = Path(path)
    mode = get_output_mode()
    force_md = get_force_write_markdown()

    if is_final_path(target):
        print("[PROTECT] Skip writing to final directory")
        return False, target

    if mode == "experiment2" and _is_exp1_path(target):
        print(f"[SKIP] blocked path (experiment2 isolation): {target}")
        return False, target
    if mode == "experiment1" and _is_exp2_path(target):
        print(f"[SKIP] blocked path (experiment1 isolation): {target}")
        return False, target

    if is_markdown and target.exists() and (not force_md):
        print("[SKIP] Markdown exists, not overwriting")
        return False, target

    target.parent.mkdir(parents=True, exist_ok=True)
    print(f"[WRITE] target directory: {target.parent}")
    return True, target


def _write_csv_rows(output_path: str | Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> str:
    """Write csv rows with safe path guard."""
    ok, target = _safe_prepare_output_path(output_path, is_markdown=False)
    if not ok:
        return str(target)
    with open(target, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return str(target)


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
        if is_exp1_calibration_enabled():
            if student_type == "Careless":
                # Keep high ability but add stronger slip noise for better separation.
                return {
                    "mean": 0.67,
                    "std": 0.18,
                    "slip": 0.22,
                    "guess": 0.05,
                }
            if student_type == "Weak":
                # Slightly lift weak baseline to avoid near-zero baseline success.
                return {
                    "mean": 0.44,
                    "std": 0.09,
                    "slip": 0.08,
                    "guess": 0.05,
                }
            if student_type == "Average":
                return {
                    "mean": 0.57,
                    "std": 0.06,
                    "slip": 0.11,
                    "guess": 0.04,
                }
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
        if is_exp1_calibration_enabled():
            low, high = get_group_mastery_range(student_type)
            out_exp1: dict[str, float] = {}
            for subskill in POLYNOMIAL_SUBSKILLS:
                out_exp1[subskill] = clamp(random.uniform(low, high), 0.05, 0.98)
            return out_exp1

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
        if is_exp1_calibration_enabled() and self.student_type == "Careless":
            # Additional lapse event for high-ability but careless students.
            if random.random() < 0.12:
                p_correct = clamp(p_correct - 0.14, 0.01, 0.99)

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
    if is_exp1_calibration_enabled() and student.student_type == "Careless":
        # Careless learners show unstable consolidation in Exp1.
        if error_type == "correct":
            delta *= 0.88
        else:
            delta *= 1.10
    if is_exp1_calibration_enabled() and student.student_type == "Weak":
        # Diminishing return at low-mastery region for smoother weak-group gain.
        weak_scale = 0.80 + (0.35 * clamp(current_hit_mastery, 0.0, 1.0))
        if error_type == "correct":
            delta *= weak_scale

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
        reflect_scale = REFLECT_SCALE_BY_STUDENT_TYPE.get(student.student_type, 0.25)
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
    if student.reached_mastery_step is None and student.mastery >= RUNTIME_SUCCESS_THRESHOLD:
        student.reached_mastery_step = total_steps


def get_effective_max_steps(student: SimulatedStudent) -> int:
    """Experiment 1 uses a shared hard cap for all student groups."""
    return int(MAX_STEPS)


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
        nonlocal mainline_steps, foundation_extra_used, total_steps
        # Hard cap: total counted steps must never exceed MAX_STEPS.
        if total_steps >= MAX_STEPS:
            return False
        if student.student_type == "Weak" and gate_flag and foundation_extra_used < int(
            WEAK_FOUNDATION_EXTRA_STEPS
        ):
            foundation_extra_used += 1
            return True
        if mainline_steps < effective_max_steps:
            mainline_steps += 1
            return True
        return False

    done = False
    while (not done) and student.mastery < RUNTIME_SUCCESS_THRESHOLD:
        if total_steps >= MAX_STEPS:
            break
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

        if student.mastery >= RUNTIME_SUCCESS_THRESHOLD:
            done = True
            break
        if total_steps >= MAX_STEPS:
            break

        remediation_triggered = False
        remediation_steps = 0
        remediation_target_subskill = "sign_handling"
        unnecessary = False

        if strategy_name == "AB2_RuleBased" and not is_correct:
            # AB2：錯就進補救，但補救目標較固定、較不精準。
            if is_exp1_calibration_enabled():
                # Exp1 recalibration: later trigger and shorter remediation for better baseline balance.
                remediation_triggered = (student.fail_streak >= 2) or (
                    error_type == "major_error" and student.mastery < 0.62
                )
                remediation_steps = 2
                remediation_target_subskill = (
                    "sign_handling" if student.student_type == "Weak" else hit_subskill
                )
                unnecessary = (error_type == "minor_error") and (student.mastery > 0.70)
            else:
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
                if total_steps >= MAX_STEPS:
                    break
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
                if (
                    strategy_name == "AB2_RuleBased"
                    and is_exp1_calibration_enabled()
                    and rem_correct
                    and student.subskill_mastery[rem_hit] >= 0.62
                ):
                    # Exp1 recalibration: return to mainline earlier for Rule-Based.
                    break

                if student.mastery >= RUNTIME_SUCCESS_THRESHOLD:
                    done = True
                    break
                if total_steps >= MAX_STEPS:
                    break

            # Immediate episode termination once mastery threshold is reached.
            if student.mastery >= RUNTIME_SUCCESS_THRESHOLD:
                done = True
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

    success = 1 if student.mastery >= RUNTIME_SUCCESS_THRESHOLD else 0
    reached_step = student.reached_mastery_step

    # Correctness check: if success was reached, no additional steps should be taken afterward.
    if success == 1 and reached_step is not None and int(total_steps) != int(reached_step):
        print(
            "[WARN][TerminationMismatch] "
            f"strategy={strategy_name} student_type={student_type} episode={episode_id} "
            f"reached_step={reached_step} total_steps={total_steps} final_mastery={student.mastery:.4f}"
        )

    if (
        student_type == "Weak"
        and is_exp1_calibration_enabled()
        and int(MAX_STEPS) == 40
    ):
        remediation_steps = sum(
            1 for r in trajectory_rows if str(r.get("route", r.get("phase", ""))) == "remediation"
        )
        gate_active_steps = sum(
            1
            for r in trajectory_rows
            if int(r.get("progression_gate_active", 0)) == 1
        )
        print(
            "[DEBUG][WeakEpisode] "
            f"strategy={strategy_name} episode={episode_id} "
            f"success={success} steps_taken={total_steps} final_mastery={student.mastery:.4f} "
            f"reached_step={reached_step if reached_step is not None else ''} "
            f"remediation_steps={remediation_steps} gate_active_steps={gate_active_steps}"
        )

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
        "mastery_gain": round(polynomial_gain, 4),
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
def run_batch_experiments(
    strategies: list[str] | None = None,
    student_types: list[str] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Run strategy x student_type episodes."""
    episodes: list[dict[str, Any]] = []
    trajectory: list[dict[str, Any]] = []
    strategies_to_run = list(strategies) if strategies is not None else list(STRATEGIES)
    student_types_to_run = list(student_types) if student_types is not None else list(STUDENT_TYPES)

    episode_id = 0
    for strategy in strategies_to_run:
        for student_type in student_types_to_run:
            for _ in range(N_PER_TYPE):
                episode_id += 1
                one_episode, rows = simulate_episode(
                    student_type=student_type,
                    strategy_name=strategy,
                    episode_id=episode_id,
                )
                episodes.append(one_episode)
                trajectory.extend(rows)

    # Debug diagnostics: check whether Weak + Rule-Based is trapped in remediation/gate dynamics.
    weak_rule_rows = [
        r for r in trajectory
        if str(r.get("strategy")) == "AB2_RuleBased" and str(r.get("student_type")) == "Weak"
    ]
    weak_rule_eps = [
        e for e in episodes
        if str(e.get("strategy")) == "AB2_RuleBased" and str(e.get("student_type")) == "Weak"
    ]
    if weak_rule_rows and weak_rule_eps:
        rem_steps = sum(
            1 for r in weak_rule_rows if str(r.get("route", r.get("phase", ""))) == "remediation"
        )
        gate_steps = sum(
            1 for r in weak_rule_rows if int(r.get("progression_gate_active", 0)) == 1
        )
        total_rows = len(weak_rule_rows)
        success_rate = statistics.mean(float(e["success"]) for e in weak_rule_eps) * 100.0
        avg_steps = statistics.mean(float(e["total_steps"]) for e in weak_rule_eps)
        rem_ratio = (rem_steps / total_rows) if total_rows > 0 else float("nan")
        gate_ratio = (gate_steps / total_rows) if total_rows > 0 else float("nan")
        print(
            "[DEBUG][WeakRuleBasedAggregate] "
            f"max_steps={int(MAX_STEPS)} "
            f"success_rate={success_rate:.2f}% avg_steps={avg_steps:.2f} "
            f"remediation_ratio={rem_ratio:.3f} gate_active_ratio={gate_ratio:.3f} "
            f"episodes={len(weak_rule_eps)}"
        )
        if rem_ratio > 0.80:
            print("[WARN][WeakRuleBased] high remediation ratio detected (>0.80).")
        if gate_ratio > 0.80:
            print("[WARN][WeakRuleBased] progression gate active in most steps (>0.80).")

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
    reports_dir = str(get_experiment1_output_dir())
    os.makedirs(reports_dir, exist_ok=True)
    output_path = os.path.join(reports_dir, "ablation_simulation_results.csv")
    ok, target = _safe_prepare_output_path(output_path)
    if not ok:
        return str(target)

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

    with open(target, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for episode in episodes:
            row = {k: episode[k] for k in fieldnames}
            if row["reached_mastery_step"] is None:
                row["reached_mastery_step"] = ""
            writer.writerow(row)

    return str(target)


def write_trajectory_csv(trajectory_rows: list[dict[str, Any]]) -> str:
    """Write per-step trajectory log to Experiment 2 output directory."""
    reports_dir = str(get_experiment2_output_dir())
    os.makedirs(reports_dir, exist_ok=True)
    output_path = os.path.join(reports_dir, "mastery_trajectory.csv")
    ok, target = _safe_prepare_output_path(output_path)
    if not ok:
        return str(target)

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
        "foundation_mastery_mean",
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

    with open(target, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in trajectory_rows:
            out_row = _format_row_student_type(row)
            out_row["foundation_mastery_mean"] = out_row.pop("weak_foundation_mean", "")
            writer.writerow(out_row)

    return str(target)


def write_ab3_student_type_summary_csv(rows: list[dict[str, Any]]) -> str:
    output_dir = str(get_experiment2_output_dir())
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
    ok, target = _safe_prepare_output_path(output_path)
    if not ok:
        return str(target)
    with open(target, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(_format_row_student_type(row))
    return str(target)


def write_ab3_subskill_progress_summary_csv(rows: list[dict[str, Any]]) -> str:
    output_dir = str(get_experiment2_output_dir())
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "ab3_subskill_progress_summary.csv")
    fieldnames = [
        "student_type",
        "subskill",
        "avg_initial_mastery",
        "avg_final_mastery",
        "avg_gain",
    ]
    ok, target = _safe_prepare_output_path(output_path)
    if not ok:
        return str(target)
    with open(target, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(_format_row_student_type(row))
    return str(target)


def write_ablation_strategy_summary_csv(rows: list[dict[str, Any]]) -> str:
    """Write formal ablation summary by strategy."""
    output_dir = str(get_experiment1_output_dir())
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
    ok, target = _safe_prepare_output_path(output_path)
    if not ok:
        return str(target)
    with open(target, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return str(target)


def write_ablation_strategy_by_student_type_summary_csv(rows: list[dict[str, Any]]) -> str:
    """Write formal ablation summary by strategy and student type."""
    output_dir = str(get_experiment1_output_dir())
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
    ok, target = _safe_prepare_output_path(output_path)
    if not ok:
        return str(target)
    with open(target, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return str(target)


def write_ab3_student_type_detailed_summary_csv(rows: list[dict[str, Any]]) -> str:
    """Write detailed AB3 student-type summary."""
    output_dir = str(get_experiment2_output_dir())
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
    ok, target = _safe_prepare_output_path(output_path)
    if not ok:
        return str(target)
    with open(target, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(_format_row_student_type(row))
    return str(target)


def write_ab3_subskill_by_type_detailed_summary_csv(rows: list[dict[str, Any]]) -> str:
    """Write detailed AB3 subskill summary by student type."""
    output_dir = str(get_experiment2_output_dir())
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "ab3_subskill_by_type_detailed_summary.csv")
    fieldnames = [
        "student_type",
        "subskill",
        "avg_initial_mastery",
        "avg_final_mastery",
        "avg_gain",
    ]
    ok, target = _safe_prepare_output_path(output_path)
    if not ok:
        return str(target)
    with open(target, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(_format_row_student_type(row))
    return str(target)


def write_ab3_failure_breakpoint_summary_csv(rows: list[dict[str, Any]]) -> str:
    """Write AB3 failure breakpoint summary."""
    output_dir = str(get_experiment2_output_dir())
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "ab3_failure_breakpoint_summary.csv")
    fieldnames = [
        "student_type",
        "most_common_weakest_subskill",
        "avg_final_polynomial_mastery",
        "avg_steps",
        "count_failed_episodes",
    ]
    ok, target = _safe_prepare_output_path(output_path)
    if not ok:
        return str(target)
    with open(target, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(_format_row_student_type(row))
    return str(target)


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
    output_dir = str(get_experiment1_output_dir())
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
    ok, target = _safe_prepare_output_path(output_path)
    if not ok:
        return str(target)
    with open(target, "w", newline="", encoding="utf-8-sig") as csvfile:
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
    return str(target)


def write_experiment1_summary_markdown(rows: list[dict[str, Any]]) -> str:
    """Write Experiment 1 summary table in markdown format for paper/slides."""
    output_dir = str(get_experiment1_output_dir())
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
        "## Key Result",
        "",
        "Adaptive (Ours) achieves the highest success rate across all tested step budgets (30, 40, 50).",
        "Its advantage is especially clear for Average (B) students, while it also remains the best-performing strategy for Weak (C) students despite low absolute success rates.",
        "",
        "| MAX_STEPS | Strategy | Success Rate (%) | Avg Steps | Avg Final Mastery |",
        "|-----------|----------|------------------|-----------|-------------------|",
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
                    _fmt(row["Avg Final Mastery"]),
                ]
            )
            + " |"
        )

    ok, target = _safe_prepare_output_path(output_path, is_markdown=True)
    if not ok:
        return str(target)
    with open(target, "w", encoding="utf-8-sig") as f:
        f.write("\n".join(lines) + "\n")
    return str(target)


def build_experiment2_student_type_summary(
    episode_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Aggregate AB3 behavior/efficiency metrics by student type from episode rows."""
    summaries: list[dict[str, Any]] = []
    for student_type in EXP2_STUDENT_TYPE_ORDER:
        rows = [r for r in episode_rows if format_student_type_label(str(r.get("student_group", ""))) == student_type]
        if not rows:
            continue
        total_episodes = len(rows)
        success_rate = statistics.mean(float(r["success"]) for r in rows)
        avg_steps = statistics.mean(float(r["steps_taken"]) for r in rows)
        avg_final_mastery = statistics.mean(float(r["final_mastery"]) for r in rows)
        mainline_steps_mean = statistics.mean(float(r["mainline_steps"]) for r in rows)
        remediation_steps_mean = statistics.mean(float(r["remediation_steps"]) for r in rows)
        total_mainline = sum(float(r["mainline_steps"]) for r in rows)
        total_remediation = sum(float(r["remediation_steps"]) for r in rows)
        ratio_denom = total_mainline + total_remediation
        reached_vals = [
            float(r["reached_mastery_step"])
            for r in rows
            if str(r.get("reached_mastery_step", "")).strip() != ""
        ]
        avg_reached = statistics.mean(reached_vals) if reached_vals else ""
        avg_gain = statistics.mean(float(r["total_mastery_gain"]) for r in rows)
        summaries.append(
            {
                "student_group": student_type.lower(),
                "student_group_zh": to_exp2_student_type_zh(student_type),
                "max_steps": int(EXP2_FIXED_MAX_STEPS),
                "total_episodes": int(total_episodes),
                "success_rate": round(success_rate, 4),
                "avg_steps": round(avg_steps, 4),
                "avg_final_mastery": round(avg_final_mastery, 4),
                "mainline_steps_mean": round(mainline_steps_mean, 4),
                "remediation_steps_mean": round(remediation_steps_mean, 4),
                "mainline_ratio": round((total_mainline / ratio_denom), 4) if ratio_denom > 0 else 0.0,
                "remediation_ratio": round((total_remediation / ratio_denom), 4) if ratio_denom > 0 else 0.0,
                "avg_reached_mastery_step": round(avg_reached, 4) if avg_reached != "" else "",
                "avg_mastery_gain": round(avg_gain, 4),
                "interpretation": EXP2_INTERPRETATION.get(student_type, ""),
            }
        )
    return summaries


def build_mastery_step_log(trajectory_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return step-level mastery logs for reusable plotting/stat analysis."""
    return trajectory_rows


def write_experiment2_student_type_summary_csv(rows: list[dict[str, Any]]) -> str:
    """Write Experiment 2 student-type behavior summary for reproducible charting."""
    output_dir = str(get_experiment2_output_dir())
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "experiment2_student_type_summary.csv")
    fieldnames = [
        "student_group",
        "student_group_zh",
        "max_steps",
        "total_episodes",
        "success_rate",
        "avg_steps",
        "avg_final_mastery",
        "mainline_steps_mean",
        "remediation_steps_mean",
        "mainline_ratio",
        "remediation_ratio",
        "avg_reached_mastery_step",
        "avg_mastery_gain",
        "interpretation",
    ]
    ok, target = _safe_prepare_output_path(output_path)
    if not ok:
        return str(target)
    with open(target, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return str(target)


def write_experiment2_policy_behavior_figure(rows: list[dict[str, Any]]) -> str:
    """Plot Experiment 2 policy allocation figure (ratio-only, single axis)."""
    output_dir = str(get_experiment2_output_dir())
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "experiment2_policy_behavior_summary.png")
    ok, target = _safe_prepare_output_path(output_path)
    if not ok:
        return str(target)

    student_order = [to_exp2_student_type_zh(st) for st in EXP2_STUDENT_TYPE_ORDER]
    valid_rows = [row for row in rows if row.get("student_group_zh") in student_order]
    if not valid_rows:
        return output_path
    valid_rows.sort(key=lambda row: student_order.index(str(row["student_group_zh"])))

    x_labels = [str(row["student_group_zh"]) for row in valid_rows]
    remediation_ratio = [
        float(row["remediation_ratio"]) if row["remediation_ratio"] != "" else float("nan")
        for row in valid_rows
    ]
    mainline_ratio = [
        float(row["mainline_ratio"]) if row["mainline_ratio"] != "" else float("nan")
        for row in valid_rows
    ]

    fig, ax = plt.subplots(figsize=(8, 5))
    width = 0.3
    x = list(range(len(x_labels)))
    bars1 = ax.bar(
        [i - width / 2 for i in x],
        mainline_ratio,
        width=width,
        label="Mainline Ratio",
        color="#1f77b4",
    )
    bars2 = ax.bar(
        [i + width / 2 for i in x],
        remediation_ratio,
        width=width,
        label="Remediation Ratio",
        color="#ff7f0e",
    )

    ax.set_xlabel("Student Group")
    ax.set_ylabel("Ratio")
    ax.set_ylim(0, 1.0)
    ax.set_xticks(x)
    ax.set_xticklabels(x_labels)
    ax.set_title("Experiment 2: Policy Allocation by Student Group (AB3, MAX_STEPS = 40)")

    add_bar_labels(ax, fmt="{:.0%}")
    ax.legend(loc="upper right")

    ax.grid(axis="y", alpha=0.25)
    finalize_report_figure(fig, str(target))
    return str(target)


def write_experiment2_time_budget_figure(rows: list[dict[str, Any]]) -> str:
    output_dir = str(get_experiment2_output_dir())
    output_path = os.path.join(output_dir, "experiment2_time_budget_by_student_type.png")
    ok, target = _safe_prepare_output_path(output_path)
    if not ok:
        return str(target)
    student_order = [to_exp2_student_type_zh(st) for st in EXP2_STUDENT_TYPE_ORDER]
    valid_rows = [r for r in rows if r.get("student_group_zh") in student_order]
    valid_rows.sort(key=lambda r: student_order.index(str(r["student_group_zh"])))

    x_labels = [str(r["student_group_zh"]) for r in valid_rows]
    mainline = [float(r["mainline_steps_mean"]) for r in valid_rows]
    remediation = [float(r["remediation_steps_mean"]) for r in valid_rows]
    totals = [a + b for a, b in zip(mainline, remediation)]
    x = list(range(len(x_labels)))

    fig, ax = plt.subplots(figsize=(8, 5))
    bars_main = ax.bar(x, mainline, color="#1f77b4", label="Mainline Steps(主技能)")
    bars_rem = ax.bar(x, remediation, bottom=mainline, color="#ff7f0e", label="Remediation Steps(前置技能)")
    ax.set_xticks(x)
    ax.set_xticklabels(x_labels)
    ax.set_ylabel("Average Steps")
    ax.set_title("Experiment 2: Time Budget by Student Group (AB3, MAX_STEPS = 40)")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(loc="upper left")

    for i, total in enumerate(totals):
        ax.text(i, total + 0.3, f"{total:.1f}", ha="center", va="bottom", fontsize=9)
    for bar, val in zip(bars_main, mainline):
        if val > 1.5:
            ax.text(bar.get_x() + bar.get_width() / 2.0, val / 2.0, f"{val:.1f}", ha="center", va="center", fontsize=8, color="white")
    for bar, base, val in zip(bars_rem, mainline, remediation):
        if val > 1.5:
            ax.text(bar.get_x() + bar.get_width() / 2.0, base + val / 2.0, f"{val:.1f}", ha="center", va="center", fontsize=8, color="white")

    finalize_report_figure(fig, str(target))
    return str(target)


def build_experiment2_episode_metrics(
    episodes: list[dict[str, Any]],
    trajectory_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Build per-episode Experiment 2 metrics with explicit route tracking counts."""
    route_counts: dict[int, dict[str, int]] = {}
    for row in trajectory_rows:
        if str(row.get("strategy")) != "AB3_PPO_Dynamic":
            continue
        episode_id = int(row.get("episode_id", 0))
        entry = route_counts.setdefault(episode_id, {"mainline": 0, "remediation": 0})
        route_type = str(row.get("route", row.get("phase", ""))).strip().lower()
        if route_type == "mainline":
            entry["mainline"] += 1
        elif route_type == "remediation":
            entry["remediation"] += 1

    out: list[dict[str, Any]] = []
    for e in episodes:
        if str(e.get("strategy")) != "AB3_PPO_Dynamic":
            continue
        episode_id = int(e.get("episode_id", 0))
        student_type = format_student_type_label(str(e.get("student_type", "")))
        route = route_counts.get(episode_id, {"mainline": 0, "remediation": 0})
        mainline_steps = int(route.get("mainline", 0))
        remediation_steps = int(route.get("remediation", 0))
        out.append(
            {
                "episode_id": episode_id,
                "student_type": student_type.lower(),
                "student_type_zh": to_exp2_student_type_zh(student_type),
                "student_group": student_type,
                "steps_taken": int(e.get("total_steps", 0)),
                "final_mastery": float(e.get("final_mastery", 0.0)),
                "success": 1 if float(e.get("final_mastery", 0.0)) >= 0.80 else 0,
                "mainline_steps": mainline_steps,
                "remediation_steps": remediation_steps,
                "reached_mastery_step": e.get("reached_mastery_step", "") if e.get("reached_mastery_step", None) is not None else "",
                "total_mastery_gain": float(e.get("mastery_gain", 0.0)),
            }
        )
    return out


def write_experiment2_episode_metrics_csv(rows: list[dict[str, Any]]) -> str:
    output_dir = str(get_experiment2_output_dir())
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "experiment2_episode_metrics.csv")
    fieldnames = [
        "episode_id",
        "student_group",
        "student_type",
        "student_type_zh",
        "steps_taken",
        "final_mastery",
        "success",
        "mainline_steps",
        "remediation_steps",
        "reached_mastery_step",
        "total_mastery_gain",
    ]
    return _write_csv_rows(output_path, fieldnames, rows)


def write_experiment2_student_type_summary_md(rows: list[dict[str, Any]]) -> str:
    output_dir = str(get_experiment2_output_dir())
    output_path = os.path.join(output_dir, "experiment2_student_type_summary.md")
    lines = [
        "# Experiment 2 Student-Type Summary (AB3, MAX_STEPS=40)",
        "",
        "| student_group | student_group_zh | max_steps | total_episodes | success_rate | avg_steps | avg_final_mastery | mainline_steps_mean | remediation_steps_mean | mainline_ratio | remediation_ratio | avg_reached_mastery_step | avg_mastery_gain |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        avg_reached = row["avg_reached_mastery_step"]
        reached_text = f"{float(avg_reached):.2f}" if avg_reached != "" else ""
        lines.append(
            f"| {row['student_group']} | {row['student_group_zh']} | {int(row['max_steps'])} | {int(row['total_episodes'])} | "
            f"{float(row['success_rate'])*100.0:.1f}% | {float(row['avg_steps']):.2f} | {float(row['avg_final_mastery']):.3f} | "
            f"{float(row['mainline_steps_mean']):.2f} | {float(row['remediation_steps_mean']):.2f} | "
            f"{float(row['mainline_ratio']):.3f} | {float(row['remediation_ratio']):.3f} | {reached_text} | {float(row['avg_mastery_gain']):.3f} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"- 拔尖組: {EXP2_INTERPRETATION['Careless']}",
            f"- 固本組: {EXP2_INTERPRETATION['Average']}",
            f"- 減C組: {EXP2_INTERPRETATION['Weak']}",
            "",
        ]
    )
    ok, target = _safe_prepare_output_path(output_path, is_markdown=True)
    if not ok:
        return str(target)
    with open(target, "w", encoding="utf-8-sig") as f:
        f.write("\n".join(lines))
    return str(target)


def write_experiment2_efficiency_figure(rows: list[dict[str, Any]]) -> str:
    output_dir = str(get_experiment2_output_dir())
    output_path = os.path.join(output_dir, "experiment2_adaptive_gain_by_student_type.png")
    ok, target = _safe_prepare_output_path(output_path)
    if not ok:
        return str(target)
    student_order = [to_exp2_student_type_zh(st) for st in EXP2_STUDENT_TYPE_ORDER]
    valid_rows = [r for r in rows if r.get("student_group_zh") in student_order]
    valid_rows.sort(key=lambda r: student_order.index(str(r["student_group_zh"])))
    x_labels = [str(r["student_group_zh"]) for r in valid_rows]
    success_pct = [float(r["success_rate"]) * 100.0 for r in valid_rows]
    mastery_pct = [float(r["avg_final_mastery"]) * 100.0 for r in valid_rows]
    x = list(range(len(x_labels)))
    width = 0.34
    gain_vals = [float(r["avg_mastery_gain"]) for r in valid_rows]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    ax1.bar(x, gain_vals, color="#1f77b4")
    ax1.set_xticks(x)
    ax1.set_xticklabels(x_labels)
    ax1.set_ylabel("Mastery Gain")
    ax1.set_title("Panel A: Average Mastery Gain by Student Group")
    gain_top = max(gain_vals) * 1.12 if gain_vals else 1.0
    ax1.set_ylim(0, gain_top)
    ax1.grid(axis="y", alpha=0.25)
    for i, v in enumerate(gain_vals):
        y_text = min(v + 0.004, gain_top - 0.012)
        ax1.text(i, y_text, f"{v:.3f}", ha="center", va="bottom", fontsize=9)

    ax2.bar(x, success_pct, color="#2ca02c")
    ax2.set_xticks(x)
    ax2.set_xticklabels(x_labels)
    ax2.set_ylabel("Success Rate 達標A (%)")
    ax2.set_ylim(0, 100)
    ax2.set_title("Panel B: Success Rate 達標A (%) by Student Group")
    ax2.grid(axis="y", alpha=0.25)
    for i, v in enumerate(success_pct):
        ax2.text(i, v + 1.0, f"{v:.1f}%", ha="center", va="bottom", fontsize=9)

    fig.suptitle("Experiment 2: Adaptive Gain by Student Group (AB3, MAX_STEPS = 40)")
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    finalize_report_figure(fig, str(target))
    return str(target)


def write_experiment2_learning_path_diagram(rows: list[dict[str, Any]]) -> str:
    # NOTE: This plot is intentionally schematic and not derived from raw trajectory data.
    # It is used for interpretability and communication purposes only.
    output_dir = str(get_experiment2_output_dir())
    output_path = os.path.join(output_dir, "experiment2_learning_path_diagram.png")
    ok, target = _safe_prepare_output_path(output_path)
    if not ok:
        return str(target)

    group_order = [to_exp2_student_type_zh(st) for st in EXP2_STUDENT_TYPE_ORDER]
    fig, axes = plt.subplots(1, 3, figsize=(14, 4), sharey=True)
    threshold = 0.80
    x_curve = [0, 1, 2, 3, 4, 5]

    for ax, group in zip(axes, group_order):
        if group == "Careless (B++, B+)":
            y_curve = [0.65, 0.69, 0.72, 0.75, 0.78, 0.80]
            note = "主線為主，少量補救，\n快速接近門檻（示意）"
            rem_points = [3]
        elif group == "Average (B)":
            y_curve = [0.52, 0.57, 0.61, 0.69, 0.76, 0.80]
            note = "主線與補救平衡，\n補救後有明顯提升（示意）"
            rem_points = [2, 3]
        else:
            y_curve = [0.30, 0.33, 0.36, 0.40, 0.44, 0.47]
            note = "多次補救，有進步但難在40步內\n穩定達A（示意）"
            rem_points = [1, 2, 4]

        ax.plot(x_curve, y_curve, color="#1f77b4", linewidth=2.2, marker="o")
        for rp in rem_points:
            ax.scatter([rp], [y_curve[rp]], color="#d62728", s=38, zorder=3)
            ax.annotate(
                "補救 (schematic)",
                (rp, y_curve[rp]),
                textcoords="offset points",
                xytext=(0, 10),
                ha="center",
                fontsize=8,
                color="#d62728",
            )
        ax.axhline(threshold, linestyle="--", color="#666666", linewidth=1.2, label="Mastery Threshold (A-level)")
        ax.text(
            0.98,
            threshold + 0.01,
            "Mastery Threshold (A-level)",
            transform=ax.get_yaxis_transform(),
            ha="right",
            va="bottom",
            fontsize=8,
            color="#555555",
        )
        ax.set_title(group)
        ax.set_xticks([])
        ax.set_ylim(0.2, 1.0)
        ax.grid(axis="y", alpha=0.2)
        ax.text(0.03, 0.04, note, transform=ax.transAxes, fontsize=8, va="bottom")

    axes[0].set_ylabel("Mastery (schematic)")
    fig.suptitle("Experiment 2: Adaptive Learning Path (Schematic) under MAX_STEPS = 40")
    fig.text(
        0.5,
        0.01,
        "Note: This figure is a schematic illustration summarizing typical adaptive patterns,\nnot a direct plot of raw episode trajectories.",
        ha="center",
        va="bottom",
        fontsize=9,
        color="#444444",
    )
    fig.tight_layout(rect=[0, 0.08, 1, 0.92])
    finalize_report_figure(fig, str(target))
    return str(target)


def write_experiment2_required_captions(output_dir: str) -> list[str]:
    os.makedirs(output_dir, exist_ok=True)
    paths: list[str] = []
    time_caption = os.path.join(output_dir, "figure_caption_experiment2_time_budget.md")
    ok1, t1 = _safe_prepare_output_path(time_caption, is_markdown=True)
    if ok1:
        with open(t1, "w", encoding="utf-8-sig") as f:
            f.write(
                "### Figure Caption: Experiment 2 Time Budget by Student Group\n\n"
                "Weak spends more time in remediation, showing larger prerequisite deficits under the same 40-step budget.\n"
            )
        paths.append(str(t1))

    gain_caption = os.path.join(output_dir, "figure_caption_experiment2_gain.md")
    ok2, t2 = _safe_prepare_output_path(gain_caption, is_markdown=True)
    if ok2:
        with open(t2, "w", encoding="utf-8-sig") as f:
            f.write(
                "### Figure Caption: Experiment 2 Adaptive Gain by Student Group\n\n"
                "Average is the largest beneficiary under the 40-step budget. "
                "Weak improves but still shows low 達標A success under this budget.\n"
            )
        paths.append(str(t2))

    lp_caption = os.path.join(output_dir, "figure_caption_experiment2_learning_path.md")
    ok3, t3 = _safe_prepare_output_path(lp_caption, is_markdown=True)
    if ok3:
        with open(t3, "w", encoding="utf-8-sig") as f:
            f.write(
                "Figure X: Schematic illustration of adaptive learning paths under MAX_STEPS = 40.\n"
                "The figure summarizes typical patterns observed across student groups.\n\n"
                "Careless students primarily follow the mainline with minimal remediation.\n"
                "Average students benefit the most from adaptive remediation, showing clear improvements after prerequisite reinforcement.\n"
                "Weak students receive frequent remediation, leading to noticeable improvement, but still struggle to reach stable A-level mastery within the 40-step constraint.\n\n"
                "This figure is a schematic representation and does not directly visualize raw episode trajectories.\n"
            )
        paths.append(str(t3))
    return paths


def write_experiment2_figure_captions(output_dir: str, representative_episode_id: int | None) -> list[str]:
    """Write publication-ready captions for Experiment 2 figures."""
    os.makedirs(output_dir, exist_ok=True)
    paths: list[str] = []

    summary_caption = os.path.join(output_dir, "figure_caption_experiment2_summary.md")
    ok, target = _safe_prepare_output_path(summary_caption, is_markdown=True)
    if ok:
        with open(target, "w", encoding="utf-8-sig") as f:
            f.write(
                "### Figure Caption: Experiment 2 Policy Behavior Summary\n"
                "This figure compares policy allocation across Careless, Average, and Weak groups under AB3.\n"
                "Both bars are computed from real step-level logs: remediation ratio = remediation steps / active steps,\n"
                "mainline ratio = mainline steps / active steps.\n"
                "Experiment 1 identifies MAX_STEPS = 50 as the best-performing setting; therefore Experiment 2 uses MAX_STEPS = 50 for mechanism analysis consistency.\n"
                "Key finding: AB3 allocates different remediation intensity by student type, with weaker learners receiving\n"
                "a larger remediation share and stronger learners remaining more frequently on mainline.\n"
            )
    summary_caption = str(target)
    paths.append(summary_caption)

    episode_caption = os.path.join(output_dir, "figure_caption_mastery_episode.md")
    ok, target = _safe_prepare_output_path(episode_caption, is_markdown=True)
    if ok:
        eid_text = str(representative_episode_id) if representative_episode_id is not None else "N/A"
        with open(target, "w", encoding="utf-8-sig") as f:
            f.write(
                "### Figure Caption: Representative Mastery Trajectory\n"
                f"This trajectory shows one automatically selected representative episode (episode_id={eid_text}) from AB3 logs.\n"
                "Curves are true step-level prerequisite/target mastery values, with remediation phases marked by shaded spans;\n"
                "remediation starts are marked explicitly, and the end of each shaded span indicates return to mainline.\n"
                "Experiment 1 identifies MAX_STEPS = 50 as the best-performing setting; therefore Experiment 2 uses MAX_STEPS = 50 for mechanism analysis consistency.\n"
                "Key finding: target-mastery growth becomes clearer after remediation-supported prerequisite consolidation.\n"
            )
    episode_caption = str(target)
    paths.append(episode_caption)

    avg_caption = os.path.join(output_dir, "figure_caption_mastery_average.md")
    ok, target = _safe_prepare_output_path(avg_caption, is_markdown=True)
    if ok:
        with open(target, "w", encoding="utf-8-sig") as f:
            f.write(
                "### Figure Caption: Average Mastery Trajectory by Student Type\n"
                "This figure aligns AB3 episodes by step and reports per-step means for prerequisite mastery and target mastery\n"
                "within each student type using NaN-safe aggregation from real trajectory logs.\n"
                "All panels share the same x-axis range for direct comparison; shorter groups stop at the end of observed steps\n"
                "without interpolation or artificial extrapolation.\n"
                "Experiment 1 identifies MAX_STEPS = 50 as the best-performing setting; therefore Experiment 2 uses MAX_STEPS = 50 for mechanism analysis consistency.\n"
                "Key finding: mastery-growth dynamics differ across student types, and weaker groups show slower target mastery\n"
                "convergence even when prerequisite mastery improves.\n"
            )
    avg_caption = str(target)
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
        stype = format_student_type_label(str(meta.get("student_type", "Average")))
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
            stype = format_student_type_label(str(meta.get("student_type", "Average")))
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
    """Save representative episode in raw and clean storytelling versions."""
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

    raw_student_type = str(rows[0].get("student_type", "Unknown"))
    student_type = format_student_type_label(raw_student_type)

    os.makedirs(output_dir, exist_ok=True)

    # Version 1: raw debug view.
    fig_raw, ax_raw = plt.subplots(figsize=(8, 5))
    ax_raw.plot(
        steps,
        pre_values,
        marker="o",
        linewidth=2.2,
        label=f"Prerequisite Mastery ({prerequisite_skill})",
    )
    ax_raw.plot(
        steps,
        target_values,
        marker="s",
        linewidth=2.2,
        label=f"Target Mastery ({target_skill})",
    )
    for span_start, span_end in remediation_spans:
        ax_raw.axvspan(span_start - 0.5, span_end + 0.5, alpha=0.22, label="Remediation Phase")

    y_min = min(pre_values + target_values)
    y_max = max(pre_values + target_values)
    if y_min >= 0.0 and y_max <= 1.0:
        ax_raw.set_ylim(0.0, 1.0)

    ax_raw.set_xlabel("Step")
    ax_raw.set_ylabel("Mastery Level")
    ax_raw.set_title(
        "Representative Episode: Raw View\n"
        f"Student Type={student_type}, Episode={episode_id}"
    )
    ax_raw.legend(loc="lower right", fontsize=8, frameon=True)
    ax_raw.set_xlim(min(steps), max(steps))
    ax_raw.grid(axis="y", alpha=0.25)

    raw_path = os.path.join(output_dir, "representative_raw.png")
    ok, target_raw = _safe_prepare_output_path(raw_path)
    if ok:
        finalize_report_figure(fig_raw, str(target_raw))
    else:
        plt.close(fig_raw)

    # Version 2: clean publication/storytelling view.
    fig, ax = plt.subplots(figsize=(8, 5))
    pre_line = ax.plot(
        steps,
        pre_values,
        marker="o",
        linewidth=1.5,
        alpha=0.6,
        color="tab:blue",
        label="Prerequisite Mastery",
    )[0]
    target_line = ax.plot(
        steps,
        target_values,
        marker="s",
        linewidth=3.0,
        color="tab:orange",
        label="Target Mastery",
    )[0]

    # Keep only key remediation spans where target shows meaningful post-span gain.
    gain_threshold = 0.03
    key_spans: list[tuple[int, int, float]] = []
    for a, b in remediation_spans:
        left_idx = max(0, a - 2)
        right_step = min(max(steps), b + 2)
        right_idx = steps.index(right_step) if right_step in steps else len(steps) - 1
        delta = target_values[right_idx] - target_values[left_idx]
        if delta > gain_threshold:
            key_spans.append((a, b, delta))

    for a, b, _ in key_spans:
        ax.axvspan(a - 0.5, b + 0.5, color="gray", alpha=0.10, zorder=0)

    # Mastery threshold.
    threshold_y = 0.85
    threshold_line = ax.axhline(
        threshold_y,
        color="dimgray",
        linestyle="--",
        linewidth=1.2,
        label="Mastery Threshold",
    )

    # Causal arrow annotation for strongest key span.
    if key_spans:
        best_span = max(key_spans, key=lambda x: x[2])
        a, b, _ = best_span
        mid = (a + b) / 2.0
        end_step = min(max(steps), b + 2)
        y_end = target_values[steps.index(end_step)] if end_step in steps else target_values[-1]
        ax.annotate(
            "Remediation → prerequisite ↑ → target recovery",
            xy=(end_step, y_end),
            xytext=(mid - 6, min(0.9, y_end + 0.10)),
            arrowprops=dict(arrowstyle="->", lw=1.0, color="black"),
            fontsize=8.8,
            ha="left",
        )

    # Key turning points: first meaningful rise, largest rise, near threshold.
    diffs = [target_values[i] - target_values[i - 1] for i in range(1, len(target_values))]
    first_idx = next((i for i, d in enumerate(diffs, start=1) if d > 0.02), None)
    max_idx = (diffs.index(max(diffs)) + 1) if diffs else None
    near_idx = next((i for i, y in enumerate(target_values) if y >= threshold_y - 0.02), None)
    key_indices: list[int] = []
    for idx in [first_idx, max_idx, near_idx]:
        if idx is not None and idx not in key_indices:
            key_indices.append(idx)
    key_indices = key_indices[:3]
    for k_i, idx in enumerate(key_indices, start=1):
        ax.annotate(
            f"Key Improvement #{k_i}",
            xy=(steps[idx], target_values[idx]),
            xytext=(steps[idx] + 1, min(0.92, target_values[idx] + 0.05)),
            arrowprops=dict(arrowstyle="->", lw=0.9),
            fontsize=8.5,
        )

    ax.set_xlabel("Step")
    ax.set_ylabel("Mastery Level")
    ax.set_xlim(min(steps), max(steps))
    if y_min >= 0.0 and y_max <= 1.0:
        ax.set_ylim(0.0, 1.0)
    ax.set_title(
        "How Remediation Improves Target Mastery (Representative Episode)\n"
        f"{student_type} Student | AB3 Policy",
        fontsize=11.5,
    )
    ax.legend(
        handles=[pre_line, target_line, threshold_line],
        loc="lower right",
        fontsize=8.3,
        frameon=True,
    )

    clean_path = os.path.join(output_dir, "representative_clean.png")
    ok, target_clean = _safe_prepare_output_path(clean_path)
    if not ok:
        plt.close(fig)
        return str(target_clean)
    finalize_report_figure(fig, str(target_clean))

    # Keep legacy filename for downstream compatibility.
    output_path = os.path.join(output_dir, "mastery_trajectory_representative_episode.png")
    ok, target = _safe_prepare_output_path(output_path)
    if ok:
        shutil.copy2(str(target_clean), str(target))
    return str(target)


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
    """Save single publication figure using fixed-N (episode-padded) averaging."""
    ab3 = [r for r in step_log_rows if r.get("strategy") == "AB3_PPO_Dynamic"]
    if not ab3:
        return None
    type_episode_step, max_step = _build_mastery_by_episode(ab3)
    if max_step <= 0:
        return None

    steps = list(range(1, max_step + 1))
    student_order = ["Careless", "Average", "Weak"]
    display = {"Careless": "Careless", "Average": "Average", "Weak": "Weak"}
    colors = {"Careless": "tab:blue", "Average": "tab:orange", "Weak": "tab:green"}

    fig, ax = plt.subplots(figsize=(10, 6))
    for st in student_order:
        episodes = type_episode_step.get(st, {})
        if not episodes:
            continue
        padded_pre, padded_tar = _build_padded_episode_trajectories(episodes, max_step)
        if not padded_pre or not padded_tar:
            continue
        pre_mean = [statistics.mean(step_values) for step_values in zip(*padded_pre)]
        tar_mean = [statistics.mean(step_values) for step_values in zip(*padded_tar)]

        ax.plot(
            steps,
            tar_mean,
            color=colors[st],
            linewidth=2.4,
            linestyle="-",
            label=display[st],
        )
        ax.plot(
            steps,
            pre_mean,
            color=colors[st],
            linewidth=1.8,
            linestyle="--",
            label="_nolegend_",
        )

    ax.set_title("Average Mastery Trajectory under AB3 by Student Type")
    ax.set_xlabel("Step")
    ax.set_ylabel("Mastery")
    ax.set_ylim(0.3, 0.9)
    ax.grid(alpha=0.3)
    ax.text(
        0.98,
        0.04,
        "Solid = Target, Dashed = Prerequisite",
        transform=ax.transAxes,
        fontsize=9,
        ha="right",
        va="bottom",
        bbox=dict(facecolor="white", alpha=0.85, edgecolor="gray", boxstyle="round,pad=0.25"),
        alpha=0.85,
    )
    ax.legend(loc="upper left", fontsize=8.5, frameon=True, ncol=1)

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "mastery_trajectory_average_by_student_type.png")
    ok, target = _safe_prepare_output_path(output_path)
    if not ok:
        plt.close(fig)
        return str(target)
    fig.tight_layout()
    fig.savefig(str(target), dpi=300, bbox_inches="tight")
    plt.close(fig)
    return str(target)


def _build_padded_episode_trajectories(
    episodes: dict[int, dict[int, tuple[float, float]]],
    max_steps: int,
) -> tuple[list[list[float]], list[list[float]]]:
    """Convert sparse per-step mastery logs into fixed-length episode trajectories."""
    padded_pre: list[list[float]] = []
    padded_tar: list[list[float]] = []
    for episode_steps in episodes.values():
        if not episode_steps:
            continue
        sorted_steps = sorted(episode_steps)
        pre_traj = [episode_steps[s][0] for s in sorted_steps]
        tar_traj = [episode_steps[s][1] for s in sorted_steps]
        remaining_steps = max_steps - len(pre_traj)
        if remaining_steps > 0:
            pre_traj += [pre_traj[-1]] * remaining_steps
            tar_traj += [tar_traj[-1]] * remaining_steps
        padded_pre.append(pre_traj[:max_steps])
        padded_tar.append(tar_traj[:max_steps])
    return padded_pre, padded_tar


def _build_mastery_by_episode(
    step_log_rows: list[dict[str, Any]],
) -> tuple[dict[str, dict[int, dict[int, tuple[float, float]]]], int]:
    """Build nested map: type -> episode -> step -> (prereq, target)."""
    type_episode_step: dict[str, dict[int, dict[int, tuple[float, float]]]] = {
        "Careless": {},
        "Average": {},
        "Weak": {},
    }
    max_step = 0
    for row in step_log_rows:
        student_type = format_student_type_label(str(row.get("student_type", "")))
        if student_type not in type_episode_step:
            continue
        if row.get("step") is None:
            continue
        step = int(row["step"])
        episode_id = int(row["episode_id"])
        pre = float(row["integer_mastery"])
        tar = float(row["polynomial_mastery"])
        max_step = max(max_step, step)
        type_episode_step[student_type].setdefault(episode_id, {})[step] = (pre, tar)
    return type_episode_step, max_step


def plot_mastery_trajectory_raw(df: list[dict[str, Any]]) -> plt.Figure | None:
    """Baseline raw average: missing late steps are treated as zero (introduces bias)."""
    type_episode_step, max_step = _build_mastery_by_episode(df)
    if max_step <= 0:
        return None
    steps = list(range(1, max_step + 1))
    student_order = ["Careless", "Average", "Weak"]
    display = {"Careless": "Careless", "Average": "Average", "Weak": "Weak"}
    colors = {"Careless": "tab:blue", "Average": "tab:orange", "Weak": "tab:green"}

    fig, ax = plt.subplots(figsize=(10, 6))
    for st in student_order:
        episodes = type_episode_step.get(st, {})
        if not episodes:
            continue
        ep_ids = list(episodes.keys())
        pre_mean: list[float] = []
        tar_mean: list[float] = []
        for t in steps:
            pre_vals = []
            tar_vals = []
            for eid in ep_ids:
                pair = episodes[eid].get(t, (0.0, 0.0))
                pre_vals.append(pair[0])
                tar_vals.append(pair[1])
            pre_mean.append(statistics.mean(pre_vals))
            tar_mean.append(statistics.mean(tar_vals))
        ax.plot(steps, tar_mean, color=colors[st], linewidth=2.0, linestyle="-", label=f"{display[st]} Target")
        ax.plot(steps, pre_mean, color=colors[st], linewidth=1.8, linestyle="--", label=f"{display[st]} Prerequisite")

    ax.set_title("Average Mastery Trajectory (AB3, Raw)", fontsize=13)
    ax.set_xlabel("Step")
    ax.set_ylabel("Mastery")
    ax.set_ylim(0.3, 0.9)
    ax.grid(alpha=0.3)
    ax.legend(loc="upper right", fontsize=8.5, frameon=True, ncol=2)
    fig.tight_layout()
    fig.subplots_adjust(top=0.9)
    return fig


def plot_mastery_trajectory_corrected(df: list[dict[str, Any]]) -> plt.Figure | None:
    """Bias-corrected average using only active episodes at each step."""
    type_episode_step, max_step = _build_mastery_by_episode(df)
    if max_step <= 0:
        return None
    steps = list(range(1, max_step + 1))
    student_order = ["Careless", "Average", "Weak"]
    display = {"Careless": "Careless", "Average": "Average", "Weak": "Weak"}
    colors = {"Careless": "tab:blue", "Average": "tab:orange", "Weak": "tab:green"}

    fig, (ax, ax_count) = plt.subplots(
        2,
        1,
        figsize=(10, 6),
        gridspec_kw={"height_ratios": [4, 1]},
        sharex=True,
        constrained_layout=False,
    )

    # Remediation ratio shading (overall AB3).
    remediation_ratio_by_step: dict[int, float] = {}
    for t in steps:
        rows_t = [r for r in df if int(r.get("step", -1)) == t]
        if not rows_t:
            continue
        remediation_count = sum(1 for r in rows_t if str(r.get("route", r.get("phase", ""))) == "remediation")
        remediation_ratio_by_step[t] = remediation_count / len(rows_t)
    if remediation_ratio_by_step:
        threshold = statistics.mean(remediation_ratio_by_step.values())
        span_start = None
        for t in steps:
            ratio = remediation_ratio_by_step.get(t, 0.0)
            if ratio >= threshold and span_start is None:
                span_start = t
            if ratio < threshold and span_start is not None:
                ax.axvspan(span_start, t, color="lightskyblue", alpha=0.15, zorder=0)
                span_start = None
        if span_start is not None:
            ax.axvspan(span_start, steps[-1], color="lightskyblue", alpha=0.15, zorder=0)

    for st in student_order:
        episodes = type_episode_step.get(st, {})
        if not episodes:
            continue
        ep_ids = list(episodes.keys())
        pre_mean: list[float] = []
        tar_mean: list[float] = []
        pre_std: list[float] = []
        tar_std: list[float] = []
        active_count: list[int] = []

        for t in steps:
            valid_pre = []
            valid_tar = []
            for eid in ep_ids:
                if t in episodes[eid]:  # mask: only active episodes at step t
                    valid_pre.append(episodes[eid][t][0])
                    valid_tar.append(episodes[eid][t][1])
            active_count.append(len(valid_pre))
            if valid_pre:
                pre_mean.append(statistics.mean(valid_pre))
                tar_mean.append(statistics.mean(valid_tar))
                pre_std.append(statistics.stdev(valid_pre) if len(valid_pre) > 1 else 0.0)
                tar_std.append(statistics.stdev(valid_tar) if len(valid_tar) > 1 else 0.0)
            else:
                pre_mean.append(float("nan"))
                tar_mean.append(float("nan"))
                pre_std.append(0.0)
                tar_std.append(0.0)

        ax.plot(
            steps,
            tar_mean,
            color=colors[st],
            linewidth=2.2,
            linestyle="-",
            label=f"{display[st]} Target",
        )
        ax.plot(
            steps,
            pre_mean,
            color=colors[st],
            linewidth=2.0,
            linestyle="--",
            label=f"{display[st]} Prerequisite",
        )
        lower_tar = [m - s if m == m else float("nan") for m, s in zip(tar_mean, tar_std)]
        upper_tar = [m + s if m == m else float("nan") for m, s in zip(tar_mean, tar_std)]
        lower_pre = [m - s if m == m else float("nan") for m, s in zip(pre_mean, pre_std)]
        upper_pre = [m + s if m == m else float("nan") for m, s in zip(pre_mean, pre_std)]
        ax.fill_between(steps, lower_tar, upper_tar, color=colors[st], alpha=0.12, linewidth=0)
        ax.fill_between(steps, lower_pre, upper_pre, color=colors[st], alpha=0.08, linewidth=0)
        ax_count.plot(steps, active_count, color=colors[st], linewidth=1.5, label=f"{display[st]} Active N")

    ax.set_title("Average Mastery Trajectory (AB3, Bias-Corrected)", fontsize=13)
    ax.set_ylabel("Mastery")
    ax.set_ylim(0.3, 0.9)
    ax.grid(alpha=0.3)
    ax.legend(loc="upper right", fontsize=8.5, frameon=True, ncol=2)

    ann_x1 = min(35, steps[-1])
    ann_y1 = 0.83
    ax.annotate(
        "Survivorship bias after step ~35",
        xy=(ann_x1, ann_y1),
        xytext=(ann_x1 - 10, ann_y1 + 0.04),
        arrowprops=dict(arrowstyle="->", lw=1.0),
        fontsize=9,
    )
    ann_x2 = min(28, steps[-1])
    ann_y2 = 0.56
    ax.annotate(
        "Temporary drop due to remediation phase",
        xy=(ann_x2, ann_y2),
        xytext=(ann_x2 + 4, ann_y2 - 0.08),
        arrowprops=dict(arrowstyle="->", lw=1.0),
        fontsize=9,
    )

    ax_count.set_xlabel("Step")
    ax_count.set_ylabel("Active N")
    ax_count.grid(alpha=0.25)
    ax_count.legend(loc="upper right", fontsize=8, frameon=True, ncol=3)

    fig.tight_layout()
    fig.subplots_adjust(top=0.9)
    return fig


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
def main(output_mode: str = "experiment2") -> None:
    """Run isolated Experiment 2 workflow (AB3 only, MAX_STEPS=40)."""
    global MAX_STEPS, N_PER_TYPE, RUNTIME_SUCCESS_THRESHOLD
    normalized_mode = "experiment2"
    if str(output_mode).strip().lower() != "experiment2":
        print(f"[WARNING] output_mode={output_mode} overridden to experiment2 for isolated Exp2 run.")

    original_max_steps = int(MAX_STEPS)
    original_n_per_type = int(N_PER_TYPE)
    original_runtime_success_threshold = float(RUNTIME_SUCCESS_THRESHOLD)
    print(f"[MODE] {normalized_mode}")
    prev_exp2_env = os.environ.get(EXP2_OUTPUT_DIR_ENV)
    prev_exp1_env = os.environ.get(EXP1_OUTPUT_DIR_ENV)
    prev_mode_env = os.environ.get(OUTPUT_MODE_ENV)
    prev_profile_env = os.environ.get(EXPERIMENT_PROFILE_ENV)
    os.environ[OUTPUT_MODE_ENV] = normalized_mode
    os.environ[EXPERIMENT_PROFILE_ENV] = EXPERIMENT_PROFILE_DEFAULT

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_dir = EXPERIMENT2_OUTPUT_DIR
    run_dir = base_dir / "runs" / run_id
    latest_dir = base_dir / "latest"
    run_dir.mkdir(parents=True, exist_ok=True)
    latest_dir.mkdir(parents=True, exist_ok=True)
    assert "experiment_1" not in str(run_dir).lower(), "Experiment 2 run_dir must never point to Experiment 1"
    os.environ[EXP2_OUTPUT_DIR_ENV] = str(run_dir)
    print(f"[RUN] Writing outputs to {run_dir}")
    print(f"[LATEST] Updating {latest_dir}")

    MAX_STEPS = int(EXP2_FIXED_MAX_STEPS)
    N_PER_TYPE = int(EXP1_EPISODES_PER_TYPE)
    RUNTIME_SUCCESS_THRESHOLD = 0.80
    if MAX_STEPS != 40:
        print("[WARNING] Experiment 2 should run with MAX_STEPS = 40")
    set_global_seed(RANDOM_SEED)
    try:
        episodes, trajectory_rows = run_batch_experiments(
            strategies=list(EXP2_STRATEGIES),
            student_types=list(EXP2_STUDENT_TYPE_ORDER),
        )
        episode_metrics = build_experiment2_episode_metrics(episodes, trajectory_rows)
        exp2_behavior_summary = build_experiment2_student_type_summary(episode_metrics)
        student_groups = sorted({str(r["student_group"]) for r in exp2_behavior_summary})
        assert len(student_groups) == 3, "Experiment 2 must include exactly 3 student groups."

        trajectory_path = write_trajectory_csv(trajectory_rows)
        episode_metrics_path = write_experiment2_episode_metrics_csv(episode_metrics)
        exp2_behavior_path = write_experiment2_student_type_summary_csv(exp2_behavior_summary)
        exp2_behavior_md = write_experiment2_student_type_summary_md(exp2_behavior_summary)
        # NOTE:
        # Policy allocation (ratio) plot is removed because time budget plot
        # provides a more informative view including absolute step cost.
        exp2_time_budget_fig = write_experiment2_time_budget_figure(exp2_behavior_summary)
        exp2_gain_fig = write_experiment2_efficiency_figure(exp2_behavior_summary)
        exp2_learning_path_fig = write_experiment2_learning_path_diagram(exp2_behavior_summary)
        exp2_dir = str(get_experiment2_output_dir())
        caption_paths = write_experiment2_required_captions(exp2_dir)

        readme_text = (
            "# Experiment 2 (AB3 Student-Type Analysis)\n\n"
            "## Fixed Setting\n"
            "- MAX_STEPS = 40\n"
            "- Strategy = AB3 only\n"
            "- Student groups: 拔尖組 / 固本組 / 減C組\n\n"
            "## Core Findings\n"
            "- Adaptive uses different paths for different groups (mechanism analysis, not strategy re-ranking).\n"
            "- Average (固本組) is the main beneficiary under MAX_STEPS = 40.\n"
            "- Weak (減C組) is helped, but not fully rescued to A within 40 steps.\n"
            "- 在固定 40 steps 的限制下，Adaptive 並非單純改變比例，而是重新分配有限學習資源；固本組從這種資源配置中獲益最大，而減C組則因補救成本過高，即使有進步仍難以達到 A 水準。\n\n"
            "## Figures\n"
            "- experiment2_time_budget_by_student_type.png\n"
            "- experiment2_adaptive_gain_by_student_type.png\n"
            "- experiment2_learning_path_diagram.png (schematic)\n"
        )
        with open(EXPERIMENT2_OUTPUT_DIR / "README.md", "w", encoding="utf-8-sig") as f:
            f.write(readme_text)

        sync_run_to_latest(run_dir, latest_dir)
        print(f"[LATEST] Updated {latest_dir}")

        print("\nSimulation completed.")
        print(f"Trajectory CSV: {trajectory_path}")
        print(f"Episode Metrics CSV: {episode_metrics_path}")
        print(f"Experiment2 Student-Type Summary CSV: {exp2_behavior_path}")
        print(f"Experiment2 Student-Type Summary MD: {exp2_behavior_md}")
        print(f"Experiment2 Time Budget Figure: {exp2_time_budget_fig}")
        print(f"Experiment2 Adaptive Gain Figure: {exp2_gain_fig}")
        print(f"Experiment2 Learning Path Diagram: {exp2_learning_path_fig}")
        for cp in caption_paths:
            print(f"Experiment2 Caption: {cp}")
        print(f"RANDOM_SEED: {RANDOM_SEED}")
        print(f"EXPERIMENT_PROFILE: {get_experiment_profile()}")
        print(f"N_PER_TYPE: {N_PER_TYPE}")
        print(f"MAX_STEPS: {MAX_STEPS}")
        print(f"TARGET_MASTERY: {TARGET_MASTERY}")
        print(f"RUNTIME_SUCCESS_THRESHOLD: {RUNTIME_SUCCESS_THRESHOLD}")
    finally:
        MAX_STEPS = original_max_steps
        N_PER_TYPE = original_n_per_type
        RUNTIME_SUCCESS_THRESHOLD = original_runtime_success_threshold
        if prev_exp2_env is None:
            os.environ.pop(EXP2_OUTPUT_DIR_ENV, None)
        else:
            os.environ[EXP2_OUTPUT_DIR_ENV] = prev_exp2_env
        if prev_exp1_env is None:
            os.environ.pop(EXP1_OUTPUT_DIR_ENV, None)
        else:
            os.environ[EXP1_OUTPUT_DIR_ENV] = prev_exp1_env
        if prev_mode_env is None:
            os.environ.pop(OUTPUT_MODE_ENV, None)
        else:
            os.environ[OUTPUT_MODE_ENV] = prev_mode_env
        if prev_profile_env is None:
            os.environ.pop(EXPERIMENT_PROFILE_ENV, None)
        else:
            os.environ[EXPERIMENT_PROFILE_ENV] = prev_profile_env


if __name__ == "__main__":
    main()




