# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


ALLOWED_PPO_STRATEGIES = {0, 1, 2, 3}


def _require_non_empty_str(name: str, value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip()


def _normalize_subskills(value: Any) -> list[str]:
    if isinstance(value, str):
        raw = [x.strip() for x in value.split(';') if x.strip()]
    elif isinstance(value, list):
        raw = []
        for item in value:
            if not isinstance(item, str):
                raise ValueError("subskill_nodes must contain strings only")
            token = item.strip()
            if token:
                raw.append(token)
    else:
        raise ValueError("subskill_nodes must be a list[str] or semicolon-delimited string")

    deduped: list[str] = []
    seen = set()
    for token in raw:
        if token not in seen:
            seen.add(token)
            deduped.append(token)
    if not deduped:
        raise ValueError("subskill_nodes cannot be empty")
    return deduped


@dataclass
class CatalogEntry:
    skill_id: str
    skill_name: str
    family_id: str
    family_name: str
    theme: str
    subskill_nodes: list[str]
    notes: str

    @classmethod
    def from_row(cls, row: dict[str, Any]) -> "CatalogEntry":
        return cls(
            skill_id=_require_non_empty_str("skill_id", row.get("skill_id", "")),
            skill_name=_require_non_empty_str("skill_name", row.get("skill_name", "")),
            family_id=_require_non_empty_str("family_id", row.get("family_id", "")),
            family_name=_require_non_empty_str("family_name", row.get("family_name", "")),
            theme=_require_non_empty_str("theme", row.get("theme", "")),
            subskill_nodes=_normalize_subskills(row.get("subskill_nodes", [])),
            notes=str(row.get("notes", "") or "").strip(),
        )


@dataclass
class ManifestEntry:
    skill_id: str
    family_id: str
    script_path: str
    version: int
    subskill_nodes: list[str]
    generated_at: str
    model_name: str
    healer_applied: bool

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ManifestEntry":
        skill_id = _require_non_empty_str("skill_id", payload.get("skill_id", ""))
        family_id = _require_non_empty_str("family_id", payload.get("family_id", ""))
        script_path = _require_non_empty_str("script_path", payload.get("script_path", ""))
        version = int(payload.get("version", 1))
        if version <= 0:
            raise ValueError("version must be > 0")
        subskills = _normalize_subskills(payload.get("subskill_nodes", []))
        generated_at = str(payload.get("generated_at", "") or "").strip()
        if generated_at:
            # Ensure ISO-ish timestamp can be parsed.
            datetime.fromisoformat(generated_at.replace("Z", "+00:00"))
        else:
            generated_at = datetime.utcnow().isoformat(timespec="seconds")
        model_name = _require_non_empty_str("model_name", payload.get("model_name", "unknown"))
        healer_applied = bool(payload.get("healer_applied", False))
        return cls(
            skill_id=skill_id,
            family_id=family_id,
            script_path=script_path,
            version=version,
            subskill_nodes=subskills,
            generated_at=generated_at,
            model_name=model_name,
            healer_applied=healer_applied,
        )

    @property
    def manifest_key(self) -> str:
        return f"{self.skill_id}:{self.family_id}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "family_id": self.family_id,
            "script_path": self.script_path,
            "version": self.version,
            "subskill_nodes": list(self.subskill_nodes),
            "generated_at": self.generated_at,
            "model_name": self.model_name,
            "healer_applied": self.healer_applied,
        }


def validate_ppo_strategy(value: int) -> int:
    strategy = int(value)
    if strategy not in ALLOWED_PPO_STRATEGIES:
        raise ValueError(f"ppo_strategy must be one of {sorted(ALLOWED_PPO_STRATEGIES)}")
    return strategy
