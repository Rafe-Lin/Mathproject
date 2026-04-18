# -*- coding: utf-8 -*-
"""
快速測試腳本：驗證模型選擇菜單
"""
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from config import Config

print("="*70)
print("🔍 驗證 Config.CODER_PRESETS 配置")
print("="*70)

if hasattr(Config, 'CODER_PRESETS'):
    print(f"\n✅ 找到 {len(Config.CODER_PRESETS)} 個模型配置：\n")
    for key, preset in Config.CODER_PRESETS.items():
        provider = preset.get('provider', 'unknown')
        model_name = preset.get('model', key)
        desc = preset.get('description', key)
        
        icon = "☁️ " if provider == 'google' else "💻"
        print(f"  {icon} [{key}]")
        print(f"     Model: {model_name}")
        print(f"     Description: {desc}")
        print()

print("="*70)
print("🎯 Benchmark 菜單顯示預覽")
print("="*70)

BENCHMARK_MODELS = ['gemini-3-flash', 'qwen3-14b', 'qwen3-8b']

print("\n🤖 [模型選擇] 請選擇要使用的 AI 模型")
print("="*70)

for i, model_key in enumerate(BENCHMARK_MODELS, 1):
    if model_key in Config.CODER_PRESETS:
        preset = Config.CODER_PRESETS[model_key]
        provider = preset.get('provider', 'unknown')
        model_name = preset.get('model', model_key)
        desc = preset.get('description', model_key)
        
        icon = "☁️ " if provider == 'google' else "💻"
        print(f"   [{i}] {icon} {model_name} ({desc})")
    else:
        print(f"   [{i}] ⚠️  {model_key} (未找到配置)")

print("\n" + "="*70)
print("✅ 測試完成！")
print("="*70)
