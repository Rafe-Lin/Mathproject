# -*- coding: utf-8 -*-

from core.polynomial_domain_functions import PolynomialFunctionHelper


def test_reverse_division_word_problem_uses_deterministic_path():
    helper = PolynomialFunctionHelper()
    question = "如果一個多項式A除以x+2的商式為3x^{2}+1，餘式為4，試求此多項式A。"
    assert helper.detect_family(question) == "poly_div_reverse"
    config = helper.build_config(question)
    assert config["reverse_kind"] == "find_dividend"
    code = helper.build_generator_code(question)
    ns = {}
    exec(code, ns)
    out = ns["generate"]()
    assert "商式為" in out["question_text"]
    assert out["correct_answer"]
