# -*- coding: utf-8 -*-

from core.prompts.domain_function_library import POLYNOMIALOPS_HELPERS


def _load_polynomial_ops():
    ns = {}
    exec(POLYNOMIALOPS_HELPERS, ns)
    return ns["PolynomialOps"]


def test_polynomialops_supports_x_and_x2_helpers():
    ops = _load_polynomial_ops()
    assert ops.x() == [1, 0]
    assert ops.x2() == [1, 0, 0]


def test_polynomialops_accepts_scalar_operands():
    ops = _load_polynomial_ops()
    expr = ops.sub(
        ops.add(ops.mul(3, ops.x2()), ops.add(5, ops.mul(2, ops.x()))),
        ops.sub(1, ops.mul(4, ops.x2()))
    )
    assert ops.format_plain(expr) == "7x^2+2x+4"
