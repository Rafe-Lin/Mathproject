import random

def generate(level=1):
    """
    生成一道「空間直線對稱式」的題目。
    """
    point = [random.randint(-5, 5) for _ in range(3)]
    direction = [random.randint(1, 4) for _ in range(3)] # 避免為 0
    
    if level == 1:
        question_text = f"已知空間中一條直線通過點 {tuple(point)}，且方向向量為 {tuple(direction)}，請寫出此直線的對稱比例式。\n(這是一道觀念題，請在紙上作答)"
        correct_answer = "觀念題"
    else: # level 2
        question_text = f"已知直線 L 的對稱式為 (x-{point[0]})/{direction[0]} = (y-{point[1]})/{direction[1]} = (z-{point[2]})/{direction[2]}，請問此直線的方向向量為何？"
        correct_answer = str(tuple(direction))
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    if correct_answer == "觀念題": return {"correct": True, "result": "觀念正確！對稱式為 (x-x₀)/a = (y-y₀)/b = (z-z₀)/c。", "next_question": True}
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip().replace(" ", "")
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}