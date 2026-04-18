import random

def generate(level=1):
    """
    生成一道「讀懂遞迴關係式」的題目。
    level 1: an = an-1 + d
    level 2: an = r*an-1
    """
    a1 = random.randint(1, 10)
    
    if level == 1: # 等差
        d = random.randint(2, 8)
        relation = f"a₁ = {a1} 且 aₙ = aₙ₋₁ + {d} (當 n ≥ 2)"
        a3 = a1 + 2*d
    else: # 等比
        r = random.randint(2, 4)
        relation = f"a₁ = {a1} 且 aₙ = {r} * aₙ₋₁ (當 n ≥ 2)"
        a3 = a1 * r * r

    question_text = f"已知數列 <aₙ> 的遞迴定義為：{relation}，請求出 a₃ 的值。"
    correct_answer = str(a3)

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}