from core.adaptive.judge import judge_answer


def test_tolerant_parser_accepts_equivalent_forms():
    correct = "3x + 1 + 5/(3x)"
    assert judge_answer("3x+1+5/(3x)", correct) is True
    assert judge_answer("1+3x+5/(3x)", correct) is True
    assert judge_answer("3*x+1+5/(3*x)", correct) is True
    assert judge_answer("3x+1+(5/3x)", correct) is True


def test_tolerant_parser_does_not_over_accept_non_equivalent_forms():
    correct = "3x + 1 + 5/(3x)"
    assert judge_answer("3x+1+5/3*x", correct) is False
    assert judge_answer("3x+1+5/(3)+x", correct) is False
    assert judge_answer("3x+1+5/3+x", correct) is False

