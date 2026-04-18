# Experiment 1 Summary Table

| MAX_STEPS | Strategy | Success Rate (%) | Avg Steps | Avg Unnecessary Remediations | Avg Final Mastery |
|-----------|----------|------------------|-----------|------------------------------|-------------------|
| 30 | Baseline | 44.00 | 25.29 | 0.00 | 0.70 |
| 30 | Rule-Based | 46.00 | 24.56 | 0.59 | 0.72 |
| 30 | Adaptive (Ours) | 61.33 | 22.00 | 0.19 | 0.69 |
| 40 | Baseline | 54.67 | 30.16 | 0.00 | 0.72 |
| 40 | Rule-Based | 58.33 | 29.33 | 0.88 | 0.74 |
| 40 | Adaptive (Ours) | 70.33 | 25.36 | 0.16 | 0.73 |
| 50 | Baseline | 62.67 | 34.06 | 0.00 | 0.73 |
| 50 | Rule-Based | 65.67 | 32.95 | 0.73 | 0.75 |
| 50 | Adaptive (Ours) | 75.33 | 28.04 | 0.23 | 0.73 |

Note: The weak foundation group shows low absolute success rates, but Adaptive (Ours) still achieves the highest relative improvement.

## Experiment 1 Student-Type Assumptions

The Experiment 1 runtime path is: `scripts/run_experiment1_multisteps.py` -> `simulate_student.run_batch_experiments()` -> `simulate_episode()` -> `SimulatedStudent(...)`.  
The code initializes each student with a full polynomial subskill vector (`sign_handling`, `combine_like_terms`, `sign_distribution`, `expand_monomial`, `expand_binomial`, `family_isomorphism`) and then computes overall polynomial mastery from that vector.

| Student Type | Initial Mastery Mean | Variance / Randomness | Subskill Initialization Logic | Interpretation |
|---|---:|---|---|---|
| Careless | mean = 0.70 | Gaussian sampling with `std = 0.17` per subskill (`random.gauss`), then clipped to `[0.05, 0.98]` | All six subskills use the same Gaussian rule (no per-subskill fixed offset) | Starts with relatively high ability but high slip behavior; mistakes can still occur even at high mastery |
| Average | Base curve means = `[0.68, 0.62, 0.58, 0.53, 0.48, 0.44]` by subskill order | Uniform jitter per subskill: `random.uniform(-0.05, +0.05)`, then clipped to `[0.05, 0.98]` | Not one shared distribution; each subskill follows a rule-based descending curve + jitter | Encodes a balanced profile: foundational subskills start higher than later structural subskills |
| Weak Foundation | mean = 0.32 | Gaussian sampling with `std = 0.06` per subskill (`random.gauss`), then clipped to `[0.05, 0.98]` | All six subskills use the same Gaussian rule (no per-subskill fixed offset) | Starts with low mastery across the board and narrower spread, representing globally weak foundations |

- Subskills are always explicitly initialized for all six polynomial subskills; no subskill is left as a default or missing value.
- Overall polynomial mastery is not a simple average. The code uses a weighted blend plus weakest-skill penalty: `0.75 * weighted_mean + 0.25 * weakest_subskill`, then clamps to `[0.0, 1.0]`.
- The simulation uses condition-wise seeds for reproducibility (`MAX_STEPS=30 -> 42`, `40 -> 43`, `50 -> 44`).
- Student types differ by more than initial mastery:
  - `slip/guess` parameters differ by type (`Careless`: slip 0.20, guess 0.06; `Average`: slip 0.10, guess 0.04; `Weak`: slip 0.07, guess 0.03).
  - Careless has an extra slip increase of `+0.05` when hit-subskill mastery is `>= 0.70`.
  - Weak has stronger prerequisite transfer coefficient (`0.06` vs `0.03`) and a weak-only progression gate (`foundation mean < 0.55`) that constrains family routing during weak foundations.
- Mastery bounds in runtime updates:
- Initialization clamp: `[0.05, 0.98]` for per-subskill initial values.
- Update clamp: subskill and aggregated mastery are clamped to `[0.0, 1.0]`.
- Counted step hard cap is enforced by `MAX_STEPS` in Experiment 1 loops (`if total_steps >= MAX_STEPS: break`).

## Experiment 1 Sample Size

Experiment 1 is executed by `scripts/run_experiment1_multisteps.py`, which runs each `MAX_STEPS` setting (30, 40, 50) under an independent condition seed. In `scripts/simulate_student.py`, the sample size is centrally defined by `EXP1_EPISODES_PER_TYPE = 100`, and the runtime loop uses that setting for each student type under each strategy.

| Scope | Sample Size | Notes |
|---|---:|---|
| Per student type (within one strategy, one MAX_STEPS run) | 100 | Defined by `EXP1_EPISODES_PER_TYPE = 100` |
| Careless (per strategy, per MAX_STEPS run) | 100 | From `STUDENT_TYPES` loop + per-type episode count |
| Average (per strategy, per MAX_STEPS run) | 100 | From `STUDENT_TYPES` loop + per-type episode count |
| Weak Foundation (per strategy, per MAX_STEPS run) | 100 | Runtime type label is `Weak`; report naming is Weak Foundation |
| Total per strategy (one MAX_STEPS run) | 300 | 3 student types x 100 each |
| Total per MAX_STEPS run (all 3 strategies) | 900 | 3 strategies x 3 student types x 100 each |
| Total across full multi-steps Experiment 1 sweep (30/40/50) | 2700 | 3 MAX_STEPS runs x 900 each |

Each condition uses a balanced design with the same number of simulated students in each student type.
Per-type sample sizes are equal, which matters because it makes strategy comparisons across student types fair and reduces bias from unequal group sizes.
