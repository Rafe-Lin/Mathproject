# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.adaptive.catalog_loader import load_catalog
from core.adaptive.manifest_registry import load_manifest, register_manifest_entry


OUTPUT_DIR = PROJECT_ROOT / "skills" / "adaptive"
MANIFEST_PATH = PROJECT_ROOT / "docs" / "自適應實作" / "skill_manifest.json"


SCRIPT_TEMPLATE = """# -*- coding: utf-8 -*-
\"\"\"Auto-generated adaptive micro-skill stub.

skill_id: {skill_id}
family_id: {family_id}
family_name: {family_name}
subskill_nodes: {subskills}
\"\"\"

from __future__ import annotations


def generate(level=1):
    question_text = "【{family_id}】{family_name}（level={{}}）".format(level)
    answer = "{family_id}_answer"
    return {{
        "question": question_text,
        "question_text": question_text,
        "latex": question_text,
        "answer": answer,
        "family_id": "{family_id}",
        "subskill_nodes": {subskills},
    }}


def check(user_answer, correct_answer):
    return str(user_answer).strip() == str(correct_answer).strip()
"""


def _safe_slug(text: str) -> str:
    keep: list[str] = []
    for ch in text:
        if ch.isalnum() or ch in ("_", "-"):
            keep.append(ch)
        else:
            keep.append("_")
    return "".join(keep).strip("_")


def build_micro_skills() -> dict[str, int]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    catalog = load_catalog()
    existing = {entry.manifest_key for entry in load_manifest(MANIFEST_PATH)}

    created = 0
    reused = 0
    registered = 0

    for entry in catalog:
        stem = f"{_safe_slug(entry.skill_id)}__{_safe_slug(entry.family_id)}__{_safe_slug(entry.family_name)}"
        script_path = OUTPUT_DIR / f"{stem}.py"

        if script_path.exists():
            reused += 1
        else:
            script_path.write_text(
                SCRIPT_TEMPLATE.format(
                    skill_id=entry.skill_id,
                    family_id=entry.family_id,
                    family_name=entry.family_name,
                    subskills=json.dumps(entry.subskill_nodes, ensure_ascii=False),
                ),
                encoding="utf-8",
            )
            created += 1

        manifest_payload = {
            "skill_id": entry.skill_id,
            "family_id": entry.family_id,
            "script_path": str(script_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
            "version": 1,
            "subskill_nodes": entry.subskill_nodes,
            "generated_at": datetime.utcnow().isoformat(timespec="seconds"),
            "model_name": "micro-skill-factory-stub",
            "healer_applied": False,
        }
        register_manifest_entry(manifest_payload, MANIFEST_PATH)

        composite_key = f"{entry.skill_id}:{entry.family_id}"
        if composite_key not in existing:
            existing.add(composite_key)
            registered += 1

    return {
        "catalog_entries": len(catalog),
        "created_scripts": created,
        "reused_scripts": reused,
        "registered_entries": registered,
    }


if __name__ == "__main__":
    print(json.dumps(build_micro_skills(), ensure_ascii=False, indent=2))
