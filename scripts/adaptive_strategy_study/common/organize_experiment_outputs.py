# -*- coding: utf-8 -*-
# ==============================================================================
# ID: organize_experiment_outputs.py
# Version: V1.0.0 (Report Artifact Organizer)
# Last Updated: 2026-04-15
# Author: *Steve
#
# [Description]:
#   將 reports 根目錄產生的 CSV、圖檔依實驗別複製到對應子資料夾，
#   維持 Exp1/2/3/4 交付物目錄一致。
#
# [Database Schema Usage]:
#   無直接資料庫操作。
#
# [Logic Flow]:
#   1. 依允許清單比對來源檔名。
#   2. 複製至各實驗 curated 目錄。
# ==============================================================================

import shutil
import sys
from pathlib import Path

_STUDY_ROOT = Path(__file__).resolve().parents[1]
if str(_STUDY_ROOT) not in sys.path:
    sys.path.insert(0, str(_STUDY_ROOT))
import study_paths as _study_paths  # noqa: E402

_study_paths.ensure_repo_root_on_syspath()

REPORTS_DIR = _study_paths.study_reports_root()
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
