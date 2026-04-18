import random
import re
from fractions import Fraction

def generate(level=1):
    """
    生成「數線上的距離」相關題目。
    技能: jh_數學1上_DistanceBetweenTwoPointsOnNumberLine
    
    包含三種題型：
    1.  給定兩點座標，求兩點距離。
    2.  給定一點座標與距離，求另一點的可能座標。
    3.  給定兩點座標，求中點座標。
    """
    # 隨機選擇一個題型生成器函數
    problem_generators = [
        generate_distance_given_two_points,
        generate_point_given_distance,
        generate_midpoint_problem
    ]
    chosen_generator = random.choice(problem_generators)
    return chosen_generator()

def generate_distance_given_two_points():
    """
    題型：給定兩點座標 A(a)、B(b)，求兩點距離 AB。
    對應例題 1, 2
    """
    # 產生兩個不重複的整數座標
    val_a = random.randint(-20, 20)
    val_b = val_a
    while val_b == val_a:
        val_b = random.randint(-20, 20)

    # 計算距離
    distance = abs(val_a - val_b)

    # 組合問題文字
    # 範例: 數線上有 A(-9)、B(6) 兩點，則 A、B 兩點的距離 AB 為多少？
    question_text = f"數線上有 A(${val_a}$)、B(${val_b}$) 兩點，則 A、B 兩點的距離 $\\overline{{AB}}$ 為多少？"
    
    # 正確答案
    correct_answer = str(distance)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_point_given_distance():
    """
    題型：給定一點座標 B(b) 與距離 AB=d，求另一點 A(a) 的可能座標。
    對應例題 3, 4
    """
    # 產生基準點座標與距離
    val_b = random.randint(-15, 15)
    distance = random.randint(2, 12)
    
    # 計算可能的兩個座標
    ans1 = val_b + distance
    ans2 = val_b - distance
    
    # 確保答案順序一致，由小到大
    answers = sorted([ans1, ans2])
    
    # 組合問題文字
    # 範例: 數線上有 A(a)、B(5) 兩點，如果 AB=3，則 a 可能是多少？
    question_text = f"數線上有 A(a)、B(${val_b}$) 兩點，如果兩點的距離 $\\overline{{AB}} = {distance}$，則 a 可能是多少？"
    
    # 正確答案格式為 "ans_small 或 ans_large"
    correct_answer = f"{answers[0]} 或 {answers[1]}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_midpoint_problem():
    """
    題型：給定兩點座標 A(a)、B(b)，求中點座標 C(c)。
    對應例題 5, 6
    """
    # 產生起始點座標
    val_a = random.randint(-20, 20)
    
    # 80% 的機率讓中點是整數 (偶數距離)
    if random.random() < 0.8:
        diff = random.randint(2, 12) * 2 # 產生偶數距離
    else:
        diff = random.randint(2, 12) * 2 - 1 # 產生奇數距離
        
    # 隨機決定第二點在第一點的左邊或右邊
    if random.random() < 0.5:
        val_b = val_a + diff
    else:
        val_b = val_a - diff
        
    # 計算中點
    midpoint = (val_a + val_b) / 2
    
    # 格式化答案
    if midpoint.is_integer():
        midpoint_str = str(int(midpoint))
    else:
        midpoint_str = str(midpoint) # 結果會是 x.5
        
    # 組合問題文字
    # 範例: 數線上有 A(5)、B(-11)、C(c) 三點，若 C 為 A、B 的中點，則 c 是多少？
    question_text = f"數線上有 A(${val_a}$)、B(${val_b}$)、C(c) 三點，若 C 為 A、B 的中點，則 c 是多少？"
    correct_answer = midpoint_str
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    能處理單一數字答案，以及 "A 或 B" 形式的答案。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()

    is_correct = False
    
    # 題型1: 答案包含 "或" (e.g., "8 或 2")
    if "或" in correct_answer:
        # 將正確答案拆解為集合，以便比對，忽略順序
        correct_parts = set(part.strip() for part in correct_answer.split("或"))
        
        # 從使用者答案中提取所有數字 (包括負數和小數)
        user_numbers = re.findall(r'-?\\d+\\.?\\d*', user_answer)
        user_parts = set(user_numbers)
        
        # 比較兩個集合是否相等
        if user_parts == correct_parts:
            is_correct = True
            
    # 題型2: 單一數字答案
    else:
        # 直接比對字串
        if user_answer == correct_answer:
            is_correct = True
        else:
            # 嘗試用浮點數比對，增加容錯 (e.g., 2.5 vs 2.50)
            try:
                if float(user_answer) == float(correct_answer):
                    is_correct = True
            except (ValueError, TypeError):
                # 如果無法轉換為數字，則判定為錯誤
                pass

    # 根據比對結果生成回饋文字
    # 將答案用 $...$ 包裹以利前端 LaTeX 渲染
    if is_correct:
        result_text = f"完全正確！答案是 ${correct_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer}$"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}
