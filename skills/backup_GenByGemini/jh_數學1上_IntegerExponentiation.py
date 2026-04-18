import random
import math

def generate(level=1):
    """
    生成「整數的乘方」相關題目 (標準 LaTeX 範本)。
    包含：
    1. 基本乘方計算
    2. 指數形式簡記
    3. 四則運算與乘方混合
    """
    # 根據難度調整題型權重，此處暫定平均分配
    problem_type = random.choice(['basic_calculation', 'exponential_form', 'order_of_operations'])
    # 可根據 level 調整權重，例如 level 越高，order_of_operations 權重越高
    # if level == 1:
    #     problem_type = random.choices(['basic_calculation', 'exponential_form'], weights=[3, 1], k=1)[0]
    # else:
    #     problem_type = random.choices(['basic_calculation', 'order_of_operations'], weights=[1, 2], k=1)[0]
    
    if problem_type == 'basic_calculation':
        return generate_basic_calculation_problem()
    elif problem_type == 'exponential_form':
        return generate_exponential_form_problem()
    else: # order_of_operations
        return generate_order_of_operations_problem()

def generate_basic_calculation_problem():
    """生成基本乘方計算題，比較 (-a)^n, -a^n, a^n 的區別"""
    base = random.randint(2, 9)
    exponent = random.randint(2, 4)
    
    form_type = random.choice(['positive', 'negative_in', 'negative_out'])
    
    if form_type == 'positive':
        # 題型： a^n
        latex_expr = f"{base}^{{{exponent}}}"
        correct_value = base ** exponent
    elif form_type == 'negative_in':
        # 題型： (-a)^n
        latex_expr = f"(-{base})^{{{exponent}}}"
        correct_value = (-base) ** exponent
    else: # negative_out
        # 題型： -a^n
        latex_expr = f"-{base}^{{{exponent}}}"
        correct_value = -(base ** exponent)

    question_text = f"計算下列各式的值。\n${latex_expr}$"
    correct_answer = str(correct_value)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_exponential_form_problem():
    """生成將連乘式以指數形式簡記的題目"""
    base = random.choice([*range(2, 10), *range(-9, -1)])
    reps = random.randint(3, 5)
    
    base_str = str(base) if base > 0 else f"({base})"
    
    # 產生連乘的字串, e.g., "(-5) \\times (-5) \\times (-5)"
    mult_list = [base_str] * reps
    mult_str = " \\times ".join(mult_list)
    
    question_text = f"以指數的形式簡記下列各式。\n${mult_str} = \_\_\_\_\_ 。$"
    
    # 答案不需要包含$，以便檢查函數比對
    if base > 0:
        correct_answer = f"{base}^{{{reps}}}"
    else:
        correct_answer = f"({base})^{{{reps}}}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def _get_factors(n):
    """輔助函數：取得一個數的所有正因數"""
    n = abs(n)
    factors = set()
    for i in range(1, int(math.sqrt(n)) + 1):
        if n % i == 0:
            factors.add(i)
            factors.add(n//i)
    return sorted(list(factors))

def generate_order_of_operations_problem():
    """生成含乘方的四則運算題"""
    template = random.choice(['template1', 'template2', 'template3', 'template4'])
    
    if template == 'template1':
        # 範本： (-a^2) ÷ a - b^3
        a = random.randint(2, 6)
        b = random.randint(2, 3)
        latex_expr = f"(-{a}^2) \\div {a} - {b}^3"
        correct_value = (-(a**2)) // a - (b**3)
    elif template == 'template2':
        # 範本： c - a^3 × [ d + (-b^2) ]
        a = random.randint(2, 3)
        b = random.randint(2, 5)
        c = random.randint(1, 20)
        d = random.randint(1, 20)
        # 確保 d + (-b^2) 不為 0，避免答案過於簡單
        while d == b**2:
            d = random.randint(1, 20)
        latex_expr = f"{c} - {a}^3 \\times [ {d} + (-{b}^2) ]"
        correct_value = c - (a**3) * (d + (-(b**2)))
    elif template == 'template3':
        # 範本： [ -(-a)^2 + b ] ÷ c
        a = random.randint(2, 5)
        b = random.randint(1, 20)
        numerator = -((-a)**2) + b
        # 避免分子為0
        while numerator == 0:
            a = random.randint(2, 5)
            b = random.randint(1, 20)
            numerator = -((-a)**2) + b
        
        factors = _get_factors(numerator)
        c = random.choice(factors)
        
        latex_expr = f"[ -(-{a})^2 + {b} ] \\div {c}"
        correct_value = numerator // c
    else: # template4
        # 範本： a - (-b) ÷ (-c)^2
        c = random.randint(2, 5)
        # 確保 b 是 c^2 的倍數
        b_multiple = random.randint(1, 5)
        b = (c**2) * b_multiple
        a = random.randint(-100, -50)

        latex_expr = f"{a} - (-{b}) \\div (-{c})^2"
        correct_value = a - (-b) // ((-c)**2)

    question_text = f"計算下列各式的值。\n${latex_expr}$"
    correct_answer = str(correct_value)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    # 去除使用者答案中的所有空白字元，方便比對
    user_answer = user_answer.strip().replace(' ', '')
    correct_answer = correct_answer.strip().replace(' ', '')
    
    is_correct = (user_answer.lower() == correct_answer.lower())
    
    # 如果是純數字答案，嘗試用浮點數比較，允許 '5' 和 '5.0' 等價
    if not is_correct:
        try:
            if float(user_answer) == float(correct_answer):
                is_correct = True
        except (ValueError, TypeError):
            # 答案可能包含 '^' 或 '()' 等符號，無法轉換為浮點數，此時維持字串比對結果
            pass

    # 為了美觀，在結果中用 LaTeX 格式化正確答案
    correct_answer_latex = f"${correct_answer}$"

    if is_correct:
        result_text = f"完全正確！答案是 {correct_answer_latex}。"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer_latex}"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}
