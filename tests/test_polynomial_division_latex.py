# -*- coding: utf-8 -*-

from fractions import Fraction

from core.polynomial_domain_functions import PolynomialFunctionHelper


def test_division_question_wraps_divisor_to_avoid_divx_latex():
    helper = PolynomialFunctionHelper()
    code = helper.build_generator_code("(15x^{2})\\div(3x)")
    ns = {}
    exec(code, ns)
    for _ in range(5):
        question = ns["generate"]()["question_text"]
        assert "\\divx" not in question
        assert "\\div (" in question


def test_fractional_monomial_division_answer_keeps_variable_visible():
    helper = PolynomialFunctionHelper()
    assert helper.poly_plain({1: Fraction(3, 4)}, "x") == "(3/4)x"
    assert helper.poly_plain({1: Fraction(1, 4)}, "x") == "(1/4)x"
