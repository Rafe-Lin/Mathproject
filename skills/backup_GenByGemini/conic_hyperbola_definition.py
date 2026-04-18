# \圓錐曲線\雙曲線定義
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「雙曲線定義」的觀念題。
    """
    question_text = (
        "在平面上，到兩個「定點 F₁, F₂」的距離「差的絕對值」為一個定值 (2a) 的所有點，其所形成的軌跡圖形稱為什麼？ (前提是 0 < 2a < |F₁F₂|)\n\n"
        "A) 拋物線\n"
        "B) 橢圓\n"
        "C) 雙曲線"
    )
    correct_answer = "C"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    return check_answer(user_answer, correct_answer, check_type='case_insensitive')