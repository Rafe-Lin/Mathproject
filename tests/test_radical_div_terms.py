# -*- coding: utf-8 -*-
"""
=============================================================================
測試名稱: test_radical_div_terms.py
功能說明: 驗證 RadicalOps.div_terms 對根式除法的化簡與有理化
測試對象: core.scaffold.domain_libs.RadicalOps
關聯技能: jh_數學2上_FourOperationsOfRadicals
=============================================================================
"""

import os
import sys
import unittest
from fractions import Fraction


# 強制加入專案根目錄以匯入 core 模組
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.scaffold.domain_libs import RadicalOps  # noqa: E402


class TestRadicalDivTerms(unittest.TestCase):
    def test_div_simplifies_when_divisible(self):
        c, r = RadicalOps.div_terms(1, 35, 1, 5)
        self.assertEqual(r, 7)
        self.assertTrue(c == 1 or c == Fraction(1, 1))

        terms = {}
        RadicalOps.add_term(terms, c, r)
        self.assertEqual(RadicalOps.format_expression(terms), r"\sqrt{7}")

    def test_div_rationalizes_when_not_divisible(self):
        c, r = RadicalOps.div_terms(1, 2, 1, 3)
        self.assertEqual((c, r), (Fraction(1, 3), 6))

        terms = {}
        RadicalOps.add_term(terms, c, r)
        self.assertEqual(RadicalOps.format_expression(terms), r"\frac{1}{3}\sqrt{6}")


if __name__ == "__main__":
    unittest.main()

