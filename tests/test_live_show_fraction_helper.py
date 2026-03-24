from __future__ import annotations

import math
import os
import re
import sys


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app import app
from core.routes.live_show import deterministic_classify_skill_id


FRACTION_SKILL = "jh_數學1上_FourArithmeticOperationsOfNumbers"
POLY_SKILL = "jh_數學2上_FourArithmeticOperationsOfPolynomial"


def test_generate_live_uses_fraction_helper_for_textbook_fraction_case():
    client = app.test_client()
    prompt = "計算下列各式的值。⑴ $(-7/5)+(-9/5)$"
    response = client.post(
        "/api/generate_live",
        json={
            "prompt": prompt,
            "input_text": prompt,
            "skill_id": FRACTION_SKILL,
            "ablation_mode": False,
            "count": 1,
            "json_spec": {"ocr_text": prompt},
        },
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert body["architect_model"] == "FractionFunctionHelper"
    assert body["correct_answer"] == "-16/5"


def test_generate_live_keeps_bare_latex_mixed_fraction_on_fraction_path():
    client = app.test_client()
    prompt = r"9\frac{1}{5}\times239+9\frac{1}{5}\times(-39)"
    response = client.post(
        "/api/generate_live",
        json={
            "prompt": prompt,
            "input_text": prompt,
            "skill_id": FRACTION_SKILL,
            "ablation_mode": False,
            "count": 1,
            "json_spec": {"ocr_text": prompt},
        },
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert body["architect_model"] == "FractionFunctionHelper"
    assert "$" in body["question_text"]
    assert r"9\frac{1}{5}\times" in body["question_text"]
    assert body["correct_answer"] == "1840"


def test_deterministic_classify_prefers_fraction_for_frac_latex_input():
    skill_id, reason = deterministic_classify_skill_id(
        r"9\frac{1}{5}\times239+9\frac{1}{5}\times(-39)",
        [FRACTION_SKILL, POLY_SKILL],
    )
    assert skill_id == FRACTION_SKILL
    assert reason == "rule:fraction_marker"


def test_deterministic_classify_prefers_fraction_for_repeated_mixed_fraction_expression():
    skill_id, reason = deterministic_classify_skill_id(
        r"3\frac{9}{11}\times(-57)-1\frac{9}{11}\times(-57)",
        [FRACTION_SKILL, POLY_SKILL],
    )
    assert skill_id == FRACTION_SKILL
    assert reason == "rule:fraction_marker"


def test_classify_route_prefers_fraction_even_with_image_payload_when_text_is_strong():
    client = app.test_client()
    expr = r"3\frac{9}{11}\times(-57)-1\frac{9}{11}\times(-57)"
    response = client.post(
        "/api/classify",
        json={
            "text_data": expr,
            "image_data": "data:image/png;base64,ZmFrZQ==",
        },
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert body["skill_id"] == FRACTION_SKILL


def test_classify_route_image_payload_overrides_polynomial_vl_result_for_fraction_common_factor():
    client = app.test_client()
    expr = r"3\frac{9}{11}\times(-57)-1\frac{9}{11}\times(-57)"
    response = client.post(
        "/api/classify",
        json={
            "text_data": expr,
            "image_data": "data:image/png;base64,ZmFrZQ==",
        },
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert body["skill_id"] == FRACTION_SKILL
    assert body["classify_source"] in {"deterministic", "deterministic_override"}


def test_run_generated_code_returns_fraction_variant_with_parenthesized_negative_divisor():
    client = app.test_client()
    prompt = r"(-\frac{1}{3})\times(\frac{3}{5}+1.5)\div(-\frac{21}{5})"
    generated = client.post(
        "/api/generate_live",
        json={
            "prompt": prompt,
            "input_text": prompt,
            "skill_id": FRACTION_SKILL,
            "ablation_mode": False,
            "count": 1,
            "json_spec": {"ocr_text": prompt},
        },
    ).get_json()

    response = client.post(
        "/api/run_generated_code",
        json={
            "file_path": generated["file_path"],
            "skill_id": FRACTION_SKILL,
            "ocr_text": prompt,
            "json_spec": {"ocr_text": prompt},
        },
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert "\\div(-" in body["problem"] or "\\div (-" in body["problem"]
    assert body["problem"] != generated["question_text"]


def test_fraction_next_problem_has_real_variation_across_multiple_runs():
    client = app.test_client()
    prompt = r"(-\frac{1}{3})\times(\frac{3}{5}+1.5)\div(-\frac{21}{5})"
    generated = client.post(
        "/api/generate_live",
        json={
            "prompt": prompt,
            "input_text": prompt,
            "skill_id": FRACTION_SKILL,
            "ablation_mode": False,
            "count": 1,
            "json_spec": {"ocr_text": prompt},
        },
    ).get_json()

    seen = set()
    for _ in range(8):
        body = client.post(
            "/api/run_generated_code",
            json={
                "file_path": generated["file_path"],
                "skill_id": FRACTION_SKILL,
                "ocr_text": prompt,
                "json_spec": {"ocr_text": prompt},
            },
        ).get_json()
        seen.add(body["problem"])

    assert len(seen) >= 3
    assert any(r"(-\frac{2}{3})" not in item for item in seen)


def test_fraction_next_problem_prefers_reduced_textbook_fractions():
    client = app.test_client()
    prompt = r"(-\frac{1}{3})\times(\frac{3}{5}+1.5)\div(-\frac{21}{5})"
    generated = client.post(
        "/api/generate_live",
        json={
            "prompt": prompt,
            "input_text": prompt,
            "skill_id": FRACTION_SKILL,
            "ablation_mode": False,
            "count": 1,
            "json_spec": {"ocr_text": prompt},
        },
    ).get_json()

    fraction_pattern = re.compile(r"\\frac\{(\d+)\}\{(\d+)\}")
    seen = set()
    for _ in range(8):
        body = client.post(
            "/api/run_generated_code",
            json={
                "file_path": generated["file_path"],
                "skill_id": FRACTION_SKILL,
                "ocr_text": prompt,
                "json_spec": {"ocr_text": prompt},
            },
        ).get_json()
        problem = body["problem"]
        seen.add(problem)
        for num, den in fraction_pattern.findall(problem):
            assert math.gcd(int(num), int(den)) == 1

    assert all(r"\frac{2}{4}" not in item for item in seen)
    assert all(r"\frac{4}{6}" not in item for item in seen)


def test_fraction_next_problem_keeps_mixed_numbers_reduced():
    client = app.test_client()
    prompt = r"(-3\frac{3}{4})-(-1\frac{1}{6})+1\frac{5}{8}"
    generated = client.post(
        "/api/generate_live",
        json={
            "prompt": prompt,
            "input_text": prompt,
            "skill_id": FRACTION_SKILL,
            "ablation_mode": False,
            "count": 1,
            "json_spec": {"ocr_text": prompt},
        },
    ).get_json()

    mixed_pattern = re.compile(r"-?\d+\\frac\{(\d+)\}\{(\d+)\}")
    for _ in range(8):
        body = client.post(
            "/api/run_generated_code",
            json={
                "file_path": generated["file_path"],
                "skill_id": FRACTION_SKILL,
                "ocr_text": prompt,
                "json_spec": {"ocr_text": prompt},
            },
        ).get_json()
        for num, den in mixed_pattern.findall(body["problem"]):
            assert math.gcd(int(num), int(den)) == 1


def test_fraction_common_factor_expression_is_fully_wrapped_and_preserved():
    client = app.test_client()
    prompt = r"3\frac{9}{11}\times(-57)-1\frac{9}{11}\times(-57)"
    generated = client.post(
        "/api/generate_live",
        json={
            "prompt": prompt,
            "input_text": prompt,
            "skill_id": FRACTION_SKILL,
            "ablation_mode": False,
            "count": 1,
            "json_spec": {"ocr_text": prompt},
        },
    ).get_json()

    assert generated["architect_model"] == "FractionFunctionHelper"
    assert "$" in generated["question_text"]

    rerun = client.post(
        "/api/run_generated_code",
        json={
            "file_path": generated["file_path"],
            "skill_id": FRACTION_SKILL,
            "ocr_text": prompt,
            "json_spec": {"ocr_text": prompt},
        },
    ).get_json()

    problem = rerun["problem"]
    assert "$" in problem
    assert problem.count(r"\times") == 2
    factors = re.findall(r"\\times\s*(\(-?\d+\)|\d+)", problem)
    assert len(factors) == 2
    assert factors[0] == factors[1]


def test_fraction_common_factor_left_shared_factor_generates_new_problem():
    client = app.test_client()
    prompt = r"9\frac{1}{5}\times239+9\frac{1}{5}\times(-39)"
    generated = client.post(
        "/api/generate_live",
        json={
            "prompt": prompt,
            "input_text": prompt,
            "skill_id": FRACTION_SKILL,
            "ablation_mode": False,
            "count": 1,
            "json_spec": {"ocr_text": prompt},
        },
    ).get_json()

    assert generated["architect_model"] == "FractionFunctionHelper"
    assert "$" in generated["question_text"]
    assert r"\times" in generated["question_text"]

    rerun = client.post(
        "/api/run_generated_code",
        json={
            "file_path": generated["file_path"],
            "skill_id": FRACTION_SKILL,
            "ocr_text": prompt,
            "json_spec": {"ocr_text": prompt},
        },
    ).get_json()

    problem = rerun["problem"]
    assert problem
    assert problem != generated["question_text"]
    assert problem.count(r"\times") == 2
    problem_math = problem.replace("計算 ", "").replace(" 的值。", "").replace("$", "")
    parts = re.split(r"[+-]", problem_math, maxsplit=1)
    assert len(parts) == 2
    left_shared = parts[0].split(r"\times")[0].strip()
    right_shared = parts[1].split(r"\times")[0].strip()
    assert left_shared == right_shared


def test_fraction_common_factor_generation_stays_grade7_friendly():
    client = app.test_client()
    prompt = r"3\frac{9}{11}\times(-57)-1\frac{9}{11}\times(-57)"
    generated = client.post(
        "/api/generate_live",
        json={
            "prompt": prompt,
            "input_text": prompt,
            "skill_id": FRACTION_SKILL,
            "ablation_mode": False,
            "count": 1,
            "json_spec": {"ocr_text": prompt},
        },
    ).get_json()

    for _ in range(8):
        body = client.post(
            "/api/run_generated_code",
            json={
                "file_path": generated["file_path"],
                "skill_id": FRACTION_SKILL,
                "ocr_text": prompt,
                "json_spec": {"ocr_text": prompt},
            },
        ).get_json()
        answer = body["answer"]
        assert len(answer) <= 6
        if "/" in answer:
            num, den = answer.split("/", 1)
            assert abs(int(num)) <= 60
            assert int(den) <= 6
        else:
            assert abs(int(answer)) <= 120


def test_fraction_decimal_mix_generation_stays_grade7_friendly():
    client = app.test_client()
    prompt = r"\frac{3}{2}\div(-0.6)\times(-\frac{3}{5})-\frac{1}{2}"
    generated = client.post(
        "/api/generate_live",
        json={
            "prompt": prompt,
            "input_text": prompt,
            "skill_id": FRACTION_SKILL,
            "ablation_mode": False,
            "count": 1,
            "json_spec": {"ocr_text": prompt},
        },
    ).get_json()

    assert "$" in generated["question_text"]
    assert "\\div" in generated["question_text"]
    assert "\\times" in generated["question_text"]

    seen = set()
    for _ in range(8):
        body = client.post(
            "/api/run_generated_code",
            json={
                "file_path": generated["file_path"],
                "skill_id": FRACTION_SKILL,
                "ocr_text": prompt,
                "json_spec": {"ocr_text": prompt},
            },
        ).get_json()
        answer = body["answer"]
        seen.add(body["problem"])
        assert len(answer) <= 5
        if "/" in answer:
            num, den = answer.split("/", 1)
            assert abs(int(num)) <= 12
            assert int(den) <= 6
        else:
            assert abs(int(answer)) <= 6

    assert len(seen) >= 3


def test_fraction_grouped_decimal_mix_generation_stays_grade7_friendly():
    client = app.test_client()
    prompt = r"(-\frac{1}{3})\times(\frac{3}{5}+1.5)\div(-\frac{21}{5})"
    generated = client.post(
        "/api/generate_live",
        json={
            "prompt": prompt,
            "input_text": prompt,
            "skill_id": FRACTION_SKILL,
            "ablation_mode": False,
            "count": 1,
            "json_spec": {"ocr_text": prompt},
        },
    ).get_json()

    assert "$" in generated["question_text"]
    assert "\\div" in generated["question_text"]
    assert "\\times" in generated["question_text"]

    seen = set()
    for _ in range(8):
        body = client.post(
            "/api/run_generated_code",
            json={
                "file_path": generated["file_path"],
                "skill_id": FRACTION_SKILL,
                "ocr_text": prompt,
                "json_spec": {"ocr_text": prompt},
            },
        ).get_json()
        answer = body["answer"]
        seen.add(body["problem"])
        assert len(answer) <= 5
        if "/" in answer:
            num, den = answer.split("/", 1)
            assert abs(int(num)) <= 6
            assert int(den) <= 20
        else:
            assert abs(int(answer)) <= 4
        assert "\\div(-" in body["problem"] or "\\div (-" in body["problem"]

    assert len(seen) >= 3
