# skills/jh_arithmetic_series_sum_calc.py
import random

def generate(level=1):
    """
    生成一道「等差級數求和」的題目。
    """
    a1 = random.randint(-5, 5)
    d = random.randint(1, 5)
    n = random.randint(10, 20)

    # an = a1 + (n-1)d
    an = a1 + (n - 1) * d
    # Sn = n * (a1 + an) / 2
    total_sum = n * (a1 + an) // 2

    question_text = f"一個等差級數的首項為 {a1}，公差為 {d}，共有 {n} 項，請問此級數的和是多少？"
    correct_answer = str(total_sum)

    context_string = f"利用等差級數求和公式 S_n = n(a_1+a_n)/2 或 S_n = n[2a_1+(n-1)d]/2 來計算。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    user = user_answer.strip()
    correct = correct_answer.strip()
    try:
        is_correct = int(user) == int(correct)
        result_text = f"完全正確！答案是 {correct}。" if is_correct else f"答案不正確。正確答案是：{correct}"
    except ValueError:
        is_correct = False
        result_text = f"請輸入數字答案。正確答案是：{correct}"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}