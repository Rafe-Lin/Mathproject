# -*- coding: utf-8 -*-

import shutil
import uuid
from pathlib import Path

from core.adaptive.policy_findings_mapping import (
    _reset_config_cache_for_tests as reset_policy_cfg,
    build_policy_findings_hints,
)
from core.adaptive.rag_diagnosis_mapping import (
    _reset_config_cache_for_tests as reset_rag_cfg,
    map_retrieval_to_diagnosis,
)


def _local_tmp_dir() -> Path:
    base = Path("tests") / ".tmp_config"
    base.mkdir(parents=True, exist_ok=True)
    target = base / f"case_{uuid.uuid4().hex[:8]}"
    target.mkdir(parents=True, exist_ok=True)
    return target


def test_rag_mapping_yaml_override_success(monkeypatch):
    tmp_dir = _local_tmp_dir()
    cfg = tmp_dir / "rag_override.yaml"
    cfg.write_text(
        "\n".join(
            [
                "concept_to_prereq:",
                "  negative_sign_handling:",
                "    suggested_prereq_skill: integer_arithmetic",
                "    suggested_prereq_subskill: sign_custom",
                "    concept_weight: 0.99",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("ADAPTIVE_RAG_DIAGNOSIS_MAPPING_CONFIG", str(cfg))
    reset_rag_cfg()

    diagnosis = map_retrieval_to_diagnosis(
        {"top_concept": "negative_sign_handling", "retrieval_confidence": 0.8},
        current_skill="polynomial_arithmetic",
        current_subskill="sign_distribution",
    )
    assert diagnosis["suggested_prereq_subskill"] == "sign_custom"
    assert "diagnosis_confidence" in diagnosis
    reset_rag_cfg()
    shutil.rmtree(tmp_dir, ignore_errors=True)


def test_rag_mapping_yaml_fallback_when_missing(monkeypatch):
    monkeypatch.setenv("ADAPTIVE_RAG_DIAGNOSIS_MAPPING_CONFIG", "D:/__not_exists__/rag.yaml")
    reset_rag_cfg()

    diagnosis = map_retrieval_to_diagnosis(
        {"top_concept": "division_misconception", "retrieval_confidence": 0.7},
        current_skill="fraction_arithmetic",
        current_subskill="fraction_mul_div",
    )
    assert diagnosis["suggested_prereq_skill"] == "integer_arithmetic"
    assert diagnosis["suggested_prereq_subskill"] == "division"
    reset_rag_cfg()


def test_policy_findings_yaml_partial_fields_do_not_crash(monkeypatch):
    tmp_dir = _local_tmp_dir()
    cfg = tmp_dir / "policy_partial.yaml"
    cfg.write_text(
        "\n".join(
            [
                "action_prior_hints:",
                "  remediate_bias: 0.5",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("ADAPTIVE_POLICY_FINDINGS_MAPPING_CONFIG", str(cfg))
    reset_policy_cfg()

    hints = build_policy_findings_hints(
        fail_streak=1,
        frustration=0.8,
        same_skill_streak=2,
        cross_skill_trigger=True,
        allowed_actions=["stay", "remediate"],
    )
    assert "trigger_hints" in hints
    assert "reward_hints" in hints
    assert "action_prior_hints" in hints
    assert "prefer_remediate" in hints["action_prior_hints"]
    reset_policy_cfg()
    shutil.rmtree(tmp_dir, ignore_errors=True)


def test_policy_findings_yaml_override_success(monkeypatch):
    tmp_dir = _local_tmp_dir()
    cfg = tmp_dir / "policy_override.yaml"
    cfg.write_text(
        "\n".join(
            [
                "trigger_hints:",
                "  fail_streak_cross_skill_threshold: 5",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("ADAPTIVE_POLICY_FINDINGS_MAPPING_CONFIG", str(cfg))
    reset_policy_cfg()

    hints = build_policy_findings_hints(
        fail_streak=2,
        frustration=0.2,
        same_skill_streak=1,
        cross_skill_trigger=False,
        allowed_actions=["stay"],
    )
    assert hints["trigger_hints"]["allow_cross_skill_by_finding"] is False
    reset_policy_cfg()
    shutil.rmtree(tmp_dir, ignore_errors=True)
