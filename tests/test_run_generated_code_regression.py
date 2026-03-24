import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app


CASES = [
    (r"12\div(-4)\times(-3)", "integer"),
    (r"\frac{1}{2}+\frac{3}{4}", "number"),
    (r"x^2+3x+2", "polynomial"),
    (r"\frac{2}{\sqrt{10}}", "radical"),
]


@pytest.fixture(scope="module")
def client():
    app = create_app()
    app.config.update(TESTING=True)
    with app.test_client() as c:
        yield c


@pytest.mark.parametrize(("expr", "family"), CASES)
def test_run_generated_code_no_runtime_failure(client, expr: str, family: str):
    classify_resp = client.post("/api/classify", json={"text_data": expr})
    assert classify_resp.status_code == 200
    classify_data = classify_resp.get_json() or {}
    assert classify_data.get("success") is True

    generate_payload = {
        "input_text": classify_data.get("ocr_text"),
        "prompt": classify_data.get("ocr_text"),
        "ablation_mode": False,
        "model_id": "qwen3-vl-8b",
        "model": "qwen3-vl-8b",
        "skill_id": classify_data.get("skill_id"),
        "json_spec": classify_data.get("json_spec"),
    }
    generate_resp = client.post("/api/generate_live", json=generate_payload)
    assert generate_resp.status_code == 200
    generate_data = generate_resp.get_json() or {}
    assert generate_data.get("file_path")

    rerun_resp = client.post(
        "/api/run_generated_code",
        json={
            "file_path": generate_data.get("file_path"),
            "skill_id": classify_data.get("skill_id"),
            "fraction_display_mode": "auto",
            "ocr_text": classify_data.get("ocr_text"),
            "json_spec": classify_data.get("json_spec"),
            "level": 1,
        },
    )
    assert rerun_resp.status_code == 200
    rerun_data = rerun_resp.get_json() or {}

    assert rerun_data.get("success") is True, (family, expr, rerun_data)
    assert not rerun_data.get("error"), (family, expr, rerun_data)
    assert (rerun_data.get("problem") or "").strip() not in {"", "Error"}, (
        family,
        expr,
        rerun_data,
    )


def test_radical_ab2_ab3_rerun_keeps_same_problem_family(client):
    expr = r"\frac{2}{\sqrt{10}}"

    classify_resp = client.post("/api/classify", json={"text_data": expr})
    assert classify_resp.status_code == 200
    classify_data = classify_resp.get_json() or {}
    assert classify_data.get("success") is True

    generate_payload = {
        "input_text": classify_data.get("ocr_text"),
        "prompt": classify_data.get("ocr_text"),
        "ablation_mode": False,
        "model_id": "qwen3-vl-8b",
        "model": "qwen3-vl-8b",
        "skill_id": classify_data.get("skill_id"),
        "json_spec": classify_data.get("json_spec"),
    }
    generate_resp = client.post("/api/generate_live", json=generate_payload)
    assert generate_resp.status_code == 200
    generate_data = generate_resp.get_json() or {}

    ab3_problem = (generate_data.get("problem") or "").strip()
    ab2_problem = ((generate_data.get("ab2_result") or {}).get("problem") or "").strip()
    assert ab3_problem
    assert ab2_problem

    rerun_ab3 = client.post(
        "/api/run_generated_code",
        json={
            "file_path": generate_data.get("file_path"),
            "skill_id": classify_data.get("skill_id"),
            "fraction_display_mode": "auto",
            "ocr_text": classify_data.get("ocr_text"),
            "json_spec": classify_data.get("json_spec"),
            "level": 1,
        },
    )
    assert rerun_ab3.status_code == 200
    rerun_ab3_data = rerun_ab3.get_json() or {}
    assert rerun_ab3_data.get("success") is True
    assert (rerun_ab3_data.get("problem") or "").strip() == ab3_problem

    rerun_ab2 = client.post(
        "/api/run_generated_code",
        json={
            "file_path": (generate_data.get("ab2_result") or {}).get("file_path"),
            "skill_id": classify_data.get("skill_id"),
            "fraction_display_mode": "auto",
            "ocr_text": classify_data.get("ocr_text"),
            "json_spec": classify_data.get("json_spec"),
            "level": 1,
        },
    )
    assert rerun_ab2.status_code == 200
    rerun_ab2_data = rerun_ab2.get_json() or {}
    assert rerun_ab2_data.get("success") is True
    assert (rerun_ab2_data.get("problem") or "").strip() == ab2_problem


def test_radical_mixed_fraction_root_add_hits_p7_family(client):
    expr = r"\sqrt{1\frac{9}{16}}+\sqrt{4\frac{25}{36}}"

    classify_resp = client.post("/api/classify", json={"text_data": expr})
    assert classify_resp.status_code == 200
    classify_data = classify_resp.get_json() or {}
    assert classify_data.get("success") is True

    generate_payload = {
        "input_text": classify_data.get("ocr_text"),
        "prompt": classify_data.get("ocr_text"),
        "ablation_mode": False,
        "model_id": "qwen3-vl-8b",
        "model": "qwen3-vl-8b",
        "skill_id": classify_data.get("skill_id"),
        "json_spec": classify_data.get("json_spec"),
    }
    generate_resp = client.post("/api/generate_live", json=generate_payload)
    assert generate_resp.status_code == 200
    generate_data = generate_resp.get_json() or {}

    ab3_problem = (generate_data.get("problem") or "").strip()
    ab2_problem = ((generate_data.get("ab2_result") or {}).get("problem") or "").strip()

    assert ab3_problem.startswith("計算 $\\sqrt{"), generate_data
    assert "\\sqrt{" in ab3_problem, generate_data
    assert "\\frac{" in ab3_problem, generate_data
    assert "+" in ab3_problem or " - " in ab3_problem, generate_data

    assert ab2_problem.startswith("計算 $\\sqrt{"), generate_data
    assert "\\sqrt{" in ab2_problem, generate_data
    assert "\\frac{" in ab2_problem, generate_data
