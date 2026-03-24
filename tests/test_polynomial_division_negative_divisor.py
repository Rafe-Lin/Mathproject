# -*- coding: utf-8 -*-

from core.polynomial_domain_functions import PolynomialFunctionHelper


def test_division_question_wraps_negative_divisor_for_teaching_display():
    helper = PolynomialFunctionHelper()
    code = helper.build_generator_code("(14x^{2})\\div(-4x^{2})")
    ns = {}
    exec(code, ns)
    for _ in range(5):
        question = ns["generate"]()["question_text"]
        assert "\\div ((-" in question or "\\div (-" in question
