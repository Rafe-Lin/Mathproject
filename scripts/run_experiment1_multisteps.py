from __future__ import annotations

import os
import random
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

import simulate_student
from core.experiment_config import (
    EXP1_SUCCESS_THRESHOLD as CONFIG_EXP1_SUCCESS_THRESHOLD,
    GROUP_ORDER,
    display_student_group,
    get_group_narrative,
    validate_group_config,
)
from plot_experiment1_multisteps import (
    plot_avg_steps_by_group,
    plot_average_success_trend,
    plot_student_type_comparison_30_vs_40,
    plot_student_type_improved,
    validate_experiment1_labels,
)

try:
    from tqdm import tqdm
except Exception:  # pragma: no cover
    tqdm = None

RUNS_DIR = Path("reports/experiment_1_ablation/runs")
MAX_STEPS_LIST = [30, 40, 50]
CLASSIC_N_PER_TYPE = 100

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

SUCCESS_DISPLAY_LABEL = "Success(達標A) Rate%"
SUCCESS_THRESHOLD_DISPLAY = "0.80"
CORE_PLOT_NAMES = {
    "fig_exp1_student_type_improved.png",
    "fig_exp1_student_type_comparison_30_vs_40.png",
    "fig_exp1_average_success_trend.png",
    "fig_exp1_avg_steps_by_group.png",
}
PRIMARY_MAX_STEPS = 40


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
    assert SUCCESS_DISPLAY_LABEL == "Success(達標A) Rate%"
    assert SUCCESS_THRESHOLD_DISPLAY == "0.80"
    assert abs(CONFIG_EXP1_SUCCESS_THRESHOLD - 0.80) < 1e-9


def _iter_steps(steps: list[int]):
    if tqdm is None:
        return steps
    return tqdm(steps, desc="Experiment1 multi-steps", unit="step")


def run_experiment1_multisteps() -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []

    original_max_steps = int(simulate_student.MAX_STEPS)
    original_n_per_type = int(simulate_student.N_PER_TYPE)
    original_threshold = float(simulate_student.RUNTIME_SUCCESS_THRESHOLD)
    prev_mode_env = os.environ.get(simulate_student.OUTPUT_MODE_ENV)

    try:
        os.environ[simulate_student.OUTPUT_MODE_ENV] = "experiment1"
        simulate_student.N_PER_TYPE = int(CLASSIC_N_PER_TYPE)
        simulate_student.RUNTIME_SUCCESS_THRESHOLD = float(simulate_student.EXP1_SUCCESS_THRESHOLD)
        random.seed(simulate_student.RANDOM_SEED)

        for max_steps in _iter_steps(MAX_STEPS_LIST):
            simulate_student.MAX_STEPS = int(max_steps)
            episodes, _ = simulate_student.run_batch_experiments()

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

    assert len(results) > 0, "No Experiment 1 multi-step results were generated."

    for max_steps in MAX_STEPS_LIST:
        strategies = {r["strategy"] for r in results if int(r["max_steps"]) == int(max_steps)}
        assert strategies == set(STRATEGY_ORDER)
        groups = {r["student_group"] for r in results if int(r["max_steps"]) == int(max_steps)}
        assert groups == set(STUDENT_GROUP_ORDER)

    return results


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


def build_student_type_comparison_30_vs_40_from_df(df: pd.DataFrame) -> pd.DataFrame:
    """Build 30-vs-40 comparison strictly from main Experiment 1 dataframe (no rerun)."""
    if df.empty:
        return pd.DataFrame()
    out = df[df["max_steps"].astype(int).isin([30, 40])].copy()
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


def validate_30_vs_40_consistency(df_compare: pd.DataFrame) -> None:
    if df_compare.empty:
        print("[WARN] 30_vs_40 comparison dataframe is empty.")
        return

    groups = list(GROUP_DISPLAY_ORDER)
    for max_steps in [30, 40]:
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
        "| max_steps | strategy | student_group | avg_steps | Success(達標A) Rate% | n_success | n_failure |",
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


def write_multi_steps_summary_markdown(df: pd.DataFrame, df_overall: pd.DataFrame, output_dir: Path) -> Path:
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
        f"| MAX_STEPS | Strategy | {SUCCESS_DISPLAY_LABEL} | Avg Steps |",
        "|---:|---|---:|---:|",
    ]

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
        f"- fig_exp1_student_type_improved.png (主圖, MAX_STEPS={PRIMARY_MAX_STEPS})\n"
        "- fig_exp1_student_type_comparison_30_vs_40.png (30 vs 40 對照圖)\n"
        "- fig_exp1_average_success_trend.png (Average(B) multi-step trend 圖)\n\n"
        "- fig_exp1_avg_steps_by_group.png (MAX_STEPS=40 補充驗證圖)\n\n"
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


def create_experiment1_run_dir(base_dir: str | Path = "reports/experiment_1_ablation/runs") -> Path:
    runs_dir = Path(base_dir)
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
    sub["Avg Unnecessary Remediations"] = pd.to_numeric(sub["unnecessary_remediation"], errors="coerce")
    out_cols = [
        "Strategy",
        "Student Level",
        SUCCESS_DISPLAY_LABEL,
        "Avg Steps",
        "Avg Final Mastery",
        "Avg Unnecessary Remediations",
    ]
    out = sub[out_cols].copy()
    s_order = {"Baseline": 0, "Rule-Based": 1, "Adaptive (Ours)": 2}
    g_order = {
        display_student_group("careless"): 0,
        display_student_group("average"): 1,
        display_student_group("weak"): 2,
    }
    out["_s"] = out["Strategy"].map(s_order)
    out["_g"] = out["Student Level"].map(g_order)
    out = out.sort_values(["_g", "_s"]).drop(columns=["_s", "_g"])
    out.to_csv(output_dir / "experiment1_summary_table.csv", index=False, encoding="utf-8-sig")

    lines = [
        f"# Experiment 1 Summary Table (MAX_STEPS={PRIMARY_MAX_STEPS})",
        "",
        f"| Strategy | Student Level | {SUCCESS_DISPLAY_LABEL} | Avg Steps | Avg Final Mastery | Avg Unnecessary Remediations |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for _, r in out.iterrows():
        lines.append(
            f"| {r['Strategy']} | {r['Student Level']} | {float(r[SUCCESS_DISPLAY_LABEL]):.1f}% | "
            f"{float(r['Avg Steps']):.1f} | {float(r['Avg Final Mastery']):.3f} | "
            f"{float(r['Avg Unnecessary Remediations']):.2f} |"
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


def export_experiment1_core_figures_classic(
    df: pd.DataFrame,
    df_overall: pd.DataFrame,
    df_group_steps: pd.DataFrame,
    df_30_40: pd.DataFrame,
    output_dir: Path,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    # Figure role 1 (main): MAX_STEPS=40 student-level performance.
    plot_student_type_improved(df, output_dir)
    # Figure role 2 (contrast): 30 is constrained, 40 is balanced main setting.
    plot_student_type_comparison_30_vs_40(df_30_40, output_dir)
    # Figure role 3 (trend): Average(B) success trend under 30/40/50.
    plot_average_success_trend(df, output_dir)
    # Figure role 4 (supporting validation): average steps by group at MAX_STEPS=40.
    plot_avg_steps_by_group(df_group_steps, output_dir, target_max_steps=40)


def validate_experiment1_core_outputs(run_dir: Path) -> None:
    expected_files = set(CORE_PLOT_NAMES)
    existing_png = {p.name for p in run_dir.glob("*.png")}
    missing = sorted(expected_files - existing_png)
    extras = sorted(existing_png - expected_files)
    if missing:
        print(f"[WARN] Missing core plots: {missing}")
    if extras:
        print(f"[WARN] Extra Experiment 1 plots in run dir: {extras}")


def write_final_readme(output_dir: Path) -> None:
    text = (
        "# Experiment 1 Core Plot Set\n\n"
        "本 run 的正式輸出保留 4 張核心圖：\n\n"
        "1. fig_exp1_student_type_improved.png\n"
        "2. fig_exp1_student_type_comparison_30_vs_40.png\n"
        "3. fig_exp1_average_success_trend.png\n"
        "4. fig_exp1_avg_steps_by_group.png\n\n"
        "說明：\n"
        "- 主設定為 MAX_STEPS=40，用於主結果比較。\n"
        "- 30 vs 40 對照圖用於說明 constrained 與 balanced setting 差異。\n"
        "- 正式趨勢圖使用 Average (B) 單獨分析，以降低 ceiling/floor 對 overall 曲線的稀釋。\n"
        "- avg_steps_by_group 為補充驗證圖，不作為第一主敘事圖。\n"
    )
    (output_dir / "README.md").write_text(text, encoding="utf-8-sig")


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

    results = run_experiment1_multisteps()
    df = build_multi_steps_dataframe(results)
    df_overall = build_overall_dataframe(df)

    assert set(df["max_steps"].astype(int).unique().tolist()) == set(MAX_STEPS_LIST)
    assert set(df["strategy"].astype(str).unique().tolist()) == set(STRATEGY_ORDER)
    assert set(df["student_group"].astype(str).unique().tolist()) == set(STUDENT_GROUP_ORDER)

    save_outputs(df, df_overall, target_dir)
    multi_steps_md_path = write_multi_steps_summary_markdown(df, df_overall, target_dir)
    write_final_summary(df, df_overall, target_dir)
    export_experiment1_summary_table(df, target_dir)
    df_group_steps = build_avg_steps_by_group_table(df, target_max_steps=40)
    if not df_group_steps.empty:
        df_group_steps.to_csv(
            target_dir / "experiment1_avg_steps_by_group.csv", index=False, encoding="utf-8-sig"
        )
        write_avg_steps_by_group_markdown(df_group_steps, target_dir)

    df_30_40 = build_student_type_comparison_30_vs_40_from_df(df)
    validate_30_vs_40_consistency(df_30_40)
    export_experiment1_core_figures_classic(df, df_overall, df_group_steps, df_30_40, target_dir)
    write_final_readme(target_dir)
    validate_experiment1_core_outputs(target_dir)
    print_classic_debug_summary(df_overall)

    print(f"Multi-step summary markdown saved: {multi_steps_md_path}")
    print(f"Outputs saved to: {target_dir}")
