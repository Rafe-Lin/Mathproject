# -*- coding: utf-8 -*-

from core.adaptive.rag_diagnosis_mapping import (
    _reset_config_cache_for_tests as reset_rag_cfg,
    map_retrieval_to_diagnosis,
)


def test_map_negative_sign_handling_to_integer_signed_arithmetic():
    reset_rag_cfg()
    diagnosis = map_retrieval_to_diagnosis(
        retrieval_result={"top_concept": "negative_sign_handling", "retrieval_confidence": 0.9},
        current_skill="polynomial_arithmetic",
        current_subskill="sign_distribution",
    )
    assert diagnosis["top_concept"] == "negative_sign_handling"
    assert diagnosis["suggested_prereq_skill"] == "integer_arithmetic"
    assert diagnosis["suggested_prereq_subskill"] == "signed_arithmetic"
    assert "retrieval_confidence" in diagnosis
    assert "diagnosis_confidence" in diagnosis
    assert diagnosis["route_type"] == "rescue"


def test_map_division_misconception_to_integer_division():
    reset_rag_cfg()
    diagnosis = map_retrieval_to_diagnosis(
        retrieval_result={"top_concept": "division_misconception", "retrieval_confidence": 0.82},
        current_skill="fraction_arithmetic",
        current_subskill="fraction_mul_div",
    )
    assert diagnosis["suggested_prereq_skill"] == "integer_arithmetic"
    assert diagnosis["suggested_prereq_subskill"] == "division"
    assert 0.0 <= float(diagnosis["retrieval_confidence"]) <= 1.0
    assert 0.0 <= float(diagnosis["diagnosis_confidence"]) <= 1.0


def test_map_basic_arithmetic_instability_to_integer_basic_operations():
    reset_rag_cfg()
    diagnosis = map_retrieval_to_diagnosis(
        retrieval_result={"top_concept": "basic_arithmetic_instability", "retrieval_confidence": 0.7},
        current_skill="fraction_arithmetic",
        current_subskill="fraction_add_sub",
    )
    assert diagnosis["suggested_prereq_skill"] == "integer_arithmetic"
    assert diagnosis["suggested_prereq_subskill"] == "basic_operations"
    assert diagnosis["error_concept"] == "basic_arithmetic_instability"
