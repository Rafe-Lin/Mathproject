# -*- coding: utf-8 -*-
"""
=============================================================================
模組名稱 (Module Name): sim_llm_judge.py
功能說明 (Description): LLM-as-a-judge 模組 — 透過 Ollama 本地模型模擬學生作答。
                        以 "LLM as a judge" 設計提示詞，讓 AI 模擬不同能力的國中生。
=============================================================================
"""
from __future__ import annotations

import json
import re
import time
from typing import Any

import requests


# ─── Default configuration ─────────────────────────────────────────────────
DEFAULT_MODEL = "qwen2.5:3b"
DEFAULT_API_URL = "http://localhost:11434/api/generate"

# ─── Ability-level prompt modifiers ────────────────────────────────────────
ABILITY_PROMPT_MAP: dict[str, str] = {
    "weak": (
        "你是一個數學基礎**比較薄弱**的國中生。"
        "你經常在正負號判讀、括號展開、同類項合併上犯錯。"
        "你遇到較複雜的題目時容易粗心或直接猜答案。"
        "你的正確率大約只有 30%。"
    ),
    "medium": (
        "你是一個數學能力**中等**的國中生。"
        "你對基礎運算大致理解，但在多步驟計算或混合運算時偶爾犯錯。"
        "你有時會忘記分配負號或搞混運算順序。"
        "你的正確率大約是 55%。"
    ),
    "strong": (
        "你是一個數學能力**很強**的國中生。"
        "你對整數、分數、多項式四則運算都很熟練。"
        "你很少犯計算錯誤，但偶爾在非常複雜的題目上可能失誤。"
        "你的正確率大約是 85%。"
    ),
}


class LLMJudge:
    """
    Uses a local Ollama model to simulate a student answering math questions.

    The prompt follows "LLM-as-a-judge" design: the model is asked to role-play
    a student of a given ability level, show reasoning, and return a structured
    JSON response.

    Example
    -------
    >>> judge = LLMJudge(ability="medium")
    >>> result = judge.judge(
    ...     question_text="計算 3x + 2x",
    ...     correct_answer="5x",
    ...     subskills="like_term_combination",
    ...     family_name="同類項合併",
    ... )
    >>> print(result["is_correct"], result["student_answer"])
    """

    def __init__(
        self,
        *,
        model: str = DEFAULT_MODEL,
        api_url: str = DEFAULT_API_URL,
        ability: str = "medium",
        temperature: float = 0.7,
        timeout: int = 60,
    ):
        self.model = model
        self.api_url = api_url
        self.ability = ability
        self.temperature = temperature
        self.timeout = timeout
        self._ability_prompt = ABILITY_PROMPT_MAP.get(ability, ABILITY_PROMPT_MAP["medium"])

    def judge(
        self,
        question_text: str,
        correct_answer: str,
        subskills: str = "",
        family_name: str = "",
    ) -> dict[str, Any]:
        """
        Send the question to the LLM and get a simulated student response.

        Returns
        -------
        dict with keys:
            - is_correct : bool
            - student_answer : str
            - thinking : str
            - confidence : float
            - raw_response : str
            - latency_ms : int
        """
        prompt = self._build_prompt(question_text, correct_answer, subskills, family_name)
        start = time.perf_counter()

        try:
            raw = self._call_ollama(prompt)
        except Exception as exc:
            return {
                "is_correct": False,
                "student_answer": "",
                "thinking": f"LLM 呼叫失敗: {exc}",
                "confidence": 0.0,
                "raw_response": "",
                "latency_ms": int((time.perf_counter() - start) * 1000),
                "error": str(exc),
            }

        latency_ms = int((time.perf_counter() - start) * 1000)
        parsed = self._parse_response(raw)
        parsed["raw_response"] = raw
        parsed["latency_ms"] = latency_ms
        return parsed

    # ------------------------------------------------------------------
    # Prompt construction
    # ------------------------------------------------------------------
    def _build_prompt(
        self,
        question_text: str,
        correct_answer: str,
        subskills: str,
        family_name: str,
    ) -> str:
        return f"""你是一個正在練習數學的國中生模擬器。

## 你的角色設定
{self._ability_prompt}

## 題目資訊
- **題目：** {question_text}
- **正確答案：** {correct_answer}
- **涉及子技能：** {subskills or '（未指定）'}
- **題型名稱：** {family_name or '（未指定）'}

## 你的任務
1. 根據你的角色設定（能力水準），模擬這個國中生的真實思維過程
2. **重要**：你不一定要答對！根據你的能力水準，你可能在某些步驟犯錯
3. 給出你的模擬作答
4. 誠實判斷你的答案是否與正確答案一致

## 回覆格式
請嚴格用以下 JSON 格式回覆，不要加任何 markdown 標記或其他文字：
{{"thinking": "你的思考過程（用中文描述你如何解題、可能在哪一步犯錯）", "student_answer": "你的最終答案（只寫數學表達式或數值）", "is_correct": true或false, "confidence": 0.0到1.0之間的數字}}

注意：
- is_correct 必須是 true 或 false（小寫、無引號）
- confidence 是一個 0~1 的浮點數
- 整個回覆只有一個 JSON 物件，不要有其他內容"""

    # ------------------------------------------------------------------
    # Ollama API call
    # ------------------------------------------------------------------
    def _call_ollama(self, prompt: str) -> str:
        """Call the Ollama generate API and return the full response text."""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_predict": 512,
            },
        }
        resp = requests.post(
            self.api_url,
            json=payload,
            timeout=self.timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        return str(data.get("response", "")).strip()

    # ------------------------------------------------------------------
    # Response parsing with fallback
    # ------------------------------------------------------------------
    def _parse_response(self, raw: str) -> dict[str, Any]:
        """Parse the LLM response into a structured dict with fallback."""
        default = {
            "is_correct": False,
            "student_answer": "",
            "thinking": "",
            "confidence": 0.0,
        }

        if not raw:
            default["thinking"] = "LLM 回傳空白"
            return default

        # Try direct JSON parse
        cleaned = raw.strip()
        # Remove markdown code fences if present
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        cleaned = cleaned.strip()

        try:
            parsed = json.loads(cleaned)
            if isinstance(parsed, dict):
                return {
                    "is_correct": bool(parsed.get("is_correct", False)),
                    "student_answer": str(parsed.get("student_answer", "")),
                    "thinking": str(parsed.get("thinking", "")),
                    "confidence": float(parsed.get("confidence", 0.0)),
                }
        except (json.JSONDecodeError, ValueError):
            pass

        # Fallback: try to find JSON block in text
        json_match = re.search(r"\{[^{}]*\}", cleaned, re.DOTALL)
        if json_match:
            try:
                parsed = json.loads(json_match.group())
                if isinstance(parsed, dict):
                    return {
                        "is_correct": bool(parsed.get("is_correct", False)),
                        "student_answer": str(parsed.get("student_answer", "")),
                        "thinking": str(parsed.get("thinking", "")),
                        "confidence": float(parsed.get("confidence", 0.0)),
                    }
            except (json.JSONDecodeError, ValueError):
                pass

        # Last resort: heuristic
        default["thinking"] = f"無法解析 LLM 回傳: {raw[:200]}"
        if '"is_correct": true' in raw.lower() or '"is_correct":true' in raw.lower():
            default["is_correct"] = True
        return default
