# skills/jh_geo_triangle_angle_sum_interior.py
import random

def generate(level=1):
    """
    生成一道「三角形內角和」的題目。
    """
    # 內角和為 180
    angle1 = random.randint(20, 100)
    angle2 = random.randint(20, 150 - angle1)
    angle3 = 180 - angle1 - angle2

    question_text = f"一個三角形的其中兩個內角分別是 {angle1}° 和 {angle2}°，請問第三個內角是多少度？"
    correct_answer = str(angle3)

    context_string = "利用三角形內角和為 180 度的性質來計算。"

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