from __future__ import annotations

import os
import sys


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.fraction_domain_functions import FractionFunctionHelper


def test_fraction_simplify_negative_improper():
    helper = FractionFunctionHelper()
    body = helper.generate_from_config(helper.build_config("將下列各分數化成最簡分數。⑴ $-21/9$"))
    assert body["correct_answer"] == "-7/3"


def test_fraction_fill_blank_chain():
    helper = FractionFunctionHelper()
    body = helper.generate_from_config(
        helper.build_config("在下列空格內填入適當的數字。⑴ $-7/3=(-35)/15=28/(_)=(_)/(-45)$")
    )
    assert body["correct_answer"] == "-12,105"


def test_fraction_compare_negative_mixed_numbers():
    helper = FractionFunctionHelper()
    body = helper.generate_from_config(helper.build_config("比較 $-1 1/2$、$-1 2/3$、$-1 3/4$ 的大小。"))
    assert body["correct_answer"] == "-1 3/4 < -1 2/3 < -1 1/2"


def test_fraction_eval_decimal_mixed_expression():
    helper = FractionFunctionHelper()
    body = helper.generate_from_config(helper.build_config("計算下列各式的值。⑴ $0.3*2/3-(-7/5)/[5/3+(-0.5)]$"))
    assert body["correct_answer"] == "7/5"


def test_fraction_word_problem_drone_weight():
    helper = FractionFunctionHelper()
    body = helper.generate_from_config(
        helper.build_config(
            "一臺農用無人機裝滿農藥的重量為 45 公斤，若每分鐘噴灑的農藥重量皆相等，噴灑飛行 50 分鐘後，可將農藥噴完沒有剩下。某次此無人機裝滿農藥噴灑飛行 20 分鐘後，無人機與剩餘農藥重量為 37 公斤，則此無人機未裝農藥時的重量為多少公斤？"
        )
    )
    assert body["correct_answer"] == "25"


def test_fraction_common_factor_expression_answer():
    helper = FractionFunctionHelper()
    body = helper.generate_from_config(
        helper.build_config(r"計算下列各式的值。⑵ $3\frac{9}{11}\times(-57)-1\frac{9}{11}\times(-57)$")
    )
    assert body["correct_answer"] == "-114"


def test_fraction_word_problem_library_total():
    helper = FractionFunctionHelper()
    body = helper.generate_from_config(
        helper.build_config("已知康康國中圖書館今年添購了 450 本新書，且添購新書前的數量是添購後的 $7/10$ 倍，試問添購前圖書館共有多少本書？")
    )
    assert body["correct_answer"] == "1050"


def test_fraction_question_text_wraps_word_problem_fraction_in_latex():
    helper = FractionFunctionHelper()
    body = helper.generate_from_config(
        helper.build_config("有一瓶果汁，連瓶子共重 930 公克，喝了 2/3 瓶的果汁後，剩餘的果汁連瓶子共重 430 公克，求空瓶子重多少公克？")
    )
    assert "$\\frac{2}{3}$" in body["question_text"]


def test_fraction_question_text_renders_mixed_number_in_textbook_latex():
    helper = FractionFunctionHelper()
    body = helper.generate_from_config(helper.build_config("計算 $(-2 3/4)+1 2/7$ 的值。"))
    assert "\\frac{3}{4}" in body["question_text"]
    assert "\\frac{2}{7}" in body["question_text"]


def test_fraction_question_text_uses_textbook_mul_div_symbols():
    helper = FractionFunctionHelper()
    body = helper.generate_from_config(helper.build_config("計算 $(-1/3)*(3/5+1.5)/(-2 1/5)$ 的值。"))
    assert "\\times" in body["question_text"]
    assert "\\div" in body["question_text"]
    assert "\\frac{1}{3}" in body["question_text"]
    assert "\\frac{3}{5}" in body["question_text"]
    assert "\\frac{1}{5}" in body["question_text"]


def test_fraction_question_text_keeps_fraction_not_division_for_negative_denominator():
    helper = FractionFunctionHelper()
    body = helper.generate_from_config(helper.build_config("判斷下列各分數是否為最簡分數，如果不是，請化成最簡分數。⑶ $16/-81$"))
    assert "\\frac{16}{81}" in body["question_text"]
    assert "\\div" not in body["question_text"]


def test_fraction_question_text_wraps_bare_latex_mixed_expression():
    helper = FractionFunctionHelper()
    config = helper.build_config(r"3\frac{9}{11}\times(-57)-1\frac{9}{11}\times(-57)")
    body = helper.generate_from_config(config)
    assert config["family"] == "frac_eval_common_factor"
    assert "$" in body["question_text"]
    assert r"3\frac{9}{11}\times" in body["question_text"]


def test_fraction_common_factor_detection_supports_left_shared_factor():
    helper = FractionFunctionHelper()
    config = helper.build_config(r"9\frac{1}{5}\times239+9\frac{1}{5}\times(-39)")
    assert config["family"] == "frac_eval_common_factor"
    assert config["common_factor_pattern"]["shared_side"] == "left"
    body = helper.generate_from_config(config)
    assert "$" in body["question_text"]
    assert r"9\frac{1}{5}\times" in body["question_text"]
