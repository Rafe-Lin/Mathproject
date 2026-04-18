import random
import math

def generate(level=1):
    """
    生成一道「三角形面積公式」的題目。
    Area = 1/2 * a * b * sin(C)
    """
    a = random.randint(5, 10)
    b = random.randint(5, 10)
    
    if level == 1:
        angle = random.choice([30, 45, 60])
        s_angle = math.sin(math.radians(angle))
    else: # level 2
        angle = random.choice([120, 135, 150])
        s_angle = math.sin(math.radians(angle))

    question_text = f"已知三角形的兩邊長分別為 {a} 和 {b}，其夾角為 {angle}°，請問此三角形的面積是多少？"
    area = 0.5 * a * b * s_angle
    correct_answer = str(round(area, 2))
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    try:
        user_float = float(user)
        is_correct = abs(user_float - float(correct)) < 0.01
        result_text = f"完全正確！答案約為 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
        return {"correct": is_correct, "result": result_text, "next_question": True}
    except ValueError:
        return {"correct": False, "result": f"請輸入有效的數字答案。正確答案應為：{correct_answer}", "next_question": False}