from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .rag_diagnosis_mapping import map_retrieval_to_diagnosis


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
}

ALLOWED_CROSS_SKILL_PATHS = {
    ("polynomial_arithmetic", "integer_arithmetic"),
    ("fraction_arithmetic", "integer_arithmetic"),
}


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
    student_answer: str = "",
    expected_answer: str = "",
    is_correct: bool | None = None,
    fail_streak: int = 0,
    frustration: float = 0.0,
    same_skill_streak: int = 0,
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

    error_concept = "basic_arithmetic_instability"
    answer_text = str(student_answer or "").strip()
    expected_text = str(expected_answer or "").strip()
    sub = str(current_subskill or "").strip().lower()

    if "-" in answer_text or "-" in expected_text or "sign" in sub:
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
        _norm01(diagnosis.get("diagnosis_confidence", 0.0)) >= 0.80
        and bool(diagnosis.get("suggested_prereq_skill"))
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
) -> dict[str, bool]:
    mask = {ROUTE_STAY: True, ROUTE_REMEDIATE: False, ROUTE_RETURN: False}
    if in_remediation:
        if int(remediation_step_count) < int(lock_min_steps):
            return mask
        mask[ROUTE_RETURN] = True
        return mask
    if cross_skill_trigger:
        mask[ROUTE_REMEDIATE] = True
    return mask


def start_remediation_session(
    *,
    origin_skill: str,
    origin_subskill: str,
    remediation_skill: str,
    remediation_subskill: str,
    entry_reason: str,
    entry_confidence: float,
) -> dict[str, Any]:
    return {
        "in_remediation": True,
        "origin_skill": origin_skill,
        "origin_subskill": origin_subskill,
        "remediation_skill": remediation_skill,
        "remediation_subskill": remediation_subskill,
        "lock_min_steps": 2,
        "lock_max_steps": 4,
        "steps_taken": 0,
        "entry_reason": entry_reason,
        "entry_confidence": _norm01(entry_confidence),
        "recent_results": [],
        "bridge_remaining": 0,
        "recent_routing_count": 1,
        "cooldown_active": False,
    }


def should_return_from_remediation(routing_session: dict[str, Any] | None) -> tuple[bool, str]:
    s = routing_session or {}
    steps_taken = int(s.get("steps_taken", 0) or 0)
    lock_max_steps = int(s.get("lock_max_steps", 4) or 4)
    recent_results = list(s.get("recent_results") or [])
    if steps_taken >= lock_max_steps:
        return True, "forced_by_lock_max"
    if steps_taken >= 2 and recent_results:
        acc = sum(1 for x in recent_results[-2:] if bool(x)) / float(min(2, len(recent_results[-2:])))
        if acc >= 0.8:
            return True, "ready_by_recent_accuracy"
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
    diagnosis: dict[str, Any],
    routing_session: dict[str, Any] | None,
) -> tuple[dict[str, Any], str, str | None]:
    s = dict(routing_session or {})
    bridge_subskill: str | None = None
    action = str(action or ROUTE_STAY)

    if action == ROUTE_REMEDIATE and not s.get("in_remediation", False):
        rem_skill = str(diagnosis.get("suggested_prereq_skill") or "")
        rem_sub = str(diagnosis.get("suggested_prereq_subskill") or "")
        if rem_skill:
            s = start_remediation_session(
                origin_skill=current_skill,
                origin_subskill=current_subskill,
                remediation_skill=rem_skill,
                remediation_subskill=rem_sub or "add_sub",
                entry_reason=str(diagnosis.get("error_concept") or "unknown"),
                entry_confidence=float(diagnosis.get("diagnosis_confidence", 0.0) or 0.0),
            )
            return s, rem_skill, rem_sub or None

    if s.get("in_remediation", False):
        if action == ROUTE_RETURN:
            origin_skill = str(s.get("origin_skill") or current_skill)
            rem_sub = str(s.get("remediation_subskill") or "")
            s["in_remediation"] = False
            s["cooldown_active"] = True
            s["bridge_remaining"] = 2
            bridge_subskill = _bridge_subskill(origin_skill, rem_sub)
            return s, origin_skill, bridge_subskill
        rem_skill = str(s.get("remediation_skill") or current_skill)
        rem_sub = str(s.get("remediation_subskill") or "")
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
