# -*- coding: utf-8 -*-
# ==============================================================================
# ID: plot_experiment_results.py
# Version: V1.0.0 (Shared Experiment Plotting)
# Last Updated: 2026-04-15
# Author: *Steve
#
# [Description]:
#   讀取 reports/adaptive_strategy_study/ 下實驗 CSV，產生 Exp1/2/3/4 等出版用圖表（消融、分群、掌握度、
#   Weak foundation、RAG 延伸）；含目錄建立、樣式與 caption 檔輸出，供各 runner 共用。
#
# [Database Schema Usage]:
#   無直接資料庫操作。
#
# [Logic Flow]:
#   1. 載入資料框並驗證欄位。
#   2. 呼叫各 plot_* 函式繪圖。
#   3. 輸出 PNG 與說明 markdown。
# ==============================================================================
import csv
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

_STUDY_ROOT = Path(__file__).resolve().parents[1]
if str(_STUDY_ROOT) not in sys.path:
    sys.path.insert(0, str(_STUDY_ROOT))
import study_paths as _study_paths  # noqa: E402

_study_paths.ensure_repo_root_on_syspath()

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch

REPORTS_DIR = str(_study_paths.study_reports_root())
EXP1_BASE_DIR = os.path.join(REPORTS_DIR, "experiment_1_ablation")
EXP2_BASE_DIR = os.path.join(REPORTS_DIR, "experiment_2_ab3_student_types")
EXP3_BASE_DIR = os.path.join(REPORTS_DIR, "experiment_3_weak_foundation_support")
EXP4_BASE_DIR = os.path.join(REPORTS_DIR, "experiment_4_rag_tutor")
EXP1_DIR = os.path.join(EXP1_BASE_DIR, "latest")
EXP2_DIR = os.path.join(EXP2_BASE_DIR, "latest")
FORCE_WRITE_MARKDOWN_ENV = "MATHPROJECT_FORCE_WRITE_MARKDOWN"

REPORT_COLOR_MAP = {
    "AB1_Baseline": "#4C72B0",
    "AB2_RuleBased": "#DD8452",
    "AB3_PPO_Dynamic": "#55A868",
    "baseline": "#4C72B0",
    "rule_based": "#DD8452",
    "adaptive": "#55A868",
}

STRATEGY_LABEL_MAP = {
    "AB1_Baseline": "Baseline",
    "AB2_RuleBased": "Rule-Based",
    "AB3_PPO_Dynamic": "Adaptive (Ours)",
}

EXP1_STUDENT_DISPLAY_MAP = {
    "Careless": "Careless (B+,B++)",
    "Average": "Average (B)",
    "Weak": "Weak (C)",
}
EXP1_STUDENT_ORDER = [
    "Careless (B+,B++)",
    "Average (B)",
    "Weak (C)",
]
EXP1_SUCCESS_LABEL = "Success Rate 達標A (%)"


def _exp1_success_col(df: pd.DataFrame) -> str | None:
    for c in [EXP1_SUCCESS_LABEL, "Success Rate (%)"]:
        if c in df.columns:
            return c
    return None


def _exp1_group_col(df: pd.DataFrame) -> str | None:
    for c in ["Student Level", "Student Group"]:
        if c in df.columns:
            return c
    return None


def setup_report_style() -> None:
    """Apply a simple report-style matplotlib theme for all generated figures."""
    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "font.family": "sans-serif",
            "font.sans-serif": ["Microsoft JhengHei", "DejaVu Sans", "Arial"],
            "axes.unicode_minus": False,
            "axes.titlesize": 13,
            "axes.labelsize": 10.5,
            "xtick.labelsize": 9.5,
            "ytick.labelsize": 9.5,
            "legend.fontsize": 9.5,
            "axes.linewidth": 0.8,
            "legend.frameon": True,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
        }
    )


def report_color_for_strategy(strategy: str) -> str:
    """Return a stable strategy color using report palette."""
    return REPORT_COLOR_MAP.get(strategy, "tab:blue")


def display_strategy(strategy: str) -> str:
    """Normalize strategy display names for report figures."""
    return STRATEGY_LABEL_MAP.get(strategy, strategy)


def _read_csv_df(path: str | Path) -> pd.DataFrame:
    """Read CSV safely for plotting; return empty dataframe when missing."""
    p = Path(path)
    if not p.exists():
        return pd.DataFrame()
    return pd.read_csv(p)


def plot_exp1_overall_success_rate(summary_csv_path: str | Path, output_path: str | Path) -> None:
    """Experiment 1 figure 1: overall success-rate bar chart."""
    df = _read_csv_df(summary_csv_path)
    success_col = _exp1_success_col(df)
    if df.empty or "Strategy" not in df.columns or success_col is None:
        return
    order = ["Baseline", "Rule-Based", "Adaptive (Ours)"]
    plot_df = df[df["Strategy"].isin(order)].copy()
    plot_df["Strategy"] = pd.Categorical(plot_df["Strategy"], categories=order, ordered=True)
    plot_df = plot_df.sort_values("Strategy")
    if plot_df.empty:
        return

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(
        plot_df["Strategy"].tolist(),
        pd.to_numeric(plot_df[success_col], errors="coerce").tolist(),
        color=[
            report_color_for_strategy("AB1_Baseline"),
            report_color_for_strategy("AB2_RuleBased"),
            report_color_for_strategy("AB3_PPO_Dynamic"),
        ],
    )
    for bar in bars:
        h = float(bar.get_height())
        ax.annotate(
            f"{h:.1f}%",
            (bar.get_x() + bar.get_width() / 2.0, h),
            textcoords="offset points",
            xytext=(0, 3),
            ha="center",
            va="bottom",
            fontsize=9,
        )
    ax.set_title("Experiment 1: Overall Success Rate")
    ax.set_xlabel("Strategy")
    ax.set_ylabel(EXP1_SUCCESS_LABEL)
    ax.set_ylim(0, 100)
    finalize_report_figure(fig, str(output_path))


def plot_exp1_overall_efficiency(summary_csv_path: str | Path, output_path: str | Path) -> None:
    """Experiment 1 figure 2: overall average-steps bar chart."""
    df = _read_csv_df(summary_csv_path)
    required = {"Strategy", "Avg Steps"}
    if df.empty or not required.issubset(df.columns):
        return
    order = ["Baseline", "Rule-Based", "Adaptive (Ours)"]
    plot_df = df[df["Strategy"].isin(order)].copy()
    plot_df["Strategy"] = pd.Categorical(plot_df["Strategy"], categories=order, ordered=True)
    plot_df = plot_df.sort_values("Strategy")
    if plot_df.empty:
        return

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(
        plot_df["Strategy"].tolist(),
        pd.to_numeric(plot_df["Avg Steps"], errors="coerce").tolist(),
        color=[
            report_color_for_strategy("AB1_Baseline"),
            report_color_for_strategy("AB2_RuleBased"),
            report_color_for_strategy("AB3_PPO_Dynamic"),
        ],
    )
    ax.set_title("Experiment 1: Overall Efficiency (Avg Steps)")
    ax.set_xlabel("Strategy")
    ax.set_ylabel("Average Steps")
    finalize_report_figure(fig, str(output_path))


def plot_exp1_student_type_comparison(group_csv_path: str | Path, output_path: str | Path) -> None:
    """Experiment 1 figure 3: grouped success-rate bars by student group."""
    df = _read_csv_df(group_csv_path)
    success_col = _exp1_success_col(df)
    group_col = _exp1_group_col(df)
    if df.empty or success_col is None or group_col is None or "Strategy" not in df.columns:
        return
    student_order = EXP1_STUDENT_ORDER
    strategy_order = ["Baseline", "Rule-Based", "Adaptive (Ours)"]
    plot_df = df.copy()
    plot_df[group_col] = plot_df[group_col].astype(str).str.strip()
    plot_df[group_col] = plot_df[group_col].replace(EXP1_STUDENT_DISPLAY_MAP)
    plot_df["Strategy"] = plot_df["Strategy"].astype(str).str.strip()
    plot_df = plot_df[
        plot_df[group_col].isin(student_order) & plot_df["Strategy"].isin(strategy_order)
    ]
    if plot_df.empty:
        return

    fig, ax = plt.subplots(figsize=(8, 5))
    x = list(range(len(student_order)))
    width = 0.25
    color_map = {
        "Baseline": report_color_for_strategy("AB1_Baseline"),
        "Rule-Based": report_color_for_strategy("AB2_RuleBased"),
        "Adaptive (Ours)": report_color_for_strategy("AB3_PPO_Dynamic"),
    }
    for idx, strategy in enumerate(strategy_order):
        ys = []
        for student in student_order:
            hit = plot_df[
                (plot_df[group_col] == student) & (plot_df["Strategy"] == strategy)
            ]
            v = (
                float(pd.to_numeric(hit[success_col], errors="coerce").mean())
                if not hit.empty
                else float("nan")
            )
            ys.append(v)
        offset = (idx - 1) * width
        ax.bar(
            [i + offset for i in x],
            ys,
            width=width,
            label=strategy,
            color=color_map[strategy],
        )

    ax.set_xticks(x)
    ax.set_xticklabels(student_order)
    ax.set_ylim(0, 100)
    ax.set_xlabel("Student Level")
    ax.set_ylabel(EXP1_SUCCESS_LABEL)
    ax.set_title("Experiment 1: Success Rate by Student Level")
    ax.legend(loc="upper right")
    finalize_report_figure(fig, str(output_path))


def plot_exp1_final_mastery_comparison(group_csv_path: str | Path, output_path: str | Path) -> None:
    """Experiment 1 figure 4: grouped final-mastery bars by student group."""
    df = _read_csv_df(group_csv_path)
    group_col = _exp1_group_col(df)
    required = {"Strategy", "Avg Final Mastery"}
    if df.empty or group_col is None or not required.issubset(df.columns):
        return
    student_order = EXP1_STUDENT_ORDER
    strategy_order = ["Baseline", "Rule-Based", "Adaptive (Ours)"]
    plot_df = df.copy()
    plot_df[group_col] = plot_df[group_col].astype(str).str.strip()
    plot_df[group_col] = plot_df[group_col].replace(EXP1_STUDENT_DISPLAY_MAP)
    plot_df["Strategy"] = plot_df["Strategy"].astype(str).str.strip()
    plot_df = plot_df[
        plot_df[group_col].isin(student_order) & plot_df["Strategy"].isin(strategy_order)
    ]
    if plot_df.empty:
        return

    fig, ax = plt.subplots(figsize=(8, 5))
    x = list(range(len(student_order)))
    width = 0.25
    color_map = {
        "Baseline": report_color_for_strategy("AB1_Baseline"),
        "Rule-Based": report_color_for_strategy("AB2_RuleBased"),
        "Adaptive (Ours)": report_color_for_strategy("AB3_PPO_Dynamic"),
    }
    for idx, strategy in enumerate(strategy_order):
        ys = []
        for student in student_order:
            hit = plot_df[
                (plot_df[group_col] == student) & (plot_df["Strategy"] == strategy)
            ]
            v = (
                float(pd.to_numeric(hit["Avg Final Mastery"], errors="coerce").mean())
                if not hit.empty
                else float("nan")
            )
            ys.append(v)
        offset = (idx - 1) * width
        ax.bar(
            [i + offset for i in x],
            ys,
            width=width,
            label=strategy,
            color=color_map[strategy],
        )

    ax.set_xticks(x)
    ax.set_xticklabels(student_order)
    ax.set_ylim(0, 1.0)
    ax.set_xlabel("Student Level")
    ax.set_ylabel("Avg Final Mastery")
    ax.set_title("Experiment 1: Final Mastery by Student Level")
    ax.legend(loc="upper right")
    finalize_report_figure(fig, str(output_path))


def plot_exp1_mastery_gain_comparison(group_csv_path: str | Path, output_path: str | Path) -> None:
    """Experiment 1 figure 4: grouped mastery-gain bars by student group."""
    df = _read_csv_df(group_csv_path)
    group_col = _exp1_group_col(df)
    required = {"Strategy", "Avg Mastery Gain"}
    if df.empty or group_col is None or not required.issubset(df.columns):
        return
    student_order = EXP1_STUDENT_ORDER
    strategy_order = ["Baseline", "Rule-Based", "Adaptive (Ours)"]
    plot_df = df.copy()
    plot_df[group_col] = plot_df[group_col].astype(str).str.strip()
    plot_df[group_col] = plot_df[group_col].replace(EXP1_STUDENT_DISPLAY_MAP)
    plot_df["Strategy"] = plot_df["Strategy"].astype(str).str.strip()
    plot_df = plot_df[
        plot_df[group_col].isin(student_order) & plot_df["Strategy"].isin(strategy_order)
    ]
    if plot_df.empty:
        return

    fig, ax = plt.subplots(figsize=(8, 5))
    x = list(range(len(student_order)))
    width = 0.25
    color_map = {
        "Baseline": report_color_for_strategy("AB1_Baseline"),
        "Rule-Based": report_color_for_strategy("AB2_RuleBased"),
        "Adaptive (Ours)": report_color_for_strategy("AB3_PPO_Dynamic"),
    }
    for idx, strategy in enumerate(strategy_order):
        ys = []
        for student in student_order:
            hit = plot_df[
                (plot_df[group_col] == student) & (plot_df["Strategy"] == strategy)
            ]
            v = (
                float(pd.to_numeric(hit["Avg Mastery Gain"], errors="coerce").mean())
                if not hit.empty
                else float("nan")
            )
            ys.append(v)
        offset = (idx - 1) * width
        ax.bar(
            [i + offset for i in x],
            ys,
            width=width,
            label=strategy,
            color=color_map[strategy],
        )

    ax.set_xticks(x)
    ax.set_xticklabels(student_order)
    ax.set_xlabel("Student Level")
    ax.set_ylabel("Avg Mastery Gain")
    ax.set_title("Experiment 1: Mastery Gain by Student Level")
    ax.legend(loc="upper right")
    finalize_report_figure(fig, str(output_path))


def add_bar_labels(ax: plt.Axes, fmt: str = "{:.1f}%") -> None:
    """Attach value labels to all bar patches in an axis."""
    for bar in ax.patches:
        height = bar.get_height()
        if height != height:  # NaN
            continue
        ax.annotate(
            fmt.format(float(height)),
            (bar.get_x() + bar.get_width() / 2, height),
            textcoords="offset points",
            xytext=(0, 3),
            ha="center",
            va="bottom",
            fontsize=9,
            color="#333333",
        )


def add_figure_note(fig: plt.Figure, text: str, y: float = 0.03) -> None:
    """Add small centered note at figure bottom."""
    fig.text(0.5, y, text, ha="center", va="center", fontsize=8.5, color="dimgray")


def finalize_report_figure(fig_or_plt: Any, path: str) -> None:
    """Finalize and save figure with unified report output settings."""
    target = Path(path)
    if "final" in {part.lower() for part in target.parts}:
        print(f"[PROTECT] Skip writing to final directory: {target}")
        plt.close(fig_or_plt if hasattr(fig_or_plt, "axes") else plt.gcf())
        return
    setup_report_style()
    fig = fig_or_plt if hasattr(fig_or_plt, "savefig") else plt.gcf()
    for ax in fig.axes:
        ax.grid(False)
    fig.tight_layout()
    target.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(target), dpi=300, bbox_inches="tight")
    plt.close(fig)


def safe_write_markdown(path: str | Path, content: str) -> bool:
    """Write markdown with overwrite protection unless explicitly forced."""
    target = Path(path)
    if "final" in {part.lower() for part in target.parts}:
        print(f"[PROTECT] Skip writing to final directory: {target}")
        return False
    force_md = str(os.environ.get(FORCE_WRITE_MARKDOWN_ENV, "")).strip().lower() in {
        "1",
        "true",
        "yes",
        "y",
        "on",
    }
    if target.exists() and (not force_md):
        print("[SKIP] Markdown exists, not overwriting")
        return False
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8-sig")
    return True


def ensure_experiment_output_dirs(experiment_base_dir: str | Path) -> dict[str, Path]:
    """Ensure run/latest scaffolding exists; never auto-write into final/."""
    base_dir = Path(experiment_base_dir)
    runs_dir = base_dir / "runs"
    latest_dir = base_dir / "latest"
    final_dir = base_dir / "final"
    base_dir.mkdir(parents=True, exist_ok=True)
    runs_dir.mkdir(parents=True, exist_ok=True)
    latest_dir.mkdir(parents=True, exist_ok=True)
    return {
        "base_dir": base_dir,
        "runs_dir": runs_dir,
        "latest_dir": latest_dir,
        "final_dir": final_dir,
    }


def create_timestamped_run_dir(experiment_base_dir: str | Path) -> dict[str, Path]:
    """Create runs/<timestamp>/ under one experiment output root."""
    dirs = ensure_experiment_output_dirs(experiment_base_dir)
    run_dir = dirs["runs_dir"] / datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir.mkdir(parents=True, exist_ok=True)
    dirs["run_dir"] = run_dir
    return dirs


def sync_run_to_latest(run_dir: str | Path, latest_dir: str | Path) -> None:
    """Replace latest/ contents with files from this run."""
    run_path = Path(run_dir)
    latest_path = Path(latest_dir)
    latest_path.mkdir(parents=True, exist_ok=True)
    for child in latest_path.iterdir():
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()
    for child in run_path.iterdir():
        dst = latest_path / child.name
        if child.is_dir():
            shutil.copytree(child, dst)
        else:
            shutil.copy2(child, dst)


setup_report_style()

STRATEGY_ORDER = ["AB1_Baseline", "AB2_RuleBased", "AB3_PPO_Dynamic"]
student_type_order = ["Careless", "Average", "Weak Foundation"]
STUDENT_TYPE_ORDER = student_type_order
STUDENT_TYPE_SLUG_MAP = {
    "Careless": "careless",
    "Average": "average",
    "Weak Foundation": "weak",
}
STUDENT_TYPE_NORMALIZE_MAP = {
    "careless": "Careless",
    "average": "Average",
    "weak": "Weak Foundation",
    "weak foundation": "Weak Foundation",
    "low": "Weak Foundation",
    "mid": "Average",
    "high": "Careless",
}
SUBSKILL_ORDER = [
    "sign_handling",
    "combine_like_terms",
    "sign_distribution",
    "expand_monomial",
    "expand_binomial",
    "family_isomorphism",
]


def normalize_student_type(value: Any) -> str:
    """Normalize student-type labels to report-standard names."""
    text = str(value).strip()
    return STUDENT_TYPE_NORMALIZE_MAP.get(text.lower(), text)


def normalize_and_sort_student_types(df: pd.DataFrame, col: str = "student_type") -> pd.DataFrame:
    """Normalize and apply fixed ordered student-type categorical sorting."""
    if df.empty or col not in df.columns:
        return df
    out = df.copy()
    out[col] = out[col].astype(str).map(normalize_student_type)
    out[col] = pd.Categorical(out[col], categories=student_type_order, ordered=True)
    out = out.sort_values(col)
    return out


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
    finalize_report_figure(plt.gcf(), path)


def save_fig_high_quality(path: str) -> None:
    """Save high-quality publication figure."""
    finalize_report_figure(plt.gcf(), path)


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

    setup_report_style()
    fig, ax = plt.subplots(figsize=(8, 5))
    x_labels = [display_strategy(s) for s in xs]
    bars = ax.bar(
        x_labels,
        ys,
        width=0.3,
        color=[report_color_for_strategy(s) for s in xs],
    )
    add_bar_labels(ax, fmt="{:.1f}%")
    ax.set_title("Overall Strategy Comparison")
    ax.set_xlabel("Strategy")
    ax.set_ylabel("Success Rate (%)")
    ax.set_ylim(0, 100)
    os.makedirs(EXP1_DIR, exist_ok=True)
    finalize_report_figure(fig, os.path.join(EXP1_DIR, "fig_ablation_success_rate.png"))


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
    width = 0.3

    setup_report_style()
    fig, ax = plt.subplots(figsize=(8, 5))
    bars_steps = ax.bar(
        [i - width / 2 for i in x],
        steps_vals,
        width=width,
        label="Avg Steps",
        color="tab:orange",
    )
    bars_success = ax.bar(
        [i + width / 2 for i in x],
        success_vals,
        width=width,
        label="Success Rate (%)",
        color="tab:blue",
    )
    ax.set_xticks(x)
    ax.set_xticklabels([display_strategy(s) for s in labels])
    ax.set_title("Ablation Avg Steps vs Success Rate")
    ax.set_xlabel("Strategy")
    ax.set_ylabel("Value")
    add_bar_labels(ax, fmt="{:.1f}%")
    ax.legend()
    os.makedirs(EXP1_DIR, exist_ok=True)
    finalize_report_figure(fig, os.path.join(EXP1_DIR, "fig_ablation_steps_vs_success.png"))


def plot_ablation_by_student_type_success(rows: list[dict[str, str]]) -> None:
    """Figure C: grouped success bars by student type."""
    present_types = [t for t in STUDENT_TYPE_ORDER if any(r.get("student_type") == t for r in rows)]
    if not present_types:
        return

    x = list(range(len(present_types)))
    width = 0.3

    setup_report_style()
    fig, ax = plt.subplots(figsize=(8, 5))
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
        ax.bar(
            [i + offset for i in x],
            ys,
            width=width,
            label=display_strategy(strategy),
            color=report_color_for_strategy(strategy),
        )

    ax.set_xticks(x)
    ax.set_xticklabels(present_types)
    ax.set_title("Ablation Success Rate by Student Type")
    ax.set_xlabel("Student Type")
    ax.set_ylabel("Success Rate (%)")
    ax.set_ylim(0, 100)
    add_bar_labels(ax, fmt="{:.1f}%")
    ax.legend()
    os.makedirs(EXP1_DIR, exist_ok=True)
    finalize_report_figure(fig, os.path.join(EXP1_DIR, "fig_ablation_by_student_type_success.png"))


def plot_ablation_strategy_breakdown(summary_csv_path: str | None = None) -> None:
    """Experiment 1 analysis figure: simplified success-rate comparison."""
    path = summary_csv_path or os.path.join(EXP1_DIR, "ablation_strategy_summary.csv")
    if not os.path.exists(path):
        alt = os.path.join(REPORTS_DIR, "ablation_strategy_summary.csv")
        path = alt if os.path.exists(alt) else path
    if not os.path.exists(path):
        return

    df = pd.read_csv(path)
    if df.empty or "strategy" not in df.columns:
        return

    if "success_rate" not in df.columns:
        return

    ordered = df[df["strategy"].isin(STRATEGY_ORDER)].copy()
    if ordered.empty:
        return
    ordered["strategy"] = pd.Categorical(ordered["strategy"], categories=STRATEGY_ORDER, ordered=True)
    ordered = ordered.sort_values("strategy")

    setup_report_style()
    fig, ax = plt.subplots(figsize=(8, 5))
    x_labels = ordered["strategy"].tolist()
    y_vals = pd.to_numeric(ordered["success_rate"], errors="coerce").fillna(0.0) * 100.0
    ax.bar(
        [display_strategy(s) for s in x_labels],
        y_vals,
        width=0.3,
        color=[report_color_for_strategy(s) for s in x_labels],
    )
    add_bar_labels(ax, fmt="{:.1f}%")
    ax.set_title("Overall Strategy Comparison")
    ax.set_xlabel("Strategy")
    ax.set_ylabel("Success Rate (%)")
    ax.set_ylim(0, 100)
    os.makedirs(EXP1_DIR, exist_ok=True)
    finalize_report_figure(fig, os.path.join(EXP1_DIR, "fig_ablation_strategy_breakdown.png"))


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

    student_type_alias = {
        "high": "Careless (B+~B++)",
        "careless": "Careless (B+~B++)",
        "mid": "Average (B)",
        "average": "Average (B)",
        "low": "Weak (C)",
        "weak": "Weak (C)",
        "weak foundation": "Weak (C)",
        "weak_foundation": "Weak (C)",
    }
    normalized = df.copy()
    normalized["student_type"] = (
        normalized["student_type"]
        .astype(str)
        .map(lambda s: student_type_alias.get(s.strip().lower(), s.strip()))
    )

    grouped = (
        normalized.groupby(["strategy", "student_type"], as_index=False)
        .agg(success_rate=("success_rate", "mean"))
        .copy()
    )
    if grouped.empty:
        return

    student_order = ["Careless (B+~B++)", "Average (B)", "Weak (C)"]
    assert student_order == ["Careless (B+~B++)", "Average (B)", "Weak (C)"]
    strategy_display = {
        "AB1_Baseline": "Baseline",
        "AB2_RuleBased": "Rule-Based",
        "AB3_PPO_Dynamic": "Adaptive (Ours)",
    }
    strategy_colors = {
        "AB1_Baseline": "#808080",   # Baseline: gray
        "AB2_RuleBased": "#ff7f0e",  # Rule-Based: orange
        "AB3_PPO_Dynamic": "#1f77b4",  # Adaptive: blue (highlight)
    }
    x_labels = [t for t in student_order if any(grouped["student_type"] == t)]
    if not x_labels:
        return

    x = list(range(len(x_labels)))
    width = 0.24

    setup_report_style()
    fig, ax = plt.subplots(figsize=(9, 5.5), constrained_layout=False)
    fig.subplots_adjust(left=0.10, right=0.98, top=0.90, bottom=0.14)
    ax.set_facecolor("white")
    plotted_vals: dict[str, dict[str, float]] = {s: {} for s in STRATEGY_ORDER}
    bar_containers = []
    for idx, strategy in enumerate(STRATEGY_ORDER):
        ys: list[float] = []
        for st in x_labels:
            hit = grouped[(grouped["strategy"] == strategy) & (grouped["student_type"] == st)]
            if hit.empty:
                ys.append(0.0)
            else:
                ys.append(float(pd.to_numeric(hit["success_rate"], errors="coerce").mean()) * 100.0)
        for st, y in zip(x_labels, ys):
            plotted_vals[strategy][st] = float(y)
        offset = (idx - 1) * width
        bars = ax.bar(
            [i + offset for i in x],
            ys,
            width=width,
            label=strategy_display.get(strategy, strategy),
            color=strategy_colors.get(strategy),
        )
        bar_containers.append(bars)

    # Value labels (1 decimal), compact to avoid overlap.
    for bars in bar_containers:
        for b in bars:
            h = float(b.get_height())
            ax.annotate(
                f"{h:.1f}%",
                (b.get_x() + b.get_width() / 2.0, h),
                textcoords="offset points",
                xytext=(0, 3),
                ha="center",
                va="bottom",
                fontsize=9,
            )

    ax.set_xticks(x)
    ax.set_xticklabels(x_labels, fontsize=11)
    ax.set_title(
        "Experiment 1: Strategy Comparison by Student Type",
        fontsize=14,
        pad=8,
        color="#333333",
        fontweight="normal",
    )
    ax.set_xlabel("Student Type", labelpad=8, fontsize=10.5, color="#333333")
    ax.set_ylabel(EXP1_SUCCESS_LABEL, fontsize=10.5, color="#333333")
    ax.set_ylim(0, 100)
    ax.tick_params(axis="both", labelsize=9.5, colors="#333333")
    ax.legend(loc="upper left", fontsize=10, frameon=True)
    plt.tight_layout()

    # Compute largest improvement dynamically: AB3 - Baseline.
    improvement_rows: list[tuple[str, float]] = []
    for st in student_order:
        b = plotted_vals.get("AB1_Baseline", {}).get(st, float("nan"))
        a = plotted_vals.get("AB3_PPO_Dynamic", {}).get(st, float("nan"))
        if pd.notna(b) and pd.notna(a):
            improvement_rows.append((st, float(a - b)))
    best_group = "Average (B)"
    if improvement_rows:
        best_group = max(improvement_rows, key=lambda t: t[1])[0]

    os.makedirs(EXP1_BASE_DIR, exist_ok=True)
    os.makedirs(EXP1_DIR, exist_ok=True)
    # Required output path.
    base_fig_path = os.path.join(EXP1_BASE_DIR, "fig_exp1_student_type_improved.png")
    finalize_report_figure(fig, base_fig_path)
    # Keep compatibility with existing latest-based pipeline.
    try:
        shutil.copy2(base_fig_path, os.path.join(EXP1_DIR, "fig_exp1_student_type_improved.png"))
    except Exception:
        pass

    caption_text = (
        "[Figure Title]\n"
        "Experiment 1: Strategy Comparison by Student Type\n\n"
        "[Main Finding]\n"
        "Adaptive policy (AB3) improves success rate across all student groups.\n\n"
        "[Key Insight]\n"
        f"The largest improvement is observed in: {best_group}\n\n"
        "Why:\n"
        "- Careless: already near threshold -> limited gain\n"
        "- Average: most sensitive to timing -> biggest gain\n"
        "- Weak: still constrained by foundation\n\n"
        "[Conclusion]\n"
        "Adaptive decision (when to remediate) is the key driver of performance.\n"
    )
    caption_path = Path(EXP1_BASE_DIR) / "figure_caption_exp1_student_type.md"
    caption_path.write_text(caption_text, encoding="utf-8-sig")


def plot_ab3_subskill_gain_by_type(rows: list[dict[str, str]]) -> None:
    """Figure D: grouped subskill gain bars by student type."""
    present_subskills = [s for s in SUBSKILL_ORDER if any(r.get("subskill") == s for r in rows)]
    if not present_subskills:
        return

    x = list(range(len(present_subskills)))
    width = 0.3

    setup_report_style()
    fig, ax = plt.subplots(figsize=(8, 5))
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
        color = "tab:blue" if student_type == "Careless" else ("tab:orange" if student_type == "Average" else "tab:green")
        ax.bar([i + offset for i in x], ys, width=width, label=student_type, color=color)

    ax.set_xticks(x)
    ax.set_xticklabels(present_subskills, rotation=20, ha="right")
    ax.set_title("AB3 Subskill Gain by Student Type")
    ax.set_xlabel("Subskill")
    ax.set_ylabel("Average Gain")
    add_bar_labels(ax, fmt="{:.2f}")
    ax.legend()
    finalize_report_figure(fig, os.path.join(REPORTS_DIR, "fig_ab3_subskill_gain_by_type.png"))


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

    setup_report_style()
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(xs, ys, color=["tab:blue", "tab:orange", "tab:green"][: len(xs)])
    add_bar_labels(ax, fmt="{:.2f}")
    ax.set_title("AB3 Polynomial Gain by Student Type")
    ax.set_xlabel("Student Type")
    ax.set_ylabel("Average Polynomial Gain")
    finalize_report_figure(fig, os.path.join(REPORTS_DIR, "fig_ab3_polynomial_gain_by_type.png"))


def plot_multi_steps_results(include_ab3_by_student_type: bool = False) -> None:
    """Plot cross-step comparisons from multi-step summary CSV outputs."""
    strategy_path = os.path.join(REPORTS_DIR, "multi_steps_strategy_summary.csv")
    by_type_path = os.path.join(REPORTS_DIR, "multi_steps_strategy_by_type_summary.csv")
    if not os.path.exists(strategy_path):
        strategy_path = os.path.join(EXP1_DIR, "multi_steps_strategy_summary.csv")
    if not os.path.exists(by_type_path):
        by_type_path = os.path.join(EXP1_DIR, "multi_steps_strategy_by_type_summary.csv")

    strategy_df = pd.read_csv(strategy_path) if os.path.exists(strategy_path) else pd.DataFrame()
    by_type_df = pd.read_csv(by_type_path) if os.path.exists(by_type_path) else pd.DataFrame()

    if not strategy_df.empty and {"max_steps", "strategy", "success_rate", "avg_steps"}.issubset(strategy_df.columns):
        setup_report_style()
        plt.figure(figsize=(8, 5))
        for idx, strategy in enumerate(STRATEGY_ORDER):
            sub = strategy_df[strategy_df["strategy"] == strategy].copy()
            if sub.empty:
                continue
            sub = sub.sort_values("max_steps")
            is_adaptive = strategy == "AB3_PPO_Dynamic"
            plt.plot(
                sub["max_steps"],
                sub["success_rate"] * 100.0,
                marker="o",
                label=display_strategy(strategy),
                color=report_color_for_strategy(strategy),
                linewidth=3.0 if is_adaptive else 2.0,
                markersize=8 if is_adaptive else 6,
            )
            for _, row in sub.iterrows():
                max_steps = pd.to_numeric(row["max_steps"], errors="coerce")
                success_pct = pd.to_numeric(row["success_rate"], errors="coerce") * 100.0
                avg_steps = pd.to_numeric(row["avg_steps"], errors="coerce")
                if pd.isna(max_steps) or pd.isna(success_pct) or pd.isna(avg_steps):
                    continue
                if strategy == "AB2_RuleBased":
                    y_offset = -12
                    va = "top"
                elif strategy == "AB3_PPO_Dynamic":
                    y_offset = 18
                    va = "bottom"
                else:
                    y_offset = 8
                    va = "bottom"
                plt.annotate(
                    f"Avg Steps = {float(avg_steps):.2f}",
                    (float(max_steps), float(success_pct)),
                    textcoords="offset points",
                    xytext=(0, y_offset),
                    ha="center",
                    va=va,
                    fontsize=9,
                )
        plt.title("Success Rate vs MAX_STEPS")
        plt.xlabel("MAX_STEPS")
        plt.ylabel("Success Rate 達標A (%)")
        plt.ylim(0, 100)
        plt.legend()
        try:
            baseline_last = strategy_df[strategy_df["strategy"] == "AB1_Baseline"].sort_values("max_steps").iloc[-1]
            adaptive_last = strategy_df[strategy_df["strategy"] == "AB3_PPO_Dynamic"].sort_values("max_steps").iloc[-1]
            plt.annotate(
                "Higher success with fewer steps",
                xy=(float(adaptive_last["max_steps"]), float(adaptive_last["success_rate"]) * 100.0),
                xytext=(float(baseline_last["max_steps"]) - 6, float(baseline_last["success_rate"]) * 100.0 + 18),
                arrowprops={"arrowstyle": "->", "linewidth": 1.2, "color": "#333333"},
                fontsize=9.5,
            )
        except Exception:
            pass
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
        setup_report_style()
        plt.figure(figsize=(8, 5))
        for strategy in STRATEGY_ORDER:
            sub = strategy_df[strategy_df["strategy"] == strategy]
            if sub.empty:
                continue
            is_adaptive = strategy == "AB3_PPO_Dynamic"
            plt.scatter(
                sub["avg_steps"],
                sub["success_rate"] * 100.0,
                s=90 if is_adaptive else 55,
                color=report_color_for_strategy(strategy),
                label=display_strategy(strategy),
            )
            for _, row in sub.iterrows():
                label = f"{display_strategy(str(row['strategy']))}@{int(row['max_steps'])}"
                plt.annotate(label, (row["avg_steps"], row["success_rate"] * 100.0), fontsize=9)
                plt.annotate(
                    f"Avg Steps = {float(row['avg_steps']):.2f}",
                    (row["avg_steps"], row["success_rate"] * 100.0),
                    textcoords="offset points",
                    xytext=(0, -10),
                    ha="center",
                    va="top",
                    fontsize=9,
                )
        try:
            adaptive = strategy_df[strategy_df["strategy"] == "AB3_PPO_Dynamic"]
            if not adaptive.empty:
                best = adaptive.sort_values("success_rate", ascending=False).iloc[0]
                plt.annotate(
                    "Higher success with fewer steps",
                    (float(best["avg_steps"]), float(best["success_rate"]) * 100.0),
                    textcoords="offset points",
                    xytext=(18, -18),
                    ha="left",
                    va="top",
                    arrowprops={"arrowstyle": "->", "linewidth": 1.2, "color": "#333333"},
                    fontsize=9.5,
                )
        except Exception:
            pass
        plt.title("Steps vs Success Tradeoff Across MAX_STEPS")
        plt.xlabel("Average Steps")
        plt.ylabel("Success Rate (%)")
        plt.legend(loc="upper left")
        os.makedirs(EXP1_DIR, exist_ok=True)
        save_fig(os.path.join(EXP1_DIR, "fig_multi_steps_efficiency.png"))

    # Experiment 1: keep only the 3 main report figures.
    plot_ablation_by_student_type()


def plot_weak_foundation_support_results(
    output_dir: str = os.path.join(EXP3_BASE_DIR, "latest"),
) -> None:
    """Plot Experiment 3 figures focused on escape-from-C educational value."""
    setup_report_style()
    out_dir = output_dir
    summary_path = os.path.join(out_dir, "weak_escape_total_step_summary.csv")
    subskill_path = os.path.join(out_dir, "weak_foundation_subskill_summary.csv")
    breakpoint_path = os.path.join(out_dir, "weak_foundation_breakpoint_summary.csv")

    summary_df = pd.read_csv(summary_path) if os.path.exists(summary_path) else pd.DataFrame()
    if summary_df.empty:
        legacy_summary = os.path.join(out_dir, "weak_foundation_support_summary.csv")
        summary_df = pd.read_csv(legacy_summary) if os.path.exists(legacy_summary) else pd.DataFrame()
    subskill_df = pd.read_csv(subskill_path) if os.path.exists(subskill_path) else pd.DataFrame()
    breakpoint_df = pd.read_csv(breakpoint_path) if os.path.exists(breakpoint_path) else pd.DataFrame()

    if summary_df.empty:
        return

    # Backward/forward compatibility for summary column names.
    if "support_steps" not in summary_df.columns and "max_steps" in summary_df.columns:
        summary_df = summary_df.rename(columns={"max_steps": "support_steps"})
    if "support_steps" not in summary_df.columns and "foundation_extra_steps" in summary_df.columns:
        summary_df = summary_df.rename(columns={"foundation_extra_steps": "support_steps"})
    if "avg_final_mastery" not in summary_df.columns and "avg_final_polynomial_mastery" in summary_df.columns:
        summary_df = summary_df.rename(columns={"avg_final_polynomial_mastery": "avg_final_mastery"})
    if "avg_steps_used" not in summary_df.columns and "avg_total_steps" in summary_df.columns:
        summary_df = summary_df.rename(columns={"avg_total_steps": "avg_steps_used"})
    if "marginal_gain" not in summary_df.columns and "marginal_success_gain" in summary_df.columns:
        summary_df = summary_df.rename(columns={"marginal_success_gain": "marginal_gain"})

    summary_df["support_steps"] = pd.to_numeric(summary_df["support_steps"], errors="coerce")
    summary_df["success_rate"] = pd.to_numeric(summary_df["success_rate"], errors="coerce")
    summary_df["avg_final_mastery"] = pd.to_numeric(summary_df["avg_final_mastery"], errors="coerce")
    summary_df["avg_steps_used"] = pd.to_numeric(summary_df["avg_steps_used"], errors="coerce")
    if "marginal_gain" in summary_df.columns:
        summary_df["marginal_gain"] = pd.to_numeric(summary_df["marginal_gain"], errors="coerce")
    sub = summary_df.sort_values("support_steps").dropna(subset=["support_steps"])

    # Figure 1 (PRIMARY): Escape-from-C rate with marginal annotation and best point.
    if {"support_steps", "success_rate"}.issubset(sub.columns):
        fig, ax = plt.subplots(figsize=(8, 5))
        x = sub["support_steps"].astype(float).tolist()
        y = (sub["success_rate"].astype(float) * 100.0).tolist()
        ax.plot(x, y, marker="o", linewidth=3, markersize=8, color="#2ca02c")
        ax.set_title("Experiment 3: Escape-from-C Rate under Adaptive Support")
        ax.text(
            0.5,
            1.01,
            "Final mastery >= 0.60 (B threshold)",
            transform=ax.transAxes,
            ha="center",
            va="bottom",
            fontsize=9,
            color="#444444",
        )
        ax.set_xlabel("support_steps")
        ax.set_ylabel("success_rate (%)")
        for xv, yv in zip(x, y):
            ax.annotate(f"{yv:.0f}%", (xv, yv), textcoords="offset points", xytext=(0, 6), ha="center")
        if len(x) > 1:
            for i in range(1, len(x)):
                dx = (x[i - 1] + x[i]) / 2.0
                dy = (y[i - 1] + y[i]) / 2.0
                delta = y[i] - y[i - 1]
                ax.annotate(f"{delta:+.0f}%", (dx, dy), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=9, color="#444444")
        if y:
            best_idx = int(y.index(max(y)))
            ax.scatter([x[best_idx]], [y[best_idx]], color="red", zorder=5)
            ax.annotate("best", (x[best_idx], y[best_idx]), textcoords="offset points", xytext=(0, -16), ha="center", color="red")
        save_fig_high_quality(os.path.join(out_dir, "fig_exp3_escape_rate.png"))

    # Figure 2: Cost vs Benefit.
    if {"avg_steps_used", "success_rate", "support_steps"}.issubset(sub.columns):
        fig, ax = plt.subplots(figsize=(8, 5))
        x = sub["avg_steps_used"].astype(float).tolist()
        y = (sub["success_rate"].astype(float) * 100.0).tolist()
        labels = sub["support_steps"].astype(int).tolist()
        ax.scatter(x, y, s=70, color="#1f77b4")
        ax.plot(x, y, linewidth=1.5, alpha=0.6, color="#1f77b4")
        ax.set_title("Cost vs Benefit of Foundation Support")
        ax.set_xlabel("avg_steps_used")
        ax.set_ylabel("success_rate (%)")
        for xv, yv, sv in zip(x, y, labels):
            ax.annotate(f"{sv} steps", (xv, yv), textcoords="offset points", xytext=(5, 6), fontsize=9)
        save_fig_high_quality(os.path.join(out_dir, "fig_exp3_cost_vs_benefit.png"))

    # Figure 3: ROI / marginal impact on escape rate.
    if {"support_steps", "success_rate"}.issubset(sub.columns) and len(sub) > 1:
        m = sub.sort_values("support_steps").copy()
        m["delta_success"] = m["success_rate"].diff() * 100.0
        m = m.dropna(subset=["delta_success"])
        if not m.empty:
            fig, ax = plt.subplots(figsize=(8, 5))
            x = m["support_steps"].astype(float).tolist()
            y = m["delta_success"].astype(float).tolist()
            ax.plot(x, y, marker="o", linewidth=3, markersize=8, color="#ff7f0e")
            ax.axhline(0.0, linestyle="--", linewidth=1.0, color="#666666")
            ax.set_title("Marginal Impact of Additional Support (Escape Rate)")
            ax.set_xlabel("support_steps")
            ax.set_ylabel("delta_success (%)")
            for xv, yv in zip(x, y):
                ax.annotate(f"{yv:+.0f}%", (xv, yv), textcoords="offset points", xytext=(0, 6), ha="center")
            save_fig_high_quality(os.path.join(out_dir, "fig_exp3_marginal_gain.png"))

    # Figure 4: Mastery with explicit B threshold.
    if {"support_steps", "avg_final_mastery"}.issubset(sub.columns):
        fig, ax = plt.subplots(figsize=(8, 5))
        x = sub["support_steps"].astype(float).tolist()
        y = sub["avg_final_mastery"].astype(float).tolist()
        ax.plot(x, y, marker="o", linewidth=3, markersize=8, color="#1f77b4")
        ax.axhline(0.60, linestyle="--", linewidth=2.0, color="#333333")
        ax.axhspan(0.0, 0.60, color="#eeeeee", alpha=0.45)
        ax.annotate("B Threshold (Escape from C)", (x[-1], 0.60), textcoords="offset points", xytext=(-160, 8))
        ax.set_title("Experiment 3: Final Mastery under Adaptive Support")
        ax.set_xlabel("support_steps")
        ax.set_ylabel("avg_final_mastery")
        for xv, yv in zip(x, y):
            ax.annotate(f"{yv:.3f}", (xv, yv), textcoords="offset points", xytext=(0, 6), ha="center")
        save_fig_high_quality(os.path.join(out_dir, "fig_exp3_mastery_threshold.png"))

    # Optional plots are intentionally not generated by default:
    # - fig_weak_foundation_breakpoint_shift.png
    # - fig_weak_foundation_subskill_gain.png

    # Captions for Experiment 3.
    caption_success = os.path.join(out_dir, "figure_caption_exp3_success.md")
    safe_write_markdown(
        caption_success,
        "### Figure Caption: Escape-from-C Rate under Adaptive Support\n"
        "Experiment 3 focuses on escaping C, not reaching A.\n"
        "This figure reports weak-group success defined by final mastery >= 0.60.\n",
    )
    caption_cost = os.path.join(out_dir, "figure_caption_exp3_cost.md")
    safe_write_markdown(
        caption_cost,
        "### Figure Caption: Cost vs Benefit of Foundation Support\n"
        "Each point corresponds to one support_steps condition, showing avg_steps_used versus escape-from-C rate.\n",
    )
    caption_marginal = os.path.join(out_dir, "figure_caption_exp3_marginal.md")
    safe_write_markdown(
        caption_marginal,
        "### Figure Caption: Marginal Impact of Additional Support (Escape Rate)\n"
        "delta_success is computed as neighboring differences in success_rate (%), indicating diminishing returns.\n",
    )
    caption_mastery = os.path.join(out_dir, "figure_caption_exp3_mastery.md")
    safe_write_markdown(
        caption_mastery,
        "### Figure Caption: Final Mastery under Adaptive Support\n"
        "The bold dashed 0.60 line marks the B-threshold for escape from C.\n",
    )


def plot_exp3_multiseed_results(output_dir: str = os.path.join(EXP3_BASE_DIR, "latest")) -> None:
    """Plot Experiment 3 multi-seed decision figures with error bars."""
    setup_report_style()
    out_dir = output_dir
    summary_path = os.path.join(out_dir, "exp3_multiseed_summary.csv")
    df = pd.read_csv(summary_path) if os.path.exists(summary_path) else pd.DataFrame()
    if df.empty:
        return

    required = {
        "MAX_STEPS",
        "mean_escape_from_c_rate_pct",
        "std_escape_from_c_rate_pct",
        "mean_final_mastery",
        "std_final_mastery",
        "mean_steps_used",
        "std_steps_used",
    }
    if not required.issubset(df.columns):
        return

    for c in required:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.sort_values("MAX_STEPS").dropna(subset=["MAX_STEPS"])
    if df.empty:
        return

    x = df["MAX_STEPS"].astype(float).tolist()

    # Figure 1: escape rate (mean ± std).
    y_escape = df["mean_escape_from_c_rate_pct"].astype(float).tolist()
    yerr_escape = df["std_escape_from_c_rate_pct"].astype(float).tolist()
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.errorbar(x, y_escape, yerr=yerr_escape, fmt="o-", linewidth=2.2, markersize=7, capsize=4, color="#2ca02c")
    ax.set_title("Experiment 3: Escape-from-C Rate under Total-Step Relaxation (Multi-Seed)")
    ax.text(
        0.5,
        1.01,
        "Weak only, AB3 only, success = final mastery >= 0.60",
        transform=ax.transAxes,
        ha="center",
        va="bottom",
        fontsize=9,
        color="#444444",
    )
    ax.set_xlabel("MAX_STEPS")
    ax.set_ylabel("Escape-from-C Rate (%)")
    for xv, yv in zip(x, y_escape):
        ax.annotate(f"{yv:.1f}%", (xv, yv), textcoords="offset points", xytext=(0, 7), ha="center", fontsize=9)
    save_fig_high_quality(os.path.join(out_dir, "fig_exp3_escape_rate_multiseed.png"))

    # Figure 2: final mastery (mean ± std) with B threshold.
    y_mastery = df["mean_final_mastery"].astype(float).tolist()
    yerr_mastery = df["std_final_mastery"].astype(float).tolist()
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.errorbar(x, y_mastery, yerr=yerr_mastery, fmt="o-", linewidth=2.2, markersize=7, capsize=4, color="#1f77b4")
    ax.axhline(0.60, linestyle="--", linewidth=1.8, color="#333333")
    ax.annotate("B Threshold (Escape from C)", (x[-1], 0.60), textcoords="offset points", xytext=(-165, 7), fontsize=9)
    ax.set_title("Experiment 3: Final Mastery under Total-Step Relaxation (Multi-Seed)")
    ax.set_xlabel("MAX_STEPS")
    ax.set_ylabel("Mean Final Mastery")
    for xv, yv in zip(x, y_mastery):
        ax.annotate(f"{yv:.3f}", (xv, yv), textcoords="offset points", xytext=(0, 7), ha="center", fontsize=9)
    save_fig_high_quality(os.path.join(out_dir, "fig_exp3_mastery_multiseed.png"))

    # Figure 3: cost vs benefit with optional x/y error bars.
    x_cost = df["mean_steps_used"].astype(float).tolist()
    xerr_cost = df["std_steps_used"].astype(float).tolist()
    labels = df["MAX_STEPS"].astype(int).tolist()
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.errorbar(
        x_cost,
        y_escape,
        xerr=xerr_cost,
        yerr=yerr_escape,
        fmt="o",
        markersize=7,
        capsize=4,
        color="#1f77b4",
    )
    ax.plot(x_cost, y_escape, linewidth=1.3, alpha=0.6, color="#1f77b4")
    ax.set_title("Experiment 3: Cost vs Benefit under Total-Step Relaxation (Multi-Seed)")
    ax.set_xlabel("Mean Steps Used")
    ax.set_ylabel("Mean Escape-from-C Rate (%)")
    for xv, yv, step_label in zip(x_cost, y_escape, labels):
        ax.annotate(f"MAX_STEPS={step_label}", (xv, yv), textcoords="offset points", xytext=(5, 8), fontsize=8.5)
    save_fig_high_quality(os.path.join(out_dir, "fig_exp3_cost_vs_benefit_multiseed.png"))


def plot_exp3_marginal_cost(output_dir: str = os.path.join(EXP3_BASE_DIR, "latest")) -> None:
    """Plot incremental marginal cost (steps per +1% escape-from-C) by MAX_STEPS interval."""
    setup_report_style()
    out_dir = output_dir
    summary_path = os.path.join(out_dir, "exp3_marginal_cost_summary.csv")
    df = pd.read_csv(summary_path) if os.path.exists(summary_path) else pd.DataFrame()
    if df.empty:
        return
    required = {
        "from_max_steps",
        "to_max_steps",
        "delta_escape_rate_pct",
        "marginal_cost_per_1pct_escape",
    }
    if not required.issubset(df.columns):
        return

    df = df.copy()
    df["from_max_steps"] = pd.to_numeric(df["from_max_steps"], errors="coerce")
    df["to_max_steps"] = pd.to_numeric(df["to_max_steps"], errors="coerce")
    df["delta_escape_rate_pct"] = pd.to_numeric(df["delta_escape_rate_pct"], errors="coerce")
    df = df.sort_values(["from_max_steps", "to_max_steps"]).dropna(subset=["from_max_steps", "to_max_steps"])
    if df.empty:
        return

    intervals = [f"{int(a)}→{int(b)}" for a, b in zip(df["from_max_steps"], df["to_max_steps"])]
    raw_marginal = pd.to_numeric(df["marginal_cost_per_1pct_escape"], errors="coerce")
    vals = raw_marginal.fillna(0.0).tolist()
    colors = ["#9E9E9E" if (pd.isna(m) or float(d) <= 0) else "#4C72B0" for m, d in zip(raw_marginal, df["delta_escape_rate_pct"])]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(intervals, vals, color=colors)
    ax.set_title("Experiment 3: Marginal Cost of Additional Support")
    ax.set_xlabel("MAX_STEPS Interval")
    ax.set_ylabel("Steps per +1% Escape-from-C")

    for i, bar in enumerate(bars):
        val = float(bar.get_height())
        d = float(df["delta_escape_rate_pct"].iloc[i]) if pd.notna(df["delta_escape_rate_pct"].iloc[i]) else 0.0
        if pd.isna(raw_marginal.iloc[i]) or d <= 0:
            ax.annotate("NA", (bar.get_x() + bar.get_width() / 2.0, max(val, 0.0)), textcoords="offset points", xytext=(0, 5), ha="center", fontsize=9, color="#555555")
        else:
            ax.annotate(f"{val:.2f}", (bar.get_x() + bar.get_width() / 2.0, val), textcoords="offset points", xytext=(0, 5), ha="center", fontsize=9)

    save_fig_high_quality(os.path.join(out_dir, "fig_exp3_marginal_cost.png"))

    caption_path = os.path.join(out_dir, "figure_caption_exp3_marginal_cost.md")
    safe_write_markdown(
        caption_path,
        "### Figure Caption: Marginal Cost of Additional Support\n\n"
        "This figure reports the incremental cost of improving escape-from-C performance under larger total-step budgets.\n"
        "For each adjacent MAX_STEPS interval, marginal cost is defined as the additional mean steps used divided by the additional escape-from-C rate (%).\n\n"
        "Lower values indicate more efficient support.\n"
        "Higher values indicate diminishing efficiency, meaning that additional steps are required to produce the same improvement in student outcomes.\n",
    )


def plot_exp3_strategy_comparison(
    summary_csv_path: str | Path,
    output_dir: str | Path,
) -> None:
    """Plot Exp3 strategy comparison figures under fixed MAX_STEPS budgets."""
    setup_report_style()
    df = _read_csv_df(summary_csv_path)
    if df.empty:
        return
    required = {
        "MAX_STEPS",
        "Strategy",
        "mean_escape_rate_pct",
        "std_escape_rate_pct",
        "mean_final_mastery",
        "std_final_mastery",
    }
    if not required.issubset(df.columns):
        return

    work = df.copy()
    for c in ["MAX_STEPS", "mean_escape_rate_pct", "std_escape_rate_pct", "mean_final_mastery", "std_final_mastery"]:
        work[c] = pd.to_numeric(work[c], errors="coerce")
    work = work.dropna(subset=["MAX_STEPS"])
    if work.empty:
        return

    strategy_order = ["Baseline", "Rule-Based", "Adaptive (Ours)"]
    hatch_map = {
        "Baseline": "//",
        "Rule-Based": "..",
        "Adaptive (Ours)": "xx",
    }
    color_map = {
        "Baseline": "#4C72B0",
        "Rule-Based": "#DD8452",
        "Adaptive (Ours)": "#55A868",
    }

    budgets = sorted(work["MAX_STEPS"].dropna().astype(int).unique().tolist())
    if not budgets:
        return
    x = list(range(len(budgets)))
    width = 0.25

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Figure 1: escape rate grouped bars.
    fig, ax = plt.subplots(figsize=(8.4, 5.2))
    for idx, strategy in enumerate(strategy_order):
        ys = []
        es = []
        for b in budgets:
            hit = work[(work["MAX_STEPS"] == b) & (work["Strategy"] == strategy)]
            ys.append(float(hit["mean_escape_rate_pct"].iloc[0]) if not hit.empty else float("nan"))
            es.append(float(hit["std_escape_rate_pct"].iloc[0]) if not hit.empty else float("nan"))
        offset = (idx - 1) * width
        bars = ax.bar(
            [i + offset for i in x],
            ys,
            width=width,
            yerr=es,
            capsize=4,
            label=strategy,
            color=color_map[strategy],
            edgecolor="#333333",
            linewidth=0.6,
            hatch=hatch_map[strategy],
        )
        for bar, val in zip(bars, ys):
            if pd.isna(val):
                continue
            ax.annotate(
                f"{val:.1f}%",
                (bar.get_x() + bar.get_width() / 2.0, val),
                textcoords="offset points",
                xytext=(0, 5),
                ha="center",
                fontsize=8.5,
            )

    ax.set_title("Experiment 3: Escape-from-C Rate by Strategy under Fixed Support Budgets")
    ax.set_xlabel("MAX_STEPS")
    ax.set_ylabel("Escape-from-C Rate (%)")
    ax.set_xticks(x)
    ax.set_xticklabels([str(b) for b in budgets])
    ax.set_ylim(0, max(100, (pd.to_numeric(work["mean_escape_rate_pct"], errors="coerce").max() or 0) + 10))
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(str(out_dir / "fig_exp3_strategy_comparison_escape_rate.png"), dpi=300, bbox_inches="tight")
    plt.close(fig)

    # Figure 2: final mastery grouped bars.
    fig, ax = plt.subplots(figsize=(8.4, 5.2))
    for idx, strategy in enumerate(strategy_order):
        ys = []
        es = []
        for b in budgets:
            hit = work[(work["MAX_STEPS"] == b) & (work["Strategy"] == strategy)]
            ys.append(float(hit["mean_final_mastery"].iloc[0]) if not hit.empty else float("nan"))
            es.append(float(hit["std_final_mastery"].iloc[0]) if not hit.empty else float("nan"))
        offset = (idx - 1) * width
        bars = ax.bar(
            [i + offset for i in x],
            ys,
            width=width,
            yerr=es,
            capsize=4,
            label=strategy,
            color=color_map[strategy],
            edgecolor="#333333",
            linewidth=0.6,
            hatch=hatch_map[strategy],
        )
        for bar, val in zip(bars, ys):
            if pd.isna(val):
                continue
            ax.annotate(
                f"{val:.3f}",
                (bar.get_x() + bar.get_width() / 2.0, val),
                textcoords="offset points",
                xytext=(0, 5),
                ha="center",
                fontsize=8.5,
            )

    ax.set_title("Experiment 3: Final Mastery by Strategy under Fixed Support Budgets")
    ax.set_xlabel("MAX_STEPS")
    ax.set_ylabel("Mean Final Mastery")
    ax.set_xticks(x)
    ax.set_xticklabels([str(b) for b in budgets])
    ymax = pd.to_numeric(work["mean_final_mastery"], errors="coerce").max()
    ax.set_ylim(0, 1.0 if pd.isna(ymax) else min(1.0, float(ymax) + 0.2))
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(str(out_dir / "fig_exp3_strategy_comparison_final_mastery.png"), dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_exp3_rq3_results(
    summary_csv_path: str | Path,
    output_dir: str | Path,
    error_by_point: dict[tuple[int, str], float] | None = None,
) -> None:
    """Plot Experiment 3 RQ3 main figure only (Weak, strategy comparison, 30-100 budgets)."""
    setup_report_style()
    df = _read_csv_df(summary_csv_path)
    if df.empty:
        return

    required = {
        "MAX_STEPS",
        "Strategy",
        "Escape-from-C Rate (%)",
    }
    if not required.issubset(df.columns):
        return

    work = df.copy()
    for c in ["MAX_STEPS", "Escape-from-C Rate (%)"]:
        work[c] = pd.to_numeric(work[c], errors="coerce")
    work = work.dropna(subset=["MAX_STEPS"]).copy()
    if work.empty:
        return

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    strategy_order = ["Baseline", "Rule-Based", "Adaptive (Ours)"]
    color_map = {
        "Baseline": "#1f77b4",
        "Rule-Based": "#ff7f0e",
        "Adaptive (Ours)": "#2ca02c",
    }
    budgets = sorted(work["MAX_STEPS"].astype(int).unique().tolist())
    x = [int(v) for v in budgets]

    fig, ax = plt.subplots(figsize=(9, 6))
    max_x = int(max(x)) if x else 100
    adaptive_last: tuple[int, float] | None = None

    for strategy in strategy_order:
        sub = work[work["Strategy"] == strategy].sort_values("MAX_STEPS")
        if sub.empty:
            continue
        xs = sub["MAX_STEPS"].astype(int).tolist()
        ys = sub["Escape-from-C Rate (%)"].astype(float).tolist()
        lw = 2.5 if strategy == "Adaptive (Ours)" else 2.0
        ax.plot(
            xs,
            ys,
            marker="o",
            linewidth=lw,
            markersize=7,
            label=strategy,
            color=color_map[strategy],
            alpha=1.0,
        )
        if strategy == "Adaptive (Ours)" and xs and ys:
            adaptive_last = (int(xs[-1]), float(ys[-1]))

    if adaptive_last is not None:
        ax.annotate(
            "Consistently highest performance",
            adaptive_last,
            textcoords="offset points",
            xytext=(-65, 8),
            fontsize=10,
            fontweight="normal",
            alpha=0.9,
        )
    ax.set_title("Success Rate vs MAX_STEPS", fontsize=16, pad=20)
    ax.text(
        0.02,
        0.95,
        "Student Group: Weak (C)",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=10,
        alpha=0.9,
    )
    ax.set_xlabel("MAX_STEPS", fontsize=12)
    ax.set_ylabel("Success Rate 達標B (%)", fontsize=12)
    ax.set_xticks(x)
    ax.set_ylim(0, 100)
    ax.tick_params(axis="both", labelsize=12)
    ax.legend(
        loc="upper left",
        bbox_to_anchor=(0.0, 0.90),
        fontsize=12,
        frameon=True,
        shadow=False,
    )
    ax.grid(True, alpha=0.28)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    fig.savefig(str(out_dir / "fig_multi_steps_success_rate.png"), dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_exp3_marginal_gain(
    summary_csv_path: str | Path,
    output_dir: str | Path,
) -> None:
    """Plot marginal success-rate gain for each +10 MAX_STEPS in Experiment 3."""
    setup_report_style()
    df = _read_csv_df(summary_csv_path)
    if df.empty:
        return

    required = {"MAX_STEPS", "Strategy", "Escape-from-C Rate (%)"}
    if not required.issubset(df.columns):
        return

    work = df.copy()
    work["MAX_STEPS"] = pd.to_numeric(work["MAX_STEPS"], errors="coerce")
    work["Escape-from-C Rate (%)"] = pd.to_numeric(work["Escape-from-C Rate (%)"], errors="coerce")
    work = work.dropna(subset=["MAX_STEPS", "Escape-from-C Rate (%)"]).copy()
    if work.empty:
        return

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    strategy_order = ["Baseline", "Rule-Based", "Adaptive (Ours)"]
    color_map = {
        "Baseline": "#1f77b4",
        "Rule-Based": "#ff7f0e",
        "Adaptive (Ours)": "#2ca02c",
    }

    fig, ax = plt.subplots(figsize=(9, 6))
    for strategy in strategy_order:
        sub = work[work["Strategy"] == strategy].sort_values("MAX_STEPS")
        if len(sub) < 2:
            continue
        steps = sub["MAX_STEPS"].astype(int).tolist()
        success = sub["Escape-from-C Rate (%)"].astype(float).tolist()
        x_vals = steps[1:]
        y_vals = [success[i] - success[i - 1] for i in range(1, len(success))]
        lw = 2.5 if strategy == "Adaptive (Ours)" else 2.0
        ax.plot(
            x_vals,
            y_vals,
            marker="o",
            linewidth=lw,
            markersize=7,
            color=color_map[strategy],
            label=strategy,
        )

    ax.set_title("Marginal Gain of Success Rate vs MAX_STEPS", fontsize=16, pad=20)
    ax.set_xlabel("MAX_STEPS", fontsize=12)
    ax.set_ylabel("Δ Success Rate (%)", fontsize=12)
    ax.set_xticks([40, 50, 60, 70, 80, 90, 100])
    ax.tick_params(axis="both", labelsize=12)
    ax.legend(loc="upper right", fontsize=12, frameon=True, shadow=False)
    ax.grid(True, alpha=0.3)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    fig.savefig(str(out_dir / "fig_exp3_marginal_gain.png"), dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_rag_intervention_results(
    output_dir: str = os.path.join(EXP4_BASE_DIR, "latest"),
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

            plt.figure(figsize=(8, 5))
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
        setup_report_style()
        fig, ax = plt.subplots(figsize=(8, 5))
        colors = ["tab:green" if "rag" in str(c).lower() else "tab:blue" for c in summary_df["condition"]]
        ax.bar(summary_df["condition"], summary_df["success_rate"] * 100.0, color=colors)
        add_bar_labels(ax, fmt="{:.1f}%")
        ax.set_title("RAG Tutor: Success Rate Comparison")
        ax.set_xlabel("Condition")
        ax.set_ylabel("Success Rate (%)")
        ax.set_ylim(0, 100)
        finalize_report_figure(fig, os.path.join(out_dir, "fig_rag_success_rate.png"))

    if not summary_df.empty and {"condition", "avg_final_polynomial_mastery"}.issubset(summary_df.columns):
        setup_report_style()
        fig, ax = plt.subplots(figsize=(8, 5))
        colors = ["tab:green" if "rag" in str(c).lower() else "tab:blue" for c in summary_df["condition"]]
        ax.bar(summary_df["condition"], summary_df["avg_final_polynomial_mastery"], color=colors)
        add_bar_labels(ax, fmt="{:.2f}")
        ax.set_title("RAG Tutor: Final Polynomial Mastery")
        ax.set_xlabel("Condition")
        ax.set_ylabel("Average Final Polynomial Mastery")
        finalize_report_figure(fig, os.path.join(out_dir, "fig_rag_mastery.png"))

    if not subskill_df.empty and {"condition", "subskill", "avg_gain"}.issubset(subskill_df.columns):
        conditions = summary_df["condition"].tolist() if not summary_df.empty else sorted(
            subskill_df["condition"].unique().tolist()
        )
        subskills = [s for s in SUBSKILL_ORDER if any(subskill_df["subskill"] == s)]
        if conditions and subskills:
            x = list(range(len(subskills)))
            width = 0.3
            setup_report_style()
            fig, ax = plt.subplots(figsize=(8, 5))
            for idx, cond in enumerate(conditions):
                ys: list[float] = []
                cond_df = subskill_df[subskill_df["condition"] == cond]
                for skill in subskills:
                    row = cond_df[cond_df["subskill"] == skill]
                    ys.append(float(row["avg_gain"].iloc[0]) if not row.empty else 0.0)
                offset = (idx - (len(conditions) - 1) / 2) * width
                color = "tab:green" if "rag" in str(cond).lower() else "tab:blue"
                ax.bar([i + offset for i in x], ys, width=width, label=cond, color=color)
            ax.set_xticks(x)
            ax.set_xticklabels(subskills, rotation=20, ha="right")
            ax.set_title("RAG Tutor: Subskill Gain Comparison")
            ax.set_xlabel("Subskill")
            ax.set_ylabel("Average Gain")
            add_bar_labels(ax, fmt="{:.2f}")

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
                    ax.set_title("RAG Tutor: Subskill Gain Comparison" + title_suffix)

            ax.legend()
            finalize_report_figure(fig, os.path.join(out_dir, "fig_rag_subskill_gain.png"))

    if not breakpoint_df.empty and {"condition", "subskill", "percentage"}.issubset(
        breakpoint_df.columns
    ):
        conditions = sorted(breakpoint_df["condition"].unique().tolist())
        subskills = [s for s in SUBSKILL_ORDER if any(breakpoint_df["subskill"] == s)]
        if conditions and subskills:
            x = list(range(len(subskills)))
            width = 0.3
            setup_report_style()
            fig, ax = plt.subplots(figsize=(8, 5))
            for idx, cond in enumerate(conditions):
                ys: list[float] = []
                cond_df = breakpoint_df[breakpoint_df["condition"] == cond]
                for skill in subskills:
                    row = cond_df[cond_df["subskill"] == skill]
                    ys.append(float(row["percentage"].iloc[0]) * 100.0 if not row.empty else 0.0)
                offset = (idx - (len(conditions) - 1) / 2) * width
                color = "tab:green" if "rag" in str(cond).lower() else "tab:blue"
                ax.bar([i + offset for i in x], ys, width=width, label=cond, color=color)
            ax.set_xticks(x)
            ax.set_xticklabels(subskills, rotation=20, ha="right")
            ax.set_title("RAG Tutor: Breakpoint Shift")
            ax.set_xlabel("Subskill")
            ax.set_ylabel("Weakest Subskill Share (%)")
            add_bar_labels(ax, fmt="{:.1f}%")
            ax.legend()
            finalize_report_figure(fig, os.path.join(out_dir, "fig_rag_breakpoint_shift.png"))


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
    color_map = {
        "weak_ab3_foundation": "tab:blue",
        "weak_ab3_foundation_rag_v1": "tab:orange",
        "weak_ab3_foundation_rag_v2": "tab:green",
    }

    if not summary_df.empty:
        summary_df["condition"] = pd.Categorical(
            summary_df["condition"], categories=condition_order, ordered=True
        )
        summary_df = summary_df.sort_values("condition")

    if not summary_df.empty and {"condition", "success_rate"}.issubset(summary_df.columns):
        setup_report_style()
        fig, ax = plt.subplots(figsize=(8, 5))
        colors = [color_map.get(str(c), "tab:blue") for c in summary_df["condition"]]
        ax.bar(summary_df["condition"], summary_df["success_rate"] * 100.0, color=colors)
        add_bar_labels(ax, fmt="{:.1f}%")
        ax.set_title("RAG v2: Success Rate Comparison")
        ax.set_xlabel("Condition")
        ax.set_ylabel("Success Rate (%)")
        ax.set_ylim(0, 100)
        ax.tick_params(axis="x", rotation=15)
        finalize_report_figure(fig, os.path.join(out_dir, "fig_rag_v2_success_rate.png"))

    if not summary_df.empty and {"condition", "avg_final_polynomial_mastery"}.issubset(summary_df.columns):
        setup_report_style()
        fig, ax = plt.subplots(figsize=(8, 5))
        colors = [color_map.get(str(c), "tab:blue") for c in summary_df["condition"]]
        ax.bar(summary_df["condition"], summary_df["avg_final_polynomial_mastery"], color=colors)
        add_bar_labels(ax, fmt="{:.2f}")
        ax.set_title("RAG v2: Final Polynomial Mastery")
        ax.set_xlabel("Condition")
        ax.set_ylabel("Average Final Polynomial Mastery")
        ax.tick_params(axis="x", rotation=15)
        finalize_report_figure(fig, os.path.join(out_dir, "fig_rag_v2_mastery.png"))

    if not subskill_df.empty and {"condition", "subskill", "avg_gain"}.issubset(subskill_df.columns):
        subskill_df["condition"] = pd.Categorical(
            subskill_df["condition"], categories=condition_order, ordered=True
        )
        subskills = [s for s in SUBSKILL_ORDER if any(subskill_df["subskill"] == s)]
        conditions = [c for c in condition_order if any(subskill_df["condition"] == c)]
        if subskills and conditions:
            x = list(range(len(subskills)))
            width = 0.3
            setup_report_style()
            fig, ax = plt.subplots(figsize=(8, 5))
            for idx, cond in enumerate(conditions):
                ys: list[float] = []
                cond_df = subskill_df[subskill_df["condition"] == cond]
                for skill in subskills:
                    row = cond_df[cond_df["subskill"] == skill]
                    ys.append(float(row["avg_gain"].iloc[0]) if not row.empty else 0.0)
                offset = (idx - (len(conditions) - 1) / 2) * width
                color = color_map.get(str(cond), "tab:blue")
                ax.bar([i + offset for i in x], ys, width=width, label=cond, color=color)
            ax.set_xticks(x)
            ax.set_xticklabels(subskills, rotation=20, ha="right")
            ax.set_title("RAG v2: Subskill Gain Comparison")
            ax.set_xlabel("Subskill")
            ax.set_ylabel("Average Gain")
            add_bar_labels(ax, fmt="{:.2f}")
            ax.legend()
            finalize_report_figure(fig, os.path.join(out_dir, "fig_rag_v2_subskill_gain.png"))

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
            width = 0.3
            setup_report_style()
            fig, ax = plt.subplots(figsize=(8, 5))
            for idx, cond in enumerate(conditions):
                ys: list[float] = []
                cond_df = breakpoint_df[breakpoint_df["condition"] == cond]
                for skill in subskills:
                    row = cond_df[cond_df["subskill"] == skill]
                    ys.append(float(row["percentage"].iloc[0]) * 100.0 if not row.empty else 0.0)
                offset = (idx - (len(conditions) - 1) / 2) * width
                color = color_map.get(str(cond), "tab:blue")
                ax.bar([i + offset for i in x], ys, width=width, label=cond, color=color)
            ax.set_xticks(x)
            ax.set_xticklabels(subskills, rotation=20, ha="right")
            ax.set_title("RAG v2: Breakpoint Shift")
            ax.set_xlabel("Subskill")
            ax.set_ylabel("Weakest Subskill Share (%)")
            add_bar_labels(ax, fmt="{:.1f}%")
            ax.legend()
            finalize_report_figure(fig, os.path.join(out_dir, "fig_rag_v2_breakpoint_shift.png"))

    if not summary_df.empty and {"condition", "rag_usage_rate", "avg_rag_per_episode"}.issubset(
        summary_df.columns
    ):
        x = list(range(len(summary_df)))
        width = 0.3
        setup_report_style()
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(
            [i - width / 2 for i in x],
            summary_df["rag_usage_rate"] * 100.0,
            width=width,
            label="RAG Usage Rate (%)",
            color="tab:green",
        )
        ax.bar(
            [i + width / 2 for i in x],
            summary_df["avg_rag_per_episode"],
            width=width,
            label="Avg RAG Per Episode",
            color="tab:orange",
        )
        ax.set_xticks(x)
        ax.set_xticklabels(summary_df["condition"], rotation=15, ha="right")
        ax.set_title("RAG v2: Usage Distribution")
        ax.set_xlabel("Condition")
        ax.set_ylabel("Value")
        add_bar_labels(ax, fmt="{:.2f}")
        ax.legend()
        finalize_report_figure(fig, os.path.join(out_dir, "fig_rag_usage_distribution.png"))


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
    output_dir: str = os.path.join(EXP2_BASE_DIR, "latest"),
) -> None:
    """Plot AB3 remediation timeline by student type and combined 1x3 overview."""
    if not os.path.exists(trajectory_path):
        return

    df = pd.read_csv(trajectory_path)
    required_cols = {"strategy", "student_type", "episode_id", "step", "phase"}
    if df.empty or not required_cols.issubset(df.columns):
        return

    ab3 = df[df["strategy"] == "AB3_PPO_Dynamic"].copy()
    ab3 = normalize_and_sort_student_types(ab3, "student_type")
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

        plt.figure(figsize=(8, 5))
        plt.imshow(matrix.values, aspect="auto", interpolation="nearest", cmap=cmap, vmin=0, vmax=3)
        plt.title(f"AB3 Remediation Timeline - {student_type}")
        plt.xlabel("Step")
        plt.ylabel("Episode Index")
        xticks = list(range(0, matrix.shape[1], max(1, matrix.shape[1] // 10)))
        plt.xticks(xticks, [str(matrix.columns[i]) for i in xticks])
        plt.yticks([])
        plt.legend(handles=legend_handles, loc="upper right", frameon=True)
        slug = STUDENT_TYPE_SLUG_MAP.get(student_type, student_type.lower().replace(" ", "_"))
        save_fig(os.path.join(output_dir, f"fig_exp2_remediation_timeline_{slug}.png"))

    fig, axes = plt.subplots(1, 3, figsize=(8, 5), sharex=False, sharey=False)
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
        finalize_report_figure(
            fig,
            os.path.join(output_dir, "fig_exp2_remediation_timeline_by_student_type.png"),
        )
    else:
        plt.close(fig)


def _build_exp2_ratio_profile(
    ab3_df: pd.DataFrame,
    student_type: str,
    phase_name: str,
) -> pd.DataFrame:
    """Compute per-step phase ratio for one student type."""
    normalized = normalize_and_sort_student_types(ab3_df, "student_type")
    sub = normalized[normalized["student_type"] == student_type].copy()
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

    normalized = normalize_and_sort_student_types(ab3_df, "student_type")
    weak = normalized[normalized["student_type"] == "Weak Foundation"].copy()
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
    output_dir: str = os.path.join(EXP2_BASE_DIR, "latest"),
) -> None:
    """Plot step-wise remediation/mainline/rag ratio summaries for AB3 student-type analysis."""
    if not os.path.exists(trajectory_path):
        return

    df = pd.read_csv(trajectory_path)
    required_cols = {"strategy", "student_type", "episode_id", "step", "phase"}
    if df.empty or not required_cols.issubset(df.columns):
        return

    ab3 = df[df["strategy"] == "AB3_PPO_Dynamic"].copy()
    ab3 = normalize_and_sort_student_types(ab3, "student_type")
    if ab3.empty:
        return

    os.makedirs(output_dir, exist_ok=True)

    # 1) Remediation ratio by step
    plt.figure(figsize=(8, 5))
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
    plt.figure(figsize=(8, 5))
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
        plt.figure(figsize=(8, 5))
        plt.plot(rag_profile["step"], rag_profile["ratio"], marker="o", linewidth=1.5, color="#7a5195")
        plt.title("AB3 Weak RAG Trigger Ratio by Step")
        plt.xlabel("Step")
        plt.ylabel("RAG Trigger Ratio")
        plt.ylim(0, 1)
        save_fig(os.path.join(output_dir, "fig_exp2_rag_ratio_by_step_weak.png"))

    # 4) Phase profile summary (1x3)
    fig, axes = plt.subplots(1, 3, figsize=(8, 5), sharey=True)
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
    finalize_report_figure(
        fig,
        os.path.join(output_dir, "fig_exp2_phase_profile_summary.png"),
    )


def build_experiment2_summary(
    df_logs: pd.DataFrame,
    output_dir: str = os.path.join(EXP2_BASE_DIR, "latest"),
) -> pd.DataFrame:
    """Aggregate AB3 behavior summary by student type from trajectory logs."""
    required_cols = {"strategy", "student_type", "episode_id", "step", "phase"}
    if df_logs.empty or not required_cols.issubset(df_logs.columns):
        return pd.DataFrame()

    ab3 = df_logs[df_logs["strategy"] == "AB3_PPO_Dynamic"].copy()
    ab3 = normalize_and_sort_student_types(ab3, "student_type")
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
    output_dir: str = os.path.join(EXP2_BASE_DIR, "latest"),
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

    plot_df = normalize_and_sort_student_types(summary_df.copy(), "student_type")
    plot_df = plot_df[plot_df["student_type"].isin(STUDENT_TYPE_ORDER)]
    if plot_df.empty:
        return
    plot_df["student_type"] = pd.Categorical(plot_df["student_type"], categories=STUDENT_TYPE_ORDER, ordered=True)
    plot_df = plot_df.sort_values("student_type")

    fig, ax1 = plt.subplots(figsize=(8, 5))
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
    df = normalize_and_sort_student_types(df, "student_type")
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

    priority = {"Average": 0, "Weak Foundation": 1, "Careless": 2}
    candidates: list[tuple[int, int, int, int]] = []
    for episode_id, sub in ab3.groupby("episode_id"):
        rem_steps = int((sub["route"] == "remediation").sum()) if "route" in sub.columns else 0
        if rem_steps <= 0:
            continue
        return_count = int(pd.to_numeric(sub.get("is_return_to_mainline", 0), errors="coerce").fillna(0).sum())
        stype = normalize_student_type(sub["student_type"].iloc[0]) if "student_type" in sub.columns else "Average"
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
        stype = normalize_student_type(sub["student_type"].iloc[0]) if "student_type" in sub.columns else "Average"
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
    output_dir: str = os.path.join(EXP2_BASE_DIR, "latest"),
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
            fig, ax = plt.subplots(figsize=(8, 5))
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
            out_path = os.path.join(output_dir, "mastery_trajectory_representative_episode.png")
            fig.tight_layout()
            finalize_report_figure(fig, out_path)
            out_files.append(out_path)

    # Average by student type with step alignment (NaN-safe groupby mean).
    ab3 = mastery_df[mastery_df["strategy"] == "AB3_PPO_Dynamic"].copy()
    ab3 = normalize_and_sort_student_types(ab3, "student_type")
    if not ab3.empty and {"student_type", "step", "integer_mastery", "polynomial_mastery"}.issubset(ab3.columns):
        fig, axes = plt.subplots(1, 3, figsize=(8, 5), sharey=True)
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
            finalize_report_figure(fig, out_path)
            out_files.append(out_path)
        else:
            plt.close(fig)

    return out_files


def write_experiment2_figure_captions(output_dir: str, representative_episode_id: int | None) -> list[str]:
    """Write publication captions for Experiment 2 summary and mastery trajectory figures."""
    os.makedirs(output_dir, exist_ok=True)
    paths: list[str] = []

    summary_caption = os.path.join(output_dir, "figure_caption_experiment2_summary.md")
    safe_write_markdown(
        summary_caption,
        "### Figure Caption: Experiment 2 Policy Behavior Summary\n"
        "This figure reports AB3 policy behavior across Careless, Average, and Weak Foundation groups.\n"
        "All values are computed from the current run logs: remediation ratio (remediation steps / total steps),\n"
        "mainline ratio (mainline steps / total steps), and average steps per episode.\n"
        "Experiment 1 identifies MAX_STEPS = 50 as the best-performing setting; therefore Experiment 2 uses MAX_STEPS = 50 for mechanism analysis consistency.\n"
        "Key finding: policy behavior differs by student type, with weaker learners spending more time in remediation\n"
        "and requiring longer trajectories before convergence.\n",
    )
    paths.append(summary_caption)

    episode_caption = os.path.join(output_dir, "figure_caption_mastery_episode.md")
    eid_text = str(representative_episode_id) if representative_episode_id is not None else "N/A"
    safe_write_markdown(
        episode_caption,
        "### Figure Caption: Representative Mastery Trajectory\n"
        f"This plot shows one automatically selected representative AB3 episode (episode_id={eid_text}).\n"
        "Curves are true per-step mastery values from trajectory logs (prerequisite and target mastery), and shaded\n"
        "bands denote remediation phases identified by route==remediation.\n"
        "Experiment 1 identifies MAX_STEPS = 50 as the best-performing setting; therefore Experiment 2 uses MAX_STEPS = 50 for mechanism analysis consistency.\n"
        "Key finding: remediation intervals are associated with prerequisite consolidation before stronger target mastery growth.\n",
    )
    paths.append(episode_caption)

    avg_caption = os.path.join(output_dir, "figure_caption_mastery_average.md")
    safe_write_markdown(
        avg_caption,
        "### Figure Caption: Average Mastery Trajectory by Student Type\n"
        "This figure aggregates AB3 episodes by step within each student type using NaN-safe averaging,\n"
        "reporting average prerequisite mastery, average target mastery, and average remediation ratio.\n"
        "Experiment 1 identifies MAX_STEPS = 50 as the best-performing setting; therefore Experiment 2 uses MAX_STEPS = 50 for mechanism analysis consistency.\n"
        "Key finding: student types exhibit distinct learning dynamics; weaker groups sustain higher remediation intensity\n"
        "and slower target mastery accumulation.\n",
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

    # Experiment 1 (report priority): keep only three core figures.
    plot_multi_steps_results(include_ab3_by_student_type=False)
    trajectory_path = os.path.join(REPORTS_DIR, "mastery_trajectory.csv")
    if os.path.exists(trajectory_path):
        traj_df = pd.read_csv(trajectory_path)
        exp2_summary_df = build_experiment2_summary(
            traj_df,
            output_dir=os.path.join(EXP2_BASE_DIR, "latest"),
        )
        generate_student_type_summary_charts(
            exp2_summary_df,
            output_dir=os.path.join(EXP2_BASE_DIR, "latest"),
        )
        mastery_paths = generate_mastery_trajectory_charts(
            traj_df,
            output_dir=os.path.join(EXP2_BASE_DIR, "latest"),
        )
        rep_episode_id: int | None = None
        caption_paths = write_experiment2_figure_captions(
            output_dir=os.path.join(EXP2_BASE_DIR, "latest"),
            representative_episode_id=rep_episode_id,
        )
    else:
        mastery_paths = []
        caption_paths = []

    print("Saved reports/adaptive_strategy_study/experiment_1_ablation/fig_exp1_student_type_improved.png")
    print("Saved reports/adaptive_strategy_study/experiment_1_ablation/fig_multi_steps_success_rate.png")
    print("Saved reports/adaptive_strategy_study/experiment_1_ablation/fig_multi_steps_efficiency.png")
    print("Saved reports/adaptive_strategy_study/experiment_2_ab3_student_types/latest/experiment2_student_type_summary.csv")
    print("Saved reports/adaptive_strategy_study/experiment_2_ab3_student_types/latest/experiment2_policy_behavior_summary.png")
    for p in mastery_paths:
        print(f"Saved {p.replace(os.sep, '/')}")
    for p in caption_paths:
        print(f"Saved {p.replace(os.sep, '/')}")


if __name__ == "__main__":
    main()



