"""
[File Name]
run_multi_steps_experiment.py

[Created Date]
2026-04-09

[Project]
Adaptive Math Learning System (Adaptive Summative + Teaching)

[Description]
This runner executes multi-budget AB experiments by sweeping MAX_STEPS settings.
It repeatedly calls the simulation entrypoint, preserves per-step result snapshots,
and builds cross-step summary tables for strategy-level and student-type-level comparisons.
The script also triggers cross-step plotting and output synchronization for reporting.

[Core Functionality]
- Override MAX_STEPS in batch mode (30/40/50) and run simulation rounds
- Preserve each round outputs with step-specific filenames to avoid overwrite
- Build cross-step merged summaries for strategy and strategy-by-student-type
- Regenerate multi-step comparison figures from merged summary tables
- Sync curated outputs into experiment subdirectories for presentation

[Related Experiments]
- Experiment 1: Baseline vs AB2 vs AB3
- Experiment 3: Policy Timing (AB3)

[Notes]
- No experiment logic is modified by this header.
- Added for maintainability and research documentation only.
"""

import os
import shutil
from pathlib import Path

import pandas as pd

import simulate_student
from plot_experiment_results import plot_multi_steps_results

MAX_STEPS_LIST = [30, 40, 50]
REPORTS_DIR = Path("reports")
EXP1_DIR = REPORTS_DIR / "experiment_1_ablation"
EXPERIMENT1_OUTPUT_DIR = (Path(__file__).resolve().parents[1] / "reports" / "experiment_1_ablation")

# Per-run outputs that should be preserved with a steps suffix.
PRESERVE_FILES = [
    "ablation_simulation_results.csv",
    "ablation_strategy_summary.csv",
    "ablation_strategy_by_student_type_summary.csv",
]

EXP1_ARTIFACTS = [
    "ablation_simulation_results.csv",
    "ablation_strategy_summary.csv",
    "ablation_strategy_by_student_type_summary.csv",
    "multi_steps_strategy_summary.csv",
    "multi_steps_strategy_by_type_summary.csv",
    "experiment1_summary_table.csv",
    "experiment1_summary_table.md",
    "fig_multi_steps_success_rate.png",
    "fig_multi_steps_efficiency.png",
]


def run_single_steps_experiment(max_steps: int) -> None:
    """Run one simulate_student round with an overridden MAX_STEPS."""
    simulate_student.MAX_STEPS = int(max_steps)
    simulate_student.main(output_mode="experiment1")


def preserve_step_outputs(max_steps: int) -> None:
    """Copy current report CSVs to step-suffixed files to avoid overwrite."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    EXP1_DIR.mkdir(parents=True, exist_ok=True)
    for filename in PRESERVE_FILES:
        src = REPORTS_DIR / filename
        if not src.exists():
            src = EXP1_DIR / filename
        if not src.exists():
            continue
        stem = src.stem
        dst = EXP1_DIR / f"{stem}_steps{max_steps}.csv"
        shutil.copy2(src, dst)


def consolidate_experiment1_outputs() -> None:
    """Move Experiment 1 artifacts from reports root into experiment_1_ablation."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    EXP1_DIR.mkdir(parents=True, exist_ok=True)
    for filename in EXP1_ARTIFACTS:
        src = REPORTS_DIR / filename
        if not src.exists():
            continue
        dst = EXP1_DIR / filename
        shutil.move(src, dst)


def build_multi_steps_strategy_summary(max_steps_list: list[int]) -> Path:
    """Merge per-step strategy summaries into one cross-step table."""
    rows: list[pd.DataFrame] = []
    for steps in max_steps_list:
        path = EXP1_DIR / f"ablation_strategy_summary_steps{steps}.csv"
        if not path.exists():
            continue
        df = pd.read_csv(path)
        if df.empty:
            continue
        df["max_steps"] = int(steps)
        df = df.rename(
            columns={
                "avg_final_polynomial_mastery": "avg_final_mastery",
                "avg_unnecessary_remediations": "avg_unnecessary_remediation",
            }
        )
        keep = [
            "max_steps",
            "strategy",
            "success_rate",
            "avg_steps",
            "avg_final_mastery",
            "avg_unnecessary_remediation",
        ]
        for col in keep:
            if col not in df.columns:
                df[col] = pd.NA
        rows.append(df[keep])

    out = EXP1_DIR / "multi_steps_strategy_summary.csv"
    if rows:
        pd.concat(rows, ignore_index=True).to_csv(out, index=False, encoding="utf-8-sig")
    else:
        pd.DataFrame(
            columns=[
                "max_steps",
                "strategy",
                "success_rate",
                "avg_steps",
                "avg_final_mastery",
                "avg_unnecessary_remediation",
            ]
        ).to_csv(out, index=False, encoding="utf-8-sig")
    return out


def build_multi_steps_strategy_by_type_summary(max_steps_list: list[int]) -> Path:
    """Merge per-step strategy x student_type summaries into one cross-step table."""
    rows: list[pd.DataFrame] = []
    for steps in max_steps_list:
        path = EXP1_DIR / f"ablation_strategy_by_student_type_summary_steps{steps}.csv"
        if not path.exists():
            continue
        df = pd.read_csv(path)
        if df.empty:
            continue
        df["max_steps"] = int(steps)
        df = df.rename(columns={"avg_final_polynomial_mastery": "avg_final_mastery"})
        keep = [
            "max_steps",
            "strategy",
            "student_type",
            "success_rate",
            "avg_steps",
            "avg_final_mastery",
        ]
        for col in keep:
            if col not in df.columns:
                df[col] = pd.NA
        rows.append(df[keep])

    out = EXP1_DIR / "multi_steps_strategy_by_type_summary.csv"
    if rows:
        pd.concat(rows, ignore_index=True).to_csv(out, index=False, encoding="utf-8-sig")
    else:
        pd.DataFrame(
            columns=[
                "max_steps",
                "strategy",
                "student_type",
                "success_rate",
                "avg_steps",
                "avg_final_mastery",
            ]
        ).to_csv(out, index=False, encoding="utf-8-sig")
    return out


def build_experiment1_summary_table_from_multi_steps() -> pd.DataFrame:
    """Build Experiment 1 final summary table from cross-step strategy summary."""
    src = EXP1_DIR / "multi_steps_strategy_summary.csv"
    if not src.exists():
        return pd.DataFrame(
            columns=[
                "MAX_STEPS",
                "Strategy",
                "Success Rate (%)",
                "Avg Steps",
                "Avg Unnecessary Remediations",
                "Avg Final Mastery",
            ]
        )

    df = pd.read_csv(src)
    if df.empty:
        return pd.DataFrame(
            columns=[
                "MAX_STEPS",
                "Strategy",
                "Success Rate (%)",
                "Avg Steps",
                "Avg Unnecessary Remediations",
                "Avg Final Mastery",
            ]
        )

    # Normalize source columns from existing summary output.
    if "avg_unnecessary_remediation" in df.columns:
        df["avg_unnecessary_remediations"] = df["avg_unnecessary_remediation"]

    keep = [
        "max_steps",
        "strategy",
        "success_rate",
        "avg_steps",
        "avg_unnecessary_remediations",
        "avg_final_mastery",
    ]
    for col in keep:
        if col not in df.columns:
            df[col] = pd.NA
    out = df[keep].copy()
    out = out.rename(
        columns={
            "max_steps": "MAX_STEPS",
            "strategy": "Strategy",
            "success_rate": "Success Rate (%)",
            "avg_steps": "Avg Steps",
            "avg_unnecessary_remediations": "Avg Unnecessary Remediations",
            "avg_final_mastery": "Avg Final Mastery",
        }
    )
    # success_rate in source is [0,1]; convert to percentage for final table.
    out["Success Rate (%)"] = pd.to_numeric(out["Success Rate (%)"], errors="coerce") * 100.0
    out["MAX_STEPS"] = pd.to_numeric(out["MAX_STEPS"], errors="coerce")

    strategy_order = {"AB1_Baseline": 0, "AB2_RuleBased": 1, "AB3_PPO_Dynamic": 2}
    out["_strategy_order"] = out["Strategy"].map(strategy_order).fillna(99)
    out = out.sort_values(["MAX_STEPS", "_strategy_order"]).drop(columns=["_strategy_order"])

    # Format all numeric columns to 2 decimals while keeping NaN-safe output.
    for col in [
        "Success Rate (%)",
        "Avg Steps",
        "Avg Unnecessary Remediations",
        "Avg Final Mastery",
    ]:
        out[col] = pd.to_numeric(out[col], errors="coerce").round(2)
    out["MAX_STEPS"] = out["MAX_STEPS"].astype("Int64")
    return out


def write_experiment1_summary_table(df: pd.DataFrame) -> tuple[Path, Path]:
    """Write Experiment 1 summary table in CSV and Markdown formats."""
    EXP1_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = EXP1_DIR / "experiment1_summary_table.csv"
    md_path = EXP1_DIR / "experiment1_summary_table.md"

    df.to_csv(csv_path, index=False, encoding="utf-8-sig")

    lines = [
        "# Experiment 1 Summary Table",
        "",
        "| MAX_STEPS | Strategy | Success Rate (%) | Avg Steps | Avg Unnecessary Remediations | Avg Final Mastery |",
        "|-----------|----------|------------------|-----------|------------------------------|-------------------|",
    ]
    for _, row in df.iterrows():
        def fmt_num(v: object) -> str:
            if pd.isna(v):
                return "NaN"
            return f"{float(v):.2f}"

        max_steps = "NaN" if pd.isna(row["MAX_STEPS"]) else str(int(row["MAX_STEPS"]))
        lines.append(
            "| "
            + " | ".join(
                [
                    max_steps,
                    str(row["Strategy"]),
                    fmt_num(row["Success Rate (%)"]),
                    fmt_num(row["Avg Steps"]),
                    fmt_num(row["Avg Unnecessary Remediations"]),
                    fmt_num(row["Avg Final Mastery"]),
                ]
            )
            + " |"
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8-sig")
    return csv_path, md_path


def main() -> None:
    """Run multiple MAX_STEPS experiments and generate cross-step summaries + plots."""
    original_max_steps = simulate_student.MAX_STEPS
    try:
        for steps in MAX_STEPS_LIST:
            print(f"\n=== Running simulate_student with MAX_STEPS={steps} ===")
            run_single_steps_experiment(steps)
            preserve_step_outputs(steps)

        strategy_out = build_multi_steps_strategy_summary(MAX_STEPS_LIST)
        by_type_out = build_multi_steps_strategy_by_type_summary(MAX_STEPS_LIST)
        exp1_table_df = build_experiment1_summary_table_from_multi_steps()
        exp1_csv, exp1_md = write_experiment1_summary_table(exp1_table_df)

        plot_multi_steps_results(include_ab3_by_student_type=False)
        consolidate_experiment1_outputs()

        print("\nMulti-steps experiment completed.")
        print(f"Output CSV: {strategy_out}")
        print(f"Output CSV: {by_type_out}")
        print(f"Output CSV: {exp1_csv}")
        print(f"Output Markdown: {exp1_md}")
        print("Output Figure: reports/experiment_1_ablation/fig_multi_steps_success_rate.png")
        print("Output Figure: reports/experiment_1_ablation/fig_multi_steps_efficiency.png")
    finally:
        simulate_student.MAX_STEPS = original_max_steps


if __name__ == "__main__":
    main()
