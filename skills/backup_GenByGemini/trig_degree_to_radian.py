import random

def generate(level=1):
    """
    生成一道「角度與弧度互換」的題目。
    """
    if level == 1:
        angle_deg = random.choice([30, 45, 60, 90, 120, 150, 180, 270, 360])
        question_text = f"請將角度 {angle_deg}° 轉換為弧度（以 π 表示）。\n(例如: π/2)"
        if angle_deg == 30: correct_answer = "π/6"
        elif angle_deg == 45: correct_answer = "π/4"
        elif angle_deg == 60: correct_answer = "π/3"
        elif angle_deg == 90: correct_answer = "π/2"
        elif angle_deg == 120: correct_answer = "2π/3"
        elif angle_deg == 150: correct_answer = "5π/6"
        elif angle_deg == 180: correct_answer = "π"
        elif angle_deg == 270: correct_answer = "3π/2"
        else: correct_answer = "2π"
    else: # level 2
        rad_num = random.randint(1, 4)
        rad_den = random.choice([2, 3, 4, 6])
        question_text = f"請將弧度 {rad_num}π/{rad_den} 轉換為角度。"
        correct_answer = str(rad_num * 180 // rad_den) + "°"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").replace("pi", "π")
    correct = str(correct_answer).strip().replace(" ", "")
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}