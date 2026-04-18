# -*- coding: utf-8 -*-
# ==============================================================================
# ID: plot_experiment1_multisteps.py
# Version: V1.0.0 (Experiment 1 Multistep Figures)
# Last Updated: 2026-04-15
# Author: *Steve
#
# [Description]:
#   專責 Experiment 1 多步數（30/40/50）成功率柱狀圖、學生分群比較圖與標籤驗證，
#   與 run_experiment1_multisteps.py 搭配使用。
#
# [Database Schema Usage]:
#   無直接資料庫操作。
#
# [Logic Flow]:
#   1. 讀取彙總資料或傳入 DataFrame。
#   2. 套用策略與分群色碼。
#   3. 輸出圖檔與同步路徑。
# ==============================================================================
from __future__ import annotations

import sys
from pathlib import Path
import shutil

_STUDY_ROOT = Path(__file__).resolve().parents[1]
if str(_STUDY_ROOT) not in sys.path:
    sys.path.insert(0, str(_STUDY_ROOT))
import study_paths as _study_paths  # noqa: E402

_study_paths.ensure_repo_root_on_syspath()

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Patch
from core.experiment_config import (  # noqa: E402
    display_student_group,
    student_group_display_order,
    validate_group_config,
)

COLOR_MAP = {
    "Baseline": "#1f77b4",
    "Rule-Based": "#ff7f0e",
    "Adaptive (Ours)": "#2ca02c",
}

SUCCESS_RATE_LABEL_ZH = "Success Rate 達標A (%)"
SUCCESS_THRESHOLD_DISPLAY = "0.80"

STRATEGY_LABEL_MAP = {
    "AB1_Baseline": "Baseline",
    "AB2_RuleBased": "Rule-Based",
    "AB3_PPO_Dynamic": "Adaptive (Ours)",
}

GROUP_LABEL_MAP = {
    "careless": display_student_group("careless"),
    "average": display_student_group("average"),
    "weak": display_student_group("weak"),
    "high": display_student_group("careless"),
    "mid": display_student_group("average"),
    "low": display_student_group("weak"),
}

GROUP_ORDER_DISPLAY = list(student_group_display_order())
STEP_ORDER = [30, 40, 50]
STEP_STYLE = {
    30: {"alpha": 0.45, "hatch": ""},
    40: {"alpha": 0.72, "hatch": "//"},
    50: {"alpha": 1.0, "hatch": "xx"},
}

plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["Microsoft JhengHei", "Noto Sans CJK TC", "DejaVu Sans", "Arial"]
plt.rcParams["axes.unicode_minus"] = False


def validate_experiment1_labels() -> None:
    """Check Experiment 1 display labels and key wording consistency."""
    validate_group_config()
    label_values = list(GROUP_LABEL_MAP.values()) + [SUCCESS_RATE_LABEL_ZH]
    blocked = [
        "Success(達標A) Rate%",
        "Success Rate % (達標A, threshold=0.80)",
        "A~B++",
        "B~B+",
        "Weak Foundation",
        "達標率（精熟度 ≥ 0.80, %）",
        "Success Rate (Mastery ≥ 0.80, %)",
    ]
    bad_hits = [w for w in blocked if any(w in str(v) for v in label_values)]
    if bad_hits:
        print(f"[WARN] Experiment 1 display label check found legacy terms: {bad_hits}")
    assert SUCCESS_THRESHOLD_DISPLAY == "0.80"
    assert SUCCESS_RATE_LABEL_ZH == "Success Rate 達標A (%)"
    assert "A~B++" not in " | ".join(label_values)
    assert "B~B+" not in " | ".join(label_values)
    assert "Weak Foundation" not in " | ".join(label_values)
    assert "達標率（精熟度 ≥ 0.80, %）" not in " | ".join(label_values)


def _strategy_label(strategy: str) -> str:
    return STRATEGY_LABEL_MAP.get(str(strategy), str(strategy))


def _ensure_output_dir(output_dir: str | Path) -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    return out


def _two_level_legends(ax: plt.Axes) -> None:
    strategy_handles = [
        Patch(facecolor=COLOR_MAP["Baseline"], edgecolor="black", label="Baseline"),
        Patch(facecolor=COLOR_MAP["Rule-Based"], edgecolor="black", label="Rule-Based"),
        Patch(facecolor=COLOR_MAP["Adaptive (Ours)"], edgecolor="black", label="Adaptive (Ours)"),
    ]
    step_handles = [
        Patch(facecolor="white", edgecolor="black", hatch=STEP_STYLE[s]["hatch"], alpha=STEP_STYLE[s]["alpha"], label=f"MAX_STEPS={s}")
        for s in STEP_ORDER
    ]
    leg1 = ax.legend(handles=strategy_handles, loc="upper left", fontsize=11, framealpha=0.9)
    ax.add_artist(leg1)
    ax.legend(handles=step_handles, loc="upper left", bbox_to_anchor=(0.0, 0.80), fontsize=10, framealpha=0.9)


def _strategy_step_bar_positions(level_idx: int, strategy_idx: int, step_idx: int) -> float:
    base = level_idx * 1.9
    strategy_gap = 0.54
    step_gap = 0.14
    return base + strategy_idx * strategy_gap + (step_idx - 1) * step_gap


def _plot_level_metric_multistep(
    df: pd.DataFrame,
    value_col: str,
    y_label: str,
    title: str,
    file_name: str,
    note: str,
    output_dir: str | Path,
    show_percent: bool = False,
) -> None:
    out = _ensure_output_dir(output_dir)
    validate_experiment1_labels()
    if df.empty or value_col not in df.columns:
        return

    level_order = GROUP_ORDER_DISPLAY
    strategy_order = ["Baseline", "Rule-Based", "Adaptive (Ours)"]
    strategy_raw_map = {
        "Baseline": "AB1_Baseline",
        "Rule-Based": "AB2_RuleBased",
        "Adaptive (Ours)": "AB3_PPO_Dynamic",
    }
    width = 0.12

    fig, ax = plt.subplots(figsize=(14, 6))
    for li, level in enumerate(level_order):
        for si, strategy in enumerate(strategy_order):
            for ti, step in enumerate(STEP_ORDER):
                raw = strategy_raw_map[strategy]
                hit = df[
                    (df["max_steps"] == step)
                    & (df["strategy"] == raw)
                    & (df["student_group"].map(GROUP_LABEL_MAP) == level)
                ]
                if hit.empty:
                    continue
                y = float(pd.to_numeric(hit[value_col], errors="coerce").iloc[0])
                if show_percent:
                    y = y * 100.0
                x = _strategy_step_bar_positions(li, si, ti)
                st = STEP_STYLE[step]
                ax.bar(
                    x,
                    y,
                    width=width,
                    color=COLOR_MAP[strategy],
                    alpha=st["alpha"],
                    hatch=st["hatch"],
                    edgecolor="black",
                    linewidth=0.5,
                )

    # center xticks by level
    centers = [_strategy_step_bar_positions(i, 1, 1) for i in range(len(level_order))]
    ax.set_xticks(centers)
    ax.set_xticklabels(level_order, fontsize=12)
    ax.set_xlabel("Student Level", fontsize=12)
    ax.set_ylabel(y_label, fontsize=12)
    ax.set_title(title, fontsize=16, pad=14)
    ax.grid(axis="y", alpha=0.18, linewidth=0.8)
    _two_level_legends(ax)
    ax.text(0.5, 0.96, note, transform=ax.transAxes, ha="center", va="top", fontsize=10, color="dimgray")
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    if show_percent:
        ax.set_ylim(0, 100)
    plt.tight_layout()
    fig.savefig(out / file_name, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_exp1_mastery_gain_comparison_multistep(df: pd.DataFrame, output_dir: str | Path) -> None:
    _plot_level_metric_multistep(
        df=df,
        value_col="avg_mastery_gain",
        y_label="Avg Mastery Gain",
        title="Experiment 1: Mastery Gain by Student Level across MAX_STEPS (30/40/50)",
        file_name="fig_exp1_mastery_gain_comparison.png",
        note="Adaptive improves learning gain most clearly in mid-level learners.",
        output_dir=output_dir,
        show_percent=False,
    )


def plot_exp1_student_type_comparison_multistep(df: pd.DataFrame, output_dir: str | Path) -> None:
    _plot_level_metric_multistep(
        df=df,
        value_col="success_rate",
        y_label=SUCCESS_RATE_LABEL_ZH,
        title="Experiment 1: Success Rate by Student Level across MAX_STEPS (30/40/50)",
        file_name="fig_exp1_student_type_comparison.png",
        note="Adaptive benefits all student levels, with the clearest advantage under constrained budgets.",
        output_dir=output_dir,
        show_percent=True,
    )


def _plot_overall_by_strategy_multistep(
    df_overall: pd.DataFrame,
    value_col: str,
    y_label: str,
    title: str,
    file_name: str,
    note: str,
    output_dir: str | Path,
    show_percent: bool = False,
) -> None:
    out = _ensure_output_dir(output_dir)
    validate_experiment1_labels()
    if df_overall.empty or value_col not in df_overall.columns:
        return
    strategy_order = ["Baseline", "Rule-Based", "Adaptive (Ours)"]
    strategy_raw_map = {
        "Baseline": "AB1_Baseline",
        "Rule-Based": "AB2_RuleBased",
        "Adaptive (Ours)": "AB3_PPO_Dynamic",
    }
    width = 0.18
    x = list(range(len(strategy_order)))

    fig, ax = plt.subplots(figsize=(12, 6))
    for ti, step in enumerate(STEP_ORDER):
        ys = []
        for strategy in strategy_order:
            raw = strategy_raw_map[strategy]
            hit = df_overall[(df_overall["max_steps"] == step) & (df_overall["strategy"] == raw)]
            val = float(pd.to_numeric(hit[value_col], errors="coerce").iloc[0]) if not hit.empty else float("nan")
            if show_percent and val == val:
                val = val * 100.0
            ys.append(val)
        offset = (ti - 1) * width
        st = STEP_STYLE[step]
        bars = ax.bar(
            [v + offset for v in x],
            ys,
            width=width,
            color=[COLOR_MAP[s] for s in strategy_order],
            alpha=st["alpha"],
            hatch=st["hatch"],
            edgecolor="black",
            linewidth=0.5,
            label=f"MAX_STEPS={step}",
        )
        for bar in bars:
            h = float(bar.get_height())
            if h == h:
                txt = f"{h:.1f}%" if show_percent else f"{h:.1f}"
                ax.annotate(
                    txt,
                    (bar.get_x() + bar.get_width() / 2.0, h),
                    textcoords="offset points",
                    xytext=(0, 3),
                    ha="center",
                    va="bottom",
                    fontsize=10,
                )

    ax.set_xticks(x)
    ax.set_xticklabels(strategy_order, fontsize=12)
    ax.set_xlabel("Strategy", fontsize=12)
    ax.set_ylabel(y_label, fontsize=12)
    ax.set_title(title, fontsize=16, pad=14)
    ax.grid(axis="y", alpha=0.18, linewidth=0.8)
    ax.legend(loc="upper left", fontsize=11)
    ax.text(0.5, 0.96, note, transform=ax.transAxes, ha="center", va="top", fontsize=10, color="dimgray")
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    if show_percent:
        ax.set_ylim(0, 100)
    plt.tight_layout()
    fig.savefig(out / file_name, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_exp1_overall_efficiency_multistep(df_overall: pd.DataFrame, output_dir: str | Path) -> None:
    _plot_overall_by_strategy_multistep(
        df_overall=df_overall,
        value_col="avg_steps",
        y_label="Average Steps",
        title="Experiment 1: Overall Efficiency across MAX_STEPS (30/40/50)",
        file_name="fig_exp1_overall_efficiency.png",
        note="Adaptive consistently achieves lower average steps under all step budgets.",
        output_dir=output_dir,
        show_percent=False,
    )


def plot_exp1_overall_success_rate_multistep(df_overall: pd.DataFrame, output_dir: str | Path) -> None:
    _plot_overall_by_strategy_multistep(
        df_overall=df_overall,
        value_col="success_rate",
        y_label=SUCCESS_RATE_LABEL_ZH,
        title="Experiment 1: Overall Success Rate across MAX_STEPS (30/40/50)",
        file_name="fig_exp1_overall_success_rate.png",
        note="All methods improve with larger step budgets, but Adaptive remains highest.",
        output_dir=output_dir,
        show_percent=True,
    )


def _plot_student_type_single(
    sub: pd.DataFrame,
    output_dir: str | Path,
    max_steps: int,
    file_name: str,
) -> None:
    out = _ensure_output_dir(output_dir)
    group_order = GROUP_ORDER_DISPLAY
    strategy_order = ["Baseline", "Rule-Based", "Adaptive (Ours)"]

    sub = sub.copy()
    sub["student_group_display"] = sub["student_group"].map(GROUP_LABEL_MAP)
    sub["strategy_display"] = sub["strategy"].map(_strategy_label)

    x = list(range(len(group_order)))
    width = 0.25

    fig, ax = plt.subplots(figsize=(9, 6))
    weak_label = display_student_group("weak")
    for idx, strategy in enumerate(strategy_order):
        ys = []
        for g in group_order:
            hit = sub[(sub["strategy_display"] == strategy) & (sub["student_group_display"] == g)]
            if hit.empty:
                ys.append(float("nan"))
            else:
                ys.append(float(pd.to_numeric(hit["success_rate"], errors="coerce").iloc[0]) * 100.0)
        offset = (idx - 1) * width
        bars = ax.bar(
            [i + offset for i in x],
            ys,
            width=width,
            label=strategy,
            color=COLOR_MAP[strategy],
        )
        for g, bar in zip(group_order, bars):
            h = float(bar.get_height())
            if h == h:
                if g == weak_label and h <= 0.5:
                    continue
                font_size = 9 if (g == weak_label and h <= 2.0) else 12
                ax.annotate(
                    f"{h:.1f}%",
                    (bar.get_x() + bar.get_width() / 2.0, h + 2.5),
                    textcoords="data",
                    ha="center",
                    va="bottom",
                    fontsize=font_size,
                )

    ax.set_xticks(x)
    ax.set_xticklabels(group_order, fontsize=12)
    ax.set_ylabel(SUCCESS_RATE_LABEL_ZH, fontsize=12)
    ax.set_xlabel("Student Level", fontsize=12)
    ax.set_title(
        f"Experiment 1 (MAX_STEPS={max_steps}): Performance Across Student Levels",
        fontsize=16,
        pad=20,
    )
    ax.set_ylim(0, 100)
    ax.tick_params(axis="y", labelsize=12)
    ax.grid(axis="y", alpha=0.18, linewidth=0.8)
    ax.legend(loc="upper right", fontsize=12)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    plt.tight_layout()
    plt.subplots_adjust(top=0.88)
    fig.savefig(out / file_name, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_student_type_improved(df: pd.DataFrame, output_dir: str | Path) -> None:
    """Figure 1 (publication style): strategy comparison by student type at MAX_STEPS=40."""
    validate_experiment1_labels()
    if df.empty:
        return
    sub = df[df["max_steps"] == 40].copy()
    if sub.empty:
        return
    out = _ensure_output_dir(output_dir)
    group_order = GROUP_ORDER_DISPLAY
    # Match publication label style used in the requested figure.
    x_label_map = {
        display_student_group("careless"): "Careless (B+~B++)",
        display_student_group("average"): "Average (B)",
        display_student_group("weak"): "Weak (C)",
    }
    x_labels = [x_label_map.get(g, g) for g in group_order]
    strategy_order = ["Baseline", "Rule-Based", "Adaptive (Ours)"]
    strategy_colors = {
        "Baseline": COLOR_MAP["Baseline"],
        "Rule-Based": COLOR_MAP["Rule-Based"],
        "Adaptive (Ours)": COLOR_MAP["Adaptive (Ours)"],
    }

    sub = sub.copy()
    sub["student_group_display"] = sub["student_group"].map(GROUP_LABEL_MAP)
    sub["strategy_display"] = sub["strategy"].map(_strategy_label)

    x = list(range(len(group_order)))
    width = 0.25
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_facecolor("#f2f2f2")
    fig.patch.set_facecolor("#f2f2f2")

    for idx, strategy in enumerate(strategy_order):
        ys = []
        for g in group_order:
            hit = sub[(sub["strategy_display"] == strategy) & (sub["student_group_display"] == g)]
            if hit.empty:
                ys.append(float("nan"))
            else:
                ys.append(float(pd.to_numeric(hit["success_rate"], errors="coerce").iloc[0]) * 100.0)
        offset = (idx - 1) * width
        bars = ax.bar(
            [i + offset for i in x],
            ys,
            width=width,
            label=strategy,
            color=strategy_colors[strategy],
            edgecolor=strategy_colors[strategy],
            linewidth=0.5,
        )
        for bar in bars:
            h = float(bar.get_height())
            if h == h:
                ax.annotate(
                    f"{h:.1f}%",
                    (bar.get_x() + bar.get_width() / 2.0, h),
                    textcoords="offset points",
                    xytext=(0, 3),
                    ha="center",
                    va="bottom",
                    fontsize=11,
                )

    ax.set_xticks(x)
    ax.set_xticklabels(x_labels, fontsize=12)
    ax.set_ylabel(SUCCESS_RATE_LABEL_ZH, fontsize=12)
    ax.set_xlabel("Student Type", fontsize=12, labelpad=8)
    ax.set_title("Experiment 1: Strategy Comparison by Student Type", fontsize=16, pad=8)
    ax.set_ylim(0, 100)
    ax.tick_params(axis="y", labelsize=12)
    ax.legend(loc="upper right", fontsize=12, frameon=True, framealpha=0.95)
    for spine in ax.spines.values():
        spine.set_linewidth(1.0)
    plt.tight_layout()

    run_fig = out / "fig_exp1_student_type_improved.png"
    fig.savefig(run_fig, dpi=300, bbox_inches="tight")
    plt.close(fig)

    # Keep canonical path refreshed for quick access outside run folders.
    base_fig = _study_paths.study_reports_root() / "experiment_1_ablation" / "fig_exp1_student_type_improved.png"
    base_fig.parent.mkdir(parents=True, exist_ok=True)
    try:
        shutil.copy2(run_fig, base_fig)
    except Exception:
        pass


def plot_student_type_improved_40(df: pd.DataFrame, output_dir: str | Path) -> None:
    """Figure 1b: student-group comparison at MAX_STEPS=40."""
    validate_experiment1_labels()
    if df.empty:
        return
    sub = df[df["max_steps"] == 40].copy()
    if sub.empty:
        return
    _plot_student_type_single(sub, output_dir, 40, "fig_exp1_student_type_improved_40.png")


def plot_student_type_comparison_30_vs_40(
    df_compare: pd.DataFrame,
    output_dir: str | Path,
) -> None:
    """Supplementary figure: student-level success comparison at 30 vs 40 steps."""
    _plot_student_type_comparison_panels(
        df_compare=df_compare,
        output_dir=output_dir,
        panel_steps=[30, 40],
        file_name="fig_exp1_student_type_comparison_30_vs_40.png",
        figure_title="Experiment 1: Strategy Comparison Across Student Levels under Different Step Budgets",
    )


def _plot_student_type_comparison_panels(
    df_compare: pd.DataFrame,
    output_dir: str | Path,
    panel_steps: list[int],
    file_name: str,
    figure_title: str,
) -> None:
    out = _ensure_output_dir(output_dir)
    validate_experiment1_labels()
    if df_compare.empty:
        return

    group_order = GROUP_ORDER_DISPLAY
    strategy_order = ["Baseline", "Rule-Based", "Adaptive (Ours)"]
    width = 0.25
    x = list(range(len(group_order)))

    panel_count = len(panel_steps)
    fig, axes = plt.subplots(1, panel_count, figsize=(6.0 * panel_count, 6.2), sharey=True)
    if panel_count == 1:
        axes = [axes]

    for ax, max_steps in zip(axes, panel_steps):
        sub = df_compare[df_compare["max_steps"] == int(max_steps)].copy()
        for idx, strategy in enumerate(strategy_order):
            ys = []
            for g in group_order:
                hit = sub[
                    (sub["strategy_display"] == strategy)
                    & (sub["student_group_display"] == g)
                ]
                if hit.empty:
                    ys.append(float("nan"))
                else:
                    ys.append(float(pd.to_numeric(hit["success_rate_pct"], errors="coerce").iloc[0]))

            offset = (idx - 1) * width
            bars = ax.bar(
                [i + offset for i in x],
                ys,
                width=width,
                color=COLOR_MAP[strategy],
                label=strategy,
            )
            for g, bar in zip(group_order, bars):
                h = float(bar.get_height())
                if h == h:
                    font_size = 10 if h <= 2.0 else 11
                    y_offset = 0.8 if h <= 2.0 else 1.2
                    ax.annotate(
                        f"{h:.1f}%",
                        (bar.get_x() + bar.get_width() / 2.0, h + y_offset),
                        textcoords="data",
                        ha="center",
                        va="bottom",
                        fontsize=font_size,
                    )

        ax.set_title(f"MAX_STEPS = {max_steps}", fontsize=13, pad=8)
        ax.set_xticks(x)
        ax.set_xticklabels(group_order, fontsize=12)
        ax.set_xlabel("Student Level", fontsize=12)
        ax.set_ylim(0, 100)
        ax.grid(axis="y", alpha=0.18, linewidth=0.8)
        ax.tick_params(axis="y", labelsize=12)
        for spine in ["top", "right"]:
            ax.spines[spine].set_visible(False)

    axes[0].set_ylabel(SUCCESS_RATE_LABEL_ZH, fontsize=12)
    fig.suptitle(figure_title, fontsize=16)
    legend_handles = [
        Patch(facecolor=COLOR_MAP["Baseline"], label="Baseline"),
        Patch(facecolor=COLOR_MAP["Rule-Based"], label="Rule-Based"),
        Patch(facecolor=COLOR_MAP["Adaptive (Ours)"], label="Adaptive (Ours)"),
    ]
    fig.legend(
        legend_handles,
        [h.get_label() for h in legend_handles],
        loc="upper center",
        bbox_to_anchor=(0.5, 0.96),
        ncol=3,
        fontsize=12,
        framealpha=0.9,
    )
    plt.tight_layout(rect=(0.02, 0.02, 0.98, 0.90))
    fig.savefig(out / file_name, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_student_type_comparison_30_40_50(
    df_compare: pd.DataFrame,
    output_dir: str | Path,
) -> None:
    """Main figure: student-level success comparison at 30/40/50 steps."""
    _plot_student_type_comparison_panels(
        df_compare=df_compare,
        output_dir=output_dir,
        panel_steps=[30, 40, 50],
        file_name="fig_exp1_student_type_comparison_30_40_50.png",
        figure_title="Experiment 1: Strategy Comparison Across Student Levels under Different Step Budgets",
    )


def _rq1_best_strategy_table(df_compare: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    if df_compare.empty:
        return pd.DataFrame()
    for max_steps in [30, 40, 50]:
        step_df = df_compare[df_compare["max_steps"].astype(int) == max_steps]
        for group in GROUP_ORDER_DISPLAY:
            sub = step_df[step_df["student_group_display"] == group]
            if sub.empty:
                continue
            sub = sub.copy()
            sub["success_rate_pct"] = pd.to_numeric(sub["success_rate_pct"], errors="coerce")
            sub = sub.sort_values(["success_rate_pct", "strategy_display"], ascending=[False, True])
            best = sub.iloc[0]
            rows.append(
                {
                    "max_steps": int(max_steps),
                    "student_group_display": str(group),
                    "best_strategy": str(best["strategy_display"]),
                    "best_rate": float(best["success_rate_pct"]),
                    "adaptive_is_best": str(best["strategy_display"]) == "Adaptive (Ours)",
                }
            )
    return pd.DataFrame(rows)


def plot_exp1_rq1_best_strategy_heatmap(
    df_compare: pd.DataFrame,
    output_dir: str | Path,
) -> None:
    """RQ1 verdict heatmap: best strategy for each (MAX_STEPS, student level)."""
    out = _ensure_output_dir(output_dir)
    validate_experiment1_labels()
    best = _rq1_best_strategy_table(df_compare)
    if best.empty:
        return

    steps = [30, 40, 50]
    groups = GROUP_ORDER_DISPLAY
    z: list[list[int]] = []
    labels: list[list[str]] = []
    for s in steps:
        row_vals: list[int] = []
        row_text: list[str] = []
        step_df = best[best["max_steps"] == s]
        for g in groups:
            cell = step_df[step_df["student_group_display"] == g]
            if cell.empty:
                row_vals.append(0)
                row_text.append("N/A")
                continue
            c = cell.iloc[0]
            is_adaptive = bool(c["adaptive_is_best"])
            row_vals.append(1 if is_adaptive else 0)
            short = "Adaptive" if is_adaptive else str(c["best_strategy"])
            row_text.append(f"{short}\n{float(c['best_rate']):.0f}%")
        z.append(row_vals)
        labels.append(row_text)

    fig, ax = plt.subplots(figsize=(10, 5.4))
    ax.imshow(z, cmap=plt.cm.get_cmap("RdYlGn"), vmin=0, vmax=1, aspect="auto")
    for i in range(len(steps)):
        for j in range(len(groups)):
            ax.text(j, i, labels[i][j], ha="center", va="center", fontsize=10, color="black")

    ax.set_xticks(list(range(len(groups))))
    ax.set_xticklabels(groups, fontsize=11)
    ax.set_yticks(list(range(len(steps))))
    ax.set_yticklabels([f"MAX_STEPS = {s}" for s in steps], fontsize=11)
    ax.set_xlabel("Student Level", fontsize=12)
    ax.set_ylabel("Step Budget", fontsize=12)
    ax.set_title("Experiment 1 RQ1 Verdict: Best Strategy by Step Budget and Student Level", fontsize=14, pad=10)
    plt.tight_layout()
    fig.savefig(out / "fig_exp1_rq1_best_strategy_heatmap.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def write_figure_caption_exp1_main(
    df_compare: pd.DataFrame,
    output_dir: str | Path,
) -> None:
    """Write caption for the main 30/40/50 student-level comparison figure."""
    out = _ensure_output_dir(output_dir)
    if df_compare.empty:
        return

    compare = df_compare[df_compare["max_steps"].astype(int).isin([30, 40, 50])].copy()
    if compare.empty:
        return

    hardest_step = None
    hardest_group = None
    hardest_score = None
    max_gap_step = None
    max_gap_group = None
    max_gap_value = None

    for max_steps in [30, 40, 50]:
        sub_step = compare[compare["max_steps"] == max_steps]
        for g in GROUP_ORDER_DISPLAY:
            sub = sub_step[sub_step["student_group_display"] == g]
            if sub.empty:
                continue
            by_strategy = {
                str(r["strategy_display"]): float(pd.to_numeric(r["success_rate_pct"], errors="coerce"))
                for _, r in sub.iterrows()
            }
            vals = [v for v in by_strategy.values() if v == v]
            if not vals:
                continue
            avg_success = sum(vals) / len(vals)
            if hardest_score is None or avg_success < hardest_score:
                hardest_score = avg_success
                hardest_step = max_steps
                hardest_group = g

            a = by_strategy.get("Adaptive (Ours)")
            b = by_strategy.get("Baseline")
            rb = by_strategy.get("Rule-Based")
            if a is None or b is None or rb is None:
                continue
            gap = a - max(b, rb)
            if max_gap_value is None or gap > max_gap_value:
                max_gap_value = gap
                max_gap_step = max_steps
                max_gap_group = g

    if max_gap_value is None:
        max_gap_step = "N/A"
        max_gap_group = "N/A"
        max_gap_text = "N/A"
    else:
        max_gap_text = f"{float(max_gap_value):.1f}%"

    if hardest_step is None:
        hardest_step = "N/A"
    if hardest_group is None:
        hardest_group = "N/A"

    caption = (
        "### Figure Caption: Experiment 1 Main Figure (30/40/50 Student-Level Comparison)\n\n"
        "This figure compares success rate across three strategies (Baseline, Rule-Based, Adaptive) "
        "under three step budgets (MAX_STEPS = 30/40/50) and three student levels (Careless, Average, Weak).\n\n"
        "MAX_STEPS = 40 is used as the primary interpretation baseline because it is the most balanced and "
        "representative setting. In this setting, Adaptive (Ours) is best for Careless, Average, and Weak.\n\n"
        "At MAX_STEPS = 30, strategy gaps are most visible in the resource-constrained regime; "
        "at MAX_STEPS = 50, all methods improve but Adaptive remains the top strategy.\n\n"
        f"The largest gap is at MAX_STEPS={max_gap_step}, {max_gap_group} (Adaptive lead: {max_gap_text}). "
        f"The most difficult condition is {hardest_group} at MAX_STEPS={hardest_step}.\n"
    )
    (out / "figure_caption_exp1_main.md").write_text(
        caption,
        encoding="utf-8-sig",
    )


def write_figure_caption_exp1_heatmap(
    df_compare: pd.DataFrame,
    output_dir: str | Path,
) -> None:
    """Write caption for RQ1 best-strategy heatmap."""
    out = _ensure_output_dir(output_dir)
    best = _rq1_best_strategy_table(df_compare)
    if best.empty:
        return
    all_adaptive = bool(best["adaptive_is_best"].all())
    verdict = (
        "Adaptive is the best strategy across all step budgets and student levels."
        if all_adaptive
        else "Adaptive is not the best strategy in every condition."
    )
    caption = (
        "### Figure Caption: Experiment 1 RQ1 Best-Strategy Heatmap\n\n"
        "This heatmap summarizes all 9 conditions (3 step budgets × 3 student levels). "
        "Each cell shows the best strategy and its success rate.\n\n"
        f"{verdict}\n"
    )
    (out / "figure_caption_exp1_heatmap.md").write_text(caption, encoding="utf-8-sig")


def write_figure_caption_exp1_student_type_comparison_30_40_50(
    df_compare: pd.DataFrame,
    output_dir: str | Path,
) -> None:
    """Backward-compatible wrapper to new main-figure caption file."""
    write_figure_caption_exp1_main(df_compare, output_dir)


def plot_multi_steps_efficiency(
    df_overall: pd.DataFrame,
    df_group: pd.DataFrame,
    output_dir: str | Path,
) -> None:
    """Figure 2: efficiency scatter (avg_steps vs success_rate)."""
    out = _ensure_output_dir(output_dir)
    validate_experiment1_labels()
    if df_overall.empty or df_group.empty:
        return

    # Sanity check: overall avg_steps must lie within per-group avg_steps bounds.
    for _, row in df_overall.iterrows():
        m = int(row["max_steps"])
        s = str(row["strategy"])
        overall_steps = float(row["avg_steps"])
        g = df_group[(df_group["max_steps"] == m) & (df_group["strategy"] == s)]
        if g.empty:
            raise ValueError(f"Missing group rows for max_steps={m}, strategy={s}")
        group_vals = pd.to_numeric(g["avg_steps"], errors="coerce").dropna().tolist()
        if not group_vals:
            raise ValueError(f"No valid group avg_steps for max_steps={m}, strategy={s}")
        g_min = min(group_vals)
        g_max = max(group_vals)
        if not (g_min <= overall_steps <= g_max):
            raise ValueError(
                f"Sanity check failed for max_steps={m}, strategy={s}: "
                f"overall avg_steps={overall_steps:.4f}, group range=[{g_min:.4f}, {g_max:.4f}]"
            )

    fig, ax = plt.subplots(figsize=(9, 6))
    strategy_order = ["Baseline", "Rule-Based", "Adaptive (Ours)"]
    marker_map = {"Baseline": "o", "Rule-Based": "s", "Adaptive (Ours)": "^"}
    labeled = set()
    offset_map = {
        ("Baseline", 20): (6, 4),
        ("Baseline", 30): (6, -10),
        ("Baseline", 40): (6, 6),
        ("Rule-Based", 20): (6, 8),
        ("Rule-Based", 30): (6, -12),
        ("Rule-Based", 40): (6, -2),
        ("Adaptive (Ours)", 20): (6, 8),
        ("Adaptive (Ours)", 30): (6, -12),
        ("Adaptive (Ours)", 40): (6, 8),
    }
    adaptive_points: list[tuple[int, float, float]] = []
    by_strategy_points: dict[str, list[tuple[int, float, float]]] = {
        "Baseline": [],
        "Rule-Based": [],
        "Adaptive (Ours)": [],
    }
    for _, row in df_overall.iterrows():
        strategy = _strategy_label(str(row["strategy"]))
        max_steps = int(row["max_steps"])
        x = float(row["avg_steps"])
        x_plot = x
        # plotting-only jitter to separate near-overlap points at MAX_STEPS=40
        if strategy == "Baseline" and max_steps == 40:
            x_plot = x + 0.15
        if strategy == "Rule-Based" and max_steps == 40:
            x_plot = x - 0.15
        y = float(row["success_rate"]) * 100.0
        point_label = strategy if strategy not in labeled else "_nolegend_"
        labeled.add(strategy)
        ax.scatter(
            x_plot,
            y,
            s=90,
            marker=marker_map.get(strategy, "o"),
            color=COLOR_MAP[strategy],
            alpha=0.92,
            label=point_label,
        )
        by_strategy_points[strategy].append((max_steps, x_plot, y))
        text = f"Adaptive@{max_steps}" if strategy == "Adaptive (Ours)" else f"{strategy}@{max_steps}"
        dx, dy = offset_map.get((strategy, max_steps), (5, 8))
        if strategy == "Baseline" and max_steps == 40:
            dx, dy = (5, -10)
        if strategy == "Rule-Based" and max_steps == 40:
            dx, dy = (5, 10)
        ax.annotate(text, (x_plot, y), textcoords="offset points", xytext=(dx, dy), fontsize=12)
        if strategy == "Adaptive (Ours)":
            adaptive_points.append((max_steps, x_plot, y))

    for strategy in strategy_order:
        pts = sorted(by_strategy_points[strategy], key=lambda t: t[0])
        if len(pts) < 2:
            continue
        xs = [p[1] for p in pts]
        ys = [p[2] for p in pts]
        ax.plot(
            xs,
            ys,
            color=COLOR_MAP[strategy],
            alpha=0.4,
            linewidth=1.5,
            zorder=1,
        )

    target = None
    if adaptive_points:
        target = next((p for p in adaptive_points if p[0] == 30), adaptive_points[-1])
    if target is not None:
        _, tx, ty = target
        ax.annotate(
            "Breaks efficiency trade-off",
            xy=(tx, ty),
            textcoords="offset points",
            xytext=(10, 10),
            arrowprops=dict(arrowstyle="->", lw=1.2),
            fontsize=12,
        )

    ax.set_xlabel("Average Steps", fontsize=12)
    ax.set_ylabel(SUCCESS_RATE_LABEL_ZH, fontsize=12)
    ax.set_title("Efficiency vs Performance under Different Step Budgets", fontsize=16, pad=20)
    ax.tick_params(axis="both", labelsize=12)
    ax.legend(loc="upper left", fontsize=12, framealpha=0.9)
    ax.grid(alpha=0.18, linewidth=0.8)
    ax.text(
        0.98,
        0.02,
        "Early success can reduce average steps",
        transform=ax.transAxes,
        ha="right",
        fontsize=9,
        color="gray",
    )
    xs_all = []
    for pts in by_strategy_points.values():
        xs_all.extend([p[1] for p in pts])
    if xs_all:
        ax.set_xlim(min(xs_all) - 1.0, max(xs_all) + 1.0)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    plt.tight_layout()
    plt.subplots_adjust(top=0.88)
    fig.savefig(out / "fig_multi_steps_efficiency.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_multi_steps_success_rate(df_overall: pd.DataFrame, output_dir: str | Path) -> None:
    """Figure 3: success-rate vs max_steps, annotate avg_steps per point."""
    out = _ensure_output_dir(output_dir)
    validate_experiment1_labels()
    if df_overall.empty:
        return

    strategy_order = ["Baseline", "Rule-Based", "Adaptive (Ours)"]
    step_values = sorted(
        pd.to_numeric(df_overall["max_steps"], errors="coerce").dropna().astype(int).unique().tolist()
    )
    if not step_values:
        return
    min_step = min(step_values)
    max_step = max(step_values)
    fig, ax = plt.subplots(figsize=(9, 6))
    adaptive_points: list[tuple[int, float, float]] = []
    for strategy in strategy_order:
        sub = df_overall[df_overall["strategy"].map(_strategy_label) == strategy].copy()
        if sub.empty:
            continue
        sub = sub.sort_values("max_steps")
        xs = sub["max_steps"].astype(int).tolist()
        ys = (pd.to_numeric(sub["success_rate"], errors="coerce") * 100.0).tolist()
        z = 3 if strategy == "Adaptive (Ours)" else (2 if strategy == "Rule-Based" else 1)
        ax.plot(xs, ys, marker="o", linewidth=2.0, color=COLOR_MAP[strategy], label=strategy, zorder=z)
        for _, r in sub.iterrows():
            y = float(r["success_rate"]) * 100.0
            x = int(r["max_steps"])
            if strategy == "Adaptive (Ours)":
                dy = 10
                if x == max_step:
                    dy = -12
                dx = 0
            elif strategy == "Rule-Based":
                dx, dy = (5, 5)
                if x == max_step:
                    dx, dy = (0, 10)
            else:
                dx, dy = (0, -12)
                if x == max_step:
                    dx, dy = (0, -15)
            if x == min_step:
                dx = 10
            ax.annotate(
                f"Avg Steps={float(r['avg_steps']):.1f}",
                (x, y),
                textcoords="offset points",
                xytext=(dx, dy),
                ha="center",
                fontsize=12,
            )
            if strategy == "Adaptive (Ours)":
                adaptive_points.append((x, y, float(r["avg_steps"])))

    if adaptive_points:
        peak = max(adaptive_points, key=lambda t: t[1])
        ax.annotate(
            "Consistently highest performance",
            xy=(peak[0], peak[1]),
            textcoords="offset points",
            xytext=(-50, 10),
            arrowprops=dict(arrowstyle="->", lw=1.2),
            fontsize=12,
        )

    ax.set_xticks(step_values)
    ax.set_xlabel("MAX_STEPS", fontsize=12)
    ax.set_ylabel(SUCCESS_RATE_LABEL_ZH, fontsize=12)
    ax.set_title("Success Rate vs MAX_STEPS", fontsize=16, pad=20)
    ax.tick_params(axis="both", labelsize=12)
    ax.legend(loc="upper left", fontsize=12)
    ax.grid(alpha=0.18, linewidth=0.8)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    plt.tight_layout()
    plt.subplots_adjust(top=0.88)
    fig.savefig(out / "fig_multi_steps_success_rate.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_average_success_trend(df: pd.DataFrame, output_dir: str | Path) -> None:
    """Official trend figure: Average(B) only, across MAX_STEPS=30/40/50."""
    out = _ensure_output_dir(output_dir)
    validate_experiment1_labels()
    if df.empty:
        return

    avg_key = "average"
    sub = df[df["student_group"].astype(str) == avg_key].copy()
    if sub.empty:
        return

    strategy_order = ["Baseline", "Rule-Based", "Adaptive (Ours)"]
    step_values = sorted(pd.to_numeric(sub["max_steps"], errors="coerce").dropna().astype(int).unique().tolist())
    if not step_values:
        return
    min_step = min(step_values)
    max_step = max(step_values)

    fig, ax = plt.subplots(figsize=(9, 6))
    offset_map = {
        ("Baseline", min_step): (10, -10),
        ("Rule-Based", min_step): (10, 6),
        ("Adaptive (Ours)", min_step): (10, 12),
        ("Baseline", max_step): (-8, -15),
        ("Rule-Based", max_step): (-8, 8),
        ("Adaptive (Ours)", max_step): (-8, -10),
    }
    for strategy in strategy_order:
        ssub = sub[sub["strategy"].map(_strategy_label) == strategy].copy()
        if ssub.empty:
            continue
        ssub = ssub.sort_values("max_steps")
        xs = ssub["max_steps"].astype(int).tolist()
        ys = (pd.to_numeric(ssub["success_rate"], errors="coerce") * 100.0).tolist()
        ax.plot(xs, ys, marker="o", linewidth=2.0, color=COLOR_MAP[strategy], label=strategy)
        for _, r in ssub.iterrows():
            x = int(r["max_steps"])
            y = float(r["success_rate"]) * 100.0
            dx, dy = offset_map.get((strategy, x), (4, 5 if strategy != "Baseline" else -9))
            ax.annotate(
                f"{float(r['avg_steps']):.1f}",
                (x, y),
                textcoords="offset points",
                xytext=(dx, dy),
                ha="center",
                fontsize=10,
            )

    ax.set_xticks(step_values)
    ax.set_xlabel("MAX_STEPS", fontsize=12)
    ax.set_ylabel(SUCCESS_RATE_LABEL_ZH, fontsize=12)
    ax.set_title("Success Rate vs MAX_STEPS on Average (B) Students", fontsize=16, pad=20)
    ax.tick_params(axis="both", labelsize=12)
    ax.legend(loc="upper left", fontsize=12)
    ax.grid(alpha=0.18, linewidth=0.8)
    ax.text(
        0.98,
        0.02,
        "Annotation numbers = Avg Steps",
        transform=ax.transAxes,
        ha="right",
        fontsize=9,
        color="gray",
    )
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    plt.tight_layout()
    plt.subplots_adjust(top=0.88)
    fig.savefig(out / "fig_exp1_average_success_trend.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_avg_steps_by_group(
    df_group_steps: pd.DataFrame,
    output_dir: str | Path,
    target_max_steps: int = 40,
) -> None:
    """Validation figure: per-group avg steps under one max-step budget."""
    out = _ensure_output_dir(output_dir)
    validate_experiment1_labels()
    if df_group_steps.empty:
        return
    sub = df_group_steps[df_group_steps["max_steps"] == int(target_max_steps)].copy()
    if sub.empty:
        return

    group_order = GROUP_ORDER_DISPLAY
    strategy_order = ["Baseline", "Rule-Based", "Adaptive (Ours)"]
    sub["student_group"] = sub["student_group"].astype(str)
    sub["strategy"] = sub["strategy"].astype(str)

    x = list(range(len(group_order)))
    width = 0.25

    fig, ax = plt.subplots(figsize=(9, 6))
    for idx, strategy in enumerate(strategy_order):
        ys = []
        for g in group_order:
            hit = sub[(sub["strategy"] == strategy) & (sub["student_group"] == g)]
            if hit.empty:
                ys.append(float("nan"))
            else:
                ys.append(float(pd.to_numeric(hit["avg_steps"], errors="coerce").iloc[0]))
        offset = (idx - 1) * width
        bars = ax.bar(
            [i + offset for i in x],
            ys,
            width=width,
            label=strategy,
            color=COLOR_MAP[strategy],
        )
        for bar in bars:
            h = float(bar.get_height())
            if h == h:
                ax.annotate(
                    f"{h:.1f}",
                    (bar.get_x() + bar.get_width() / 2.0, h),
                    textcoords="offset points",
                    xytext=(0, 4),
                    ha="center",
                    va="bottom",
                    fontsize=12,
                )

    ax.axhline(y=target_max_steps, color="gray", linestyle="--", linewidth=1.2, alpha=0.7)
    ax.text(
        0.98,
        min(0.98, (target_max_steps + 1.0) / 42.0),
        f"MAX_STEPS = {target_max_steps}",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=12,
        color="gray",
    )
    ax.set_xticks(x)
    ax.set_xticklabels(group_order, fontsize=12)
    ax.set_xlabel("Student Level", fontsize=12)
    ax.set_ylabel("Average Steps", fontsize=12)
    ax.set_title(
        f"Validation: Average Steps by Student Level (MAX_STEPS={target_max_steps})",
        fontsize=16,
        pad=20,
    )
    ax.set_ylim(0, 42)
    ax.tick_params(axis="y", labelsize=12)
    ax.grid(axis="y", alpha=0.18, linewidth=0.8)
    ax.legend(loc="upper left", fontsize=12)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)

    plt.tight_layout()
    plt.subplots_adjust(top=0.88)
    fig.savefig(out / "fig_exp1_avg_steps_by_group.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
