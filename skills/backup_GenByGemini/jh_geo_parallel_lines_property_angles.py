# skills/jh_geo_parallel_lines_property_angles.py
import random

def generate(level=1):
    """
    生成一道「平行線的截角性質」的題目。
    """
    angle_type = random.choice(['alternate_interior', 'corresponding', 'consecutive_interior'])
    
    angle1 = random.randint(40, 140)

    if angle_type == 'alternate_interior':
        question_text = f"兩平行線被一截線所截，若其中一個內錯角為 {angle1}°，請問另一個內錯角是多少度？"
        correct_answer = str(angle1)
        context_string = "平行線的內錯角相等。"
    elif angle_type == 'corresponding':
        question_text = f"兩平行線被一截線所截，若其中一個同位角為 {angle1}°，請問另一個同位角是多少度？"
        correct_answer = str(angle1)
        context_string = "平行線的同位角相等。"
    else: # consecutive_interior
        angle2 = 180 - angle1
        question_text = f"兩平行線被一截線所截，若其中一個同側內角為 {angle1}°，請問另一個同側內角是多少度？"
        correct_answer = str(angle2)
        context_string = "平行線的同側內角互補（相加為180度）。"

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