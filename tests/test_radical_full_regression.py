import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app
from core.code_utils.live_show_math_utils import build_radical_complexity_mirror_profile
from core.routes.live_show_pipeline import evaluate_radical_quality_gate
from tests.comprehensive_stress_test import collect_pure_math_cases


SPECIAL_FAMILY_CHECKS = {
    r"\frac{1}{\sqrt{3}}\div\frac{\sqrt{6}}{\sqrt{2}}": lambda s: (r"\div" in s and s.count(r"\frac") >= 2),
    r"\sqrt{\frac{1}{2}}\times\sqrt{\frac{1}{5}}\div\sqrt{\frac{1}{6}}": lambda s: (
        s.count(r"\sqrt{\frac") == 3 and r"\times" in s and r"\div" in s
    ),
    r"(\sqrt{3}+2\sqrt{2}\quad)^2": lambda s: _normalized(s).endswith(")^2"),
    r"\frac{1}{\sqrt{3}-\sqrt{2}}": lambda s: (
        r"\frac{1}{" in s and s.count(r"\sqrt") >= 2 and ("+" in s or "-" in s)
    ),
    r"\frac{\sqrt{2}}{3\sqrt{2}+4}": lambda s: (
        r"\frac{\sqrt{" in s and s.count(r"\sqrt") >= 2 and ("+" in s or "-" in s)
    ),
}


@pytest.fixture(scope="module")
def client():
    app = create_app()
    app.config.update(TESTING=True)
    with app.test_client() as c:
        yield c


def _generate_for_expr(client, expr: str) -> dict:
    classify_resp = client.post("/api/classify", json={"text_data": expr})
    assert classify_resp.status_code == 200, f"classify failed for {expr!r}"
    classify_data = classify_resp.get_json() or {}
    assert classify_data.get("success") is True, f"classify success=false for {expr!r}"

    payload = {
        "input_text": classify_data.get("ocr_text"),
        "prompt": classify_data.get("ocr_text"),
        "ablation_mode": False,
        "model_id": "qwen3-vl-8b",
        "model": "qwen3-vl-8b",
        "skill_id": classify_data.get("skill_id"),
        "json_spec": classify_data.get("json_spec"),
    }
    generate_resp = client.post("/api/generate_live", json=payload)
    assert generate_resp.status_code == 200, f"generate failed for {expr!r}"
    return generate_resp.get_json() or {}


def _extract_expr(problem_text: str) -> str:
    m = re.search(r"\$(.*?)\$", str(problem_text or ""))
    return (m.group(1) if m else str(problem_text or "")).strip()


def _normalized(expr: str) -> str:
    return re.sub(r"\s+", "", str(expr or ""))


def test_full_radical_regression_suite(client):
    failures = []

    for _, _, expr, _ in collect_pure_math_cases():
        data = _generate_for_expr(client, expr)
        problem = (data.get("problem") or "").strip()
        ab2 = data.get("ab2_result") or {}
        ab2_problem = (ab2.get("question_text") or ab2.get("problem") or "").strip()

        if not problem or "$" not in problem:
            failures.append(f"{expr}: missing final problem text -> {problem!r}")
            continue
        if not ab2_problem or "$" not in ab2_problem:
            failures.append(f"{expr}: missing ab2 problem text -> {ab2_problem!r}")
            continue

        final_expr = _extract_expr(problem)
        ab2_expr = _extract_expr(ab2_problem)

        final_qg = evaluate_radical_quality_gate(
            source_ocr_expr=expr,
            question_text=problem,
            generated_expr=final_expr,
        )
        if final_qg.get("reasons"):
            failures.append(f"{expr}: final quality gate -> {final_qg['reasons']}")

        ab2_qg = evaluate_radical_quality_gate(
            source_ocr_expr=expr,
            question_text=ab2_problem,
            generated_expr=ab2_expr,
        )
        if ab2_qg.get("reasons"):
            failures.append(f"{expr}: ab2 quality gate -> {ab2_qg['reasons']}")

        src_profile = build_radical_complexity_mirror_profile(expr)
        out_profile = build_radical_complexity_mirror_profile(problem)
        for key in ("number_count", "operator_sequence", "rad_count", "simplifiable_count"):
            if src_profile.get(key) != out_profile.get(key):
                failures.append(
                    f"{expr}: profile mismatch on {key}: "
                    f"src={src_profile.get(key)!r} out={out_profile.get(key)!r}"
                )

        family_check = SPECIAL_FAMILY_CHECKS.get(expr)
        if family_check and not family_check(final_expr):
            failures.append(f"{expr}: special family drift -> {final_expr!r}")

    assert not failures, "\n".join(failures)
