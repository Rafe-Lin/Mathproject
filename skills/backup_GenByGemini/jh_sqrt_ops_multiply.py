# skills/jh_sqrt_ops_multiply.py
import random

def generate(level=1):
    """
    生成一道「方根的乘法」的題目。
    """
    # 構造 √a * √b = √(ab)
    a = random.randint(2, 7)
    b = random.randint(2, 7)
    
    product = a * b
    
    # 嘗試化簡 √(ab)
    simplified_coeff = 1
    simplified_radicand = product
    i = 2
    while i * i <= simplified_radicand:
        if simplified_radicand % (i*i) == 0:
            simplified_radicand //= (i*i)
            simplified_coeff *= i
        else:
            i += 1

    question_text = f"請計算 √{a} × √{b}，並化為最簡根式。"
    correct_answer = f"{simplified_coeff}sqrt({simplified_radicand})" if simplified_coeff > 1 else f"sqrt({simplified_radicand})"

    context_string = "利用根式乘法性質 √a × √b = √(ab)，再化為最簡根式。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").replace("根號", "sqrt")
    correct = correct_answer.strip().replace(" ", "")
    is_correct = user == correct
    result_text = f"完全正確！答案是 {correct_answer.replace('sqrt(', '√').replace(')', '')}。" if is_correct else f"答案不正確。參考答案是：{correct_answer.replace('sqrt(', '√').replace(')', '')}"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}