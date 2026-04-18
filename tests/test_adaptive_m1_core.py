# -*- coding: utf-8 -*-

import json
import os
import sys
from pathlib import Path

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from core.adaptive.catalog_loader import build_family_index, load_catalog
from core.adaptive.manifest_registry import load_manifest, register_manifest_entry, resolve_script_path
from core.adaptive.schema import ManifestEntry, validate_ppo_strategy


TARGET_SKILL_ID = "jh_數學1上_FourArithmeticOperationsOfIntegers"


def test_catalog_loads_and_has_family_ids():
    entries = load_catalog()
    assert len(entries) > 0
    assert all(e.family_id for e in entries)


def test_catalog_index_contains_unique_keys():
    idx = build_family_index()
    assert len(idx) > 0
    assert len(idx) == len(set(idx.keys()))


def test_manifest_register_and_resolve():
    manifest_dir = Path(_PROJECT_ROOT) / "temp"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = manifest_dir / "pytest_skill_manifest.json"
    if manifest_path.exists():
        manifest_path.unlink()

    entry = register_manifest_entry(
        {
            "skill_id": TARGET_SKILL_ID,
            "family_id": "I4",
            "script_path": "skills/adaptive/jh_數學1上_FourArithmeticOperationsOfIntegers__I4__int_flat_mixed_four_ops.py",
            "version": 1,
            "subskill_nodes": ["sign_handling", "add_sub", "mul_div", "order_of_operations"],
            "generated_at": "2026-03-25T11:00:00",
            "model_name": "qwen3-vl-8b",
            "healer_applied": True,
        },
        manifest_path,
    )
    assert isinstance(entry, ManifestEntry)
    assert resolve_script_path("I4", manifest_path, skill_id=TARGET_SKILL_ID) == "skills/adaptive/jh_數學1上_FourArithmeticOperationsOfIntegers__I4__int_flat_mixed_four_ops.py"

    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    assert data[0]["family_id"] == "I4"
    assert data[0]["skill_id"] == TARGET_SKILL_ID
    assert len(load_manifest(manifest_path)) == 1
    manifest_path.unlink(missing_ok=True)


def test_validate_strategy():
    assert validate_ppo_strategy(3) == 3
