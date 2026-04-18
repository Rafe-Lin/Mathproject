# -*- coding: utf-8 -*-
"""
=============================================================================
模組名稱 (Module Name): run_sim_fixed.py
功能說明 (Description): 固定/隨機模式批量測試腳本 — 用不同能力等級跑模擬並畫圖。
                        一次模擬 弱/中/強 × teaching/assessment = 6 組。
執行語法 (Usage): python Simulated_student/run_sim_fixed.py
=============================================================================
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# ─── Path bootstrap ────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault("SEED_DB_ONLY", "0")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

# ─── Chinese font setup ───────────────────────────────────────────────────
def _setup_chinese_font():
    """Try to use a Chinese font for matplotlib labels."""
    candidates = [
        "C:/Windows/Fonts/msjhl.ttc",
        "C:/Windows/Fonts/msjh.ttc",
        "C:/Windows/Fonts/msyh.ttc",
    ]
    for path in candidates:
        if os.path.exists(path):
            fm.fontManager.addfont(path)
            available = {f.name for f in fm.fontManager.ttflist}
            for name in ("Microsoft JhengHei", "Microsoft JhengHei UI", "Microsoft YaHei"):
                if name in available:
                    plt.rcParams["font.sans-serif"] = [name, "DejaVu Sans"]
                    plt.rcParams["axes.unicode_minus"] = False
                    return
    plt.rcParams["font.sans-serif"] = ["DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False

_setup_chinese_font()

# ─── Color palette ─────────────────────────────────────────────────────────
COLORS = {
    "weak":   {"line": "#e74c3c", "fill": "#fadbd8"},
    "medium": {"line": "#f39c12", "fill": "#fdebd0"},
    "strong": {"line": "#27ae60", "fill": "#d5f5e3"},
}
MODE_MARKERS = {"teaching": "o", "assessment": "s"}


# ═══════════════════════════════════════════════════════════════════════════
# Main entry
# ═══════════════════════════════════════════════════════════════════════════
def main():
    from Simulated_student.sim_core import SimulatedStudent, ABILITY_PRESETS

    output_dir = Path(__file__).parent / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    max_steps = 25
    abilities = ["weak", "medium", "strong"]
    modes = ["teaching", "assessment"]
    seed_base = 42

    all_results: dict[str, dict] = {}  # key = "ability_mode"

    print("=" * 70)
    print("  模擬學生 — 固定/隨機模式批量測試")
    print("=" * 70)

    for ability in abilities:
        for mode in modes:
            label = f"{ability}_{mode}"
            print(f"\n▶ Running: {label} (prob={ABILITY_PRESETS[ability]['correct_probability']}, steps={max_steps})")

            sim = SimulatedStudent(
                mode=mode,
                ability=ability,
                answer_strategy="random",
                student_label=label,
                seed=seed_base,
            )
            sim.run_session(max_steps=max_steps)
            log_path = sim.save_log(output_dir / f"sim_{label}_{ts}.json")

            summary = sim._build_result_summary()
            all_results[label] = {
                "steps": sim.steps,
                "summary": summary,
                "ability": ability,
                "mode": mode,
                "log_path": str(log_path),
            }

            print(f"  ✔ {summary['total_steps']} steps, accuracy={summary['accuracy']:.2%}, "
                  f"final_apr={summary['final_apr']:.4f}, "
                  f"families={summary['unique_families_count']}, "
                  f"completed={summary['completed']}")

    # ── Save combined results ──
    combined_path = output_dir / f"sim_batch_combined_{ts}.json"
    with open(combined_path, "w", encoding="utf-8") as fh:
        json.dump(
            {k: {"summary": v["summary"], "mode": v["mode"], "ability": v["ability"]}
             for k, v in all_results.items()},
            fh, ensure_ascii=False, indent=2,
        )
    print(f"\n[Combined summary] → {combined_path}")

    # ── Generate plots ──
    print("\n📊 Generating plots …")
    _plot_apr_curves(all_results, output_dir, ts)
    _plot_frustration_curves(all_results, output_dir, ts)
    _plot_family_coverage(all_results, output_dir, ts)
    _plot_ppo_strategy_distribution(all_results, output_dir, ts)
    _plot_remediation_timeline(all_results, output_dir, ts)
    _plot_accuracy_comparison(all_results, output_dir, ts)

    # ── Adaptive vs Baseline comparison ──
    print("\n📊 Running baseline (non-adaptive) simulations for comparison …")
    from Simulated_student.sim_core import BaselineStudent
    baseline_results: dict[str, list] = {}
    for ability in abilities:
        bl = BaselineStudent(ability=ability, seed=seed_base)
        bl.run_session(max_steps=max_steps)
        baseline_results[ability] = bl.steps
        print(f"  ✔ baseline_{ability}: {len(bl.steps)} steps")

    _plot_adaptive_vs_baseline(all_results, baseline_results, output_dir, ts)

    print(f"\n✅ All outputs saved in {output_dir}")
    print("=" * 70)


# ═══════════════════════════════════════════════════════════════════════════
# Plot functions
# ═══════════════════════════════════════════════════════════════════════════

def _plot_apr_curves(results: dict, output_dir: Path, ts: str):
    """APR over steps for each ability × mode combination."""
    fig, axes = plt.subplots(1, 2, figsize=(16, 6), sharey=True)
    fig.suptitle("學生 APR 能力值變化曲線", fontsize=16, fontweight="bold")

    for ax, mode in zip(axes, ["teaching", "assessment"]):
        ax.set_title(f"模式：{'教學' if mode == 'teaching' else '評量'}", fontsize=13)
        ax.set_xlabel("步驟", fontsize=11)
        ax.set_ylabel("APR (能力估計)", fontsize=11)
        ax.axhline(y=0.65, color="gray", linestyle="--", alpha=0.5, label="目標 APR (0.65)")

        for ability in ["weak", "medium", "strong"]:
            key = f"{ability}_{mode}"
            if key not in results:
                continue
            steps = results[key]["steps"]
            x = [s["step_number"] for s in steps]
            y = [s["current_apr"] for s in steps]
            color = COLORS[ability]

            ax.plot(x, y, color=color["line"], linewidth=2, marker=".", markersize=4,
                    label=f"{ability} (p={results[key]['summary']['accuracy']:.0%})")
            ax.fill_between(x, 0, y, alpha=0.12, color=color["fill"])

            # Mark remediation triggers
            rem_steps = [s["step_number"] for s in steps if s.get("remediation_triggered")]
            rem_aprs = [s["current_apr"] for s in steps if s.get("remediation_triggered")]
            if rem_steps:
                ax.scatter(rem_steps, rem_aprs, color=color["line"],
                           marker="v", s=80, zorder=5, edgecolors="black", linewidths=0.5)

        ax.legend(fontsize=9, loc="lower right")
        ax.set_ylim(0, 1)
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    path = output_dir / f"plot_apr_curves_{ts}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  📈 APR curves → {path}")


def _plot_frustration_curves(results: dict, output_dir: Path, ts: str):
    """Frustration index over steps."""
    fig, axes = plt.subplots(1, 2, figsize=(16, 5), sharey=True)
    fig.suptitle("挫折指數 (Frustration Index) 變化", fontsize=16, fontweight="bold")

    for ax, mode in zip(axes, ["teaching", "assessment"]):
        ax.set_title(f"模式：{'教學' if mode == 'teaching' else '評量'}", fontsize=13)
        ax.set_xlabel("步驟", fontsize=11)
        ax.set_ylabel("挫折指數", fontsize=11)

        for ability in ["weak", "medium", "strong"]:
            key = f"{ability}_{mode}"
            if key not in results:
                continue
            steps = results[key]["steps"]
            x = [s["step_number"] for s in steps]
            y = [s["frustration_index"] for s in steps]
            color = COLORS[ability]
            ax.plot(x, y, color=color["line"], linewidth=2, marker=".", markersize=4,
                    label=ability)
            ax.fill_between(x, 0, y, alpha=0.15, color=color["fill"])

        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    path = output_dir / f"plot_frustration_{ts}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  📈 Frustration curves → {path}")


def _plot_family_coverage(results: dict, output_dir: Path, ts: str):
    """Bar chart of unique families visited per run."""
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.set_title("各模擬組的 Family 覆蓋數", fontsize=14, fontweight="bold")

    labels = []
    counts = []
    colors_bar = []
    for ability in ["weak", "medium", "strong"]:
        for mode in ["teaching", "assessment"]:
            key = f"{ability}_{mode}"
            if key not in results:
                continue
            labels.append(f"{ability}\n{mode[:5]}")
            counts.append(results[key]["summary"]["unique_families_count"])
            colors_bar.append(COLORS[ability]["line"])

    x_pos = np.arange(len(labels))
    bars = ax.bar(x_pos, counts, color=colors_bar, edgecolor="white", linewidth=1.5, width=0.6)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_ylabel("不同 Family 數量", fontsize=11)

    for bar, count in zip(bars, counts):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.2,
                str(count), ha="center", fontsize=11, fontweight="bold")

    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    path = output_dir / f"plot_family_coverage_{ts}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  📊 Family coverage → {path}")


def _plot_ppo_strategy_distribution(results: dict, output_dir: Path, ts: str):
    """Pie chart of PPO strategy usage for each ability."""
    strategy_names = {0: "Max-Fisher", 1: "ZPD", 2: "Diversity", 3: "Review"}
    strategy_colors = {0: "#3498db", 1: "#2ecc71", 2: "#9b59b6", 3: "#e67e22"}

    fig, axes = plt.subplots(2, 3, figsize=(15, 9))
    fig.suptitle("PPO 策略分佈", fontsize=16, fontweight="bold")

    idx = 0
    for ability in ["weak", "medium", "strong"]:
        for mi, mode in enumerate(["teaching", "assessment"]):
            key = f"{ability}_{mode}"
            if key not in results:
                continue
            ax = axes[mi][idx // 2 if mi == 0 else idx // 2]
            steps = results[key]["steps"]
            strat_counts = {}
            for s in steps:
                st = s.get("ppo_strategy", 0)
                strat_counts[st] = strat_counts.get(st, 0) + 1

            labels_pie = [strategy_names.get(k, f"S{k}") for k in sorted(strat_counts)]
            sizes = [strat_counts[k] for k in sorted(strat_counts)]
            colors_pie = [strategy_colors.get(k, "#95a5a6") for k in sorted(strat_counts)]

            ax.pie(sizes, labels=labels_pie, colors=colors_pie, autopct="%1.0f%%",
                   startangle=90, textprops={"fontsize": 9})
            mode_zh = "教學" if mode == "teaching" else "評量"
            ax.set_title(f"{ability} / {mode_zh}", fontsize=11)
        idx += 2

    plt.tight_layout()
    path = output_dir / f"plot_ppo_strategy_{ts}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  🥧 PPO strategy → {path}")


def _plot_remediation_timeline(results: dict, output_dir: Path, ts: str):
    """Timeline showing remediation entry/return points + mode (mainline vs remediation)."""
    fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)
    fig.suptitle("補救機制時間線 (Teaching 模式)", fontsize=16, fontweight="bold")

    for ax, ability in zip(axes, ["weak", "medium", "strong"]):
        key = f"{ability}_teaching"
        if key not in results:
            continue
        steps = results[key]["steps"]
        x = [s["step_number"] for s in steps]
        modes_binary = [1 if s.get("current_mode") == "remediation" else 0 for s in steps]
        aprs = [s["current_apr"] for s in steps]
        color = COLORS[ability]

        ax2 = ax.twinx()
        ax.fill_between(x, 0, modes_binary, alpha=0.25, color="#e74c3c",
                         step="mid", label="補救模式")
        ax2.plot(x, aprs, color=color["line"], linewidth=2, label="APR")

        # Remediation markers
        rem = [s["step_number"] for s in steps if s.get("remediation_triggered")]
        ret = [s["step_number"] for s in steps if s.get("return_to_mainline")]
        if rem:
            ax.scatter(rem, [1.05] * len(rem), marker="v", color="#c0392b", s=60,
                       zorder=5, label="觸發補救")
        if ret:
            ax.scatter(ret, [1.05] * len(ret), marker="^", color="#27ae60", s=60,
                       zorder=5, label="返回主線")

        ax.set_ylabel("模式", fontsize=10)
        ax.set_yticks([0, 1])
        ax.set_yticklabels(["主線", "補救"])
        ax.set_ylim(-0.1, 1.3)
        ax2.set_ylabel("APR", fontsize=10)
        ax2.set_ylim(0, 1)
        ax.set_title(f"{ability} 學生", fontsize=12, color=color["line"], fontweight="bold")

        lines1, labels1 = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(lines1 + lines2, labels1 + labels2, fontsize=8, loc="upper right")
        ax.grid(True, alpha=0.2)

    axes[-1].set_xlabel("步驟", fontsize=11)
    plt.tight_layout()
    path = output_dir / f"plot_remediation_timeline_{ts}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  📍 Remediation timeline → {path}")


def _plot_accuracy_comparison(results: dict, output_dir: Path, ts: str):
    """Summary bar chart comparing final APR, accuracy, families across all runs."""
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.suptitle("模擬結果總覽比較", fontsize=16, fontweight="bold")
    metrics = [
        ("final_apr", "最終 APR"),
        ("accuracy", "正確率"),
        ("unique_families_count", "覆蓋 Family 數"),
    ]

    for ax, (metric, title) in zip(axes, metrics):
        ax.set_title(title, fontsize=12, fontweight="bold")
        labels = []
        values = []
        colors_bar = []
        for ability in ["weak", "medium", "strong"]:
            for mode in ["teaching", "assessment"]:
                key = f"{ability}_{mode}"
                if key not in results:
                    continue
                labels.append(f"{ability}\n{mode[:5]}")
                values.append(results[key]["summary"].get(metric, 0))
                colors_bar.append(COLORS[ability]["line"])

        x_pos = np.arange(len(labels))
        bars = ax.bar(x_pos, values, color=colors_bar, edgecolor="white", linewidth=1.5, width=0.6)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(labels, fontsize=8)

        for bar, val in zip(bars, values):
            text = f"{val:.2f}" if isinstance(val, float) else str(val)
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                    text, ha="center", fontsize=9, fontweight="bold")
        ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    path = output_dir / f"plot_summary_comparison_{ts}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  📊 Summary comparison → {path}")


def _plot_adaptive_vs_baseline(
    adaptive_results: dict,
    baseline_results: dict[str, list],
    output_dir: Path,
    ts: str,
):
    """
    Compare APR growth curves: adaptive (with routing/remediation) vs
    baseline (fixed textbook sequence, no adaptive mechanisms).

    This is the key chart that shows the benefit of adaptive learning.
    """
    fig, axes = plt.subplots(1, 3, figsize=(18, 6), sharey=True)
    fig.suptitle(
        "自適應 vs. 傳統順序教學 — APR 能力成長比較",
        fontsize=16, fontweight="bold",
    )

    for ax, ability in zip(axes, ["weak", "medium", "strong"]):
        color = COLORS[ability]
        ability_zh = {"weak": "弱", "medium": "中等", "strong": "強"}[ability]
        ax.set_title(f"{ability_zh}學生 ({ability})", fontsize=13, fontweight="bold",
                     color=color["line"])
        ax.set_xlabel("步驟", fontsize=11)
        ax.set_ylabel("APR (能力估計)", fontsize=11)
        ax.axhline(y=0.65, color="gray", linestyle=":", alpha=0.4, label="目標 APR")

        # ── Adaptive curve ──
        key = f"{ability}_teaching"
        if key in adaptive_results:
            steps_ada = adaptive_results[key]["steps"]
            x_ada = [s["step_number"] for s in steps_ada]
            y_ada = [s["current_apr"] for s in steps_ada]
            ax.plot(x_ada, y_ada, color=color["line"], linewidth=2.5,
                    marker="o", markersize=5, label="自適應教學", zorder=4)
            ax.fill_between(x_ada, 0, y_ada, alpha=0.10, color=color["line"])

            # Mark remediation triggers
            rem_x = [s["step_number"] for s in steps_ada if s.get("remediation_triggered")]
            rem_y = [s["current_apr"] for s in steps_ada if s.get("remediation_triggered")]
            if rem_x:
                ax.scatter(rem_x, rem_y, marker="v", color="#c0392b", s=70,
                           zorder=5, edgecolors="black", linewidths=0.5,
                           label="觸發補救")

        # ── Baseline curve ──
        if ability in baseline_results:
            steps_bl = baseline_results[ability]
            x_bl = [s["step_number"] for s in steps_bl]
            y_bl = [s["current_apr"] for s in steps_bl]
            ax.plot(x_bl, y_bl, color="#7f8c8d", linewidth=2, linestyle="--",
                    marker="s", markersize=4, alpha=0.8, label="傳統順序教學", zorder=3)
            ax.fill_between(x_bl, 0, y_bl, alpha=0.06, color="#7f8c8d")

        ax.legend(fontsize=9, loc="lower right")
        ax.set_ylim(0, 1.05)
        ax.grid(True, alpha=0.25)

    plt.tight_layout()
    path = output_dir / f"plot_adaptive_vs_baseline_{ts}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  📈 Adaptive vs Baseline → {path}")


if __name__ == "__main__":
    main()
