import random

def num_to_chinese(n):
    """將數字轉換為中文數字，用於題目生成。"""
    num_map = {
        3: '三', 4: '四', 5: '五', 6: '六', 7: '七', 8: '八', 9: '九', 10: '十',
        11: '十一', 12: '十二', 13: '十三', 14: '十四', 15: '十五', 16: '十六',
        17: '十七', 18: '十八', 19: '十九', 20: '二十', 24: '二十四'
    }
    return num_map.get(n, str(n))

def generate_interior_angle_sum_problem():
    """
    題型：給定邊數 n，求 n 邊形內角和。
    """
    n = random.randint(4, 20)
    angle_sum = (n - 2) * 180
    n_chinese = num_to_chinese(n)
    
    question_text = f"一個{n_chinese}邊形的內角和為多少度？"
    correct_answer = str(angle_sum)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_regular_interior_angle_problem():
    """
    題型：給定正 n 邊形，求每一個內角的度數。
    """
    # 選擇 n，使得 360/n 是整數，以得到整數角度
    valid_n = [4, 5, 6, 8, 9, 10, 12, 15, 18, 20, 24]
    n = random.choice(valid_n)
    interior_angle = 180 - (360 // n)
    n_chinese = num_to_chinese(n)
    
    question_text = f"一個正{n_chinese}邊形的每一個內角為多少度？"
    correct_answer = str(interior_angle)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_find_n_from_interior_angle_problem():
    """
    題型：給定正 n 邊形的一個內角度數，求 n。
    """
    valid_n = [4, 5, 6, 8, 9, 10, 12, 15, 18, 20, 24]
    n = random.choice(valid_n)
    interior_angle = 180 - (360 // n)
    
    question_text = f"若一個正 n 邊形的每一個內角為 ${interior_angle}^{{\\circ}}$，則 n 是多少？"
    correct_answer = str(n)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_find_n_from_exterior_angle_problem():
    """
    題型：給定正 n 邊形的一個外角度數，求 n。
    """
    valid_n = [4, 5, 6, 8, 9, 10, 12, 15, 18, 20, 24]
    n = random.choice(valid_n)
    exterior_angle = 360 // n
    
    question_text = f"若一個正 n 邊形的每一個外角為 ${exterior_angle}^{{\\circ}}$，則 n 是多少？"
    correct_answer = str(n)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_find_n_from_angle_ratio_problem():
    """
    題型：給定正 n 邊形內角與外角的倍數關係，求 n。
    """
    # 設內角 I = k * 外角 E。 I+E=180 => (k+1)E=180。
    # 為確保 E 是整數且為 360 的因數，選擇 k 使得 k+1 為 180 的因數。
    k_options = [2, 3, 4, 5, 8, 9, 11, 14, 17] # k+1 分別為 3, 4, 5, 6, 9, 10, 12, 15, 18
    k = random.choice(k_options)
    
    # 計算 n
    # E = 180 / (k+1)
    # n = 360 / E = 360 / (180 / (k+1)) = 2 * (k+1)
    n = 2 * (k + 1)
    
    # 隨機選擇問題的表述方式
    if random.random() < 0.5:
        # 內角是外角的 k 倍
        question_text = f"若正 n 邊形的一個內角度數恰好為一個外角度數的 ${k}$ 倍，則 n 是多少？"
    else:
        # 外角是內角的 1/k 倍
        frac_str = f"\\frac{{1}}{{{k}}}"
        question_text = f"若正 n 邊形的一個外角度數恰好為一個內角度數的 ${frac_str}$ 倍，則 n 是多少？"

    correct_answer = str(n)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def generate(level=1):
    """
    生成「多邊形內角與外角」相關題目。
    """
    problem_types = [
        'interior_angle_sum',
        'regular_interior_angle',
        'find_n_from_interior_angle',
        'find_n_from_exterior_angle',
        'find_n_from_angle_ratio'
    ]
    problem_type = random.choice(problem_types)
    
    if problem_type == 'interior_angle_sum':
        return generate_interior_angle_sum_problem()
    elif problem_type == 'regular_interior_angle':
        return generate_regular_interior_angle_problem()
    elif problem_type == 'find_n_from_interior_angle':
        return generate_find_n_from_interior_angle_problem()
    elif problem_type == 'find_n_from_exterior_angle':
        return generate_find_n_from_exterior_angle_problem()
    else: # find_n_from_angle_ratio
        return generate_find_n_from_angle_ratio_problem()

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    
    # 移除答案中的度數符號（如果有的話）
    user_answer = user_answer.replace('°', '').replace('度', '')
    
    is_correct = (user_answer == correct_answer)
    
    if not is_correct:
        try:
            # 比較浮點數以應對可能的輸入格式差異
            if float(user_answer) == float(correct_answer):
                is_correct = True
        except (ValueError, TypeError):
            pass

    if is_correct:
        result_text = f"完全正確！答案是 ${correct_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer}$。"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}