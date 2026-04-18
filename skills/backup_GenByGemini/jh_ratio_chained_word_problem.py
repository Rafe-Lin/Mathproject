# skills/jh_ratio_chained_word_problem.py
import random
import math

def generate(level=1):
    """
    生成一道「連比應用問題」的題目。
    """
    # 構造 a:b:c
    a = random.randint(2, 5)
    b = random.randint(2, 5)
    c = random.randint(2, 5)
    
    # 簡化連比
    common_divisor = math.gcd(math.gcd(a, b), c)
    a //= common_divisor
    b //= common_divisor
    c //= common_divisor

    # 總和
    multiplier = random.randint(5, 20)
    total = (a + b + c) * multiplier
    
    val_a = a * multiplier
    val_b = b * multiplier
    val_c = c * multiplier

    question_text = f"一個三角形的周長為 {total} 公分，其三邊長的比為 {a}:{b}:{c}。請問最長邊的長度是多少公分？"
    correct_answer = str(max(val_a, val_b, val_c))

    context_string = "利用連比假設各部分為 ar, br, cr，再根據總和求出 r，進而算出各部分實際的值。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    user = user_answer.strip()
    correct = correct_answer.strip()
    is_correct = user == correct
    result_text = f"完全正確！答案是 {correct} 公分。" if is_correct else f"答案不正確。正確答案是：{correct} 公分"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}