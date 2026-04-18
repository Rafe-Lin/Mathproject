# skills/jh_arithmetic_seq_term_calc.py
import random

def generate(level=1):
    """
    生成一道「等差數列求項」的題目。
    """
    a1 = random.randint(-5, 5)
    d = random.randint(-4, 4)
    while d == 0: d = random.randint(-4, 4)
    n = random.randint(5, 15)

    # an = a1 + (n-1)d
    an = a1 + (n - 1) * d

    question_text = f"一個等差數列的首項為 {a1}，公差為 {d}，請問第 {n} 項是多少？"
    correct_answer = str(an)

    context_string = f"利用等差數列第n項公式 a_n = a_1 + (n-1)d 來計算。"

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