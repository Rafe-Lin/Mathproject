import re
from fractions import Fraction
from core.polynomial_domain_functions import PolynomialFunctionHelper

_POLY_HELPER = PolynomialFunctionHelper()
_POLY_CONFIG = {'family': 'poly_add_sub_flat', 'source_text': 'x^{2}+3x+2', 'variable': 'x', 'ast': {'kind': 'binop', 'op': '+', 'left': {'kind': 'binop', 'op': '+', 'left': {'kind': 'poly', 'terms': [{'sign': 1, 'magnitude': Fraction(1, 1), 'fractional': False, 'exponent': 2}]}, 'right': {'kind': 'poly', 'terms': [{'sign': 1, 'magnitude': Fraction(3, 1), 'fractional': False, 'exponent': 1}]}}, 'right': {'kind': 'poly', 'terms': [{'sign': 1, 'magnitude': Fraction(2, 1), 'fractional': False, 'exponent': 0}]}}}

def generate(level=1, **kwargs):
    return _POLY_HELPER.generate_from_config(_POLY_CONFIG)

def check(user_answer, correct_answer):
    def _norm(text):
        s = str(text or "").strip().replace(" ", "")
        s = s.replace("（", "(").replace("）", ")")
        s = s.replace("＋", "+").replace("－", "-").replace("−", "-")
        return s
    u = _norm(user_answer)
    c = _norm(correct_answer)
    return {"correct": u == c, "result": "正確" if u == c else "錯誤"}
