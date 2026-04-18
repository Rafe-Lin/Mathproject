# skills/jh_geo_polygon_angle_sum_exterior.py
import random

def generate(level=1):
    """
    生成一道「多邊形外角和」的題目。
    """
    sides = random.randint(5, 12)
    polygon_name = {5: "五邊形", 6: "六邊形", 7: "七邊形", 8: "八邊形", 10: "十邊形", 12: "十二邊形"}.get(sides, f"{sides}邊形")

    question_text = f"請問任意一個凸{polygon_name}的外角和是多少度？"
    correct_answer = "360"

    context_string = "任意凸多邊形的外角和恆為 360 度。"

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