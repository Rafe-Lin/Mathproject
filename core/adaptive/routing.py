from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .agent_skill_schema import AGENT_SKILL_SUBSKILLS
from .qwen_diagnostic_classifier import QwenDiagnosticClassifier
from .rag_diagnosis_mapping import map_retrieval_to_diagnosis
from .remediation_retriever import retrieve_remediation_candidates
from .subskill_ontology import normalize_runtime_subskill


ROUTE_STAY = "stay"
ROUTE_REMEDIATE = "remediate"
ROUTE_RETURN = "return"

ERROR_CONCEPT_TO_PREREQ: dict[str, dict[str, str]] = {
    "negative_sign_handling": {
        "skill": "integer_arithmetic",
        "subskill": "sign_handling",
    },
    "division_misconception": {
        "skill": "integer_arithmetic",
        "subskill": "mul_div",
    },
    "basic_arithmetic_instability": {
        "skill": "integer_arithmetic",
        "subskill": "add_sub",
    },
    "fraction_as_whole_number_confusion": {
        "skill": "integer_arithmetic",
        "subskill": "mul_div",
    },
    "outer_minus_scope": {
        "skill": "integer_arithmetic",
        "subskill": "outer_minus_scope",
    },
    "bracket_scope_error": {
        "skill": "integer_arithmetic",
        "subskill": "outer_minus_scope",
    },
    "sign_distribution": {
        "skill": "integer_arithmetic",
        "subskill": "sign_handling",
    },
    "sign_flip_after_distribution": {
        "skill": "integer_arithmetic",
        "subskill": "sign_handling",
    },
    "combine_like_terms_after_distribution": {
        "skill": "integer_arithmetic",
        "subskill": "basic_operations",
    },
    "coefficient_arithmetic_error": {
        "skill": "integer_arithmetic",
        "subskill": "division",
    },
    "nested_grouping_structure_error": {
        "skill": "integer_arithmetic",
        "subskill": "bracket_scope",
    },
    "binomial_expansion_structure_error": {
        "skill": "integer_arithmetic",
        "subskill": "division",
    },
    "mixed_simplify_transition_error": {
        "skill": "integer_arithmetic",
        "subskill": "order_of_operations",
    },
    "family_isomorphism_confusion": {
        "skill": "integer_arithmetic",
        "subskill": "basic_operations",
    },
}

ALLOWED_CROSS_SKILL_PATHS = {
    ("polynomial_arithmetic", "integer_arithmetic"),
    ("polynomial_arithmetic", "linear_expression_arithmetic"),
    ("polynomial_arithmetic", "fraction_arithmetic"),
    ("fraction_arithmetic", "integer_arithmetic"),
}


def _infer_prereq_skill_from_runtime_subskill(runtime_subskill: str, default_skill: str = "integer_arithmetic") -> str:
    key = str(runtime_subskill or "").strip()
    if not key:
        return default_skill
    for agent_skill, subskills in AGENT_SKILL_SUBSKILLS.items():
        if key in set(subskills or []):
            return str(agent_skill)
    return default_skill


@dataclass
class DiagnosisPacket:
    error_concept: str
    retrieval_confidence: float
    diagnosis_confidence: float
    suggested_prereq_skill: str | None
    suggested_prereq_subskill: str | None
    route_type: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "error_concept": self.error_concept,
            "retrieval_confidence": self.retrieval_confidence,
            "diagnosis_confidence": self.diagnosis_confidence,
            "suggested_prereq_skill": self.suggested_prereq_skill,
            "suggested_prereq_subskill": self.suggested_prereq_subskill,
            "route_type": self.route_type,
        }


def _norm01(value: Any, default: float = 0.0) -> float:
    try:
        return max(0.0, min(1.0, float(value)))
    except Exception:
        return default


def rag_diagnose(
    *,
    current_skill: str,
    current_subskill: str,
    current_family_id: str = "",
    question_text: str = "",
    student_answer: str = "",
    expected_answer: str = "",
    is_correct: bool | None = None,
    fail_streak: int = 0,
    frustration: float = 0.0,
    same_skill_streak: int = 0,
    routing_session: dict[str, Any] | None = None,
    prerequisite_candidates: list[dict[str, Any]] | None = None,
    unit_skill_id: str = "",
    enable_choice_diagnosis: bool = False,
) -> dict[str, Any]:
    if is_correct:
        return map_retrieval_to_diagnosis(
            {
                "top_concept": "none",
                "retrieval_confidence": 0.5,
            },
            current_skill=current_skill,
            current_subskill=current_subskill,
        )

    if enable_choice_diagnosis and str(current_skill) == "polynomial_arithmetic":
        retrieval = retrieve_remediation_candidates(
            skill_id=str(unit_skill_id or ""),
            family_id=str(current_family_id or ""),
            question_text=str(question_text or ""),
            correct_answer=str(expected_answer or ""),
            student_answer=str(student_answer or ""),
            top_k=3,
        )
        if prerequisite_candidates:
            candidates = list(prerequisite_candidates)
            retrieval = {
                "candidate_codes": [
                    str(item.get("code") or item.get("runtime_subskill") or "")
                    for item in candidates
                    if isinstance(item, dict)
                ],
                "candidate_descriptions": {
                    str(item.get("code") or item.get("runtime_subskill") or ""): str(
                        item.get("description") or item.get("symptom") or ""
                    )
                    for item in candidates
                    if isinstance(item, dict)
                },
                "candidates": candidates,
                "retrieval_source": "session_override",
                "retrieval_confidence": None,
            }
        else:
            candidates = list(retrieval.get("candidates") or [])
        if not candidates:
            retrieval = retrieve_remediation_candidates(
                skill_id=str(unit_skill_id or ""),
                family_id=str(current_family_id or ""),
                question_text=str(question_text or ""),
                correct_answer=str(expected_answer or ""),
                student_answer=str(student_answer or ""),
                top_k=3,
            )
            candidates = list(retrieval.get("candidates") or [])
        if len(candidates) >= 3:
            classifier = QwenDiagnosticClassifier(role="classifier", timeout=45)
            options = []
            for idx, candidate in enumerate(candidates[:3]):
                option_choice = ["A", "B", "C"][idx]
                options.append(
                    {
                        "choice": option_choice,
                        "code": str(candidate.get("code") or candidate.get("runtime_subskill") or ""),
                        "description": str(candidate.get("description") or candidate.get("symptom") or ""),
                    }
                )
            choice = classifier.classify(
                question_text=str(question_text or ""),
                correct_answer=str(expected_answer or ""),
                student_answer=str(student_answer or ""),
                candidate_options=options,
            )
            if choice is None:
                question_raw = str(question_text or "")
                expected_raw = str(expected_answer or "")
                student_raw = str(student_answer or "")
                if "-" in question_raw or "-" in expected_raw or "-" in student_raw:
                    choice = "A"
                elif "÷" in question_raw or "/" in question_raw or "×" in question_raw:
                    choice = "B"
                else:
                    choice = "C"
                diagnosis_source = "heuristic_choice"
                diagnostic_confidence = 0.62
            else:
                diagnosis_source = "qwen_classifier"
                diagnostic_confidence = 0.72

            choice_index = {"A": 0, "B": 1, "C": 2}.get(str(choice), 0)
            selected = dict(candidates[min(choice_index, len(candidates) - 1)])
            selected_runtime = str(selected.get("runtime_subskill") or "add_sub")
            selected_diag = str(selected.get("diagnosis_label") or "basic_operations")
            selected_concept = str(selected.get("error_concept") or "basic_arithmetic_instability")
            selected_prereq_skill = str(
                selected.get("prereq_skill")
                or selected.get("suggested_prereq_skill")
                or _infer_prereq_skill_from_runtime_subskill(selected_runtime)
            )

            session_state = dict(routing_session or {})
            evidence = dict(session_state.get("diagnostic_evidence") or {})
            next_score = float(evidence.get(selected_runtime, 0.0) or 0.0) + 1.0
            evidence[selected_runtime] = next_score
            session_state["diagnostic_evidence"] = evidence

            threshold = 2.0
            remediation_recommended = next_score >= threshold
            diagnosis_confidence = 0.72 if choice is not None else 0.62
            return {
                "version": "rag_qwen_choice_v1",
                "current_skill": str(current_skill or ""),
                "current_subskill": str(current_subskill or ""),
                "top_concept": selected_concept,
                "error_concept": selected_concept,
                "retrieval_confidence": _norm01(diagnostic_confidence),
                "diagnosis_confidence": _norm01(diagnosis_confidence),
                "suggested_prereq_skill": selected_prereq_skill,
                "suggested_prereq_subskill": selected_diag,
                "selected_prereq_skill": selected_prereq_skill,
                "selected_prereq_subskill": selected_diag,
                "route_type": "rescue_candidate",
                "retrieved_candidates": candidates,
                "retrieval_source": retrieval.get("retrieval_source"),
                "retrieval_confidence": retrieval.get("retrieval_confidence"),
                "diagnostic_choice": choice,
                "diagnostic_confidence": _norm01(diagnostic_confidence),
                "evidence_score": float(next_score),
                "remediation_triggered": remediation_recommended,
                "remediation_recommended": remediation_recommended,
                "diagnosis_source": diagnosis_source,
                "selected_runtime_subskill": selected_runtime,
                "routing_session": session_state,
            }

    error_concept = "basic_arithmetic_instability"
    answer_text = str(student_answer or "").strip()
    expected_text = str(expected_answer or "").strip()
    question_text_norm = str(question_text or "").strip()
    error_type_hint = str((routing_session or {}).get("last_error_type") or "").strip().lower()
    sub = str(current_subskill or "").strip().lower()
    family = str(current_family_id or "").strip().upper()

    if str(current_skill) == "polynomial_arithmetic":
        if family == "F2" and ("-(" in question_text_norm or "bracket" in error_type_hint):
            error_concept = "outer_minus_scope"
        elif "sign_distribution" in sub or "distribution" in error_type_hint:
            error_concept = "sign_distribution"
        elif "family_isomorphism" in sub or "isomorphism" in error_type_hint:
            error_concept = "family_isomorphism_confusion"
        elif family == "F5" and ("expand" in sub or "expand" in error_type_hint):
            error_concept = "binomial_expansion_structure_error"
        elif family == "F11" and ("mixed" in error_type_hint or "transition" in error_type_hint):
            error_concept = "mixed_simplify_transition_error"
        elif "-" in answer_text or "-" in expected_text:
            error_concept = "sign_flip_after_distribution"
        elif "x" in expected_text and "x" in answer_text and answer_text != expected_text:
            error_concept = "combine_like_terms_after_distribution"
        elif "×" in question_text_norm or "*" in question_text_norm:
            error_concept = "coefficient_arithmetic_error"
        else:
            error_concept = "nested_grouping_structure_error"
    elif "-" in answer_text or "-" in expected_text or "sign" in sub:
        error_concept = "negative_sign_handling"
    elif "div" in sub or "/" in answer_text or "/" in expected_text:
        error_concept = "division_misconception"
    elif "fraction" in str(current_skill or ""):
        error_concept = "fraction_as_whole_number_confusion"

    severity = 0.0
    severity += 0.25 if int(fail_streak) >= 2 else 0.0
    severity += 0.25 if _norm01(frustration) >= 0.65 else 0.0
    severity += 0.20 if int(same_skill_streak) >= 5 else 0.0
    retrieval_confidence = _norm01(0.55 + severity)
    diagnosis = map_retrieval_to_diagnosis(
        {
            "top_concept": error_concept,
            "retrieval_confidence": retrieval_confidence,
        },
        current_skill=current_skill,
        current_subskill=current_subskill,
    )
    suggested_prereq_skill = diagnosis.get("suggested_prereq_skill")
    if not suggested_prereq_skill or (current_skill, str(suggested_prereq_skill)) not in ALLOWED_CROSS_SKILL_PATHS:
        diagnosis["route_type"] = "stay"
        diagnosis["suggested_prereq_skill"] = None
        diagnosis["suggested_prereq_subskill"] = None
        diagnosis["selected_prereq_skill"] = None
        diagnosis["selected_prereq_subskill"] = None
    else:
        diagnosis["selected_prereq_skill"] = diagnosis.get("suggested_prereq_skill")
        diagnosis["selected_prereq_subskill"] = diagnosis.get("suggested_prereq_subskill")
    return diagnosis


def build_routing_state(
    *,
    agent_state: dict[str, Any],
    diagnosis: dict[str, Any],
    current_skill: str,
    current_subskill: str,
    routing_session: dict[str, Any] | None,
) -> dict[str, Any]:
    routing_session = routing_session or {}
    mastery = dict(agent_state.get("mastery_by_skill") or {})
    frustration_raw = float(agent_state.get("frustration_index", 0) or 0)
    frustration_norm = _norm01(frustration_raw / 3.0)
    fail_streak = int(agent_state.get("fail_streak", 0) or 0)
    same_skill_streak = int(agent_state.get("same_skill_streak", 0) or 0)
    last_is_correct = 1 if bool(agent_state.get("last_is_correct", False)) else 0
    diag_conf = _norm01(diagnosis.get("diagnosis_confidence", 0.0))

    return {
        "mastery": {
            "integer": mastery.get("integer_arithmetic", 0.45),
            "fraction": mastery.get("fraction_arithmetic", 0.45),
            "radical": mastery.get("radical_arithmetic", 0.45),
            "polynomial": mastery.get("polynomial_arithmetic", 0.45),
        },
        "affect": {
            "frustration": frustration_norm,
            "fail_streak": fail_streak,
            "same_skill_streak": same_skill_streak,
            "last_is_correct": last_is_correct,
        },
        "current_task": {
            "skill": current_skill,
            "subskill": current_subskill,
        },
        "diagnostic_signal": {
            "error_concept": diagnosis.get("error_concept"),
            "retrieval_confidence": _norm01(diagnosis.get("retrieval_confidence", 0.0)),
            "diagnosis_confidence": diag_conf,
            "suggested_prereq_skill": diagnosis.get("suggested_prereq_skill"),
            "suggested_prereq_subskill": diagnosis.get("suggested_prereq_subskill"),
            "rescue_recommended": 1 if (diag_conf >= 0.8 and diagnosis.get("suggested_prereq_skill")) else 0,
        },
        "routing_context": {
            "in_remediation": 1 if bool(routing_session.get("in_remediation", False)) else 0,
            "origin_skill": routing_session.get("origin_skill"),
            "remediation_skill": routing_session.get("remediation_skill"),
            "remediation_step_count": int(routing_session.get("steps_taken", 0) or 0),
            "recent_routing_count": int(routing_session.get("recent_routing_count", 0) or 0),
            "cooldown_active": 1 if bool(routing_session.get("cooldown_active", False)) else 0,
        },
    }


def compute_cross_skill_trigger(*, fail_streak: int, frustration: float, same_skill_streak: int, diagnosis: dict[str, Any], current_skill: str) -> bool:
    can_route_cross_skill = (
        int(fail_streak) >= 2
        or float(frustration) >= 0.65
        or int(same_skill_streak) >= 5
    )
    valid_diagnosis = (
        bool(diagnosis.get("suggested_prereq_skill"))
        and str(diagnosis.get("suggested_prereq_skill")) != str(current_skill)
    )
    if not (can_route_cross_skill and valid_diagnosis):
        return False
    to_skill = str(diagnosis.get("suggested_prereq_skill"))
    return (str(current_skill), to_skill) in ALLOWED_CROSS_SKILL_PATHS


def build_action_mask(
    *,
    in_remediation: bool,
    remediation_step_count: int,
    lock_min_steps: int,
    cross_skill_trigger: bool,
    return_ready: bool = False,
) -> dict[str, bool]:
    mask = {ROUTE_STAY: True, ROUTE_REMEDIATE: False, ROUTE_RETURN: False}
    if in_remediation:
        if int(remediation_step_count) < int(lock_min_steps):
            return mask
        mask[ROUTE_RETURN] = bool(return_ready)
        return mask
    if cross_skill_trigger:
        mask[ROUTE_REMEDIATE] = True
    return mask


def start_remediation_session(
    *,
    origin_skill: str,
    origin_subskill: str,
    origin_family: str = "",
    remediation_skill: str,
    remediation_subskill: str,
    entry_reason: str,
    entry_confidence: float,
) -> dict[str, Any]:
    return {
        "in_remediation": True,
        "origin_skill": origin_skill,
        "origin_subskill": origin_subskill,
        "origin_family": str(origin_family or ""),
        "remediation_skill": remediation_skill,
        "remediation_subskill": remediation_subskill,
        "lock_min_steps": 2,
        "lock_max_steps": 4,
        "steps_taken": 0,
        "entry_reason": entry_reason,
        "entry_confidence": _norm01(entry_confidence),
        "recent_results": [],
        "remediation_mastery": 0.0,
        "bridge_remaining": 0,
        "recent_routing_count": 1,
        "cooldown_active": False,
    }


def should_return_from_remediation(routing_session: dict[str, Any] | None) -> tuple[bool, str]:
    s = routing_session or {}
    mastery = _norm01(s.get("remediation_mastery", 0.0))
    recent_results = list(s.get("recent_results") or [])
    recent_correct = bool(recent_results[-1]) if recent_results else bool(s.get("last_result", False))
    high_threshold = _norm01(s.get("return_mastery_threshold", 0.85), 0.85)
    low_threshold = _norm01(
        s.get("return_mastery_with_recent_correct_threshold", 0.75),
        0.75,
    )
    if mastery >= high_threshold:
        return True, "ready_by_mastery_threshold"
    if mastery >= low_threshold and recent_correct:
        return True, "ready_by_mastery_recent_correct_threshold"
    return False, "not_ready"


def _bridge_subskill(origin_skill: str, remediation_subskill: str) -> str:
    if origin_skill == "polynomial_arithmetic":
        if remediation_subskill == "sign_handling":
            return "sign_distribution"
        return "combine_like_terms"
    if origin_skill == "fraction_arithmetic":
        if remediation_subskill == "mul_div":
            return "fraction_mul_div"
        return "equivalent_fraction_scaling"
    return remediation_subskill


def apply_routing_action(
    *,
    action: str,
    current_skill: str,
    current_subskill: str,
    current_family: str = "",
    diagnosis: dict[str, Any],
    routing_session: dict[str, Any] | None,
) -> tuple[dict[str, Any], str, str | None]:
    s = dict(routing_session or {})
    bridge_subskill: str | None = None
    action = str(action or ROUTE_STAY)

    if action == ROUTE_REMEDIATE and not s.get("in_remediation", False):
        rem_skill = str(diagnosis.get("suggested_prereq_skill") or "")
        rem_sub_raw = str(diagnosis.get("suggested_prereq_subskill") or "")
        rem_sub = normalize_runtime_subskill(
            rem_sub_raw,
            target_agent_skill=rem_skill,
            origin_agent_skill=current_skill,
            error_concept=str(diagnosis.get("error_concept") or ""),
        )
        if rem_skill:
            s = start_remediation_session(
                origin_skill=current_skill,
                origin_subskill=current_subskill,
                origin_family=current_family,
                remediation_skill=rem_skill,
                remediation_subskill=rem_sub or "add_sub",
                entry_reason=str(diagnosis.get("error_concept") or "unknown"),
                entry_confidence=float(diagnosis.get("diagnosis_confidence", 0.0) or 0.0),
            )
            return s, rem_skill, rem_sub or None

    if s.get("in_remediation", False):
        if action == ROUTE_RETURN:
            origin_skill = str(s.get("origin_skill") or current_skill)
            rem_sub = normalize_runtime_subskill(
                str(s.get("remediation_subskill") or ""),
                target_agent_skill=str(s.get("remediation_skill") or ""),
                origin_agent_skill=origin_skill,
                error_concept=str(s.get("entry_reason") or ""),
            )
            s["in_remediation"] = False
            s["cooldown_active"] = True
            s["bridge_remaining"] = 2
            bridge_subskill = _bridge_subskill(origin_skill, rem_sub)
            return s, origin_skill, bridge_subskill
        rem_skill = str(s.get("remediation_skill") or current_skill)
        rem_sub = normalize_runtime_subskill(
            str(s.get("remediation_subskill") or ""),
            target_agent_skill=rem_skill,
            origin_agent_skill=str(s.get("origin_skill") or current_skill),
            error_concept=str(s.get("entry_reason") or ""),
        )
        if rem_sub and rem_sub != str(s.get("remediation_subskill") or ""):
            s["remediation_subskill"] = rem_sub
        return s, rem_skill, rem_sub or None

    if int(s.get("bridge_remaining", 0) or 0) > 0:
        s["bridge_remaining"] = int(s.get("bridge_remaining", 0) or 0) - 1
        origin_skill = str(s.get("origin_skill") or current_skill)
        rem_sub = str(s.get("remediation_subskill") or "")
        bridge_subskill = _bridge_subskill(origin_skill, rem_sub)
        if int(s.get("bridge_remaining", 0) or 0) <= 0:
            s["cooldown_active"] = False
        return s, origin_skill, bridge_subskill

    return s, current_skill, None


