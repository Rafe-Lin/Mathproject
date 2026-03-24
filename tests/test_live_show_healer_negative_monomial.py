# -*- coding: utf-8 -*-

from core.healers.live_show_healer import (
    enforce_negative_parentheses,
    sanitize_question_text_display,
)


def test_wraps_negative_monomial_with_exponent():
    fixed, count = enforce_negative_parentheses("(8x-3x^{3}+3)+[-8x^{3}+6x^{2}]")
    assert fixed == "(8x-3x^{3}+3)+[(-8x^{3})+6x^{2}]"
    assert count == 1


def test_preserves_already_wrapped_negative_fractional_monomial():
    fixed, count = enforce_negative_parentheses(r"\frac{1}{2}x+(-\frac{4}{5}x^{2})")
    assert fixed == r"\frac{1}{2}x+(-\frac{4}{5}x^{2})"
    assert count == 0


def test_normalizes_negative_integer_inside_absolute_value():
    fixed = sanitize_question_text_display("計算 $|(-9)|-|(-47)|(-20)$ 的值。")
    assert fixed == "計算 $|-9|-|-47|-20$ 的值。"


def test_preserves_minus_between_absolute_value_and_tail_integer():
    fixed = sanitize_question_text_display("計算 $|(-5)|-|(-67)|(-18)$ 的值。")
    assert fixed == "計算 $|-5|-|-67|-18$ 的值。"
