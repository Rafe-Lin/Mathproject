from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.adaptive.catalog_loader import load_catalog
from core.adaptive.micro_generators import generate_micro_question


TARGET_SKILL_KEYWORDS = [
    "FourArithmeticOperationsOfNumbers",
    "FourArithmeticOperationsOfIntegers",
    "FourArithmeticOperationsOfPolynomial",
    "FourOperationsOfRadicals",
]

NARRATIVE_MARKERS = ["一個", "平均分成", "先", "剩下", "再", "面積", "長方形", "寬"]


def _contains_control_chars(text: str) -> bool:
    return any(ord(ch) < 32 and ch not in "\n\r\t" for ch in text)


def _contains_chinese(text: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", text))


def _extract_fraction_from_latex(text: str) -> tuple[int, int] | None:
    m = re.search(r"\\frac\{(-?\d+)\}\{(-?\d+)\}", text)
    if not m:
        return None
    return int(m.group(1)), int(m.group(2))


def _family_category(entry) -> str:
    sid = entry.skill_id
    fid = entry.family_id
    if "FourArithmeticOperationsOfNumbers" in sid:
        return "numbers"
    if "FourArithmeticOperationsOfIntegers" in sid:
        return "integers"
    if "FourArithmeticOperationsOfPolynomial" in sid:
        return "polynomial"
    if "FourOperationsOfRadicals" in sid:
        return "radicals"
    return fid.lower()


def _base_checks(entry, payload: dict) -> list[str]:
    issues: list[str] = []
    q = str(payload.get("question_text") or payload.get("question") or "")
    latex = str(payload.get("latex") or "")
    ans = str(payload.get("answer") or payload.get("correct_answer") or "")

    if not q.strip():
        issues.append("missing_question_text")
    if not ans.strip():
        issues.append("missing_answer")
    if "???" in q or "???" in latex:
        issues.append("mojibake_or_placeholder")
    if "_answer" in ans:
        issues.append("stub_answer_marker")
    if _contains_control_chars(q) or _contains_control_chars(latex):
        issues.append("control_character_in_text")
    if not _contains_chinese(q):
        issues.append("question_without_chinese")
    if "：" not in q and "?" not in q and "？" not in q:
        issues.append("missing_clear_instruction_shape")
    return issues


def _numbers_checks(entry, payload: dict) -> list[str]:
    issues: list[str] = []
    q = str(payload.get("question_text") or "")
    latex = str(payload.get("latex") or "")
    ans = str(payload.get("answer") or "")
    family_name = entry.family_name.lower()

    if "simplification" in family_name:
        frac = _extract_fraction_from_latex(latex or q)
        if frac:
            num, den = frac
            if den != 0 and math.gcd(abs(num), abs(den)) == 1:
                issues.append("simplification_question_already_reduced")
        if "化簡" not in q:
            issues.append("simplification_wording_mismatch")

    if "fill-blank" in family_name:
        if "\\square" not in q and "____" not in q and "空格" not in q:
            issues.append("fill_blank_without_blank")
        if "填入" not in q:
            issues.append("fill_blank_wording_mismatch")

    if "invariance" in family_name:
        if "擴大" not in q and "約分" not in q and "等值" not in q:
            issues.append("invariance_wording_unclear")

    if "comparison" in family_name:
        if "比較大小" not in q:
            issues.append("comparison_wording_mismatch")
        if ans not in {">", "<", "="}:
            issues.append("comparison_answer_not_relation_symbol")

    if "add/subtract" in family_name:
        if "和" not in q and "差" not in q and "計算" not in q:
            issues.append("add_sub_wording_unclear")

    if "multiply" in family_name and "積" not in q and "計算" not in q:
        issues.append("multiply_wording_unclear")

    if "divide" in family_name and "商" not in q and "計算" not in q:
        issues.append("divide_wording_unclear")

    if "reciprocal" in family_name:
        if "倒數" not in q:
            issues.append("reciprocal_wording_mismatch")
        try:
            Fraction(ans)
        except Exception:
            issues.append("reciprocal_answer_not_fraction")

    if "decimal-fraction" in family_name:
        if "小數" not in q or "分數" not in q:
            issues.append("decimal_fraction_wording_unclear")

    if "word problems" in family_name:
        if "\\frac" in q and not any(marker in q for marker in NARRATIVE_MARKERS):
            issues.append("word_problem_not_narrative_enough")
        if "請計算" not in q:
            issues.append("word_problem_missing_task_intro")

    return issues


def _integer_checks(entry, payload: dict) -> list[str]:
    issues: list[str] = []
    q = str(payload.get("question_text") or "")
    family = entry.family_id
    if family == "I6" and "絕對值" not in q and "|" not in q:
        issues.append("absolute_value_family_without_absolute_form")
    if family == "I5" and "left" not in q.lower() and "\\left" not in q and "(" not in q:
        issues.append("bracket_family_without_brackets")
    if family == "I4" and "\\times" not in q and "÷" not in q and "\\div" not in q:
        issues.append("mixed_ops_family_not_mixed")
    return issues


def _polynomial_checks(entry, payload: dict) -> list[str]:
    issues: list[str] = []
    q = str(payload.get("question_text") or "")
    family = entry.family_id
    if "x" not in q:
        issues.append("polynomial_question_without_variable")
    if family in {"F8", "F9", "F10"} and "展開" not in q:
        issues.append("expand_family_without_expand_wording")
    if family in {"F1", "F2", "F3", "F11", "F13"} and "化簡" not in q:
        issues.append("simplify_family_without_simplify_wording")
    return issues


def _radical_checks(entry, payload: dict) -> list[str]:
    issues: list[str] = []
    q = str(payload.get("question_text") or "")
    family = entry.family_id
    if "\\sqrt" not in q and "根號" not in q:
        issues.append("radical_question_without_radical_symbol")
    if family in {"p5a", "p5b"} and "有理化" not in q:
        issues.append("rationalize_family_without_rationalize_wording")
    if family in {"p2b", "p2c", "p2d"} and "展開" not in q:
        issues.append("expand_radical_family_without_expand_wording")
    return issues


def _scan_one(entry, payload: dict) -> list[str]:
    issues = _base_checks(entry, payload)
    category = _family_category(entry)
    if category == "numbers":
        issues.extend(_numbers_checks(entry, payload))
    elif category == "integers":
        issues.extend(_integer_checks(entry, payload))
    elif category == "polynomial":
        issues.extend(_polynomial_checks(entry, payload))
    elif category == "radicals":
        issues.extend(_radical_checks(entry, payload))
    return sorted(set(issues))


def _make_manual_sample(entry, payload: dict) -> dict:
    return {
        "family_id": entry.family_id,
        "family_name": entry.family_name,
        "question_text": payload.get("question_text"),
        "answer": payload.get("answer"),
        "subskill_nodes": list(entry.subskill_nodes),
    }


def build_report(samples_per_family: int = 8, manual_examples_per_family: int = 2) -> dict:
    entries = load_catalog()
    filtered = [e for e in entries if any(key in e.skill_id for key in TARGET_SKILL_KEYWORDS)]

    report: dict = {
        "summary": {},
        "skills": {},
        "manual_review_samples": {},
    }

    total_samples = 0
    total_issues = 0
    by_skill: dict[str, list] = defaultdict(list)
    for entry in filtered:
        by_skill[entry.skill_id].append(entry)

    for skill_id, skill_entries in by_skill.items():
        skill_result = {"families": {}, "issue_count": 0, "sample_count": 0}
        manual_samples: list[dict] = []
        for entry in skill_entries:
            family_result = {
                "family_name": entry.family_name,
                "samples_checked": 0,
                "issues": [],
                "examples": [],
            }
            for sample_idx in range(samples_per_family):
                payload = generate_micro_question(entry)
                family_result["samples_checked"] += 1
                skill_result["sample_count"] += 1
                total_samples += 1

                issues = _scan_one(entry, payload or {})
                if issues:
                    total_issues += len(issues)
                    skill_result["issue_count"] += len(issues)
                    family_result["issues"].extend(issues)
                    if len(family_result["examples"]) < 3:
                        family_result["examples"].append(
                            {
                                "question_text": payload.get("question_text"),
                                "answer": payload.get("answer"),
                                "issues": issues,
                            }
                        )

                if sample_idx < manual_examples_per_family:
                    manual_samples.append(_make_manual_sample(entry, payload or {}))

            family_result["issues"] = sorted(set(family_result["issues"]))
            skill_result["families"][entry.family_id] = family_result

        report["skills"][skill_id] = skill_result
        report["manual_review_samples"][skill_id] = manual_samples

    report["summary"] = {
        "skills_scanned": len(by_skill),
        "families_scanned": sum(len(v) for v in by_skill.values()),
        "samples_checked": total_samples,
        "issues_found": total_issues,
        "scan_version": "v2",
    }
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=int, default=8)
    parser.add_argument("--manual-examples", type=int, default=2)
    parser.add_argument("--output", type=str, default="")
    args = parser.parse_args()

    report = build_report(
        samples_per_family=args.samples,
        manual_examples_per_family=args.manual_examples,
    )
    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"report_written={args.output}")
    else:
        print(text)


if __name__ == "__main__":
    main()
