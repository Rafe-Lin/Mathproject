# -*- coding: utf-8 -*-
from __future__ import annotations


def _clamp(value: float, lower: float = 0.05, upper: float = 0.98) -> float:
    return max(lower, min(upper, float(value)))


def bootstrap_local_apr() -> float:
    """
    v1.1 local APR bootstrap value.
    This module is a heuristic runtime tracker (AKT stub), not a real AKT model.
    """
    return 0.45


def update_local_apr(previous_apr: float, is_correct: bool, frustration_index: int, subskill_count: int = 1) -> float:
    """
    Heuristic local APR update for v1.1:
    - correct answers raise local APR
    - wrong answers lower local APR
    - repeated frustration slightly amplifies the penalty
    """
    apr = float(previous_apr)
    span_bonus = min(max(int(subskill_count), 1), 4) * 0.01

    if bool(is_correct):
        apr += 0.08 + span_bonus
        apr -= min(max(frustration_index, 0), 3) * 0.01
    else:
        apr -= 0.10 + span_bonus
        apr -= min(max(frustration_index, 0), 3) * 0.02

    return round(_clamp(apr), 4)
