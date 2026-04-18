# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.adaptive.script_dispatch import call_adaptive_script


@dataclass(frozen=True)
class FamilyTarget:
    skill_id: str
    family_id: str
    name: str


TARGETS: list[FamilyTarget] = [
    FamilyTarget(
        skill_id="jh_數學2上_FourArithmeticOperationsOfPolynomial",
        family_id="F1",
        name="poly_add_sub_flat",
    ),
    FamilyTarget(
        skill_id="jh_數學2上_FourArithmeticOperationsOfPolynomial",
        family_id="F2",
        name="poly_add_sub_nested",
    ),
    FamilyTarget(
        skill_id="jh_數學2上_FourArithmeticOperationsOfPolynomial",
        family_id="F5",
        name="poly_mul_poly",
    ),
    FamilyTarget(
        skill_id="jh_數學2上_FourArithmeticOperationsOfPolynomial",
        family_id="F11",
        name="poly_mixed_simplify",
    ),
    FamilyTarget(
        skill_id="jh_數學1上_FourArithmeticOperationsOfIntegers",
        family_id="I1",
        name="int_numberline_add_sub",
    ),
    FamilyTarget(
        skill_id="jh_數學1上_FourArithmeticOperationsOfIntegers",
        family_id="I2",
        name="int_flat_add_sub",
    ),
    FamilyTarget(
        skill_id="jh_數學1上_FourArithmeticOperationsOfIntegers",
        family_id="I3",
        name="int_flat_mul_div_exact",
    ),
    FamilyTarget(
        skill_id="jh_數學1上_FourArithmeticOperationsOfIntegers",
        family_id="I4",
        name="int_flat_mixed_four_ops",
    ),
    FamilyTarget(
        skill_id="jh_數學1上_FourArithmeticOperationsOfIntegers",
        family_id="I7",
        name="int_division_exact_nested",
    ),
]


def _looks_like_placeholder(payload: dict) -> bool:
    if not isinstance(payload, dict):
        return True
    question_text = str(payload.get("question_text") or payload.get("question") or "").strip()
    answer = str(payload.get("answer") or payload.get("correct_answer") or "").strip()
    if not question_text or not answer:
        return True
    if answer.endswith("_answer"):
        return True
    if "請完成" in question_text:
        return True
    if question_text.startswith("【") and "level=" in question_text:
        return True
    lowered = question_text.lower()
    return ("poly_" in lowered) or ("int_" in lowered) or ("fraction_" in lowered)


def run_smoke(samples_per_family: int = 10) -> dict:
    report: dict[str, dict] = {}
    demo_safe: list[str] = []
    for target in TARGETS:
        success = 0
        placeholder = 0
        errors: list[str] = []
        for _ in range(samples_per_family):
            result = call_adaptive_script(target.skill_id, target.family_id, level=1)
            payload = result.get("payload") if isinstance(result, dict) else None
            call_ok = bool(result.get("generator_call_success")) if isinstance(result, dict) else False
            schema_ok = bool(result.get("payload_schema_valid")) if isinstance(result, dict) else False
            is_placeholder = _looks_like_placeholder(payload if isinstance(payload, dict) else {})
            if call_ok and schema_ok and not is_placeholder:
                success += 1
            if is_placeholder:
                placeholder += 1
            if not call_ok:
                errors.append(str(result.get("error") if isinstance(result, dict) else "unknown_error"))
        success_rate = success / float(samples_per_family)
        placeholder_rate = placeholder / float(samples_per_family)
        key = f"{target.family_id}:{target.name}"
        report[key] = {
            "skill_id": target.skill_id,
            "family_id": target.family_id,
            "family_name": target.name,
            "samples": samples_per_family,
            "success_rate": round(success_rate, 4),
            "placeholder_rate": round(placeholder_rate, 4),
            "demo_safe": (success_rate == 1.0 and placeholder_rate == 0.0),
            "errors": sorted(set(errors)),
        }
        if report[key]["demo_safe"]:
            demo_safe.append(key)
    return {"report": report, "demo_safe_families": demo_safe}


if __name__ == "__main__":
    output = run_smoke(samples_per_family=10)
    for key, row in output["report"].items():
        print(
            f"{key} success_rate={row['success_rate']:.2f} "
            f"placeholder_rate={row['placeholder_rate']:.2f} demo_safe={row['demo_safe']}"
        )
    print("demo_safe_families=", ",".join(output["demo_safe_families"]))
