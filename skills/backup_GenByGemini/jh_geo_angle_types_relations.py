# skills/jh_geo_angle_types_relations.py
import random

def generate(level=1):
    """
    生成一道「角的關係(補角、餘角、對頂角)」的題目。
    """
    q_type = random.choice(['complementary', 'supplementary', 'vertical'])
    
    if q_type == 'complementary':
        angle1 = random.randint(10, 80)
        angle2 = 90 - angle1
        question_text = f"若 ∠A 和 ∠B 互為餘角，且 ∠A = {angle1}°，請問 ∠B 是多少度？"
        correct_answer = str(angle2)
        context_string = "互為餘角的兩個角，其度數和為 90 度。"
    elif q_type == 'supplementary':
        angle1 = random.randint(10, 170)
        angle2 = 180 - angle1
        question_text = f"若 ∠A 和 ∠B 互為補角，且 ∠A = {angle1}°，請問 ∠B 是多少度？"
        correct_answer = str(angle2)
        context_string = "互為補角的兩個角，其度數和為 180 度。"
    else: # vertical
        angle1 = random.randint(10, 170)
        question_text = f"兩直線相交於一點，形成四個角。若其中一個角為 {angle1}°，請問它的對頂角是多少度？"
        correct_answer = str(angle1)
        context_string = "兩直線相交時，對頂角相等。"

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