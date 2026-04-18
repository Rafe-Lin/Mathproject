import random
import math

def simplify_sqrt(n):
    """
    Simplifies a square root. For example, sqrt(32) becomes 4*sqrt(2).
    Returns a tuple (outside, inside).
    """
    if not isinstance(n, int) or n < 0:
        raise ValueError("Input must be a non-negative integer.")
    if n == 0:
        return (0, 1)
    
    # Use math.isqrt for integer square root, available in Python 3.8+
    i = math.isqrt(n)
    while i > 1:
        if n % (i * i) == 0:
            outside = i
            inside = n // (i * i)
            return (outside, inside)
        i -= 1
    
    return (1, n)

def generate_find_mean_problem():
    """
    Generates a problem asking to find the geometric mean of two numbers.
    Example: Given -4, k, -8 are in a geometric sequence, find k.
    """
    # Generate two numbers a and c such that their product is a positive, non-perfect square.
    # This ensures the answer involves a simplified square root.
    product = 1
    while math.isqrt(product)**2 == product:
        a_base = random.randint(2, 10)
        c_base = random.randint(2, 10)
        product = a_base * c_base

    sign = random.choice([1, -1])
    a = a_base * sign
    c = c_base * sign
    
    # Randomly shuffle the order of a and c for variety
    if random.choice([True, False]):
        a, c = c, a
        
    question_text = f"已知 ${a}$ , $k$ , ${c}$ 三數成等比數列，求 ${a}$ 與 ${c}$ 的等比中項 $k$=？"
    
    # The product is already calculated and is guaranteed positive
    outside, inside = simplify_sqrt(product)
    
    if inside == 1:
        ans_latex = f"{outside}"
    elif outside == 1:
        ans_latex = f"\\sqrt{{{inside}}}"
    else:
        ans_latex = f"{outside}\\sqrt{{{inside}}}"
        
    correct_answer = f"\\pm{ans_latex}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_product_of_three_problem():
    """
    Generates a problem asking for the product of three terms in a geometric sequence, given the middle term.
    """
    middle_term = random.randint(2, 10) * random.choice([-1, 1])
    product = middle_term ** 3
    
    question_text = f"有三數成等比數列，已知數列的第 2 項為 ${middle_term}$，則此三數的乘積為何？"
    correct_answer = str(product)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_symmetric_product_problem():
    """
    Generates a problem asking for the product of two symmetric terms in a geometric sequence, given the center term.
    """
    num_terms = random.choice([5, 7, 9, 11])
    middle_index = (num_terms + 1) // 2
    middle_value = random.randint(2, 12) * random.choice([-1, 1])
    
    product = middle_value ** 2
    
    # We will ask for the product of the first and last terms for clarity, as per the example.
    term_desc = "首項與末項"
        
    question_text = f"若一等比數列共有 ${num_terms}$ 項，已知數列的第 ${middle_index}$ 項為 ${middle_value}$，則此數列{term_desc}的乘積為何？"
    correct_answer = str(product)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    生成「等比中項」相關題目。
    包含：
    1. 求兩數的等比中項
    2. 給定中間項，求三數之積
    3. 給定奇數項數列的中間項，求對稱項之積
    """
    problem_type = random.choice(['find_mean', 'product_of_three', 'symmetric_product'])
    
    if problem_type == 'find_mean':
        return generate_find_mean_problem()
    elif problem_type == 'product_of_three':
        return generate_product_of_three_problem()
    else: # symmetric_product
        return generate_symmetric_product_problem()

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    # Normalize by removing spaces
    user_ans = user_answer.strip().replace(' ', '')
    corr_ans = correct_answer.strip().replace(' ', '')
    
    # Canonical representation for ± symbol to handle user input variations like 'pm' or '\\pm'
    user_ans = user_ans.replace('pm', '±').replace('\\pm', '±')
    corr_ans = corr_ans.replace('pm', '±').replace('\\pm', '±')

    is_correct = (user_ans == corr_ans)

    # Fallback for simple numeric answers, which covers two of the three problem types.
    if not is_correct:
        try:
            if float(user_ans) == float(corr_ans):
                is_correct = True
        except (ValueError, TypeError):
            # This can happen if one of the answers contains non-numeric characters (e.g., 'sqrt'),
            # in which case the string comparison is the only valid check.
            pass

    # The result text should display the answer in proper LaTeX format.
    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}