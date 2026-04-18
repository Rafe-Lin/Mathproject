import random

def generate(level=1):
    """
    生成一道「空間坐標系」的題目。
    """
    x, y, z = [random.randint(-10, 10) for _ in range(3)]
    
    if level == 1:
        question_text = f"點 P({x}, {y}, {z}) 在 xy 平面上的投影點坐標為何？"
        correct_answer = f"({x},{y},0)"
    else: # level 2
        axis = random.choice(['x', 'y', 'z'])
        question_text = f"點 P({x}, {y}, {z}) 到 {axis} 軸的距離是多少？"
        if axis == 'x': dist_sq = y**2 + z**2
        elif axis == 'y': dist_sq = x**2 + z**2
        else: dist_sq = x**2 + y**2
        correct_answer = f"√{dist_sq}"

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").replace("sqrt", "√")
    correct = str(correct_answer).strip().replace(" ", "")
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}