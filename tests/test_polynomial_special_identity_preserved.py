# -*- coding: utf-8 -*-

import re

from core.polynomial_domain_functions import PolynomialFunctionHelper


def test_conjugate_product_stays_special_identity():
    helper = PolynomialFunctionHelper()
    code = helper.build_generator_code("(4x+7)(4x-7)")
    ns = {}
    exec(code, ns)
    for _ in range(5):
        question = ns["generate"]()["question_text"]
        assert re.search(r"\(((?:\d+)?x)\+\d+\)\(\1-\d+\)", question), question


def test_binomial_square_stays_square_pattern():
    helper = PolynomialFunctionHelper()
    code = helper.build_generator_code("利用乘法公式計算 $(3x+4)^{2}$。")
    ns = {}
    exec(code, ns)
    for _ in range(5):
        question = ns["generate"]()["question_text"]
        assert "利用乘法公式計算" in question
        assert re.search(r"\(((?:\d+)?x)\+\d+\)\^\{2\}", question), question
