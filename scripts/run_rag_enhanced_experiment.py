# -*- coding: utf-8 -*-
# ==============================================================================
# ID: run_rag_enhanced_experiment.py
# Version: V1.0.0 (Experiment 5 RAG Enhanced)
# Last Updated: 2026-04-15
# Author: *Steve
#
# [Description]:
#   RAG 延伸評測：在對齊的 Weak 支援下比較無 RAG、RAG v1、RAG v2，
#   彙整使用量、觸發效益、子技能與斷點變化，並透過共用繪圖管線產生圖表。
#
# [Database Schema Usage]:
#   無直接資料庫操作。
#
# [Logic Flow]:
#   1. 定義 CONDITIONS 與額外步數。
#   2. 批次模擬並聚合指標。
#   3. 呼叫 plot_rag_v2_enhanced_results。
# ==============================================================================

import csv
import random
import sys
from collections import Counter
from pathlib import Path

_STUDY_ROOT = Path(__file__).resolve().parent / "adaptive_strategy_study"
if str(_STUDY_ROOT) not in sys.path:
    sys.path.insert(0, str(_STUDY_ROOT))
import study_paths as _study_paths  # noqa: E402

_study_paths.ensure_repo_root_on_syspath()
_study_paths.ensure_exp2_mechanism_on_syspath()
_study_paths.ensure_common_on_syspath()

import simulate_student  # noqa: E402
from plot_experiment_results import plot_rag_v2_enhanced_results  # noqa: E402

REPORTS_DIR = _study_paths.study_reports_root()
EXP5_DIR = REPORTS_DIR / "experiment_5_rag_enhanced"

FOUNDATION_EXTRA_STEPS = 20

CONDITIONS = [
    {"name": "weak_ab3_foundation", "enable_rag": False, "rag_version": "v1"},
    {"name": "weak_ab3_foundation_rag_v1", "enable_rag": True, "rag_version": "v1"},
    {"name": "weak_ab3_foundation_rag_v2", "enable_rag": True, "rag_version": "v2"},
]


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _mean_reached(values: list[int | None]) -> float | str:
    valid = [float(v) for v in values if v is not None]
    return (_mean(valid) if valid else "")


def run_condition(condition: dict[str, object]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """Run Weak + AB3 episodes under a given RAG condition."""
    name = str(condition["name"])
    enable_rag = bool(condition["enable_rag"])
    rag_version = str(condition["rag_version"])

    simulate_student.WEAK_FOUNDATION_EXTRA_STEPS = FOUNDATION_EXTRA_STEPS
    simulate_student.ENABLE_RAG_TUTOR = enable_rag
    simulate_student.RAG_TUTOR_VERSION = rag_version
    simulate_student.MAX_RAG_INTERVENTIONS_PER_EPISODE = 5 if rag_version == "v2" else 3

    seed_offset = {"weak_ab3_foundation": 0, "weak_ab3_foundation_rag_v1": 1000, "weak_ab3_foundation_rag_v2": 2000}[name]
    random.seed(simulate_student.RANDOM_SEED + seed_offset)

    episodes: list[dict[str, object]] = []
    trajectory: list[dict[str, object]] = []
    for episode_id in range(1, simulate_student.N_PER_TYPE + 1):
        ep, rows = simulate_student.simulate_episode(
            student_type="Weak",
            strategy_name="AB3_PPO_Dynamic",
            episode_id=episode_id,
        )
        ep["condition"] = name
        episodes.append(ep)
        for row in rows:
            row["condition"] = name
            trajectory.append(row)
    return episodes, trajectory


def build_summary(
    all_episodes: dict[str, list[dict[str, object]]],
    all_traj: dict[str, list[dict[str, object]]],
) -> list[dict[str, object]]:
    """Top-level comparison summary across baseline/rag v1/rag v2."""
    rows: list[dict[str, object]] = []
    for cfg in CONDITIONS:
        name = str(cfg["name"])
        episodes = all_episodes.get(name, [])
        traj = all_traj.get(name, [])
        if not episodes:
            continue

        triggered = [r for r in traj if int(r.get("rag_triggered", 0)) == 1]
        triggered_correct = [
            r for r in triggered if int(r.get("is_correct", 0)) == 1
        ]
        rag_effectiveness_correct = _mean(
            [float(r.get("rag_bonus_after_decay", 0.0)) for r in triggered_correct]
        )
        rag_effectiveness_triggered = _mean(
            [float(r.get("rag_bonus_after_decay", 0.0)) for r in triggered]
        )
        rag_effectiveness = (
            rag_effectiveness_correct
            if len(triggered_correct) > 0
            else rag_effectiveness_triggered
        )
        rag_usage_rate = _mean([1.0 if float(e.get("rag_intervention_count", 0.0)) > 0 else 0.0 for e in episodes])
        avg_rag = _mean([float(e.get("rag_intervention_count", 0.0)) for e in episodes])
        iso_gain = _mean(
            [
                float(e["final_subskills"]["family_isomorphism"])
                - float(e["initial_subskills"]["family_isomorphism"])
                for e in episodes
            ]
        )

        rows.append(
            {
                "condition": name,
                "success_rate": round(_mean([float(e["success"]) for e in episodes]), 4),
                "avg_final_polynomial_mastery": round(
                    _mean([float(e["final_mastery"]) for e in episodes]), 4
                ),
                "avg_total_steps": round(_mean([float(e["total_steps"]) for e in episodes]), 4),
                "family_isomorphism_gain": round(iso_gain, 4),
                "breakpoint_distribution": "see rag_breakpoint_shift.csv",
                "rag_usage_rate": round(rag_usage_rate, 4),
                "avg_rag_per_episode": round(avg_rag, 4),
                "rag_effectiveness": round(rag_effectiveness, 6),
            }
        )
    return rows


def build_student_type_summary(all_episodes: dict[str, list[dict[str, object]]]) -> list[dict[str, object]]:
    """Weak-only student summary by condition."""
    rows: list[dict[str, object]] = []
    for cfg in CONDITIONS:
        name = str(cfg["name"])
        episodes = all_episodes.get(name, [])
        if not episodes:
            continue
        rows.append(
            {
                "condition": name,
                "student_type": "Weak",
                "success_rate": round(_mean([float(e["success"]) for e in episodes]), 4),
                "avg_final_polynomial_mastery": round(
                    _mean([float(e["final_mastery"]) for e in episodes]), 4
                ),
                "avg_total_steps": round(_mean([float(e["total_steps"]) for e in episodes]), 4),
                "avg_reached_mastery_step": (
                    round(_mean_reached([e["reached_mastery_step"] for e in episodes]), 4)
                    if _mean_reached([e["reached_mastery_step"] for e in episodes]) != ""
                    else ""
                ),
            }
        )
    return rows


def build_subskill_summary(all_episodes: dict[str, list[dict[str, object]]]) -> list[dict[str, object]]:
    """Per-subskill gain by condition."""
    rows: list[dict[str, object]] = []
    for cfg in CONDITIONS:
        name = str(cfg["name"])
        episodes = all_episodes.get(name, [])
        if not episodes:
            continue
        for subskill in simulate_student.POLYNOMIAL_SUBSKILLS:
            init_vals = [float(e["initial_subskills"][subskill]) for e in episodes]
            final_vals = [float(e["final_subskills"][subskill]) for e in episodes]
            avg_init = _mean(init_vals)
            avg_final = _mean(final_vals)
            rows.append(
                {
                    "condition": name,
                    "subskill": subskill,
                    "avg_initial_mastery": round(avg_init, 4),
                    "avg_final_mastery": round(avg_final, 4),
                    "avg_gain": round(avg_final - avg_init, 4),
                }
            )
    return rows


def build_breakpoint_shift(all_episodes: dict[str, list[dict[str, object]]]) -> list[dict[str, object]]:
    """Weakest-subskill distribution among failed episodes."""
    rows: list[dict[str, object]] = []
    for cfg in CONDITIONS:
        name = str(cfg["name"])
        episodes = all_episodes.get(name, [])
        failed = [e for e in episodes if int(e["success"]) == 0]
        weakest: list[str] = []
        for e in failed:
            final_map = e["final_subskills"]
            weakest.append(
                min(
                    simulate_student.POLYNOMIAL_SUBSKILLS,
                    key=lambda s: float(final_map[s]),
                )
            )
        total = len(failed)
        counts = Counter(weakest)
        for subskill in simulate_student.POLYNOMIAL_SUBSKILLS:
            count = int(counts.get(subskill, 0))
            pct = (count / total) if total > 0 else 0.0
            rows.append(
                {
                    "condition": name,
                    "subskill": subskill,
                    "count": count,
                    "percentage": round(pct, 4),
                }
            )
    return rows


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    """Write CSV in UTF-8 BOM format."""
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main() -> None:
    """Run Experiment 5: Weak + Enhanced RAG Tutor (v2)."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    EXP5_DIR.mkdir(parents=True, exist_ok=True)

    original_extra = simulate_student.WEAK_FOUNDATION_EXTRA_STEPS
    original_enable = simulate_student.ENABLE_RAG_TUTOR
    original_version = simulate_student.RAG_TUTOR_VERSION
    original_max_interventions = simulate_student.MAX_RAG_INTERVENTIONS_PER_EPISODE

    all_episodes: dict[str, list[dict[str, object]]] = {}
    all_traj: dict[str, list[dict[str, object]]] = {}
    try:
        for cfg in CONDITIONS:
            name = str(cfg["name"])
            print(f"Running condition: {name}")
            episodes, traj = run_condition(cfg)
            all_episodes[name] = episodes
            all_traj[name] = traj
    finally:
        simulate_student.WEAK_FOUNDATION_EXTRA_STEPS = original_extra
        simulate_student.ENABLE_RAG_TUTOR = original_enable
        simulate_student.RAG_TUTOR_VERSION = original_version
        simulate_student.MAX_RAG_INTERVENTIONS_PER_EPISODE = original_max_interventions

    summary_rows = build_summary(all_episodes, all_traj)
    student_rows = build_student_type_summary(all_episodes)
    subskill_rows = build_subskill_summary(all_episodes)
    breakpoint_rows = build_breakpoint_shift(all_episodes)

    summary_path = EXP5_DIR / "rag_vs_baseline_summary.csv"
    student_path = EXP5_DIR / "rag_student_type_summary.csv"
    subskill_path = EXP5_DIR / "rag_subskill_summary.csv"
    breakpoint_path = EXP5_DIR / "rag_breakpoint_shift.csv"

    write_csv(
        summary_path,
        [
            "condition",
            "success_rate",
            "avg_final_polynomial_mastery",
            "avg_total_steps",
            "family_isomorphism_gain",
            "breakpoint_distribution",
            "rag_usage_rate",
            "avg_rag_per_episode",
            "rag_effectiveness",
        ],
        summary_rows,
    )
    write_csv(
        student_path,
        ["condition", "student_type", "success_rate", "avg_final_polynomial_mastery", "avg_total_steps", "avg_reached_mastery_step"],
        student_rows,
    )
    write_csv(
        subskill_path,
        ["condition", "subskill", "avg_initial_mastery", "avg_final_mastery", "avg_gain"],
        subskill_rows,
    )
    write_csv(
        breakpoint_path,
        ["condition", "subskill", "count", "percentage"],
        breakpoint_rows,
    )

    plot_rag_v2_enhanced_results(str(EXP5_DIR))

    print("Experiment 5 completed.")
    print(f"Output CSV: {summary_path}")
    print(f"Output CSV: {student_path}")
    print(f"Output CSV: {subskill_path}")
    print(f"Output CSV: {breakpoint_path}")
    print(f"Output Figure: {EXP5_DIR / 'fig_rag_v2_success_rate.png'}")
    print(f"Output Figure: {EXP5_DIR / 'fig_rag_v2_mastery.png'}")
    print(f"Output Figure: {EXP5_DIR / 'fig_rag_v2_subskill_gain.png'}")
    print(f"Output Figure: {EXP5_DIR / 'fig_rag_v2_breakpoint_shift.png'}")
    print(f"Output Figure: {EXP5_DIR / 'fig_rag_usage_distribution.png'}")


if __name__ == "__main__":
    main()
