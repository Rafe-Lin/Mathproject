import random
import math

def generate(level=1):
    """
    生成一個計算平面上兩點距離的題目。
    """
    # level 參數暫時未使用，但保留以符合架構
    # 從畢氏三元數中選擇一組，確保距離為整數
    pythagorean_triples = [(3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25)]
    dx_base, dy_base, distance = random.choice(pythagorean_triples)

    # 隨機決定正負號和交換 dx, dy
    dx = random.choice([dx_base, -dx_base, dy_base, -dy_base])
    dy = random.choice([dy_base, -dy_base])
    if abs(dx) == abs(dy): # 避免 dx, dy 相同
        dx = random.choice([dx_base, -dx_base])
        dy = random.choice([dy_base, -dy_base])

    # 隨機生成點 A
    x1 = random.randint(-10, 10)
    y1 = random.randint(-10, 10)

    # 根據距離反推點 B
    x2 = x1 + dx
    y2 = y1 + dy

    question_text = f"計算平面上兩點 A({x1}, {y1}) 和 B({x2}, {y2}) 之間的距離。"
    
    correct_answer = str(distance)

    return {
        "question_text": question_text,
        "answer": str(correct_answer) # 儲存數值答案用於檢查
    }

def check(user_answer, correct_answer):
    """
    檢查使用者計算的距離是否正確。
    允許一定的誤差。
    """
    try:
        user_val = float(user_answer.strip())
        correct_val = float(correct_answer)
        if math.isclose(user_val, correct_val):
            return {"correct": True, "result": "完全正確！"}
    except (ValueError, TypeError):
        pass # 解析失敗

    return {"correct": False, "result": f"答案不正確。正確答案是：{correct_answer}"}