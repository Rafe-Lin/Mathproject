# -*- coding: utf-8 -*-
# ==============================================================================
# ID: run_weak_foundation_support_strategy_comparison.py
# Version: V1.0.0 (Experiment 3 RQ3 Main Runner)
# Last Updated: 2026-04-15
# Author: *Steve
#
# [Description]:
#   Exp3（RQ3）主流程：Weak 組於多組 MAX_STEPS 與多 seed 下比較三策略，
#   含 reflect-scale 設定，產生主表、摘要與 RQ3 圖表。
#
# [Database Schema Usage]:
#   無直接資料庫操作。
#
# [Logic Flow]:
#   1. 建立時間戳 run 目錄。
#   2. 呼叫 simulate_student 與繪圖函式。
#   3. 寫入 reports/adaptive_strategy_study/experiment_3_weak_foundation_support。
# ==============================================================================

from __future__ import annotations

import csv
import random
import statistics
import sys
from pathlib import Path
from typing import Any

_STUDY_ROOT = Path(__file__).resolve().parents[1]
if str(_STUDY_ROOT) not in sys.path:
    sys.path.insert(0, str(_STUDY_ROOT))
import study_paths as _study_paths  # noqa: E402

_study_paths.ensure_repo_root_on_syspath()
_study_paths.ensure_exp2_mechanism_on_syspath()
_study_paths.ensure_common_on_syspath()

import matplotlib.pyplot as plt  # noqa: E402

import simulate_student  # noqa: E402
from plot_experiment_results import (  # noqa: E402
    create_timestamped_run_dir,
    plot_exp3_rq3_results,
    setup_report_style,
)

REPORTS_DIR = _study_paths.study_reports_root()
EXP3_DIR = REPORTS_DIR / "experiment_3_weak_foundation_support"

FIXED_BUDGETS = [30, 40, 50, 60, 70, 80, 90, 100]
SEED_LIST = [42, 43, 44, 45, 46, 47, 48, 49, 50, 51]
EXP3_SUCCESS_THRESHOLD = 0.60
STRATEGY_ORDER = [
    ("AB1_Baseline", "Baseline"),
    ("AB2_RuleBased", "Rule-Based"),
    ("AB3_PPO_Dynamic", "Adaptive (Ours)"),
]


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _std(values: list[float]) -> float:
    if len(values) <= 1:
        return 0.0
    return float(statistics.pstdev(values))


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _to_md_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "|" + "|".join(["---"] * len(headers)) + "|",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def run_condition(max_steps: int, strategy_id: str, seed: int) -> list[dict[str, Any]]:
    random.seed(int(seed))
    simulate_student.MAX_STEPS = int(max_steps)
    simulate_student.WEAK_FOUNDATION_EXTRA_STEPS = 0
    episodes: list[dict[str, Any]] = []
    for episode_id in range(1, int(simulate_student.N_PER_TYPE) + 1):
        ep, _ = simulate_student.simulate_episode(
            student_type="Weak",
            strategy_name=strategy_id,
            episode_id=episode_id,
        )
        episodes.append(ep)
    return [e for e in episodes if str(e.get("student_type", "")) == "Weak"]


def summarize_seed(max_steps: int, strategy: str, seed: int, episodes: list[dict[str, Any]]) -> dict[str, Any]:
    escape_rate_pct = _mean(
        [1.0 if float(e["final_mastery"]) >= EXP3_SUCCESS_THRESHOLD else 0.0 for e in episodes]
    ) * 100.0
    final_mastery = _mean([float(e["final_mastery"]) for e in episodes])
    avg_steps = _mean([float(e.get("total_steps", 0.0)) for e in episodes])
    return {
        "MAX_STEPS": int(max_steps),
        "Strategy": strategy,
        "seed": int(seed),
        "Escape-from-C Rate (%)": float(escape_rate_pct),
        "Mean Final Mastery": float(final_mastery),
        "Avg Steps": float(avg_steps),
    }


def aggregate_rows(seed_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for budget in FIXED_BUDGETS:
        for _, strategy_label in STRATEGY_ORDER:
            subset = [
                r
                for r in seed_rows
                if int(r["MAX_STEPS"]) == int(budget) and str(r["Strategy"]) == strategy_label
            ]
            if not subset:
                continue
            out.append(
                {
                    "MAX_STEPS": int(budget),
                    "Strategy": strategy_label,
                    "Escape-from-C Rate (%)": round(_mean([float(r["Escape-from-C Rate (%)"]) for r in subset]), 4),
                    "Escape-from-C Std (%)": round(_std([float(r["Escape-from-C Rate (%)"]) for r in subset]), 4),
                    "Mean Final Mastery": round(_mean([float(r["Mean Final Mastery"]) for r in subset]), 6),
                    "Avg Steps": round(_mean([float(r["Avg Steps"]) for r in subset]), 4),
                }
            )
    return out


def run_reflect_setting(weak_reflect: float) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    seed_rows: list[dict[str, Any]] = []
    orig_map = dict(simulate_student.REFLECT_SCALE_BY_STUDENT_TYPE)
    orig_extra = int(simulate_student.WEAK_FOUNDATION_EXTRA_STEPS)
    orig_thr = float(simulate_student.RUNTIME_SUCCESS_THRESHOLD)
    orig_steps = int(simulate_student.MAX_STEPS)
    try:
        simulate_student.RUNTIME_SUCCESS_THRESHOLD = float(EXP3_SUCCESS_THRESHOLD)
        simulate_student.WEAK_FOUNDATION_EXTRA_STEPS = 0
        simulate_student.REFLECT_SCALE_BY_STUDENT_TYPE["Weak"] = float(weak_reflect)
        for budget in FIXED_BUDGETS:
            for strategy_id, strategy_label in STRATEGY_ORDER:
                for seed in SEED_LIST:
                    episodes = run_condition(budget, strategy_id, seed)
                    seed_rows.append(summarize_seed(budget, strategy_label, seed, episodes))
    finally:
        simulate_student.REFLECT_SCALE_BY_STUDENT_TYPE.clear()
        simulate_student.REFLECT_SCALE_BY_STUDENT_TYPE.update(orig_map)
        simulate_student.WEAK_FOUNDATION_EXTRA_STEPS = orig_extra
        simulate_student.RUNTIME_SUCCESS_THRESHOLD = orig_thr
        simulate_student.MAX_STEPS = orig_steps
    return seed_rows, aggregate_rows(seed_rows)


def build_best_method_rows(summary_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not summary_rows:
        return []
    best_escape = max(summary_rows, key=lambda r: float(r["Escape-from-C Rate (%)"]))
    return [
        {
            "Metric": "Escape-from-C Rate (%)",
            "Best Strategy": str(best_escape["Strategy"]),
            "Best MAX_STEPS": int(best_escape["MAX_STEPS"]),
            "Value": round(float(best_escape["Escape-from-C Rate (%)"]), 4),
        }
    ]


def write_summary_md(path: Path, rows: list[dict[str, Any]]) -> None:
    headers = ["MAX_STEPS", "Strategy", "Escape-from-C Rate (%)", "Mean Final Mastery"]
    table_rows = [
        [
            str(int(r["MAX_STEPS"])),
            str(r["Strategy"]),
            f"{float(r['Escape-from-C Rate (%)']):.2f}",
            f"{float(r['Mean Final Mastery']):.4f}",
        ]
        for r in sorted(rows, key=lambda x: (int(x["MAX_STEPS"]), str(x["Strategy"])))
    ]
    path.write_text("# Experiment 3 RQ3 Summary Table\n\n" + _to_md_table(headers, table_rows) + "\n", encoding="utf-8-sig")


def write_best_method_md(path: Path, rows: list[dict[str, Any]]) -> None:
    headers = ["Metric", "Best Strategy", "Best MAX_STEPS", "Value"]
    table_rows = [
        [str(r["Metric"]), str(r["Best Strategy"]), str(int(r["Best MAX_STEPS"])), f"{float(r['Value']):.4f}"]
        for r in rows
    ]
    path.write_text(
        "# Experiment 3 RQ3 Best Method Summary\n\n" + _to_md_table(headers, table_rows) + "\n",
        encoding="utf-8-sig",
    )


def _winner_counts(summary_rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for budget in FIXED_BUDGETS:
        bucket = [r for r in summary_rows if int(r["MAX_STEPS"]) == int(budget)]
        if not bucket:
            continue
        winner = max(bucket, key=lambda x: float(x["Escape-from-C Rate (%)"]))
        name = str(winner["Strategy"])
        counts[name] = counts.get(name, 0) + 1
    return counts


def write_rq3_captions(out_dir: Path, summary_rows: list[dict[str, Any]]) -> None:
    counts = _winner_counts(summary_rows)
    total = len(FIXED_BUDGETS)
    if counts:
        top = max(counts.keys(), key=lambda k: counts[k])
        top_n = int(counts[top])
        if top_n == total:
            verdict = f"{top} is best at all budgets ({top_n}/{total})."
        else:
            verdict = f"{top} is best at most budgets ({top_n}/{total})."
        detail = ", ".join([f"{k}: {v}/{total}" for k, v in sorted(counts.items())])
    else:
        verdict = "No winner can be inferred from the current rows."
        detail = "No budget-level winner counts available."
    (out_dir / "figure_caption_exp3_rq3_success.md").write_text(
        (
            "### Figure Caption: RQ3 Success Rate (Weak Students)\n\n"
            "This figure compares Baseline, Rule-Based, and Adaptive (Ours) on Weak students.\n"
            "The x-axis is MAX_STEPS (30-100), and the y-axis is Success Rate 達標B (%).\n"
            "Success is defined as final mastery >= 0.60 (B threshold).\n"
            "This run uses the corrected reflect-scale setting: Careless=0.15, Average=0.10, Weak=0.05.\n"
            f"{verdict}\n"
            f"Budget-level winner counts: {detail}.\n"
        ),
        encoding="utf-8-sig",
    )
    (out_dir / "table_caption_exp3_rq3_summary.md").write_text(
        (
            "### Table Caption: RQ3 Core Evidence Summary\n\n"
            "This table summarizes the core RQ3 evidence.\n"
            "It compares strategy-level escape-from-C rate and mean final mastery at each MAX_STEPS.\n"
            "It is used to identify which strategy best helps Weak students cross the B threshold.\n"
        ),
        encoding="utf-8-sig",
    )


def write_reflect_robustness(out_dir: Path, summary_010: list[dict[str, Any]], summary_005: list[dict[str, Any]]) -> None:
    budgets = FIXED_BUDGETS
    def pick(summary: list[dict[str, Any]], budget: int, col: str) -> float:
        hit = [r for r in summary if int(r["MAX_STEPS"]) == int(budget) and str(r["Strategy"]) == "Adaptive (Ours)"]
        if not hit:
            return float("nan")
        return float(hit[0][col])

    y_010 = [pick(summary_010, b, "Escape-from-C Rate (%)") for b in budgets]
    e_010 = [pick(summary_010, b, "Escape-from-C Std (%)") for b in budgets]
    y_005 = [pick(summary_005, b, "Escape-from-C Rate (%)") for b in budgets]
    e_005 = [pick(summary_005, b, "Escape-from-C Std (%)") for b in budgets]

    fig, ax = plt.subplots(figsize=(8, 5))
    color = "#2ca02c"
    ax.errorbar(
        budgets, y_010, yerr=e_010, linestyle="--", marker="o", linewidth=2.0, markersize=6, capsize=3,
        color=color, label="Adaptive (Weak=0.10)"
    )
    ax.errorbar(
        budgets, y_005, yerr=e_005, linestyle="-", marker="o", linewidth=2.0, markersize=6, capsize=3,
        color=color, label="Adaptive (Weak=0.05)"
    )
    ax.set_title("Reflect Scale Robustness (Weak Students)")
    ax.set_xlabel("MAX_STEPS")
    ax.set_ylabel("Success Rate 達標B (%)")
    ax.set_xticks(budgets)
    ax.set_ylim(0, 100)
    ax.tick_params(axis="both", labelsize=12)
    ax.legend(loc="upper left", fontsize=12)
    ax.grid(alpha=0.18, linewidth=0.8)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    fig.savefig(str(out_dir / "fig_reflect_scale_robustness.png"), dpi=300, bbox_inches="tight")
    plt.close(fig)

    old_counts = _winner_counts(summary_010)
    new_counts = _winner_counts(summary_005)
    old_top = max(old_counts.keys(), key=lambda k: old_counts[k]) if old_counts else "N/A"
    new_top = max(new_counts.keys(), key=lambda k: new_counts[k]) if new_counts else "N/A"
    ranking_changed = old_top != new_top
    verdict = (
        "The ranking pattern changes between reflect-scale settings."
        if ranking_changed
        else "The ranking pattern is stable across reflect-scale settings."
    )
    (out_dir / "figure_caption_reflect_scale_robustness.md").write_text(
        (
            "### Figure Caption: Reflect Scale Robustness (Weak Students)\n\n"
            "This figure compares Weak reflect_scale = 0.10 versus 0.05.\n"
            "The 0.10 condition represents a relatively permissive transfer assumption, while 0.05 is a conservative weak-transfer setting.\n"
            "Both curves report Adaptive success rate (final mastery >= 0.60) over MAX_STEPS 30-100 with multi-seed error bars.\n"
            f"Under reflect_scale=0.10, winner-count pattern is {old_counts}; under reflect_scale=0.05, it is {new_counts}.\n"
            f"Conclusion: {verdict}\n"
        ),
        encoding="utf-8-sig",
    )


def main() -> None:
    setup_report_style()
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    exp3_dirs = create_timestamped_run_dir(EXP3_DIR)
    run_dir = exp3_dirs["run_dir"]
    run_dir.mkdir(parents=True, exist_ok=True)

    # Full rerun in one execution: baseline comparison (0.10) and current setting (0.05).
    _, summary_010 = run_reflect_setting(0.10)
    _, summary_005 = run_reflect_setting(0.05)

    # Main RQ3 outputs use current setting (0.05).
    export_rows = [
        {
            "MAX_STEPS": int(r["MAX_STEPS"]),
            "Strategy": str(r["Strategy"]),
            "Escape-from-C Rate (%)": float(r["Escape-from-C Rate (%)"]),
            "Mean Final Mastery": float(r["Mean Final Mastery"]),
        }
        for r in summary_005
    ]
    best_rows = build_best_method_rows(summary_005)
    summary_csv = run_dir / "exp3_rq3_summary_table.csv"
    _write_csv(summary_csv, ["MAX_STEPS", "Strategy", "Escape-from-C Rate (%)", "Mean Final Mastery"], export_rows)
    _write_csv(
        run_dir / "exp3_rq3_best_method_summary.csv",
        ["Metric", "Best Strategy", "Best MAX_STEPS", "Value"],
        best_rows,
    )
    write_summary_md(run_dir / "exp3_rq3_summary_table.md", export_rows)
    write_best_method_md(run_dir / "exp3_rq3_best_method_summary.md", best_rows)
    write_rq3_captions(run_dir, summary_005)

    error_by_point = {
        (int(r["MAX_STEPS"]), str(r["Strategy"])): float(r["Escape-from-C Std (%)"])
        for r in summary_005
    }
    plot_exp3_rq3_results(
        summary_csv_path=summary_csv,
        output_dir=run_dir,
        error_by_point=error_by_point,
    )

    # Robustness figure export is intentionally disabled in final minimal Exp3 output set.

    print(f"[RUN] outputs saved to: {run_dir}")
    if best_rows:
        row = best_rows[0]
        print(
            f"[SUMMARY] {row['Metric']}: {row['Best Strategy']} @ MAX_STEPS={int(row['Best MAX_STEPS'])} "
            f"({float(row['Value']):.4f})"
        )


if __name__ == "__main__":
    main()
