"""
[File Name]
cleanup_non_experiment1_outputs.py

[Created Date]
2026-04-09

[Project]
Adaptive Math Learning System (Adaptive Summative + Teaching)

[Description]
This utility script cleans legacy non-Experiment-1 artifacts from the reports root.
It moves Experiment-2-related files into reports/experiment_2_ab3_student_types.
The script is designed for output organization only and does not affect simulation logic.

[Core Functionality]
- Scan only reports root-level files (no recursive traversal)
- Match configured filename patterns for non-Experiment-1 artifacts
- Move matched files into experiment_2_ab3_student_types
- Optionally back up existing destination files before overwrite

[Related Experiments]
- Experiment 2: Student Type Analysis

[Notes]
- No experiment logic is modified by this script.
- Added for maintainability and report-output housekeeping only.
"""

from __future__ import annotations

import fnmatch
import shutil
from datetime import datetime
from pathlib import Path


REPORTS_DIR = Path("reports")
EXP2_DIR = REPORTS_DIR / "experiment_2_ab3_student_types"

# Only clean these root-level file patterns.
MOVE_PATTERNS = [
    "mastery_trajectory.csv",
    "ab3_student_type_*.csv",
    "ab3_subskill_*.csv",
    "figure_caption_mastery_*.md",
    "figure_caption_experiment2_*.md",
    "mastery_trajectory_*.png",
    "experiment2_*.csv",
    "experiment2_*.png",
]


def should_move(filename: str) -> bool:
    """Return True when filename matches any configured move pattern."""
    return any(fnmatch.fnmatch(filename, pattern) for pattern in MOVE_PATTERNS)


def move_non_experiment1_outputs() -> list[tuple[Path, Path]]:
    """Move matched root-level report files into Experiment 2 folder."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    EXP2_DIR.mkdir(parents=True, exist_ok=True)

    moved: list[tuple[Path, Path]] = []
    for src in REPORTS_DIR.iterdir():
        if not src.is_file():
            continue
        if not should_move(src.name):
            continue

        dst = EXP2_DIR / src.name
        if dst.exists():
            # Keep prior destination artifact recoverable before overwrite.
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup = EXP2_DIR / f"{dst.name}.bak_{ts}"
            shutil.move(str(dst), str(backup))
        shutil.move(str(src), str(dst))
        moved.append((src, dst))
    return moved


def main() -> None:
    moved = move_non_experiment1_outputs()
    print("Cleanup completed.")
    print(f"Source: {REPORTS_DIR.resolve()}")
    print(f"Target: {EXP2_DIR.resolve()}")
    if not moved:
        print("No matching root-level files found.")
        return
    print("Moved files:")
    for src, dst in moved:
        print(f"- {src.name} -> {dst}")


if __name__ == "__main__":
    main()

