# -*- coding: utf-8 -*-
# ==============================================================================
# ID: run_ablation_experiment.py
# Version: V1.0.0 (Ablation CLI)
# Last Updated: 2026-04-15
# Author: *Steve
#
# [Description]:
#   命令列包裝 core.adaptive.ablation_experiment：以指定 episodes、max_steps、seed
#   執行 AB1/AB2/AB3 模擬消融實驗，輸出至指定目錄。
#
# [Database Schema Usage]:
#   無直接資料庫操作。
#
# [Logic Flow]:
#   1. 解析 CLI 參數並組 ExperimentConfig。
#   2. 呼叫 run_experiment。
# ==============================================================================
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from core.adaptive.ablation_experiment import ExperimentConfig, run_experiment


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run simulation-based ablation experiment for AB1/AB2/AB3.")
    parser.add_argument("--episodes", type=int, default=100, help="Episodes per prototype.")
    parser.add_argument("--max-steps", type=int, default=30, help="Max steps per episode.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed.")
    parser.add_argument("--output-dir", type=str, default="outputs", help="Experiment output directory.")
    parser.add_argument(
        "--success-threshold",
        type=float,
        default=0.8,
        help="Polynomial ability threshold used to mark episode success.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = ExperimentConfig(
        episodes_per_prototype=args.episodes,
        max_steps_per_episode=args.max_steps,
        random_seed=args.seed,
        output_dir=args.output_dir,
        success_polynomial_threshold=args.success_threshold,
    )
    outputs = run_experiment(config)
    for key, path in outputs.items():
        print(f"{key}={Path(path)}", flush=True)


if __name__ == "__main__":
    main()
