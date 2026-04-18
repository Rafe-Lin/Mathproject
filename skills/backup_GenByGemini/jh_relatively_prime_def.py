# skills/jh_relatively_prime_def.py
import random
import math

def generate(level=1):
    """
    生成一道「互質定義」的題目。
    """
    are_relatively_prime = random.choice([True, False])

    if are_relatively_prime:
        num1 = random.randint(10, 30)
        num2 = random.randint(10, 30)
        while math.gcd(num1, num2) != 1 or num1 == num2:
            num1 = random.randint(10, 30)
            num2 = random.randint(10, 30)
        correct_answer = "是"
    else:
        common_factor = random.randint(2, 5)
        num1 = common_factor * random.randint(2, 7)
        num2 = common_factor * random.randint(2, 7)
        while num1 == num2:
            num2 = common_factor * random.randint(2, 7)
        correct_answer = "否"

    question_text = f"請問 {num1} 和 {num2} 是否互質？ (請回答 '是' 或 '否')"

    context_string = f"判斷兩數的最大公因數是否為 1。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    user = user_answer.strip()
    correct = str(correct_answer).strip()
    if user in ["是", "Y", "y"] and correct == "是": is_correct = True
    elif user in ["否", "N", "n"] and correct == "否": is_correct = True
    else: is_correct = False
    result_text = f"完全正確！答案是 {correct}。" if is_correct else f"答案不正確。正確答案是：{correct}"
    return {"correct": is_correct, "result": result_text, "next_question": True}