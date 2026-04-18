import random
import re

def generate(level=1):
    """
    生成一個計算兩點中點坐標的題目。
    """
    # level 參數暫時未使用，但保留以符合架構
    x1 = random.randint(-20, 20)
    y1 = random.randint(-20, 20)
    x2 = random.randint(-20, 20)
    y2 = random.randint(-20, 20)

    # 為了讓中點坐標可能是整數，我們讓坐標和為偶數
    if (x1 + x2) % 2 != 0:
        x2 += 1
    if (y1 + y2) % 2 != 0:
        y2 += 1

    question_text = f"計算點 A({x1}, {y1}) 和點 B({x2}, {y2}) 的中點坐標。"
    
    # 計算正確答案
    mid_x = (x1 + x2) / 2
    mid_y = (y1 + y2) / 2
    correct_answer = f"({mid_x}, {mid_y})"

    return {
        "question_text": question_text,
        "answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查使用者輸入的中點坐標是否正確。
    接受的格式: (x, y), (x,y), x, y, x,y
    """
    # 從 "(x, y)" 格式中提取數字
    correct_match = re.match(r'\(\s*(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)\s*\)', correct_answer)
    correct_x = float(correct_match.group(1))
    correct_y = float(correct_match.group(2))

    # 清理使用者輸入，使其能處理多種格式
    user_clean = user_answer.strip().replace('(', '').replace(')', '').replace(' ', '')
    
    try:
        parts = user_clean.split(',')
        if len(parts) != 2:
            return {"correct": False, "result": "請輸入兩個坐標值，並用逗號分隔。"}
        
        user_x = float(parts[0])
        user_y = float(parts[1])
        
        if abs(user_x - correct_x) < 1e-9 and abs(user_y - correct_y) < 1e-9:
            return {"correct": True, "result": "完全正確！"}
        else:
            return {"correct": False, "result": f"答案不正確。正確答案是 ({correct_x}, {correct_y})。"}

    except ValueError:
        return {"correct": False, "result": "請輸入有效的數字坐標，例如 '3, 5' 或 '(3,5)'。"}