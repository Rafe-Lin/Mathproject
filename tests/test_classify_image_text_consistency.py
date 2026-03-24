# -*- coding: utf-8 -*-
"""
/api/classify 與 /api/generate_live：圖文路徑一致化之回歸測試（mock VL / engine）。
"""

import json
import os
import sys
from unittest.mock import MagicMock, patch

import pytest

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from app import create_app

_INT_SKILL = "jh_數學1上_FourArithmeticOperationsOfIntegers"


def _vl_json_content(obj: dict) -> str:
    return json.dumps(obj, ensure_ascii=False)


class _FakeVLResponse:
    def __init__(self, content: str):
        self._content = content

    def raise_for_status(self):
        return None

    def json(self):
        return {"message": {"content": self._content}}


@pytest.fixture()
def app_client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_classify_text_deterministic_matches_mocked_image_vl(app_client):
    """純文字走決定性分類；圖片路徑 mock VL 回傳同題 OCR，skill / fingerprint 應一致。"""
    text_body = {"text_data": "3+5"}
    r_text = app_client.post("/api/classify", json=text_body)
    assert r_text.status_code == 200, r_text.get_data(as_text=True)
    j_text = r_text.get_json()
    assert j_text.get("success") is True
    assert j_text.get("skill_id") == _INT_SKILL
    assert j_text.get("classify_source") == "deterministic"
    assert j_text.get("deterministic_rule") == "rule:integer_arithmetic"
    fp_text = (j_text.get("json_spec") or {}).get("operator_fingerprint")
    assert isinstance(fp_text, dict)

    vl_payload = {
        "ocr_text": "3 + 5",
        "skill_id": _INT_SKILL,
        "confidence": 95,
    }

    def _fake_post(url, json=None, timeout=None, **kwargs):
        return _FakeVLResponse(_vl_json_content(vl_payload))

    with patch("core.routes.live_show.requests.post", side_effect=_fake_post):
        r_img = app_client.post("/api/classify", json={"image_data": "ZmFrZQ=="})
    assert r_img.status_code == 200, r_img.get_data(as_text=True)
    j_img = r_img.get_json()
    assert j_img.get("skill_id") == _INT_SKILL
    assert j_img.get("classify_source") == "vision_llm"
    fp_img = (j_img.get("json_spec") or {}).get("operator_fingerprint")
    assert j_img.get("ocr_text") == j_text.get("ocr_text") == "3+5"
    assert fp_img == fp_text


def test_generate_live_same_json_spec_text_vs_image_payload_mock_engine(app_client):
    """帶 image_data 但預設不附圖時，與純文字請求共用同一 canonical OCR，debug_meta 關鍵欄位一致。"""
    json_spec = {
        "ocr_text": "7+8",
        "operator_fingerprint": {"number_count": 2, "operator_count": 1},
        "isomorphic_constraints": "",
    }

    def _fake_generate_practice_set(**kwargs):
        return {
            "success": True,
            "problems": [
                {
                    "question_text": r"$7+8$",
                    "correct_answer": "15",
                    "_live_mcri": {
                        "syntax_score": 80,
                        "logic_score": 80,
                        "render_score": 80,
                        "stability_score": 80,
                        "total_score": 80,
                        "breakdown": {},
                    },
                }
            ],
            "debug_meta": {
                "final_code": 'pattern_id = "unit_test_pattern"\n',
                "raw_code": "",
                "performance": {"ai_inference_time_sec": 0, "cpu_execution_time_sec": 0},
                "healer_trace": {
                    "regex_fixes": 0,
                    "regex_code_fixes": 0,
                    "regex_display_fixes": 0,
                    "ast_fixes": 0,
                    "o1_fixes": 0,
                },
                "mcri_report": {"robustness_grade": "NEUTRAL"},
                "healer_logs": [],
                "selected_pattern_id": "unit_test_pattern",
                "fallback_used": False,
                "iso_guard_triggered": False,
            },
        }

    base = {
        "skill_id": _INT_SKILL,
        "json_spec": json_spec,
        "input_text": "7+8",
        "prompt": "7+8",
        "ablation_mode": True,
        "count": 1,
    }

    engine_mock = MagicMock()
    engine_mock.generate_practice_set = MagicMock(side_effect=_fake_generate_practice_set)

    with patch("core.routes.live_show.get_engine", return_value=engine_mock):
        r_a = app_client.post("/api/generate_live", json=dict(base))
        r_b = app_client.post(
            "/api/generate_live",
            json=dict(base, image_data="ZmFrZV9pbWFnZV9kYXRh"),
        )

    assert r_a.status_code == 200, r_a.get_data(as_text=True)
    assert r_b.status_code == 200, r_b.get_data(as_text=True)
    ja, jb = r_a.get_json(), r_b.get_json()
    dma = ja.get("debug_meta") or {}
    dmb = jb.get("debug_meta") or {}

    assert dma.get("canonical_ocr_text") == dmb.get("canonical_ocr_text") == "7+8"
    assert dma.get("selected_pattern_id") == dmb.get("selected_pattern_id")
    ofa = ja.get("iso_profile_expected") or {}
    ofb = jb.get("iso_profile_expected") or {}
    assert ofa.get("number_count") == ofb.get("number_count") == 2
    assert dma.get("used_image_hint_in_generate") is False
    assert dmb.get("used_image_hint_in_generate") is False
    assert dma.get("input_mode") == "text"
    assert dmb.get("input_mode") == "image"
