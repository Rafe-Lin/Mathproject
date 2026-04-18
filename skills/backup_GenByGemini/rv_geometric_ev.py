# \機率統計\幾何分布的期望值
import random
from fractions import Fraction

def generate(level=1):
    """
    生成一道「幾何分布的期望值」的題目。
    """
    p_den = random.randint(3, 10)
    p = Fraction(1, p_den)
    
    question_text = f"重複進行一項成功的機率為 {p} 的試驗，直到成功為止。請問平均需要進行多少次試驗？"
    ans = 1 / p
    correct_answer = str(ans)
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}