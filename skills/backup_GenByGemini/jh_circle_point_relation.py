# skills/jh_circle_point_relation.py
import random

def generate(level=1):
    """
    生成一道「點與圓的關係」的題目。
    """
    center_x, center_y = random.randint(-2, 2), random.randint(-2, 2)
    radius = random.randint(3, 8)
    
    relation = random.choice(['inside', 'on', 'outside'])
    
    if relation == 'inside':
        # 隨機生成圓內點
        point_x = center_x + random.randint(-radius+1, radius-1)
        point_y = center_y + random.randint(-radius+1, radius-1)
        correct_answer = "圓內"
    elif relation == 'on':
        # 隨機生成圓上點 (簡化，只在x或y軸上)
        point_x = center_x + radius
        point_y = center_y
        correct_answer = "圓上"
    else: # outside
        point_x = center_x + random.randint(radius+1, radius+5)
        point_y = center_y + random.randint(radius+1, radius+5)
        correct_answer = "圓外"

    question_text = f"坐標平面上，有一個圓心在 ({center_x}, {center_y})、半徑為 {radius} 的圓。請問點 P({point_x}, {point_y}) 在圓內、圓上、還是圓外？"

    context_string = "判斷點與圓的關係，可以計算點到圓心的距離，再與半徑比較。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    user = user_answer.strip()
    correct = correct_answer.strip()
    is_correct = user == correct
    result_text = f"完全正確！答案是「{correct}」。" if is_correct else f"答案不正確。正確答案是：「{correct}」"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}