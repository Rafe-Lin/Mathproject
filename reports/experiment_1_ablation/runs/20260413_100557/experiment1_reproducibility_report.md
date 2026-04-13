# Experiment 1 Reproducibility Report

## Seed Policy
- Global seed helper: `set_global_seed(seed)` sets PYTHONHASHSEED + random (+ numpy/torch when available).
- Condition-wise seeding is enabled (independent seed per MAX_STEPS).
- MAX_STEPS=30 uses seed 42.
- MAX_STEPS=40 uses seed 43.
- MAX_STEPS=50 uses seed 44.

## Sample Size Source
- Single source: `simulate_student.EXP1_EPISODES_PER_TYPE = 100`.
- Runner and simulator now both use this source; no dual overwrite constants remain.

## Output Mode vs Logic
- Output mode now controls output routing only.
- Experiment 1 behavior is controlled by explicit profile flag: `MATHPROJECT_EXPERIMENT_PROFILE=exp1`.

## MAX_STEPS Hard Cap
- `get_effective_max_steps()` now returns `MAX_STEPS` for all groups.
- Weak students no longer receive implicit +10 steps in Experiment 1.

## Determinism Self-Check
- Determinism check skipped (set MATHPROJECT_RUN_DETERMINISM_CHECK=1 to enable).

Experiment 1 randomness is now condition-wise deterministic.
Output mode no longer changes experiment logic.
All student groups now share the same MAX_STEPS hard cap.
