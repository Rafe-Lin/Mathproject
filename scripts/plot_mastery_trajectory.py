# -*- coding: utf-8 -*-
# ==============================================================================
# ID: plot_mastery_trajectory.py
# Version: V1.0.0 (Mastery Trajectory Figures)
# Last Updated: 2026-04-15
# Author: *Steve
#
# [Description]:
#   讀取實驗輸出 CSV，依學生類型與策略繪製多項式掌握度軌跡圖，
#   與 figure_style 共用出版級樣式。
#
# [Database Schema Usage]:
#   無直接資料庫操作。
#
# [Logic Flow]:
#   1. 載入資料並依策略著色。
#   2. 繪製子圖與圖例。
#   3. 輸出 PNG。
# ==============================================================================
import os
import sys
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

_STUDY = Path(__file__).resolve().parent / "adaptive_strategy_study"
if str(_STUDY) not in sys.path:
    sys.path.insert(0, str(_STUDY))
import study_paths as _study_paths  # noqa: E402

_SR = _study_paths.study_reports_root()
_EXP2_LATEST = _SR / "experiment_2_ab3_student_types" / "latest"

from figure_style import (  # noqa: E402
    add_threshold_line,
    color_for_strategy,
    save_figure,
    setup_publication_style,
    style_axes,
    style_legend,
)

setup_publication_style()


def plot_by_student_type(df: pd.DataFrame) -> None:
    student_types = ["Careless", "Average", "Weak"]
    subplot_titles = {
        "Careless": "Careless Students",
        "Average": "Average Students",
        "Weak": "Weak Students",
    }
    strategy_colors = {
        "AB1_Baseline": color_for_strategy("AB1_Baseline"),
        "AB2_RuleBased": color_for_strategy("AB2_RuleBased"),
        "AB3_PPO_Dynamic": color_for_strategy("AB3_PPO_Dynamic"),
    }

    fig, axes = plt.subplots(1, 3, figsize=(18, 5), sharey=True)
    for ax, student_type in zip(axes, student_types):
        sub_df = df[df["student_type"] == student_type]
        if not sub_df.empty:
            curve = (
                sub_df.groupby(["strategy", "step"], as_index=False)["polynomial_mastery"]
                .mean()
            )
            for strategy in ["AB1_Baseline", "AB2_RuleBased", "AB3_PPO_Dynamic"]:
                strategy_curve = curve[curve["strategy"] == strategy]
                if strategy_curve.empty:
                    continue
                ax.plot(
                    strategy_curve["step"],
                    strategy_curve["polynomial_mastery"],
                    label=strategy,
                    color=strategy_colors[strategy],
                )
        else:
            ax.text(0.5, 0.5, "No data", ha="center", va="center", transform=ax.transAxes)

        add_threshold_line(ax, y=0.85, label="TARGET_MASTERY")
        ax.set_title(subplot_titles[student_type])
        ax.set_xlabel("Step")
        ax.set_ylim(0.0, 1.0)
        style_axes(ax, ygrid=True)
        style_legend(ax, loc="upper left")

    axes[0].set_ylabel("Mean Polynomial Mastery")
    fig.suptitle("Mastery Trajectory by Student Type")
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    save_figure(fig, str(_EXP2_LATEST / "fig_mastery_trajectory_by_student_type.png"), dpi=300)


def main() -> None:
    input_path = str(_EXP2_LATEST / "mastery_trajectory.csv")
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Missing input CSV: {input_path}")

    df = pd.read_csv(input_path)
    df = df.sort_values(["strategy", "student_type", "episode_id", "step"])

    # 圖1：AB1/AB2/AB3 的平均 polynomial mastery vs step（全體學生）
    overall = (
        df.groupby(["strategy", "step"], as_index=False)["polynomial_mastery"]
        .mean()
    )
    plt.figure(figsize=(9, 5))
    for strategy in sorted(overall["strategy"].unique()):
        sub = overall[overall["strategy"] == strategy]
        plt.plot(sub["step"], sub["polynomial_mastery"], label=strategy)
    plt.title("Overall Mean Polynomial Mastery by Step")
    plt.xlabel("Step")
    plt.ylabel("Mean Polynomial Mastery")
    plt.ylim(0.0, 1.0)
    ax = plt.gca()
    style_axes(ax, ygrid=True)
    style_legend(ax, loc="upper left")
    fig = plt.gcf()
    fig.tight_layout()
    save_figure(fig, str(_EXP2_LATEST / "fig_mastery_trajectory_overall.png"), dpi=300)

    # 圖2：Average 學生三策略平均 polynomial mastery vs step
    avg_df = df[df["student_type"] == "Average"]
    avg_curve = (
        avg_df.groupby(["strategy", "step"], as_index=False)["polynomial_mastery"]
        .mean()
    )
    plt.figure(figsize=(9, 5))
    for strategy in sorted(avg_curve["strategy"].unique()):
        sub = avg_curve[avg_curve["strategy"] == strategy]
        plt.plot(sub["step"], sub["polynomial_mastery"], label=strategy)
    plt.title("Average Students: Mean Polynomial Mastery by Step")
    plt.xlabel("Step")
    plt.ylabel("Mean Polynomial Mastery")
    plt.ylim(0.0, 1.0)
    ax = plt.gca()
    style_axes(ax, ygrid=True)
    style_legend(ax, loc="upper left")
    fig = plt.gcf()
    fig.tight_layout()
    save_figure(fig, str(_EXP2_LATEST / "fig_mastery_trajectory_average.png"), dpi=300)

    plot_by_student_type(df)

    print(f"Saved {_EXP2_LATEST / 'fig_mastery_trajectory_overall.png'}")
    print(f"Saved {_EXP2_LATEST / 'fig_mastery_trajectory_average.png'}")
    print(f"Saved {_EXP2_LATEST / 'fig_mastery_trajectory_by_student_type.png'}")


if __name__ == "__main__":
    main()
