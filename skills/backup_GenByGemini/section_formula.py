import random
import re

def generate(level=1):
    """
    生成一個計算內分點坐標的題目。
    """
    # level 參數暫時未使用，但保留以符合架構
    # 選擇簡單的比例
    m = random.randint(1, 5)
    n = random.randint(1, 5)
    while m == n:
        n = random.randint(1, 5)

    # 為了讓答案是整數，我們先決定內分點 P 和一個端點 A
    # 然後反推出另一個端點 B
    px = random.randint(-10, 10)
    py = random.randint(-10, 10)
    x1 = random.randint(-10, 10)
    y1 = random.randint(-10, 10)

    # P = (n*A + m*B) / (m+n)
    # (m+n)P = nA + mB
    # mB = (m+n)P - nA
    # B = ((m+n)P - nA) / m
    x2 = ((m + n) * px - n * x1) / m
    y2 = ((m + n) * py - n * y1) / m

    # 如果 B 不是整數點，重新生成
    while x2 != int(x2) or y2 != int(y2):
        px = random.randint(-10, 10)
        py = random.randint(-10, 10)
        x1 = random.randint(-10, 10)
        y1 = random.randint(-10, 10)
        x2 = ((m + n) * px - n * x1) / m
        y2 = ((m + n) * py - n * y1) / m
    
    x2 = int(x2)
    y2 = int(y2)

    question_text = f"設 A({x1}, {y1})、B({x2}, {y2}) 為平面上兩點。若點 P 在線段 AB 上，且 AP:PB = {m}:{n}，求 P 點的坐標。"
    
    correct_answer = f"({px}, {py})"

    return {
        "question_text": question_text,
        "answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查使用者輸入的內分點坐標是否正確。
    接受的格式: (x, y), (x,y), x, y, x,y
    """
    correct_match = re.match(r'\(\s*(-?\d+)\s*,\s*(-?\d+)\s*\)', correct_answer)
    correct_x = int(correct_match.group(1))
    correct_y = int(correct_match.group(2))

    user_answer = user_answer.replace('(', '').replace(')', '').replace(' ', '')
    
    try:
        parts = user_answer.split(',')
        if len(parts) != 2:
            return {"correct": False, "result": "請輸入兩個坐標值，並用逗號分隔。"}
        
        user_x = float(parts[0])
        user_y = float(parts[1])
        
        if user_x == correct_x and user_y == correct_y:
            return {"correct": True, "result": "完全正確！"}
        else:
            return {"correct": False, "result": f"答案不正確。正確答案是 ({correct_x}, {correct_y})。"}

    except ValueError:
        return {"correct": False, "result": "請輸入有效的數字坐標，例如 '3, 5' 或 '(3, 5)'。"}