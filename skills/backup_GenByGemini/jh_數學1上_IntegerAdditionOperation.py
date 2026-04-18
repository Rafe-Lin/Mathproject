import random

def _format_term(n):
    """Helper function to format a number for display in a math expression."""
    return f"({n})" if n < 0 else str(n)

def generate_negative_plus_negative():
    """
    題型：負數＋負數。
    範例：(-9) + (-7) = -16
    """
    a = random.randint(1, 50)
    b = random.randint(1, 50)
    num1 = -a
    num2 = -b
    
    correct_answer = num1 + num2
    
    question_text = f"計算 ${'('}{num1}{')'} + {'('}{num2}{')'}$ 的值。"
    
    return {
        "question_text": question_text,
        "answer": str(correct_answer),
        "correct_answer": str(correct_answer)
    }

def generate_mixed_sign_addition():
    """
    題型：正數＋負數 或 負數＋正數。
    範例：13 + (-4) = 9  或  (-15) + 9 = -6
    """
    a = random.randint(1, 50)
    b = random.randint(1, 50)
    
    # 確保兩數不相等，以避免答案為 0 (這是 special_cases 的範疇)
    while a == b:
        b = random.randint(1, 50)
        
    if random.choice([True, False]):
        # 正 + 負
        num1 = a
        num2 = -b
    else:
        # 負 + 正
        num1 = -a
        num2 = b
        
    correct_answer = num1 + num2
    
    formatted_num1 = _format_term(num1)
    formatted_num2 = _format_term(num2)
    
    question_text = f"計算 ${formatted_num1} + {formatted_num2}$ 的值。"
    
    return {
        "question_text": question_text,
        "answer": str(correct_answer),
        "correct_answer": str(correct_answer)
    }

def generate_special_cases_addition():
    """
    題型：與 0 相加，或互為相反數的兩數相加。
    範例：(-18) + 0 = -18  或  13 + (-13) = 0
    """
    problem_subtype = random.choice(['zero', 'inverse'])
    
    if problem_subtype == 'zero':
        num1 = random.randint(-50, 50)
        num2 = 0
        if random.choice([True, False]): # 隨機交換順序
            num1, num2 = num2, num1
    else: # inverse
        num1 = random.randint(1, 50)
        num2 = -num1
        if random.choice([True, False]): # 隨機交換順序
            num1, num2 = num2, num1
            
    correct_answer = num1 + num2
    
    formatted_num1 = _format_term(num1)
    formatted_num2 = _format_term(num2)
    
    question_text = f"計算 ${formatted_num1} + {formatted_num2}$ 的值。"
    
    return {
        "question_text": question_text,
        "answer": str(correct_answer),
        "correct_answer": str(correct_answer)
    }

def generate_three_term_addition():
    """
    題型：三個整數相加，可利用交換律與結合律簡化。
    範例：132 + (-59) + (-132) 或 (-23) + 1205 + (-77)
    """
    problem_subtype = random.choice(['inverse_trick', 'combine_trick'])
    
    if problem_subtype == 'inverse_trick':
        # 包含一對相反數, e.g., a + b + (-a)
        a = random.randint(20, 200)
        b = random.randint(20, 200)
        while a == b or a == -b:
            b = random.randint(20, 200)
            
        terms = [a, b, -a]
        correct_answer = b
        
    else: # combine_trick
        # 兩個負數可以湊成整十或整百, e.g., a + (-b) + (-c) where b+c is nice
        nice_sum = random.choice([50, 100, 150, 200])
        b = random.randint(1, nice_sum - 1)
        c = nice_sum - b
        
        a = random.randint(nice_sum + 10, nice_sum + 300)
        
        terms = [a, -b, -c]
        correct_answer = a - nice_sum
        
    random.shuffle(terms)
    num1, num2, num3 = terms
    
    f1 = _format_term(num1)
    f2 = _format_term(num2)
    f3 = _format_term(num3)
    
    question_text = f"計算 ${f1} + {f2} + {f3}$ 的值。"
    
    return {
        "question_text": question_text,
        "answer": str(correct_answer),
        "correct_answer": str(correct_answer)
    }

def generate(level=1):
    """
    生成「整數的加法」相關題目。
    
    包含：
    1. 負數 + 負數
    2. 正負數相加
    3. 特殊情況 (與 0 相加、相反數相加)
    4. 三數相加 (利用運算律)
    """
    
    # 根據難度級別選擇題型
    # level 1: 基本的兩數相加
    # level 2: 包含特殊情況與三數相加
    if level == 1:
        problem_generators = [
            generate_negative_plus_negative,
            generate_mixed_sign_addition
        ]
    else: # level 2 and above
        problem_generators = [
            generate_negative_plus_negative,
            generate_mixed_sign_addition,
            generate_special_cases_addition,
            generate_three_term_addition
        ]

    # 從可用的題型中隨機選擇一個
    chosen_generator = random.choice(problem_generators)
    return chosen_generator()

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    
    is_correct = (user_answer == correct_answer)
    
    # 數值容錯 (例如使用者輸入了 +9 而非 9)
    if not is_correct:
        try:
            if int(user_answer) == int(correct_answer):
                is_correct = True
        except ValueError:
            # 如果無法轉換為整數，則保持原來的比較結果
            pass

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}