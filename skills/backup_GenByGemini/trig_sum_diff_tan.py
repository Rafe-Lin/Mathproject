# \三角函數\正切的和角與差角公式
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「正切的和角與差角公式」的題目。
    """
    if level == 1:
        question_text = (
            "根據正切的和角公式，tan(α + β) 等於什麼？\n\n"
            "A) (tan(α)+tan(β))/(1-tan(α)tan(β))\n"
            "B) (tan(α)-tan(β))/(1+tan(α)tan(β))\n"
            "C) tan(α) + tan(β)"
        )
        correct_answer = "A"
    else: # level 2
        question_text = "請利用和角或差角公式，計算 tan(105°) 的值。\n(105° = 60° + 45°)"
        correct_answer = "-(2+√3)"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    if correct_answer in ["A", "B", "C"]:
        return check_answer(user_answer, correct_answer, check_type='case_insensitive')
    else:
        user_answer = user_answer.replace(" ", "").upper()
        return check_answer(user_answer, correct_answer.upper())