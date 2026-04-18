# skills/jh_opposite_number_def.py
import random

def generate(level=1):
    """
    生成一道「相反數定義」的題目。
    與原點距離相等，但方向相反的兩個數互為相反數。
    """
    num = random.randint(-20, 20)
    while num == 0:
        num = random.randint(-20, 20)
    
    correct_answer = str(-num)

    question_text = f"請問 {num} 的相反數是多少？"

    context_string = f"求 {num} 的相反數。"

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
        "next_question": is_correct
    }