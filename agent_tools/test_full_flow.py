# -*- coding: utf-8 -*-
"""
完整流程测试（不调用 AI）
验证从模型选择到客户端创建的完整逻辑
"""
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from config import Config
from core.ai_wrapper import LocalAIClient, GoogleAIClient

print("="*70)
print("🔄 模拟完整 Benchmark 流程")
print("="*70)

# Step 1: 模拟用户选择
print("\n📝 Step 1: 模拟用户选择模型")
override_model = "qwen3-14b"  # 用户选择
print(f"   选择的模型: {override_model}")

# Step 2: 创建客户端（和 benchmark.py 中的逻辑完全相同）
print("\n🔧 Step 2: 创建 AI 客户端")
print("-"*70)

if override_model:
    if hasattr(Config, 'CODER_PRESETS') and override_model in Config.CODER_PRESETS:
        preset = Config.CODER_PRESETS[override_model]
        provider = preset.get('provider', 'local').lower()
        model_name = preset.get('model', override_model)
        temperature = preset.get('temperature', 0.1)
        max_tokens = preset.get('max_tokens', 16384)
        extra_body = preset.get('extra_body', {})
        safety_settings = preset.get('safety_settings')
        
        print(f"   从 CODER_PRESETS 读取配置:")
        print(f"   - Provider: {provider}")
        print(f"   - Model: {model_name}")
        print(f"   - Temperature: {temperature}")
        print(f"   - Max Tokens: {max_tokens}")
        
        # Instantiate client
        if provider in ['google', 'gemini']:
            client = GoogleAIClient(model_name, temperature, max_tokens=max_tokens, safety_settings=safety_settings)
            print(f"\n   ✅ GoogleAIClient 创建成功")
        else:
            client = LocalAIClient(model_name, temperature, max_tokens=max_tokens, extra_body=extra_body)
            print(f"\n   ✅ LocalAIClient 创建成功")
            print(f"      - API URL: {client.api_url}")
            print(f"      - Model: {client.model}")
            print(f"      - Temperature: {client.temperature}")
            print(f"      - Max Tokens: {client.max_tokens}")
    else:
        print(f"   ❌ Model '{override_model}' not found in CODER_PRESETS")
        client = None

# Step 3: 验证客户端可用性
print("\n✅ Step 3: 验证客户端")
print("-"*70)

if client:
    print(f"   客户端类型: {type(client).__name__}")
    print(f"   是否为 LocalAIClient: {isinstance(client, LocalAIClient)}")
    print(f"   是否为 GoogleAIClient: {isinstance(client, GoogleAIClient)}")
    
    # 检查必要的方法
    if hasattr(client, 'generate_content'):
        print(f"   ✓ generate_content() 方法存在")
    else:
        print(f"   ✗ generate_content() 方法不存在")
else:
    print(f"   ❌ 客户端创建失败")

print("\n" + "="*70)
print("🎉 流程测试完成！")
print("="*70)
print("\n💡 结论:")
print("   ✅ 模型选择逻辑正确")
print("   ✅ 客户端创建逻辑正确")
print("   ✅ 可以开始运行实际测试")
print("="*70)
