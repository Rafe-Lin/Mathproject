# -*- coding: utf-8 -*-
"""Default prompt templates for bootstrap."""

DEFAULT_PROMPT_TEMPLATES = {
    "base_prompt": {
        "title": "基礎角色設定 (Base Prompt)",
        "category": "system",
        "description": "全局基礎指令，設定 AI 助教的 Persona、語氣風格，以及禁止 AI 做出危險行為。",
        "usage_context": "作為所有 RAG 與對話模型調用的最底層 Prompt，用來奠定基礎對話行為。",
        "used_in": "core/advanced_rag_engine.py -> _build_adv_rag_prompt()",
        "example_trigger": "任何透過 Advanced RAG 觸發的對話，或直接呼叫 LLM 進行解題時均會預設插入此段。",
        "content": (
            "You are a math tutoring assistant. Keep explanations step-by-step, "
            "clear, and aligned with student grade level."
        ),
        "required_variables": "",
        "is_active": True,
    },
    "tutor_hint_prompt": {
        "title": "對話引導提示 (Tutor Hint)",
        "category": "tutor",
        "description": "鷹架式的引導提示，要求 AI 在不直接給出答案的情況下給予下一步提示。",
        "usage_context": "當學生於對話框詢問「這題怎麼解？」或是提交錯誤答案後請求協助時使用。",
        "used_in": "core/advanced_rag_engine.py -> _build_adv_rag_prompt() (作為引導層附加)",
        "example_trigger": "學生在練習頁點擊「請問助教」或向前端發送聊天訊息時觸發。",
        "content": (
            "Given the student question: {question}, provide one concise hint first "
            "without revealing the final answer."
        ),
        "required_variables": "question",
        "is_active": True,
    },
    "concept_prompt": {
        "title": "觀念解說提示 (Concept)",
        "category": "concept",
        "description": "用於針對特定名詞或數學觀念進行舉例說明的專用提示詞。",
        "usage_context": "當學生明確要求解釋某個數學觀念（如：什麼是同類項），或系統偵測到觀念澄清需求時。",
        "used_in": "core/ai_analyzer.py -> generate_concept_explanation() 或相關概念解析模組",
        "example_trigger": "學生點擊「這是什麼意思？」的觀念查詢功能，或是系統觸發觀念小卡時。",
        "content": (
            "Explain the concept '{concept}' for grade {grade} students with one "
            "example and one common misconception."
        ),
        "required_variables": "concept,grade",
        "is_active": True,
    },
    "mistake_prompt": {
        "title": "錯誤分析診斷 (Mistake Analysis)",
        "category": "diagnosis",
        "description": "專門用於分析學生錯誤原因、歸納錯誤類型，並給予糾正建議的提示詞。",
        "usage_context": "當學生在手寫批改、一般測驗或互動流程中作答錯誤時，於後台進行隱含診斷或給予回饋。",
        "used_in": "core/ai_analyzer.py -> analyze_student_mistake()",
        "example_trigger": "批改模組判定學生計算錯誤，將學生的算式紀錄傳送給 LLM 要求分析弱點時。",
        "content": (
            "Analyze the student mistake from question: {question}, answer: "
            "{student_answer}, expected: {correct_answer}. Return mistake type, "
            "reason, and one correction step."
        ),
        "required_variables": "question,student_answer,correct_answer",
        "is_active": True,
    },
}

