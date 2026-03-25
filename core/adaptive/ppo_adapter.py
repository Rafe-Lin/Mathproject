# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Iterable

from .schema import CatalogEntry, validate_ppo_strategy


def choose_strategy(current_apr: float, frustration_index: int, step_number: int) -> int:
    """
    v1.1 PoC PPO stub.
    Strategy codes are fixed to the paper-aligned mapping:
    0 = Max-Fisher
    1 = ZPD
    2 = Diversity
    3 = Review
    """
    if frustration_index >= 2:
        return 3
    if current_apr < 0.45:
        return 1
    if step_number > 0 and step_number % 4 == 0:
        return 2
    return 0


def choose_next_family(
    entries: list[CatalogEntry],
    visited_family_ids: Iterable[str] | None,
    strategy: int,
    last_family_id: str | None = None,
) -> CatalogEntry:
    """
    Choose the next family with deterministic behavior for M2 API testing.
    """
    validate_ppo_strategy(strategy)
    if not entries:
        raise ValueError("entries cannot be empty")

    visited = {item.strip() for item in (visited_family_ids or []) if str(item).strip()}
    ordered = sorted(entries, key=lambda entry: (entry.skill_id, entry.family_id))

    if strategy == 3 and last_family_id:
        for entry in ordered:
            if entry.family_id == last_family_id:
                return entry

    unvisited = [entry for entry in ordered if entry.family_id not in visited]
    if strategy == 2 and unvisited:
        return unvisited[-1]
    if unvisited:
        return unvisited[0]

    if last_family_id:
        for idx, entry in enumerate(ordered):
            if entry.family_id == last_family_id:
                return ordered[(idx + 1) % len(ordered)]

    return ordered[0]
