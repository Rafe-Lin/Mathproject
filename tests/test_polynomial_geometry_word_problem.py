from core.polynomial_domain_functions import PolynomialFunctionHelper


def test_trapezoid_word_problem_generates_nonempty_answer():
    helper = PolynomialFunctionHelper()
    question = (
        "\u53f3\u5716\u662f\u5927\u8c61\u9020\u578b\u7684\u68af\u5f62\u6ebc\u6ed1\u68af\uff0c"
        "\u82e5\u6ebc\u6ed1\u68af\u7684\u4e0a\u5e95\u70bax-3\u3001\u4e0b\u5e95\u70ba3x+5\u3001"
        "\u9762\u7a4d\u70ba2x^{2}+5x+2\uff0c\u8a66\u4ee5x\u7684\u591a\u9805\u5f0f\u8868\u793a"
        "\u6b64\u6ebc\u6ed1\u68af\u7684\u9ad8\u3002"
    )

    assert helper.detect_family(question) == "poly_geom_formula_direct"

    config = helper.build_config(question)
    assert config["family"] == "poly_geom_formula_direct"

    out = helper.generate_from_config(config)
    assert out["correct_answer"]
    assert out["answer"] == out["correct_answer"]

