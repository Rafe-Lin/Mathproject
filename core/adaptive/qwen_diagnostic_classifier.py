# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import re
from typing import Any

from core.ai_wrapper import call_ai_with_retry, get_ai_client


class QwenDiagnosticClassifier:
    """Qwen 8B diagnostic classifier adapter (replaceable backend)."""

    def __init__(self, role: str = "classifier", timeout: int = 45):
        self.role = role
        self.timeout = timeout

    def build_prompt(
        self,
        *,
        question_text: str,
        correct_answer: str,
        student_answer: str,
        candidate_options: list[dict[str, Any]],
    ) -> str:
        lines = [
            "你是數學補救診斷分類器。",
            "只允許輸出 A/B/C 三選一，不得輸出推理過程。",
            "請只輸出 JSON：{\"choice\":\"A|B|C\"}",
            f"題目: {question_text}",
            f"正確答案: {correct_answer}",
            f"學生錯誤答案: {student_answer}",
            "候選子技能：",
        ]
        for idx, option in enumerate(candidate_options[:3]):
            default_choice = ["A", "B", "C"][idx]
            choice = str(option.get("choice") or default_choice).strip().upper()
            code = str(option.get("code") or option.get("runtime_subskill") or "")
            description = str(option.get("description") or option.get("symptom") or "")
            lines.append(f"{choice}. {code} | {description}")
        return "\n".join(lines)

    def parse_choice(self, raw_output: str) -> str | None:
        raw = str(raw_output or "").strip()
        if not raw:
            return None
        try:
            payload = json.loads(raw)
            if isinstance(payload, dict):
                choice = str(payload.get("choice", "")).strip().upper()
                if choice in {"A", "B", "C"}:
                    return choice
        except Exception:
            pass
        match = re.search(r"\b([ABC])\b", raw.upper())
        if match:
            return match.group(1)
        return None

    def classify(
        self,
        *,
        question_text: str,
        correct_answer: str,
        student_answer: str,
        candidate_options: list[dict[str, Any]],
    ) -> str | None:
        if len(candidate_options) < 3:
            return None
        prompt = self.build_prompt(
            question_text=question_text,
            correct_answer=correct_answer,
            student_answer=student_answer,
            candidate_options=candidate_options,
        )
        try:
            client = get_ai_client(self.role)
            response = call_ai_with_retry(
                client,
                prompt,
                max_retries=1,
                retry_delay=0,
                verbose=False,
                timeout=self.timeout,
            )
            raw_text = str(getattr(response, "text", "") or "")
            return self.parse_choice(raw_text)
        except Exception:
            # TODO: replace with explicit model circuit-breaker / telemetry when model backend is stable.
            return None
