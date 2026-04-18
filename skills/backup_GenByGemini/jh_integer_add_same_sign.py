# skills/jh_integer_add_same_sign.py
import random

def generate(level=1):
    """
    生成一道「同號整數加法」的題目。
    """
    # 隨機決定是正數加法還是負數加法
    is_positive = random.choice([True, False])

    if is_positive:
        num1 = random.randint(1, 50)
        num2 = random.randint(1, 50)
    else:
        num1 = random.randint(-50, -1)
        num2 = random.randint(-50, -1)

    correct_answer = str(num1 + num2)

    question_text = f"請問 ({num1}) + ({num2}) 的值是多少？"

    context_string = f"計算同號兩數相加，結果的性質符號不變，數字部分相加。"

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