# skills/jh_geo_parallel_lines_test.py
import random

def generate(level=1):
    """
    生成一道「平行線的判別」的題目。
    """
    condition = random.choice(['alternate_interior', 'corresponding', 'consecutive_interior'])
    are_parallel = random.choice([True, False])

    angle1 = random.randint(50, 130)

    if are_parallel:
        correct_answer = "是"
        if condition == 'alternate_interior':
            angle2 = angle1
            question_text = f"兩直線被一截線所截，若一組內錯角皆為 {angle1}°，請問這兩條直線是否平行？"
        elif condition == 'corresponding':
            angle2 = angle1
            question_text = f"兩直線被一截線所截，若一組同位角皆為 {angle1}°，請問這兩條直線是否平行？"
        else: # consecutive_interior
            angle2 = 180 - angle1
            question_text = f"兩直線被一截線所截，若一組同側內角分別為 {angle1}° 和 {angle2}°，請問這兩條直線是否平行？"
    else:
        correct_answer = "否"
        angle2 = angle1 + random.randint(5, 20)
        question_text = f"兩直線被一截線所截，若一組同位角分別為 {angle1}° 和 {angle2}°，請問這兩條直線是否平行？"

    question_text += "\n(請回答 '是' 或 '否')"
    context_string = "利用「同位角相等」、「內錯角相等」或「同側內角互補」來判斷兩直線是否平行。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    user = user_answer.strip()
    correct = str(correct_answer).strip()
    if user in ["是", "Y", "y"] and correct == "是": is_correct = True
    elif user in ["否", "N", "n"] and correct == "否": is_correct = True
    else: is_correct = False
    result_text = f"完全正確！答案是 {correct}。" if is_correct else f"答案不正確。正確答案是：{correct}"
    return {"correct": is_correct, "result": result_text, "next_question": True}