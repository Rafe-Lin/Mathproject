# -*- coding: utf-8 -*-
"""
=============================================================================
模組名稱 (Module Name): sim_core.py
功能說明 (Description): 模擬學生核心引擎 — 無 GUI 驅動自適應 session，
                        直接呼叫 submit_and_get_next()，紀錄每步能力值。
=============================================================================
"""
from __future__ import annotations

import json
import os
import random
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

# ---------------------------------------------------------------------------
# Path bootstrap – ensure project root is importable
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ---------------------------------------------------------------------------
# Answer-strategy presets for different ability levels
# ---------------------------------------------------------------------------
ABILITY_PRESETS: dict[str, dict[str, Any]] = {
    "weak": {
        "correct_probability": 0.30,
        "description": "弱學生 — 正確率 30 %，容易連續犯錯觸發補救",
    },
    "medium": {
        "correct_probability": 0.55,
        "description": "中等學生 — 正確率 55 %，偶爾觸發補救",
    },
    "strong": {
        "correct_probability": 0.85,
        "description": "強學生 — 正確率 85 %，幾乎不進入補救",
    },
}

# Default target skill for polynomial arithmetic (the most complete adaptive skill)
DEFAULT_SKILL_ID = "jh_數學2上_FourArithmeticOperationsOfPolynomial"

# Default teaching mainline family sequence (from textbook_progression.py)
# Used by BaselineStudent to simulate fixed-order, non-adaptive learning.
TEACHING_MAINLINE_SEQUENCE = ["F1", "F2", "F5", "F11", "F9", "F10"]


# ──────────────────────────────────────────────────────────────────────────────
# SimulatedStudent
# ──────────────────────────────────────────────────────────────────────────────
class SimulatedStudent:
    """
    Drives one full adaptive session without a GUI.

    Usage
    -----
    >>> from Simulated_student.sim_core import SimulatedStudent
    >>> sim = SimulatedStudent(skill_id="jh_...", mode="teaching", ability="medium")
    >>> result = sim.run_session(max_steps=20)
    >>> sim.save_log("./output.json")
    """

    def __init__(
        self,
        *,
        skill_id: str = DEFAULT_SKILL_ID,
        mode: str = "teaching",
        ability: str = "medium",
        correct_probability: float | None = None,
        answer_strategy: str = "random",
        fixed_pattern: list[bool] | None = None,
        llm_judge: Any | None = None,
        student_label: str = "",
        seed: int | None = None,
    ):
        """
        Parameters
        ----------
        skill_id : str
            System skill id sent to the adaptive engine.
        mode : str
            "teaching" or "assessment".
        ability : str
            One of "weak", "medium", "strong" – picks a preset correct_probability.
        correct_probability : float or None
            Override probability (0‒1). Takes precedence over *ability* preset.
        answer_strategy : str
            "random" | "fixed" | "llm"
        fixed_pattern : list[bool] or None
            Cyclic T/F pattern for *fixed* strategy, e.g. [True, True, False].
        llm_judge : object or None
            An instance of ``LLMJudge`` (from sim_llm_judge.py).
        student_label : str
            For labelling output files when running batches.
        seed : int or None
            RNG seed for reproducibility.
        """
        self.skill_id = skill_id
        self.mode = mode
        self.ability = ability
        self.answer_strategy = answer_strategy
        self.fixed_pattern = fixed_pattern or [True, True, False]
        self.llm_judge = llm_judge
        self.student_label = student_label or f"sim_{ability}_{mode}"
        self.session_id = str(uuid.uuid4())

        # Resolve correct probability
        if correct_probability is not None:
            self.correct_probability = correct_probability
        elif ability in ABILITY_PRESETS:
            self.correct_probability = ABILITY_PRESETS[ability]["correct_probability"]
        else:
            self.correct_probability = 0.55

        # RNG
        self._rng = random.Random(seed)

        # --- runtime state ---
        self.steps: list[dict[str, Any]] = []
        self._student_id: int | None = None
        self._app = None  # Flask app context

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def run_session(self, max_steps: int = 30) -> dict[str, Any]:
        """Run a full adaptive session, return summary + step log."""
        self._ensure_app_context()
        self._ensure_student_user()

        from core.adaptive.session_engine import submit_and_get_next

        routing_state: dict[str, Any] = {}
        session_id = self.session_id
        last_family_id: str | None = None
        last_subskills: list[str] = []
        completed = False

        for step in range(max_steps):
            # --- Build payload for this step ---
            payload: dict[str, Any] = {
                "student_id": self._student_id,
                "session_id": session_id,
                "step_number": step,
                "skill_id": self.skill_id,
                "mode": self.mode,
                "routing_state": routing_state,
            }

            if step > 0 and last_family_id:
                # Decide whether the simulated student got the *previous* question right
                is_correct = self._decide_answer(
                    question_data=self.steps[-1].get("question_data", {}),
                    step=step,
                )
                payload["is_correct"] = is_correct
                payload["last_family_id"] = last_family_id
                payload["last_subskills"] = last_subskills
                payload["user_answer"] = "(模擬作答)"
                payload["last_expected_answer"] = self.steps[-1].get("question_data", {}).get("correct_answer", "")
                payload["last_question_text"] = self.steps[-1].get("question_data", {}).get("question_text", "")
            else:
                is_correct = None  # first call — no previous answer

            # --- Call engine ---
            try:
                response = submit_and_get_next(payload)
            except Exception as exc:
                print(f"[SimStudent] engine error at step {step}: {exc}", flush=True)
                break

            # --- Extract key fields ---
            session_id = response.get("session_id", session_id)
            completed = bool(response.get("completed", False))

            new_q = response.get("new_question_data", {}) or {}
            target_family_id = str(response.get("target_family_id", "") or "")
            target_subskills = response.get("target_subskills", []) or []

            # Build mastery snapshot
            mastery_snapshot = self._extract_mastery(response)

            step_record: dict[str, Any] = {
                "step_number": step,
                "session_id": session_id,
                "is_correct": is_correct,
                "target_family_id": target_family_id,
                "target_subskills": target_subskills,
                "current_apr": response.get("current_apr", 0.0),
                "frustration_index": response.get("frustration_index", 0),
                "ppo_strategy": response.get("ppo_strategy", 0),
                "current_mode": response.get("current_mode", response.get("post_mode", "mainline")),
                "display_mode": response.get("display_mode", ""),
                "display_family": response.get("display_family", ""),
                "display_skill": response.get("display_skill", ""),
                "remediation_triggered": bool(response.get("remediation_triggered_final", False)),
                "return_to_mainline": bool(response.get("return_to_mainline", False)),
                "completed": completed,
                "unit_completed": bool(response.get("unit_completed", False)),
                "scenario_stage": response.get("scenario_stage", ""),
                "mastery_snapshot": mastery_snapshot,
                "routing_summary": response.get("routing_summary", {}),
                "question_data": {
                    "question_text": new_q.get("question_text", ""),
                    "correct_answer": new_q.get("correct_answer", new_q.get("answer", "")),
                    "family_name": new_q.get("family_name", ""),
                    "source": new_q.get("source", ""),
                },
                "timestamp": datetime.utcnow().isoformat(),
            }

            # If LLM strategy, also capture the LLM response detail
            if self.answer_strategy == "llm" and step > 0 and hasattr(self, "_last_llm_detail"):
                step_record["llm_detail"] = self._last_llm_detail

            self.steps.append(step_record)

            # Advance pointers
            last_family_id = target_family_id
            last_subskills = list(target_subskills)
            routing_state = response.get("routing_state", routing_state)

            if completed:
                # Record diagnostic report if available
                diag_report = response.get("diagnostic_report")
                if diag_report:
                    step_record["diagnostic_report"] = diag_report
                break

        return self._build_result_summary()

    def save_log(self, output_path: str | Path | None = None) -> Path:
        """Write step log to JSON file."""
        if output_path is None:
            output_dir = Path(__file__).parent / "outputs"
            output_dir.mkdir(parents=True, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = output_dir / f"sim_{self.student_label}_{ts}.json"
        else:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "metadata": {
                "student_label": self.student_label,
                "skill_id": self.skill_id,
                "mode": self.mode,
                "ability": self.ability,
                "correct_probability": self.correct_probability,
                "answer_strategy": self.answer_strategy,
                "session_id": self.session_id,
                "total_steps": len(self.steps),
                "created_at": datetime.utcnow().isoformat(),
            },
            "steps": self.steps,
            "summary": self._build_result_summary(),
        }
        with open(output_path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)

        print(f"[SimStudent] Log saved → {output_path}", flush=True)
        return output_path

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _decide_answer(self, question_data: dict, step: int) -> bool:
        """Decide is_correct for the *current* question based on strategy."""
        if self.answer_strategy == "fixed":
            idx = (step - 1) % len(self.fixed_pattern)
            return self.fixed_pattern[idx]

        if self.answer_strategy == "llm" and self.llm_judge is not None:
            try:
                result = self.llm_judge.judge(
                    question_text=question_data.get("question_text", ""),
                    correct_answer=question_data.get("correct_answer", ""),
                    subskills=", ".join(self.steps[-1].get("target_subskills", [])),
                    family_name=question_data.get("family_name", ""),
                )
                self._last_llm_detail = result
                return bool(result.get("is_correct", False))
            except Exception as exc:
                print(f"[SimStudent] LLM judge error: {exc}; falling back to random", flush=True)

        # Default: random strategy
        return self._rng.random() < self.correct_probability

    def _extract_mastery(self, response: dict) -> dict[str, Any]:
        """Extract mastery-related values from the engine response."""
        selection_debug = {}
        for key in ("selection_debug",):
            if isinstance(response.get(key), dict):
                selection_debug = response[key]
                break

        return {
            "apr": response.get("current_apr", 0.0),
            "frustration_index": response.get("frustration_index", 0),
            "ppo_strategy": response.get("ppo_strategy", 0),
            "remediation_mastery": response.get("remediation_mastery", 0.0),
            "local_apr": selection_debug.get("local_apr", response.get("current_apr", 0.0)),
            "in_remediation": bool(
                response.get("current_mode", "mainline") == "remediation"
                or (response.get("routing_state") or {}).get("in_remediation", False)
            ),
        }

    def _build_result_summary(self) -> dict[str, Any]:
        """Build a summary dict from collected steps."""
        if not self.steps:
            return {"total_steps": 0}

        correct_count = sum(1 for s in self.steps if s.get("is_correct") is True)
        answered_count = sum(1 for s in self.steps if s.get("is_correct") is not None)
        accuracy = correct_count / answered_count if answered_count > 0 else 0.0

        aprs = [s["current_apr"] for s in self.steps]
        families_visited = list(dict.fromkeys(
            s["target_family_id"] for s in self.steps if s.get("target_family_id")
        ))
        remediation_steps = [
            s["step_number"] for s in self.steps if s.get("remediation_triggered")
        ]
        return_steps = [
            s["step_number"] for s in self.steps if s.get("return_to_mainline")
        ]

        return {
            "total_steps": len(self.steps),
            "answered_steps": answered_count,
            "correct_count": correct_count,
            "accuracy": round(accuracy, 4),
            "final_apr": aprs[-1] if aprs else 0.0,
            "min_apr": min(aprs) if aprs else 0.0,
            "max_apr": max(aprs) if aprs else 0.0,
            "families_visited": families_visited,
            "unique_families_count": len(set(families_visited)),
            "remediation_trigger_steps": remediation_steps,
            "return_to_mainline_steps": return_steps,
            "completed": self.steps[-1].get("completed", False) if self.steps else False,
            "unit_completed": self.steps[-1].get("unit_completed", False) if self.steps else False,
        }

    # ------------------------------------------------------------------
    # Flask app context management
    # ------------------------------------------------------------------
    def _ensure_app_context(self):
        """Push a Flask app context so that DB operations work."""
        if self._app is not None:
            return
        from app import create_app
        self._app = create_app()
        self._ctx = self._app.app_context()
        self._ctx.push()

    def _ensure_student_user(self):
        """Create or fetch a simulated student user in the DB."""
        from models import User, db
        from werkzeug.security import generate_password_hash

        username = f"sim_student_{self.ability}_{self.mode}"
        user = db.session.query(User).filter_by(username=username).first()
        if user is None:
            user = User(
                username=username,
                password_hash=generate_password_hash("sim_test_1234", method="pbkdf2:sha256"),
                role="student",
            )
            db.session.add(user)
            db.session.commit()
            print(f"[SimStudent] Created user '{username}' (id={user.id})", flush=True)
        else:
            print(f"[SimStudent] Using existing user '{username}' (id={user.id})", flush=True)

        self._student_id = user.id


# ──────────────────────────────────────────────────────────────────────────────
# Convenience function: run one simulation (for API / scripting)
# ──────────────────────────────────────────────────────────────────────────────
def run_simulation(
    *,
    skill_id: str = DEFAULT_SKILL_ID,
    mode: str = "teaching",
    ability: str = "medium",
    max_steps: int = 30,
    answer_strategy: str = "random",
    correct_probability: float | None = None,
    fixed_pattern: list[bool] | None = None,
    llm_judge: Any | None = None,
    student_label: str = "",
    seed: int | None = None,
    save: bool = True,
) -> dict[str, Any]:
    """
    Run a single simulation and optionally save the log.

    Returns
    -------
    dict with keys: metadata, steps, summary, log_path (if saved).
    """
    sim = SimulatedStudent(
        skill_id=skill_id,
        mode=mode,
        ability=ability,
        correct_probability=correct_probability,
        answer_strategy=answer_strategy,
        fixed_pattern=fixed_pattern,
        llm_judge=llm_judge,
        student_label=student_label,
        seed=seed,
    )
    sim.run_session(max_steps=max_steps)
    log_path = None
    if save:
        log_path = sim.save_log()

    return {
        "metadata": {
            "student_label": sim.student_label,
            "skill_id": sim.skill_id,
            "mode": sim.mode,
            "ability": sim.ability,
            "correct_probability": sim.correct_probability,
            "answer_strategy": sim.answer_strategy,
            "session_id": sim.session_id,
        },
        "steps": sim.steps,
        "summary": sim._build_result_summary(),
        "log_path": str(log_path) if log_path else None,
    }


# ──────────────────────────────────────────────────────────────────────────────
# BaselineStudent — non-adaptive, fixed-sequence control group
# ──────────────────────────────────────────────────────────────────────────────
class BaselineStudent:
    """
    Simulates a student who follows the textbook family sequence in fixed
    order **without** any adaptive routing, remediation, or PPO policy.

    Uses the same APR heuristic (akt_adapter.update_local_apr) so the APR
    curve is directly comparable to the adaptive SimulatedStudent.

    This serves as the **control group** for the "adaptive vs. baseline"
    comparison chart.
    """

    def __init__(
        self,
        *,
        ability: str = "medium",
        correct_probability: float | None = None,
        family_sequence: list[str] | None = None,
        seed: int | None = None,
        student_label: str = "",
    ):
        self.ability = ability
        self.family_sequence = family_sequence or list(TEACHING_MAINLINE_SEQUENCE)
        self.student_label = student_label or f"baseline_{ability}"

        if correct_probability is not None:
            self.correct_probability = correct_probability
        elif ability in ABILITY_PRESETS:
            self.correct_probability = ABILITY_PRESETS[ability]["correct_probability"]
        else:
            self.correct_probability = 0.55

        self._rng = random.Random(seed)
        self.steps: list[dict[str, Any]] = []

    def run_session(self, max_steps: int = 30) -> list[dict[str, Any]]:
        """
        Run a baseline (non-adaptive) session.

        The student simply goes through the family sequence in order,
        one question per family, cycling if max_steps > len(sequence).
        APR is updated with the same heuristic as the adaptive engine.
        """
        from core.adaptive.akt_adapter import bootstrap_local_apr, update_local_apr

        apr = bootstrap_local_apr()  # 0.45
        frustration = 0

        for step in range(max_steps):
            family_idx = step % len(self.family_sequence)
            family_id = self.family_sequence[family_idx]

            # Decide correctness with same probability
            is_correct = self._rng.random() < self.correct_probability

            # Update APR with the SAME heuristic as the adaptive engine
            if step > 0:
                apr = update_local_apr(
                    previous_apr=apr,
                    is_correct=is_correct,
                    frustration_index=frustration,
                    subskill_count=1,
                )

            # Update frustration (same logic as session_engine._compute_frustration)
            if is_correct:
                frustration = 0
            else:
                frustration += 1

            self.steps.append({
                "step_number": step,
                "is_correct": is_correct if step > 0 else None,
                "target_family_id": family_id,
                "current_apr": apr,
                "frustration_index": frustration,
                "current_mode": "mainline",
                "remediation_triggered": False,
                "return_to_mainline": False,
            })

        return self.steps

