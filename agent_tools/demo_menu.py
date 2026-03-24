# -*- coding: utf-8 -*-
"""
快速演示：模型選擇菜單
用於確認選單正常工作，不執行實際測試
"""
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from agent_tools.benchmark import show_model_selection_menu

print("="*70)
print("🎯 Benchmark 模型選擇菜單演示")
print("="*70)
print("\n這個腳本只是演示菜單，不會執行實際測試")
print("按 Ctrl+C 可隨時退出\n")

try:
    selected_model = show_model_selection_menu()
    
    if selected_model:
        print(f"\n✅ 您選擇的模型: {selected_model}")
        print("\n📋 選擇完成！")
        print("   若要執行實際測試，請運行：")
        print("   python agent_tools/benchmark.py")
    else:
        print("\n⚠️  未選擇模型")
        
except KeyboardInterrupt:
    print("\n\n⚠️  已取消")
    
print("\n" + "="*70)
