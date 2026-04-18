# skills/num_line_basic.py
import random

def generate(level=1):
    """生成「數線基礎與坐標」題目"""
    question_type = random.choice([
        'opposite',      # 相反數
        'coordinate',    # 標定坐標
        'distance',      # 數線距離
        'midpoint',      # 中點
        'compare'        # 比較大小
    ])
    # level 參數暫時未使用，但保留以符合架構
    
    if question_type == 'opposite':
        # 相反數題目
        num = random.choice([random.randint(-10, 10), random.choice([-5, -3, -2, -1, 1, 2, 3, 5])])
        opposite = -num
        
        question_text = f"請問 {num} 的相反數是多少？"
        context_string = f"求 {num} 的相反數"
        
        return {
            "question_text": question_text,
            "answer": str(opposite),
            "correct_answer": str(opposite),
            "context_string": context_string
        }
    
    elif question_type == 'coordinate':
        # 標定坐標題目（圖形題）
        num = random.choice([
            random.randint(-8, 8),
            random.choice([-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]),
            round(random.uniform(-5, 5), 1)  # 小數
        ])
        
        # 簡化小數顯示
        if isinstance(num, float):
            if num == int(num):
                num = int(num)
            else:
                num = round(num, 1)
        
        question_text = (
            f"請在下方的「數位計算紙」上，在數線上標定坐標 {num} 的位置。\n\n"
            f"畫完後，請點擊「AI 檢查」按鈕。"
        )
        
        return {
            "question_text": question_text,
            "answer": None,
            "correct_answer": "graph",
            "context_string": f"在數線上標定坐標 {num}"
        }
    
    elif question_type == 'distance':
        # 數線距離題目
        point1 = random.randint(-5, 5)
        point2 = random.randint(-5, 5)
        while point1 == point2:
            point2 = random.randint(-5, 5)
        
        distance = abs(point2 - point1)
        
        question_text = f"數線上 A({point1}) 與 B({point2}) 兩點的距離是多少？"
        context_string = f"計算數線上 A({point1}) 與 B({point2}) 兩點的距離"
        
        return {
            "question_text": question_text,
            "answer": str(distance),
            "correct_answer": str(distance),
            "context_string": context_string
        }
    
    elif question_type == 'midpoint':
        # 中點題目
        point1 = random.randint(-5, 5)
        point2 = random.randint(-5, 5)
        while point1 == point2:
            point2 = random.randint(-5, 5)
        
        midpoint = (point1 + point2) / 2
        
        # 簡化中點顯示
        if midpoint == int(midpoint):
            midpoint = int(midpoint)
        else:
            midpoint = round(midpoint, 1)
        
        question_text = f"數線上 A({point1}) 與 B({point2}) 兩點的中點坐標是多少？"
        context_string = f"求數線上 A({point1}) 與 B({point2}) 兩點的中點坐標"
        
        return {
            "question_text": question_text,
            "answer": str(midpoint),
            "correct_answer": str(midpoint),
            "context_string": context_string
        }
    
    else:  # compare
        # 比較大小題目
        num1 = random.randint(-5, 5)
        num2 = random.randint(-5, 5)
        while num1 == num2:
            num2 = random.randint(-5, 5)
        
        if num1 > num2:
            correct_answer = ">"
            answer_text = f"{num1} 大於 {num2}"
        else:
            correct_answer = "<"
            answer_text = f"{num1} 小於 {num2}"
        
        question_text = f"請比較數線上 {num1} 與 {num2} 的大小關係（請回答 '>' 或 '<'）"
        context_string = f"比較數線上 {num1} 與 {num2} 的大小關係"
        
        return {
            "question_text": question_text,
            "answer": correct_answer,
            "correct_answer": correct_answer,
            "context_string": context_string
        }

def check(user_answer, correct_answer):
    """檢查答案"""
    if correct_answer is None:
        return {"correct": False, "result": "系統錯誤：缺少正確答案"}
    
    # 處理圖形題（標定坐標）
    if correct_answer == "graph":
        return {
            "correct": False,
            "result": "請使用畫筆在數線上標定坐標，然後點選「AI 檢查」",
            "next_question": False
        }
    
    user = user_answer.strip()
    correct = str(correct_answer).strip()
    
    # 處理數值答案（相反數、距離、中點）
    try:
        user_num = float(user)
        correct_num = float(correct)
        if abs(user_num - correct_num) < 0.01:  # 允許小數誤差
            return {"correct": True, "result": "正確！"}
        else:
            return {"correct": False, "result": f"錯誤，正解：{correct_answer}"}
    except ValueError:
        pass
    
    # 處理文字答案（如比較大小）
    if user.lower() == correct.lower():
        return {"correct": True, "result": "正確！"}
    
    # 處理比較符號
    if user in ['>', '大於', 'greater'] and correct == '>':
        return {"correct": True, "result": "正確！"}
    if user in ['<', '小於', 'less'] and correct == '<':
        return {"correct": True, "result": "正確！"}
    
    return {"correct": False, "result": f"錯誤，正解：{correct_answer}"}
