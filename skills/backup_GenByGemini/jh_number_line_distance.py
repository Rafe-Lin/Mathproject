# skills/jh_number_line_distance.py
import random

def generate(level=1):
    """
    生成一道「數線上的距離」的題目。
    """
    point1 = random.randint(-20, 20)
    point2 = random.randint(-20, 20)
    while point1 == point2:
        point2 = random.randint(-20, 20)

    distance = abs(point1 - point2)
    correct_answer = str(distance)

    question_text = f"請問在數線上，點 A({point1}) 和點 B({point2}) 之間的距離是多少？"

    context_string = f"計算數線上兩點的距離公式為 |a - b|"

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