# skills/jh_integer_multiply_sign_rules.py
import random

def generate(level=1):
    """
    生成一道「整數乘法符號法則」的題目。
    """
    num1 = random.randint(-10, 10)
    num2 = random.randint(-10, 10)
    
    correct_answer = str(num1 * num2)

    question_text = f"請問 ({num1}) × ({num2}) 的值是多少？"

    context_string = f"正正得正、正負得負、負正得負、負負得正。"

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

    return {
        "correct": is_correct,
        "result": result_text,
        "next_question": True
    }