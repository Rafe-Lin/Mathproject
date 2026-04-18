# -*- coding: utf-8 -*-
# ==============================================================================
# ID: cleanup_non_experiment1_outputs.py
# Version: V1.0.0 (Reports Root Cleanup)
# Last Updated: 2026-04-15
# Author: *Steve
#
# [Description]:
#   掃描 reports 根目錄檔案，將非 Exp1 產物（如 Exp2 相關）搬移至
#   experiment_2_ab3_student_types，避免根目錄混置；不影響模擬邏輯。
#
# [Database Schema Usage]:
#   無直接資料庫操作。
#
# [Logic Flow]:
#   1. 比對檔名模式。
#   2. 可選備份後搬移目標目錄。
# ==============================================================================

from __future__ import annotations

import fnmatch
import shutil
import sys
from datetime import datetime
from pathlib import Path

_STUDY_ROOT = Path(__file__).resolve().parents[1]
if str(_STUDY_ROOT) not in sys.path:
    sys.path.insert(0, str(_STUDY_ROOT))
import study_paths as _study_paths  # noqa: E402

_study_paths.ensure_repo_root_on_syspath()

REPORTS_DIR = _study_paths.study_reports_root()
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

