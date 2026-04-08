import os
import pandas as pd
import matplotlib.pyplot as plt


def plot_by_student_type(df: pd.DataFrame) -> None:
    student_types = ["Careless", "Average", "Weak"]
    subplot_titles = {
        "Careless": "Careless Students",
        "Average": "Average Students",
        "Weak": "Weak Students",
    }
    strategy_colors = {
        "AB1_Baseline": "blue",
        "AB2_RuleBased": "orange",
        "AB3_PPO_Dynamic": "green",
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

        ax.axhline(y=0.85, color="gray", linestyle="--", label="TARGET_MASTERY")
        ax.set_title(subplot_titles[student_type])
        ax.set_xlabel("Step")
        ax.set_ylim(0.0, 1.0)
        ax.grid(alpha=0.3)
        ax.legend()

    axes[0].set_ylabel("Mean Polynomial Mastery")
    fig.suptitle("Mastery Trajectory by Student Type")
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig("reports/fig_mastery_trajectory_by_student_type.png", dpi=150)
    plt.close(fig)


def main() -> None:
    input_path = "reports/mastery_trajectory.csv"
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
    plt.grid(alpha=0.25)
    plt.legend()
    plt.tight_layout()
    plt.savefig("reports/fig_mastery_trajectory_overall.png", dpi=150)
    plt.close()

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
    plt.grid(alpha=0.25)
    plt.legend()
    plt.tight_layout()
    plt.savefig("reports/fig_mastery_trajectory_average.png", dpi=150)
    plt.close()

    plot_by_student_type(df)

    print("Saved reports/fig_mastery_trajectory_overall.png")
    print("Saved reports/fig_mastery_trajectory_average.png")
    print("Saved reports/fig_mastery_trajectory_by_student_type.png")


if __name__ == "__main__":
    main()
