# skills/horiz_vert_lines.py
import random

def generate(level=1):
    """
    生成一道「水平線與鉛垂線」題目
    """
    # level 參數暫時未使用，但保留以符合架構
    # 隨機決定是水平線還是鉛垂線
    is_horizontal = random.choice([True, False])

    # 隨機生成兩個點
    x1 = random.randint(-10, 10)
    y1 = random.randint(-10, 10)

    if is_horizontal:
        # 水平線: y 坐標相同
        x2 = random.randint(-10, 10)
        while x1 == x2: # 確保兩點不同
            x2 = random.randint(-10, 10)
        y2 = y1
        correct_answer = f"y={y1}"
        line_type = "水平線"
    else:
        # 鉛垂線: x 坐標相同
        x2 = x1
        y2 = random.randint(-10, 10)
        while y1 == y2: # 確保兩點不同
            y2 = random.randint(-10, 10)
        correct_answer = f"x={x1}"
        line_type = "鉛垂線"

    question_text = (
        f"已知直線 L 通過 A({x1}, {y1}) 與 B({x2}, {y2}) 兩點。\n"
        f"請問這是一條{line_type}還是水平線？它的方程式為何？"
    )
    context_string = f"求通過 A({x1}, {y1}) 與 B({x2}, {y2}) 的直線方程式"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    """檢查使用者輸入的方程式是否正確"""
    user_clean = user_answer.strip().replace(" ", "")
    correct_clean = correct_answer.strip().replace(" ", "")

    if user_clean.lower() == correct_clean.lower():
        return {"correct": True, "result": f"完全正確！答案是 {correct_answer}。"}
    
    # 處理使用者可能只回答 y=k 或 x=k 的情況
    if "y=" in user_clean and "y=" in correct_clean and user_clean == correct_clean:
        return {"correct": True, "result": f"完全正確！答案是 {correct_answer}。"}
    if "x=" in user_clean and "x=" in correct_clean and user_clean == correct_clean:
        return {"correct": True, "result": f"完全正確！答案是 {correct_answer}。"}

    return {"correct": False, "result": f"答案不正確。正確答案是：{correct_answer}"}