# skills/jh_prime_composite_def.py
import random

def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

def generate(level=1):
    """
    生成一道「質數與合數的定義」的題目。
    """
    num = random.randint(2, 50)

    if is_prime(num):
        correct_answer = "質數"
    else:
        correct_answer = "合數"

    question_text = f"請問 {num} 是質數還是合數？"

    context_string = f"判斷一個大於1的整數，除了1和本身以外，是否還有其他因數。"

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
    user = user_answer.strip()
    correct = str(correct_answer).strip()

    is_correct = user == correct
    result_text = f"完全正確！答案是 {correct}。" if is_correct else f"答案不正確。正確答案是：{correct}"
    return {"correct": is_correct, "result": result_text, "next_question": True}