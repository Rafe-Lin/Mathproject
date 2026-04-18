# \機率統計\幾何分布
import random
from fractions import Fraction

def generate(level=1):
    """
    生成一道「幾何分布」的題目。
    """
    p = Fraction(1, random.randint(3, 6))
    if level == 1:
        k = 1
    else: # level 2
        k = random.randint(2, 4)
    
    question_text = f"重複擲一顆特製骰子，出現6點的機率為 {p}。請問在第 {k} 次投擲時「首次」出現6點的機率是多少？ (請以最簡分數 a/b 表示)"
    ans = ((1-p)**(k-1)) * p
    correct_answer = f"{ans.numerator}/{ans.denominator}"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}