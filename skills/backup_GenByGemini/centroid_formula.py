import random
import re

def generate(level=1):
    """
    生成一個計算三角形重心坐標的題目。
    """
    # level 參數暫時未使用，但保留以符合架構
    # 為了讓重心是整數，我們先決定重心 G
    gx = random.randint(-10, 10)
    gy = random.randint(-10, 10)

    # 然後隨機選擇兩個頂點 A 和 B
    x1 = random.randint(-10, 10)
    y1 = random.randint(-10, 10)
    x2 = random.randint(-10, 10)
    y2 = random.randint(-10, 10)

    # 根據重心公式 G = ((x1+x2+x3)/3, (y1+y2+y3)/3)
    # 反推出第三個頂點 C
    x3 = 3 * gx - x1 - x2
    y3 = 3 * gy - y1 - y2

    # 如果 C 點坐標超出範圍，重新生成
    while abs(x3) > 20 or abs(y3) > 20:
        x1 = random.randint(-10, 10)
        y1 = random.randint(-10, 10)
        x2 = random.randint(-10, 10)
        y2 = random.randint(-10, 10)
        x3 = 3 * gx - x1 - x2
        y3 = 3 * gy - y1 - y2

    question_text = f"設三角形的三個頂點為 A({x1}, {y1})、B({x2}, {y2})、C({x3}, {y3})，求此三角形的重心坐標。"
    
    correct_answer = f"({gx}, {gy})"

    return {
        "question_text": question_text,
        "answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查使用者輸入的重心坐標是否正確。
    接受的格式: (x, y), (x,y), x, y, x,y
    """
    correct_match = re.match(r'\(\s*(-?\d+)\s*,\s*(-?\d+)\s*\)', correct_answer)
    correct_x = int(correct_match.group(1))
    correct_y = int(correct_match.group(2))

    user_answer = user_answer.replace('(', '').replace(')', '').replace(' ', '')
    
    parts = user_answer.split(',')
    if len(parts) != 2:
        return {"correct": False, "result": "請輸入兩個坐標值，並用逗號分隔。", "next_question": False}
    
    try:
        user_x = float(parts[0].strip())
        user_y = float(parts[1].strip())
        
        if user_x == correct_x and user_y == correct_y:
            return {"correct": True, "result": "完全正確！", "next_question": True}
        else:
            return {"correct": False, "result": f"答案不正確。正確答案是 ({correct_x}, {correct_y})。", "next_question": True}
    except ValueError:
        return {"correct": False, "result": "請輸入有效的數字坐標，例如 '3, 5' 或 '(3, 5)'。", "next_question": False}