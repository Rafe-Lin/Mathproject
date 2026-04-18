# skills/jh_factor_def_check.py
import random

def generate(level=1):
    """
    生成一道「因式與倍式定義」的題目。
    """
    # 構造 A = B * C
    # B = (x+a)
    a = random.randint(1, 5)
    B_str = f"(x+{a})"
    
    # C = (x+b)
    b = random.randint(1, 5)
    C_str = f"(x+{b})"
    
    # A = x^2 + (a+b)x + ab
    A_coeff_b = a + b
    A_coeff_c = a * b
    A_str = f"x² + {A_coeff_b}x + {A_coeff_c}"

    # 隨機問 B 是不是 A 的因式，或 A 是不是 B 的倍式
    if random.choice([True, False]):
        question_text = f"請問 {B_str} 是不是 {A_str} 的因式？ (請回答 '是' 或 '否')"
    else:
        question_text = f"請問 {A_str} 是不是 {B_str} 的倍式？ (請回答 '是' 或 '否')"
        
    correct_answer = "是"

    context_string = "如果多項式 A 可以被多項式 B 整除，則 B 是 A 的因式，A 是 B 的倍式。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    user = user_answer.strip()
    correct = str(correct_answer).strip()
    if user in ["是", "Y", "y"] and correct == "是": is_correct = True
    elif user in ["否", "N", "n"] and correct == "否": is_correct = True
    else: is_correct = False
    result_text = f"完全正確！答案是 {correct}。" if is_correct else f"答案不正確。正確答案是：{correct}"
    return {"correct": is_correct, "result": result_text, "next_question": True}