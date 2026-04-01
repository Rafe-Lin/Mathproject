from core.adaptive.judge import judge_answer, judge_answer_with_feedback


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


def test_qr_parser_accepts_f8_f9_equivalent_formats():
    correct_forms = [
        "商：-3x-2，餘：-1",
        "商:-3x-2,餘:-1",
        "商式：-3x-2；餘式：-1",
    ]
    user_forms = [
        "-3x-2...-1",
        "商:-3x-2,餘:-1",
        "(-3x-2,-1)",
    ]

    for correct in correct_forms:
        for user in user_forms:
            result = judge_answer_with_feedback(user, correct)
            assert result["is_correct"] is True


def test_qr_parser_missing_format_returns_feedback():
    result = judge_answer_with_feedback("x+1", "商：x，餘：1")
    assert result["is_correct"] is False
    assert "商與餘數" in result.get("feedback", "")

