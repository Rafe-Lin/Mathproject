# run_multi_steps_experiment.py Status

Status: Deprecated

## Official Runner
- `scripts/run_experiment1_multisteps.py`

## Why Deprecated
- To keep a single official Experiment 1 reproducibility policy.
- To avoid policy split across runners (seed, sample size, experiment profile, and MAX_STEPS semantics).
- To prevent generating legacy outputs that can conflict with official Experiment 1 results.

## How Misuse Is Prevented
- `scripts/run_multi_steps_experiment.py` now prints a deprecation warning and exits immediately.
- Documentation is updated to use `scripts/run_experiment1_multisteps.py` as the official entry point.

## Policy Notes
- Seed policy, sample size source, profile flag handling, and hard-cap behavior are centralized in `scripts/run_experiment1_multisteps.py` with `scripts/simulate_student.py`.
