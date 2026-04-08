# -*- coding: utf-8 -*-
"""
=============================================================================
模組名稱 (Module Name): run_sim_llm.py
功能說明 (Description): LLM 模式測試腳本 — 連接 Ollama 本地模型，
                        用 LLM-as-a-judge 模擬學生作答，畫出結果圖表。
                        預設模型: qwen3-vl:8b-instruct-q4_k_m
                        預設 API: http://localhost:11434/api/generate
執行語法 (Usage): python Simulated_student/run_sim_llm.py [--ability medium] [--mode teaching] [--steps 20]
=============================================================================
"""
from __future__ import annotations

import argparse
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


COLORS = {
    "weak":   {"line": "#e74c3c", "fill": "#fadbd8"},
    "medium": {"line": "#f39c12", "fill": "#fdebd0"},
    "strong": {"line": "#27ae60", "fill": "#d5f5e3"},
}


def _check_ollama(api_url: str) -> bool:
    """Quick check if Ollama is reachable."""
    import requests
    try:
        resp = requests.get(api_url.replace("/api/generate", "/"), timeout=5)
        return resp.status_code == 200
    except Exception:
        return False


def main():
    parser = argparse.ArgumentParser(description="LLM 模擬學生測試")
    parser.add_argument("--ability", default="medium", choices=["weak", "medium", "strong"],
                        help="模擬學生能力等級")
    parser.add_argument("--mode", default="teaching", choices=["teaching", "assessment"],
                        help="自適應模式")
    parser.add_argument("--steps", type=int, default=20, help="最大步數")
    parser.add_argument("--model", default="qwen2.5:3b",
                        help="Ollama 模型名稱")
    parser.add_argument("--api-url", default="http://localhost:11434/api/generate",
                        help="Ollama API URL")
    args = parser.parse_args()

    print("=" * 70)
    print("  模擬學生 — LLM-as-a-judge 模式測試")
    print("=" * 70)
    print(f"  模型: {args.model}")
    print(f"  API:  {args.api_url}")
    print(f"  能力: {args.ability}")
    print(f"  模式: {args.mode}")
    print(f"  步數: {args.steps}")
    print("=" * 70)

    # Check Ollama
    if not _check_ollama(args.api_url):
        print("\n❌ 無法連線到 Ollama。請確認：")
        print(f"   1. Ollama 已啟動 (ollama serve)")
        print(f"   2. API URL 正確: {args.api_url}")
        print(f"   3. 模型已下載: ollama pull {args.model}")
        return

    print("\n✅ Ollama 連線成功")

    from Simulated_student.sim_llm_judge import LLMJudge
    from Simulated_student.sim_core import SimulatedStudent

    output_dir = Path(__file__).parent / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create LLM judge
    judge = LLMJudge(
        model=args.model,
        api_url=args.api_url,
        ability=args.ability,
    )

    label = f"llm_{args.ability}_{args.mode}"
    print(f"\n▶ Running LLM simulation: {label}")

    sim = SimulatedStudent(
        mode=args.mode,
        ability=args.ability,
        answer_strategy="llm",
        llm_judge=judge,
        student_label=label,
    )
    sim.run_session(max_steps=args.steps)
    log_path = sim.save_log(output_dir / f"sim_{label}_{ts}.json")

    summary = sim._build_result_summary()
    print(f"\n  ✔ 完成: {summary['total_steps']} 步")
    print(f"    正確率: {summary['accuracy']:.2%}")
    print(f"    最終 APR: {summary['final_apr']:.4f}")
    print(f"    覆蓋 Families: {summary['unique_families_count']}")
    print(f"    完成: {summary['completed']}")

    # ── Generate plots ──
    print("\n📊 Generating plots …")
    _plot_llm_apr_and_confidence(sim.steps, args.ability, args.mode, output_dir, ts)
    _plot_llm_accuracy_trend(sim.steps, args.ability, args.mode, output_dir, ts)
    _plot_llm_confidence_distribution(sim.steps, output_dir, ts)
    _plot_llm_latency(sim.steps, output_dir, ts)
    _plot_llm_remediation_timeline(sim.steps, args.ability, output_dir, ts)

    print(f"\n✅ All outputs saved in {output_dir}")
    print("=" * 70)


# ═══════════════════════════════════════════════════════════════════════════
# Plot functions (LLM specific)
# ═══════════════════════════════════════════════════════════════════════════

def _plot_llm_apr_and_confidence(steps: list, ability: str, mode: str, output_dir: Path, ts: str):
    """APR curve overlaid with LLM confidence."""
    fig, ax1 = plt.subplots(figsize=(14, 6))
    color_line = COLORS.get(ability, COLORS["medium"])["line"]
    mode_zh = "教學" if mode == "teaching" else "評量"

    ax1.set_title(f"LLM 模擬學生 — APR 與 LLM 信心度 ({ability}/{mode_zh})",
                  fontsize=14, fontweight="bold")

    x = [s["step_number"] for s in steps]
    aprs = [s["current_apr"] for s in steps]
    ax1.plot(x, aprs, color=color_line, linewidth=2.5, marker="o", markersize=5, label="APR")
    ax1.axhline(y=0.65, color="gray", linestyle="--", alpha=0.5, label="目標 APR")
    ax1.set_xlabel("步驟", fontsize=11)
    ax1.set_ylabel("APR", fontsize=11, color=color_line)
    ax1.set_ylim(0, 1)

    # LLM confidence on twin axis
    ax2 = ax1.twinx()
    confidences = []
    conf_x = []
    for s in steps:
        detail = s.get("llm_detail", {})
        if detail and "confidence" in detail:
            conf_x.append(s["step_number"])
            confidences.append(detail["confidence"])

    if confidences:
        ax2.bar(conf_x, confidences, alpha=0.3, color="#3498db", width=0.6, label="LLM 信心度")
        ax2.set_ylabel("LLM 信心度", fontsize=11, color="#3498db")
        ax2.set_ylim(0, 1.2)

    # Correct / incorrect markers
    for s in steps:
        if s.get("is_correct") is True:
            ax1.scatter(s["step_number"], s["current_apr"],
                        marker="o", color="#27ae60", s=40, zorder=5)
        elif s.get("is_correct") is False:
            ax1.scatter(s["step_number"], s["current_apr"],
                        marker="x", color="#e74c3c", s=50, zorder=5, linewidths=2)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, fontsize=9, loc="upper left")
    ax1.grid(True, alpha=0.3)

    plt.tight_layout()
    path = output_dir / f"plot_llm_apr_confidence_{ts}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  📈 APR + Confidence → {path}")


def _plot_llm_accuracy_trend(steps: list, ability: str, mode: str, output_dir: Path, ts: str):
    """Rolling accuracy (window=5) over steps."""
    fig, ax = plt.subplots(figsize=(12, 5))
    mode_zh = "教學" if mode == "teaching" else "評量"
    ax.set_title(f"LLM 正確率滾動趨勢 ({ability}/{mode_zh})", fontsize=14, fontweight="bold")

    results_binary = []
    for s in steps:
        if s.get("is_correct") is not None:
            results_binary.append(1 if s["is_correct"] else 0)

    if len(results_binary) < 2:
        plt.close(fig)
        return

    window = min(5, len(results_binary))
    rolling = []
    for i in range(len(results_binary)):
        start = max(0, i - window + 1)
        segment = results_binary[start:i + 1]
        rolling.append(sum(segment) / len(segment))

    x = list(range(1, len(rolling) + 1))
    color_line = COLORS.get(ability, COLORS["medium"])["line"]
    ax.plot(x, rolling, color=color_line, linewidth=2.5, marker=".", markersize=4)
    ax.fill_between(x, 0, rolling, alpha=0.15, color=color_line)
    ax.axhline(y=0.5, color="gray", linestyle="--", alpha=0.4)
    ax.set_xlabel("已作答步驟", fontsize=11)
    ax.set_ylabel(f"滾動正確率 (window={window})", fontsize=11)
    ax.set_ylim(0, 1.05)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    path = output_dir / f"plot_llm_accuracy_trend_{ts}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  📈 Accuracy trend → {path}")


def _plot_llm_confidence_distribution(steps: list, output_dir: Path, ts: str):
    """Histogram of LLM confidence values, split by correct/incorrect."""
    confidences_correct = []
    confidences_wrong = []
    for s in steps:
        detail = s.get("llm_detail", {})
        if not detail or "confidence" not in detail:
            continue
        conf = detail["confidence"]
        if s.get("is_correct") is True:
            confidences_correct.append(conf)
        elif s.get("is_correct") is False:
            confidences_wrong.append(conf)

    if not confidences_correct and not confidences_wrong:
        return

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_title("LLM 信心度分佈 (正確 vs 錯誤)", fontsize=14, fontweight="bold")

    bins = np.linspace(0, 1, 11)
    if confidences_correct:
        ax.hist(confidences_correct, bins=bins, alpha=0.6, color="#27ae60",
                edgecolor="white", label=f"正確 (n={len(confidences_correct)})")
    if confidences_wrong:
        ax.hist(confidences_wrong, bins=bins, alpha=0.6, color="#e74c3c",
                edgecolor="white", label=f"錯誤 (n={len(confidences_wrong)})")

    ax.set_xlabel("LLM 信心度", fontsize=11)
    ax.set_ylabel("次數", fontsize=11)
    ax.legend(fontsize=10)
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    path = output_dir / f"plot_llm_confidence_hist_{ts}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  📊 Confidence histogram → {path}")


def _plot_llm_latency(steps: list, output_dir: Path, ts: str):
    """LLM response latency per step."""
    latencies = []
    lat_x = []
    for s in steps:
        detail = s.get("llm_detail", {})
        if detail and "latency_ms" in detail:
            lat_x.append(s["step_number"])
            latencies.append(detail["latency_ms"] / 1000.0)  # seconds

    if not latencies:
        return

    fig, ax = plt.subplots(figsize=(12, 4))
    ax.set_title("LLM 回應延遲 (秒)", fontsize=14, fontweight="bold")
    ax.bar(lat_x, latencies, color="#3498db", alpha=0.7, edgecolor="white", width=0.7)
    ax.axhline(y=sum(latencies) / len(latencies), color="#e74c3c", linestyle="--",
               label=f"平均: {sum(latencies)/len(latencies):.1f}s")
    ax.set_xlabel("步驟", fontsize=11)
    ax.set_ylabel("延遲 (秒)", fontsize=11)
    ax.legend(fontsize=10)
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    path = output_dir / f"plot_llm_latency_{ts}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  ⏱️ Latency → {path}")


def _plot_llm_remediation_timeline(steps: list, ability: str, output_dir: Path, ts: str):
    """Remediation timeline for LLM run."""
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.set_title(f"LLM 模擬 — 補救時間線 ({ability})", fontsize=14, fontweight="bold")

    x = [s["step_number"] for s in steps]
    modes_binary = [1 if s.get("current_mode") == "remediation" else 0 for s in steps]
    aprs = [s["current_apr"] for s in steps]
    color = COLORS.get(ability, COLORS["medium"])

    ax2 = ax.twinx()
    ax.fill_between(x, 0, modes_binary, alpha=0.25, color="#e74c3c", step="mid", label="補救模式")
    ax2.plot(x, aprs, color=color["line"], linewidth=2, label="APR")

    # Correct / incorrect scatter
    for s in steps:
        if s.get("is_correct") is True:
            ax2.scatter(s["step_number"], s["current_apr"], marker="o",
                        color="#27ae60", s=30, zorder=5)
        elif s.get("is_correct") is False:
            ax2.scatter(s["step_number"], s["current_apr"], marker="x",
                        color="#e74c3c", s=40, zorder=5, linewidths=1.5)

    ax.set_ylabel("模式", fontsize=10)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["主線", "補救"])
    ax.set_ylim(-0.1, 1.3)
    ax.set_xlabel("步驟", fontsize=11)
    ax2.set_ylabel("APR", fontsize=10)
    ax2.set_ylim(0, 1)

    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, fontsize=9, loc="upper right")
    ax.grid(True, alpha=0.2)

    plt.tight_layout()
    path = output_dir / f"plot_llm_remediation_{ts}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  📍 LLM Remediation timeline → {path}")


if __name__ == "__main__":
    main()
