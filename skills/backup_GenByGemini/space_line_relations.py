# \空間幾何\空間中兩直線關係
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import random
import math
from .utils import check_answer


@dataclass
class Question:
    """標準化問題的資料結構"""
    qtype: str
    prompt: str
    answer: Any
    choices: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


# --- 向量運算輔助函式 ---
def _dot(a: Tuple[float, ...], b: Tuple[float, ...]) -> float:
    return sum(x * y for x, y in zip(a, b))

def _norm(a: Tuple[float, ...]) -> float:
    return math.sqrt(_dot(a, a))

def _cross(a: Tuple[float, float, float], b: Tuple[float, float, float]) -> Tuple[float, float, float]:
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])

def _sub(a: Tuple[float, ...], b: Tuple[float, ...]) -> Tuple[float, ...]:
    return tuple(x - y for x, y in zip(a, b))

def _add(a: Tuple[float, ...], b: Tuple[float, ...]) -> Tuple[float, ...]:
    return tuple(x + y for x, y in zip(a, b))

def _scale(a: Tuple[float, ...], k: float) -> Tuple[float, ...]:
    return tuple(x * k for x in a)

def _format_pt(p: Tuple[float, ...]) -> str:
    return "(" + ", ".join(map(str, p)) + ")"

def _rand_int_tuple(dim: int = 3, low: int = -5, high: int = 5, avoid_zero: bool = False):
    while True:
        t = tuple(random.randint(low, high) for _ in range(dim))
        if not (avoid_zero and all(x == 0 for x in t)):
            return t

# --- 核心邏輯函式 ---
def lines_relation(p1, v1, p2, v2, tol: float = 1e-6) -> str:
    """判斷兩直線關係：重合、平行、相交、歪斜"""
    v1_norm = _norm(v1)
    v2_norm = _norm(v2)
    if v1_norm < tol or v2_norm < tol: return "invalid"

    # 檢查是否平行
    cross_v1_v2 = _cross(v1, v2)
    if _norm(cross_v1_v2) < tol:
        # 檢查是否共線 (重合)
        if _norm(_cross(_sub(p2, p1), v1)) < tol:
            return "重合"
        else:
            return "平行"

    # 檢查是否相交或歪斜
    # 三向量 (p2-p1, v1, v2) 的混合積若為 0，則共平面
    mixed_product = _dot(_sub(p2, p1), cross_v1_v2)
    if abs(mixed_product) < tol:
        return "相交"
    else:
        return "歪斜"

# --- 題型生成器 ---
def _generate_conceptual_question() -> Question:
    """生成觀念題"""
    q_type = random.choice([1, 2])
    if q_type == 1:
        prompt = (
            "在空間中，兩條「不相交」的直線，其關係可能為何？\n\n"
            "A) 只有平行\n"
            "B) 只有歪斜\n"
            "C) 平行或歪斜"
        )
        answer = "C"
    else:
        prompt = (
            "在空間中，兩條「不平行」的直線，其關係可能為何？\n\n"
            "A) 只有相交\n"
            "B) 只有歪斜\n"
            "C) 相交或歪斜"
        )
        answer = "C"
    return Question(qtype="conceptual", prompt=prompt, answer=answer, choices=["A", "B", "C"])

def _generate_relation_judgement_question() -> Question:
    """生成兩直線關係判斷題"""
    # 隨機選擇一個關係，再依此構造題目，確保題型多樣性
    relation_type = random.choice(["平行", "重合", "相交", "歪斜"])

    p1 = _rand_int_tuple(3)
    v1 = _rand_int_tuple(3, avoid_zero=True)

    if relation_type == "平行":
        p2 = _add(p1, _rand_int_tuple(3, avoid_zero=True)) # 確保 p2 不在 L1 上
        v2 = _scale(v1, random.randint(2, 3) * random.choice([-1, 1]))
    elif relation_type == "重合":
        p2 = _add(p1, _scale(v1, random.randint(-2, 2))) # 讓 p2 在 L1 上
        v2 = _scale(v1, random.randint(2, 3) * random.choice([-1, 1]))
    elif relation_type == "相交":
        v2 = _rand_int_tuple(3, avoid_zero=True)
        # 確保 v1, v2 不平行
        while _norm(_cross(v1, v2)) < 1e-6:
            v2 = _rand_int_tuple(3, avoid_zero=True)
        # 讓兩線交於 p1
        p2 = p1
    else: # 歪斜
        v2 = _rand_int_tuple(3, avoid_zero=True)
        p2 = _add(p1, _rand_int_tuple(3, avoid_zero=True))
        # 確保不平行且不共平面
        while _norm(_cross(v1, v2)) < 1e-6 or abs(_dot(_sub(p2, p1), _cross(v1, v2))) < 1e-6:
            v2 = _rand_int_tuple(3, avoid_zero=True)
            p2 = _add(p1, _rand_int_tuple(3, avoid_zero=True))

    prompt = (
        f"判斷下列兩直線的關係：\n"
        f"L₁: 通過點 {_format_pt(p1)}，方向向量為 {_format_pt(v1)}\n"
        f"L₂: 通過點 {_format_pt(p2)}，方向向量為 {_format_pt(v2)}\n\n"
        "選項: A) 重合 B) 平行 C) 相交 D) 歪斜"
    )
    
    # 將中文答案對應到選項
    answer_map = {"重合": "A", "平行": "B", "相交": "C", "歪斜": "D"}
    answer = answer_map[relation_type]

    return Question(qtype="judgement", prompt=prompt, answer=answer, choices=["A", "B", "C", "D"])

# --- 主生成與檢查函式 ---
def generate(level: int = 1) -> Dict[str, Any]:
    """
    主生成函式，根據等級選擇不同的題型。
    """
    if level == 1:
        # Level 1: 只出觀念題
        q = _generate_conceptual_question()
    else:
        # Level 2 以上: 隨機出觀念題或判斷題
        q = random.choice([
            _generate_conceptual_question(),
            _generate_relation_judgement_question()
        ])

    return {
        "question_text": q.prompt,
        "answer": q.answer,
        "correct_answer": "text",  # 告訴前端這是一個文字/選項答案
        "metadata": q.metadata
    }

def check(user_answer: str, correct_answer: str) -> Dict[str, Any]:
    """
    主檢查函式，使用通用的 check_answer。
    """
    return check_answer(user_answer, correct_answer, check_type='case_insensitive')

