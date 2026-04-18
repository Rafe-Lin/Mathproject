import random
import numpy as np

def generate(level=1):
    """
    生成一道「數據線性變換」的題目。
    Y = aX + b
    level 1: 對平均數的影響。
    level 2: 對標準差的影響。
    """
    mean_x = random.randint(60, 80)
    std_x = random.randint(5, 15)
    a = random.randint(2, 5)
    b = random.randint(-10, 10)
    b_str = f"加 {b}" if b >= 0 else f"減 {abs(b)}"
    
    if level == 1:
        question_text = f"某班數學成績的平均數為 {mean_x} 分。若將每位同學的成績都乘以 {a} 倍再{b_str}分，請問新的平均數會是多少分？"
        # E(aX+b) = aE(X)+b
        correct_answer = str(a * mean_x + b)
    else: # level 2
        question_text = f"某班數學成績的標準差為 {std_x} 分。若將每位同學的成績都乘以 {a} 倍再{b_str}分，請問新的標準差會是多少分？"
        # Std(aX+b) = |a|Std(X)
        correct_answer = str(abs(a) * std_x)

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}