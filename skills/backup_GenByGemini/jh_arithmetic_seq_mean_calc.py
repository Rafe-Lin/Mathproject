# skills/jh_arithmetic_seq_mean_calc.py
import random

def generate(level=1):
    """
    生成一道「等差中項計算」的題目。
    """
    # 構造 a, b, c 為等差數列
    a = random.randint(-10, 10)
    d = random.randint(1, 5)
    b = a + d
    c = b + d

    question_text = f"若 {a}, x, {c} 三數成等差數列，請問 x (等差中項) 的值是多少？"
    correct_answer = str(b)

    context_string = "在等差數列 a, b, c 中，b 稱為 a 和 c 的等差中項，其值為 (a+c)/2。"

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