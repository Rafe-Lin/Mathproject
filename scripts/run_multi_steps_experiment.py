"""
DEPRECATED: Do not use this script for official Experiment 1 results.

Use scripts/run_experiment1_multisteps.py instead.
Reason: Experiment 1 reproducibility and config policy are centralized there
(condition-wise seed, unified sample size source, explicit experiment profile,
and consistent MAX_STEPS hard-cap semantics).
"""

from __future__ import annotations

import sys


DEPRECATION_MESSAGE = (
    "[DEPRECATED] scripts/run_multi_steps_experiment.py is no longer an official "
    "Experiment 1 runner.\n"
    "Use: python scripts/run_experiment1_multisteps.py\n"
    "Reason: to prevent seed/sample-size/profile policy divergence and "
    "non-reproducible outputs."
)


def main() -> None:
    print(DEPRECATION_MESSAGE)
    raise SystemExit(2)


if __name__ == "__main__":
    main()
