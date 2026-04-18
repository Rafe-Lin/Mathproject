# skills/jh_integer_divide_sign_rules.py
import random

def generate(level=1):
    """
    生成一道「整數除法符號法則」的題目。
    """
    # 為了確保能整除，先決定商和除數
    quotient = random.randint(-10, 10)
    while quotient == 0:
        quotient = random.randint(-10, 10)
        
    divisor = random.randint(-10, 10)
    while divisor == 0 or divisor == 1 or divisor == -1:
        divisor = random.randint(-10, 10)

    dividend = quotient * divisor

    correct_answer = str(quotient)

    question_text = f"請問 ({dividend}) ÷ ({divisor}) 的值是多少？"

    context_string = f"同號相除為正，異號相除為負。"

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

    if user == correct:
        is_correct = True
        result_text = f"完全正確！答案是 {correct}。"
    else:
        is_correct = False
        result_text = f"答案不正確。正確答案是：{correct}"

    return {"correct": is_correct, "result": result_text, "next_question": True}