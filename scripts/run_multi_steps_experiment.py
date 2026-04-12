"""
Experiment 1 official runner (single fixed setting, timestamped run output).
"""

from __future__ import annotations

import csv
import os
import random
from datetime import datetime
from pathlib import Path
from typing import Any

import simulate_student
from core.experiment_config import (
    EXP1_SUCCESS_THRESHOLD as CONFIG_EXP1_SUCCESS_THRESHOLD,
    display_student_group,
    validate_group_config,
)
from plot_experiment_results import (
    plot_exp1_mastery_gain_comparison,
    plot_exp1_overall_efficiency,
    plot_exp1_overall_success_rate,
    plot_exp1_student_type_comparison,
    setup_report_style,
)

REPORTS_DIR = Path("reports")
EXP1_BASE_DIR = REPORTS_DIR / "experiment_1_ablation"
RUNS_DIR = EXP1_BASE_DIR / "runs"

N_PER_GROUP = 300
MAX_STEPS = 30
SUCCESS_THRESHOLD = 0.80

STRATEGY_DISPLAY_MAP = {
    "AB1_Baseline": "Baseline",
    "AB2_RuleBased": "Rule-Based",
    "AB3_PPO_Dynamic": "Adaptive (Ours)",
}
STUDENT_ORDER = ["Careless", "Average", "Weak"]
STUDENT_DISPLAY_MAP = {
    "Careless": display_student_group("careless"),
    "Average": display_student_group("average"),
    "Weak": display_student_group("weak"),
}
STRATEGY_ORDER = ["AB1_Baseline", "AB2_RuleBased", "AB3_PPO_Dynamic"]
SUCCESS_DISPLAY_LABEL = "Success(達標A) Rate%"
SUCCESS_THRESHOLD_DISPLAY = "0.80"


def _as_pct(x: float) -> float:
    return round(float(x) * 100.0, 2)


def _new_run_dir() -> Path:
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    run_dir = RUNS_DIR / datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def validate_experiment1_labels() -> None:
    validate_group_config()
    blocked = [
        "A~B++",
        "B~B+",
        "Weak Foundation",
        "達標率（精熟度 ≥ 0.80, %）",
        "Success Rate (Mastery ≥ 0.80, %)",
    ]
    values = list(STUDENT_DISPLAY_MAP.values()) + [SUCCESS_DISPLAY_LABEL]
    bad_hits = [w for w in blocked if any(w in str(v) for v in values)]
    if bad_hits:
        print(f"[WARN] Experiment 1 label check found legacy terms: {bad_hits}")
    assert SUCCESS_THRESHOLD_DISPLAY == "0.80"
    assert abs(CONFIG_EXP1_SUCCESS_THRESHOLD - 0.80) < 1e-9
    assert SUCCESS_DISPLAY_LABEL == "Success(達標A) Rate%"


def _build_overall_summary(episodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for strategy in STRATEGY_ORDER:
        subset = [e for e in episodes if str(e["strategy"]) == strategy]
        if not subset:
            continue
        success_rate = sum(int(e["success"]) for e in subset) / len(subset)
        avg_steps = sum(float(e["total_steps"]) for e in subset) / len(subset)
        avg_mastery_gain = sum(float(e["mastery_gain"]) for e in subset) / len(subset)
        avg_unnecessary = sum(float(e["unnecessary_remediations"]) for e in subset) / len(subset)
        rows.append(
            {
                "Strategy": STRATEGY_DISPLAY_MAP.get(strategy, strategy),
                SUCCESS_DISPLAY_LABEL: _as_pct(success_rate),
                "Avg Steps": round(avg_steps, 2),
                "Avg Mastery Gain": round(avg_mastery_gain, 4),
                "Avg Unnecessary Remediations": round(avg_unnecessary, 2),
            }
        )
    return rows


def _build_group_summary(episodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for student_group in STUDENT_ORDER:
        for strategy in STRATEGY_ORDER:
            subset = [
                e
                for e in episodes
                if str(e["student_type"]) == student_group and str(e["strategy"]) == strategy
            ]
            if not subset:
                continue
            success_rate = sum(int(e["success"]) for e in subset) / len(subset)
            avg_steps = sum(float(e["total_steps"]) for e in subset) / len(subset)
            avg_mastery_gain = sum(float(e["mastery_gain"]) for e in subset) / len(subset)
            avg_unnecessary = sum(float(e["unnecessary_remediations"]) for e in subset) / len(subset)
            rows.append(
                {
                    "Student Level": STUDENT_DISPLAY_MAP.get(student_group, student_group),
                    "Strategy": STRATEGY_DISPLAY_MAP.get(strategy, strategy),
                    SUCCESS_DISPLAY_LABEL: _as_pct(success_rate),
                    "Avg Steps": round(avg_steps, 2),
                    "Avg Mastery Gain": round(avg_mastery_gain, 4),
                    "Avg Unnecessary Remediations": round(avg_unnecessary, 2),
                }
            )
    return rows


def _build_markdown_table(rows: list[dict[str, Any]], conclusion: str) -> str:
    lines = [
        "# Experiment 1 Summary Table",
        "",
        f"本實驗成功指標為：{SUCCESS_DISPLAY_LABEL}",
        "學生分為三類：",
        f"- {display_student_group('careless')}：起始精熟度約 0.68–0.80，基礎能力較高但表現不穩定",
        f"- {display_student_group('average')}：起始精熟度約 0.50–0.68，屬一般中段學生",
        f"- {display_student_group('weak')}：起始精熟度約 0.20–0.50，基礎較弱，需要補救",
        "",
        f"| Strategy | Student Level | {SUCCESS_DISPLAY_LABEL} | Avg Steps | Avg Mastery Gain | Avg Unnecessary Remediations |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for strategy in ["Baseline", "Rule-Based", "Adaptive (Ours)"]:
        for student_group in STUDENT_ORDER:
            target_group = STUDENT_DISPLAY_MAP.get(student_group, student_group)
            row = next(
                (
                    r
                    for r in rows
                    if r["Strategy"] == strategy and r["Student Level"] == target_group
                ),
                None,
            )
            if row is None:
                continue
            lines.append(
                f"| {row['Strategy']} | {row['Student Level']} | {row[SUCCESS_DISPLAY_LABEL]:.2f} | "
                f"{row['Avg Steps']:.2f} | {row['Avg Mastery Gain']:.4f} | {row['Avg Unnecessary Remediations']:.2f} |"
            )
    lines.extend(["", f"結論：{conclusion}", ""])
    return "\n".join(lines)


def _make_overall_conclusion(overall_rows: list[dict[str, Any]]) -> str:
    by_name = {str(r["Strategy"]): r for r in overall_rows}
    adaptive = by_name.get("Adaptive (Ours)")
    baseline = by_name.get("Baseline")
    rule = by_name.get("Rule-Based")
    if not adaptive or not baseline or not rule:
        return "Unable to recover from current outputs"

    success_best = adaptive[SUCCESS_DISPLAY_LABEL] >= max(
        baseline[SUCCESS_DISPLAY_LABEL], rule[SUCCESS_DISPLAY_LABEL]
    )
    steps_best = adaptive["Avg Steps"] <= min(baseline["Avg Steps"], rule["Avg Steps"])
    unnecessary_best = adaptive["Avg Unnecessary Remediations"] <= min(
        baseline["Avg Unnecessary Remediations"], rule["Avg Unnecessary Remediations"]
    )
    if success_best and (steps_best or unnecessary_best):
        return "在 Success(達標A) Rate% 指標下，Adaptive (Ours) 於達標率領先，且在效率或補救精準度至少一項更優。"
    if success_best:
        return "在 Success(達標A) Rate% 指標下，Adaptive (Ours) 的達標率高於 Baseline 與 Rule-Based。"
    return "Adaptive (Ours) 未在整體達標率上領先，需檢查設定與隨機性。"


def _write_readme(path: Path) -> None:
    content = (
        "# Experiment 1 (Formal)\n\n"
        "## Purpose\n"
        "Compare Baseline, Rule-Based, and Adaptive (Ours) under one fixed setting to answer: "
        "why choose Adaptive as the core system.\n\n"
        "## Student Levels\n"
        f"- {display_student_group('careless')}：起始精熟度約 0.68–0.80，基礎能力較高但表現不穩定\n"
        f"- {display_student_group('average')}：起始精熟度約 0.50–0.68，屬一般中段學生\n"
        f"- {display_student_group('weak')}：起始精熟度約 0.20–0.50，基礎較弱，需要補救\n\n"
        "## Fixed Settings\n"
        f"- 成功定義：{SUCCESS_DISPLAY_LABEL}\n"
        f"- MAX_STEPS = {MAX_STEPS}\n"
        f"- N_PER_GROUP = {N_PER_GROUP}\n"
        f"- TOTAL = {N_PER_GROUP * len(STUDENT_ORDER)}\n\n"
        "## Output Files\n"
        "- experiment1_summary_table.csv: strategy x student-level formal table\n"
        "- experiment1_summary_table.md: markdown table + one-line conclusion\n"
        "- experiment1_overall_summary.csv: strategy-level summary\n"
        "- experiment1_group_summary.csv: student-level summary\n"
        "- fig_exp1_overall_success_rate.png: overall success-rate comparison\n"
        "- fig_exp1_overall_efficiency.png: overall avg-steps comparison\n"
        "- fig_exp1_student_type_comparison.png: success-rate grouped comparison\n"
        "- fig_exp1_mastery_gain_comparison.png: mastery-gain grouped comparison\n"
    )
    path.write_text(content, encoding="utf-8-sig")


def main() -> None:
    validate_experiment1_labels()
    run_dir = _new_run_dir()
    setup_report_style()

    original_max_steps = int(simulate_student.MAX_STEPS)
    original_n_per_type = int(simulate_student.N_PER_TYPE)
    original_threshold = float(simulate_student.RUNTIME_SUCCESS_THRESHOLD)
    prev_mode_env = os.environ.get(simulate_student.OUTPUT_MODE_ENV)

    try:
        os.environ[simulate_student.OUTPUT_MODE_ENV] = "experiment1"
        simulate_student.MAX_STEPS = int(MAX_STEPS)
        simulate_student.N_PER_TYPE = int(N_PER_GROUP)
        simulate_student.RUNTIME_SUCCESS_THRESHOLD = float(SUCCESS_THRESHOLD)
        random.seed(simulate_student.RANDOM_SEED)

        episodes, _ = simulate_student.run_batch_experiments()

        overall_rows = _build_overall_summary(episodes)
        group_rows = _build_group_summary(episodes)

        summary_table_rows = [
            {
                "Strategy": r["Strategy"],
                "Student Level": r["Student Level"],
                SUCCESS_DISPLAY_LABEL: r[SUCCESS_DISPLAY_LABEL],
                "Avg Steps": r["Avg Steps"],
                "Avg Mastery Gain": r["Avg Mastery Gain"],
                "Avg Unnecessary Remediations": r["Avg Unnecessary Remediations"],
            }
            for r in group_rows
        ]

        _write_csv(
            run_dir / "experiment1_overall_summary.csv",
            [
                "Strategy",
                SUCCESS_DISPLAY_LABEL,
                "Avg Steps",
                "Avg Mastery Gain",
                "Avg Unnecessary Remediations",
            ],
            overall_rows,
        )
        _write_csv(
            run_dir / "experiment1_group_summary.csv",
            [
                "Student Level",
                "Strategy",
                SUCCESS_DISPLAY_LABEL,
                "Avg Steps",
                "Avg Mastery Gain",
                "Avg Unnecessary Remediations",
            ],
            group_rows,
        )
        _write_csv(
            run_dir / "experiment1_summary_table.csv",
            [
                "Strategy",
                "Student Level",
                SUCCESS_DISPLAY_LABEL,
                "Avg Steps",
                "Avg Mastery Gain",
                "Avg Unnecessary Remediations",
            ],
            summary_table_rows,
        )

        conclusion = _make_overall_conclusion(overall_rows)
        md_text = _build_markdown_table(summary_table_rows, conclusion)
        (run_dir / "experiment1_summary_table.md").write_text(md_text, encoding="utf-8-sig")
        _write_readme(run_dir / "README.md")

        plot_exp1_overall_success_rate(
            run_dir / "experiment1_overall_summary.csv",
            run_dir / "fig_exp1_overall_success_rate.png",
        )
        plot_exp1_overall_efficiency(
            run_dir / "experiment1_overall_summary.csv",
            run_dir / "fig_exp1_overall_efficiency.png",
        )
        plot_exp1_student_type_comparison(
            run_dir / "experiment1_group_summary.csv",
            run_dir / "fig_exp1_student_type_comparison.png",
        )
        plot_exp1_mastery_gain_comparison(
            run_dir / "experiment1_group_summary.csv",
            run_dir / "fig_exp1_mastery_gain_comparison.png",
        )

        print("Experiment 1 completed.")
        print(f"Run directory: {run_dir}")
    finally:
        simulate_student.MAX_STEPS = original_max_steps
        simulate_student.N_PER_TYPE = original_n_per_type
        simulate_student.RUNTIME_SUCCESS_THRESHOLD = original_threshold
        if prev_mode_env is None:
            os.environ.pop(simulate_student.OUTPUT_MODE_ENV, None)
        else:
            os.environ[simulate_student.OUTPUT_MODE_ENV] = prev_mode_env


if __name__ == "__main__":
    main()
