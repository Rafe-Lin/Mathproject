# -*- coding: utf-8 -*-

from core.adaptive.micro_generators import generate_micro_question
from core.adaptive.schema import CatalogEntry


POLY_SKILL_ID = "jh_數學2上_FourArithmeticOperationsOfPolynomial"


def _entry(family_id: str, family_name: str) -> CatalogEntry:
    return CatalogEntry(
        skill_id=POLY_SKILL_ID,
        skill_name="多項式四則運算",
        family_id=family_id,
        family_name=family_name,
        theme="test",
        subskill_nodes=["poly.test"],
        notes="",
    )


def test_f8_generates_division_qr_prompt():
    payload = generate_micro_question(_entry("F8", "poly_div_monomial_qr"))
    text = str(payload.get("question_text", ""))
    assert "展開" not in text
    assert "div" in text or "求商與餘數" in text
    assert "Q=" in str(payload.get("answer", ""))
    assert "R=" in str(payload.get("answer", ""))


def test_f9_generates_poly_division_qr_prompt():
    payload = generate_micro_question(_entry("F9", "poly_div_poly_qr"))
    text = str(payload.get("question_text", ""))
    assert "展開" not in text
    assert "多項式除法" in text or "求商與餘數" in text
    assert "Q=" in str(payload.get("answer", ""))
    assert "R=" in str(payload.get("answer", ""))


def test_f10_generates_reverse_division_prompt_not_expansion():
    payload = generate_micro_question(_entry("F10", "poly_div_reverse"))
    text = str(payload.get("question_text", ""))
    assert "展開" not in text
    assert "反推被除式" in text
    assert "除式" in text and "商" in text and "餘數" in text
