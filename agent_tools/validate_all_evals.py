#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证所有三个单元的 evals.json 文件"""

import json
from pathlib import Path

def validate_unit(unit_name):
    """验证单个单元的 evals.json"""
    evals_path = Path(__file__).parent.parent / "agent_skills" / unit_name / "evals.json"
    
    print(f"\n{'='*70}")
    print(f"📂 {unit_name}")
    print(f"{'='*70}")
    
    try:
        with open(evals_path, encoding='utf-8') as f:
            data = json.load(f)
        print("✅ JSON 格式正確")
    except json.JSONDecodeError as e:
        print(f"❌ JSON 解析錯誤: {e}")
        return False
    except FileNotFoundError:
        print(f"❌ 文件不存在: {evals_path}")
        return False
    
    evals = data.get("evals", [])
    print(f"📊 測試總數: {len(evals)}")
    
    # 统计消融和难度分布
    ab_counts = {"Ab1": 0, "Ab2": 0, "Ab3": 0}
    level_matrix = {f"Ab{i}_L{j}": 0 for i in [1,2,3] for j in [1,2,3]}
    
    for e in evals:
        ab = e.get("ablation_target", "unknown")
        level = e.get("generation_kwargs", {}).get("level", 0)
        
        if ab in ab_counts:
            ab_counts[ab] += 1
        
        key = f"{ab}_L{level}"
        if key in level_matrix:
            level_matrix[key] += 1
    
    # 显示消融分布
    print(f"\n🎯 消融分布:")
    for ab in ["Ab1", "Ab2", "Ab3"]:
        print(f"  {ab}: {ab_counts[ab]}個")
    
    # 显示矩阵
    print(f"\n📊 完整矩阵 (難度 × 消融):")
    print(f"     │ Level 1 │ Level 2 │ Level 3 │")
    print(f"─────┼─────────┼─────────┼─────────┤")
    for ab in ["Ab1", "Ab2", "Ab3"]:
        counts = [level_matrix[f"{ab}_L{lv}"] for lv in [1,2,3]]
        print(f" {ab} │    {counts[0]}    │    {counts[1]}    │    {counts[2]}    │")
    
    # 验证均衡性
    expected = [1, 1, 1]
    all_balanced = True
    for ab in ["Ab1", "Ab2", "Ab3"]:
        actual = [level_matrix[f"{ab}_L{lv}"] for lv in [1,2,3]]
        if actual != expected:
            all_balanced = False
            print(f"\n⚠️ {ab} 分布不均: {actual} (期望: {expected})")
    
    if all_balanced and len(evals) == 9:
        print(f"\n✅ 完美的 3×3 科學實驗設計！")
        return True
    elif len(evals) != 9:
        print(f"\n⚠️ 測試數量錯誤: {len(evals)} (期望: 9)")
        return False
    else:
        return False

if __name__ == "__main__":
    print("🔍 驗證所有單元的 evals.json 文件")
    print("="*70)
    
    units = [
        "jh_數學2上_FourOperationsOfRadicals",
        "jh_數學1上_FourArithmeticOperationsOfIntegers",
        "jh_數學1上_FourArithmeticOperationsOfNumbers"
    ]
    
    results = []
    for unit in units:
        result = validate_unit(unit)
        results.append((unit, result))
    
    print("\n" + "="*70)
    print("📊 總結")
    print("="*70)
    
    for unit, result in results:
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{status} - {unit}")
    
    all_pass = all(r for _, r in results)
    if all_pass:
        print("\n🎉 所有單元都已準備就緒！可以運行 benchmark.py")
    else:
        print("\n⚠️ 部分單元需要修正")
