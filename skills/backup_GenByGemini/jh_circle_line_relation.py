# skills/jh_circle_line_relation.py
import random

def generate(level=1):
    """
    生成一道「圓與直線的關係」的題目。
    """
    radius = random.randint(3, 10)
    
    relation = random.choice(['secant', 'tangent', 'disjoint'])

    if relation == 'secant':
        # 交兩點，圓心到直線距離 d < r
        distance = random.randint(1, radius - 1)
        correct_answer = "2"
    elif relation == 'tangent':
        # 交一點，d = r
        distance = radius
        correct_answer = "1"
    else: # disjoint
        # 不相交，d > r
        distance = random.randint(radius + 1, radius + 5)
        correct_answer = "0"

    question_text = f"一個圓的半徑為 {radius}，圓心到直線 L 的距離為 {distance}。請問這個圓和直線 L 有幾個交點？"

    context_string = "判斷圓與直線的關係，可以比較圓心到直線的距離 (d) 與半徑 (r) 的大小。"

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
    result_text = f"完全正確！答案是 {correct} 個交點。" if is_correct else f"答案不正確。正確答案是：{correct} 個交點"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}