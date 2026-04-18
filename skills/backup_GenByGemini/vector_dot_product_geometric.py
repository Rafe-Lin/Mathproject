import random
import math

def generate(level=1):
    """
    生成一道「向量內積的幾何定義」的題目。
    """
    mag1 = random.randint(2, 10)
    mag2 = random.randint(2, 10)
    if level == 1:
        angle = random.choice([0, 60, 90, 120, 180])
    else: # level 2
        angle = random.choice([30, 45, 135, 150])

    question_text = f"已知向量 a 的長度為 {mag1}，向量 b 的長度為 {mag2}，兩向量的夾角為 {angle}°，請求出其內積 a · b。"
    dot_product = mag1 * mag2 * math.cos(math.radians(angle))
    correct_answer = str(round(dot_product))
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}