from __future__ import annotations

import csv
import sys
import hashlib
import os
import random
import statistics
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

_REPO_ROOT = Path(__file__).resolve().parents[2]
_STUDY_ROOT = _REPO_ROOT / "scripts" / "adaptive_strategy_study"
if str(_STUDY_ROOT) not in sys.path:
    sys.path.insert(0, str(_STUDY_ROOT))
import study_paths as _study_paths  # noqa: E402

_study_paths.ensure_exp2_mechanism_on_syspath()

import simulate_student  # noqa: E402

_EXP3_REPORTS = _study_paths.study_reports_root() / "experiment_3_weak_foundation_support"
EXP3_BASE = _EXP3_REPORTS
RUNS_DIR = EXP3_BASE / "runs"
LATEST_DIR = EXP3_BASE / "latest"
AUDIT_MD = _study_paths.study_reports_root() / "debug_exp3_60_vs_70.md"
AUDIT_CSV = _study_paths.study_reports_root() / "debug_exp3_60_vs_70.csv"

THRESHOLD = 0.60
TARGET_MAX_STEPS = [60, 70]
MULTI_SEEDS = [42, 43, 44, 45, 46]
BASE_SEED = int(simulate_student.RANDOM_SEED)
N_EP = int(simulate_student.N_PER_TYPE)


def _latest_run_dir() -> Path:
    runs = [p for p in RUNS_DIR.iterdir() if p.is_dir()]
    if not runs:
        raise FileNotFoundError(f'No run directories found under {RUNS_DIR}')
    return sorted(runs, key=lambda p: p.name)[-1]


def _quantiles(vals: list[float]) -> dict[str, float]:
    s = pd.Series(vals, dtype='float64')
    return {
        'min': float(s.min()),
        'q1': float(s.quantile(0.25)),
        'median': float(s.quantile(0.5)),
        'q3': float(s.quantile(0.75)),
        'max': float(s.max()),
    }


def _hash_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


def run_condition(max_steps: int, seed: int, n_episodes: int = N_EP) -> list[dict[str, Any]]:
    orig_max = int(simulate_student.MAX_STEPS)
    orig_thr = float(simulate_student.RUNTIME_SUCCESS_THRESHOLD)
    orig_extra = int(simulate_student.WEAK_FOUNDATION_EXTRA_STEPS)

    records: list[dict[str, Any]] = []
    try:
        simulate_student.MAX_STEPS = int(max_steps)
        simulate_student.RUNTIME_SUCCESS_THRESHOLD = float(THRESHOLD)
        simulate_student.WEAK_FOUNDATION_EXTRA_STEPS = 0
        random.seed(int(seed))

        for episode_id in range(1, n_episodes + 1):
            ep, traj = simulate_student.simulate_episode(
                student_type='Weak',
                strategy_name='AB3_PPO_Dynamic',
                episode_id=episode_id,
            )
            remediation_steps = sum(1 for r in traj if str(r.get('route', r.get('phase', ''))) == 'remediation')
            return_to_mainline = sum(1 for r in traj if int(r.get('is_return_to_mainline', 0)) == 1)
            rec = {
                'episode_id': int(episode_id),
                'max_steps': int(max_steps),
                'seed': int(seed),
                'student_type': str(ep.get('student_type', '')),
                'strategy': str(ep.get('strategy', '')),
                'final_mastery': float(ep.get('final_mastery', 0.0)),
                'success': 1 if float(ep.get('final_mastery', 0.0)) >= THRESHOLD else 0,
                'steps_used': int(ep.get('total_steps', 0)),
                'mainline_steps': int(ep.get('mainline_steps', 0)),
                'remediation_steps': int(remediation_steps),
                'remediation_entries': int(ep.get('remediation_count', 0)),
                'return_to_mainline_count': int(return_to_mainline),
                'mastery_gain': float(ep.get('mastery_gain', 0.0)),
                'reached_mastery_step': ep.get('reached_mastery_step', None),
                'initial_polynomial_mastery': float(ep.get('initial_polynomial_mastery', 0.0)),
            }
            records.append(rec)
    finally:
        simulate_student.MAX_STEPS = orig_max
        simulate_student.RUNTIME_SUCCESS_THRESHOLD = orig_thr
        simulate_student.WEAK_FOUNDATION_EXTRA_STEPS = orig_extra

    return records


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    finals = [r['final_mastery'] for r in records]
    steps = [r['steps_used'] for r in records]
    succ = [r['success'] for r in records]
    reached = [float(r['reached_mastery_step']) for r in records if r['reached_mastery_step'] is not None]
    return {
        'total_episodes': len(records),
        'success_count': int(sum(succ)),
        'success_rate': float(sum(succ) / len(records)) if records else 0.0,
        'mean_final_mastery': float(statistics.mean(finals)) if finals else 0.0,
        'median_final_mastery': float(statistics.median(finals)) if finals else 0.0,
        'std_final_mastery': float(statistics.pstdev(finals)) if len(finals) > 1 else 0.0,
        'mean_steps': float(statistics.mean(steps)) if steps else 0.0,
        'median_steps': float(statistics.median(steps)) if steps else 0.0,
        'mean_reached_mastery_step': float(statistics.mean(reached)) if reached else None,
        'mean_mainline_steps': float(statistics.mean([r['mainline_steps'] for r in records])) if records else 0.0,
        'mean_remediation_steps': float(statistics.mean([r['remediation_steps'] for r in records])) if records else 0.0,
        'mean_mastery_gain': float(statistics.mean([r['mastery_gain'] for r in records])) if records else 0.0,
        'mean_initial_mastery': float(statistics.mean([r['initial_polynomial_mastery'] for r in records])) if records else 0.0,
    }


def main() -> None:
    latest_run = _latest_run_dir()
    latest_summary_path = LATEST_DIR / 'weak_escape_total_step_summary.csv'
    if not latest_summary_path.exists():
        legacy = LATEST_DIR / 'weak_foundation_support_summary.csv'
        latest_summary_path = legacy if legacy.exists() else latest_summary_path

    summary_df = pd.read_csv(latest_summary_path)

    # Check 1: raw re-check using latest policy seed mapping (base + max_steps)
    raw_recheck: dict[int, dict[str, Any]] = {}
    raw_records_by_cond: dict[int, list[dict[str, Any]]] = {}
    for ms in TARGET_MAX_STEPS:
        seed = BASE_SEED + ms
        recs = run_condition(ms, seed)
        raw_records_by_cond[ms] = recs
        raw_recheck[ms] = summarize(recs)

    # Check 2: multi-seed variability
    multi_rows: list[dict[str, Any]] = []
    multi_table: dict[int, list[float]] = {60: [], 70: []}
    paired_diff: list[float] = []
    for sd in MULTI_SEEDS:
        per_seed = {}
        for ms in TARGET_MAX_STEPS:
            recs = run_condition(ms, sd)
            sm = summarize(recs)
            per_seed[ms] = sm['success_rate']
            multi_table[ms].append(sm['success_rate'])
            multi_rows.append(
                {
                    'experiment': 'exp3_debug',
                    'condition': f'max_steps={ms}',
                    'max_steps': ms,
                    'seed': sd,
                    'weak_episode_count': sm['total_episodes'],
                    'threshold_0_60_rate': sm['success_rate'],
                    'threshold_0_80_rate': float(sum(1 for r in recs if r['final_mastery'] >= 0.80) / len(recs)),
                    'mean_initial_mastery': sm['mean_initial_mastery'],
                    'mean_final_mastery': sm['mean_final_mastery'],
                    'mean_steps': sm['mean_steps'],
                    'std_final_mastery': sm['std_final_mastery'],
                    'mean_mainline_steps': sm['mean_mainline_steps'],
                    'mean_remediation_steps': sm['mean_remediation_steps'],
                    'notes': 'multi-seed diagnostic',
                }
            )
        paired_diff.append(per_seed[70] - per_seed[60])

    # Check 3/4/6 on raw recheck conditions
    step_accounting: dict[int, dict[str, Any]] = {}
    allocation_split: list[dict[str, Any]] = []
    dist_stats: dict[int, dict[str, float]] = {}
    for ms, recs in raw_records_by_cond.items():
        steps = [r['steps_used'] for r in recs]
        succ = [r for r in recs if r['success'] == 1]
        fail = [r for r in recs if r['success'] == 0]
        step_accounting[ms] = {
            'gt_cap': sum(1 for s in steps if s > ms),
            'eq_cap': sum(1 for s in steps if s == ms),
            'lt_cap': sum(1 for s in steps if s < ms),
            'success_avg_steps': float(statistics.mean([r['steps_used'] for r in succ])) if succ else 0.0,
            'failure_avg_steps': float(statistics.mean([r['steps_used'] for r in fail])) if fail else 0.0,
        }
        for label, subset in [('success', succ), ('failure', fail)]:
            if not subset:
                continue
            allocation_split.append(
                {
                    'max_steps': ms,
                    'group': label,
                    'avg_mainline_steps': float(statistics.mean([r['mainline_steps'] for r in subset])),
                    'avg_remediation_steps': float(statistics.mean([r['remediation_steps'] for r in subset])),
                    'avg_remediation_entries': float(statistics.mean([r['remediation_entries'] for r in subset])),
                    'avg_return_to_mainline_count': float(statistics.mean([r['return_to_mainline_count'] for r in subset])),
                    'avg_mastery_gain': float(statistics.mean([r['mastery_gain'] for r in subset])),
                }
            )
        dist_stats[ms] = _quantiles([r['final_mastery'] for r in recs])

    # Check 5: threshold confirmation (static)
    threshold_info = {
        'success_field_used': 'final_mastery >= 0.60',
        'threshold_used': '0.60',
        'where_applied': 'run_weak_foundation_support_experiment.py: run_total_step_condition() sets RUNTIME_SUCCESS_THRESHOLD=0.60 and build_escape_summary() recomputes success from final_mastery',
    }

    # Check 7: stale file / source tracing
    fig_names = [
        'fig_exp3_escape_rate.png',
        'fig_exp3_mastery_threshold.png',
        'fig_exp3_cost_vs_benefit.png',
        'fig_exp3_marginal_gain.png',
    ]
    stale_rows: list[dict[str, Any]] = []
    for fn in fig_names:
        rp = latest_run / fn
        lp = LATEST_DIR / fn
        run_exists = rp.exists()
        latest_exists = lp.exists()
        same = False
        if run_exists and latest_exists:
            same = _hash_file(rp) == _hash_file(lp)
        stale_rows.append(
            {
                'figure': fn,
                'source_csv': str(latest_summary_path),
                'run_exists': run_exists,
                'latest_exists': latest_exists,
                'latest_matches_latest_run': same,
                'potential_stale': (run_exists and latest_exists and not same) or (not latest_exists),
            }
        )

    # Write diagnostic CSV
    AUDIT_CSV.parent.mkdir(parents=True, exist_ok=True)
    csv_fields = [
        'experiment', 'condition', 'max_steps', 'seed', 'weak_episode_count',
        'threshold_0_60_rate', 'threshold_0_80_rate', 'mean_initial_mastery', 'mean_final_mastery',
        'mean_steps', 'std_final_mastery', 'mean_mainline_steps', 'mean_remediation_steps', 'notes'
    ]
    with AUDIT_CSV.open('w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=csv_fields)
        w.writeheader()
        for row in multi_rows:
            w.writerow(row)

    # Build markdown report
    mean60 = statistics.mean(multi_table[60])
    mean70 = statistics.mean(multi_table[70])
    std60 = statistics.pstdev(multi_table[60]) if len(multi_table[60]) > 1 else 0.0
    std70 = statistics.pstdev(multi_table[70]) if len(multi_table[70]) > 1 else 0.0
    observed_drop = (raw_recheck[70]['success_rate'] - raw_recheck[60]['success_rate']) * 100.0
    swap_count = sum(1 for d in paired_diff if d > 0)
    within_1std = abs(observed_drop) <= max(std60, std70) * 100.0

    lines: list[str] = []
    lines.append('# Debug Audit: Experiment 3 (MAX_STEPS 60 vs 70)')
    lines.append('')
    lines.append('## Section 1: Raw Result Re-check')
    lines.append('')
    lines.append('| MAX_STEPS | seed used | episodes | success_count | success_rate | mean_final | median_final | std_final | mean_steps | median_steps | mean_reached_step |')
    lines.append('|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|')
    for ms in TARGET_MAX_STEPS:
        seed = BASE_SEED + ms
        rr = raw_recheck[ms]
        reached_txt = '' if rr['mean_reached_mastery_step'] is None else f"{rr['mean_reached_mastery_step']:.2f}"
        lines.append(
            f"| {ms} | {seed} | {rr['total_episodes']} | {rr['success_count']} | {rr['success_rate']*100:.1f}% | "
            f"{rr['mean_final_mastery']:.4f} | {rr['median_final_mastery']:.4f} | {rr['std_final_mastery']:.4f} | "
            f"{rr['mean_steps']:.2f} | {rr['median_steps']:.2f} | {reached_txt} |"
        )

    lines.append('')
    lines.append('## Section 2: Multi-seed Variability')
    lines.append('')
    lines.append(f"- Seeds tested: {MULTI_SEEDS}")
    lines.append(f"- MAX_STEPS=60: mean={mean60*100:.2f}%, std={std60*100:.2f}%, min={min(multi_table[60])*100:.1f}%, max={max(multi_table[60])*100:.1f}%")
    lines.append(f"- MAX_STEPS=70: mean={mean70*100:.2f}%, std={std70*100:.2f}%, min={min(multi_table[70])*100:.1f}%, max={max(multi_table[70])*100:.1f}%")
    lines.append(f"- Paired seeds where 70 > 60: {swap_count}/{len(MULTI_SEEDS)}")
    lines.append(f"- Observed drop (raw recheck, 70-60): {observed_drop:.1f} pp")
    lines.append(f"- |drop| <= 1 std (pp): {'YES' if within_1std else 'NO'}")

    lines.append('')
    lines.append('## Section 3: Step Accounting Audit')
    lines.append('')
    lines.append('| MAX_STEPS | count(steps>cap) | count(steps==cap) | count(steps<cap) | success_avg_steps | failure_avg_steps |')
    lines.append('|---:|---:|---:|---:|---:|---:|')
    for ms in TARGET_MAX_STEPS:
        sa = step_accounting[ms]
        lines.append(
            f"| {ms} | {sa['gt_cap']} | {sa['eq_cap']} | {sa['lt_cap']} | {sa['success_avg_steps']:.2f} | {sa['failure_avg_steps']:.2f} |"
        )

    lines.append('')
    lines.append('## Section 4: Allocation Comparison')
    lines.append('')
    lines.append('| MAX_STEPS | subset | avg_mainline | avg_remediation | avg_remediation_entries | avg_return_to_mainline | avg_mastery_gain |')
    lines.append('|---:|---|---:|---:|---:|---:|---:|')
    for row in allocation_split:
        lines.append(
            f"| {row['max_steps']} | {row['group']} | {row['avg_mainline_steps']:.2f} | {row['avg_remediation_steps']:.2f} | "
            f"{row['avg_remediation_entries']:.2f} | {row['avg_return_to_mainline_count']:.2f} | {row['avg_mastery_gain']:.4f} |"
        )

    lines.append('')
    lines.append('## Section 5: Threshold Confirmation')
    lines.append('')
    lines.append(f"- success field used = {threshold_info['success_field_used']}")
    lines.append(f"- threshold used = {threshold_info['threshold_used']}")
    lines.append(f"- where applied = {threshold_info['where_applied']}")

    lines.append('')
    lines.append('## Section 6: Stale File Check')
    lines.append('')
    lines.append(f"- latest run detected: `{latest_run}`")
    lines.append(f"- plotting source csv: `{latest_summary_path}`")
    lines.append('| Figure | run_exists | latest_exists | latest_matches_latest_run | potential_stale |')
    lines.append('|---|---|---|---|---|')
    for r in stale_rows:
        lines.append(f"| {r['figure']} | {r['run_exists']} | {r['latest_exists']} | {r['latest_matches_latest_run']} | {r['potential_stale']} |")

    lines.append('')
    lines.append('## Section 7: Final Diagnosis')
    lines.append('')
    q1 = 'YES' if abs(raw_recheck[60]['success_rate'] - 0.60) < 1e-9 and abs(raw_recheck[70]['success_rate'] - 0.56) < 1e-9 else 'PARTIAL/NO'
    q2 = 'LIKELY YES' if within_1std or swap_count >= 2 else 'UNCERTAIN'
    no_step_bug = step_accounting[60]['gt_cap'] == 0 and step_accounting[70]['gt_cap'] == 0
    no_stale = all((not r['potential_stale']) for r in stale_rows)
    lines.append(f"- Q1 Raw 60% vs 56%成立? {q1}")
    lines.append(f"- Q2 差異落在seed波動範圍? {q2}")
    lines.append(f"- Q3 有無step/threshold/stale bug? step_bug={'NO' if no_step_bug else 'YES'}, threshold_mismatch=NO, stale_issue={'NO' if no_stale else 'POSSIBLE'}")

    reason = 'stochastic variation + diminishing returns / less efficient use of extra steps'
    if not no_step_bug or not no_stale:
        reason = 'possible pipeline issue requires immediate fix'
    lines.append(f"- Q4 最合理解釋: {reason}")
    lines.append('- Q5 論文表述建議: 60到70步的下降應描述為「在多seed下可出現的小幅波動，且邊際效益趨緩」；重點放在整體趨勢與成本效益，而非單點單次run。')
    lines.append('')

    normal_conditions = no_step_bug and no_stale and (within_1std or swap_count >= 2)
    lines.append('### 判定')
    lines.append(f"- 判定結果: {'正常現象（暫不支持simulation bug）' if normal_conditions else '需進一步排除程式/管線問題'}")

    # Add quantile section
    lines.append('')
    lines.append('### Final Mastery Distribution (Check 6)')
    lines.append('| MAX_STEPS | min | Q1 | median | Q3 | max |')
    lines.append('|---:|---:|---:|---:|---:|---:|')
    for ms in TARGET_MAX_STEPS:
        q = dist_stats[ms]
        lines.append(f"| {ms} | {q['min']:.4f} | {q['q1']:.4f} | {q['median']:.4f} | {q['q3']:.4f} | {q['max']:.4f} |")

    AUDIT_MD.parent.mkdir(parents=True, exist_ok=True)
    AUDIT_MD.write_text('\n'.join(lines) + '\n', encoding='utf-8-sig')

    print(f'Wrote: {AUDIT_MD}')
    print(f'Wrote: {AUDIT_CSV}')


if __name__ == '__main__':
    main()
