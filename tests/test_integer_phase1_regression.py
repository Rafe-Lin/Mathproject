import re

import pytest

from core.integer_domain_functions import IntegerFunctionHelper
from tests.integer_phase1_cases import PHASE1_CASES


@pytest.mark.parametrize("question", PHASE1_CASES)
def test_integer_phase1_case_can_generate(question):
    helper = IntegerFunctionHelper()
    assert helper.can_handle(question), question
    config = helper.build_config(question)
    out = helper.generate_from_config(config)
    assert out["question_text"], question
    assert out["correct_answer"], question
    assert out["answer"] == out["correct_answer"], question


def test_integer_phase1_recursive_regression():
    helper = IntegerFunctionHelper()
    for question in PHASE1_CASES:
        config = helper.build_config(question)
        for _ in range(20):
            out = helper.generate_from_config(config)
            assert out["question_text"], question
            assert out["correct_answer"], question
            assert out["answer"] == out["correct_answer"], question


def test_integer_phase1_generator_code_executes():
    helper = IntegerFunctionHelper()
    question = "計算下列各式的值。\n⑴ $13+(-4)$\n⑵ $(-15)+9$"
    code = helper.build_generator_code(question)
    ns = {}
    exec(code, ns)
    out = ns["generate"]()
    assert out["question_text"]
    assert out["correct_answer"]


def test_integer_phase1_handles_bare_expression_input():
    helper = IntegerFunctionHelper()
    question = "13+(-13)"
    assert helper.can_handle(question)
    config = helper.build_config(question)
    out = helper.generate_from_config(config)
    assert out["question_text"].startswith("計算 $")
    assert out["correct_answer"]


@pytest.mark.parametrize(
    "question",
    [
        "13+(-13)",
        "(-9)-(-4)",
        "|-25|-18",
        "(-4)\\times(-8)",
        "(-4)times(-8)",
        "5*12-30/(-5)",
        "(-20+(-10))/(-5)*3",
    ],
)
def test_integer_phase1_handles_multiple_bare_expression_shapes(question):
    helper = IntegerFunctionHelper()
    assert helper.can_handle(question), question
    out = helper.generate_from_config(helper.build_config(question))
    assert out["question_text"].startswith("計算 $"), question
    assert out["correct_answer"], question


def test_integer_phase1_preserves_operator_between_absolute_values_and_tail_number():
    helper = IntegerFunctionHelper()
    question = "|-25|-|-75|-18"
    out = helper.generate_from_config(helper.build_config(question))
    rendered = out["question_text"]
    assert "|-" in rendered
    assert "||" not in rendered
    assert ")(" not in rendered
    assert re.search(r"\|[^|]+\|-\|[^|]+\|-\d", rendered)


def test_integer_phase1_renders_nested_absolute_value_as_bars():
    helper = IntegerFunctionHelper()
    question = "30+|(-64)+14|-25"
    out = helper.generate_from_config(helper.build_config(question))
    rendered = out["question_text"]
    assert "abs(" not in rendered
    assert re.search(r"\$\d+\+\|\(-\d+\)\+\d+\|-\d+\$", rendered)


def test_integer_phase1_handles_bare_times_operator_variants():
    helper = IntegerFunctionHelper()
    for question in ["(-4)\\times(-8)", "(-4)times(-8)", "(-4)*(-8)"]:
        assert helper.can_handle(question), question
        out = helper.generate_from_config(helper.build_config(question))
        rendered = out["question_text"]
        assert "\\times" in rendered
        assert out["correct_answer"]


def test_integer_phase1_handles_left_right_absolute_value_expression():
    helper = IntegerFunctionHelper()
    question = r"(-8)\times6+\left|(-5)\times10-1\right|"
    assert helper.can_handle(question)
    out = helper.generate_from_config(helper.build_config(question))
    rendered = out["question_text"]
    assert "\\times" in rendered
    assert "|" in rendered
    assert "abs(" not in rendered
    assert "*" not in rendered
    assert out["correct_answer"]


@pytest.mark.parametrize(
    ("question", "expected_token"),
    [
        (r"(-273)\times999", "999"),
        (r"1002\times(-175)", "1002"),
        (r"198\times(-18)", "198"),
        (r"(-55)\times401", "401"),
        (r"304\times(-125)", "125"),
        (r"(-260)\times499", "499"),
    ],
)
def test_integer_phase1_preserves_special_mental_multiplier_family(question, expected_token):
    helper = IntegerFunctionHelper()
    config = helper.build_config(question)
    assert config["family"] == "int_special_multiplier"
    out = helper.generate_from_config(config)
    rendered = out["question_text"]
    assert expected_token in rendered
    assert "\\times" in rendered
    assert out["correct_answer"]
