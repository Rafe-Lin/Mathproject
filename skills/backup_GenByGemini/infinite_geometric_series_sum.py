# \極限\無窮等比級數和
import random
from fractions import Fraction

def generate(level=1):
    """
    生成一道「無窮等比級數和」的題目。
    """
    if level == 1:
        a = random.randint(1, 10)
        r_den = random.randint(2, 5)
        r_num = random.randint(1, r_den - 1)
        r = Fraction(r_num, r_den)
        question_text = f"一個無窮等比級數，其首項為 {a}，公比為 {r}，請求出此級數的和。"
    else: # level 2
        # 0.999...
        question_text = "請求出 0.9 + 0.09 + 0.009 + ... 的值。"
        a = Fraction(9, 10)
        r = Fraction(1, 10)
    
    ans = a / (1 - r)
    correct_answer = f"{ans.numerator}/{ans.denominator}" if ans.denominator != 1 else str(ans.numerator)
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}