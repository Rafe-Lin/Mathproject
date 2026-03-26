# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from core.adaptive.skill_policy_trainer import (
    generate_imitation_dataset,
    save_policy_checkpoint,
    train_policy_from_imitation,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train minimal adaptive skill policy model.")
    parser.add_argument("--episodes", type=int, default=400, help="Number of simulator episodes.")
    parser.add_argument("--horizon", type=int, default=12, help="Steps per episode.")
    parser.add_argument("--epochs", type=int, default=30, help="Training epochs.")
    parser.add_argument("--batch-size", type=int, default=64, help="Batch size.")
    parser.add_argument("--lr", type=float, default=1e-3, help="Learning rate.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed.")
    parser.add_argument(
        "--output",
        type=str,
        default=str(Path("artifacts") / "ppo_skill_policy.pt"),
        help="Checkpoint output path.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print("[trainer] generating imitation dataset...", flush=True)
    dataset = generate_imitation_dataset(
        num_episodes=args.episodes,
        horizon=args.horizon,
        seed=args.seed,
    )
    print(f"[trainer] dataset_size={len(dataset)}", flush=True)

    print("[trainer] training policy network...", flush=True)
    model, metrics = train_policy_from_imitation(
        dataset=dataset,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
        seed=args.seed,
    )
    print(
        f"[trainer] imitation_accuracy={metrics['imitation_accuracy']:.4f} "
        f"dataset_size={int(metrics['dataset_size'])}",
        flush=True,
    )

    output_path = save_policy_checkpoint(
        model=model,
        checkpoint_path=args.output,
        metadata={
            "episodes": args.episodes,
            "horizon": args.horizon,
            "epochs": args.epochs,
            "batch_size": args.batch_size,
            "lr": args.lr,
            "seed": args.seed,
            "imitation_accuracy": metrics["imitation_accuracy"],
        },
    )
    print(f"[trainer] checkpoint_saved={output_path}", flush=True)


if __name__ == "__main__":
    main()
