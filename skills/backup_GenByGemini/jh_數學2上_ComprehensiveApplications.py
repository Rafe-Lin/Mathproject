import random

def generate(level=1):
    """
    生成應用乘法公式計算面積的應用題。
    此技能專注於將和的平方或差的平方公式應用於幾何面積問題。
    包含：
    1. 正方形增加 L 型邊框後的面積計算 ($(a+b)^2$)
    2. 正方形內部移除 L 型路徑後的面積計算 ($(a-b)^2$)
    """
    problem_type = random.choice(['add_border', 'remove_path'])
    
    if problem_type == 'add_border':
        return generate_addition_problem()
    else: # 'remove_path'
        return generate_subtraction_problem()

def generate_addition_problem():
    """
    題型：正方形增加 L 型邊框後的面積計算 ($(a+b)^2$)
    例如：在邊長為 a 的正方形外，加上寬為 b 的 L 型邊框，總面積為何？
    新邊長為 (a+b)，總面積為 (a+b)^2。
    """
    a = random.choice([10, 20, 30, 40, 50, 80, 100, 120])
    b = random.choice([0.1, 0.2, 0.3, 0.4, 0.5, 1.5, 2.5])
    
    # 將 b 格式化為字串，避免不必要的尾隨零 (e.g., 1.50 -> 1.5)
    b_str = f'{b:.2f}'.rstrip('0').rstrip('.')

    unit = random.choice(['公分', '公尺'])
    item = random.choice(['桌墊', '畫布', '磁磚', '草地', '地毯'])
    person = random.choice(['瑩芳', '小明', '志華', '美玲'])
    
    question_text = f"{person}在邊長為 ${a}$ {unit} 的正方形{item}外加了一條寬為 ${b_str}$ {unit} 的 L 型拼布，則{item}加了拼布後的面積總和為多少平方{unit}？"
    
    # 計算答案 (a+b)^2
    answer_val = (a + b)**2
    
    # 將答案格式化為字串，去除不必要的 .0，保留最多4位小數
    correct_answer = f'{answer_val:.4f}'.rstrip('0').rstrip('.')

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_subtraction_problem():
    """
    題型：正方形內部移除 L 型路徑後的面積計算 ($(a-b)^2$)
    例如：在邊長為 a 的正方形內，開闢一條寬為 b 的 L 型道路，剩餘面積為何？
    剩餘正方形邊長為 (a-b)，剩餘面積為 (a-b)^2。
    此題型可能包含單位換算。
    """
    person = random.choice(['阿榮伯', '陳先生', '林太太', '王叔叔'])
    item = random.choice(['土地', '花園', '木板', '庭院'])
    path_item = random.choice(['水泥道路', '走道', '水溝', '小徑'])
    
    # 約 1/3 的機率出現單位換算題
    use_conversion = random.choice([True, False, False])

    if use_conversion:
        # 主單位為公尺，道路寬度以公分給定
        a = random.choice([10, 20, 30, 40, 50]) # 公尺
        b_cm = random.choice([10, 20, 30, 40, 50, 60, 80]) # 公分
        b = b_cm / 100.0 # 換算成公尺
        
        question_text = f"{person}有一塊邊長 ${a}$ 公尺的正方形{item}，他規畫在土地內部開闢一條 ${b_cm}$ 公分寬的 L 型{path_item}，則扣除{path_item}後，剩餘的土地面積是多少平方公尺？"
    else:
        # 單位一致，無須換算
        unit = random.choice(['公分', '公尺'])
        if unit == '公尺':
            a = random.choice([10, 20, 30, 40, 50])
            b = random.choice([0.1, 0.2, 0.5, 1.2, 1.5])
        else: # 公分
            a = random.choice([50, 80, 100, 120, 150])
            b = random.choice([0.5, 1, 1.5, 2, 2.5])
        
        # 確保 b 遠小於 a，使題目合理
        while b >= a / 5:
            if unit == '公尺':
                b = random.choice([0.1, 0.2, 0.5, 1.2, 1.5])
            else:
                b = random.choice([0.5, 1, 1.5, 2, 2.5])

        b_str = f'{b:.2f}'.rstrip('0').rstrip('.')
        
        question_text = f"{person}有一塊邊長 ${a}$ {unit} 的正方形{item}，他規畫在內部開闢一條 ${b_str}$ {unit} 寬的 L 型{path_item}，則扣除{path_item}後，剩餘的面積是多少平方{unit}？"

    # 計算答案 (a-b)^2
    answer_val = (a - b)**2
    
    # 將答案格式化為字串，去除不必要的 .0
    correct_answer = f'{answer_val:.4f}'.rstrip('0').rstrip('.')

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查使用者答案是否正確，特別處理浮點數比較。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    
    try:
        # 轉換為浮點數進行比較，以處理潛在的格式差異 (例如 "90.25" vs "90.250")
        user_float = float(user_answer)
        correct_float = float(correct_answer)
        # 使用容差比較浮點數，避免浮點數精度問題
        is_correct = abs(user_float - correct_float) < 1e-9
    except (ValueError, TypeError):
        # 如果無法轉換為浮點數，則進行不分大小寫的字串比較
        is_correct = (user_answer.upper() == correct_answer.upper())

    if is_correct:
        result_text = f"完全正確！答案是 ${correct_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer}$"

    return {"correct": is_correct, "result": result_text, "next_question": True}