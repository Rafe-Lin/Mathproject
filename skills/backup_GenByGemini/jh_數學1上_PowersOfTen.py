import random

def generate(level=1):
    """
    生成「10的次方」相關題目。
    包含：
    1. 10的次方轉數字 (整數/小數)
    2. 數字轉10的次方
    3. 10的負次方轉分數
    4. 綜合填空題
    """
    problem_types = [
        'power_to_number', 
        'number_to_power', 
        'power_to_fraction', 
        'fill_in_the_blanks'
    ]
    problem_type = random.choice(problem_types)
    
    if problem_type == 'power_to_number':
        return generate_power_to_number()
    elif problem_type == 'number_to_power':
        return generate_number_to_power()
    elif problem_type == 'power_to_fraction':
        return generate_power_to_fraction()
    else: # 'fill_in_the_blanks'
        return generate_fill_in_the_blanks()

def generate_power_to_number():
    """
    題型：將 10 的 n 次方轉為數字 (整數或小數)
    """
    is_positive_exp = random.choice([True, False])
    
    if is_positive_exp:
        exp = random.randint(2, 8)
        question_text = f"請問 $10^{{{exp}}}$ 的值是多少？"
        correct_answer = str(10**exp)
    else:
        exp = random.randint(2, 8)
        question_text = f"請將 $10^{{{-exp}}}$ 以小數表示。"
        # Format to avoid scientific notation e.g., 1e-7
        correct_answer = f"{10**(-exp):.{exp}f}"
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "input_type": "text"
    }

def generate_number_to_power():
    """
    題型：將數字 (如 1000 或 0.001) 轉為 10 的 n 次方，求 n
    """
    is_integer = random.choice([True, False])
    
    if is_integer:
        exp = random.randint(2, 8)
        num = 10**exp
        question_text = f"若 ${num:,} = 10^x$，則 $x$ 的值為何？"
        correct_answer = str(exp)
    else:
        exp = random.randint(2, 8)
        num_str = f"{10**(-exp):.{exp}f}"
        question_text = f"若 ${num_str} = 10^y$，則 $y$ 的值為何？"
        correct_answer = str(-exp)
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "input_type": "text"
    }

def generate_power_to_fraction():
    """
    題型：將 10 的負 n 次方轉為分數
    """
    exp = random.randint(2, 9)
    denominator = 10**exp
    
    question_text = f"請將 $10^{{{-exp}}}$ 以分數表示。"
    # LaTeX format for fraction, with thousands separators for readability
    correct_answer = f"\\frac{{1}}{{{denominator:,}}}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "input_type": "handwriting"
    }

def generate_fill_in_the_blanks():
    """
    題型：綜合填空，如 0.001 = 1/1000 = 1/10^3 = 10^-3
    """
    exp = random.randint(3, 7)
    
    decimal_str = f"{10**(-exp):.{exp}f}"
    denominator_num = 10**exp
    
    question_text = (
        f"在下列式子的括號中填入適當的數：<br>"
        f"${decimal_str} = \\frac{{1}}{{( A )}} = \\frac{{1}}{{10^{{( B )}}}} = 10^{{( C )}}$<br>"
        f"請依序寫出 A, B, C 的值 (答案用逗號分隔)。"
    )
    
    answer_a = str(denominator_num)
    answer_b = str(exp)
    answer_c = str(-exp)
    
    correct_answer = f"{answer_a},{answer_b},{answer_c}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "input_type": "text"
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    # 標準化使用者輸入：去除頭尾空白，並將全形逗號轉為半形
    user_answer = user_answer.strip().replace("－", "-").replace("，", ",")
    
    # 對於多部分答案，移除數字和逗號之間的空格以進行比較
    if ',' in correct_answer:
        user_answer = "".join(user_answer.split())

    is_correct = (user_answer == correct_answer)

    # 為了在結果中更好地顯示 LaTeX 答案，進行格式化處理
    display_answer = correct_answer
    if "\\frac" in correct_answer:
        display_answer = f"${correct_answer}$"

    result_text = f"完全正確！答案是 {display_answer}。" if is_correct else f"答案不正確。正確答案應為：{display_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}
