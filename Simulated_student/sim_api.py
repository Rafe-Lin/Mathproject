# -*- coding: utf-8 -*-
"""
=============================================================================
模組名稱 (Module Name): sim_api.py
功能說明 (Description): Flask Blueprint API — 提供 REST 端口讓外部程式觸發模擬。
                        不需要登入驗證（本地開發用途）。
=============================================================================
"""
from __future__ import annotations

import json
import os
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any

from flask import Blueprint, jsonify, request

sim_bp = Blueprint("sim", __name__)

# Cache of completed simulation results (in-memory; lost on restart)
_SIM_RESULTS: list[dict[str, Any]] = []


@sim_bp.route("/api/sim/run", methods=["POST"])
def sim_run():
    """
    Run a simulated student session.

    Request JSON body:
    {
        "skill_id":            str   (optional, default polynomial),
        "mode":                str   (optional, "teaching" or "assessment"),
        "ability":             str   (optional, "weak" / "medium" / "strong"),
        "max_steps":           int   (optional, default 30),
        "answer_strategy":     str   (optional, "random" / "fixed" / "llm"),
        "correct_probability": float (optional, override ability preset),
        "fixed_pattern":       list  (optional, e.g. [true, true, false]),
        "model_name":          str   (optional, for LLM strategy),
        "student_label":       str   (optional, label for output file),
        "seed":                int   (optional, RNG seed)
    }
    """
    try:
        data = request.get_json(silent=True) or {}

        from Simulated_student.sim_core import SimulatedStudent, DEFAULT_SKILL_ID

        skill_id = str(data.get("skill_id", DEFAULT_SKILL_ID) or DEFAULT_SKILL_ID).strip()
        mode = str(data.get("mode", "teaching") or "teaching").strip()
        ability = str(data.get("ability", "medium") or "medium").strip()
        max_steps = int(data.get("max_steps", 30) or 30)
        answer_strategy = str(data.get("answer_strategy", "random") or "random").strip()
        correct_probability = data.get("correct_probability")
        if correct_probability is not None:
            correct_probability = float(correct_probability)
        fixed_pattern = data.get("fixed_pattern")
        student_label = str(data.get("student_label", "") or "").strip()
        seed = data.get("seed")
        if seed is not None:
            seed = int(seed)

        # LLM judge setup
        llm_judge = None
        if answer_strategy == "llm":
            from Simulated_student.sim_llm_judge import LLMJudge
            model_name = str(data.get("model_name", "") or "").strip()
            llm_judge = LLMJudge(
                model=model_name if model_name else None,
                ability=ability,
            )

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
        log_path = sim.save_log()

        result = {
            "status": "completed",
            "metadata": {
                "student_label": sim.student_label,
                "skill_id": sim.skill_id,
                "mode": sim.mode,
                "ability": sim.ability,
                "correct_probability": sim.correct_probability,
                "answer_strategy": sim.answer_strategy,
                "session_id": sim.session_id,
            },
            "summary": sim._build_result_summary(),
            "steps": sim.steps,
            "log_path": str(log_path),
        }

        _SIM_RESULTS.append({
            "session_id": sim.session_id,
            "student_label": sim.student_label,
            "mode": mode,
            "ability": ability,
            "total_steps": len(sim.steps),
            "final_apr": sim.steps[-1]["current_apr"] if sim.steps else 0,
            "accuracy": result["summary"].get("accuracy", 0),
            "log_path": str(log_path),
            "created_at": datetime.utcnow().isoformat(),
        })

        return jsonify(result)

    except Exception as exc:
        tb = traceback.format_exc()
        return jsonify({
            "status": "error",
            "error": str(exc),
            "traceback": tb,
        }), 500


@sim_bp.route("/api/sim/results", methods=["GET"])
def sim_results():
    """List all completed simulation results (from current server session)."""
    return jsonify({
        "count": len(_SIM_RESULTS),
        "results": list(reversed(_SIM_RESULTS)),
    })


@sim_bp.route("/api/sim/presets", methods=["GET"])
def sim_presets():
    """Return available ability presets."""
    from Simulated_student.sim_core import ABILITY_PRESETS, DEFAULT_SKILL_ID
    return jsonify({
        "ability_presets": ABILITY_PRESETS,
        "default_skill_id": DEFAULT_SKILL_ID,
        "supported_strategies": ["random", "fixed", "llm"],
        "supported_modes": ["teaching", "assessment"],
    })
