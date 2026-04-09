"""
[File Name]
run_weak_foundation_support_experiment.py

[Created Date]
2026-04-09

[Project]
Adaptive Math Learning System (Adaptive Summative + Teaching)

[Description]
This runner evaluates weak-learner foundation support cost curves under AB3 conditions.
It sweeps extra foundation support budgets, aggregates gains and bottlenecks,
and exports dedicated summaries and figures for weak-support behavior analysis.
The outputs are used as supporting evidence for weak-focused intervention design.

[Core Functionality]
- Run Weak-only AB3 simulations across multiple foundation extra-step settings
- Build support summary, subskill gain summary, and breakpoint distribution tables
- Compute marginal gains to analyze diminishing-return behavior
- Export experiment-specific CSV outputs and weak-support figures
- Sync outputs into experiment report subdirectories

[Related Experiments]
- Experiment 2: Student Type Analysis
- Experiment 4: Weak + RAG (Extension)

[Notes]
- No experiment logic is modified by this header.
- Added for maintainability and research documentation only.
"""

import csv
import random
from collections import Counter
from pathlib import Path

import simulate_student
from organize_experiment_outputs import sync_experiment_output_dirs
from plot_experiment_results import plot_weak_foundation_support_results

REPORTS_DIR = Path("reports")
EXP3_DIR = REPORTS_DIR / "experiment_3_weak_foundation_support"
FOUNDATION_EXTRA_STEPS_LIST = [0, 10, 20, 40, 50, 60]


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _mean_reached(values: list[int | None]) -> float | str:
    valid = [float(v) for v in values if v is not None]
    return (_mean(valid) if valid else "")


def run_condition(foundation_extra_steps: int) -> list[dict[str, object]]:
    """Run AB3 + Weak episodes under one foundation-extra budget condition."""
    simulate_student.WEAK_FOUNDATION_EXTRA_STEPS = int(foundation_extra_steps)
    random.seed(simulate_student.RANDOM_SEED + int(foundation_extra_steps))

    episodes: list[dict[str, object]] = []
    for episode_id in range(1, simulate_student.N_PER_TYPE + 1):
        episode, _ = simulate_student.simulate_episode(
            student_type="Weak",
            strategy_name="AB3_PPO_Dynamic",
            episode_id=episode_id,
        )
        episodes.append(episode)
    return episodes


def build_support_summary(all_episodes: dict[int, list[dict[str, object]]]) -> list[dict[str, object]]:
    """Build summary CSV rows for foundation support cost analysis."""
    rows: list[dict[str, object]] = []
    prev_success: float | None = None
    prev_mastery: float | None = None
    for extra_steps in FOUNDATION_EXTRA_STEPS_LIST:
        episodes = all_episodes.get(extra_steps, [])
        if not episodes:
            continue
        success_rate = round(_mean([float(e["success"]) for e in episodes]), 4)
        avg_final_mastery = round(_mean([float(e["final_mastery"]) for e in episodes]), 4)
        marginal_success = "" if prev_success is None else round(success_rate - prev_success, 4)
        marginal_mastery = "" if prev_mastery is None else round(avg_final_mastery - prev_mastery, 4)
        rows.append(
            {
                "foundation_extra_steps": extra_steps,
                "success_rate": success_rate,
                "avg_total_steps": round(_mean([float(e["total_steps"]) for e in episodes]), 4),
                "avg_mainline_steps": round(_mean([float(e["mainline_steps"]) for e in episodes]), 4),
                "avg_foundation_extra_used": round(
                    _mean([float(e["foundation_extra_used"]) for e in episodes]), 4
                ),
                "avg_final_polynomial_mastery": avg_final_mastery,
                "avg_reached_mastery_step": (
                    round(_mean_reached([e["reached_mastery_step"] for e in episodes]), 4)
                    if _mean_reached([e["reached_mastery_step"] for e in episodes]) != ""
                    else ""
                ),
                "avg_remediation_count": round(
                    _mean([float(e["remediation_count"]) for e in episodes]), 4
                ),
                "avg_unnecessary_remediations": round(
                    _mean([float(e["unnecessary_remediations"]) for e in episodes]), 4
                ),
                "marginal_success_gain": marginal_success,
                "marginal_mastery_gain": marginal_mastery,
            }
        )
        prev_success = success_rate
        prev_mastery = avg_final_mastery
    return rows


def build_subskill_summary(all_episodes: dict[int, list[dict[str, object]]]) -> list[dict[str, object]]:
    """Build per-subskill gain summary by foundation support condition."""
    rows: list[dict[str, object]] = []
    for extra_steps in FOUNDATION_EXTRA_STEPS_LIST:
        episodes = all_episodes.get(extra_steps, [])
        if not episodes:
            continue
        for subskill in simulate_student.POLYNOMIAL_SUBSKILLS:
            init_vals = [float(e["initial_subskills"][subskill]) for e in episodes]
            final_vals = [float(e["final_subskills"][subskill]) for e in episodes]
            avg_initial = _mean(init_vals)
            avg_final = _mean(final_vals)
            rows.append(
                {
                    "foundation_extra_steps": extra_steps,
                    "subskill": subskill,
                    "avg_initial_mastery": round(avg_initial, 4),
                    "avg_final_mastery": round(avg_final, 4),
                    "avg_gain": round(avg_final - avg_initial, 4),
                }
            )
    return rows


def build_breakpoint_summary(all_episodes: dict[int, list[dict[str, object]]]) -> list[dict[str, object]]:
    """Summarize failed-episode weakest subskill distribution by condition."""
    rows: list[dict[str, object]] = []
    for extra_steps in FOUNDATION_EXTRA_STEPS_LIST:
        episodes = all_episodes.get(extra_steps, [])
        failed = [e for e in episodes if int(e["success"]) == 0]
        weakest: list[str] = []
        for e in failed:
            final_map = e["final_subskills"]
            weakest.append(
                min(
                    simulate_student.POLYNOMIAL_SUBSKILLS,
                    key=lambda s: float(final_map[s]),
                )
            )
        total_failed = len(failed)
        counts = Counter(weakest)
        for subskill in simulate_student.POLYNOMIAL_SUBSKILLS:
            count = int(counts.get(subskill, 0))
            percentage = (count / total_failed) if total_failed > 0 else 0.0
            rows.append(
                {
                    "foundation_extra_steps": extra_steps,
                    "subskill": subskill,
                    "count": count,
                    "percentage": round(percentage, 4),
                }
            )
    return rows


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    """Write rows to CSV with UTF-8 BOM for Excel compatibility."""
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main() -> None:
    """Run Weak Foundation Support experiment (AB3 + Weak only)."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    EXP3_DIR.mkdir(parents=True, exist_ok=True)

    original_extra = simulate_student.WEAK_FOUNDATION_EXTRA_STEPS
    all_episodes: dict[int, list[dict[str, object]]] = {}

    try:
        for extra_steps in FOUNDATION_EXTRA_STEPS_LIST:
            print(f"Running Weak foundation support condition: extra_steps={extra_steps}")
            all_episodes[extra_steps] = run_condition(extra_steps)
    finally:
        simulate_student.WEAK_FOUNDATION_EXTRA_STEPS = original_extra

    summary_rows = build_support_summary(all_episodes)
    subskill_rows = build_subskill_summary(all_episodes)
    breakpoint_rows = build_breakpoint_summary(all_episodes)

    summary_path = EXP3_DIR / "weak_foundation_support_summary.csv"
    subskill_path = EXP3_DIR / "weak_foundation_subskill_summary.csv"
    breakpoint_path = EXP3_DIR / "weak_foundation_breakpoint_summary.csv"

    write_csv(
        summary_path,
        [
            "foundation_extra_steps",
            "success_rate",
            "avg_total_steps",
            "avg_mainline_steps",
            "avg_foundation_extra_used",
            "avg_final_polynomial_mastery",
            "avg_reached_mastery_step",
            "avg_remediation_count",
            "avg_unnecessary_remediations",
            "marginal_success_gain",
            "marginal_mastery_gain",
        ],
        summary_rows,
    )
    write_csv(
        subskill_path,
        [
            "foundation_extra_steps",
            "subskill",
            "avg_initial_mastery",
            "avg_final_mastery",
            "avg_gain",
        ],
        subskill_rows,
    )
    write_csv(
        breakpoint_path,
        [
            "foundation_extra_steps",
            "subskill",
            "count",
            "percentage",
        ],
        breakpoint_rows,
    )

    plot_weak_foundation_support_results(str(EXP3_DIR))
    sync_experiment_output_dirs()

    print("Weak Foundation Support experiment completed.")
    print(f"Output CSV: {summary_path}")
    print(f"Output CSV: {subskill_path}")
    print(f"Output CSV: {breakpoint_path}")
    print(f"Output Figure: {EXP3_DIR / 'fig_weak_foundation_success_rate.png'}")
    print(f"Output Figure: {EXP3_DIR / 'fig_weak_foundation_mastery.png'}")
    print(f"Output Figure: {EXP3_DIR / 'fig_weak_foundation_breakpoint_shift.png'}")
    print(f"Output Figure: {EXP3_DIR / 'fig_weak_foundation_subskill_gain.png'}")


if __name__ == "__main__":
    main()
