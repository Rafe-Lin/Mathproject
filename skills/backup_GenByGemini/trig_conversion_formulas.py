import random

def generate(level=1):
    """
    生成一道「三角函數化簡公式」的題目。
    """
    angle = random.choice([30, 45, 60])
    if level == 1:
        # sin(180-θ) = sin(θ)
        q_angle = 180 - angle
        question_text = f"請求出 sin({q_angle}°) 的值。\n(若答案有根號，請用 √ 表示)"
        if angle == 30: correct_answer = "1/2"
        elif angle == 45: correct_answer = "1/√2"
        else: correct_answer = "√3/2"
    else: # level 2
        # cos(180+θ) = -cos(θ)
        q_angle = 180 + angle
        question_text = f"請求出 cos({q_angle}°) 的值。\n(若答案有根號，請用 √ 表示)"
        if angle == 30: correct_answer = "-√3/2"
        elif angle == 45: correct_answer = "-1/√2"
        else: correct_answer = "-1/2"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").replace("sqrt", "√")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}