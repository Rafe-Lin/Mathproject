#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证所有三个单元的 SKILL.md 是否采用统一的严谨格式"""

from pathlib import Path

def check_skill_md(unit_name):
    """检查单个 SKILL.md 的关键特征"""
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
    
    checks = {
        "【絕對禁止輸出 thinking】警告": "【絕對禁止輸出 thinking" in content,
        "【第一優先規則】声明": "【第一優先規則】" in content,
        "⚠️ check 函式【必須返回字典】": "⚠️ check 函式【必須返回字典】" in content,
        "$$   ...   $$ 数学式包裹": "$$   " in content,
        "\\left| ... \\right| 绝对值": "\\left|" in content and "\\right|" in content,
        "【常見錯誤警告】章节": "【常見錯誤警告】" in content,
        "完整 check 函数示例": "def check(user_answer, correct_answer):" in content and "return {'correct'" in content,
        "禁止中文注解警告": "絕對禁止任何中文註解" in content or "禁止中文註釋" in content,
    }
    
    passed = 0
    total = len(checks)
    
    for feature, present in checks.items():
        status = "✅" if present else "❌"
        print(f"{status} {feature}")
        if present:
            passed += 1
    
    print(f"\n通過率: {passed}/{total} ({passed/total*100:.0f}%)")
    
    return passed == total

if __name__ == "__main__":
    print("🔍 驗證所有單元的 SKILL.md 格式一致性")
    print("="*70)
    
    units = [
        "jh_數學2上_FourOperationsOfRadicals",
        "jh_數學1上_FourArithmeticOperationsOfIntegers",
        "jh_數學1上_FourArithmeticOperationsOfNumbers"
    ]
    
    results = []
    for unit in units:
        result = check_skill_md(unit)
        results.append((unit, result))
    
    print("\n" + "="*70)
    print("📊 總結")
    print("="*70)
    
    for unit, result in results:
        status = "✅ 通過" if result else "⚠️ 需改進"
        print(f"{status} - {unit}")
    
    all_pass = all(r for _, r in results)
    if all_pass:
        print("\n🎉 所有單元的 SKILL.md 都採用統一嚴謹格式！")
    else:
        print("\n⚠️ 部分單元需要進一步對齊格式")
