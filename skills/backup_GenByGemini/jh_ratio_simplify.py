# skills/jh_ratio_simplify.py
import random
import math

def generate(level=1):
    """
    生成一道「最簡整數比」的題目。
    """
    # 先決定最簡比
    a_simple = random.randint(1, 9)
    b_simple = random.randint(1, 9)
    while math.gcd(a_simple, b_simple) != 1:
        b_simple = random.randint(1, 9)
        
    # 再乘以一個公因數來擴大
    common_factor = random.randint(2, 5)
    
    a_orig = a_simple * common_factor
    b_orig = b_simple * common_factor

    question_text = f"請將 {a_orig} : {b_orig} 化為最簡整數比。"
    correct_answer = f"{a_simple}:{b_simple}"

    context_string = "將比的前項和後項同除以它們的最大公因數。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    """
    檢查使用者輸入的答案是否正確。
    """
    user = user_answer.strip().replace(" ", "")
    correct = correct_answer.strip().replace(" ", "")
    is_correct = user == correct
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案是：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}