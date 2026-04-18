import random

def _format_num(n):
    """Formats a number for display, adding parentheses if it's negative."""
    return f"({n})" if n < 0 else str(n)

def generate(level=1):
    """
    生成「整數的乘法」相關題目。
    包含：
    1. 兩整數乘法 (正負數混合)
    2. 三整數乘法 (含交換律與結合律應用)
    3. 連續負整數乘積之正負號判斷
    """
    problem_type = random.choice(['two_integers', 'three_integers_trick', 'sign_determination'])
    
    if problem_type == 'two_integers':
        return generate_two_integer_multiplication()
    elif problem_type == 'three_integers_trick':
        return generate_three_integer_multiplication_trick()
    else: # 'sign_determination'
        return generate_sign_determination()

def generate_two_integer_multiplication():
    """
    題型：計算兩整數的乘積。
    對應課本例題 1, 2。
    """
    a = random.randint(2, 12)
    b = random.randint(2, 12)
    
    # 避免數字相同
    while a == b:
        b = random.randint(2, 12)

    # 隨機分配正負號
    num_a = a * random.choice([-1, 1])
    num_b = b * random.choice([-1, 1])
    
    # 格式化數字（負數加括號）
    str_a = _format_num(num_a)
    str_b = _format_num(num_b)
    
    question_text = f"計算 ${str_a} \\times {str_b}$ 的值。"
    correct_answer = str(num_a * num_b)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_three_integer_multiplication_trick():
    """
    題型：計算三整數的乘積，鼓勵使用乘法結合律或交換律。
    對應課本例題 3, 4。
    """
    trick_pairs = [(4, 25), (8, 125), (2, 50), (20, 5)]
    pair = random.choice(trick_pairs)
    
    third_num = random.randint(3, 19)
    # 避免第三個數字與配對中的數字相同
    while third_num in pair:
        third_num = random.randint(3, 19)

    # 隨機分配正負號
    nums = [
        pair[0] * random.choice([-1, 1]),
        pair[1] * random.choice([-1, 1]),
        third_num * random.choice([-1, 1])
    ]
    
    random.shuffle(nums)
    
    # 格式化數字
    str_nums = [_format_num(n) for n in nums]
    
    question_text = f"計算 ${str_nums[0]} \\times {str_nums[1]} \\times {str_nums[2]}$ 的值。"
    
    product = nums[0] * nums[1] * nums[2]
    correct_answer = str(product)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_sign_determination():
    """
    題型：判斷多個負整數連乘積的正負號。
    對應課本例題 5。
    """
    num_factors = random.randint(4, 9)
    
    # 產生多個不重複的負整數
    factors = random.sample(range(-20, -1), num_factors)
    
    # 格式化數字
    str_factors = [_format_num(n) for n in factors]
    
    expression = " \\times ".join(str_factors)
    
    question_text = f"不需計算出結果，請判斷 ${expression}$ 的計算結果為「正數」或「負數」？"
    
    # 負數個數為奇數，結果為負；若為偶數，結果為正。
    if num_factors % 2 == 0:
        correct_answer = "正數"
    else:
        correct_answer = "負數"
        
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
    
    if is_correct:
        result_text = f"完全正確！答案是 {correct_answer}。"
    else:
        result_text = f"答案不正確。正確答案應為：{correct_answer}"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}
