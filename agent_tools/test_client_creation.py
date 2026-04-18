# -*- coding: utf-8 -*-
"""
测试模型客户端创建
"""
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from config import Config
from core.ai_wrapper import LocalAIClient, GoogleAIClient

print("="*70)
print("🧪 测试模型客户端创建逻辑")
print("="*70)

test_models = ['qwen3-14b', 'qwen3-8b', 'gemini-3-flash']

for override_model in test_models:
    print(f"\n🔍 测试模型: {override_model}")
    print("-"*70)
    
    if hasattr(Config, 'CODER_PRESETS') and override_model in Config.CODER_PRESETS:
        preset = Config.CODER_PRESETS[override_model]
        provider = preset.get('provider', 'local').lower()
        model_name = preset.get('model', override_model)
        temperature = preset.get('temperature', 0.1)
        max_tokens = preset.get('max_tokens', 16384)
        extra_body = preset.get('extra_body', {})
        safety_settings = preset.get('safety_settings')
        
        print(f"  Provider: {provider}")
        print(f"  Model Name: {model_name}")
        print(f"  Temperature: {temperature}")
        print(f"  Max Tokens: {max_tokens}")
        
        # Test client instantiation
        try:
            if provider in ['google', 'gemini']:
                client = GoogleAIClient(model_name, temperature, max_tokens=max_tokens, safety_settings=safety_settings)
                print(f"  ✅ GoogleAIClient 创建成功")
            else:
                client = LocalAIClient(model_name, temperature, max_tokens=max_tokens, extra_body=extra_body)
                print(f"  ✅ LocalAIClient 创建成功")
                print(f"     - API URL: {client.api_url}")
                print(f"     - Model: {client.model}")
        except Exception as e:
            print(f"  ❌ 客户端创建失败: {e}")
    else:
        print(f"  ❌ 未找到配置")

print("\n" + "="*70)
print("✅ 测试完成")
print("="*70)
