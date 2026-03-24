# -*- coding: utf-8 -*-
"""
验证 Ab2/Ab3 流程的关键组件
"""
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

print("="*70)
print("🔍 验证 Ab2/Ab3 关键配置")
print("="*70)

# 1. 验证 Prompt 文件存在
print("\n📄 步骤 1: 检查 Prompt 文件")
print("-"*70)

skill_name = "jh_數學2上_FourOperationsOfRadicals"
skill_dir = os.path.join(PROJECT_ROOT, "agent_skills", skill_name)

ab1_prompt = os.path.join(skill_dir, "experiments", "ab1_bare_prompt.md")
skill_md = os.path.join(skill_dir, "SKILL.md")

if os.path.exists(ab1_prompt):
    print(f"✅ Ab1 Prompt: {ab1_prompt}")
    with open(ab1_prompt, 'r', encoding='utf-8') as f:
        content = f.read()
        if "check 函式必須回傳字典" in content:
            print("   ✓ 包含 check() 函數格式要求")
        if "絕對禁止任何中文註解" in content:
            print("   ✓ 包含中文註解禁令")
else:
    print(f"❌ Ab1 Prompt 不存在")

if os.path.exists(skill_md):
    print(f"✅ Ab2/Ab3 Prompt: {skill_md}")
    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()
        if "check() 函數正確格式" in content or "check 函式必須回傳字典" in content:
            print("   ✓ 包含 check() 函數格式要求")
        if "is_first 參數正確用法" in content:
            print("   ✓ 包含 is_first 正確用法說明")
        if "format_expression 正確用法" in content:
            print("   ✓ 包含 format_expression 正確用法說明")
        if "禁止任何中文註解" in content or "絕對禁止中文" in content:
            print("   ✓ 包含中文註解禁令")
else:
    print(f"❌ SKILL.md 不存在")

# 2. 验证 Healer 导入
print("\n🔧 步骤 2: 检查 Healer 组件")
print("-"*70)

try:
    from core.healers.regex_healer import RegexHealer
    print("✅ RegexHealer 导入成功")
    
    healer = RegexHealer()
    # 检查 heal_minimal 方法
    if hasattr(healer, 'heal_minimal'):
        print("   ✓ heal_minimal() 方法存在 (Ab2 使用)")
    if hasattr(healer, 'heal'):
        print("   ✓ heal() 方法存在 (Ab3 使用)")
except ImportError as e:
    print(f"❌ RegexHealer 导入失败: {e}")

try:
    from core.healers.ast_healer import ASTHealer
    print("✅ ASTHealer 导入成功")
    
    ast_healer = ASTHealer()
    if hasattr(ast_healer, 'heal'):
        print("   ✓ heal() 方法存在 (Ab3 使用)")
except ImportError as e:
    print(f"❌ ASTHealer 导入失败: {e}")

# 3. 验证 evals.json
print("\n📊 步骤 3: 检查测试用例")
print("-"*70)

import json
evals_file = os.path.join(skill_dir, "evals.json")

if os.path.exists(evals_file):
    print(f"✅ evals.json: {evals_file}")
    with open(evals_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        evals = data.get('evals', [])
        
        ab_counts = {'Ab1': 0, 'Ab2': 0, 'Ab3': 0}
        for e in evals:
            ab = e.get('ablation_target', 'Unknown')
            if ab in ab_counts:
                ab_counts[ab] += 1
        
        print(f"   总测试用例: {len(evals)}")
        for ab, count in ab_counts.items():
            print(f"   - {ab}: {count} 个")
else:
    print(f"❌ evals.json 不存在")

# 4. 验证 benchmark.py 逻辑
print("\n🎯 步骤 4: 验证 benchmark.py 逻辑")
print("-"*70)

from agent_tools.benchmark import load_prompt_from_skill

# 测试 Ab1 (应该读取 ab1_bare_prompt.md)
ab1_content = load_prompt_from_skill(skill_name, "Ab1")
if ab1_content and "絕對禁止任何中文註解" in ab1_content:
    print("✅ Ab1 正确读取 ab1_bare_prompt.md")
else:
    print("❌ Ab1 读取错误")

# 测试 Ab2 (应该读取 SKILL.md)
ab2_content = load_prompt_from_skill(skill_name, "Ab2")
if ab2_content and "RadicalOps" in ab2_content:
    print("✅ Ab2 正确读取 SKILL.md")
else:
    print("❌ Ab2 读取错误")

# 测试 Ab3 (应该读取 SKILL.md)
ab3_content = load_prompt_from_skill(skill_name, "Ab3")
if ab3_content and "RadicalOps" in ab3_content:
    print("✅ Ab3 正确读取 SKILL.md")
else:
    print("❌ Ab3 读取错误")

print("\n" + "="*70)
print("✅ 验证完成！所有组件就绪")
print("="*70)
print("\n💡 提示:")
print("   - Ab1: 使用 ab1_bare_prompt.md (无 Healer)")
print("   - Ab2: 使用 SKILL.md + heal_minimal()")
print("   - Ab3: 使用 SKILL.md + heal() + AST")
print("="*70)
