#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""驗證 evals.json 格式和分布"""

import json
import sys
from pathlib import Path

def validate_evals():
    evals_path = Path(__file__).parent.parent / "agent_skills" / "jh_數學2上_FourOperationsOfRadicals" / "evals.json"
    
    print(f"📄 檢查文件: {evals_path}\n")
    
    try:
        with open(evals_path, encoding='utf-8') as f:
            data = json.load(f)
        print("✅ JSON 格式正確\n")
    except json.JSONDecodeError as e:
        print(f"❌ JSON 解析錯誤: {e}")
        sys.exit(1)
    
    evals = data.get("evals", [])
    print(f"📊 測試總數: {len(evals)}\n")
    
    # 統計消融分布
    ab_counts = {}
    level_dist = {}
    
    for e in evals:
        ab = e.get("ablation_target", "unknown")
        level = e.get("generation_kwargs", {}).get("level", 0)
        
        ab_counts[ab] = ab_counts.get(ab, 0) + 1
        
        key = f"{ab}_L{level}"
        level_dist[key] = level_dist.get(key, 0) + 1
    
    # 顯示消融分布
    print("🎯 消融分布:")
    for ab in sorted(ab_counts.keys()):
        print(f"  {ab}: {ab_counts[ab]}個")
    
    # 顯示難度分布
    print("\n📈 難度分布 (每個消融):")
    for ab in ["Ab1", "Ab2", "Ab3"]:
        print(f"\n  {ab}:")
        for lv in [1, 2, 3]:
            key = f"{ab}_L{lv}"
            count = level_dist.get(key, 0)
            print(f"    Level {lv}: {count}個")
    
    # 驗證均衡性
    print("\n✅ 均衡性驗證:")
    ab1_levels = [level_dist.get(f"Ab1_L{lv}", 0) for lv in [1, 2, 3]]
    ab2_levels = [level_dist.get(f"Ab2_L{lv}", 0) for lv in [1, 2, 3]]
    ab3_levels = [level_dist.get(f"Ab3_L{lv}", 0) for lv in [1, 2, 3]]
    
    if ab1_levels == ab2_levels == ab3_levels:
        print("  ✅ Ab1/Ab2/Ab3 難度分布完全相同")
        print(f"  分布: Easy×{ab1_levels[0]}, Medium×{ab1_levels[1]}, Hard×{ab1_levels[2]}")
    else:
        print("  ⚠️ 難度分布不一致:")
        print(f"    Ab1: {ab1_levels}")
        print(f"    Ab2: {ab2_levels}")
        print(f"    Ab3: {ab3_levels}")

if __name__ == "__main__":
    validate_evals()
