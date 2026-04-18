# -*- coding: utf-8 -*-
# Pattern skill: p2a_mult_direct — 兩根式相乘
# 一題型一檔，委派 DomainFunctionHelper

from core.domain_functions import DomainFunctionHelper

PATTERN_ID = "p2a_mult_direct"

def _level_to_difficulty(level):
    if level <= 1: return "easy"
    if level == 2: return "mid"
    return "hard"

def generate(level=1):
    df = DomainFunctionHelper()
    difficulty = _level_to_difficulty(level)
    vars_ = df.get_safe_vars_for_pattern(PATTERN_ID, difficulty)
    ans_latex, _ = df.solve_problem_pattern(PATTERN_ID, vars_, difficulty)
    q_latex = df.format_question_LaTeX(PATTERN_ID, vars_)
    canonical = _latex_to_canonical(ans_latex)
    return {
        "question_text": q_latex,
        "correct_answer": canonical,
        "answer": canonical,
        "mode": 1,
    }

def _latex_to_canonical(latex):
    """將 LaTeX 答案轉為比對用 canonical 格式 (如 "6,2" 或 "5")"""
    import re
    s = str(latex).strip().replace("\\", "")
    if re.match(r"^-?\d+$", s):
        return s
    m = re.search(r"(-?\d*)sqrt\{(\d+)\}", s, re.I)
    if m:
        c_str, r = m.group(1), m.group(2)
        if not c_str or c_str == "-":
            c_str = "-1" if c_str == "-" else "1"
        return f"{c_str},{r}"
    return latex

def check(user_answer, correct_answer):
    if user_answer is None:
        return {"correct": False, "result": "未提供答案。"}
    u = str(user_answer).strip().replace(" ", "").replace("$", "").replace("\\", "")
    c = str(correct_answer).strip()
    if u == c:
        return {"correct": True, "result": "正確！"}
    try:
        import math
        if math.isclose(float(u), float(c), abs_tol=1e-6):
            return {"correct": True, "result": "正確！"}
    except (ValueError, TypeError):
        pass
    return {"correct": False, "result": f"答案錯誤。正確答案為：{correct_answer}"}
