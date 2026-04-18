# -*- coding: utf-8 -*-

from core.adaptive.policy_findings_mapping import (
    _reset_config_cache_for_tests as reset_policy_cfg,
    build_policy_findings_hints,
)


def test_findings_trigger_hint_allows_cross_skill_when_fail_streak_high():
    reset_policy_cfg()
    hints = build_policy_findings_hints(
        fail_streak=2,
        frustration=0.2,
        same_skill_streak=1,
        cross_skill_trigger=False,
        allowed_actions=["stay"],
    )
    assert hints["trigger_hints"]["base_cross_skill_trigger"] is False
    assert hints["trigger_hints"]["allow_cross_skill_by_finding"] is True
    assert hints["trigger_hints"]["effective_cross_skill_trigger"] is True


def test_findings_action_prior_prefers_remediate_on_high_frustration():
    reset_policy_cfg()
    hints = build_policy_findings_hints(
        fail_streak=1,
        frustration=0.75,
        same_skill_streak=2,
        cross_skill_trigger=True,
        allowed_actions=["stay", "remediate"],
    )
    prior = hints["action_prior_hints"]
    assert prior["prefer_remediate"] is True
    assert "remediate" in prior
    assert "stay" in prior
    assert "return" in prior
