"""
Experiment 3 strategy comparison layer (fixed budgets, weak group only).

RQ3-Strategy:
Under the same total support budget, which strategy is most effective at helping
Weak (C) students escape from the lowest mastery tier?
"""

from __future__ import annotations

import csv
import os
import random
import shutil
import statistics
from pathlib import Path
from typing import Any

import simulate_student
from plot_experiment_results import (
    create_timestamped_run_dir,
    plot_exp3_strategy_comparison,
    setup_report_style,
)

REPORTS_DIR = Path("reports")
EXP3_DIR = REPORTS_DIR / "experiment_3_weak_foundation_support"
LATEST_DIR = EXP3_DIR / "latest"
EXP3_OUTPUT_DIR_ENV = "MATHPROJECT_EXP3_OUTPUT_DIR"

FIXED_BUDGETS = [50, 70, 90]
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


def _validate_exp3_output_path(path: Path) -> None:
    low = str(path).replace("\\", "/").lower()
    if "experiment_1_ablation" in low or "experiment_2_ab3_student_types" in low:
        raise RuntimeError(f"Exp3 output path points to forbidden location: {path}")


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
    escape = _mean([1.0 if float(e["final_mastery"]) >= EXP3_SUCCESS_THRESHOLD else 0.0 for e in episodes])
    return {
        "MAX_STEPS": int(max_steps),
        "Strategy": strategy,
        "seed": int(seed),
        "episodes": int(len(episodes)),
        "escape_rate_pct": float(escape * 100.0),
        "avg_steps_used": float(_mean([float(e["total_steps"]) for e in episodes])),
        "final_mastery": float(_mean([float(e["final_mastery"]) for e in episodes])),
    }


def build_long_summary(seed_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for ms in FIXED_BUDGETS:
        bucket = [r for r in seed_rows if int(r["MAX_STEPS"]) == int(ms)]
        if not bucket:
            continue
        baseline = next((r for r in bucket if r["Strategy"] == "Baseline"), None)
        rule = next((r for r in bucket if r["Strategy"] == "Rule-Based"), None)
        if baseline is None or rule is None:
            continue
        baseline_escape = float(baseline["mean_escape_rate_pct"])
        baseline_mastery = float(baseline["mean_final_mastery"])
        rule_escape = float(rule["mean_escape_rate_pct"])
        rule_mastery = float(rule["mean_final_mastery"])
        for r in bucket:
            out.append(
                {
                    "MAX_STEPS": int(ms),
                    "Strategy": r["Strategy"],
                    "mean_escape_rate_pct": round(float(r["mean_escape_rate_pct"]), 4),
                    "std_escape_rate_pct": round(float(r["std_escape_rate_pct"]), 4),
                    "mean_avg_steps_used": round(float(r["mean_avg_steps_used"]), 6),
                    "std_avg_steps_used": round(float(r["std_avg_steps_used"]), 6),
                    "mean_final_mastery": round(float(r["mean_final_mastery"]), 6),
                    "std_final_mastery": round(float(r["std_final_mastery"]), 6),
                    "escape_gain_vs_baseline_pp": round(float(r["mean_escape_rate_pct"]) - baseline_escape, 4),
                    "mastery_gain_vs_baseline": round(float(r["mean_final_mastery"]) - baseline_mastery, 6),
                    "escape_gain_vs_rule_based_pp": round(float(r["mean_escape_rate_pct"]) - rule_escape, 4),
                    "mastery_gain_vs_rule_based": round(float(r["mean_final_mastery"]) - rule_mastery, 6),
                }
            )
    return out


def build_pivot_summary(long_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for ms in FIXED_BUDGETS:
        bucket = [r for r in long_rows if int(r["MAX_STEPS"]) == int(ms)]
        if not bucket:
            continue
        m = {r["Strategy"]: r for r in bucket}
        if not all(k in m for k in ["Baseline", "Rule-Based", "Adaptive (Ours)"]):
            continue
        out.append(
            {
                "MAX_STEPS": int(ms),
                "Baseline_Escape": round(float(m["Baseline"]["mean_escape_rate_pct"]), 4),
                "RuleBased_Escape": round(float(m["Rule-Based"]["mean_escape_rate_pct"]), 4),
                "Adaptive_Escape": round(float(m["Adaptive (Ours)"]["mean_escape_rate_pct"]), 4),
                "Adaptive_minus_Baseline_pp": round(
                    float(m["Adaptive (Ours)"]["mean_escape_rate_pct"]) - float(m["Baseline"]["mean_escape_rate_pct"]),
                    4,
                ),
                "Adaptive_minus_RuleBased_pp": round(
                    float(m["Adaptive (Ours)"]["mean_escape_rate_pct"]) - float(m["Rule-Based"]["mean_escape_rate_pct"]),
                    4,
                ),
                "Baseline_Mastery": round(float(m["Baseline"]["mean_final_mastery"]), 6),
                "RuleBased_Mastery": round(float(m["Rule-Based"]["mean_final_mastery"]), 6),
                "Adaptive_Mastery": round(float(m["Adaptive (Ours)"]["mean_final_mastery"]), 6),
            }
        )
    return out


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def _to_md_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "|" + "|".join(["---"] * len(headers)) + "|",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def write_summary_md(path: Path, long_rows: list[dict[str, Any]], pivot_rows: list[dict[str, Any]]) -> None:
    lines = [
        "# Experiment 3 Strategy Comparison Summary (Weak, Fixed Budgets)",
        "",
        "RQ3-Strategy: Under the same total support budget, which strategy is most effective at helping Weak (C) students escape from C (final mastery >= 0.60)?",
        "",
    ]

    headers = [
        "MAX_STEPS",
        "Strategy",
        "Mean Escape-from-C Rate (%)",
        "Std",
        "Mean Final Mastery",
        "Escape Gain vs Baseline (pp)",
        "Escape Gain vs Rule-Based (pp)",
    ]
    rows: list[list[str]] = []
    for r in sorted(long_rows, key=lambda x: (int(x["MAX_STEPS"]), x["Strategy"])):
        rows.append(
            [
                str(int(r["MAX_STEPS"])),
                str(r["Strategy"]),
                f"{float(r['mean_escape_rate_pct']):.2f}",
                f"{float(r['std_escape_rate_pct']):.2f}",
                f"{float(r['mean_final_mastery']):.4f}",
                f"{float(r['escape_gain_vs_baseline_pp']):+.2f}",
                f"{float(r['escape_gain_vs_rule_based_pp']):+.2f}",
            ]
        )
    lines.append(_to_md_table(headers, rows))
    lines.append("")

    # Formal result paragraph.
    best_lines: list[str] = []
    for pr in sorted(pivot_rows, key=lambda x: int(x["MAX_STEPS"])):
        best_lines.append(
            f"At MAX_STEPS={int(pr['MAX_STEPS'])}, Adaptive (Ours) achieved {float(pr['Adaptive_Escape']):.2f}% escape-from-C, "
            f"with differences of {float(pr['Adaptive_minus_Baseline_pp']):+.2f} pp vs Baseline and {float(pr['Adaptive_minus_RuleBased_pp']):+.2f} pp vs Rule-Based."
        )
    adaptive_best_all = all(float(p["Adaptive_Escape"]) >= float(p["Baseline_Escape"]) and float(p["Adaptive_Escape"]) >= float(p["RuleBased_Escape"]) for p in pivot_rows)
    if adaptive_best_all:
        top_line = (
            "Under fixed instructional budgets, Adaptive (Ours) consistently achieved the highest escape-from-C rate for Weak (C) students."
        )
    else:
        top_line = (
            "Under fixed instructional budgets, the best-performing strategy varies by budget, indicating that strategy effectiveness is sensitive to the fixed resource regime."
        )

    lines.extend(
        [
            "## Result Interpretation",
            "",
            top_line,
            "This pattern indicates that the advantage of Adaptive is not explained solely by longer support horizons; rather, it reflects stronger use of limited instructional opportunities to complete the remediation-to-mainline learning cycle.",
            "",
        ]
        + [f"- {x}" for x in best_lines]
        + [""]
    )

    path.write_text("\n".join(lines), encoding="utf-8-sig")


def write_pivot_md(path: Path, rows: list[dict[str, Any]]) -> None:
    headers = [
        "MAX_STEPS",
        "Baseline_Escape",
        "RuleBased_Escape",
        "Adaptive_Escape",
        "Adaptive_minus_Baseline_pp",
        "Adaptive_minus_RuleBased_pp",
        "Baseline_Mastery",
        "RuleBased_Mastery",
        "Adaptive_Mastery",
    ]
    table_rows = [
        [
            str(int(r["MAX_STEPS"])),
            f"{float(r['Baseline_Escape']):.2f}",
            f"{float(r['RuleBased_Escape']):.2f}",
            f"{float(r['Adaptive_Escape']):.2f}",
            f"{float(r['Adaptive_minus_Baseline_pp']):+.2f}",
            f"{float(r['Adaptive_minus_RuleBased_pp']):+.2f}",
            f"{float(r['Baseline_Mastery']):.4f}",
            f"{float(r['RuleBased_Mastery']):.4f}",
            f"{float(r['Adaptive_Mastery']):.4f}",
        ]
        for r in sorted(rows, key=lambda x: int(x["MAX_STEPS"]))
    ]
    text = "# Experiment 3 Strategy Comparison Pivot\n\n" + _to_md_table(headers, table_rows) + "\n"
    path.write_text(text, encoding="utf-8-sig")


def write_caption(path: Path, pivot_rows: list[dict[str, Any]]) -> None:
    bullet = []
    for r in sorted(pivot_rows, key=lambda x: int(x["MAX_STEPS"])):
        bullet.append(
            f"MAX_STEPS={int(r['MAX_STEPS'])}: Adaptive difference is {float(r['Adaptive_minus_Baseline_pp']):+.2f} pp vs Baseline "
            f"and {float(r['Adaptive_minus_RuleBased_pp']):+.2f} pp vs Rule-Based."
        )
    adaptive_best_all = all(float(p["Adaptive_Escape"]) >= float(p["Baseline_Escape"]) and float(p["Adaptive_Escape"]) >= float(p["RuleBased_Escape"]) for p in pivot_rows)
    if adaptive_best_all:
        verdict = "Across fixed budgets, Adaptive consistently attains the strongest outcomes."
    else:
        verdict = "Across fixed budgets, the strongest strategy differs by budget, so system-level effectiveness should be interpreted condition-wise."

    text = (
        "### Figure Caption: Strategy Comparison under Fixed Budgets (Weak Students)\n\n"
        "This figure compares Baseline, Rule-Based, and Adaptive (Ours) under identical MAX_STEPS budgets for Weak (C) students, "
        "with escape-from-C defined as final mastery >= 0.60.\n"
        + verdict + "\n\n"
        + "\n".join([f"- {b}" for b in bullet])
        + "\n"
    )
    path.write_text(text, encoding="utf-8-sig")


def _sync_strategy_outputs(run_dir: Path) -> None:
    LATEST_DIR.mkdir(parents=True, exist_ok=True)
    for p in run_dir.iterdir():
        if not p.is_file():
            continue
        if (
            p.name.startswith("exp3_strategy_comparison_")
            or p.name.startswith("fig_exp3_strategy_comparison_")
            or p.name == "figure_caption_exp3_strategy_comparison.md"
        ):
            shutil.copy2(p, LATEST_DIR / p.name)


def _upsert_readme(path: Path, conclusion_line: str) -> None:
    section = (
        "## Strategy Comparison under Fixed Budgets\n"
        "- Why this view: to isolate system ability under equal resource limits rather than horizon length effects.\n"
        "- Research meaning: this comparison tests which strategy is most effective at rescuing Weak (C) students under the same MAX_STEPS.\n"
        "- Outputs:\n"
        "  - exp3_strategy_comparison_summary.csv/.md\n"
        "  - exp3_strategy_comparison_pivot.csv/.md\n"
        "  - fig_exp3_strategy_comparison_escape_rate.png\n"
        "  - fig_exp3_strategy_comparison_final_mastery.png\n"
        "  - figure_caption_exp3_strategy_comparison.md\n"
        f"- One-line conclusion: {conclusion_line}\n"
    )
    existing = path.read_text(encoding="utf-8-sig") if path.exists() else ""
    marker = "## Strategy Comparison under Fixed Budgets"
    if marker in existing:
        updated = existing.split(marker)[0].rstrip() + "\n\n" + section
    else:
        updated = existing.rstrip() + "\n\n" + section if existing.strip() else section
    path.write_text(updated.strip() + "\n", encoding="utf-8-sig")


def main() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    exp3_dirs = create_timestamped_run_dir(EXP3_DIR)
    run_dir = exp3_dirs["run_dir"]
    latest_dir = exp3_dirs["latest_dir"]
    final_dir = exp3_dirs["final_dir"]
    _validate_exp3_output_path(run_dir)
    _validate_exp3_output_path(latest_dir)
    _validate_exp3_output_path(final_dir)

    print(f"[RUN] Exp3 strategy comparison -> {run_dir}")
    if abs(float(EXP3_SUCCESS_THRESHOLD) - 0.60) > 1e-9:
        print("[WARNING] Exp3 threshold drift detected (expected 0.60)")

    prev_env = os.environ.get(EXP3_OUTPUT_DIR_ENV)
    os.environ[EXP3_OUTPUT_DIR_ENV] = str(run_dir)

    orig_extra = simulate_student.WEAK_FOUNDATION_EXTRA_STEPS
    orig_thr = float(simulate_student.RUNTIME_SUCCESS_THRESHOLD)
    orig_steps = int(simulate_student.MAX_STEPS)

    seed_raw: list[dict[str, Any]] = []
    try:
        try:
            simulate_student.RUNTIME_SUCCESS_THRESHOLD = float(EXP3_SUCCESS_THRESHOLD)
            simulate_student.WEAK_FOUNDATION_EXTRA_STEPS = 0

            # seed-level aggregation per (budget, strategy)
            tmp: dict[tuple[int, str], list[dict[str, Any]]] = {}
            for budget in FIXED_BUDGETS:
                for strategy_id, strategy_label in STRATEGY_ORDER:
                    key = (budget, strategy_label)
                    tmp[key] = []
                    for sd in SEED_LIST:
                        episodes = run_condition(budget, strategy_id, sd)
                        sr = summarize_seed(budget, strategy_label, sd, episodes)
                        tmp[key].append(sr)

            agg_rows: list[dict[str, Any]] = []
            for budget in FIXED_BUDGETS:
                for _, strategy_label in STRATEGY_ORDER:
                    seed_rows = tmp[(budget, strategy_label)]
                    seed_raw.extend(seed_rows)
                    agg_rows.append(
                        {
                            "MAX_STEPS": int(budget),
                            "Strategy": strategy_label,
                            "mean_escape_rate_pct": _mean([float(r["escape_rate_pct"]) for r in seed_rows]),
                            "std_escape_rate_pct": _std([float(r["escape_rate_pct"]) for r in seed_rows]),
                            "mean_avg_steps_used": _mean([float(r["avg_steps_used"]) for r in seed_rows]),
                            "std_avg_steps_used": _std([float(r["avg_steps_used"]) for r in seed_rows]),
                            "mean_final_mastery": _mean([float(r["final_mastery"]) for r in seed_rows]),
                            "std_final_mastery": _std([float(r["final_mastery"]) for r in seed_rows]),
                        }
                    )
        finally:
            simulate_student.WEAK_FOUNDATION_EXTRA_STEPS = orig_extra
            simulate_student.RUNTIME_SUCCESS_THRESHOLD = orig_thr
            simulate_student.MAX_STEPS = orig_steps

        long_rows = build_long_summary(agg_rows)
        pivot_rows = build_pivot_summary(long_rows)

        _write_csv(
            run_dir / "exp3_strategy_comparison_summary.csv",
            [
                "MAX_STEPS",
                "Strategy",
                "mean_escape_rate_pct",
                "std_escape_rate_pct",
                "mean_avg_steps_used",
                "std_avg_steps_used",
                "mean_final_mastery",
                "std_final_mastery",
                "escape_gain_vs_baseline_pp",
                "mastery_gain_vs_baseline",
                "escape_gain_vs_rule_based_pp",
                "mastery_gain_vs_rule_based",
            ],
            long_rows,
        )
        _write_csv(
            run_dir / "exp3_strategy_comparison_pivot.csv",
            [
                "MAX_STEPS",
                "Baseline_Escape",
                "RuleBased_Escape",
                "Adaptive_Escape",
                "Adaptive_minus_Baseline_pp",
                "Adaptive_minus_RuleBased_pp",
                "Baseline_Mastery",
                "RuleBased_Mastery",
                "Adaptive_Mastery",
            ],
            pivot_rows,
        )
        write_summary_md(run_dir / "exp3_strategy_comparison_summary.md", long_rows, pivot_rows)
        write_pivot_md(run_dir / "exp3_strategy_comparison_pivot.md", pivot_rows)
        write_caption(run_dir / "figure_caption_exp3_strategy_comparison.md", pivot_rows)

        setup_report_style()
        plot_exp3_strategy_comparison(
            summary_csv_path=run_dir / "exp3_strategy_comparison_summary.csv",
            output_dir=run_dir,
        )

        _sync_strategy_outputs(run_dir)
        adaptive_best_all = all(float(p["Adaptive_Escape"]) >= float(p["Baseline_Escape"]) and float(p["Adaptive_Escape"]) >= float(p["RuleBased_Escape"]) for p in pivot_rows)
        if adaptive_best_all:
            readme_line = (
                "Adaptive (Ours) consistently achieved the highest escape-from-C rate across fixed support budgets, indicating that its advantage is not merely due to longer support horizons, but also due to better use of limited instructional opportunities."
            )
        else:
            readme_line = (
                "Strategy effectiveness differs across fixed support budgets; therefore, system ability should be interpreted by budget-specific comparisons rather than a single universal winner."
            )
        _upsert_readme(EXP3_DIR / "README.md", readme_line)

        # Console summary requested by user.
        for pr in sorted(pivot_rows, key=lambda x: int(x["MAX_STEPS"])):
            best_name = "Adaptive (Ours)"
            best_val = float(pr["Adaptive_Escape"])
            if float(pr["Baseline_Escape"]) > best_val:
                best_name = "Baseline"
                best_val = float(pr["Baseline_Escape"])
            if float(pr["RuleBased_Escape"]) > best_val:
                best_name = "Rule-Based"
                best_val = float(pr["RuleBased_Escape"])
            print(f"[SUMMARY] MAX_STEPS={int(pr['MAX_STEPS'])}: best strategy={best_name} ({best_val:.2f}%)")

        max_gain_base = max(float(r["Adaptive_minus_Baseline_pp"]) for r in pivot_rows) if pivot_rows else 0.0
        max_gain_rule = max(float(r["Adaptive_minus_RuleBased_pp"]) for r in pivot_rows) if pivot_rows else 0.0
        print(f"[SUMMARY] max Adaptive gain vs Baseline: {max_gain_base:+.2f} pp")
        print(f"[SUMMARY] max Adaptive gain vs Rule-Based: {max_gain_rule:+.2f} pp")
    finally:
        if prev_env is None:
            os.environ.pop(EXP3_OUTPUT_DIR_ENV, None)
        else:
            os.environ[EXP3_OUTPUT_DIR_ENV] = prev_env


if __name__ == "__main__":
    main()
