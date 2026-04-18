# skills/jh_circle_inscribed_quadrilateral.py
import random

def generate(level=1):
    """
    生成一道「圓內接四邊形」的題目。
    """
    angle1 = random.randint(70, 110)
    angle2 = 180 - angle1

    question_text = f"一個四邊形 ABCD 內接於一個圓。若 ∠A = {angle1}°，請問它的對角 ∠C 是多少度？"
    correct_answer = str(angle2)

    context_string = "圓內接四邊形的對角互補（相加等於 180°）。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    user = user_answer.strip().replace("°", "")
    correct = correct_answer.strip()
    try:
        is_correct = int(user) == int(correct)
        result_text = f"完全正確！答案是 {correct}°。" if is_correct else f"答案不正確。正確答案是：{correct}°"
    except ValueError:
        is_correct = False
        result_text = f"請輸入數字答案。正確答案是：{correct}°"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}