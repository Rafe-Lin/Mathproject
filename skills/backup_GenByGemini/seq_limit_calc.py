# \極限\數列極限計算
import random
from fractions import Fraction

def generate(level=1):
    """
    生成一道「數列極限計算」的題目。
    """
    if level == 1:
        a, b = random.randint(1, 5), random.randint(1, 5)
        c, d = random.randint(1, 5), random.randint(1, 5)
        question_text = f"請求出無窮數列 aₙ = ({a}n + {b}) / ({c}n + {d}) 的極限值。"
        ans = Fraction(a, c)
    else: # level 2
        a, b = random.randint(1, 5), random.randint(1, 5)
        c, d = random.randint(1, 5), random.randint(1, 5)
        question_text = f"請求出無窮數列 aₙ = ({a}n² + {b}) / ({c}n² - {d}n) 的極限值。"
        ans = Fraction(a, c)
        
    correct_answer = f"{ans.numerator}/{ans.denominator}" if ans.denominator != 1 else str(ans.numerator)
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}