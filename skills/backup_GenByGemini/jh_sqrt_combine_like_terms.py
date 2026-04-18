# skills/jh_sqrt_combine_like_terms.py
import random

def generate(level=1):
    """
    生成一道「方根的化簡與同類方根合併」的題目。
    """
    # 構造 a√c + b√c
    c = random.choice([2, 3, 5, 6, 7]) # 不可再化簡的根號
    a = random.randint(2, 7)
    b = random.randint(-5, 5)
    while b == 0: b = random.randint(-5, 5)

    # 為了讓題目看起來複雜一點，將其中一項藏起來
    # a√c + b√(d^2 * c)
    d = random.randint(2, 3)
    term1_val = a
    term2_val = b * d
    term2_radicand = c * (d**2)

    question_text = f"請化簡並計算：{term1_val}√{c} + √{term2_radicand}"
    
    # 正確答案 (a+bd)√c
    final_coeff = a + b*d
    correct_answer = f"{final_coeff}sqrt({c})"

    context_string = "先將各方根化為最簡根式，再合併同類方根。"

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