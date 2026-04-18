# \三角函數\餘弦的和角與差角公式
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「餘弦的和角與差角公式」的題目。
    """
    if level == 1:
        question_text = (
            "根據餘弦的和角公式，cos(α + β) 等於什麼？\n\n"
            "A) sin(α)cos(β) + cos(α)sin(β)\n"
            "B) cos(α)cos(β) - sin(α)sin(β)\n"
            "C) cos(α)cos(β) + sin(α)sin(β)"
        )
        correct_answer = "B"
    else: # level 2
        question_text = "請利用和角或差角公式，計算 cos(75°) 的值。\n(75° = 45° + 30°)"
        correct_answer = "(√6-√2)/4"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    if correct_answer in ["A", "B", "C"]:
        return check_answer(user_answer, correct_answer, check_type='case_insensitive')
    else:
        user_answer = user_answer.replace(" ", "").upper()
        return check_answer(user_answer, correct_answer.upper())