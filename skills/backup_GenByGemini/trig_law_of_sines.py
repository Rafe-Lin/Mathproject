import random
import math

def generate(level=1):
    """
    生成一道「正弦定理」的題目。
    a/sinA = b/sinB = 2R
    """
    angle_A = random.choice([30, 45, 60])
    angle_B = random.choice([30, 45, 60])
    while angle_A == angle_B: angle_B = random.choice([30, 45, 60])
    
    if level == 1:
        a = random.randint(5, 10)
        question_text = f"在三角形ABC中，已知 ∠A = {angle_A}°，∠B = {angle_B}°，且邊長 a (∠A的對邊) = {a}，請問邊長 b 是多少？ (四捨五入至小數點後一位)"
        # b = a * sinB / sinA
        b = a * math.sin(math.radians(angle_B)) / math.sin(math.radians(angle_A))
        correct_answer = str(round(b, 1))
    else: # level 2
        R = random.randint(5, 10)
        question_text = f"在三角形ABC中，已知 ∠A = {angle_A}°，其外接圓半徑 R = {R}，請問邊長 a (∠A的對邊) 是多少？ (四捨五入至小數點後一位)"
        # a = 2R * sinA
        a = 2 * R * math.sin(math.radians(angle_A))
        correct_answer = str(round(a, 1))
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    try:
        user_float = float(user)
        is_correct = abs(user_float - float(correct)) < 0.1
        result_text = f"完全正確！答案約為 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
        return {"correct": is_correct, "result": result_text, "next_question": True}
    except ValueError:
        return {"correct": False, "result": f"請輸入有效的數字答案。正確答案應為：{correct_answer}", "next_question": False}