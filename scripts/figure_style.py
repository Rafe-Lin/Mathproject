# -*- coding: utf-8 -*-
# ==============================================================================
# ID: figure_style.py
# Version: V1.0.0 (Publication Matplotlib Style)
# Last Updated: 2026-04-15
# Author: *Steve
#
# [Description]:
#   實驗報告共用 matplotlib 樣式：色票、字體、座標軸與圖例格式，
#   供 plot_experiment_results、plot_mastery_trajectory 等模組匯入。
#
# [Database Schema Usage]:
#   無直接資料庫操作。
#
# [Logic Flow]:
#   1. 設定 rcParams 與策略色對照。
#   2. 提供儲存圖檔與軸線裝飾輔助函式。
# ==============================================================================

from __future__ import annotations

from typing import Iterable

import matplotlib as mpl
import matplotlib.pyplot as plt

# Semantic palette (low-saturation, report-friendly).
PALETTE = {
    "baseline": "#5AA0CC",      # report-style blue
    "rule_based": "#F0A44B",    # report-style orange
    "adaptive": "#73B978",      # report-style green
    "warning": "#A25C5C",       # muted red
    "reference": "#7F7F7F",     # neutral gray
    "text": "#333333",
    "note": "dimgray",
    "grid": "#D0D0D0",
}

STRATEGY_COLORS = {
    "AB1_Baseline": PALETTE["baseline"],
    "AB2_RuleBased": PALETTE["rule_based"],
    "AB3_PPO_Dynamic": PALETTE["adaptive"],
}


def setup_publication_style() -> None:
    """Apply a unified figure style across all report plotting scripts."""
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": [
                "Microsoft JhengHei",
                "PingFang TC",
                "Noto Sans CJK TC",
                "DejaVu Sans",
                "Arial",
            ],
            "axes.unicode_minus": False,
            "axes.titlesize": 13,
            "axes.labelsize": 11,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "legend.fontsize": 10,
            "axes.edgecolor": "#555555",
            "axes.linewidth": 0.9,
            "axes.facecolor": "white",
            "grid.color": PALETTE["grid"],
            "grid.linestyle": "--",
            "grid.linewidth": 0.8,
            "grid.alpha": 0.30,
            "lines.linewidth": 2.0,
            "lines.markersize": 5,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
        }
    )


def color_for_strategy(strategy: str, fallback: str = "#7F7F7F") -> str:
    """Return a stable semantic color for known strategy IDs."""
    return STRATEGY_COLORS.get(strategy, fallback)


def add_bar_value_labels(ax: plt.Axes, *, fmt: str = "{:.2f}", fontsize: float = 9, y_offset: int = 4) -> None:
    """Annotate all bars in the axis with values."""
    for bar in ax.patches:
        h = bar.get_height()
        if h != h:  # NaN-safe
            continue
        ax.annotate(
            fmt.format(float(h)),
            (bar.get_x() + bar.get_width() / 2, h),
            textcoords="offset points",
            xytext=(0, y_offset),
            ha="center",
            va="bottom",
            fontsize=fontsize,
            color=PALETTE["text"],
        )


def add_figure_note(fig: plt.Figure, text: str, *, y: float = 0.04, fontsize: float = 9.0) -> None:
    """Add a centered multi-line caption-style note at figure bottom."""
    fig.text(0.5, y, text, ha="center", va="center", fontsize=fontsize, color=PALETTE["note"])


def add_threshold_line(ax: plt.Axes, y: float, *, label: str = "Threshold") -> None:
    """Add a standardized threshold line."""
    ax.axhline(y=y, color=PALETTE["warning"], linestyle=":", linewidth=1.4, label=label)


def mark_optimal_point(ax: plt.Axes, x: float, y: float, text: str) -> None:
    """Mark and label one important point in a curve/trade-off plot."""
    ax.scatter([x], [y], color=PALETTE["adaptive"], s=52, zorder=5, edgecolor="white", linewidth=0.8)
    ax.annotate(
        text,
        (x, y),
        textcoords="offset points",
        xytext=(8, 8),
        fontsize=9,
        color=PALETTE["text"],
        bbox={"boxstyle": "round,pad=0.2", "fc": "white", "ec": "#C0C0C0", "lw": 0.7, "alpha": 0.95},
    )


def style_axes(ax: plt.Axes, *, ygrid: bool = True) -> None:
    """Apply default axis formatting used across report figures."""
    ax.tick_params(axis="both", labelsize=10, colors=PALETTE["text"])
    for spine in ax.spines.values():
        spine.set_linewidth(0.9)
        spine.set_color("#555555")
    if ygrid:
        ax.grid(axis="y")
        ax.set_axisbelow(True)


def style_legend(ax: plt.Axes, *, loc: str = "upper left", ncol: int = 1) -> None:
    """Apply consistent legend style."""
    handles, labels = ax.get_legend_handles_labels()
    if not handles:
        return
    ax.legend(
        loc=loc,
        ncol=ncol,
        frameon=True,
        framealpha=1.0,
        facecolor="white",
        edgecolor="#C8C8C8",
        fontsize=9.5,
    )


def save_figure(fig: plt.Figure, path: str, *, dpi: int = 300) -> None:
    """Save figure with report-wide output quality settings."""
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)


def apply_strategy_colors_in_order(strategies: Iterable[str]) -> list[str]:
    """Map a strategy sequence to consistent colors."""
    return [color_for_strategy(s) for s in strategies]
