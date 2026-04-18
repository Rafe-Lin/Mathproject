# skills/jh_geometric_seq_mean_calc.py
import random

def generate(level=1):
    """
    生成一道「等比中項計算」的題目。
    """
    # 構造 a, b, c 為等比數列
    a = random.randint(1, 4)
    r = random.randint(2, 4)
    b = a * r
    c = b * r

    question_text = f"若 {a}, x, {c} 三正數成等比數列，請問 x (等比中項) 的值是多少？"
    correct_answer = str(b)

    context_string = "在等比數列 a, b, c 中，b 稱為 a 和 c 的等比中項，其關係為 b² = ac。"

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