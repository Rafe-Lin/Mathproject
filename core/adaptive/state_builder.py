from __future__ import annotations

from collections import defaultdict
from typing import Any

from .agent_skill_schema import AGENT_SKILLS, resolve_agent_skill


def _to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    text = str(value or "").strip().lower()
    return text in {"1", "true", "yes"}


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _row_get(row: Any, key: str, default: Any = None) -> Any:
    if row is None:
        return default
    if isinstance(row, dict):
        return row.get(key, default)
    return getattr(row, key, default)


def build_agent_state(
    *,
    session: dict[str, Any] | None,
    history: list[Any] | None,
    system_skill_id: str,
    current_apr: float,
    frustration_index: int,
    last_is_correct: bool | None,
) -> dict[str, Any]:
    session = session or {}
    rows = history or []

    mastery_by_skill = {skill: 0.45 for skill in AGENT_SKILLS}
    counts_by_skill = defaultdict(int)

    # Aggregate observed APR per mapped agent skill from history.
    for row in rows:
        mapped = resolve_agent_skill(_row_get(row, "system_skill_id", system_skill_id))
        if mapped not in mastery_by_skill:
            continue
        apr = _safe_float(_row_get(row, "current_apr", 0.45), 0.45)
        mastery_by_skill[mapped] += apr
        counts_by_skill[mapped] += 1

    for skill in AGENT_SKILLS:
        if counts_by_skill[skill] > 0:
            mastery_by_skill[skill] = round(
                mastery_by_skill[skill] / float(counts_by_skill[skill] + 1), 4
            )
        else:
            # Current session APR as weak prior for the currently active system skill.
            mapped_current = resolve_agent_skill(system_skill_id)
            if mapped_current == skill:
                mastery_by_skill[skill] = round(_safe_float(current_apr, 0.45), 4)
            else:
                mastery_by_skill[skill] = 0.45

    # Fail streak from tail of history.
    fail_streak = 0
    for row in reversed(rows):
        is_correct = _row_get(row, "is_correct", None)
        if is_correct is None:
            break
        if _to_bool(is_correct):
            break
        fail_streak += 1

    # Same-skill streak from tail of history.
    same_skill_streak = 0
    mapped_current = resolve_agent_skill(system_skill_id)
    for row in reversed(rows):
        mapped = resolve_agent_skill(_row_get(row, "system_skill_id", system_skill_id))
        if mapped != mapped_current:
            break
        same_skill_streak += 1

    if last_is_correct is None:
        last_is_correct_flag = _to_bool(_row_get(rows[-1], "is_correct", False)) if rows else False
    else:
        last_is_correct_flag = bool(last_is_correct)

    vector = [
        mastery_by_skill[AGENT_SKILLS[0]],
        mastery_by_skill[AGENT_SKILLS[1]],
        mastery_by_skill[AGENT_SKILLS[2]],
        mastery_by_skill[AGENT_SKILLS[3]],
        float(_safe_int(frustration_index, 0)),
        float(fail_streak),
        float(same_skill_streak),
        1.0 if last_is_correct_flag else 0.0,
    ]

    return {
        "mastery_by_skill": mastery_by_skill,
        "frustration_index": _safe_int(frustration_index, 0),
        "fail_streak": fail_streak,
        "same_skill_streak": same_skill_streak,
        "last_is_correct": last_is_correct_flag,
        "system_skill_id": system_skill_id,
        "session_id": str(session.get("session_id", "") or ""),
        "state_vector": vector,  # fixed length = 8
    }
