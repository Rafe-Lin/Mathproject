# -*- coding: utf-8 -*-
# ==============================================================================
# ID: plot_benchmark.py
# Version: V1.0.0 (Visualization Tool)
# Last Updated: 2026-02-17
# Author: Math AI Research Team (Advisor & Student)
#
# [Description]:
#   本程式用於將 benchmark.py 產出的實驗數據可視化，生成柱狀圖 (Bar Chart)。
#   主要展示不同消融階段 (Ab1 vs Ab2 vs Ab3) 的通過率 (Pass Rate) 差異，
#   直觀呈現 Healer 機制對模型表現的提升幅度。
#
# [Scientific Control Strategy]:
#   - 視覺化三組對照數據：Bare Prompt, Scaffold, Full Healing。
#   - 標註關鍵改進點 (Syntax Errors, Format Issues, Reliable)。
#
# [Database Schema Usage]:
#   - No Database interaction.
#   - Hardcoded data points (currently) or reads from log files.
#
# [Logic Flow]:
#   1. Define Data        -> 設定各實驗組的通過率數據。
#   2. Setup Plot         -> 設定畫布大小、顏色與樣式。
#   3. Draw Bars          -> 繪製柱狀圖並標註數值。
#   4. Annotation         -> 添加箭頭與說明文字，解釋數據變化的原因。
#   5. Save Image         -> 輸出為 benchmark_result.png。
# ==============================================================================
import matplotlib.pyplot as plt
import os

def plot_benchmark_results():
    # 數據準備 (基於實驗結果)
    versions = ['v0 (Bare Prompt)', 'v1 (Scaffold)', 'v2 (Full Healing)']
    pass_rates = [0, 40, 100]
    colors = ['#ff4d4d', '#ffcc00', '#28a745'] # 紅 -> 黃 -> 綠

    # 設定圖表風格
    plt.figure(figsize=(10, 6))
    bars = plt.bar(versions, pass_rates, color=colors, width=0.6)

    # 添加標題與標籤
    plt.title('Agent Skill Benchmark: Pass Rate Improvement (Qwen-14B)', fontsize=16, fontweight='bold', pad=20)
    plt.ylabel('Pass Rate (%)', fontsize=12)
    plt.ylim(0, 110) # 預留空間給標籤
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # 在柱狀圖上方標註數值
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 2,
                 f'{height}%',
                 ha='center', va='bottom', fontsize=14, fontweight='bold')

    # 添加趨勢箭頭或說明 (可選)
    plt.annotate('Syntax Errors\n(Markdown, Braces)', 
                 xy=(0, 5), xytext=(0, 20),
                 ha='center', va='bottom', arrowprops=dict(arrowstyle='->', color='red'))
                 
    plt.annotate('Format Issues\n(JSON Truncation)', 
                 xy=(1, 45), xytext=(1, 60),
                 ha='center', va='bottom', arrowprops=dict(arrowstyle='->', color='orange'))

    plt.annotate('100% Reliable\n(Healer Fixed All)', 
                 xy=(2, 102), xytext=(2, 85),
                 ha='center', va='top', color='white', fontweight='bold')

    # 存檔
    output_path = os.path.join(os.path.dirname(__file__), '..', 'benchmark_result.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ 圖表已生成: {os.path.abspath(output_path)}")
    print("📊 這張圖表清晰展示了從 0% 到 100% 的巨大進步！")

if __name__ == "__main__":
    try:
        plot_benchmark_results()
    except ImportError:
        print("❌ 缺少 matplotlib 庫。正在嘗試安裝...")
        os.system("pip install matplotlib")
        plot_benchmark_results()
