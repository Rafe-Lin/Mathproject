import random
import math

def generate(level=1):
    """
    生成一道「空間向量夾角」的題目。
    """
    if level == 1:
        # 構造特殊角度
        angle_deg = random.choice([0, 60, 90, 120, 180])
        v1 = [random.randint(1, 5), 0, 0]
        v2_x = math.cos(math.radians(angle_deg))
        v2_y = math.sin(math.radians(angle_deg))
        v2 = [v2_x, v2_y, 0] # 簡化在 xy 平面
        question_text = f"已知兩向量的夾角為 {angle_deg}°，請問其夾角的 cos 值是多少？"
        correct_answer = str(round(math.cos(math.radians(angle_deg)), 2))
    else: # level 2
        v1 = [random.randint(-5, 5) for _ in range(3)]
        v2 = [random.randint(-5, 5) for _ in range(3)]
        question_text = f"已知向量 a = {tuple(v1)}，向量 b = {tuple(v2)}，請求出兩向量夾角的 cos 值。 (四捨五入至小數點後兩位)"
        dot_product = sum(v1[i] * v2[i] for i in range(3))
        mag1 = math.sqrt(sum(c*c for c in v1))
        mag2 = math.sqrt(sum(c*c for c in v2))
        cos_angle = dot_product / (mag1 * mag2) if mag1*mag2 != 0 else 0
        correct_answer = str(round(cos_angle, 2))
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = abs(float(user) - float(correct)) < 0.01
    result_text = f"完全正確！答案約為 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}