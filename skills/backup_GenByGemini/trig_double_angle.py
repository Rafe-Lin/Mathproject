import random
from fractions import Fraction

def generate(level=1):
    """
    生成一道「二倍角公式」的題目。
    """
    if level == 1:
        question_text = (
            "根據正弦的二倍角公式，sin(2θ) 等於什麼？\n\n"
            "A) 2sin(θ)\n"
            "B) 2sin(θ)cos(θ)\n"
            "C) cos²(θ) - sin²(θ)"
        )
        correct_answer = "B"
    else: # level 2
        s = Fraction(random.choice([3, 4]), 5)
        question_text = f"若 sin(θ) = {s} 且 θ 為銳角，請求出 sin(2θ) 的值。(請以最簡分數 a/b 表示)"
        # cos(θ) = sqrt(1 - s²)
        c = (1 - s**2)**0.5
        ans = 2 * s * c
        correct_answer = f"{ans.numerator}/{ans.denominator}"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").upper()
    correct = str(correct_answer).strip().replace(" ", "").upper()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}