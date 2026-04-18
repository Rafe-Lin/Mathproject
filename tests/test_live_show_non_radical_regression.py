# -*- coding: utf-8 -*-
"""
非根式技能回歸：確保 FourOperationsOfRadicals 專用 mirror / style debug 不污染
jh_數學1上_FourArithmeticOperationsOfIntegers、jh_數學1上_FourArithmeticOperationsOfNumbers。
"""

from __future__ import annotations

import os
import sys

import pytest

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from core.code_utils.live_show_math_utils import (
    _build_radical_profile,
    _is_radical_isomorphic,
    _radical_profile_diff,
    build_radical_complexity_mirror_profile,
    radical_complexity_mirror_diff,
    radical_complexity_mirror_isomorphic,
)
from core.routes.live_show import _RADICAL_ONLY_DEBUG_META_KEYS
from core.routes.live_show_pipeline import assemble_visual_output

INTEGER_SKILL = "jh_數學1上_FourArithmeticOperationsOfIntegers"
NUMBER_SKILL = "jh_數學1上_FourArithmeticOperationsOfNumbers"

INTEGER_PROMPTS = [
    r"$1+2$",
    r"$10-3$",
    r"$4\times5$",
    r"$12\div3$",
    r"$(-2)+9$",
]
NUMBER_PROMPTS = [
    r"$\frac{1}{2}+\frac{1}{3}$",
    r"$\frac{3}{4}-\frac{1}{4}$",
    r"$\frac{2}{3}\times\frac{3}{5}$",
    r"$\frac{5}{6}\div\frac{1}{2}$",
    r"$\frac{1}{2}+2$",
]


def test_radical_mirror_public_api_matches_private_impl():
    s = r"$\sqrt{2}\times\sqrt{3}$"
    got = build_radical_complexity_mirror_profile(s)
    base = _build_radical_profile(s)
    for k, v in base.items():
        assert got.get(k) == v
    assert got.get("fraction_count") == 0
    assert isinstance(got.get("bracket_depth"), int)
    exp = _build_radical_profile(s)
    assert radical_complexity_mirror_isomorphic(exp, s) is _is_radical_isomorphic(exp, s)
    assert radical_complexity_mirror_diff(exp, s) == _radical_profile_diff(exp, s)


def test_assemble_visual_output_omits_radical_style_keys_when_disabled():
    out = assemble_visual_output(
        problems_result=[],
        ai_inference_time_sec=0.0,
        cpu_execution_time_sec=0.0,
        raw_out="",
        api_stubs="",
        healed_code="",
        file_path="",
        system_prompt="",
        json_spec={},
        regex_fixes=0,
        regex_code_fixes=0,
        regex_display_fixes=0,
        ast_fixes=0,
        o1_fixes=0,
        detail_logs=[],
        expected_fp={"number_count": 1},
        generated_fp={"number_count": 1},
        iso_isomorphic=True,
        fraction_display_mode="inline",
        ab2_result={},
        style_meta={
            "input_radical_style": "fraction_radical",
            "output_radical_style": "fraction_radical",
            "style_preserved": True,
        },
        include_radical_style_fields=False,
    )
    dm = out["debug_meta"]
    for k in (
        "input_radical_style",
        "output_radical_style",
        "style_preserved",
        "style_mismatch_reason",
    ):
        assert k not in dm


def test_live_api_integers_and_numbers_no_radical_debug_keys():
    """
    需啟動 app 並設定 MATHPROJECT_BASE_URL；未設定時略過。
    各至少 5 題，斷言 debug_meta 不含根式專用欄位。
    """
    base = os.environ.get("MATHPROJECT_BASE_URL", "").rstrip("/")
    if not base:
        pytest.skip("MATHPROJECT_BASE_URL not set — skip live API regression")

    import requests

    url = f"{base}/api/generate_live"
    timeout = int(os.environ.get("STRESS_GENERATE_TIMEOUT", "300"))

    def _one(ocr: str, skill_id: str) -> dict:
        try:
            r = requests.post(
                url,
                json={
                    "input_text": ocr,
                    "prompt": ocr,
                    "ablation_mode": False,
                    "model_id": "qwen3-vl-8b",
                    "model": "qwen3-vl-8b",
                    "skill_id": skill_id,
                    "json_spec": {"ocr_text": ocr},
                },
                timeout=timeout,
            )
        except requests.exceptions.RequestException as exc:
            pytest.skip(f"live API unreachable ({base}): {exc}")
        assert r.status_code == 200, r.text[:500]
        body = r.json()
        assert body.get("success") is not False, body.get("error", body)
        return body.get("debug_meta") or {}

    for expr in INTEGER_PROMPTS:
        dm = _one(expr, INTEGER_SKILL)
        for k in _RADICAL_ONLY_DEBUG_META_KEYS:
            assert k not in dm, f"unexpected radical key {k!r} in Integers debug_meta"
        pid = dm.get("selected_pattern_id")
        assert pid is None or isinstance(pid, str)

    for expr in NUMBER_PROMPTS:
        dm = _one(expr, NUMBER_SKILL)
        for k in _RADICAL_ONLY_DEBUG_META_KEYS:
            assert k not in dm, f"unexpected radical key {k!r} in Numbers debug_meta"
        pid = dm.get("selected_pattern_id")
        assert pid is None or isinstance(pid, str)
