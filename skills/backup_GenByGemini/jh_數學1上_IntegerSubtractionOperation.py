import random

def generate(level=1):
    """
    生成國中一年級上學期「整數的減法」相關題目。
    包含四種基本題型：
    1. 正數 - 正數
    2. 正數 - 負數
    3. 負數 - 正數
    4. 負數 - 負數
    """
    problem_type = random.choice([
        'pos_minus_pos', 
        'pos_minus_neg', 
        'neg_minus_pos', 
        'neg_minus_neg'
    ])
    
    if problem_type == 'pos_minus_pos':
        return generate_pos_minus_pos_problem(level)
    elif problem_type == 'pos_minus_neg':
        return generate_pos_minus_neg_problem(level)
    elif problem_type == 'neg_minus_pos':
        return generate_neg_minus_pos_problem(level)
    else: # 'neg_minus_neg'
        return generate_neg_minus_neg_problem(level)

def _get_number_range(level):
    """根據難度等級回傳數字範圍"""
    if level == 1:
        return (1, 30)
    elif level == 2:
        return (20, 100)
    else: # level 3 or higher
        return (50, 200)

def generate_pos_minus_pos_problem(level):
    """
    題型：正數 - 正數 (a - b)
    範例：14 - 23
    """
    min_val, max_val = _get_number_range(level)
    a = random.randint(min_val, max_val)
    b = random.randint(min_val, max_val)
    
    # 避免 a = b，使得答案為 0，過於簡單
    while a == b:
        b = random.randint(min_val, max_val)
        
    result = a - b
    
    question_text = f"計算下列各式的值：\n$ {a} - {b} $"
    correct_answer = str(result)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_pos_minus_neg_problem(level):
    """
    題型：正數 - 負數 (a - (-b))
    範例：125 - (-25)
    """
    min_val, max_val = _get_number_range(level)
    a = random.randint(min_val, max_val)
    b = random.randint(min_val, max_val)
    
    result = a - (-b)
    
    question_text = f"計算下列各式的值：\n$ {a} - ( -{b} ) $"
    correct_answer = str(result)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_neg_minus_pos_problem(level):
    """
    題型：負數 - 正數 ((-a) - b)
    範例：(-63) - 37
    """
    min_val, max_val = _get_number_range(level)
    a = random.randint(min_val, max_val)
    b = random.randint(min_val, max_val)
    
    result = (-a) - b
    
    question_text = f"計算下列各式的值：\n$ ( -{a} ) - {b} $"
    correct_answer = str(result)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_neg_minus_neg_problem(level):
    """
    題型：負數 - 負數 ((-a) - (-b))
    範例：(-133) - (-13)
    """
    min_val, max_val = _get_number_range(level)
    a = random.randint(min_val, max_val)
    b = random.randint(min_val, max_val)

    # 避免 a = b
    while a == b:
        b = random.randint(min_val, max_val)
        
    result = (-a) - (-b)
    
    question_text = f"計算下列各式的值：\n$ ( -{a} ) - ( -{b} ) $"
    correct_answer = str(result)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }
    
def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    
    is_correct = (user_answer == correct_answer)
    
    # 增加對浮點數表示法的容錯，例如使用者輸入 '-9.0' 而非 '-9'
    if not is_correct:
        try:
            if float(user_answer) == float(correct_answer):
                is_correct = True
        except (ValueError, TypeError):
            pass

    if is_correct:
        result_text = f"完全正確！答案是 ${correct_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer}$"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}