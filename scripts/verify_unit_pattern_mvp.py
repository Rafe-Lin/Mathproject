#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==============================================================================
# ID: verify_unit_pattern_mvp.py
# Version: V1.0.0 (Unit Pattern MVP Check)
# Last Updated: 2026-04-15
# Author: *Steve
#
# [Description]:
#   驗證單元選題器與 pattern skill 之 generate() 可正常運作（根式單元範例），
#   作為單元—題型架構之煙霧測試。執行：python scripts/verify_unit_pattern_mvp.py
#
# [Database Schema Usage]:
#   無直接資料庫操作。
#
# [Logic Flow]:
#   1. 測試 unit selector 回傳技能 ID。
#   2. 動態 import 各 pattern skill 並呼叫 generate。
# ==============================================================================

import os
import sys

# 確保專案根目錄在 path 中
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if basedir not in sys.path:
    sys.path.insert(0, basedir)

os.chdir(basedir)


def test_unit_selector():
    """測試 unit selector"""
    print("=== 1. 測試 unit selector ===")
    from core.unit_selector import select_pattern_skill_for_unit, get_unit_pattern_skills
    
    curriculum, volume, chapter = "junior_high", "數學2上", "第二章 二次方根與畢氏定理"
    skills = get_unit_pattern_skills(curriculum, volume, chapter)
    print(f"   單元 pattern skills: {skills}")
    
    chosen = select_pattern_skill_for_unit(curriculum, volume, chapter)
    print(f"   抽樣選中: {chosen}")
    assert chosen in ["jh_數學2上_RadicalSimplify", "jh_數學2上_RadicalAddSub", "jh_數學2上_RadicalMultiply"]
    print("   ✓ unit selector OK\n")


def test_pattern_skill_generate():
    """測試三個 pattern skill 的 generate()"""
    print("=== 2. 測試 pattern skill generate() ===")
    import importlib
    
    for skill_id in ["jh_數學2上_RadicalSimplify", "jh_數學2上_RadicalAddSub", "jh_數學2上_RadicalMultiply"]:
        try:
            mod = importlib.import_module(f"skills.{skill_id}")
            data = mod.generate(level=1)
            assert "question_text" in data
            assert "correct_answer" in data
            assert "answer" in data
            print(f"   {skill_id}: question_text[:60]... correct_answer={data['correct_answer']}")
            print(f"   ✓ {skill_id} OK")
        except Exception as e:
            print(f"   ✗ {skill_id} 失敗: {e}")
            raise
    print()


def test_full_unit_flow():
    """模擬完整單元出題流程：selector → import → generate"""
    print("=== 3. 完整單元出題流程 ===")
    from core.unit_selector import select_pattern_skill_for_unit
    import importlib
    
    curriculum, volume, chapter = "junior_high", "數學2上", "第二章 二次方根與畢氏定理"
    
    for i in range(5):
        skill_id = select_pattern_skill_for_unit(curriculum, volume, chapter)
        mod = importlib.import_module(f"skills.{skill_id}")
        data = mod.generate(level=1)
        print(f"   第{i+1}次: skill={skill_id}, answer={data.get('correct_answer','')[:30]}")
    
    print("   ✓ 完整流程 OK (每次可能抽到不同 pattern)\n")


if __name__ == "__main__":
    print("\n【單元-題型-技能檔 MVP 驗證】\n")
    try:
        test_unit_selector()
        test_pattern_skill_generate()
        test_full_unit_flow()
        print("全部通過 ✓\n")
    except Exception as e:
        print(f"\n驗證失敗: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
