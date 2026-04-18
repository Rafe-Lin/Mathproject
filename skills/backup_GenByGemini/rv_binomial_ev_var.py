# \機率統計\二項分布的期望值與變異數
import random
from fractions import Fraction

def generate(level=1):
    """
    生成一道「二項分布的期望值與變異數」的題目。
    """
    n = random.randint(10, 100)
    p = Fraction(random.randint(1, 4), 10)
    
    if level == 1:
        question_text = f"已知隨機變數 X 服從二項分布 B({n}, {p})，請問 X 的期望值 E(X) 是多少？"
        ans = n * p
    else: # level 2
        question_text = f"已知隨機變數 X 服從二項分布 B({n}, {p})，請問 X 的變異數 Var(X) 是多少？"
        ans = n * p * (1-p)
        
    correct_answer = f"{ans.numerator}/{ans.denominator}" if ans.denominator != 1 else str(ans.numerator)
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}