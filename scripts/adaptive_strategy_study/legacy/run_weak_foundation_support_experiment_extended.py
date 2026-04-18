# -*- coding: utf-8 -*-
# ==============================================================================
# ID: run_weak_foundation_support_experiment_extended.py
# Version: V1.0.0 (Experiment 3 Extended / Plateau)
# Last Updated: 2026-04-15
# Author: *Steve
#
# [Description]:
#   Exp3 延伸分析：觀察 Weak 組在總支援預算上的高原點與邊際報酬遞減區間，
#   支援更長 MAX_STEPS 與選項化參數。
#
# [Database Schema Usage]:
#   無直接資料庫操作。
#
# [Logic Flow]:
#   1. 解析 CLI（若有）與步數清單。
#   2. 多 seed 模擬並計算高原指標。
#   3. 輸出圖表與報表。
# ==============================================================================

from __future__ import annotations

import argparse
import csv
import os
import random
import shutil
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
import pandas as pd  # noqa: E402

import simulate_student  # noqa: E402
from plot_experiment_results import create_timestamped_run_dir, setup_report_style  # noqa: E402

REPORTS_DIR = _study_paths.study_reports_root()
EXP3_DIR = REPORTS_DIR / "experiment_3_weak_foundation_support"
LATEST_DIR = EXP3_DIR / "latest"
EXP3_OUTPUT_DIR_ENV = "MATHPROJECT_EXP3_OUTPUT_DIR"

DEFAULT_MAX_STEPS_LIST = [30, 40, 50, 60, 70, 80, 90]
OPTIONAL_MAX_STEP = 100
SEED_LIST = [42, 43, 44, 45, 46, 47, 48, 49, 50, 51]
EXP3_SUCCESS_THRESHOLD = 0.60
PLATEAU_DELTA_THRESHOLD_PCT = 2.0


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


def run_total_step_condition(max_steps: int, seed: int) -> list[dict[str, Any]]:
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


def _build_seed_row(max_steps: int, seed: int, episodes: list[dict[str, Any]]) -> dict[str, Any]:
    weak_eps = [e for e in episodes if str(e.get("student_type", "")) == "Weak"]
    success_rate = _mean([1.0 if float(e["final_mastery"]) >= EXP3_SUCCESS_THRESHOLD else 0.0 for e in weak_eps])
    return {
        "max_steps": int(max_steps),
        "seed": int(seed),
        "episodes": int(len(weak_eps)),
        "escape_from_c_rate": round(float(success_rate), 6),
        "avg_final_mastery": round(_mean([float(e["final_mastery"]) for e in weak_eps]), 6),
        "avg_steps_used": round(_mean([float(e["total_steps"]) for e in weak_eps]), 6),
        "avg_mastery_gain": round(_mean([float(e["mastery_gain"]) for e in weak_eps]), 6),
    }


def _build_extended_summary(seed_rows: list[dict[str, Any]], max_steps_list: list[int]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    prev_escape: float | None = None
    prev_steps: float | None = None
    for ms in max_steps_list:
        cond = [r for r in seed_rows if int(r["max_steps"]) == int(ms)]
        if not cond:
            continue
        esc = [float(r["escape_from_c_rate"]) * 100.0 for r in cond]
        mastery = [float(r["avg_final_mastery"]) for r in cond]
        used = [float(r["avg_steps_used"]) for r in cond]
        mean_escape = _mean(esc)
        std_escape = _std(esc)
        mean_steps = _mean(used)
        std_steps = _std(used)
        delta_escape = None if prev_escape is None else (mean_escape - prev_escape)
        marginal_cost: float | str
        if prev_escape is None or prev_steps is None or delta_escape is None or delta_escape <= 0:
            marginal_cost = "NA"
        else:
            delta_steps = mean_steps - prev_steps
            marginal_cost = round(delta_steps / delta_escape, 6)
        rows.append(
            {
                "MAX_STEPS": int(ms),
                "mean_escape_rate_pct": round(mean_escape, 4),
                "std_escape_rate_pct": round(std_escape, 4),
                "mean_avg_steps_used": round(mean_steps, 6),
                "std_avg_steps_used": round(std_steps, 6),
                "mean_final_mastery": round(_mean(mastery), 6),
                "std_final_mastery": round(_std(mastery), 6),
                "delta_escape_vs_prev": "" if delta_escape is None else round(delta_escape, 4),
                "marginal_cost_steps_per_1pct_escape": marginal_cost,
            }
        )
        prev_escape = mean_escape
        prev_steps = mean_steps
    return rows


def _build_delta_summary(extended_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for i in range(1, len(extended_rows)):
        a = extended_rows[i - 1]
        b = extended_rows[i]
        delta_escape = float(b["mean_escape_rate_pct"]) - float(a["mean_escape_rate_pct"])
        delta_steps = float(b["mean_avg_steps_used"]) - float(a["mean_avg_steps_used"])
        if delta_escape <= 0:
            marginal_cost: float | str = "NA"
        else:
            marginal_cost = round(delta_steps / delta_escape, 6)
        plateau_flag = bool(delta_escape < PLATEAU_DELTA_THRESHOLD_PCT)
        rows.append(
            {
                "interval": f"{int(a['MAX_STEPS'])}→{int(b['MAX_STEPS'])}",
                "from_max_steps": int(a["MAX_STEPS"]),
                "to_max_steps": int(b["MAX_STEPS"]),
                "escape_rate_start": round(float(a["mean_escape_rate_pct"]), 4),
                "escape_rate_end": round(float(b["mean_escape_rate_pct"]), 4),
                "delta_escape_pct": round(delta_escape, 4),
                "avg_steps_start": round(float(a["mean_avg_steps_used"]), 6),
                "avg_steps_end": round(float(b["mean_avg_steps_used"]), 6),
                "delta_steps": round(delta_steps, 6),
                "marginal_cost_steps_per_1pct_escape": marginal_cost,
                "plateau_flag": plateau_flag,
            }
        )
    return rows


def _build_plateau_summary(delta_rows: list[dict[str, Any]], max_steps_list: list[int]) -> dict[str, Any]:
    first_plateau_interval = ""
    plateau_detected = False
    for i in range(1, len(delta_rows)):
        prev_flag = bool(delta_rows[i - 1]["plateau_flag"])
        curr_flag = bool(delta_rows[i]["plateau_flag"])
        if prev_flag and curr_flag:
            plateau_detected = True
            first_plateau_interval = str(delta_rows[i - 1]["interval"])
            break
    if plateau_detected:
        interpretation = (
            f"Plateau detected starting at interval {first_plateau_interval} "
            f"(two consecutive intervals with delta escape < {PLATEAU_DELTA_THRESHOLD_PCT:.1f} pp)."
        )
    else:
        interpretation = f"No clear plateau observed up to MAX_STEPS={max(max_steps_list)}"
    return {
        "max_steps_tested": int(max(max_steps_list)),
        "plateau_detected": bool(plateau_detected),
        "first_plateau_interval": first_plateau_interval,
        "rule_used": (
            f"plateau candidate if delta_escape < {PLATEAU_DELTA_THRESHOLD_PCT:.1f} pp; "
            "plateau detected if two consecutive candidates"
        ),
        "interpretation": interpretation,
    }


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _write_md(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8-sig")


def _md_extended_summary(rows: list[dict[str, Any]]) -> str:
    lines = [
        "# Experiment 3 Extended Summary Table",
        "",
        "| MAX_STEPS | Mean Escape-from-C Rate (%) | Std Escape Rate (%) | Mean Steps Used | Std Steps Used | Mean Final Mastery | Std Final Mastery | Delta Escape vs Prev (pp) | Marginal Cost (steps / +1%) |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in rows:
        delta = "" if r["delta_escape_vs_prev"] == "" else f"{float(r['delta_escape_vs_prev']):+.2f}"
        mc = r["marginal_cost_steps_per_1pct_escape"]
        mc_txt = "NA" if isinstance(mc, str) else f"{float(mc):.3f}"
        lines.append(
            f"| {int(r['MAX_STEPS'])} | {float(r['mean_escape_rate_pct']):.2f} | {float(r['std_escape_rate_pct']):.2f} | "
            f"{float(r['mean_avg_steps_used']):.2f} | {float(r['std_avg_steps_used']):.2f} | "
            f"{float(r['mean_final_mastery']):.4f} | {float(r['std_final_mastery']):.4f} | {delta} | {mc_txt} |"
        )
    lines.append("")
    return "\n".join(lines)


def _md_delta_summary(rows: list[dict[str, Any]]) -> str:
    lines = [
        "# Experiment 3 Delta Escape Summary",
        "",
        "| Interval | Escape Start (%) | Escape End (%) | Delta Escape (pp) | Steps Start | Steps End | Delta Steps | Marginal Cost (steps / +1%) | Plateau Candidate |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for r in rows:
        mc = r["marginal_cost_steps_per_1pct_escape"]
        mc_txt = "NA" if isinstance(mc, str) else f"{float(mc):.3f}"
        lines.append(
            f"| {r['interval']} | {float(r['escape_rate_start']):.2f} | {float(r['escape_rate_end']):.2f} | "
            f"{float(r['delta_escape_pct']):+.2f} | {float(r['avg_steps_start']):.2f} | "
            f"{float(r['avg_steps_end']):.2f} | {float(r['delta_steps']):.2f} | {mc_txt} | "
            f"{'Yes' if bool(r['plateau_flag']) else 'No'} |"
        )
    lines.append("")
    return "\n".join(lines)


def _md_plateau_summary(row: dict[str, Any]) -> str:
    lines = [
        "# Experiment 3 Plateau Summary",
        "",
        "| max_steps_tested | plateau_detected | first_plateau_interval | rule_used | interpretation |",
        "|---:|---|---|---|---|",
        f"| {int(row['max_steps_tested'])} | {bool(row['plateau_detected'])} | {row['first_plateau_interval']} | {row['rule_used']} | {row['interpretation']} |",
        "",
    ]
    return "\n".join(lines)


def _plot_escape_rate_extended(df: pd.DataFrame, plateau_summary: dict[str, Any], out_dir: Path) -> None:
    setup_report_style()
    fig, ax = plt.subplots(figsize=(8, 5))
    x = df["MAX_STEPS"].astype(float).tolist()
    y = df["mean_escape_rate_pct"].astype(float).tolist()
    yerr = df["std_escape_rate_pct"].astype(float).tolist()
    ax.errorbar(x, y, yerr=yerr, fmt="o-", linewidth=2.2, markersize=7, capsize=4, color="#2C7FB8")
    ax.set_title("Experiment 3: Escape-from-C Rate under Total-Step Relaxation (Multi-Seed)")
    ax.set_xlabel("MAX_STEPS")
    ax.set_ylabel("Escape-from-C Rate (%)")
    for xv, yv in zip(x, y):
        ax.annotate(f"{yv:.1f}%", (xv, yv), textcoords="offset points", xytext=(0, 7), ha="center", fontsize=9)

    if bool(plateau_summary["plateau_detected"]):
        interval = str(plateau_summary["first_plateau_interval"])
        start = float(interval.split("→")[0])
        ax.axvline(start, linestyle="--", linewidth=1.3, color="#666666")
        ax.text(0.98, 0.04, f"Plateau starts near {interval}", transform=ax.transAxes, ha="right", va="bottom", fontsize=8.8, color="#444444")
    else:
        ax.text(0.98, 0.04, "No clear plateau observed up to 90 steps", transform=ax.transAxes, ha="right", va="bottom", fontsize=8.8, color="#444444")

    fig.tight_layout()
    fig.savefig(str(out_dir / "fig_exp3_escape_rate_extended_multiseed.png"), dpi=300, bbox_inches="tight")
    plt.close(fig)


def _plot_cost_benefit_extended(df: pd.DataFrame, plateau_summary: dict[str, Any], out_dir: Path) -> None:
    setup_report_style()
    fig, ax = plt.subplots(figsize=(8, 5))
    x = df["mean_avg_steps_used"].astype(float).tolist()
    y = df["mean_escape_rate_pct"].astype(float).tolist()
    xerr = df["std_avg_steps_used"].astype(float).tolist()
    yerr = df["std_escape_rate_pct"].astype(float).tolist()
    labels = df["MAX_STEPS"].astype(int).tolist()
    ax.errorbar(x, y, xerr=xerr, yerr=yerr, fmt="o", capsize=4, color="#1F78B4")
    ax.plot(x, y, linewidth=1.4, alpha=0.7, color="#1F78B4")
    ax.set_title("Experiment 3: Cost vs Benefit under Total-Step Relaxation (Multi-Seed)")
    ax.set_xlabel("Mean Steps Used")
    ax.set_ylabel("Mean Escape-from-C Rate (%)")
    for xv, yv, lab in zip(x, y, labels):
        ax.annotate(f"MAX_STEPS={lab}", (xv, yv), textcoords="offset points", xytext=(5, 8), fontsize=8.5)
    if not bool(plateau_summary["plateau_detected"]):
        ax.text(0.98, 0.04, "returns still increasing through 90 steps", transform=ax.transAxes, ha="right", va="bottom", fontsize=8.8, color="#444444")
    fig.tight_layout()
    fig.savefig(str(out_dir / "fig_exp3_cost_vs_benefit_extended_multiseed.png"), dpi=300, bbox_inches="tight")
    plt.close(fig)


def _plot_marginal_gain(delta_df: pd.DataFrame, out_dir: Path) -> None:
    setup_report_style()
    fig, ax = plt.subplots(figsize=(8, 5))
    x = delta_df["interval"].astype(str).tolist()
    y = delta_df["delta_escape_pct"].astype(float).tolist()
    colors = ["#4D4D4D" if float(v) < PLATEAU_DELTA_THRESHOLD_PCT else "#4C72B0" for v in y]
    bars = ax.bar(x, y, color=colors)
    ax.axhline(PLATEAU_DELTA_THRESHOLD_PCT, linestyle="--", linewidth=1.2, color="#666666")
    ax.set_title("Experiment 3: Marginal Gain of Additional Support")
    ax.set_xlabel("MAX_STEPS Interval")
    ax.set_ylabel("Delta Escape-from-C Rate (percentage points)")
    for bar, val in zip(bars, y):
        ax.annotate(f"{val:+.1f}", (bar.get_x() + bar.get_width() / 2.0, val), textcoords="offset points", xytext=(0, 6), ha="center", fontsize=9)
    fig.tight_layout()
    fig.savefig(str(out_dir / "fig_exp3_marginal_gain_extended.png"), dpi=300, bbox_inches="tight")
    plt.close(fig)


def _plot_plateau_detection(df: pd.DataFrame, delta_df: pd.DataFrame, plateau_summary: dict[str, Any], out_dir: Path) -> None:
    setup_report_style()
    fig, ax = plt.subplots(figsize=(8.6, 5.2))
    x = df["MAX_STEPS"].astype(float).tolist()
    y = df["mean_escape_rate_pct"].astype(float).tolist()
    yerr = df["std_escape_rate_pct"].astype(float).tolist()
    ax.errorbar(x, y, yerr=yerr, fmt="o-", linewidth=2.0, markersize=6.5, capsize=4, color="#2C7FB8")

    # annotate marginal gains at interval centers
    for _, r in delta_df.iterrows():
        x0 = float(r["from_max_steps"])
        x1 = float(r["to_max_steps"])
        mid = (x0 + x1) / 2.0
        y0 = float(df.loc[df["MAX_STEPS"] == x0, "mean_escape_rate_pct"].iloc[0])
        y1 = float(df.loc[df["MAX_STEPS"] == x1, "mean_escape_rate_pct"].iloc[0])
        ym = (y0 + y1) / 2.0
        ax.text(mid, ym + 1.0, f"{float(r['delta_escape_pct']):+.1f} pp", ha="center", va="bottom", fontsize=8.6, color="#333333")

    ax.set_title("Experiment 3: Plateau Detection Summary")
    ax.set_xlabel("MAX_STEPS")
    ax.set_ylabel("Escape-from-C Rate (%)")
    ax.text(
        0.02,
        0.98,
        f"Rule: plateau candidate if delta < {PLATEAU_DELTA_THRESHOLD_PCT:.1f} pp; plateau requires two consecutive candidates",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=8.2,
        color="#444444",
    )
    if bool(plateau_summary["plateau_detected"]):
        interval = str(plateau_summary["first_plateau_interval"])
        start = float(interval.split("→")[0])
        ax.axvline(start, linestyle="--", linewidth=1.2, color="#666666")
        ax.text(0.98, 0.05, f"Plateau detected from {interval}", transform=ax.transAxes, ha="right", va="bottom", fontsize=8.8, color="#444444")
    else:
        ax.text(0.98, 0.05, "No clear plateau observed up to MAX_STEPS=90", transform=ax.transAxes, ha="right", va="bottom", fontsize=8.8, color="#444444")

    fig.tight_layout()
    fig.savefig(str(out_dir / "fig_exp3_plateau_detection.png"), dpi=300, bbox_inches="tight")
    plt.close(fig)


def _write_captions(out_dir: Path, plateau_summary: dict[str, Any]) -> None:
    _write_md(
        out_dir / "figure_caption_exp3_extended_escape_rate.md",
        "### Figure Caption: Extended Escape-from-C Rate under Total-Step Relaxation\n\n"
        "This figure reports multi-seed escape-from-C performance (final mastery >= 0.60) for weak students across an extended MAX_STEPS range (30-90).\n"
        "Error bars indicate cross-seed variability and support robustness-focused interpretation beyond single-run fluctuations.\n",
    )
    _write_md(
        out_dir / "figure_caption_exp3_extended_cost_benefit.md",
        "### Figure Caption: Extended Cost vs Benefit under Total-Step Relaxation\n\n"
        "This figure summarizes the relationship between mean learning cost (steps used) and mean escape-from-C outcomes under the extended step budget range.\n"
        "It is used to evaluate whether larger budgets continue to provide practical returns for reducing the C-range population.\n",
    )
    if bool(plateau_summary["plateau_detected"]):
        plateau_text = (
            f"Plateau detection identifies the onset of diminishing returns starting at {plateau_summary['first_plateau_interval']}, "
            "based on two consecutive low-gain intervals."
        )
    else:
        plateau_text = "No clear plateau is observed up to MAX_STEPS=90, indicating that gains still accumulate within the tested range."
    _write_md(
        out_dir / "figure_caption_exp3_plateau_detection.md",
        "### Figure Caption: Plateau Detection Summary\n\n"
        "This summary figure combines the extended escape-from-C trajectory with interval-level marginal gains.\n"
        f"{plateau_text}\n",
    )


def _sync_extended_to_latest(run_dir: Path) -> None:
    LATEST_DIR.mkdir(parents=True, exist_ok=True)
    for p in run_dir.iterdir():
        if not p.is_file():
            continue
        # Only sync extended artifacts so legacy outputs remain available.
        if (
            p.name.startswith("exp3_extended_")
            or p.name.startswith("exp3_delta_")
            or p.name.startswith("exp3_plateau_")
            or p.name.startswith("fig_exp3_escape_rate_extended_")
            or p.name.startswith("fig_exp3_cost_vs_benefit_extended_")
            or p.name.startswith("fig_exp3_marginal_gain_extended")
            or p.name.startswith("fig_exp3_plateau_detection")
            or p.name.startswith("figure_caption_exp3_extended_")
            or p.name.startswith("figure_caption_exp3_plateau_detection")
        ):
            shutil.copy2(p, LATEST_DIR / p.name)


def _upsert_extended_readme_section(path: Path, plateau_summary: dict[str, Any]) -> None:
    section = (
        "## Extended Plateau Analysis\n"
        "- Why extend from 70 to 90: to test whether escape-from-C gains begin to saturate under larger total-step budgets.\n"
        f"- Plateau rule: interval is candidate if delta escape < {PLATEAU_DELTA_THRESHOLD_PCT:.1f} pp; plateau requires two consecutive candidate intervals.\n"
        "- Main outputs:\n"
        "  - exp3_extended_summary_table.csv/.md\n"
        "  - exp3_delta_escape_summary.csv/.md\n"
        "  - exp3_plateau_summary.csv/.md\n"
        "  - fig_exp3_escape_rate_extended_multiseed.png\n"
        "  - fig_exp3_cost_vs_benefit_extended_multiseed.png\n"
        "  - fig_exp3_marginal_gain_extended.png\n"
        "  - fig_exp3_plateau_detection.png\n"
        f"- One-line conclusion: {plateau_summary['interpretation']}\n"
    )
    existing = path.read_text(encoding="utf-8-sig") if path.exists() else ""
    marker = "## Extended Plateau Analysis"
    if marker in existing:
        updated = existing.split(marker)[0].rstrip() + "\n\n" + section
    else:
        updated = existing.rstrip() + "\n\n" + section if existing.strip() else section
    path.write_text(updated.strip() + "\n", encoding="utf-8-sig")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Experiment 3 extended plateau analysis.")
    parser.add_argument("--include-100", action="store_true", help="Include MAX_STEPS=100 in extended sweep.")
    args = parser.parse_args()

    max_steps_list = list(DEFAULT_MAX_STEPS_LIST)
    if args.include_100:
        max_steps_list.append(OPTIONAL_MAX_STEP)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    exp3_dirs = create_timestamped_run_dir(EXP3_DIR)
    run_dir = exp3_dirs["run_dir"]
    latest_dir = exp3_dirs["latest_dir"]
    final_dir = exp3_dirs["final_dir"]
    _validate_exp3_output_path(run_dir)
    _validate_exp3_output_path(latest_dir)
    _validate_exp3_output_path(final_dir)

    print(f"[RUN] Extended outputs -> {run_dir}")
    print(f"[PROTECT] final/ remains untouched -> {final_dir}")
    if abs(float(EXP3_SUCCESS_THRESHOLD) - 0.60) > 1e-9:
        print("[WARNING] Exp3 threshold drift detected (expected 0.60)")

    prev_output_env = os.environ.get(EXP3_OUTPUT_DIR_ENV)
    os.environ[EXP3_OUTPUT_DIR_ENV] = str(run_dir)

    original_extra = simulate_student.WEAK_FOUNDATION_EXTRA_STEPS
    original_threshold = float(simulate_student.RUNTIME_SUCCESS_THRESHOLD)
    original_max_steps = int(simulate_student.MAX_STEPS)
    seed_rows: list[dict[str, Any]] = []
    try:
        try:
            simulate_student.RUNTIME_SUCCESS_THRESHOLD = float(EXP3_SUCCESS_THRESHOLD)
            simulate_student.WEAK_FOUNDATION_EXTRA_STEPS = 0
            for ms in max_steps_list:
                for sd in SEED_LIST:
                    print(f"Running extended condition: max_steps={ms}, seed={sd}")
                    eps = run_total_step_condition(ms, sd)
                    seed_rows.append(_build_seed_row(ms, sd, eps))
        finally:
            simulate_student.WEAK_FOUNDATION_EXTRA_STEPS = original_extra
            simulate_student.RUNTIME_SUCCESS_THRESHOLD = original_threshold
            simulate_student.MAX_STEPS = original_max_steps

        extended_rows = _build_extended_summary(seed_rows, max_steps_list)
        delta_rows = _build_delta_summary(extended_rows)
        plateau_row = _build_plateau_summary(delta_rows, max_steps_list)

        _write_csv(
            run_dir / "exp3_extended_summary_table.csv",
            [
                "MAX_STEPS",
                "mean_escape_rate_pct",
                "std_escape_rate_pct",
                "mean_avg_steps_used",
                "std_avg_steps_used",
                "mean_final_mastery",
                "std_final_mastery",
                "delta_escape_vs_prev",
                "marginal_cost_steps_per_1pct_escape",
            ],
            extended_rows,
        )
        _write_md(run_dir / "exp3_extended_summary_table.md", _md_extended_summary(extended_rows))

        _write_csv(
            run_dir / "exp3_delta_escape_summary.csv",
            [
                "interval",
                "from_max_steps",
                "to_max_steps",
                "escape_rate_start",
                "escape_rate_end",
                "delta_escape_pct",
                "avg_steps_start",
                "avg_steps_end",
                "delta_steps",
                "marginal_cost_steps_per_1pct_escape",
                "plateau_flag",
            ],
            delta_rows,
        )
        _write_md(run_dir / "exp3_delta_escape_summary.md", _md_delta_summary(delta_rows))

        _write_csv(
            run_dir / "exp3_plateau_summary.csv",
            ["max_steps_tested", "plateau_detected", "first_plateau_interval", "rule_used", "interpretation"],
            [plateau_row],
        )
        _write_md(run_dir / "exp3_plateau_summary.md", _md_plateau_summary(plateau_row))

        df_ext = pd.DataFrame(extended_rows)
        df_delta = pd.DataFrame(delta_rows)
        _plot_escape_rate_extended(df_ext, plateau_row, run_dir)
        _plot_cost_benefit_extended(df_ext, plateau_row, run_dir)
        _plot_marginal_gain(df_delta, run_dir)
        _plot_plateau_detection(df_ext, df_delta, plateau_row, run_dir)
        _write_captions(run_dir, plateau_row)

        _sync_extended_to_latest(run_dir)
        _upsert_extended_readme_section(EXP3_DIR / "README.md", plateau_row)

        best_row = max(extended_rows, key=lambda r: float(r["mean_escape_rate_pct"]))
        positive_intervals = [r for r in delta_rows if float(r["delta_escape_pct"]) > 0]
        best_interval = max(positive_intervals, key=lambda r: float(r["delta_escape_pct"])) if positive_intervals else None
        print(f"[SUMMARY] best escape rate observed: {float(best_row['mean_escape_rate_pct']):.2f}% at MAX_STEPS={int(best_row['MAX_STEPS'])}")
        if best_interval is not None:
            print(f"[SUMMARY] best marginal return interval: {best_interval['interval']} ({float(best_interval['delta_escape_pct']):+.2f} pp)")
        if bool(plateau_row["plateau_detected"]):
            print(f"[SUMMARY] plateau detected: True (starts at {plateau_row['first_plateau_interval']})")
        else:
            print(f"[SUMMARY] plateau detected: False; no clear plateau up to MAX_STEPS={int(plateau_row['max_steps_tested'])}")
    finally:
        if prev_output_env is None:
            os.environ.pop(EXP3_OUTPUT_DIR_ENV, None)
        else:
            os.environ[EXP3_OUTPUT_DIR_ENV] = prev_output_env


if __name__ == "__main__":
    main()

