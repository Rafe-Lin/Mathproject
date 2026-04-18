# skills/jh_prob_event_complementary.py
import random
from fractions import Fraction

def generate(level=1):
    """
    生成一道「餘事件機率」的題目。
    """
    # 抽球問題
    red_balls = random.randint(2, 5)
    white_balls = random.randint(2, 5)
    total_balls = red_balls + white_balls
    
    # P(至少一白) = 1 - P(全紅)
    # 簡化問題，只抽一球
    # P(不是紅球) = 1 - P(紅球)
    
    prob_red = Fraction(red_balls, total_balls)
    prob_not_red = 1 - prob_red

    question_text = f"一個袋子裡有 {red_balls} 顆紅球和 {white_balls} 顆白球。從袋中抽出一球，請問抽出的球「不是」紅球的機率是多少？ (請以最簡分數表示)"
    correct_answer = f"{prob_not_red.numerator}/{prob_not_red.denominator}"

    context_string = "利用餘事件的性質：P(A 的餘事件) = 1 - P(A)。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    try:
        is_correct = Fraction(user_answer.strip()) == Fraction(correct_answer.strip())
        result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案是：{correct_answer}"
    except (ValueError, ZeroDivisionError):
        is_correct = False
        result_text = f"請輸入分數格式。正確答案是：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}