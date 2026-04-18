# -*- coding: utf-8 -*-
# ==============================================================================
# ID: run_weak_foundation_support_experiment.py
# Version: V1.0.0 (Experiment 3 Legacy Flow)
# Last Updated: 2026-04-15
# Author: *Steve
#
# [Description]:
#   Exp3 早期／完整流程：多 seed、總步數放寬策略下分析 Weak 組達標所需步數與成本，
#   產生多張 Exp3 圖表與表格（非最小 RQ3 單一入口，但保留可重現管線）。
#
# [Database Schema Usage]:
#   無直接資料庫操作。
#
# [Logic Flow]:
#   1. 設定 MAX_STEPS 清單與種子。
#   2. 模擬並彙總。
#   3. 呼叫 plot_experiment_results 輸出圖檔。
# ==============================================================================

from __future__ import annotations

import csv
import os
import random
import statistics
import sys
from collections import Counter
from pathlib import Path
from typing import Any

_STUDY_ROOT = Path(__file__).resolve().parents[1]
if str(_STUDY_ROOT) not in sys.path:
    sys.path.insert(0, str(_STUDY_ROOT))
import study_paths as _study_paths  # noqa: E402

_study_paths.ensure_repo_root_on_syspath()
_study_paths.ensure_exp2_mechanism_on_syspath()
_study_paths.ensure_common_on_syspath()

import simulate_student  # noqa: E402
from plot_experiment_results import (  # noqa: E402
    create_timestamped_run_dir,
    plot_exp3_multiseed_results,
    plot_exp3_marginal_cost,
    plot_weak_foundation_support_results,
    setup_report_style,
    sync_run_to_latest,
)

REPORTS_DIR = _study_paths.study_reports_root()
EXP3_DIR = REPORTS_DIR / "experiment_3_weak_foundation_support"
EXP3_OUTPUT_DIR_ENV = "MATHPROJECT_EXP3_OUTPUT_DIR"

MAX_STEPS_LIST = [30, 40, 50, 60, 70]
SEED_LIST = [42, 43, 44, 45, 46, 47, 48, 49, 50, 51]
EXP3_SUCCESS_THRESHOLD = 0.60


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _std(values: list[float]) -> float:
    if len(values) <= 1:
        return 0.0
    return float(statistics.pstdev(values))


def _to_interp(success_rate: float, delta_success: float | None) -> str:
    if success_rate >= 0.75:
        return "High escape-from-C rate under current total-step budget."
    if delta_success is not None and delta_success <= 0:
        return "Additional steps show diminishing returns in this region."
    if success_rate >= 0.50:
        return "Meaningful reduction of C-range population."
    return "Some improvement observed, but many students remain below B threshold."


def _to_multiseed_interp(mean_escape_pct: float, delta_pct: float | None, std_pct: float) -> str:
    if mean_escape_pct < 15:
        return "Low escape rate under constrained budget."
    if delta_pct is not None and delta_pct >= 15:
        return "Substantial improvement with moderate extra steps."
    if delta_pct is not None and delta_pct > 0:
        if std_pct >= 5:
            return "Performance improves, though cross-seed variance remains visible."
        return "Performance continues to improve, but gains become less stable."
    if delta_pct is not None and abs(delta_pct) < 1e-9:
        return "No meaningful average gain over the previous budget."
    if delta_pct is not None and delta_pct < 0:
        return "Higher budget does not improve mean escape rate; possible diminishing returns."
    return "Baseline condition for multi-seed comparison."


def _validate_exp3_output_path(path: Path) -> None:
    low = str(path).replace("\\", "/").lower()
    if "experiment_1_ablation" in low or "experiment_2_ab3_student_types" in low:
        raise RuntimeError(f"Exp3 output path points to forbidden location: {path}")


def _format_delta(delta_pct: float | None) -> str:
    if delta_pct is None:
        return "—"
    sign = "+" if delta_pct >= 0 else ""
    return f"{sign}{delta_pct:.1f}%"


def run_total_step_condition(max_steps: int, seed: int) -> list[dict[str, Any]]:
    """Run AB3 + Weak episodes for one (MAX_STEPS, seed) condition."""
    random.seed(int(seed))
    simulate_student.MAX_STEPS = int(max_steps)
    simulate_student.WEAK_FOUNDATION_EXTRA_STEPS = 0

    episodes: list[dict[str, Any]] = []
    for episode_id in range(1, int(simulate_student.N_PER_TYPE) + 1):
        episode, _ = simulate_student.simulate_episode(
            student_type="Weak",
            strategy_name="AB3_PPO_Dynamic",
            episode_id=episode_id,
        )
        episode["seed"] = int(seed)
        episode["max_steps"] = int(max_steps)
        episodes.append(episode)
    return episodes


def build_seed_level_summary_row(max_steps: int, seed: int, episodes: list[dict[str, Any]]) -> dict[str, Any]:
    mixed = {
        str(e.get("student_type", ""))
        for e in episodes
        if str(e.get("student_type", "")) != "Weak"
    }
    if mixed:
        print(f"[WARNING] Non-Weak student types detected and ignored: {sorted(mixed)}")
        episodes = [e for e in episodes if str(e.get("student_type", "")) == "Weak"]

    success_rate = _mean(
        [1.0 if float(e["final_mastery"]) >= float(EXP3_SUCCESS_THRESHOLD) else 0.0 for e in episodes]
    )
    return {
        "max_steps": int(max_steps),
        "seed": int(seed),
        "episodes": int(len(episodes)),
        "escape_from_c_rate": round(float(success_rate), 6),
        "avg_final_mastery": round(_mean([float(e["final_mastery"]) for e in episodes]), 6),
        "avg_steps_used": round(_mean([float(e["total_steps"]) for e in episodes]), 6),
        "avg_mastery_gain": round(_mean([float(e["mastery_gain"]) for e in episodes]), 6),
    }


def build_multiseed_summary(seed_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    prev_mean_escape_pct: float | None = None

    for max_steps in MAX_STEPS_LIST:
        cond_rows = [r for r in seed_rows if int(r["max_steps"]) == int(max_steps)]
        if not cond_rows:
            continue
        escapes_pct = [float(r["escape_from_c_rate"]) * 100.0 for r in cond_rows]
        finals = [float(r["avg_final_mastery"]) for r in cond_rows]
        steps = [float(r["avg_steps_used"]) for r in cond_rows]
        gains = [float(r["avg_mastery_gain"]) for r in cond_rows]

        mean_escape_pct = _mean(escapes_pct)
        std_escape_pct = _std(escapes_pct)
        mean_final = _mean(finals)
        std_final = _std(finals)
        mean_steps = _mean(steps)
        std_steps = _std(steps)
        mean_gain = _mean(gains)
        std_gain = _std(gains)

        delta_pct = None if prev_mean_escape_pct is None else (mean_escape_pct - prev_mean_escape_pct)
        rows.append(
            {
                "MAX_STEPS": int(max_steps),
                "seeds": int(len(cond_rows)),
                "mean_escape_from_c_rate_pct": round(mean_escape_pct, 4),
                "std_escape_from_c_rate_pct": round(std_escape_pct, 4),
                "mean_final_mastery": round(mean_final, 6),
                "std_final_mastery": round(std_final, 6),
                "mean_steps_used": round(mean_steps, 6),
                "std_steps_used": round(std_steps, 6),
                "mean_mastery_gain": round(mean_gain, 6),
                "std_mastery_gain": round(std_gain, 6),
                "interpretation": _to_multiseed_interp(mean_escape_pct, delta_pct, std_escape_pct),
            }
        )
        prev_mean_escape_pct = mean_escape_pct
    return rows


def build_legacy_summary_from_multiseed(multiseed_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    prev_success: float | None = None
    for r in multiseed_rows:
        success_rate = float(r["mean_escape_from_c_rate_pct"]) / 100.0
        success_rate_pct = success_rate * 100.0
        cost_per_1pct_escape = "" if success_rate_pct <= 0 else round(float(r["mean_steps_used"]) / success_rate_pct, 4)
        delta_success = None if prev_success is None else round(success_rate - prev_success, 4)
        rows.append(
            {
                "max_steps": int(r["MAX_STEPS"]),
                "total_episodes": int(r["seeds"]) * int(simulate_student.N_PER_TYPE),
                "success_rate": round(success_rate, 6),
                "avg_final_mastery": round(float(r["mean_final_mastery"]), 6),
                "avg_steps_used": round(float(r["mean_steps_used"]), 6),
                "avg_mastery_gain": round(float(r["mean_mastery_gain"]), 6),
                "cost_per_1pct_escape": cost_per_1pct_escape,
                "interpretation": _to_interp(success_rate, delta_success),
            }
        )
        prev_success = success_rate
    return rows


def _to_marginal_interp(delta_escape_pct: float, marginal_cost: float | None) -> str:
    if delta_escape_pct <= 0:
        return "No additional escape benefit in this interval."
    if marginal_cost is None:
        return "No additional escape benefit; marginal cost is undefined or non-meaningful."
    if delta_escape_pct >= 15 and marginal_cost <= 0.6:
        return "Highly efficient interval for reducing the C population."
    if marginal_cost <= 0.8:
        return "Improvement continues with acceptable efficiency."
    return "Improvement continues, but with reduced efficiency."


def build_marginal_cost_rows(multiseed_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    sorted_rows = sorted(multiseed_rows, key=lambda r: int(r["MAX_STEPS"]))
    for i in range(1, len(sorted_rows)):
        prev_r = sorted_rows[i - 1]
        curr_r = sorted_rows[i]
        from_steps = int(prev_r["MAX_STEPS"])
        to_steps = int(curr_r["MAX_STEPS"])
        from_escape = float(prev_r["mean_escape_from_c_rate_pct"])
        to_escape = float(curr_r["mean_escape_from_c_rate_pct"])
        delta_escape = to_escape - from_escape
        from_used = float(prev_r["mean_steps_used"])
        to_used = float(curr_r["mean_steps_used"])
        delta_steps = to_used - from_used
        if delta_escape <= 0:
            marginal_cost: float | str = "NA"
            marginal_cost_num: float | None = None
        else:
            marginal_cost_num = delta_steps / delta_escape
            marginal_cost = round(marginal_cost_num, 6)
        rows.append(
            {
                "from_max_steps": from_steps,
                "to_max_steps": to_steps,
                "from_mean_escape_rate_pct": round(from_escape, 4),
                "to_mean_escape_rate_pct": round(to_escape, 4),
                "delta_escape_rate_pct": round(delta_escape, 4),
                "from_mean_steps_used": round(from_used, 6),
                "to_mean_steps_used": round(to_used, 6),
                "delta_steps_used": round(delta_steps, 6),
                "marginal_cost_per_1pct_escape": marginal_cost,
                "interpretation": _to_marginal_interp(delta_escape, marginal_cost_num),
            }
        )
    return rows


def build_escape_summary_table_rows(summary_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    prev_pct: float | None = None
    for r in sorted(summary_rows, key=lambda x: int(x["max_steps"])):
        curr_pct = float(r["success_rate"]) * 100.0
        delta_pct = None if prev_pct is None else (curr_pct - prev_pct)
        rows.append(
            {
                "MAX_STEPS": int(r["max_steps"]),
                "episodes": int(r["total_episodes"]),
                "escape_from_c_rate_pct": round(curr_pct, 1),
                "avg_final_mastery": round(float(r["avg_final_mastery"]), 3),
                "avg_steps_used": round(float(r["avg_steps_used"]), 1),
                "delta_vs_previous_pct": _format_delta(delta_pct),
                "interpretation": _to_multiseed_interp(curr_pct, delta_pct, 0.0),
            }
        )
        prev_pct = curr_pct
    return rows


def build_subskill_summary(all_episodes: dict[int, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for max_steps in MAX_STEPS_LIST:
        episodes = all_episodes.get(max_steps, [])
        if not episodes:
            continue
        for subskill in simulate_student.POLYNOMIAL_SUBSKILLS:
            init_vals = [float(e["initial_subskills"][subskill]) for e in episodes]
            final_vals = [float(e["final_subskills"][subskill]) for e in episodes]
            avg_initial = _mean(init_vals)
            avg_final = _mean(final_vals)
            rows.append(
                {
                    "max_steps": int(max_steps),
                    "subskill": subskill,
                    "avg_initial_mastery": round(avg_initial, 4),
                    "avg_final_mastery": round(avg_final, 4),
                    "avg_gain": round(avg_final - avg_initial, 4),
                }
            )
    return rows


def build_breakpoint_summary(all_episodes: dict[int, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for max_steps in MAX_STEPS_LIST:
        episodes = all_episodes.get(max_steps, [])
        failed = [e for e in episodes if float(e["final_mastery"]) < float(EXP3_SUCCESS_THRESHOLD)]
        weakest: list[str] = []
        for e in failed:
            final_map = e["final_subskills"]
            weakest.append(min(simulate_student.POLYNOMIAL_SUBSKILLS, key=lambda s: float(final_map[s])))
        total_failed = len(failed)
        counts = Counter(weakest)
        for subskill in simulate_student.POLYNOMIAL_SUBSKILLS:
            count = int(counts.get(subskill, 0))
            percentage = (count / total_failed) if total_failed > 0 else 0.0
            rows.append(
                {
                    "max_steps": int(max_steps),
                    "subskill": subskill,
                    "count": count,
                    "percentage": round(percentage, 4),
                }
            )
    return rows


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_summary_md(path: Path, rows: list[dict[str, Any]]) -> None:
    lines = [
        "# Experiment 3 Weak Escape-from-C Summary",
        "",
        "RQ3: How many additional total steps are needed for weak students to escape C (mastery >= 0.60)?",
        "",
        "- Student group: Weak only（減C組）",
        "- Success threshold: final mastery >= 0.60",
        "- Policy A: total-step relaxation only (no forced intervention)",
        "- Multi-seed summary: 10 seeds (42-51)",
        "",
        "| max_steps | total_episodes | success_rate (%) | avg_final_mastery | avg_steps_used | avg_mastery_gain | cost_per_1pct_escape | interpretation |",
        "|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for r in rows:
        cost_text = "" if r["cost_per_1pct_escape"] == "" else f"{float(r['cost_per_1pct_escape']):.3f}"
        lines.append(
            f"| {int(r['max_steps'])} | {int(r['total_episodes'])} | {float(r['success_rate'])*100.0:.1f}% | "
            f"{float(r['avg_final_mastery']):.3f} | {float(r['avg_steps_used']):.2f} | {float(r['avg_mastery_gain']):.3f} | "
            f"{cost_text} | {r['interpretation']} |"
        )
    lines.extend(
        [
            "",
            "## Key Message",
            "",
            "Main interpretation should rely on multi-seed averages rather than single-run fluctuations.",
            "Experiment 3 is a cost-effectiveness study of Adaptive support, not an A-level ranking task.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8-sig")


def write_escape_summary_table_md(path: Path, rows: list[dict[str, Any]]) -> None:
    lines = [
        "# Experiment 3 Summary Table: Escape-from-C Rate under Total-Step Relaxation",
        "",
        "This table summarizes how increasing MAX_STEPS affects the proportion of weak students",
        "who escape from C and reach B-level proficiency (final mastery >= 0.60).",
        "",
        "| MAX_STEPS | episodes | Escape-from-C Rate (%) | Avg Final Mastery | Avg Steps Used | Δ vs Previous | Interpretation |",
        "|---:|---:|---:|---:|---:|---:|---|",
    ]
    for r in rows:
        lines.append(
            f"| {int(r['MAX_STEPS'])} | {int(r['episodes'])} | {float(r['escape_from_c_rate_pct']):.1f}% | "
            f"{float(r['avg_final_mastery']):.3f} | {float(r['avg_steps_used']):.1f} | "
            f"{r['delta_vs_previous_pct']} | {r['interpretation']} |"
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8-sig")


def write_multiseed_summary_md(path: Path, rows: list[dict[str, Any]]) -> None:
    lines = [
        "# Experiment 3 Multi-Seed Summary: Escape-from-C under Total-Step Relaxation",
        "",
        "This table reports the average escape-from-C performance of weak students across multiple random seeds under different total step budgets. Success is defined as final mastery >= 0.60.",
        "",
        "| MAX_STEPS | Seeds | Mean Escape-from-C Rate (%) | Std | Mean Final Mastery | Mean Steps Used | Interpretation |",
        "|---:|---:|---:|---:|---:|---:|---|",
    ]
    for r in rows:
        lines.append(
            f"| {int(r['MAX_STEPS'])} | {int(r['seeds'])} | {float(r['mean_escape_from_c_rate_pct']):.2f}% | "
            f"{float(r['std_escape_from_c_rate_pct']):.2f}% | {float(r['mean_final_mastery']):.4f} | "
            f"{float(r['mean_steps_used']):.2f} | {r['interpretation']} |"
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8-sig")


def write_exp3_readme(path: Path) -> None:
    text = (
        "# Experiment 3: Weak Escape-from-C under Adaptive (Policy A)\n\n"
        "## Research Question\n"
        "Can Adaptive help weak students escape from C to B (mastery >= 0.60)?\n\n"
        "## Method\n"
        "- Weak only\n"
        "- AB3 only\n"
        "- Total-step relaxation only (no forced intervention)\n"
        "- MAX_STEPS sweep: 30, 40, 50, 60, 70\n\n"
        "## Multi-seed Evaluation\n"
        "Experiment 3 is now summarized with multiple random seeds to reduce single-run noise.\n"
        "Main conclusion should be based on multi-seed averages, not a single run.\n"
        f"- Seed list: {SEED_LIST}\n\n"
        "## Main Outputs\n"
        "- exp3_multiseed_summary.csv\n"
        "- exp3_multiseed_summary.md\n"
        "- fig_exp3_escape_rate_multiseed.png\n"
        "- fig_exp3_mastery_multiseed.png\n"
        "- fig_exp3_cost_vs_benefit_multiseed.png\n"
        "- fig_exp3_marginal_cost.png\n\n"
        "## Marginal Cost Analysis\n"
        "- exp3_marginal_cost_summary.csv\n"
        "- exp3_marginal_cost_summary.md\n"
        "- fig_exp3_marginal_cost.png\n\n"
        "This analysis estimates how many additional steps are needed to gain each additional 1% of "
        "escape-from-C rate, making Experiment 3 directly interpretable as a cost-effectiveness study.\n\n"
        "## Single-run Compatibility Artifacts\n"
        "Single-run results are retained for traceability, but the main interpretation should rely on multi-seed summaries.\n"
        "- weak_escape_total_step_summary.csv (compatibility schema)\n"
        "- weak_escape_total_step_summary.md\n"
        "- exp3_escape_from_c_summary_table.csv\n"
        "- exp3_escape_from_c_summary_table.md\n"
    )
    path.write_text(text, encoding="utf-8-sig")


def write_marginal_cost_md(path: Path, rows: list[dict[str, Any]]) -> None:
    lines = [
        "# Experiment 3 Marginal Cost Summary",
        "",
        "This table reports the incremental cost of improving escape-from-C performance under larger total-step budgets.",
        "",
        "| from_max_steps | to_max_steps | from_mean_escape_rate_pct | to_mean_escape_rate_pct | delta_escape_rate_pct | from_mean_steps_used | to_mean_steps_used | delta_steps_used | marginal_cost_per_1pct_escape | interpretation |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for r in rows:
        mc = r["marginal_cost_per_1pct_escape"]
        mc_txt = "NA" if isinstance(mc, str) else f"{float(mc):.3f}"
        lines.append(
            f"| {int(r['from_max_steps'])} | {int(r['to_max_steps'])} | {float(r['from_mean_escape_rate_pct']):.2f} | "
            f"{float(r['to_mean_escape_rate_pct']):.2f} | {float(r['delta_escape_rate_pct']):+.2f} | "
            f"{float(r['from_mean_steps_used']):.2f} | {float(r['to_mean_steps_used']):.2f} | "
            f"{float(r['delta_steps_used']):.2f} | {mc_txt} | {r['interpretation']} |"
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8-sig")


def main() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    exp3_dirs = create_timestamped_run_dir(EXP3_DIR)
    run_dir = exp3_dirs["run_dir"]
    latest_dir = exp3_dirs["latest_dir"]
    final_dir = exp3_dirs["final_dir"]
    prev_exp3_env = os.environ.get(EXP3_OUTPUT_DIR_ENV)
    os.environ[EXP3_OUTPUT_DIR_ENV] = str(run_dir)
    _validate_exp3_output_path(run_dir)
    _validate_exp3_output_path(latest_dir)

    print(f"[RUN] Writing outputs to {run_dir}")
    print(f"[PROTECT] Skipping final/ directory: {final_dir}")
    if abs(float(EXP3_SUCCESS_THRESHOLD) - 0.60) > 1e-9:
        print("[WARNING] Experiment 3 success threshold should be 0.60")
    if len(SEED_LIST) < 3:
        print("[WARNING] Multi-seed analysis should use at least 3 seeds")

    original_extra = simulate_student.WEAK_FOUNDATION_EXTRA_STEPS
    original_threshold = float(simulate_student.RUNTIME_SUCCESS_THRESHOLD)
    original_max_steps = int(simulate_student.MAX_STEPS)

    all_episodes: dict[int, list[dict[str, Any]]] = {ms: [] for ms in MAX_STEPS_LIST}
    raw_seed_rows: list[dict[str, Any]] = []
    try:
        try:
            simulate_student.RUNTIME_SUCCESS_THRESHOLD = float(EXP3_SUCCESS_THRESHOLD)
            simulate_student.WEAK_FOUNDATION_EXTRA_STEPS = 0
            for max_steps in MAX_STEPS_LIST:
                for seed in SEED_LIST:
                    print(f"Running Weak condition: max_steps={max_steps}, seed={seed}")
                    episodes = run_total_step_condition(max_steps, seed)
                    episodes = [e for e in episodes if str(e.get("student_type", "")) == "Weak"]
                    all_episodes[max_steps].extend(episodes)
                    raw_seed_rows.append(build_seed_level_summary_row(max_steps, seed, episodes))
        finally:
            simulate_student.WEAK_FOUNDATION_EXTRA_STEPS = original_extra
            simulate_student.RUNTIME_SUCCESS_THRESHOLD = original_threshold
            simulate_student.MAX_STEPS = original_max_steps

        multiseed_rows = build_multiseed_summary(raw_seed_rows)
        marginal_cost_rows = build_marginal_cost_rows(multiseed_rows)
        compat_summary_rows = build_legacy_summary_from_multiseed(multiseed_rows)
        subskill_rows = build_subskill_summary(all_episodes)
        breakpoint_rows = build_breakpoint_summary(all_episodes)
        escape_table_rows = build_escape_summary_table_rows(compat_summary_rows)

        raw_seed_path = run_dir / "exp3_multiseed_raw_summary.csv"
        multiseed_csv_path = run_dir / "exp3_multiseed_summary.csv"
        multiseed_md_path = run_dir / "exp3_multiseed_summary.md"
        marginal_cost_csv_path = run_dir / "exp3_marginal_cost_summary.csv"
        marginal_cost_md_path = run_dir / "exp3_marginal_cost_summary.md"
        summary_path = run_dir / "weak_escape_total_step_summary.csv"
        summary_md_path = run_dir / "weak_escape_total_step_summary.md"
        escape_table_csv_path = run_dir / "exp3_escape_from_c_summary_table.csv"
        escape_table_md_path = run_dir / "exp3_escape_from_c_summary_table.md"
        subskill_path = run_dir / "weak_foundation_subskill_summary.csv"
        breakpoint_path = run_dir / "weak_foundation_breakpoint_summary.csv"

        write_csv(
            raw_seed_path,
            ["max_steps", "seed", "episodes", "escape_from_c_rate", "avg_final_mastery", "avg_steps_used", "avg_mastery_gain"],
            raw_seed_rows,
        )
        write_csv(
            multiseed_csv_path,
            [
                "MAX_STEPS",
                "seeds",
                "mean_escape_from_c_rate_pct",
                "std_escape_from_c_rate_pct",
                "mean_final_mastery",
                "std_final_mastery",
                "mean_steps_used",
                "std_steps_used",
                "mean_mastery_gain",
                "std_mastery_gain",
                "interpretation",
            ],
            multiseed_rows,
        )
        write_multiseed_summary_md(multiseed_md_path, multiseed_rows)
        write_csv(
            marginal_cost_csv_path,
            [
                "from_max_steps",
                "to_max_steps",
                "from_mean_escape_rate_pct",
                "to_mean_escape_rate_pct",
                "delta_escape_rate_pct",
                "from_mean_steps_used",
                "to_mean_steps_used",
                "delta_steps_used",
                "marginal_cost_per_1pct_escape",
                "interpretation",
            ],
            marginal_cost_rows,
        )
        write_marginal_cost_md(marginal_cost_md_path, marginal_cost_rows)

        # Compatibility artifacts (legacy schema), now based on multi-seed means.
        write_csv(
            summary_path,
            [
                "max_steps",
                "total_episodes",
                "success_rate",
                "avg_final_mastery",
                "avg_steps_used",
                "avg_mastery_gain",
                "cost_per_1pct_escape",
                "interpretation",
            ],
            compat_summary_rows,
        )
        write_summary_md(summary_md_path, compat_summary_rows)
        write_csv(
            escape_table_csv_path,
            [
                "MAX_STEPS",
                "episodes",
                "escape_from_c_rate_pct",
                "avg_final_mastery",
                "avg_steps_used",
                "delta_vs_previous_pct",
                "interpretation",
            ],
            escape_table_rows,
        )
        write_escape_summary_table_md(escape_table_md_path, escape_table_rows)

        write_csv(
            subskill_path,
            ["max_steps", "subskill", "avg_initial_mastery", "avg_final_mastery", "avg_gain"],
            subskill_rows,
        )
        write_csv(
            breakpoint_path,
            ["max_steps", "subskill", "count", "percentage"],
            breakpoint_rows,
        )

        write_exp3_readme(run_dir / "README.md")
        write_exp3_readme(EXP3_DIR / "README.md")

        setup_report_style()
        plot_weak_foundation_support_results(str(run_dir))
        plot_exp3_multiseed_results(str(run_dir))
        plot_exp3_marginal_cost(str(run_dir))

        print(f"[LATEST] Updating {latest_dir}")
        sync_run_to_latest(run_dir, latest_dir)
        print(f"[LATEST] Updated {latest_dir}")
        print(f"[PROTECT] Skipping final/ directory: {final_dir}")
        print("Weak escape-from-C multi-seed experiment completed.")
    finally:
        if prev_exp3_env is None:
            os.environ.pop(EXP3_OUTPUT_DIR_ENV, None)
        else:
            os.environ[EXP3_OUTPUT_DIR_ENV] = prev_exp3_env


if __name__ == "__main__":
    main()
