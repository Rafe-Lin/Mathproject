# skills/jh_prob_def_classical.py
import random
from fractions import Fraction

def generate(level=1):
    """
    生成一道「古典機率定義」的題目。
    """
    # 骰子問題
    total_outcomes = 6
    
    event_type = random.choice(['odd', 'even', 'greater_than_4', 'prime'])
    
    if event_type == 'odd':
        event_name = "奇數"
        favorable_outcomes = 3 # 1, 3, 5
    elif event_type == 'even':
        event_name = "偶數"
        favorable_outcomes = 3 # 2, 4, 6
    elif event_type == 'greater_than_4':
        event_name = "大於4的點數"
        favorable_outcomes = 2 # 5, 6
    else: # prime
        event_name = "質數"
        favorable_outcomes = 3 # 2, 3, 5

    prob = Fraction(favorable_outcomes, total_outcomes)
    question_text = f"投擲一顆公正的骰子一次，出現「{event_name}」的機率是多少？ (請以最簡分數表示)"
    correct_answer = f"{prob.numerator}/{prob.denominator}"

    context_string = "古典機率 P(A) = (事件 A 包含的結果個數) / (樣本空間中所有可能結果的總數)。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    try:
        user_frac = Fraction(user_answer.strip())
        correct_frac = Fraction(correct_answer.strip())
        is_correct = user_frac == correct_frac
        result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案是：{correct_answer}"
    except (ValueError, ZeroDivisionError):
        is_correct = False
        result_text = f"請輸入分數格式，例如 1/2。正確答案是：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}