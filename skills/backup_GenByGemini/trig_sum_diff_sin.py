# \三角函數\正弦的和角與差角公式
import random

def generate(level=1):
    """
    生成一道「正弦的和角與差角公式」的題目。
    """
    if level == 1:
        question_text = (
            "根據正弦的和角公式，sin(α + β) 等於什麼？\n\n"
            "A) sin(α)cos(β) + cos(α)sin(β)\n"
            "B) cos(α)cos(β) - sin(α)sin(β)\n"
            "C) sin(α)cos(β) - cos(α)sin(β)"
        )
        correct_answer = "A"
    else: # level 2
        question_text = "請利用和角或差角公式，計算 sin(15°) 的值。\n(15° = 45° - 30°)"
        correct_answer = "(√6-√2)/4"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").upper()
    correct = str(correct_answer).strip().replace(" ", "").upper()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}