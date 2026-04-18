# -*- coding: utf-8 -*-
"""
=============================================================================
測試名稱: test_radical_sqrt_fix.py
功能說明: 驗證 AdaptiveScaler 對 LLM 幻覺生成的 sqrt(x) 是否能正確修復為 \\sqrt{x}
測試對象: core.engine.scaler.AdaptiveScaler._execute_code
關聯技能: jh_數學2上_Radicals (根號運算)
=============================================================================
"""
import sys
import os
import unittest
import re

# 強制加入專案根目錄以匯入 core 模組
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.engine.scaler import AdaptiveScaler

class TestRadicalSqrtFix(unittest.TestCase):
    
    def setUp(self):
        self.scaler = AdaptiveScaler()

    def test_fix_sqrt_hallucination(self):
        """
        測試目標：驗證當 LLM 輸出 'sqrt(2)' 或 '(-5)sqrt(15)' 這種非 LaTeX 格式時，
        系統能否自動透過 Regex Healer Patch 將其修正為 '\\sqrt{2}'。
        """
        print("\n[Test] Running Radical Sqrt Fix Regression Test...")

        # 1. 模擬 LLM 生成的有問題代碼 (含 sqrt 幻覺)
        bad_code = """
def generate(level=1):
    return {
        "question_text": "計算 7sqrt(2) \\\\times 5sqrt(2) + (-5)sqrt(15) 的值。",
        "correct_answer": "...",
        "mode": 1
    }
"""
        # 2. 執行代碼 (這會觸發 _execute_code 尾端的 post-process patch)
        result = self.scaler._execute_code(bad_code, level=1)
        q_text = result.get("question_text", "")
        
        print(f"  > Original output simulated: ... 7sqrt(2) ... (-5)sqrt(15) ...")
        print(f"  > Healed output:             {q_text}")
        
        # 3. 斷言驗證
        self.assertNotIn("sqrt(", q_text, "錯誤：輸出中仍包含 'sqrt('，修復未生效")
        self.assertIn(r"\sqrt{2}", q_text, "錯誤：未能將 sqrt(2) 轉換為 \\sqrt{2}")
        self.assertIn(r"\sqrt{15}", q_text, "錯誤：未能將 sqrt(15) 轉換為 \\sqrt{15}")
        
        # 驗證複合結構
        # 期望：7sqrt(2) -> 7\sqrt{2}
        self.assertIn(r"7\sqrt{2}", q_text)
        self.assertIn(r"(-5)\sqrt{15}", q_text)
        print("  > ✅ Regression Test Passed: sqrt() hallucinations are fixed.")

if __name__ == "__main__":
    unittest.main()