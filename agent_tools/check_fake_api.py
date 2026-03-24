#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证 SKILL.md 是否移除了不存在的 API"""

from pathlib import Path

def check_for_fake_api(unit_name):
    """检查是否还存在不存在的 API 引用"""
    skill_path = Path(__file__).parent.parent / "agent_skills" / unit_name / "SKILL.md"
    
    print(f"\n{'='*70}")
    print(f"📂 {unit_name}")
    print(f"{'='*70}")
    
    try:
        with open(skill_path, encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"❌ 文件不存在: {skill_path}")
        return False
    
    # 检查不应该存在的内容
    bad_patterns = {
        "IntegerOps.": "❌ 找到 IntegerOps.* API 引用",
        "FractionOps.": "❌ 找到 FractionOps.* API 引用",
        "【系統已注入的輔助函式（API）】": "❌ 找到错误的 API 章节声明",
        "【強制使用 API】": "❌ 找到强制使用 API 的要求",
    }
    
    # 应该存在的内容
    good_patterns = {
        "系統無注入任何 API": "✅ 明确说明无 API",
        "只能使用 random 和 Fraction": "✅ 明确说明只能用标准库",
        "禁止調用不存在的": "✅ 警告不要调用不存在的 API",
    }
    
    issues = []
    for pattern, message in bad_patterns.items():
        if pattern in content:
            print(f"❌ {message}")
            issues.append(message)
    
    for pattern, message in good_patterns.items():
        if pattern in content:
            print(f"✅ {message}")
        else:
            print(f"⚠️ 缺少: {message}")
            issues.append(f"缺少: {message}")
    
    if not issues:
        print(f"\n✅ 所有检查通过！")
        return True
    else:
        print(f"\n⚠️ 发现 {len(issues)} 个问题")
        return False

if __name__ == "__main__":
    print("🔍 验证 SKILL.md 是否已移除虚假 API")
    print("="*70)
    
    units = [
        "jh_數學2上_FourOperationsOfRadicals",
        "jh_數學1上_FourArithmeticOperationsOfIntegers",
        "jh_數學1上_FourArithmeticOperationsOfNumbers"
    ]
    
    results = []
    for unit in units:
        result = check_for_fake_api(unit)
        results.append((unit, result))
    
    print("\n" + "="*70)
    print("📊 總結")
    print("="*70)
    
    for unit, result in results:
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{status} - {unit}")
    
    all_pass = all(r for _, r in results)
    if all_pass:
        print("\n🎉 所有單元現在都不包含虚假 API！")
        print("💡 AI 现在会使用纯 Python 代码生成题目。")
    else:
        print("\n⚠️ 部分單元仍需修正")
