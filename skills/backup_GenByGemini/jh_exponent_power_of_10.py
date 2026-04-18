# skills/jh_exponent_power_of_10.py
import random

def generate(level=1):
    """
    生成一道「10的次方」的題目。
    """
    exponent = random.randint(2, 7)

    # 隨機問正向或反向問題
    if random.choice([True, False]):
        # 10^n = ?
        question_text = f"請問 10^{exponent} 等於多少？"
        correct_answer = str(10**exponent)
    else:
        # 10000 = 10^?
        value = 10**exponent
        question_text = f"請問 {value} 等於 10 的幾次方？"
        correct_answer = str(exponent)

    context_string = f"熟練 10 的次方表示法與其值的關係"

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