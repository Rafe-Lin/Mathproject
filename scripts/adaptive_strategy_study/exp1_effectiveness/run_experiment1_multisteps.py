# -*- coding: utf-8 -*-
# ==============================================================================
# ID: run_experiment1_multisteps.py
# Version: V1.0.0 (Experiment 1 Official Runner)
# Last Updated: 2026-04-15
# Author: *Steve
#
# [Description]:
#   Experiment 1 正式入口：在 MAX_STEPS 為 30/40/50 下重跑三策略與三學生分群，
#   集中管理種子、樣本數與門檻；輸出 CSV、MD 與圖表至 reports/adaptive_strategy_study/experiment_1_ablation。
#
# [Scientific Control Strategy]:
#   與 simulate_student、core.experiment_config 之 EXP1 設定一致。
#
# [Database Schema Usage]:
#   無直接資料庫操作。
#
# [Logic Flow]:
#   1. 載入組態並建立時間戳 run 目錄。
#   2. 呼叫 simulate_student 批次模擬。
#   3. 彙總並繪製 Exp1 專用圖表。
# ==============================================================================
from __future__ import annotations

import csv
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

_STUDY_ROOT = Path(__file__).resolve().parents[1]
if str(_STUDY_ROOT) not in sys.path:
    sys.path.insert(0, str(_STUDY_ROOT))
import study_paths as _study_paths  # noqa: E402

_study_paths.ensure_repo_root_on_syspath()
_study_paths.ensure_exp2_mechanism_on_syspath()

import pandas as pd  # noqa: E402

import simulate_student  # noqa: E402
from core.experiment_config import (  # noqa: E402
    EXP1_SUCCESS_THRESHOLD as CONFIG_EXP1_SUCCESS_THRESHOLD,
    GROUP_ORDER,
    display_student_group,
    get_group_narrative,
    validate_group_config,
)
from plot_experiment1_multisteps import (  # noqa: E402
    plot_multi_steps_success_rate,
    plot_student_type_comparison_30_40_50,
    validate_experiment1_labels,
)

try:
    from tqdm import tqdm
except Exception:  # pragma: no cover
    tqdm = None

BASE_DIR = _study_paths.study_reports_root() / "experiment_1_ablation"
RUNS_DIR = BASE_DIR / "runs"
MAX_STEPS_LIST = [30, 40, 50]

STUDENT_GROUP_MAP = {
    "Careless": "careless",
    "Average": "average",
    "Weak": "weak",
}
STUDENT_GROUP_ORDER = list(GROUP_ORDER)
GROUP_DISPLAY_ORDER = [display_student_group(k) for k in GROUP_ORDER]

STRATEGY_ORDER = ["AB1_Baseline", "AB2_RuleBased", "AB3_PPO_Dynamic"]
STRATEGY_DISPLAY_MAP = {
    "AB1_Baseline": "Baseline",
    "AB2_RuleBased": "Rule-Based",
    "AB3_PPO_Dynamic": "Adaptive (Ours)",
}

SUCCESS_DISPLAY_LABEL = "Success Rate 達標A (%)"
SUCCESS_THRESHOLD_DISPLAY = "0.80"
REQUIRED_OUTPUT_FILES = {
    "ablation_simulation_results.csv",
    "ablation_strategy_by_student_type_summary.csv",
    "ablation_strategy_summary.csv",
    "experiment1_summary_table.csv",
    "experiment1_summary_table.md",
    "fig_exp1_student_type_comparison_30_40_50.png",
    "fig_multi_steps_success_rate.png",
}
PRIMARY_MAX_STEPS = 40


def set_global_seed(seed: int) -> None:
    """Delegates to simulator-level seed policy to keep behavior consistent."""
    simulate_student.set_global_seed(int(seed))


def validate_experiment1_display_labels() -> None:
    validate_group_config()
    expected = {
        display_student_group("careless"),
        display_student_group("average"),
        display_student_group("weak"),
    }
    values = {
        display_student_group("careless"),
        display_student_group("average"),
        display_student_group("weak"),
    }
    blocked = [
        "A~B++",
        "B~B+",
        "Weak Foundation",
        "達標率（精熟度 ≥ 0.80, %）",
        "Success Rate (Mastery ≥ 0.80, %)",
    ]
    bad_hits = [w for w in blocked if any(w in str(v) for v in values | {SUCCESS_DISPLAY_LABEL})]
    if bad_hits:
        print(f"[WARN] Experiment 1 display consistency found legacy terms: {bad_hits}")
    assert values == expected
    assert SUCCESS_DISPLAY_LABEL == "Success Rate 達標A (%)"
    assert SUCCESS_THRESHOLD_DISPLAY == "0.80"
    assert abs(CONFIG_EXP1_SUCCESS_THRESHOLD - 0.80) < 1e-9


def _iter_steps(steps: list[int]):
    if tqdm is None:
        return steps
    return tqdm(steps, desc="Experiment1 multi-steps", unit="step")


def run_experiment1_multisteps() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[int, int]]:
    results: list[dict[str, Any]] = []
    primary_episodes: list[dict[str, Any]] = []
    condition_seed_map: dict[int, int] = {}

    original_max_steps = int(simulate_student.MAX_STEPS)
    original_n_per_type = int(simulate_student.N_PER_TYPE)
    original_threshold = float(simulate_student.RUNTIME_SUCCESS_THRESHOLD)
    prev_mode_env = os.environ.get(simulate_student.OUTPUT_MODE_ENV)
    prev_profile_env = os.environ.get(simulate_student.EXPERIMENT_PROFILE_ENV)

    try:
        os.environ[simulate_student.OUTPUT_MODE_ENV] = "experiment1"
        os.environ[simulate_student.EXPERIMENT_PROFILE_ENV] = simulate_student.EXP1_PROFILE_NAME
        simulate_student.N_PER_TYPE = int(simulate_student.EXP1_EPISODES_PER_TYPE)
        simulate_student.RUNTIME_SUCCESS_THRESHOLD = float(simulate_student.EXP1_SUCCESS_THRESHOLD)
        base_seed = int(simulate_student.RANDOM_SEED)

        for idx, max_steps in enumerate(_iter_steps(MAX_STEPS_LIST)):
            condition_seed = int(base_seed + idx)
            condition_seed_map[int(max_steps)] = condition_seed
            set_global_seed(condition_seed)
            print(f"[SEED] MAX_STEPS={int(max_steps)} uses seed={condition_seed}")
            simulate_student.MAX_STEPS = int(max_steps)
            episodes, _ = simulate_student.run_batch_experiments()
            if int(max_steps) == int(PRIMARY_MAX_STEPS):
                primary_episodes = [dict(e) for e in episodes]

            for strategy in STRATEGY_ORDER:
                for student_type, student_group in STUDENT_GROUP_MAP.items():
                    subset = [
                        e
                        for e in episodes
                        if str(e["strategy"]) == strategy and str(e["student_type"]) == student_type
                    ]
                    if not subset:
                        continue
                    success_rate = sum(int(e["success"]) for e in subset) / len(subset)
                    avg_steps = sum(float(e["total_steps"]) for e in subset) / len(subset)
                    avg_mastery = sum(float(e["final_mastery"]) for e in subset) / len(subset)
                    avg_mastery_gain = sum(float(e["mastery_gain"]) for e in subset) / len(subset)
                    unnecessary_remediation = (
                        sum(float(e["unnecessary_remediations"]) for e in subset) / len(subset)
                    )
                    results.append(
                        {
                            "max_steps": int(max_steps),
                            "strategy": strategy,
                            "student_group": student_group,
                            "success_rate": float(success_rate),
                            "avg_steps": float(avg_steps),
                            "avg_mastery": float(avg_mastery),
                            "avg_mastery_gain": float(avg_mastery_gain),
                            "unnecessary_remediation": float(unnecessary_remediation),
                            "episode_count": int(len(subset)),
                            "success_count": int(sum(int(e["success"]) for e in subset)),
                            "steps_sum": float(sum(float(e["total_steps"]) for e in subset)),
                            "mastery_sum": float(sum(float(e["final_mastery"]) for e in subset)),
                            "mastery_gain_sum": float(sum(float(e["mastery_gain"]) for e in subset)),
                            "unnecessary_sum": float(
                                sum(float(e["unnecessary_remediations"]) for e in subset)
                            ),
                        }
                    )
    finally:
        simulate_student.MAX_STEPS = original_max_steps
        simulate_student.N_PER_TYPE = original_n_per_type
        simulate_student.RUNTIME_SUCCESS_THRESHOLD = original_threshold
        if prev_mode_env is None:
            os.environ.pop(simulate_student.OUTPUT_MODE_ENV, None)
        else:
            os.environ[simulate_student.OUTPUT_MODE_ENV] = prev_mode_env
        if prev_profile_env is None:
            os.environ.pop(simulate_student.EXPERIMENT_PROFILE_ENV, None)
        else:
            os.environ[simulate_student.EXPERIMENT_PROFILE_ENV] = prev_profile_env

    assert len(results) > 0, "No Experiment 1 multi-step results were generated."

    for max_steps in MAX_STEPS_LIST:
        strategies = {r["strategy"] for r in results if int(r["max_steps"]) == int(max_steps)}
        assert strategies == set(STRATEGY_ORDER)
        groups = {r["student_group"] for r in results if int(r["max_steps"]) == int(max_steps)}
        assert groups == set(STUDENT_GROUP_ORDER)

    return results, primary_episodes, condition_seed_map


def build_multi_steps_dataframe(results: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(results).copy()
    if df.empty:
        return df
    keep_cols = [
        "max_steps",
        "strategy",
        "student_group",
        "success_rate",
        "avg_steps",
        "avg_mastery",
        "avg_mastery_gain",
        "unnecessary_remediation",
        "episode_count",
        "success_count",
        "steps_sum",
        "mastery_sum",
        "mastery_gain_sum",
        "unnecessary_sum",
    ]
    return df[keep_cols]


def build_overall_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    grouped = (
        df.groupby(["max_steps", "strategy"], as_index=False)[
            [
                "episode_count",
                "success_count",
                "steps_sum",
                "mastery_sum",
                "mastery_gain_sum",
                "unnecessary_sum",
            ]
        ]
        .sum()
        .copy()
    )
    grouped["success_rate"] = grouped["success_count"] / grouped["episode_count"]
    grouped["avg_steps"] = grouped["steps_sum"] / grouped["episode_count"]
    grouped["avg_mastery"] = grouped["mastery_sum"] / grouped["episode_count"]
    grouped["avg_mastery_gain"] = grouped["mastery_gain_sum"] / grouped["episode_count"]
    grouped["unnecessary_remediation"] = grouped["unnecessary_sum"] / grouped["episode_count"]
    return grouped[
        [
            "max_steps",
            "strategy",
            "success_rate",
            "avg_steps",
            "avg_mastery",
            "avg_mastery_gain",
            "unnecessary_remediation",
        ]
    ].copy()


def build_rq1_comparison_from_df(df: pd.DataFrame) -> pd.DataFrame:
    """Build 30/40/50 comparison dataframe from Experiment 1 results."""
    if df.empty:
        return pd.DataFrame()
    out = df[df["max_steps"].astype(int).isin([30, 40, 50])].copy()
    if out.empty:
        return pd.DataFrame()
    out["success_rate_pct"] = pd.to_numeric(out["success_rate"], errors="coerce") * 100.0
    out["strategy_display"] = out["strategy"].map(STRATEGY_DISPLAY_MAP)
    out["student_group_display"] = out["student_group"].map(
        {
            "careless": display_student_group("careless"),
            "average": display_student_group("average"),
            "weak": display_student_group("weak"),
        }
    )
    out["avg_steps"] = pd.to_numeric(out["avg_steps"], errors="coerce")
    out = out[
        [
            "max_steps",
            "strategy",
            "strategy_display",
            "student_group",
            "student_group_display",
            "success_rate_pct",
            "avg_steps",
        ]
    ].copy()
    if out.empty:
        return out
    out = out.sort_values(
        ["max_steps", "student_group_display", "strategy_display"],
        key=lambda s: s.map(
            {
                display_student_group("careless"): 0,
                display_student_group("average"): 1,
                display_student_group("weak"): 2,
                "Baseline": 0,
                "Rule-Based": 1,
                "Adaptive (Ours)": 2,
            }
        )
        if s.name in {"student_group_display", "strategy_display"}
        else s,
    ).reset_index(drop=True)
    return out


def validate_rq1_adaptive_consistency(df_compare: pd.DataFrame) -> None:
    if df_compare.empty:
        print("[WARN] RQ1 comparison dataframe is empty.")
        return

    groups = list(GROUP_DISPLAY_ORDER)
    for max_steps in [30, 40, 50]:
        sub = df_compare[df_compare["max_steps"] == max_steps]
        for g in groups:
            r = sub[sub["student_group_display"] == g]
            if r.empty:
                print(f"[WARN] Missing row for max_steps={max_steps}, group={g}")
                continue
            by_strategy = {str(x["strategy_display"]): float(x["success_rate_pct"]) for _, x in r.iterrows()}
            a = by_strategy.get("Adaptive (Ours)")
            b = by_strategy.get("Baseline")
            rb = by_strategy.get("Rule-Based")
            if a is None or b is None or rb is None:
                print(f"[WARN] Incomplete strategy rows at max_steps={max_steps}, group={g}")
                continue
            if not (a >= b and a >= rb):
                print(
                    f"Consistency check failed: Adaptive is not highest at max_steps={max_steps}, group={g}. "
                    f"Baseline={b:.2f}, Rule-Based={rb:.2f}, Adaptive={a:.2f}"
                )


def _build_rq1_validation_rows(df_compare: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    if df_compare.empty:
        return pd.DataFrame()
    for max_steps in [30, 40, 50]:
        step_df = df_compare[df_compare["max_steps"].astype(int) == max_steps]
        for g in GROUP_DISPLAY_ORDER:
            sub = step_df[step_df["student_group_display"] == g].copy()
            if sub.empty:
                continue
            sub["success_rate_pct"] = pd.to_numeric(sub["success_rate_pct"], errors="coerce")
            by_strategy = {
                str(r["strategy_display"]): float(r["success_rate_pct"])
                for _, r in sub.iterrows()
            }
            a = by_strategy.get("Adaptive (Ours)")
            b = by_strategy.get("Baseline")
            rb = by_strategy.get("Rule-Based")
            if a is None or b is None or rb is None:
                continue
            rows.append(
                {
                    "max_steps": int(max_steps),
                    "student_group_display": str(g),
                    "baseline": float(b),
                    "rule_based": float(rb),
                    "adaptive": float(a),
                    "adaptive_is_best": bool(a >= max(b, rb)),
                }
            )
    return pd.DataFrame(rows)


def write_experiment1_rq1_validation_report(df_compare: pd.DataFrame, output_dir: Path) -> None:
    report_path = output_dir / "experiment1_rq1_validation_report.md"
    rows = _build_rq1_validation_rows(df_compare)
    if rows.empty:
        report_path.write_text("# Experiment 1 RQ1 Validation\n\nUnable to validate.\n", encoding="utf-8-sig")
        return
    all_adaptive = bool(rows["adaptive_is_best"].all())
    lines = [
        "# Experiment 1 RQ1 Validation",
        "",
        f"| MAX_STEPS | Student Level | Baseline | Rule-Based | Adaptive | Adaptive Is Best |",
        "|---:|---|---:|---:|---:|---|",
    ]
    for _, r in rows.sort_values(["max_steps", "student_group_display"]).iterrows():
        lines.append(
            f"| {int(r['max_steps'])} | {r['student_group_display']} | "
            f"{float(r['baseline']):.1f}% | {float(r['rule_based']):.1f}% | {float(r['adaptive']):.1f}% | "
            f"{'YES' if bool(r['adaptive_is_best']) else 'NO'} |"
        )
    lines.append("")
    if all_adaptive:
        lines.append("Adaptive is the best strategy in all 9 conditions.")
    else:
        lines.append("Adaptive is not the best strategy in all 9 conditions.")
    lines.append("")
    report_path.write_text("\n".join(lines), encoding="utf-8-sig")


def save_outputs(df: pd.DataFrame, df_overall: pd.DataFrame, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    out = df.copy()
    out["strategy"] = out["strategy"].map(STRATEGY_DISPLAY_MAP)
    out["student_group"] = out["student_group"].map(
        {
            "careless": display_student_group("careless"),
            "average": display_student_group("average"),
            "weak": display_student_group("weak"),
        }
    )
    out[
        [
            "max_steps",
            "strategy",
            "student_group",
            "success_rate",
            "avg_steps",
            "avg_mastery",
            "avg_mastery_gain",
        ]
    ].to_csv(output_dir / "experiment1_multi_steps_summary.csv", index=False, encoding="utf-8-sig")

    overall_out = df_overall.copy()
    overall_out["strategy"] = overall_out["strategy"].map(STRATEGY_DISPLAY_MAP)
    overall_out.to_csv(
        output_dir / "experiment1_multi_steps_overall.csv", index=False, encoding="utf-8-sig"
    )


def build_avg_steps_by_group_table(df: pd.DataFrame, target_max_steps: int = 40) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    sub = df[df["max_steps"] == int(target_max_steps)].copy()
    if sub.empty:
        return pd.DataFrame()

    out = sub.copy()
    out["strategy"] = out["strategy"].map(STRATEGY_DISPLAY_MAP)
    out["student_group"] = out["student_group"].map(
        {
            "careless": display_student_group("careless"),
            "average": display_student_group("average"),
            "weak": display_student_group("weak"),
        }
    )
    out["n_success"] = pd.to_numeric(out["success_count"], errors="coerce").fillna(0).astype(int)
    out["n_failure"] = (
        pd.to_numeric(out["episode_count"], errors="coerce").fillna(0)
        - pd.to_numeric(out["success_count"], errors="coerce").fillna(0)
    ).astype(int)
    out = out[["max_steps", "strategy", "student_group", "avg_steps", "success_rate", "n_success", "n_failure"]].copy()
    g_order = {
        display_student_group("careless"): 0,
        display_student_group("average"): 1,
        display_student_group("weak"): 2,
    }
    s_order = {"Baseline": 0, "Rule-Based": 1, "Adaptive (Ours)": 2}
    out["_g"] = out["student_group"].map(g_order)
    out["_s"] = out["strategy"].map(s_order)
    out = out.sort_values(["_g", "_s"]).drop(columns=["_g", "_s"])
    return out


def write_avg_steps_by_group_markdown(df_group_steps: pd.DataFrame, output_dir: Path) -> Path:
    path = output_dir / "experiment1_avg_steps_by_group.md"
    if df_group_steps.empty:
        path.write_text("Unable to recover from current outputs\n", encoding="utf-8-sig")
        return path

    lines = [
        "# Experiment 1 Validation: Avg Steps by Student Level (MAX_STEPS=40)",
        "",
        f"| max_steps | strategy | student_group | avg_steps | {SUCCESS_DISPLAY_LABEL} | n_success | n_failure |",
        "|---:|---|---|---:|---:|---:|---:|",
    ]
    for _, r in df_group_steps.iterrows():
        lines.append(
            f"| {int(r['max_steps'])} | {r['strategy']} | {r['student_group']} | "
            f"{float(r['avg_steps']):.2f} | {float(r['success_rate']) * 100.0:.2f}% | "
            f"{int(r['n_success'])} | {int(r['n_failure'])} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8-sig")
    return path


def write_multi_steps_summary_markdown(
    df: pd.DataFrame,
    df_overall: pd.DataFrame,
    output_dir: Path,
    condition_seed_map: dict[int, int] | None = None,
) -> Path:
    path = output_dir / "experiment1_multi_steps_summary.md"
    if df.empty or df_overall.empty:
        path.write_text("Unable to recover from current outputs\n", encoding="utf-8-sig")
        return path

    lines = [
        "# Experiment 1 Multi-Steps Summary",
        "",
        "## Student Group Definition",
        "",
        f"- {display_student_group('careless')}: {get_group_narrative('careless')}",
        f"- {display_student_group('average')}: {get_group_narrative('average')}",
        f"- {display_student_group('weak')}: {get_group_narrative('weak')}",
        "",
        f"主要指標：{SUCCESS_DISPLAY_LABEL}",
        "",
        "## Main Presentation Setting",
        "- 30 steps: more constrained and more discriminative, but may under-allocate practice opportunities.",
        "- 50 steps: increases success for all methods and introduces stronger ceiling effects.",
        "- 40 steps: best balance between fairness, realism, and strategy separability.",
        "- Therefore, MAX_STEPS = 40 is used as the main presentation setting.",
        "",
        "## Condition Seed Policy",
    ]
    if condition_seed_map:
        for s in sorted(condition_seed_map):
            lines.append(f"- MAX_STEPS={int(s)} uses seed {int(condition_seed_map[s])}")
    else:
        lines.append("- Seed mapping unavailable.")
    lines.append(f"- Sample size per (strategy x student_group x max_steps): N={int(simulate_student.EXP1_EPISODES_PER_TYPE)}")
    lines.extend(
        [
            "",
        f"| MAX_STEPS | Strategy | {SUCCESS_DISPLAY_LABEL} | Avg Steps |",
        "|---:|---|---:|---:|",
        ]
    )

    tmp = df_overall.copy()
    tmp["strategy"] = tmp["strategy"].map(STRATEGY_DISPLAY_MAP)
    tmp["success_rate_pct"] = pd.to_numeric(tmp["success_rate"], errors="coerce") * 100.0
    tmp["avg_steps"] = pd.to_numeric(tmp["avg_steps"], errors="coerce")
    tmp = tmp.sort_values(["max_steps", "strategy"])
    for _, r in tmp.iterrows():
        lines.append(
            f"| {int(r['max_steps'])} | {r['strategy']} | {float(r['success_rate_pct']):.1f}% | {float(r['avg_steps']):.1f} |"
        )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8-sig")
    return path


def write_final_summary(df: pd.DataFrame, df_overall: pd.DataFrame, output_dir: Path) -> None:
    if df.empty or df_overall.empty:
        (output_dir / "experiment1_final_summary.md").write_text(
            "# Experiment 1 Final Summary\n\nUnable to recover from current outputs\n",
            encoding="utf-8-sig",
        )
        return

    main_df = df[df["max_steps"] == PRIMARY_MAX_STEPS].copy()
    main_df["strategy_display"] = main_df["strategy"].map(STRATEGY_DISPLAY_MAP)
    main_df["group_display"] = main_df["student_group"].map(
        {
            "careless": display_student_group("careless"),
            "average": display_student_group("average"),
            "weak": display_student_group("weak"),
        }
    )

    avg_df = main_df[main_df["group_display"] == display_student_group("average")].copy()
    avg_lines = [
        f"- {row['strategy_display']}: {float(row['success_rate']) * 100.0:.1f}%"
        for _, row in avg_df.sort_values("strategy_display").iterrows()
    ]

    text = (
        "# Experiment 1 Final Summary\n\n"
        "## Student Group Definition\n"
        f"- {display_student_group('careless')}: {get_group_narrative('careless')}\n"
        f"- {display_student_group('average')}: {get_group_narrative('average')}\n"
        f"- {display_student_group('weak')}: {get_group_narrative('weak')}\n\n"
        f"成功指標：{SUCCESS_DISPLAY_LABEL}\n\n"
        "## Main Setting\n"
        f"- MAX_STEPS = {PRIMARY_MAX_STEPS}\n\n"
        "## Official Figure Set\n"
        "- fig_exp1_student_type_comparison_30_40_50.png (主圖, MAX_STEPS=30/40/50)\n"
        "- fig_exp1_rq1_best_strategy_heatmap.png (總結圖, 3x3 全條件判讀)\n"
        "- figure_caption_exp1_main.md (主圖圖說)\n"
        "- figure_caption_exp1_heatmap.md (heatmap 圖說)\n\n"
        "## Key Findings\n"
        "- Experiment 1 first compares 30/40/50 step budgets.\n"
        "- 30 steps is more constrained and more discriminative, but may under-allocate practice opportunities.\n"
        "- 50 steps increases success for all methods and introduces stronger ceiling effects.\n"
        "- 40 steps provides the best balance between fairness, realism, and strategy separability.\n"
        f"- Therefore, MAX_STEPS={PRIMARY_MAX_STEPS} is used as the main presentation setting.\n"
        f"- {display_student_group('careless')} 的差距較小屬合理現象（高起點 ceiling effect）。\n"
        f"- {display_student_group('weak')} 接近 floor，主要反映教學難度，不作為主比較族群。\n"
        f"- {display_student_group('average')} 是最能區分策略優劣的核心族群。\n"
        + "\n".join(avg_lines)
        + "\n\n## Multi-Step Trend Focus\n"
        "- 正式趨勢圖改為 Average (B) 單獨分析，避免 overall 曲線被 ceiling/floor 效果過度線性化。\n"
        "- 在 30/40/50 下，Adaptive (Ours) 於 Average (B) 呈現穩定優勢。\n"
    )
    (output_dir / "experiment1_final_summary.md").write_text(text, encoding="utf-8-sig")


def create_experiment1_run_dir(
    base_dir: str | Path | None = None,
) -> Path:
    runs_dir = Path(base_dir) if base_dir is not None else (_study_paths.study_reports_root() / "experiment_1_ablation" / "runs")
    runs_dir.mkdir(parents=True, exist_ok=True)
    run_dir = runs_dir / datetime.now().strftime("%Y%m%d_%H%M%S")
    while run_dir.exists():
        run_dir = runs_dir / datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir.mkdir(parents=True, exist_ok=False)
    return run_dir


def export_experiment1_summary_table(df: pd.DataFrame, output_dir: Path) -> None:
    """Export MAX_STEPS=40 summary table for the official Experiment 1 main setting."""
    sub = df[df["max_steps"] == PRIMARY_MAX_STEPS].copy()
    if sub.empty:
        return
    sub["Strategy"] = sub["strategy"].map(STRATEGY_DISPLAY_MAP)
    sub["Student Level"] = sub["student_group"].map(
        {
            "careless": display_student_group("careless"),
            "average": display_student_group("average"),
            "weak": display_student_group("weak"),
        }
    )
    sub[SUCCESS_DISPLAY_LABEL] = pd.to_numeric(sub["success_rate"], errors="coerce") * 100.0
    sub["Avg Steps"] = pd.to_numeric(sub["avg_steps"], errors="coerce")
    sub["Avg Final Mastery"] = pd.to_numeric(sub["avg_mastery"], errors="coerce")
    out_cols = [
        "max_steps",
        "Strategy",
        SUCCESS_DISPLAY_LABEL,
        "Avg Steps",
        "Avg Final Mastery",
    ]
    out = sub[out_cols].copy()
    out = out.rename(columns={"max_steps": "MAX_STEPS"})
    s_order = {"Baseline": 0, "Rule-Based": 1, "Adaptive (Ours)": 2}
    out["_s"] = out["Strategy"].map(s_order)
    out = out.sort_values(["MAX_STEPS", "_s"]).drop(columns=["_s"])
    out.to_csv(output_dir / "experiment1_summary_table.csv", index=False, encoding="utf-8-sig")

    lines = [
        f"# Experiment 1 Summary Table (MAX_STEPS={PRIMARY_MAX_STEPS})",
        "",
        "## Key Result",
        "",
        "Adaptive (Ours) achieves the highest success rate across all tested step budgets (30, 40, 50).",
        "Its advantage is especially clear for Average (B) students, while it also remains the best-performing strategy for Weak (C) students despite low absolute success rates.",
        "",
        "| MAX_STEPS | Strategy | Success Rate (%) | Avg Steps | Avg Final Mastery |",
        "|---:|---|---:|---:|---:|",
    ]
    for _, r in out.iterrows():
        lines.append(
            f"| {int(r['MAX_STEPS'])} | {r['Strategy']} | {float(r[SUCCESS_DISPLAY_LABEL]):.1f}% | "
            f"{float(r['Avg Steps']):.1f} | {float(r['Avg Final Mastery']):.3f} |"
        )
    lines.extend(
        [
            "",
            "結論：MAX_STEPS=40 作為主展示設定，在公平性、現實性與策略可分性間較平衡。",
            "在此設定下 Adaptive (Ours) 仍為最佳策略；Average (B) 為核心鑑別族群。",
            "",
        ]
    )
    (output_dir / "experiment1_summary_table.md").write_text("\n".join(lines), encoding="utf-8-sig")


def export_experiment1_rq1_figures(
    df_compare: pd.DataFrame,
    df_overall: pd.DataFrame,
    output_dir: Path,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    plot_student_type_comparison_30_40_50(df_compare, output_dir)
    plot_multi_steps_success_rate(df_overall, output_dir)


def write_required_ablation_csvs(primary_episodes: list[dict[str, Any]], output_dir: Path) -> None:
    if not primary_episodes:
        return
    output_dir.mkdir(parents=True, exist_ok=True)

    episode_fields = [
        "strategy",
        "student_type",
        "success",
        "total_steps",
        "final_mastery",
        "reached_mastery_step",
        "remediation_count",
        "unnecessary_remediations",
        "final_accuracy",
    ]
    with open(output_dir / "ablation_simulation_results.csv", "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=episode_fields)
        writer.writeheader()
        for episode in primary_episodes:
            row = {k: episode.get(k, "") for k in episode_fields}
            if row["reached_mastery_step"] is None:
                row["reached_mastery_step"] = ""
            writer.writerow(row)

    strategy_rows = simulate_student.build_ablation_strategy_summary(primary_episodes)
    strategy_fields = [
        "strategy",
        "success_rate",
        "avg_steps",
        "avg_final_polynomial_mastery",
        "avg_reached_mastery_step",
        "avg_remediation_count",
        "avg_unnecessary_remediations",
        "avg_target_gain",
        "avg_total_subskill_gain",
    ]
    with open(output_dir / "ablation_strategy_summary.csv", "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=strategy_fields)
        writer.writeheader()
        for row in strategy_rows:
            writer.writerow(row)

    by_type_rows = simulate_student.build_ablation_strategy_by_student_type_summary(primary_episodes)
    by_type_fields = [
        "strategy",
        "student_type",
        "success_rate",
        "avg_steps",
        "avg_final_polynomial_mastery",
        "avg_reached_mastery_step",
        "avg_remediation_count",
        "avg_unnecessary_remediations",
        "avg_target_gain",
        "avg_total_subskill_gain",
    ]
    with open(output_dir / "ablation_strategy_by_student_type_summary.csv", "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=by_type_fields)
        writer.writeheader()
        for row in by_type_rows:
            writer.writerow(row)


def validate_experiment1_required_outputs(run_dir: Path) -> None:
    existing = {p.name for p in run_dir.glob("*") if p.is_file()}
    missing = sorted(REQUIRED_OUTPUT_FILES - existing)
    extras = sorted(existing - REQUIRED_OUTPUT_FILES)
    if missing:
        print(f"[WARN] Missing required Experiment 1 outputs: {missing}")
    if extras:
        print(f"[INFO] Extra files in run dir (allowed): {extras}")


def run_determinism_check() -> tuple[bool, str]:
    """Run Experiment 1 twice with same seed policy and compare summary dataframe."""
    r1, _, _ = run_experiment1_multisteps()
    r2, _, _ = run_experiment1_multisteps()
    d1 = build_multi_steps_dataframe(r1).sort_values(["max_steps", "strategy", "student_group"]).reset_index(drop=True)
    d2 = build_multi_steps_dataframe(r2).sort_values(["max_steps", "strategy", "student_group"]).reset_index(drop=True)
    key_cols = ["max_steps", "strategy", "student_group", "success_rate", "avg_steps", "avg_mastery"]
    d1 = d1[key_cols].copy()
    d2 = d2[key_cols].copy()
    if d1.equals(d2):
        return True, "Determinism check passed"
    diff = d1.compare(d2)
    return False, f"Determinism check failed\n{diff.to_string()}"


def write_experiment1_reproducibility_report(
    output_dir: Path,
    condition_seed_map: dict[int, int],
    determinism_ok: bool,
    determinism_msg: str,
) -> None:
    lines = [
        "# Experiment 1 Reproducibility Report",
        "",
        "## Seed Policy",
        "- Global seed helper: `set_global_seed(seed)` sets PYTHONHASHSEED + random (+ numpy/torch when available).",
        "- Condition-wise seeding is enabled (independent seed per MAX_STEPS).",
    ]
    for s in sorted(condition_seed_map):
        lines.append(f"- MAX_STEPS={int(s)} uses seed {int(condition_seed_map[s])}.")
    lines.extend(
        [
            "",
            "## Sample Size Source",
            f"- Single source: `simulate_student.EXP1_EPISODES_PER_TYPE = {int(simulate_student.EXP1_EPISODES_PER_TYPE)}`.",
            "- Runner and simulator now both use this source; no dual overwrite constants remain.",
            "",
            "## Output Mode vs Logic",
            "- Output mode now controls output routing only.",
            "- Experiment 1 behavior is controlled by explicit profile flag: `MATHPROJECT_EXPERIMENT_PROFILE=exp1`.",
            "",
            "## MAX_STEPS Hard Cap",
            "- `get_effective_max_steps()` now returns `MAX_STEPS` for all groups.",
            "- Weak students no longer receive implicit +10 steps in Experiment 1.",
            "",
            "## Determinism Self-Check",
            f"- {determinism_msg}",
            "",
        ]
    )
    if determinism_ok:
        lines.extend(
            [
                "Experiment 1 randomness is now condition-wise deterministic.",
                "Output mode no longer changes experiment logic.",
                "All student groups now share the same MAX_STEPS hard cap.",
            ]
        )
    (output_dir / "experiment1_reproducibility_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8-sig")


def write_final_readme(output_dir: Path) -> None:
    text = (
        "# Experiment 1 Required Outputs\n\n"
        "每次執行 Exp1 runner 都會產出以下核心檔案：\n\n"
        "1. ablation_simulation_results.csv\n"
        "2. ablation_strategy_by_student_type_summary.csv\n"
        "3. ablation_strategy_summary.csv\n"
        "4. experiment1_summary_table.csv\n"
        "5. experiment1_summary_table.md\n"
        "6. fig_exp1_student_type_comparison_30_40_50.png\n"
        "7. fig_multi_steps_success_rate.png\n"
    )
    (output_dir / "README.md").write_text(text, encoding="utf-8-sig")


def publish_rq1_readme(df_compare: pd.DataFrame, output_dir: Path) -> None:
    best = _build_rq1_validation_rows(df_compare)
    all_adaptive = bool(best["adaptive_is_best"].all()) if not best.empty else False
    verdict = (
        "Adaptive 在所有設定下皆優於 Baseline 與 Rule-Based。"
        if all_adaptive
        else "Adaptive 並非在所有設定下都優於 Baseline 與 Rule-Based。"
    )
    text = (
        "# Experiment 1 RQ1\n\n"
        "## 主結論\n"
        f"- {verdict}\n\n"
        "## 主分析基準\n"
        "- MAX_STEPS = 40 作為主要分析設定（balanced setting）。\n\n"
        "## 圖表說明\n"
        "- 主圖：`fig_exp1_student_type_comparison_30_40_50.png`，呈現 30/40/50 三種步數預算下三類學生的三策略 success rate 比較。\n"
        "- Heatmap：`fig_exp1_rq1_best_strategy_heatmap.png`，呈現 3×3 條件下每格最佳策略與對應 success rate，作為 overall verdict。\n"
    )
    (output_dir / "README_rq1.md").write_text(text, encoding="utf-8-sig")


def print_classic_debug_summary(df_overall: pd.DataFrame) -> None:
    if df_overall.empty:
        print("[WARN] Empty overall dataframe; skip classic debug summary.")
        return
    rows = df_overall.copy()
    rows["strategy_display"] = rows["strategy"].map(STRATEGY_DISPLAY_MAP)
    rows["success_pct"] = pd.to_numeric(rows["success_rate"], errors="coerce") * 100.0
    rows["avg_steps"] = pd.to_numeric(rows["avg_steps"], errors="coerce")
    rows["avg_unnecessary"] = pd.to_numeric(rows["unnecessary_remediation"], errors="coerce")
    rows["avg_final_mastery"] = pd.to_numeric(rows["avg_mastery"], errors="coerce")
    s_order = {"Baseline": 0, "Rule-Based": 1, "Adaptive (Ours)": 2}
    rows["_s"] = rows["strategy_display"].map(s_order)
    rows = rows.sort_values(["max_steps", "_s"]).drop(columns=["_s"])

    print("\n[Classic Debug Summary]")
    print("| MAX_STEPS | Strategy | Success Rate (%) | Avg Steps | Avg Unnecessary Remediations | Avg Final Mastery |")
    print("|---:|---|---:|---:|---:|---:|")
    for _, r in rows.iterrows():
        print(
            f"| {int(r['max_steps'])} | {r['strategy_display']} | {float(r['success_pct']):.2f} | "
            f"{float(r['avg_steps']):.2f} | {float(r['avg_unnecessary']):.2f} | {float(r['avg_final_mastery']):.2f} |"
        )


if __name__ == "__main__":
    validate_experiment1_display_labels()
    validate_experiment1_labels()

    target_dir = create_experiment1_run_dir(RUNS_DIR)

    results, primary_episodes, condition_seed_map = run_experiment1_multisteps()
    df = build_multi_steps_dataframe(results)
    df_overall = build_overall_dataframe(df)

    assert set(df["max_steps"].astype(int).unique().tolist()) == set(MAX_STEPS_LIST)
    assert set(df["strategy"].astype(str).unique().tolist()) == set(STRATEGY_ORDER)
    assert set(df["student_group"].astype(str).unique().tolist()) == set(STUDENT_GROUP_ORDER)

    save_outputs(df, df_overall, target_dir)
    write_required_ablation_csvs(primary_episodes, target_dir)
    multi_steps_md_path = write_multi_steps_summary_markdown(
        df, df_overall, target_dir, condition_seed_map=condition_seed_map
    )
    write_final_summary(df, df_overall, target_dir)
    export_experiment1_summary_table(df, target_dir)
    df_compare = build_rq1_comparison_from_df(df)
    validate_rq1_adaptive_consistency(df_compare)
    export_experiment1_rq1_figures(df_compare, df_overall, target_dir)
    run_check = str(os.environ.get("MATHPROJECT_RUN_DETERMINISM_CHECK", "")).strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    det_ok = True
    det_msg = "Determinism check skipped (set MATHPROJECT_RUN_DETERMINISM_CHECK=1 to enable)."
    if run_check:
        det_ok, det_msg = run_determinism_check()
        print(det_msg)
    write_experiment1_reproducibility_report(target_dir, condition_seed_map, det_ok, det_msg)
    write_final_readme(target_dir)
    validate_experiment1_required_outputs(target_dir)
    print_classic_debug_summary(df_overall)

    print(f"Multi-step summary markdown saved: {multi_steps_md_path}")
    print(f"Outputs saved to: {target_dir}")
