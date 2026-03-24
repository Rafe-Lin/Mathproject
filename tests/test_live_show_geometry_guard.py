from core.routes.live_show import _apply_skill_safety_guard


def test_geometry_word_problem_is_guarded_back_to_polynomial():
    ocr_text = (
        "\u53f3\u5716\u662f\u5927\u8c61\u9020\u578b\u7684\u68af\u5f62\u6ebc\u6ed1\u68af\uff0c"
        "\u82e5\u6ebc\u6ed1\u68af\u7684\u4e0a\u5e95\u70bax-3\u3001\u4e0b\u5e95\u70ba3x+5\u3001"
        "\u9762\u7a4d\u70ba2x^{2}+5x+2\uff0c\u8a66\u4ee5x\u7684\u591a\u9805\u5f0f\u8868\u793a"
        "\u6b64\u6ebc\u6ed1\u68af\u7684\u9ad8\u3002"
    )
    available = [
        "jh_\u6578\u5b781\u4e0a_FourArithmeticOperationsOfIntegers",
        "jh_\u6578\u5b782\u4e0a_FourArithmeticOperationsOfPolynomial",
        "jh_\u6578\u5b782\u4e0a_FourOperationsOfRadicals",
    ]

    corrected, reason = _apply_skill_safety_guard(
        "jh_\u6578\u5b782\u4e0a_FourOperationsOfRadicals",
        ocr_text,
        available,
    )

    assert "FourArithmeticOperationsOfPolynomial" in corrected
    assert reason == "polynomial_geometry_without_radical_symbol"
