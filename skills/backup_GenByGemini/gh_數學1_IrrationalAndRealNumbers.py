import random

def generate(level=1):
    """
    生成「無理數與實數」相關題目。
    主要題型為利用無理數的性質，求解方程式中的有理數未知數。
    """
    # For this skill, we focus on the single main problem type demonstrated in the reference example.
    return generate_irrational_equation_problem()

def generate_irrational_equation_problem():
    """
    生成形如 $(c_1 + c_2\\sqrt{k})a + (c_3 + c_4\\sqrt{k})b = r_1 + r_2\\sqrt{k}$ 的題目，
    要求解有理數 $a, b$。
    """
    # 1. Choose integer solutions for a and b
    a = random.choice([i for i in range(-4, 5) if i != 0])
    b = random.choice([i for i in range(-4, 5) if i != 0])
    # Ensure a and b are not the same for more interesting problems
    while a == b:
        b = random.choice([i for i in range(-4, 5) if i != 0])

    # 2. Choose a non-perfect square k for the irrational part
    k = random.choice([2, 3, 5, 6, 7])

    # 3. Choose coefficients c1, c2, c3, c4 ensuring a unique solution exists.
    # The system of equations is:
    # c1*a + c3*b = r1
    # c2*a + c4*b = r2
    # The determinant of the coefficient matrix for (a, b) is c1*c4 - c3*c2, which must not be zero.
    while True:
        # Choose non-zero integer coefficients to avoid trivial terms
        c1 = random.choice([i for i in range(-5, 6) if i != 0])
        c2 = random.choice([i for i in range(-5, 6) if i != 0])
        c3 = random.choice([i for i in range(-5, 6) if i != 0])
        c4 = random.choice([i for i in range(-5, 6) if i != 0])
        if (c1 * c4 - c3 * c2) != 0:
            break

    # 4. Calculate the right-hand side r1 and r2
    r1 = c1 * a + c3 * b
    r2 = c2 * a + c4 * b

    # Helper function to format terms like (c_rat + c_irr*sqrt(k))
    def _format_term(c_rat, c_irr, k):
        # Case 1: Purely rational term
        if c_irr == 0:
            return str(c_rat)
        
        # Case 2: Purely irrational term
        if c_rat == 0:
            if abs(c_irr) == 1:
                return f"\\sqrt{{{k}}}" if c_irr > 0 else f"-\\sqrt{{{k}}}"
            else:
                return f"{c_irr}\\sqrt{{{k}}}"

        # Case 3: Mixed term (rational + irrational)
        rat_part = str(c_rat)
        sign = " + " if c_irr > 0 else " - "
        abs_c_irr = abs(c_irr)
        
        if abs_c_irr == 1:
            irr_part = f"\\sqrt{{{k}}}"
        else:
            irr_part = f"{abs_c_irr}\\sqrt{{{k}}}"
        
        return f"{rat_part}{sign}{irr_part}"

    term_a_str = f"({_format_term(c1, c2, k)})"
    term_b_str = f"({_format_term(c3, c4, k)})"
    rhs_str = _format_term(r1, r2, k)

    # Ensure the right-hand side is not empty if it calculates to zero
    if r1 == 0 and r2 == 0:
        rhs_str = "0"
        
    question_text = f"已知 $a, b$ 為有理數，且 ${term_a_str}a + {term_b_str}b = {rhs_str}$，求 $a, b$ 的值。<br>（答案請以 `a=值, b=值` 的格式作答，例如 `a=1, b=-2`）"
    
    # The correct answer string
    correct_answer = f"a={a}, b={b}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。此函數能處理答案順序不同、包含空格等情況。
    """
    def _parse_answer(ans_str):
        try:
            # Normalize: lowercase, remove spaces
            ans_str = ans_str.lower().replace(" ", "")
            # Split into parts by comma
            parts = ans_str.split(',')
            if len(parts) != 2:
                return None
            
            ans_dict = {}
            # Parse each part (e.g., 'a=1')
            for part in parts:
                key, val_str = part.split('=')
                # Ensure keys are 'a' and 'b'
                if key not in ['a', 'b']:
                    return None
                # Store value as float for robust comparison
                ans_dict[key] = float(val_str)
            
            # Check if both 'a' and 'b' are present
            if 'a' not in ans_dict or 'b' not in ans_dict:
                return None
                
            return ans_dict
        except (ValueError, IndexError):
            # Handle cases like 'a=', 'a=b', or other format errors
            return None

    user_dict = _parse_answer(user_answer)
    correct_dict = _parse_answer(correct_answer)
    
    is_correct = (user_dict is not None) and (user_dict == correct_dict)

    # Format the correct answer for display in feedback
    # Use int if the number is a whole number, otherwise float
    a_val = correct_dict['a']
    b_val = correct_dict['b']
    a_str = int(a_val) if a_val == int(a_val) else a_val
    b_str = int(b_val) if b_val == int(b_val) else b_val
    
    formatted_correct_answer = f"$a = {a_str}, b = {b_str}$"

    if is_correct:
        result_text = f"完全正確！答案是 {formatted_correct_answer}。"
    else:
        result_text = f"答案不正確。正確答案應為：{formatted_correct_answer}"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}