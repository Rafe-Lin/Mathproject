import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.routes.live_show_pipeline import apply_radical_pattern_p1_guard


def _base_code(with_pid: bool = True) -> str:
    body = [
        "def generate(level=1):",
        "    term_count = 2",
    ]
    if with_pid:
        body.append('    pattern_id = "p1_add_sub"')
    body.extend(
        [
            '    question_text = "化簡 $\\sqrt{2}$。"',
            '    return {"question_text": question_text, "correct_answer": "0"}',
        ]
    )
    return "\n".join(body) + "\n"


def test_force_single_radical_to_p0():
    code = _base_code(with_pid=True)
    pid, hc, hx, trace = apply_radical_pattern_p1_guard(
        skill_id="jh_數學2上_FourOperationsOfRadicals",
        ocr_text=r"\sqrt{18}",
        raw_pattern_id="p1_add_sub",
        healed_code=code,
        healed_exec_code=code,
    )
    assert pid == "p0_simplify"
    assert 'pattern_id = "p0_simplify"' in hc
    assert 'pattern_id = "p0_simplify"' in hx
    assert trace.get("reject_reason") == "single_radical_requires_p0"


def test_force_exemplar_to_p5b():
    code = _base_code(with_pid=True)
    pid, hc, hx, trace = apply_radical_pattern_p1_guard(
        skill_id="jh_數學2上_FourOperationsOfRadicals",
        ocr_text=r"\frac{\sqrt{2}}{3\sqrt{2}+4}",
        raw_pattern_id="p2h_frac_mult_rad",
        healed_code=code,
        healed_exec_code=code,
    )
    assert pid == "p5b_conjugate_rad"
    assert 'pattern_id = "p5b_conjugate_rad"' in hc
    assert 'pattern_id = "p5b_conjugate_rad"' in hx
    assert trace.get("reject_reason") == "ocr_exemplar:p5b"


def test_inject_pattern_id_when_missing():
    code = _base_code(with_pid=False)
    pid, hc, hx, _ = apply_radical_pattern_p1_guard(
        skill_id="jh_數學2上_FourOperationsOfRadicals",
        ocr_text=r"\sqrt{6}",
        raw_pattern_id="",
        healed_code=code,
        healed_exec_code=code,
    )
    assert pid == "p0_simplify"
    assert 'pattern_id = "p0_simplify"' in hc
    assert 'pattern_id = "p0_simplify"' in hx
