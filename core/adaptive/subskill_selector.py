from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from .agent_skill_schema import AGENT_SKILL_SUBSKILLS


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FAMILY_SUBSKILL_MAP_PATH = PROJECT_ROOT / "docs" / "自適應實作" / "family_subskill_map.json"


def load_family_subskill_map() -> dict[str, list[str]]:
    if not FAMILY_SUBSKILL_MAP_PATH.exists():
        return {}
    try:
        payload = json.loads(FAMILY_SUBSKILL_MAP_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}
    if not isinstance(payload, dict):
        return {}
    out: dict[str, list[str]] = {}
    for key, value in payload.items():
        if isinstance(value, list):
            out[str(key)] = [str(x).strip() for x in value if str(x).strip()]
    return out


def _infer_error_type(diagnostics: dict[str, Any] | None) -> str:
    diagnostics = diagnostics or {}
    return str(
        diagnostics.get("error_type")
        or diagnostics.get("last_error_type")
        or ""
    ).strip().lower()


def _error_type_to_subskill(agent_skill: str, error_type: str) -> str | None:
    if not error_type:
        return None
    if agent_skill == "integer_arithmetic":
        if "sign" in error_type:
            return "sign_handling"
        if "add" in error_type or "sub" in error_type:
            return "add_sub"
        if "mul" in error_type or "div" in error_type:
            return "mul_div"
    if agent_skill == "fraction_arithmetic":
        if "equivalent" in error_type:
            return "equivalent_fraction_scaling"
        if "reciprocal" in error_type:
            return "reciprocal"
        if "simplify" in error_type:
            return "simplest_form_reduction"
    if agent_skill == "radical_arithmetic":
        if "rationalize" in error_type:
            return "conjugate_rationalize"
        return "radical_simplify"
    if agent_skill == "polynomial_arithmetic":
        if "expand" in error_type:
            return "poly_expand"
        if "mul" in error_type:
            return "poly_mul_poly"
        return "poly_add_sub"
    if agent_skill == "linear_expression_arithmetic":
        if "outer_minus" in error_type or "bracket" in error_type:
            return "outer_minus_scope"
        if "distribution" in error_type:
            return "monomial_distribution"
        if "nested" in error_type:
            return "nested_bracket_scope"
        if "fraction" in error_type:
            return "fractional_expression_simplification"
        if "like" in error_type:
            return "like_term_combination"
        return "term_collection_with_constants"
    return None


def _row_get(row: Any, key: str, default: Any = None) -> Any:
    if row is None:
        return default
    if isinstance(row, dict):
        return row.get(key, default)
    return getattr(row, key, default)


def select_subskill(
    agent_skill: str,
    session: dict[str, Any] | None,
    history: list[Any] | None,
    diagnostics: dict[str, Any] | None = None,
) -> tuple[str | None, dict[str, Any]]:
    session = session or {}
    history = history or []
    diagnostics = diagnostics or {}
    candidates = list(AGENT_SKILL_SUBSKILLS.get(agent_skill, []))
    if not candidates:
        return None, {"reason": "no_subskill_candidates"}

    error_type = _infer_error_type(diagnostics)
    mapped = _error_type_to_subskill(agent_skill, error_type)
    if mapped in candidates:
        return mapped, {
            "mode": "error_type_mapping",
            "error_type": error_type,
            "selected_subskill": mapped,
        }

    counts = defaultdict(int)
    for row in history:
        target_subskills = _row_get(row, "target_subskills", "")
        if isinstance(target_subskills, str):
            parts = [x.strip() for x in target_subskills.replace(",", ";").split(";") if x.strip()]
        elif isinstance(target_subskills, list):
            parts = [str(x).strip() for x in target_subskills if str(x).strip()]
        else:
            parts = []
        for sub in parts:
            if sub in candidates:
                counts[sub] += 1

    # Lower usage means weaker/less practiced in this heuristic fallback.
    ranked = sorted(candidates, key=lambda s: (counts[s], s))
    selected = ranked[0]

    # avoid too many repeated same subskill turns
    last_subskill = str(session.get("last_subskill", "") or diagnostics.get("last_subskill", "")).strip()
    same_subskill_streak = int(diagnostics.get("same_subskill_streak", 0) or 0)
    if last_subskill == selected and same_subskill_streak >= 2 and len(ranked) > 1:
        selected = ranked[1]
        mode = "second_weak_due_to_same_subskill_streak"
    else:
        mode = "weakest_subskill_by_history"

    return selected, {
        "mode": mode,
        "error_type": error_type,
        "counts": dict(counts),
        "ranked_subskills": ranked,
        "selected_subskill": selected,
    }
