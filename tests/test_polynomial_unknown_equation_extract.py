# -*- coding: utf-8 -*-

from core.polynomial_domain_functions import PolynomialFunctionHelper


def test_extract_equation_from_unknown_polynomial_word_problem():
    helper = PolynomialFunctionHelper()
    lhs, rhs = helper.extract_equation(helper.normalize_text("若A是多項式，且A+(-4x^{2}+1+5x)=x^{3}+5-2x，則多項式A=？"))
    assert lhs == "A+(-4x^2+1+5x)"
    assert rhs == "x^3+5-2x"


def test_unknown_polynomial_can_use_deterministic_helper():
    helper = PolynomialFunctionHelper()
    question = "若A是多項式，且A+(-4x^{2}+1+5x)=x^{3}+5-2x，則多項式A=？"
    config = helper.build_config(question)
    assert config["family"] == "poly_add_sub_unknown"
    code = helper.build_generator_code(question)
    ns = {}
    exec(code, ns)
    out = ns["generate"]()
    assert "多項式" in out["question_text"]
    assert out["correct_answer"]
