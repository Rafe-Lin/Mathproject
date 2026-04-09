"""
[File Name]
organize_experiment_outputs.py

[Created Date]
2026-04-09

[Project]
Adaptive Math Learning System (Adaptive Summative + Teaching)

[Description]
This utility organizes generated report artifacts into experiment-specific folders.
It copies selected CSV and figure outputs from reports root into curated subdirectories
so that Experiment 1/2/3/4 deliverables are easier to track and present consistently.

[Core Functionality]
- Define experiment output directories under reports/
- Maintain curated file allow-lists per experiment track
- Copy existing report artifacts into corresponding experiment folders
- Provide one-command synchronization for reporting workflows

[Related Experiments]
- Experiment 1: Baseline vs AB2 vs AB3
- Experiment 2: Student Type Analysis
- Experiment 3: Policy Timing (AB3)
- Experiment 4: Weak + RAG (Extension)

[Notes]
- No experiment logic is modified by this header.
- Added for maintainability and research documentation only.
"""

import shutil
from pathlib import Path

REPORTS_DIR = Path("reports")
EXP1_DIR = REPORTS_DIR / "experiment_1_ablation"
EXP2_DIR = REPORTS_DIR / "experiment_2_ab3_student_types"
EXP3_DIR = REPORTS_DIR / "experiment_3_weak_foundation_support"

EXP1_FILES = [
    "ablation_simulation_results.csv",
    "ablation_strategy_summary.csv",
    "ablation_strategy_by_student_type_summary.csv",
    "experiment1_summary_table.csv",
    "experiment1_summary_table.md",
    "fig_ablation_success_rate.png",
    "fig_ablation_steps_vs_success.png",
    "fig_ablation_by_student_type_success.png",
    "multi_steps_strategy_summary.csv",
    "multi_steps_strategy_by_type_summary.csv",
    "fig_multi_steps_success_rate.png",
    "fig_multi_steps_efficiency.png",
]

EXP2_FILES = [
    "mastery_trajectory.csv",
    "ab3_student_type_summary.csv",
    "ab3_student_type_detailed_summary.csv",
    "ab3_subskill_progress_summary.csv",
    "ab3_subskill_by_type_detailed_summary.csv",
    "ab3_failure_breakpoint_summary.csv",
    "fig_multi_steps_ab3_by_student_type.png",
    "fig_ab3_subskill_gain_by_type.png",
]


def _copy_files(target_dir: Path, filenames: list[str]) -> None:
    """Copy files from reports root into target directory when they exist."""
    target_dir.mkdir(parents=True, exist_ok=True)
    for name in filenames:
        src = REPORTS_DIR / name
        if src.exists():
            shutil.copy2(src, target_dir / name)


def sync_experiment_output_dirs() -> None:
    """Synchronize experiment 1/2 outputs into dedicated subdirectories."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    EXP1_DIR.mkdir(parents=True, exist_ok=True)
    EXP2_DIR.mkdir(parents=True, exist_ok=True)
    EXP3_DIR.mkdir(parents=True, exist_ok=True)
    _copy_files(EXP1_DIR, EXP1_FILES)
    _copy_files(EXP2_DIR, EXP2_FILES)


def main() -> None:
    sync_experiment_output_dirs()
    print(f"Synced: {EXP1_DIR}")
    print(f"Synced: {EXP2_DIR}")
    print(f"Prepared: {EXP3_DIR}")


if __name__ == "__main__":
    main()
