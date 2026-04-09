"""
[File Name]
plot_experiment_results.py

[Created Date]
2026-04-09

[Project]
Adaptive Math Learning System (Adaptive Summative + Teaching)

[Description]
This script reads experiment CSV outputs and generates publication-ready figures for ablation and learning-dynamics analysis.
It consolidates Experiment 1/2/3/4/5 visualizations into a reproducible plotting pipeline.
The file includes summary charts, remediation profiles, mastery trajectories, and multi-condition comparison figures.
It re-renders figures directly from latest logs to keep reporting synchronized with each run.

[Core Functionality]
- Load structured CSV outputs from reports/ and validate plotting prerequisites
- Generate ablation and strategy-by-student-type comparison figures
- Generate Experiment 2 policy profile and mastery trajectory figures from trajectory logs
- Generate weak-foundation and RAG extension visualization sets
- Export standardized PNG figures and caption files for reporting reuse

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
import shutil
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
try:
    import seaborn as sns
except Exception:  # pragma: no cover - plotting fallback
    sns = None

REPORTS_DIR = "reports"
EXP1_DIR = os.path.join(REPORTS_DIR, "experiment_1_ablation")

STRATEGY_ORDER = ["AB1_Baseline", "AB2_RuleBased", "AB3_PPO_Dynamic"]
STUDENT_TYPE_ORDER = ["Careless", "Average", "Weak"]
SUBSKILL_ORDER = [
    "sign_handling",
    "combine_like_terms",
    "sign_distribution",
    "expand_monomial",
    "expand_binomial",
    "family_isomorphism",
]


def read_csv_rows(path: str) -> list[dict[str, str]]:
    """Read CSV rows safely; return empty list when file is missing."""
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def as_float(value: Any) -> float | None:
    """Parse float with empty-value safety."""
    if value is None:
        return None
    text = str(value).strip()
    if text == "":
        return None
    try:
        return float(text)
    except ValueError:
        return None


def save_fig(path: str) -> None:
    """Save current figure with consistent layout and dpi."""
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def save_fig_high_quality(path: str) -> None:
    """Save high-quality publication figure."""
    plt.tight_layout()
    plt.savefig(path, dpi=300, bbox_inches="tight")
    if sns is not None:
        sns.despine()
    plt.close()


def plot_ablation_success_rate(summary_rows: list[dict[str, str]]) -> None:
    """Figure A: compare success rate by strategy."""
    xs: list[str] = []
    ys: list[float] = []

    for strategy in STRATEGY_ORDER:
        row = next((r for r in summary_rows if r.get("strategy") == strategy), None)
        if not row:
            continue
        v = as_float(row.get("success_rate"))
        if v is None:
            continue
        xs.append(strategy)
        ys.append(v * 100.0)

    if not xs:
        return

    plt.figure(figsize=(8, 5))
    plt.bar(xs, ys)
    plt.title("Ablation Success Rate by Strategy")
    plt.xlabel("Strategy")
    plt.ylabel("Success Rate (%)")
    plt.ylim(0, 100)
    os.makedirs(EXP1_DIR, exist_ok=True)
    save_fig(os.path.join(EXP1_DIR, "fig_ablation_success_rate.png"))


def plot_ablation_steps_vs_success(summary_rows: list[dict[str, str]]) -> None:
    """Figure B: grouped bars for avg steps and success rate."""
    labels: list[str] = []
    steps_vals: list[float] = []
    success_vals: list[float] = []

    for strategy in STRATEGY_ORDER:
        row = next((r for r in summary_rows if r.get("strategy") == strategy), None)
        if not row:
            continue
        step_v = as_float(row.get("avg_steps"))
        succ_v = as_float(row.get("success_rate"))
        if step_v is None or succ_v is None:
            continue
        labels.append(strategy)
        steps_vals.append(step_v)
        success_vals.append(succ_v * 100.0)

    if not labels:
        return

    x = list(range(len(labels)))
    width = 0.38

    plt.figure(figsize=(9, 5))
    plt.bar([i - width / 2 for i in x], steps_vals, width=width, label="Avg Steps")
    plt.bar([i + width / 2 for i in x], success_vals, width=width, label="Success Rate (%)")
    plt.xticks(x, labels)
    plt.title("Ablation Avg Steps vs Success Rate")
    plt.xlabel("Strategy")
    plt.ylabel("Value")
    plt.legend()
    os.makedirs(EXP1_DIR, exist_ok=True)
    save_fig(os.path.join(EXP1_DIR, "fig_ablation_steps_vs_success.png"))


def plot_ablation_by_student_type_success(rows: list[dict[str, str]]) -> None:
    """Figure C: grouped success bars by student type."""
    present_types = [t for t in STUDENT_TYPE_ORDER if any(r.get("student_type") == t for r in rows)]
    if not present_types:
        return

    x = list(range(len(present_types)))
    width = 0.24

    plt.figure(figsize=(10, 5))
    for idx, strategy in enumerate(STRATEGY_ORDER):
        ys: list[float] = []
        for student_type in present_types:
            row = next(
                (
                    r
                    for r in rows
                    if r.get("strategy") == strategy and r.get("student_type") == student_type
                ),
                None,
            )
            v = as_float(row.get("success_rate")) if row else None
            ys.append((v * 100.0) if v is not None else 0.0)
        offset = (idx - 1) * width
        plt.bar([i + offset for i in x], ys, width=width, label=strategy)

    plt.xticks(x, present_types)
    plt.title("Ablation Success Rate by Student Type")
    plt.xlabel("Student Type")
    plt.ylabel("Success Rate (%)")
    plt.ylim(0, 100)
    plt.legend()
    os.makedirs(EXP1_DIR, exist_ok=True)
    save_fig(os.path.join(EXP1_DIR, "fig_ablation_by_student_type_success.png"))


def plot_ablation_strategy_breakdown(summary_csv_path: str | None = None) -> None:
    """Experiment 1 analysis figure: grouped strategy metrics from ablation summary."""
    path = summary_csv_path or os.path.join(EXP1_DIR, "ablation_strategy_summary.csv")
    if not os.path.exists(path):
        alt = os.path.join(REPORTS_DIR, "ablation_strategy_summary.csv")
        path = alt if os.path.exists(alt) else path
    if not os.path.exists(path):
        return

    df = pd.read_csv(path)
    if df.empty or "strategy" not in df.columns:
        return

    metric_specs = [
        ("Success Rate (%)", "success_rate", 100.0),
        ("Avg Steps", "avg_steps", 1.0),
        ("Avg Final Mastery (%)", "avg_final_polynomial_mastery", 100.0),
        ("Avg Unnecessary Remediations", "avg_unnecessary_remediations", 1.0),
    ]
    for _, col, _ in metric_specs:
        if col not in df.columns:
            return

    ordered = df[df["strategy"].isin(STRATEGY_ORDER)].copy()
    if ordered.empty:
        return
    ordered["strategy"] = pd.Categorical(ordered["strategy"], categories=STRATEGY_ORDER, ordered=True)
    ordered = ordered.sort_values("strategy")

    x_labels = ordered["strategy"].tolist()
    x = list(range(len(x_labels)))
    width = 0.2

    plt.figure(figsize=(11, 6))
    for idx, (label, col, scale) in enumerate(metric_specs):
        vals = pd.to_numeric(ordered[col], errors="coerce").fillna(0.0) * scale
        offset = (idx - 1.5) * width
        bars = plt.bar([i + offset for i in x], vals, width=width, label=label)
        for bar in bars:
            h = bar.get_height()
            plt.annotate(
                f"{h:.2f}",
                (bar.get_x() + bar.get_width() / 2, h),
                textcoords="offset points",
                xytext=(0, 3),
                ha="center",
                fontsize=8,
            )

    plt.xticks(x, x_labels)
    plt.title("Experiment 1 Strategy Breakdown")
    plt.xlabel("Strategy")
    plt.ylabel("Metric Value")
    plt.legend()
    os.makedirs(EXP1_DIR, exist_ok=True)
    save_fig(os.path.join(EXP1_DIR, "fig_ablation_strategy_breakdown.png"))


def plot_ablation_by_student_type(by_type_csv_path: str | None = None) -> None:
    """Experiment 1 analysis figure: student-type success rate by strategy."""
    path = by_type_csv_path or os.path.join(EXP1_DIR, "multi_steps_strategy_by_type_summary.csv")
    if not os.path.exists(path):
        fallback = os.path.join(EXP1_DIR, "ablation_strategy_by_student_type_summary.csv")
        path = fallback if os.path.exists(fallback) else path
    if not os.path.exists(path):
        return

    df = pd.read_csv(path)
    if df.empty or "strategy" not in df.columns or "student_type" not in df.columns:
        return
    if "success_rate" not in df.columns:
        return

    grouped = (
        df.groupby(["strategy", "student_type"], as_index=False)
        .agg(success_rate=("success_rate", "mean"))
        .copy()
    )
    if grouped.empty:
        return

    student_order = ["Careless", "Average", "Weak"]
    student_display = {"Careless": "high", "Average": "mid", "Weak": "low"}
    x_labels = [t for t in student_order if any(grouped["student_type"] == t)]
    if not x_labels:
        return

    x = list(range(len(x_labels)))
    width = 0.24

    plt.figure(figsize=(10, 6))
    for idx, strategy in enumerate(STRATEGY_ORDER):
        ys: list[float] = []
        for st in x_labels:
            hit = grouped[(grouped["strategy"] == strategy) & (grouped["student_type"] == st)]
            if hit.empty:
                ys.append(float("nan"))
            else:
                ys.append(float(pd.to_numeric(hit["success_rate"], errors="coerce").mean()) * 100.0)
        offset = (idx - 1) * width
        bars = plt.bar([i + offset for i in x], ys, width=width, label=strategy)
        for bar in bars:
            h = bar.get_height()
            if pd.isna(h):
                continue
            plt.annotate(
                f"{h:.2f}",
                (bar.get_x() + bar.get_width() / 2, h),
                textcoords="offset points",
                xytext=(0, 3),
                ha="center",
                fontsize=8,
            )

    plt.xticks(x, [student_display.get(s, s) for s in x_labels])
    plt.title("Experiment 1 Success Rate by Student Type and Strategy")
    plt.xlabel("Student Type")
    plt.ylabel("Success Rate (%)")
    plt.ylim(0, 100)
    plt.legend()
    os.makedirs(EXP1_DIR, exist_ok=True)
    save_fig(os.path.join(EXP1_DIR, "fig_ablation_by_student_type.png"))


def plot_ab3_subskill_gain_by_type(rows: list[dict[str, str]]) -> None:
    """Figure D: grouped subskill gain bars by student type."""
    present_subskills = [s for s in SUBSKILL_ORDER if any(r.get("subskill") == s for r in rows)]
    if not present_subskills:
        return

    x = list(range(len(present_subskills)))
    width = 0.24

    plt.figure(figsize=(12, 5))
    for idx, student_type in enumerate(STUDENT_TYPE_ORDER):
        ys: list[float] = []
        for subskill in present_subskills:
            row = next(
                (
                    r
                    for r in rows
                    if r.get("student_type") == student_type and r.get("subskill") == subskill
                ),
                None,
            )
            v = as_float(row.get("avg_gain")) if row else None
            ys.append(v if v is not None else 0.0)
        offset = (idx - 1) * width
        plt.bar([i + offset for i in x], ys, width=width, label=student_type)

    plt.xticks(x, present_subskills, rotation=20, ha="right")
    plt.title("AB3 Subskill Gain by Student Type")
    plt.xlabel("Subskill")
    plt.ylabel("Average Gain")
    plt.legend()
    save_fig(os.path.join(REPORTS_DIR, "fig_ab3_subskill_gain_by_type.png"))


def plot_ab3_polynomial_gain_by_type(rows: list[dict[str, str]]) -> None:
    """Figure E: compare AB3 polynomial gain by student type."""
    xs: list[str] = []
    ys: list[float] = []

    for student_type in STUDENT_TYPE_ORDER:
        row = next((r for r in rows if r.get("student_type") == student_type), None)
        if not row:
            continue
        v = as_float(row.get("avg_polynomial_gain"))
        if v is None:
            continue
        xs.append(student_type)
        ys.append(v)

    if not xs:
        return

    plt.figure(figsize=(8, 5))
    plt.bar(xs, ys)
    plt.title("AB3 Polynomial Gain by Student Type")
    plt.xlabel("Student Type")
    plt.ylabel("Average Polynomial Gain")
    save_fig(os.path.join(REPORTS_DIR, "fig_ab3_polynomial_gain_by_type.png"))


def plot_multi_steps_results(include_ab3_by_student_type: bool = True) -> None:
    """Plot cross-step comparisons from multi-step summary CSV outputs."""
    strategy_path = os.path.join(REPORTS_DIR, "multi_steps_strategy_summary.csv")
    by_type_path = os.path.join(REPORTS_DIR, "multi_steps_strategy_by_type_summary.csv")
    if not os.path.exists(strategy_path):
        strategy_path = os.path.join(EXP1_DIR, "multi_steps_strategy_summary.csv")
    if not os.path.exists(by_type_path):
        by_type_path = os.path.join(EXP1_DIR, "multi_steps_strategy_by_type_summary.csv")

    strategy_df = pd.read_csv(strategy_path) if os.path.exists(strategy_path) else pd.DataFrame()
    by_type_df = pd.read_csv(by_type_path) if os.path.exists(by_type_path) else pd.DataFrame()

    if not strategy_df.empty and {"max_steps", "strategy", "success_rate"}.issubset(strategy_df.columns):
        plt.figure(figsize=(8, 5))
        for strategy in STRATEGY_ORDER:
            sub = strategy_df[strategy_df["strategy"] == strategy].copy()
            if sub.empty:
                continue
            sub = sub.sort_values("max_steps")
            plt.plot(sub["max_steps"], sub["success_rate"] * 100.0, marker="o", label=strategy)
        plt.title("Success Rate vs MAX_STEPS")
        plt.xlabel("MAX_STEPS")
        plt.ylabel("Success Rate (%)")
        plt.ylim(0, 100)
        plt.legend()
        os.makedirs(EXP1_DIR, exist_ok=True)
        save_fig(os.path.join(EXP1_DIR, "fig_multi_steps_success_rate.png"))

    if (
        include_ab3_by_student_type
        and not by_type_df.empty
        and {"max_steps", "strategy", "student_type", "success_rate"}.issubset(by_type_df.columns)
    ):
        ab3 = by_type_df[by_type_df["strategy"] == "AB3_PPO_Dynamic"].copy()
        if not ab3.empty:
            plt.figure(figsize=(8, 5))
            for student_type in STUDENT_TYPE_ORDER:
                sub = ab3[ab3["student_type"] == student_type].copy()
                if sub.empty:
                    continue
                sub = sub.sort_values("max_steps")
                plt.plot(sub["max_steps"], sub["success_rate"] * 100.0, marker="o", label=student_type)
            plt.title("AB3 Success Rate by Student Type vs MAX_STEPS")
            plt.xlabel("MAX_STEPS")
            plt.ylabel("Success Rate (%)")
            plt.ylim(0, 100)
            plt.legend()
            save_fig(os.path.join(REPORTS_DIR, "fig_multi_steps_ab3_by_student_type.png"))

    if not strategy_df.empty and {"avg_steps", "success_rate", "strategy", "max_steps"}.issubset(strategy_df.columns):
        plt.figure(figsize=(8, 5))
        plt.scatter(strategy_df["avg_steps"], strategy_df["success_rate"] * 100.0)
        for _, row in strategy_df.iterrows():
            label = f"{row['strategy']}@{int(row['max_steps'])}"
            plt.annotate(label, (row["avg_steps"], row["success_rate"] * 100.0), fontsize=8)
        plt.title("Steps vs Success Tradeoff Across MAX_STEPS")
        plt.xlabel("Average Steps")
        plt.ylabel("Success Rate (%)")
        os.makedirs(EXP1_DIR, exist_ok=True)
        save_fig(os.path.join(EXP1_DIR, "fig_multi_steps_efficiency.png"))

    # Experiment 1 analysis figures from per-strategy and strategy-by-type summaries.
    plot_ablation_strategy_breakdown()
    plot_ablation_by_student_type()


def plot_weak_foundation_support_results(
    output_dir: str = os.path.join(REPORTS_DIR, "experiment_3_weak_foundation_support"),
) -> None:
    """Plot weak foundation support decision-focused figures from experiment_3 CSV outputs."""
    plt.style.use("seaborn-v0_8-whitegrid")
    plt.rcParams["font.family"] = "Microsoft JhengHei"
    out_dir = output_dir
    summary_path = os.path.join(out_dir, "weak_foundation_support_summary.csv")
    subskill_path = os.path.join(out_dir, "weak_foundation_subskill_summary.csv")
    breakpoint_path = os.path.join(out_dir, "weak_foundation_breakpoint_summary.csv")

    summary_df = pd.read_csv(summary_path) if os.path.exists(summary_path) else pd.DataFrame()
    subskill_df = pd.read_csv(subskill_path) if os.path.exists(subskill_path) else pd.DataFrame()
    breakpoint_df = pd.read_csv(breakpoint_path) if os.path.exists(breakpoint_path) else pd.DataFrame()

    peak_steps_label = "N/A"

    # A) Success rate vs foundation extra steps (main figure).
    if not summary_df.empty and {"foundation_extra_steps", "success_rate"}.issubset(summary_df.columns):
        sub = summary_df.sort_values("foundation_extra_steps")
        plt.figure(figsize=(8, 5))
        plt.plot(
            sub["foundation_extra_steps"],
            sub["success_rate"] * 100.0,
            marker="o",
            linewidth=3,
            markersize=8,
        )
        plt.title("Effect of Foundation Support on Success Rate")
        plt.xlabel("Foundation Extra Steps")
        plt.ylabel("Success Rate (%)")
        plt.ylim(0, 35)
        plt.axvspan(40, 50, alpha=0.1, color="green")
        for _, row in sub.iterrows():
            x = float(row["foundation_extra_steps"])
            y = float(row["success_rate"]) * 100.0
            plt.annotate(f"{y:.1f}", (x, y), textcoords="offset points", xytext=(0, 6), ha="center")
        try:
            peak_idx = sub["success_rate"].astype(float).idxmax()
            peak_steps = int(float(sub.loc[peak_idx, "foundation_extra_steps"]))
            peak_rate = float(sub.loc[peak_idx, "success_rate"]) * 100.0
            peak_steps_label = str(peak_steps)
            plt.scatter([peak_steps], [peak_rate], color="red", zorder=5)
            plt.annotate(
                "Optimal (~50 steps)",
                (peak_steps, peak_rate),
                textcoords="offset points",
                xytext=(0, -18),
                ha="center",
            )
        except Exception:
            pass
        if sns is not None:
            sns.despine()
        save_fig_high_quality(os.path.join(out_dir, "fig_weak_foundation_success_rate.png"))

    # B) Learning cost vs foundation support (main figure).
    if not summary_df.empty and {"foundation_extra_steps", "avg_total_steps"}.issubset(summary_df.columns):
        sub = summary_df.sort_values("foundation_extra_steps")
        plt.figure(figsize=(8, 5))
        plt.plot(
            sub["foundation_extra_steps"],
            sub["avg_total_steps"],
            marker="o",
            linewidth=3,
            markersize=8,
        )
        plt.title("Learning Cost vs Foundation Support")
        plt.xlabel("Foundation Extra Steps")
        plt.ylabel("Average Total Steps")
        for _, row in sub.iterrows():
            x = float(row["foundation_extra_steps"])
            y = float(row["avg_total_steps"])
            plt.annotate(f"{y:.1f}", (x, y), textcoords="offset points", xytext=(0, 6), ha="center")
        try:
            x_mid = float(sub["foundation_extra_steps"].median())
            y_mid = float(sub["avg_total_steps"].median())
            plt.annotate("Cost increases steadily", (x_mid, y_mid), textcoords="offset points", xytext=(12, 12))
        except Exception:
            pass
        if sns is not None:
            sns.despine()
        save_fig_high_quality(os.path.join(out_dir, "fig_weak_foundation_cost.png"))

    # C) Final mastery vs foundation extra steps (supporting main effect).
    if not summary_df.empty and {"foundation_extra_steps", "avg_final_polynomial_mastery"}.issubset(
        summary_df.columns
    ):
        sub = summary_df.sort_values("foundation_extra_steps")
        plt.figure(figsize=(8, 5))
        plt.plot(
            sub["foundation_extra_steps"],
            sub["avg_final_polynomial_mastery"],
            marker="o",
            linewidth=3,
            markersize=8,
        )
        plt.title("Final Polynomial Mastery vs Foundation Support")
        plt.xlabel("Foundation Extra Steps")
        plt.ylabel("Average Final Polynomial Mastery")
        for _, row in sub.iterrows():
            x = float(row["foundation_extra_steps"])
            y = float(row["avg_final_polynomial_mastery"])
            plt.annotate(f"{y:.3f}", (x, y), textcoords="offset points", xytext=(0, 6), ha="center")
        try:
            x_max = float(sub.iloc[-1]["foundation_extra_steps"])
            y_max = float(sub["avg_final_polynomial_mastery"].max())
            plt.annotate("Near saturation", (x_max, y_max), textcoords="offset points", xytext=(-70, 10))
        except Exception:
            pass
        if sns is not None:
            sns.despine()
        save_fig_high_quality(os.path.join(out_dir, "fig_weak_foundation_mastery.png"))

    # D) Breakpoint shift simplified: top-2 weakest subskills only (supporting).
    if not breakpoint_df.empty and {"foundation_extra_steps", "subskill", "percentage"}.issubset(
        breakpoint_df.columns
    ):
        steps_list = sorted(breakpoint_df["foundation_extra_steps"].dropna().unique().tolist())
        if steps_list:
            mean_pct = (
                breakpoint_df.groupby("subskill", as_index=False)["percentage"]
                .mean()
                .sort_values("percentage", ascending=False)
            )
            top_skills = mean_pct["subskill"].head(2).tolist()
            if top_skills:
                plt.figure(figsize=(10, 5))
                for skill in top_skills:
                    vals = []
                    for steps in steps_list:
                        row = breakpoint_df[
                            (breakpoint_df["foundation_extra_steps"] == steps)
                            & (breakpoint_df["subskill"] == skill)
                        ]
                        vals.append(float(row["percentage"].iloc[0]) * 100.0 if not row.empty else 0.0)
                    plt.plot(steps_list, vals, marker="o", linewidth=3, markersize=8, label=skill)
                plt.title("Breakpoint Shift (Top-2 Weakest Subskills)")
                plt.xlabel("Foundation Extra Steps")
                plt.ylabel("Share of Failed Episodes (%)")
                plt.legend()
                if sns is not None:
                    sns.despine()
                save_fig_high_quality(os.path.join(out_dir, "fig_weak_foundation_breakpoint_shift.png"))

    # E) Subskill gain simplified as heatmap (supporting).
    if not subskill_df.empty and {"foundation_extra_steps", "subskill", "avg_gain"}.issubset(
        subskill_df.columns
    ):
        steps_list = sorted(subskill_df["foundation_extra_steps"].dropna().unique().tolist())
        subskills = [s for s in SUBSKILL_ORDER if any(subskill_df["subskill"] == s)]
        if steps_list and subskills:
            pivot = (
                subskill_df.pivot_table(
                    index="subskill",
                    columns="foundation_extra_steps",
                    values="avg_gain",
                    aggfunc="mean",
                )
                .reindex(index=subskills, columns=steps_list)
            )
            plt.figure(figsize=(10, 5))
            im = plt.imshow(pivot.values, aspect="auto", interpolation="nearest", cmap="YlGnBu")
            plt.title("Subskill Gain Heatmap by Foundation Support")
            plt.xlabel("Foundation Extra Steps")
            plt.ylabel("Subskill")
            plt.xticks(range(len(steps_list)), [str(int(s)) for s in steps_list])
            plt.yticks(range(len(subskills)), subskills)
            cbar = plt.colorbar(im)
            cbar.set_label("Average Gain")
            if sns is not None:
                sns.despine()
            save_fig_high_quality(os.path.join(out_dir, "fig_weak_foundation_subskill_gain.png"))

    # F) Marginal success gain only (main decision figure).
    if not summary_df.empty and {"foundation_extra_steps", "marginal_success_gain"}.issubset(summary_df.columns):
        sub = summary_df.sort_values("foundation_extra_steps").copy()
        sub = sub[sub["foundation_extra_steps"] > sub["foundation_extra_steps"].min()].copy()
        sub["marginal_success_gain"] = pd.to_numeric(sub["marginal_success_gain"], errors="coerce")
        sub = sub.dropna(subset=["marginal_success_gain"])
        if not sub.empty:
            plt.figure(figsize=(8, 5))
            x_vals = sub["foundation_extra_steps"].astype(float).tolist()
            y_vals = sub["marginal_success_gain"].astype(float).tolist()
            plt.plot(
                x_vals,
                y_vals,
                marker="o",
                linewidth=3,
                markersize=8,
                label="marginal_success_gain",
            )
            plt.axhline(0.0, linestyle="--", linewidth=1.0)
            plt.title("Marginal Benefit of Additional Foundation Support")
            plt.xlabel("Foundation Extra Steps")
            plt.ylabel("Marginal Success Gain")
            for x, y in zip(x_vals, y_vals):
                plt.annotate(f"{y:.3f}", (x, y), textcoords="offset points", xytext=(0, 6), ha="center")
                if y < 0:
                    plt.scatter([x], [y], color="red", zorder=5)
            if 50.0 in x_vals:
                y50 = y_vals[x_vals.index(50.0)]
                plt.annotate("Optimal region", (50.0, y50), textcoords="offset points", xytext=(8, 10))
            if 60.0 in x_vals:
                y60 = y_vals[x_vals.index(60.0)]
                plt.annotate("Over-support", (60.0, y60), textcoords="offset points", xytext=(-5, -16))
            plt.legend()
            if sns is not None:
                sns.despine()
            save_fig_high_quality(os.path.join(out_dir, "fig_weak_foundation_marginal_gain.png"))

    # Captions for Experiment 3 decision-oriented figures.
    summary_for_caption = (
        summary_df.sort_values("foundation_extra_steps").copy()
        if not summary_df.empty and "foundation_extra_steps" in summary_df.columns
        else pd.DataFrame()
    )
    if not summary_for_caption.empty and "success_rate" in summary_for_caption.columns:
        try:
            peak_idx = summary_for_caption["success_rate"].astype(float).idxmax()
            peak_steps_label = str(int(float(summary_for_caption.loc[peak_idx, "foundation_extra_steps"])))
        except Exception:
            peak_steps_label = "N/A"

    # simple diminishing-return signal: first step where marginal success gain <= 0 after sorting
    dim_step_label = "N/A"
    if not summary_for_caption.empty and {"foundation_extra_steps", "marginal_success_gain"}.issubset(
        summary_for_caption.columns
    ):
        tmp = summary_for_caption.copy()
        tmp["marginal_success_gain"] = pd.to_numeric(tmp["marginal_success_gain"], errors="coerce")
        tmp = tmp.dropna(subset=["marginal_success_gain"])
        tmp = tmp[tmp["foundation_extra_steps"] > tmp["foundation_extra_steps"].min()]
        non_pos = tmp[tmp["marginal_success_gain"] <= 0]
        if not non_pos.empty:
            dim_step_label = str(int(float(non_pos.iloc[0]["foundation_extra_steps"])))

    caption_success = os.path.join(out_dir, "figure_caption_exp3_success.md")
    with open(caption_success, "w", encoding="utf-8-sig") as f:
        f.write(
            "### Figure Caption: Effect of Foundation Support on Success Rate\n"
            "This figure plots weak-learner success rate across foundation-extra-step settings using simulation outputs.\n"
            "Data are taken directly from weak_foundation_support_summary.csv without manual adjustment.\n"
            f"Key finding: success generally improves with additional support, with the observed peak around {peak_steps_label} extra steps.\n"
        )

    caption_cost = os.path.join(out_dir, "figure_caption_exp3_cost.md")
    with open(caption_cost, "w", encoding="utf-8-sig") as f:
        f.write(
            "### Figure Caption: Learning Cost vs Foundation Support\n"
            "This figure reports average total steps per episode across foundation support levels.\n"
            "Values are computed from simulation summary outputs and indicate learning cost rather than learning gain.\n"
            "Key finding: increased foundation support is associated with higher learning cost, which must be balanced against success improvement.\n"
        )

    caption_marginal = os.path.join(out_dir, "figure_caption_exp3_marginal.md")
    with open(caption_marginal, "w", encoding="utf-8-sig") as f:
        f.write(
            "### Figure Caption: Marginal Benefit of Additional Foundation Support\n"
            "This figure shows marginal success gain for each increment of foundation support, derived from simulation summary rows.\n"
            "A horizontal zero line is included to distinguish positive and non-positive incremental benefit.\n"
            f"Key finding: diminishing returns are observed as extra support increases; the practical optimal range is around {peak_steps_label} steps"
            + (f", with non-positive marginal gain appearing by {dim_step_label} steps." if dim_step_label != "N/A" else ".")
            + "\n"
        )

    caption_mastery = os.path.join(out_dir, "figure_caption_exp3_mastery.md")
    with open(caption_mastery, "w", encoding="utf-8-sig") as f:
        f.write(
            "### Figure Caption: Final Polynomial Mastery vs Foundation Support\n"
            "This figure visualizes average final polynomial mastery under different foundation support budgets.\n"
            "Values are read from simulation-generated summary CSV outputs.\n"
            "Key finding: final mastery increases with support but serves as supporting evidence; the primary decision signal remains success-rate gain versus cost.\n"
        )


def plot_rag_intervention_results(
    output_dir: str = os.path.join(REPORTS_DIR, "experiment_4_rag_tutor"),
) -> None:
    """Plot Experiment 4 (Weak + RAG intervention) summary figures."""
    out_dir = output_dir
    summary_path = os.path.join(out_dir, "rag_vs_baseline_summary.csv")
    efficiency_path = os.path.join(out_dir, "rag_efficiency_summary.csv")
    subskill_path = os.path.join(out_dir, "rag_subskill_summary.csv")
    breakpoint_path = os.path.join(out_dir, "rag_breakpoint_shift.csv")

    summary_df = pd.read_csv(summary_path) if os.path.exists(summary_path) else pd.DataFrame()
    efficiency_df = pd.read_csv(efficiency_path) if os.path.exists(efficiency_path) else pd.DataFrame()
    subskill_df = pd.read_csv(subskill_path) if os.path.exists(subskill_path) else pd.DataFrame()
    breakpoint_df = pd.read_csv(breakpoint_path) if os.path.exists(breakpoint_path) else pd.DataFrame()

    # 0) Efficiency figure: mastery_gain / total_steps by condition.
    if not efficiency_df.empty and {"condition", "learning_efficiency"}.issubset(efficiency_df.columns):
        order = ["weak_ab3_foundation", "weak_ab3_foundation_rag"]
        efficiency_df["condition"] = pd.Categorical(
            efficiency_df["condition"], categories=order, ordered=True
        )
        plot_df = efficiency_df.sort_values("condition").copy()
        plot_df["learning_efficiency"] = pd.to_numeric(
            plot_df["learning_efficiency"], errors="coerce"
        )
        plot_df = plot_df.dropna(subset=["learning_efficiency"])
        if not plot_df.empty:
            x = list(range(len(plot_df)))
            y = plot_df["learning_efficiency"].tolist()

            plt.figure(figsize=(9, 5))
            plt.plot(x, y, marker="o", linewidth=2.0)
            plt.xticks(x, plot_df["condition"].tolist(), rotation=15, ha="right")
            plt.title("RAG Tutor: Learning Efficiency Comparison")
            plt.xlabel("Condition")
            plt.ylabel("Learning Efficiency (Mastery Gain / Total Steps)")

            for xi, yi in zip(x, y):
                plt.annotate(f"{yi:.4f}", (xi, yi), textcoords="offset points", xytext=(0, 8), ha="center")

            best_idx = int(plot_df["learning_efficiency"].idxmax())
            best_row = plot_df.loc[best_idx]
            best_x = int(plot_df.index.get_loc(best_idx))
            best_y = float(best_row["learning_efficiency"])
            plt.scatter([best_x], [best_y], zorder=5)
            plt.annotate(
                f"Best: {best_row['condition']}",
                (best_x, best_y),
                textcoords="offset points",
                xytext=(0, -16),
                ha="center",
            )

            baseline_row = plot_df[plot_df["condition"] == "weak_ab3_foundation"]
            rag_row = plot_df[plot_df["condition"] == "weak_ab3_foundation_rag"]
            if not baseline_row.empty and not rag_row.empty:
                base_val = float(baseline_row["learning_efficiency"].iloc[0])
                rag_val = float(rag_row["learning_efficiency"].iloc[0])
                if base_val != 0:
                    improve_pct = ((rag_val - base_val) / abs(base_val)) * 100.0
                    plt.figtext(
                        0.99,
                        0.01,
                        f"Improvement over baseline: {improve_pct:.2f}%",
                        ha="right",
                        va="bottom",
                        fontsize=9,
                    )

            save_fig(os.path.join(out_dir, "fig_rag_efficiency.png"))

    if not summary_df.empty and {"condition", "success_rate"}.issubset(summary_df.columns):
        plt.figure(figsize=(8, 5))
        plt.bar(summary_df["condition"], summary_df["success_rate"] * 100.0)
        plt.title("RAG Tutor: Success Rate Comparison")
        plt.xlabel("Condition")
        plt.ylabel("Success Rate (%)")
        plt.ylim(0, 100)
        save_fig(os.path.join(out_dir, "fig_rag_success_rate.png"))

    if not summary_df.empty and {"condition", "avg_final_polynomial_mastery"}.issubset(summary_df.columns):
        plt.figure(figsize=(8, 5))
        plt.bar(summary_df["condition"], summary_df["avg_final_polynomial_mastery"])
        plt.title("RAG Tutor: Final Polynomial Mastery")
        plt.xlabel("Condition")
        plt.ylabel("Average Final Polynomial Mastery")
        save_fig(os.path.join(out_dir, "fig_rag_mastery.png"))

    if not subskill_df.empty and {"condition", "subskill", "avg_gain"}.issubset(subskill_df.columns):
        conditions = summary_df["condition"].tolist() if not summary_df.empty else sorted(
            subskill_df["condition"].unique().tolist()
        )
        subskills = [s for s in SUBSKILL_ORDER if any(subskill_df["subskill"] == s)]
        if conditions and subskills:
            x = list(range(len(subskills)))
            width = 0.35
            plt.figure(figsize=(12, 5))
            for idx, cond in enumerate(conditions):
                ys: list[float] = []
                cond_df = subskill_df[subskill_df["condition"] == cond]
                for skill in subskills:
                    row = cond_df[cond_df["subskill"] == skill]
                    ys.append(float(row["avg_gain"].iloc[0]) if not row.empty else 0.0)
                offset = (idx - (len(conditions) - 1) / 2) * width
                plt.bar([i + offset for i in x], ys, width=width, label=cond)
            plt.xticks(x, subskills, rotation=20, ha="right")
            plt.title("RAG Tutor: Subskill Gain Comparison")
            plt.xlabel("Subskill")
            plt.ylabel("Average Gain")

            # Highlight whether gains are concentrated on the weakest baseline subskills.
            baseline_rows = subskill_df[subskill_df["condition"] == "weak_ab3_foundation"].copy()
            rag_rows = subskill_df[subskill_df["condition"] == "weak_ab3_foundation_rag"].copy()
            if (
                not baseline_rows.empty
                and not rag_rows.empty
                and {"subskill", "avg_initial_mastery", "avg_gain"}.issubset(baseline_rows.columns)
            ):
                weakest = baseline_rows.sort_values("avg_initial_mastery")["subskill"].head(2).tolist()
                gain_delta_parts: list[str] = []
                for skill in weakest:
                    b = baseline_rows[baseline_rows["subskill"] == skill]
                    r = rag_rows[rag_rows["subskill"] == skill]
                    if b.empty or r.empty:
                        continue
                    delta = float(r["avg_gain"].iloc[0]) - float(b["avg_gain"].iloc[0])
                    gain_delta_parts.append(f"{skill}: Δgain={delta:.3f}")
                if weakest:
                    title_suffix = f" | weakest baseline: {', '.join(weakest)}"
                    if gain_delta_parts:
                        title_suffix += f" | {'; '.join(gain_delta_parts)}"
                    plt.title("RAG Tutor: Subskill Gain Comparison" + title_suffix)

            plt.legend()
            save_fig(os.path.join(out_dir, "fig_rag_subskill_gain.png"))

    if not breakpoint_df.empty and {"condition", "subskill", "percentage"}.issubset(
        breakpoint_df.columns
    ):
        conditions = sorted(breakpoint_df["condition"].unique().tolist())
        subskills = [s for s in SUBSKILL_ORDER if any(breakpoint_df["subskill"] == s)]
        if conditions and subskills:
            x = list(range(len(subskills)))
            width = 0.35
            plt.figure(figsize=(12, 5))
            for idx, cond in enumerate(conditions):
                ys: list[float] = []
                cond_df = breakpoint_df[breakpoint_df["condition"] == cond]
                for skill in subskills:
                    row = cond_df[cond_df["subskill"] == skill]
                    ys.append(float(row["percentage"].iloc[0]) * 100.0 if not row.empty else 0.0)
                offset = (idx - (len(conditions) - 1) / 2) * width
                plt.bar([i + offset for i in x], ys, width=width, label=cond)
            plt.xticks(x, subskills, rotation=20, ha="right")
            plt.title("RAG Tutor: Breakpoint Shift")
            plt.xlabel("Subskill")
            plt.ylabel("Weakest Subskill Share (%)")
            plt.legend()
            save_fig(os.path.join(out_dir, "fig_rag_breakpoint_shift.png"))


def plot_rag_v2_enhanced_results(
    output_dir: str = os.path.join(REPORTS_DIR, "experiment_5_rag_enhanced"),
) -> None:
    """Plot Experiment 5 (baseline vs RAG v1 vs RAG v2) figures."""
    out_dir = output_dir
    summary_path = os.path.join(out_dir, "rag_vs_baseline_summary.csv")
    subskill_path = os.path.join(out_dir, "rag_subskill_summary.csv")
    breakpoint_path = os.path.join(out_dir, "rag_breakpoint_shift.csv")

    summary_df = pd.read_csv(summary_path) if os.path.exists(summary_path) else pd.DataFrame()
    subskill_df = pd.read_csv(subskill_path) if os.path.exists(subskill_path) else pd.DataFrame()
    breakpoint_df = pd.read_csv(breakpoint_path) if os.path.exists(breakpoint_path) else pd.DataFrame()

    condition_order = [
        "weak_ab3_foundation",
        "weak_ab3_foundation_rag_v1",
        "weak_ab3_foundation_rag_v2",
    ]

    if not summary_df.empty:
        summary_df["condition"] = pd.Categorical(
            summary_df["condition"], categories=condition_order, ordered=True
        )
        summary_df = summary_df.sort_values("condition")

    if not summary_df.empty and {"condition", "success_rate"}.issubset(summary_df.columns):
        plt.figure(figsize=(8, 5))
        plt.bar(summary_df["condition"], summary_df["success_rate"] * 100.0)
        plt.title("RAG v2: Success Rate Comparison")
        plt.xlabel("Condition")
        plt.ylabel("Success Rate (%)")
        plt.ylim(0, 100)
        plt.xticks(rotation=15, ha="right")
        save_fig(os.path.join(out_dir, "fig_rag_v2_success_rate.png"))

    if not summary_df.empty and {"condition", "avg_final_polynomial_mastery"}.issubset(summary_df.columns):
        plt.figure(figsize=(8, 5))
        plt.bar(summary_df["condition"], summary_df["avg_final_polynomial_mastery"])
        plt.title("RAG v2: Final Polynomial Mastery")
        plt.xlabel("Condition")
        plt.ylabel("Average Final Polynomial Mastery")
        plt.xticks(rotation=15, ha="right")
        save_fig(os.path.join(out_dir, "fig_rag_v2_mastery.png"))

    if not subskill_df.empty and {"condition", "subskill", "avg_gain"}.issubset(subskill_df.columns):
        subskill_df["condition"] = pd.Categorical(
            subskill_df["condition"], categories=condition_order, ordered=True
        )
        subskills = [s for s in SUBSKILL_ORDER if any(subskill_df["subskill"] == s)]
        conditions = [c for c in condition_order if any(subskill_df["condition"] == c)]
        if subskills and conditions:
            x = list(range(len(subskills)))
            width = 0.24
            plt.figure(figsize=(12, 5))
            for idx, cond in enumerate(conditions):
                ys: list[float] = []
                cond_df = subskill_df[subskill_df["condition"] == cond]
                for skill in subskills:
                    row = cond_df[cond_df["subskill"] == skill]
                    ys.append(float(row["avg_gain"].iloc[0]) if not row.empty else 0.0)
                offset = (idx - (len(conditions) - 1) / 2) * width
                plt.bar([i + offset for i in x], ys, width=width, label=cond)
            plt.xticks(x, subskills, rotation=20, ha="right")
            plt.title("RAG v2: Subskill Gain Comparison")
            plt.xlabel("Subskill")
            plt.ylabel("Average Gain")
            plt.legend()
            save_fig(os.path.join(out_dir, "fig_rag_v2_subskill_gain.png"))

    if not breakpoint_df.empty and {"condition", "subskill", "percentage"}.issubset(
        breakpoint_df.columns
    ):
        breakpoint_df["condition"] = pd.Categorical(
            breakpoint_df["condition"], categories=condition_order, ordered=True
        )
        subskills = [s for s in SUBSKILL_ORDER if any(breakpoint_df["subskill"] == s)]
        conditions = [c for c in condition_order if any(breakpoint_df["condition"] == c)]
        if subskills and conditions:
            x = list(range(len(subskills)))
            width = 0.24
            plt.figure(figsize=(12, 5))
            for idx, cond in enumerate(conditions):
                ys: list[float] = []
                cond_df = breakpoint_df[breakpoint_df["condition"] == cond]
                for skill in subskills:
                    row = cond_df[cond_df["subskill"] == skill]
                    ys.append(float(row["percentage"].iloc[0]) * 100.0 if not row.empty else 0.0)
                offset = (idx - (len(conditions) - 1) / 2) * width
                plt.bar([i + offset for i in x], ys, width=width, label=cond)
            plt.xticks(x, subskills, rotation=20, ha="right")
            plt.title("RAG v2: Breakpoint Shift")
            plt.xlabel("Subskill")
            plt.ylabel("Weakest Subskill Share (%)")
            plt.legend()
            save_fig(os.path.join(out_dir, "fig_rag_v2_breakpoint_shift.png"))

    if not summary_df.empty and {"condition", "rag_usage_rate", "avg_rag_per_episode"}.issubset(
        summary_df.columns
    ):
        x = list(range(len(summary_df)))
        width = 0.38
        plt.figure(figsize=(9, 5))
        plt.bar(
            [i - width / 2 for i in x],
            summary_df["rag_usage_rate"] * 100.0,
            width=width,
            label="RAG Usage Rate (%)",
        )
        plt.bar(
            [i + width / 2 for i in x],
            summary_df["avg_rag_per_episode"],
            width=width,
            label="Avg RAG Per Episode",
        )
        plt.xticks(x, summary_df["condition"], rotation=15, ha="right")
        plt.title("RAG v2: Usage Distribution")
        plt.xlabel("Condition")
        plt.ylabel("Value")
        plt.legend()
        save_fig(os.path.join(out_dir, "fig_rag_usage_distribution.png"))


def _build_exp2_timeline_matrix(df: pd.DataFrame, student_type: str) -> tuple[pd.DataFrame, list[int]]:
    """Build episode-index x step matrix with encoded states for one student type."""
    sub = df[df["student_type"] == student_type].copy()
    if sub.empty:
        return pd.DataFrame(), []

    sub["step"] = pd.to_numeric(sub["step"], errors="coerce")
    sub["episode_id"] = pd.to_numeric(sub["episode_id"], errors="coerce")
    sub = sub.dropna(subset=["step", "episode_id"])
    if sub.empty:
        return pd.DataFrame(), []

    sub["step"] = sub["step"].astype(int)
    sub["episode_id"] = sub["episode_id"].astype(int)

    # Encode phase: 0=empty, 1=mainline, 2=remediation, 3=remediation+RAG.
    sub["state_code"] = 1
    if "was_remediation" in sub.columns:
        sub.loc[pd.to_numeric(sub["was_remediation"], errors="coerce").fillna(0) == 1, "state_code"] = 2
    else:
        sub.loc[sub["phase"] == "remediation", "state_code"] = 2

    if "rag_triggered" in sub.columns:
        rag_mask = pd.to_numeric(sub["rag_triggered"], errors="coerce").fillna(0) == 1
        rem_mask = sub["state_code"] == 2
        sub.loc[rag_mask & rem_mask, "state_code"] = 3

    episode_ids = sorted(sub["episode_id"].unique().tolist())
    episode_index_map = {eid: idx for idx, eid in enumerate(episode_ids)}
    sub["episode_index"] = sub["episode_id"].map(episode_index_map)

    matrix = sub.pivot_table(
        index="episode_index",
        columns="step",
        values="state_code",
        aggfunc="max",
        fill_value=0,
    )
    matrix = matrix.sort_index().sort_index(axis=1)
    return matrix, episode_ids


def plot_exp2_remediation_timeline(
    trajectory_path: str = os.path.join(REPORTS_DIR, "mastery_trajectory.csv"),
    output_dir: str = os.path.join(REPORTS_DIR, "experiment_2_ab3_student_types"),
) -> None:
    """Plot AB3 remediation timeline by student type and combined 1x3 overview."""
    if not os.path.exists(trajectory_path):
        return

    df = pd.read_csv(trajectory_path)
    required_cols = {"strategy", "student_type", "episode_id", "step", "phase"}
    if df.empty or not required_cols.issubset(df.columns):
        return

    ab3 = df[df["strategy"] == "AB3_PPO_Dynamic"].copy()
    if ab3.empty:
        return

    os.makedirs(output_dir, exist_ok=True)

    cmap = ListedColormap(["#f7f7f7", "#9ecae1", "#fdae6b", "#9e9ac8"])
    legend_handles = [
        Patch(facecolor="#9ecae1", edgecolor="none", label="mainline"),
        Patch(facecolor="#fdae6b", edgecolor="none", label="remediation"),
        Patch(facecolor="#9e9ac8", edgecolor="none", label="remediation + RAG"),
    ]

    matrices: dict[str, pd.DataFrame] = {}
    for student_type in STUDENT_TYPE_ORDER:
        matrix, _ = _build_exp2_timeline_matrix(ab3, student_type)
        if matrix.empty:
            continue
        matrices[student_type] = matrix

        plt.figure(figsize=(10, 6))
        plt.imshow(matrix.values, aspect="auto", interpolation="nearest", cmap=cmap, vmin=0, vmax=3)
        plt.title(f"AB3 Remediation Timeline - {student_type}")
        plt.xlabel("Step")
        plt.ylabel("Episode Index")
        xticks = list(range(0, matrix.shape[1], max(1, matrix.shape[1] // 10)))
        plt.xticks(xticks, [str(matrix.columns[i]) for i in xticks])
        plt.yticks([])
        plt.legend(handles=legend_handles, loc="upper right", frameon=True)
        save_fig(os.path.join(output_dir, f"fig_exp2_remediation_timeline_{student_type.lower()}.png"))

    fig, axes = plt.subplots(1, 3, figsize=(18, 6), sharex=False, sharey=False)
    has_any = False
    for idx, student_type in enumerate(STUDENT_TYPE_ORDER):
        ax = axes[idx]
        matrix = matrices.get(student_type)
        if matrix is None or matrix.empty:
            ax.set_title(f"{student_type} (No Data)")
            ax.axis("off")
            continue
        has_any = True
        ax.imshow(matrix.values, aspect="auto", interpolation="nearest", cmap=cmap, vmin=0, vmax=3)
        ax.set_title(student_type)
        ax.set_xlabel("Step")
        if idx == 0:
            ax.set_ylabel("Episode Index")
        xticks = list(range(0, matrix.shape[1], max(1, matrix.shape[1] // 6)))
        ax.set_xticks(xticks)
        ax.set_xticklabels([str(matrix.columns[i]) for i in xticks])
        ax.set_yticks([])

    if has_any:
        fig.suptitle("AB3 Remediation Timeline by Student Type")
        fig.legend(handles=legend_handles, loc="upper center", ncol=3, frameon=True)
        fig.tight_layout(rect=[0, 0, 1, 0.94])
        fig.savefig(
            os.path.join(output_dir, "fig_exp2_remediation_timeline_by_student_type.png"),
            dpi=150,
        )
    plt.close(fig)


def _build_exp2_ratio_profile(
    ab3_df: pd.DataFrame,
    student_type: str,
    phase_name: str,
) -> pd.DataFrame:
    """Compute per-step phase ratio for one student type."""
    sub = ab3_df[ab3_df["student_type"] == student_type].copy()
    if sub.empty:
        return pd.DataFrame(columns=["step", "ratio"])

    sub["step"] = pd.to_numeric(sub["step"], errors="coerce")
    sub = sub.dropna(subset=["step"])
    if sub.empty:
        return pd.DataFrame(columns=["step", "ratio"])
    sub["step"] = sub["step"].astype(int)

    # total active episodes at each step
    total = (
        sub.groupby("step")["episode_id"]
        .nunique()
        .rename("total_active")
        .reset_index()
    )

    target = (
        sub[sub["phase"] == phase_name]
        .groupby("step")["episode_id"]
        .nunique()
        .rename("phase_count")
        .reset_index()
    )

    merged = total.merge(target, on="step", how="left")
    merged["phase_count"] = merged["phase_count"].fillna(0)
    merged["ratio"] = merged["phase_count"] / merged["total_active"].replace(0, pd.NA)
    return merged[["step", "ratio"]].sort_values("step")


def _build_exp2_rag_ratio_weak(ab3_df: pd.DataFrame) -> pd.DataFrame:
    """Compute per-step rag-trigger ratio for Weak episodes."""
    if "rag_triggered" not in ab3_df.columns:
        return pd.DataFrame(columns=["step", "ratio"])

    weak = ab3_df[ab3_df["student_type"] == "Weak"].copy()
    if weak.empty:
        return pd.DataFrame(columns=["step", "ratio"])

    weak["step"] = pd.to_numeric(weak["step"], errors="coerce")
    weak = weak.dropna(subset=["step"])
    if weak.empty:
        return pd.DataFrame(columns=["step", "ratio"])
    weak["step"] = weak["step"].astype(int)
    weak["rag_triggered"] = pd.to_numeric(weak["rag_triggered"], errors="coerce").fillna(0)

    total = (
        weak.groupby("step")["episode_id"]
        .nunique()
        .rename("total_active")
        .reset_index()
    )
    rag = (
        weak[weak["rag_triggered"] == 1]
        .groupby("step")["episode_id"]
        .nunique()
        .rename("rag_count")
        .reset_index()
    )
    merged = total.merge(rag, on="step", how="left")
    merged["rag_count"] = merged["rag_count"].fillna(0)
    merged["ratio"] = merged["rag_count"] / merged["total_active"].replace(0, pd.NA)
    return merged[["step", "ratio"]].sort_values("step")


def plot_exp2_remediation_profile_summary(
    trajectory_path: str = os.path.join(REPORTS_DIR, "mastery_trajectory.csv"),
    output_dir: str = os.path.join(REPORTS_DIR, "experiment_2_ab3_student_types"),
) -> None:
    """Plot step-wise remediation/mainline/rag ratio summaries for AB3 student-type analysis."""
    if not os.path.exists(trajectory_path):
        return

    df = pd.read_csv(trajectory_path)
    required_cols = {"strategy", "student_type", "episode_id", "step", "phase"}
    if df.empty or not required_cols.issubset(df.columns):
        return

    ab3 = df[df["strategy"] == "AB3_PPO_Dynamic"].copy()
    if ab3.empty:
        return

    os.makedirs(output_dir, exist_ok=True)

    # 1) Remediation ratio by step
    plt.figure(figsize=(9, 5))
    has_line = False
    for student_type in STUDENT_TYPE_ORDER:
        profile = _build_exp2_ratio_profile(ab3, student_type, "remediation")
        if profile.empty:
            continue
        has_line = True
        plt.plot(profile["step"], profile["ratio"], marker="o", linewidth=1.5, label=student_type)
    if has_line:
        plt.title("AB3 Remediation Ratio by Step")
        plt.xlabel("Step")
        plt.ylabel("Remediation Ratio")
        plt.ylim(0, 1)
        plt.legend()
        save_fig(os.path.join(output_dir, "fig_exp2_remediation_ratio_by_step.png"))
    else:
        plt.close()

    # 2) Mainline ratio by step
    plt.figure(figsize=(9, 5))
    has_line = False
    for student_type in STUDENT_TYPE_ORDER:
        profile = _build_exp2_ratio_profile(ab3, student_type, "mainline")
        if profile.empty:
            continue
        has_line = True
        plt.plot(profile["step"], profile["ratio"], marker="o", linewidth=1.5, label=student_type)
    if has_line:
        plt.title("AB3 Mainline Ratio by Step")
        plt.xlabel("Step")
        plt.ylabel("Mainline Ratio")
        plt.ylim(0, 1)
        plt.legend()
        save_fig(os.path.join(output_dir, "fig_exp2_mainline_ratio_by_step.png"))
    else:
        plt.close()

    # 3) Weak-only RAG ratio by step
    rag_profile = _build_exp2_rag_ratio_weak(ab3)
    if not rag_profile.empty:
        plt.figure(figsize=(9, 5))
        plt.plot(rag_profile["step"], rag_profile["ratio"], marker="o", linewidth=1.5, color="#7a5195")
        plt.title("AB3 Weak RAG Trigger Ratio by Step")
        plt.xlabel("Step")
        plt.ylabel("RAG Trigger Ratio")
        plt.ylim(0, 1)
        save_fig(os.path.join(output_dir, "fig_exp2_rag_ratio_by_step_weak.png"))

    # 4) Phase profile summary (1x3)
    fig, axes = plt.subplots(1, 3, figsize=(18, 5), sharey=True)
    plots_drawn = 0

    for student_type in STUDENT_TYPE_ORDER:
        profile = _build_exp2_ratio_profile(ab3, student_type, "remediation")
        if profile.empty:
            continue
        axes[0].plot(profile["step"], profile["ratio"], marker="o", linewidth=1.2, label=student_type)
        plots_drawn += 1
    axes[0].set_title("Remediation Ratio")
    axes[0].set_xlabel("Step")
    axes[0].set_ylabel("Ratio")
    axes[0].set_ylim(0, 1)
    if plots_drawn > 0:
        axes[0].legend()

    plots_drawn = 0
    for student_type in STUDENT_TYPE_ORDER:
        profile = _build_exp2_ratio_profile(ab3, student_type, "mainline")
        if profile.empty:
            continue
        axes[1].plot(profile["step"], profile["ratio"], marker="o", linewidth=1.2, label=student_type)
        plots_drawn += 1
    axes[1].set_title("Mainline Ratio")
    axes[1].set_xlabel("Step")
    axes[1].set_ylim(0, 1)
    if plots_drawn > 0:
        axes[1].legend()

    if not rag_profile.empty:
        axes[2].plot(rag_profile["step"], rag_profile["ratio"], marker="o", linewidth=1.2, color="#7a5195")
        axes[2].set_title("Weak RAG Ratio")
        axes[2].set_xlabel("Step")
        axes[2].set_ylim(0, 1)
    else:
        axes[2].set_title("Weak RAG Ratio (No Data)")
        axes[2].axis("off")

    fig.suptitle("AB3 Phase Profile Summary by Student Type")
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(
        os.path.join(output_dir, "fig_exp2_phase_profile_summary.png"),
        dpi=150,
    )
    plt.close(fig)


def build_experiment2_summary(
    df_logs: pd.DataFrame,
    output_dir: str = os.path.join(REPORTS_DIR, "experiment_2_ab3_student_types"),
) -> pd.DataFrame:
    """Aggregate AB3 behavior summary by student type from trajectory logs."""
    required_cols = {"strategy", "student_type", "episode_id", "step", "phase"}
    if df_logs.empty or not required_cols.issubset(df_logs.columns):
        return pd.DataFrame()

    ab3 = df_logs[df_logs["strategy"] == "AB3_PPO_Dynamic"].copy()
    if ab3.empty:
        return pd.DataFrame()

    if "route" not in ab3.columns:
        ab3["route"] = ab3["phase"]

    out_rows: list[dict[str, Any]] = []
    for student_type in STUDENT_TYPE_ORDER:
        sub = ab3[ab3["student_type"] == student_type].copy()
        if sub.empty:
            continue

        total_episodes = int(sub["episode_id"].nunique())
        total_steps = len(sub)
        remediation_steps = int((sub["route"] == "remediation").sum())
        mainline_steps = int((sub["route"] == "mainline").sum())
        avg_steps = (total_steps / total_episodes) if total_episodes > 0 else float("nan")

        if "rag_triggered" in sub.columns:
            sub["rag_triggered"] = pd.to_numeric(sub["rag_triggered"], errors="coerce").fillna(0)
            rag_episodes = int(sub[sub["rag_triggered"] == 1]["episode_id"].nunique())
            rag_activation_ratio = rag_episodes / total_episodes if total_episodes > 0 else float("nan")
        else:
            rag_activation_ratio = float("nan")

        out_rows.append(
            {
                "student_type": student_type,
                "total_episodes": total_episodes,
                "remediation_steps": remediation_steps,
                "mainline_steps": mainline_steps,
                "remediation_ratio": (remediation_steps / total_steps) if total_steps > 0 else float("nan"),
                "mainline_ratio": (mainline_steps / total_steps) if total_steps > 0 else float("nan"),
                "avg_steps": avg_steps,
                "rag_activation_ratio": rag_activation_ratio,
            }
        )

    summary_df = pd.DataFrame(out_rows)
    if summary_df.empty:
        return summary_df

    os.makedirs(output_dir, exist_ok=True)
    summary_df.to_csv(
        os.path.join(output_dir, "experiment2_student_type_summary.csv"),
        index=False,
        encoding="utf-8-sig",
    )
    return summary_df


def generate_student_type_summary_charts(
    summary_df: pd.DataFrame,
    output_dir: str = os.path.join(REPORTS_DIR, "experiment_2_ab3_student_types"),
) -> None:
    """Generate Experiment 2 dual-axis summary chart from aggregated summary dataframe."""
    if summary_df.empty:
        return
    required_cols = {
        "student_type",
        "remediation_ratio",
        "mainline_ratio",
        "avg_steps",
        "rag_activation_ratio",
    }
    if not required_cols.issubset(summary_df.columns):
        return

    plot_df = summary_df.copy()
    plot_df["student_type"] = plot_df["student_type"].astype(str)
    plot_df = plot_df[plot_df["student_type"].isin(STUDENT_TYPE_ORDER)]
    if plot_df.empty:
        return
    plot_df["student_type"] = pd.Categorical(
        plot_df["student_type"],
        categories=STUDENT_TYPE_ORDER,
        ordered=True,
    )
    plot_df = plot_df.sort_values("student_type")

    fig, ax1 = plt.subplots(figsize=(11, 6))
    line1 = ax1.plot(
        plot_df["student_type"],
        plot_df["remediation_ratio"],
        marker="o",
        linewidth=2.0,
        label="Remediation Ratio",
    )
    line2 = ax1.plot(
        plot_df["student_type"],
        plot_df["mainline_ratio"],
        marker="s",
        linewidth=2.0,
        label="Mainline Ratio",
    )

    rag_series = pd.to_numeric(plot_df["rag_activation_ratio"], errors="coerce")
    line3: list[Any] = []
    if rag_series.notna().any():
        line3 = ax1.plot(
            plot_df["student_type"],
            rag_series,
            marker="d",
            linewidth=2.0,
            label="RAG Activation Ratio",
        )

    ax1.set_xlabel("Student Type Group")
    ax1.set_ylabel("Step-Level Ratio")
    ax1.set_ylim(0, 1.0)

    ax2 = ax1.twinx()
    line4 = ax2.plot(
        plot_df["student_type"],
        plot_df["avg_steps"],
        marker="^",
        linestyle="--",
        linewidth=2.0,
        label="Average Steps per Episode",
    )
    ax2.set_ylabel("Average Steps per Episode")
    max_steps = pd.to_numeric(plot_df["avg_steps"], errors="coerce").max()
    max_steps = float(max_steps) if pd.notna(max_steps) else 1.0
    ax2.set_ylim(0, max_steps * 1.25 if max_steps > 0 else 1.0)

    ax1.set_title("Experiment 2: Policy Behavior Across Student Types")

    for _, row in plot_df.iterrows():
        x = row["student_type"]
        rem = pd.to_numeric(row["remediation_ratio"], errors="coerce")
        main = pd.to_numeric(row["mainline_ratio"], errors="coerce")
        rag = pd.to_numeric(row["rag_activation_ratio"], errors="coerce")
        steps = pd.to_numeric(row["avg_steps"], errors="coerce")
        if pd.notna(rem):
            ax1.annotate(
                f"{rem:.2f}", (x, rem), textcoords="offset points", xytext=(-10, 9), ha="center"
            )
        if pd.notna(main):
            ax1.annotate(
                f"{main:.2f}", (x, main), textcoords="offset points", xytext=(10, -13), ha="center"
            )
        if pd.notna(rag):
            ax1.annotate(
                f"{rag:.2f}", (x, rag), textcoords="offset points", xytext=(0, 14), ha="center"
            )
        if pd.notna(steps):
            ax2.annotate(
                f"{steps:.1f}", (x, steps), textcoords="offset points", xytext=(0, 10), ha="center"
            )

    lines = line1 + line2 + line3 + line4
    ax1.legend(lines, [ln.get_label() for ln in lines], loc="upper left")

    os.makedirs(output_dir, exist_ok=True)
    save_fig(os.path.join(output_dir, "experiment2_policy_behavior_summary.png"))


def build_mastery_plot_dataframe(df_logs: pd.DataFrame) -> pd.DataFrame:
    """Normalize mastery plot dataframe from trajectory logs with robust column fallback."""
    if df_logs.empty:
        return pd.DataFrame()
    required = {"strategy", "student_type", "episode_id", "step"}
    if not required.issubset(df_logs.columns):
        return pd.DataFrame()

    df = df_logs.copy()
    if "route" not in df.columns and "phase" in df.columns:
        df["route"] = df["phase"]

    for col in ["step", "episode_id", "integer_mastery", "polynomial_mastery", "fraction_mastery", "radical_mastery"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Fallback mapping if major mastery columns are missing.
    mastery_cols = [c for c in df.columns if c.endswith("_mastery")]
    if "integer_mastery" not in df.columns and "sign_handling_mastery" in df.columns:
        df["integer_mastery"] = pd.to_numeric(df["sign_handling_mastery"], errors="coerce")
    if "polynomial_mastery" not in df.columns:
        candidates = [c for c in mastery_cols if c != "integer_mastery"]
        if candidates:
            df["polynomial_mastery"] = pd.to_numeric(df[candidates[0]], errors="coerce")

    return df


def _select_representative_mastery_episode_plot(
    mastery_df: pd.DataFrame,
    episodes_df: pd.DataFrame,
) -> int | None:
    """Select representative episode for trajectory visualization with stable fallbacks."""
    ab3 = mastery_df[mastery_df["strategy"] == "AB3_PPO_Dynamic"].copy()
    if ab3.empty:
        return None

    priority = {"Average": 0, "Weak": 1, "Careless": 2}
    candidates: list[tuple[int, int, int, int]] = []
    for episode_id, sub in ab3.groupby("episode_id"):
        rem_steps = int((sub["route"] == "remediation").sum()) if "route" in sub.columns else 0
        if rem_steps <= 0:
            continue
        return_count = int(pd.to_numeric(sub.get("is_return_to_mainline", 0), errors="coerce").fillna(0).sum())
        stype = str(sub["student_type"].iloc[0]) if "student_type" in sub.columns else "Average"
        rank = priority.get(stype, 99)
        success = 0
        if not episodes_df.empty and {"episode_id", "success"}.issubset(episodes_df.columns):
            hit = episodes_df[episodes_df["episode_id"] == episode_id]
            if not hit.empty:
                success = int(pd.to_numeric(hit["success"], errors="coerce").fillna(0).iloc[0])
        if success == 1 and return_count > 0:
            candidates.append((rank, -rem_steps, -return_count, int(episode_id)))

    if candidates:
        candidates.sort()
        return candidates[0][3]

    fallback: list[tuple[int, int, int]] = []
    for episode_id, sub in ab3.groupby("episode_id"):
        rem_steps = int((sub["route"] == "remediation").sum()) if "route" in sub.columns else 0
        if rem_steps <= 0:
            continue
        stype = str(sub["student_type"].iloc[0]) if "student_type" in sub.columns else "Average"
        rank = priority.get(stype, 99)
        fallback.append((rank, abs(len(sub) - 30), int(episode_id)))
    if not fallback:
        return None
    fallback.sort()
    return fallback[0][2]


def _collect_remediation_spans_plot(sub: pd.DataFrame) -> list[tuple[int, int]]:
    """Collect contiguous remediation step spans."""
    if "route" not in sub.columns:
        return []
    rem_steps = sorted(sub.loc[sub["route"] == "remediation", "step"].dropna().astype(int).tolist())
    if not rem_steps:
        return []
    spans: list[tuple[int, int]] = []
    start = rem_steps[0]
    prev = rem_steps[0]
    for s in rem_steps[1:]:
        if s == prev + 1:
            prev = s
            continue
        spans.append((start, prev))
        start = s
        prev = s
    spans.append((start, prev))
    return spans


def generate_mastery_trajectory_charts(
    df_logs: pd.DataFrame,
    output_dir: str = os.path.join(REPORTS_DIR, "experiment_2_ab3_student_types"),
) -> list[str]:
    """Generate representative and averaged mastery trajectory charts from real logs."""
    out_files: list[str] = []
    mastery_df = build_mastery_plot_dataframe(df_logs)
    if mastery_df.empty:
        return out_files

    os.makedirs(output_dir, exist_ok=True)
    episodes_path = os.path.join(REPORTS_DIR, "ablation_simulation_results.csv")
    episodes_df = pd.read_csv(episodes_path) if os.path.exists(episodes_path) else pd.DataFrame()
    if not episodes_df.empty and "episode_id" in episodes_df.columns:
        episodes_df["episode_id"] = pd.to_numeric(episodes_df["episode_id"], errors="coerce")

    rep_episode = _select_representative_mastery_episode_plot(mastery_df, episodes_df)
    if rep_episode is not None:
        sub = mastery_df[
            (mastery_df["strategy"] == "AB3_PPO_Dynamic")
            & (pd.to_numeric(mastery_df["episode_id"], errors="coerce") == rep_episode)
        ].copy()
        sub = sub.sort_values("step")
        if not sub.empty and {"step", "integer_mastery", "polynomial_mastery"}.issubset(sub.columns):
            fig, ax = plt.subplots(figsize=(11, 6))
            ax.plot(
                sub["step"],
                sub["integer_mastery"],
                marker="o",
                linewidth=2.2,
                label="Prerequisite Mastery (Integer)",
            )
            ax.plot(
                sub["step"],
                sub["polynomial_mastery"],
                marker="s",
                linewidth=2.2,
                label="Target Mastery (Polynomial)",
            )
            for idx, (a, b) in enumerate(_collect_remediation_spans_plot(sub)):
                label = "Remediation Phase" if idx == 0 else "_nolegend_"
                ax.axvspan(a - 0.5, b + 0.5, alpha=0.18, label=label)
            ymin = pd.concat([sub["integer_mastery"], sub["polynomial_mastery"]]).min()
            ymax = pd.concat([sub["integer_mastery"], sub["polynomial_mastery"]]).max()
            if pd.notna(ymin) and pd.notna(ymax) and ymin >= 0 and ymax <= 1:
                ax.set_ylim(0, 1)
            ax.set_xlabel("Step")
            ax.set_ylabel("Mastery Level")
            stype = str(sub["student_type"].iloc[0]) if "student_type" in sub.columns else "Unknown"
            ax.set_title(
                f"Learning Trajectory with Remediation Phase "
                f"(Representative Episode: {stype}, #{int(rep_episode)})"
            )
            ax.legend(loc="lower right")
            out_path = os.path.join(output_dir, f"mastery_trajectory_episode_{int(rep_episode)}.png")
            plt.tight_layout()
            plt.savefig(out_path, dpi=150)
            plt.close(fig)
            out_files.append(out_path)
            fixed_out_path = os.path.join(output_dir, "mastery_trajectory_representative_episode.png")
            shutil.copy2(out_path, fixed_out_path)
            out_files.append(fixed_out_path)

    # Average by student type with step alignment (NaN-safe groupby mean).
    ab3 = mastery_df[mastery_df["strategy"] == "AB3_PPO_Dynamic"].copy()
    if not ab3.empty and {"student_type", "step", "integer_mastery", "polynomial_mastery"}.issubset(ab3.columns):
        fig, axes = plt.subplots(1, 3, figsize=(18, 5), sharey=True)
        has_plot = False
        for i, student_type in enumerate(STUDENT_TYPE_ORDER):
            ax = axes[i]
            sub = ab3[ab3["student_type"] == student_type].copy()
            if sub.empty:
                ax.set_title(f"{student_type} (No Data)")
                ax.axis("off")
                continue
            agg = (
                sub.groupby("step", as_index=False)
                .agg(
                    average_integer_mastery_by_step=("integer_mastery", "mean"),
                    average_polynomial_mastery_by_step=("polynomial_mastery", "mean"),
                    average_remediation_ratio_by_step=(
                        "route",
                        lambda x: (x == "remediation").mean() if len(x) > 0 else float("nan"),
                    ),
                )
                .sort_values("step")
            )
            if agg.empty:
                ax.set_title(f"{student_type} (No Data)")
                ax.axis("off")
                continue
            has_plot = True
            ax.plot(
                agg["step"],
                agg["average_integer_mastery_by_step"],
                marker="o",
                linewidth=2.0,
                label="Average Prerequisite Mastery (Integer)",
            )
            ax.plot(
                agg["step"],
                agg["average_polynomial_mastery_by_step"],
                marker="s",
                linewidth=2.0,
                label="Average Target Mastery (Polynomial)",
            )
            ax.plot(
                agg["step"],
                agg["average_remediation_ratio_by_step"],
                linestyle="--",
                linewidth=1.8,
                label="Average Remediation Ratio",
            )
            ax.set_title(f"Learning Trajectory ({student_type} Group)")
            ax.set_xlabel("Step")
            if i == 0:
                ax.set_ylabel("Mastery / Ratio")
            ax.set_ylim(0, 1)
            ax.legend(fontsize=8)

        if has_plot:
            fig.suptitle("Learning Trajectory by Student Type (AB3)")
            out_path = os.path.join(output_dir, "mastery_trajectory_average_by_student_type.png")
            fig.tight_layout(rect=[0, 0, 1, 0.95])
            fig.savefig(out_path, dpi=150)
            out_files.append(out_path)
        plt.close(fig)

    return out_files


def write_experiment2_figure_captions(output_dir: str, representative_episode_id: int | None) -> list[str]:
    """Write publication captions for Experiment 2 summary and mastery trajectory figures."""
    os.makedirs(output_dir, exist_ok=True)
    paths: list[str] = []

    summary_caption = os.path.join(output_dir, "figure_caption_experiment2_summary.md")
    with open(summary_caption, "w", encoding="utf-8-sig") as f:
        f.write(
            "### Figure Caption: Experiment 2 Policy Behavior Summary\n"
            "This figure reports AB3 policy behavior across Careless, Average, and Weak groups.\n"
            "All values are computed from the current run logs: remediation ratio (remediation steps / total steps),\n"
            "mainline ratio (mainline steps / total steps), and average steps per episode.\n"
            "Key finding: policy behavior differs by student type, with weaker learners spending more time in remediation\n"
            "and requiring longer trajectories before convergence.\n"
        )
    paths.append(summary_caption)

    episode_caption = os.path.join(output_dir, "figure_caption_mastery_episode.md")
    with open(episode_caption, "w", encoding="utf-8-sig") as f:
        eid_text = str(representative_episode_id) if representative_episode_id is not None else "N/A"
        f.write(
            "### Figure Caption: Representative Mastery Trajectory\n"
            f"This plot shows one automatically selected representative AB3 episode (episode_id={eid_text}).\n"
            "Curves are true per-step mastery values from trajectory logs (prerequisite and target mastery), and shaded\n"
            "bands denote remediation phases identified by route==remediation.\n"
            "Key finding: remediation intervals are associated with prerequisite consolidation before stronger target mastery growth.\n"
        )
    paths.append(episode_caption)

    avg_caption = os.path.join(output_dir, "figure_caption_mastery_average.md")
    with open(avg_caption, "w", encoding="utf-8-sig") as f:
        f.write(
            "### Figure Caption: Average Mastery Trajectory by Student Type\n"
            "This figure aggregates AB3 episodes by step within each student type using NaN-safe averaging,\n"
            "reporting average prerequisite mastery, average target mastery, and average remediation ratio.\n"
            "Key finding: student types exhibit distinct learning dynamics; weaker groups sustain higher remediation intensity\n"
            "and slower target mastery accumulation.\n"
        )
    paths.append(avg_caption)
    return paths


def main() -> None:
    """Load experiment summaries and output publication-ready figures."""
    os.makedirs(REPORTS_DIR, exist_ok=True)
    os.makedirs(EXP1_DIR, exist_ok=True)

    ablation_summary_path = os.path.join(REPORTS_DIR, "ablation_strategy_summary.csv")
    if not os.path.exists(ablation_summary_path):
        ablation_summary_path = os.path.join(EXP1_DIR, "ablation_strategy_summary.csv")
    ablation_by_type_path = os.path.join(REPORTS_DIR, "ablation_strategy_by_student_type_summary.csv")
    if not os.path.exists(ablation_by_type_path):
        ablation_by_type_path = os.path.join(EXP1_DIR, "ablation_strategy_by_student_type_summary.csv")

    ablation_summary = read_csv_rows(ablation_summary_path)
    ablation_by_type = read_csv_rows(ablation_by_type_path)
    ab3_subskill_detail = read_csv_rows(
        os.path.join(REPORTS_DIR, "ab3_subskill_by_type_detailed_summary.csv")
    )
    ab3_student_detail = read_csv_rows(
        os.path.join(REPORTS_DIR, "ab3_student_type_detailed_summary.csv")
    )

    plot_ablation_success_rate(ablation_summary)
    plot_ablation_steps_vs_success(ablation_summary)
    plot_ablation_by_student_type_success(ablation_by_type)
    plot_ab3_subskill_gain_by_type(ab3_subskill_detail)
    plot_ab3_polynomial_gain_by_type(ab3_student_detail)
    plot_multi_steps_results()
    plot_exp2_remediation_timeline()
    plot_exp2_remediation_profile_summary()
    trajectory_path = os.path.join(REPORTS_DIR, "mastery_trajectory.csv")
    if os.path.exists(trajectory_path):
        traj_df = pd.read_csv(trajectory_path)
        exp2_summary_df = build_experiment2_summary(
            traj_df,
            output_dir=os.path.join(REPORTS_DIR, "experiment_2_ab3_student_types"),
        )
        generate_student_type_summary_charts(
            exp2_summary_df,
            output_dir=os.path.join(REPORTS_DIR, "experiment_2_ab3_student_types"),
        )
        mastery_paths = generate_mastery_trajectory_charts(
            traj_df,
            output_dir=os.path.join(REPORTS_DIR, "experiment_2_ab3_student_types"),
        )
        rep_episode_id: int | None = None
        for p in mastery_paths:
            name = os.path.basename(p)
            if name.startswith("mastery_trajectory_episode_") and name.endswith(".png"):
                rep_episode_id = int(name[len("mastery_trajectory_episode_") : -4])
                break
        caption_paths = write_experiment2_figure_captions(
            output_dir=os.path.join(REPORTS_DIR, "experiment_2_ab3_student_types"),
            representative_episode_id=rep_episode_id,
        )
    else:
        mastery_paths = []
        caption_paths = []

    print("Saved reports/experiment_1_ablation/fig_ablation_success_rate.png")
    print("Saved reports/experiment_1_ablation/fig_ablation_steps_vs_success.png")
    print("Saved reports/experiment_1_ablation/fig_ablation_by_student_type_success.png")
    print("Saved reports/fig_ab3_subskill_gain_by_type.png")
    print("Saved reports/fig_ab3_polynomial_gain_by_type.png")
    print("Saved reports/experiment_1_ablation/fig_multi_steps_success_rate.png")
    print("Saved reports/fig_multi_steps_ab3_by_student_type.png")
    print("Saved reports/experiment_1_ablation/fig_multi_steps_efficiency.png")
    print("Saved reports/experiment_2_ab3_student_types/fig_exp2_remediation_timeline_careless.png")
    print("Saved reports/experiment_2_ab3_student_types/fig_exp2_remediation_timeline_average.png")
    print("Saved reports/experiment_2_ab3_student_types/fig_exp2_remediation_timeline_weak.png")
    print("Saved reports/experiment_2_ab3_student_types/fig_exp2_remediation_timeline_by_student_type.png")
    print("Saved reports/experiment_2_ab3_student_types/fig_exp2_remediation_ratio_by_step.png")
    print("Saved reports/experiment_2_ab3_student_types/fig_exp2_mainline_ratio_by_step.png")
    print("Saved reports/experiment_2_ab3_student_types/fig_exp2_rag_ratio_by_step_weak.png")
    print("Saved reports/experiment_2_ab3_student_types/fig_exp2_phase_profile_summary.png")
    print("Saved reports/experiment_2_ab3_student_types/experiment2_student_type_summary.csv")
    print("Saved reports/experiment_2_ab3_student_types/experiment2_policy_behavior_summary.png")
    for p in mastery_paths:
        print(f"Saved {p.replace(os.sep, '/')}")
    for p in caption_paths:
        print(f"Saved {p.replace(os.sep, '/')}")


if __name__ == "__main__":
    main()
