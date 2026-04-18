# skills/dist_formula_1d.py
import random
import re
import ast

def generate(level=1):
    """生成「數線上的距離公式」題目"""
    question_type = random.choice([
        'distance_given_points',    # 給定兩點求距離
        'point_given_distance'       # 給定一點和距離，求另一點（單一答案）
    ])
    # level 參數暫時未使用，但保留以符合架構
    
    if question_type == 'distance_given_points':
        # 給定兩點，求距離
        point1 = random.randint(-10, 10)
        point2 = random.randint(-10, 10)
        while point1 == point2:
            point2 = random.randint(-10, 10)
        
        distance = abs(point2 - point1)
        
        question_text = f"數線上 A({point1}) 與 B({point2}) 兩點的距離是多少？\n\n請使用距離公式：AB = |x2 - x1|"
        context_string = f"使用距離公式計算數線上 A({point1}) 與 B({point2}) 兩點的距離"
        
        return {
            "question_text": question_text,
            "answer": str(distance),
            "correct_answer": str(distance),
            "context_string": context_string
        }
    
    elif question_type == 'point_given_distance':
        # 給定一點和距離，求另一點（單一答案）
        point1 = random.randint(-8, 8)
        distance = random.randint(2, 8)
        
        # 隨機選擇在左邊或右邊
        if random.choice([True, False]):
            point2 = point1 + distance
        else:
            point2 = point1 - distance
        
        # 確保點在合理範圍內
        if point2 < -15 or point2 > 15:
            point2 = point1 - distance if point2 > 15 else point1 + distance
        
        question_text = f"數線上 A 點坐標為 {point1}，若 A 與 B 兩點的距離為 {distance}，且 B 在 A 的{'右側' if point2 > point1 else '左側'}，求 B 點坐標。\n\n請使用距離公式：AB = |x2 - x1|"
        context_string = f"已知 A({point1}) 與 B 的距離為 {distance}，且 B 在 A 的{'右側' if point2 > point1 else '左側'}，求 B 點坐標"
        
        return {
            "question_text": question_text,
            "answer": str(point2),
            "correct_answer": str(point2),
            "context_string": context_string
        }
    

def check(user_answer, correct_answer):
    """檢查答案"""
    if correct_answer is None:
        return {"correct": False, "result": "系統錯誤：缺少正確答案"}
    
    user = user_answer.strip()
    
    # 處理 correct_answer 可能是列表字符串的情況（如 "['-4', '8']"）
    if isinstance(correct_answer, str) and correct_answer.startswith('[') and correct_answer.endswith(']'):
        try:
            correct_answer = ast.literal_eval(correct_answer)
        except:
            pass
    
    # 處理多個正確答案的情況（兩個可能的點）
    # 檢查 correct_answer 是否為列表，或者是否為包含多個答案的字符串
    if isinstance(correct_answer, list):
        # 嘗試從用戶輸入中提取數字（處理"8或-4"這種格式）
        numbers = re.findall(r'-?\d+\.?\d*', user)
        
        # 如果有提取到數字，檢查第一個數字
        if numbers:
            try:
                user_num = float(numbers[0])
                for ans in correct_answer:
                    correct_num = float(ans)
                    if abs(user_num - correct_num) < 0.01:  # 允許小數誤差
                        return {"correct": True, "result": "正確！"}
            except (ValueError, IndexError):
                pass
        
        # 如果沒有提取到數字，嘗試直接轉換整個輸入
        try:
            user_num = float(user)
            for ans in correct_answer:
                correct_num = float(ans)
                if abs(user_num - correct_num) < 0.01:  # 允許小數誤差
                    return {"correct": True, "result": "正確！"}
        except ValueError:
            pass
        
        # 如果都不匹配，顯示兩個可能的答案
        return {"correct": False, "result": f"錯誤，請輸入一個數字（任選一個答案）。正解：{correct_answer[0]} 或 {correct_answer[1]}"}
    
    # 處理單一答案的情況
    # 如果 correct_answer 是字符串但包含逗號分隔的兩個答案
    if isinstance(correct_answer, str) and ',' in correct_answer:
        answers = [a.strip() for a in correct_answer.split(',')]
        try:
            user_num = float(user)
            for ans in answers:
                correct_num = float(ans)
                if abs(user_num - correct_num) < 0.01:
                    return {"correct": True, "result": "正確！"}
            return {"correct": False, "result": f"錯誤，請輸入一個數字。正解：{answers[0]} 或 {answers[1]}"}
        except ValueError:
            return {"correct": False, "result": f"錯誤，請輸入一個數字。正解：{answers[0]} 或 {answers[1]}"}
    
    # 處理單一答案的情況
    correct = str(correct_answer).strip()
    
    # 處理數值答案
    try:
        user_num = float(user)
        correct_num = float(correct)
        if abs(user_num - correct_num) < 0.01:  # 允許小數誤差
            return {"correct": True, "result": "正確！"}
        else:
            return {"correct": False, "result": f"錯誤，正解：{correct_answer}"}
    except ValueError:
        return {"correct": False, "result": f"錯誤，請輸入數字。正解：{correct_answer}"}
