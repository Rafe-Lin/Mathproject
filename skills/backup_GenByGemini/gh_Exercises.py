import random
import math
from fractions import Fraction

def generate(level=1):
    """
    生成「綜合練習」相關題目，包含觀念澄清、基礎題與進階題。
    """
    problem_types = [
        'exponent_evaluation',
        'algebraic_exponent_simplification',
        'true_false_statement',
        'trigonometric_calculation'
    ]

    # Level could influence the difficulty or specific types chosen
    # For a comprehensive unit, we'll randomly pick from the available types.
    # More advanced levels could prioritize certain types or add complexity within types.
    # For now, level=1 just ensures a mix of the implemented types.

    problem_type = random.choice(problem_types)
    
    if problem_type == 'exponent_evaluation':
        return generate_exponent_evaluation()
    elif problem_type == 'algebraic_exponent_simplification':
        return generate_algebraic_exponent_simplification()
    elif problem_type == 'true_false_statement':
        return generate_true_false_statement()
    elif problem_type == 'trigonometric_calculation':
        return generate_trigonometric_calculation()
    
    # Fallback, though one of the above should always be chosen
    return generate_exponent_evaluation()

def generate_exponent_evaluation():
    """
    生成指數/根式求值題目，例如 (27)^(2/3) 或 (16/25)^(-1/2)。
    """
    is_fractional_base = random.random() < 0.5
    
    if is_fractional_base:
        # Base is a fraction (e.g., (16/81))
        root_val = random.choice([2, 3, 4]) # q in p/q (e.g., for (x/y)^q)
        num_base_val = random.randint(2, 5) # b_num (e.g., 2 in (2/3)^4)
        den_base_val = random.randint(2, 5) # b_den (e.g., 3 in (2/3)^4)
        while num_base_val == den_base_val: # Avoid trivial base of 1
            den_base_val = random.randint(2, 5)
        
        base_num = num_base_val ** root_val
        base_den = den_base_val ** root_val
        
        exponent_power = random.randint(1, root_val + 1) # p in p/q
        
        if random.random() < 0.5: # Apply negative exponent
            exponent_power *= -1
        
        question_text = f"求下列各式的值：<br>$({{{base_num}}}/{{{base_den}}})^{{{{ {exponent_power}/{root_val} }}}}$"
        
        # Calculate (num_base_val / den_base_val) ** exponent_power
        # If exponent_power is positive: (num_base_val^exponent_power) / (den_base_val^exponent_power)
        # If exponent_power is negative: (den_base_val^-exponent_power) / (num_base_val^-exponent_power)
        
        if exponent_power < 0: # Flip fraction for negative exponent
            temp_num = den_base_val
            temp_den = num_base_val
            actual_power = -exponent_power
        else:
            temp_num = num_base_val
            temp_den = den_base_val
            actual_power = exponent_power
            
        result_num = temp_num ** actual_power
        result_den = temp_den ** actual_power
        
        correct_answer_frac = Fraction(result_num, result_den)
        correct_answer = str(correct_answer_frac)

    else: # Integer base (e.g., 27)
        root_val = random.choice([2, 3, 4, 5])
        base_val_root = random.randint(2, 6) # b in b^q
        base = base_val_root ** root_val # B = b^q (e.g., 3^3=27)
        
        exponent_power = random.randint(1, root_val + 1)
        if random.random() < 0.5: # Apply negative exponent
            exponent_power *= -1
        
        question_text = f"求下列各式的值：<br>$({base})^{{{{ {exponent_power}/{root_val} }}}}$"
        
        result_val = base_val_root ** exponent_power
        
        if exponent_power < 0:
            correct_answer = str(Fraction(1, result_val))
        else:
            correct_answer = str(result_val)
            
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_algebraic_exponent_simplification():
    """
    生成代數指數化簡題目，例如 (a^x * a^y)^z。
    答案格式會是 'a^N' 或 '1/a^N' 或 '1' 或 'a'。
    """
    x = random.randint(-4, 4)
    y = random.randint(-4, 4)
    z = random.randint(-4, 4)
    
    # Ensure exponents are not trivially 0 or 1 for base cases, for more varied questions
    if x in [0, 1]: x = random.choice([-2, 2, 3])
    if y in [0, 1]: y = random.choice([-2, 2, 3])
    if z in [0, 1]: z = random.choice([-2, 2, 3])

    op_type = random.choice(['mul_then_pow', 'div_then_pow', 'mixed_fractional'])
    
    question_text = ""
    final_exponent = Fraction(0, 1) # Initialize as Fraction
    
    if op_type == 'mul_then_pow':
        question_text = f"設 $a>0$，化簡下列各式：<br>$(a^{{{{ {x} }}}} \\cdot a^{{{{ {y} }}}})^{{{{ {z} }}}}$"
        final_exponent = Fraction((x + y) * z, 1)
    elif op_type == 'div_then_pow':
        question_text = f"設 $a>0$，化簡下列各式：<br>$(a^{{{{ {x} }}}} / a^{{{{ {y} }}}})^{{{{ {z} }}}}$"
        final_exponent = Fraction((x - y) * z, 1)
    else: # mixed_fractional: (a^(1/2) * a^(1/3)) / a^(1/6)
        x_num = random.randint(1, 3)
        x_den = random.randint(2, 4)
        y_num = random.randint(1, 3)
        y_den = random.randint(2, 4)
        z_num = random.randint(1, 3)
        z_den = random.randint(2, 4)

        # Ensure denominators are not 1, to make them proper fractions
        if x_den == 1: x_den = random.randint(2,4)
        if y_den == 1: y_den = random.randint(2,4)
        if z_den == 1: z_den = random.randint(2,4)

        x_frac = Fraction(x_num, x_den)
        y_frac = Fraction(y_num, y_den)
        z_frac = Fraction(z_num, z_den)
        
        question_text = f"設 $a>0$，化簡下列各式：<br>$(a^{{{{ {x_frac} }}}} \\cdot a^{{{{ {y_frac} }}}}) / a^{{{{ {z_frac} }}}}$"
        final_exponent = x_frac + y_frac - z_frac
           
    # Format the correct_answer string for strict comparison
    ans_str = ""
    if final_exponent == 0:
        ans_str = "1"
    elif final_exponent.denominator == 1:
        if final_exponent.numerator == 1:
            ans_str = "a"
        elif final_exponent.numerator == -1:
            ans_str = "1/a"
        else:
            ans_str = f"a^{final_exponent.numerator}"
    else: # Fractional exponent
        if final_exponent.numerator < 0:
            ans_str = f"1/a^({-final_exponent.numerator}/{final_exponent.denominator})"
        else:
            ans_str = f"a^({final_exponent.numerator}/{final_exponent.denominator})"
       
    return {
        "question_text": question_text,
        "answer": ans_str,
        "correct_answer": ans_str
    }

def generate_true_false_statement():
    """
    生成判斷對錯的題目，包含指數與三角函數的性質。
    答案為「O」或「X」。
    """
    statements = [
        # Exponent statements (based on examples)
        {"text": r"$(-2)^{{-4}} = -\\frac{{1}}{{16}}$", "answer": "X"}, # Example 1
        {"text": r"$( (-2)^{{2}} )^{{3}} = (-2)^{{6}}$", "answer": "O"}, # Example 2
        {"text": r"$\\sqrt[3]{{-8}} = -2$", "answer": "O"}, # Example 3
        {"text": r"$(a^{{x}})^{{y}} = a^{{x \\cdot y}}$", "answer": "O"}, # General rule
        {"text": r"$a^{{x}} + a^{{y}} = a^{{x+y}}$", "answer": "X"}, # Common misconception
        {"text": r"$a^{{-n}} = \\frac{{1}}{{a^{{n}}}}$", "answer": "O"}, # Negative exponent rule
        {"text": r"$\\sqrt{{a^{{2}}}} = a$", "answer": "X"}, # Should be |a|
        {"text": r"$(a \\cdot b)^{{x}} = a^{{x}} \\cdot b^{{x}}$", "answer": "O"}, # Product rule
        {"text": r"$(a/b)^{{x}} = a^{{x}} / b^{{x}}$", "answer": "O"}, # Quotient rule

        # Trigonometry statements (based on examples)
        {"text": r"$\\sin(\\alpha+\\beta) = \\sin\\alpha + \\sin\\beta$", "answer": "X"}, # Example 13
        {"text": r"$\\cos(85^{{\\circ}}+25^{{\\circ}}) = \\cos85^{{\\circ}}\\cos25^{{\\circ}} + \\sin85^{{\\circ}}\\sin25^{{\\circ}}$", "answer": "X"}, # Example 14 (should be cos(A-B) or cos(A+B) = cosAcosB - sinAsinB)
        {"text": r"$\\tan 100^{{\\circ}} = \\frac{{\\tan 40^{{\\circ}} + \\tan 60^{{\\circ}}}}{{1 - \\tan 40^{{\\circ}}\\tan 60^{{\\circ}}}}$", "answer": "O"}, # Example 15 (tan(40+60)=tan(100))
        {"text": r"$\\sin 15^{{\\circ}} = 2\\sin 7.5^{{\\circ}}\\cos 7.5^{{\\circ}}$", "answer": "O"}, # Example 16 (sin(2A)=2sinAcosA)
        {"text": r"$\\sin 3\\theta = \\sin 2\\theta\\cos\\theta + \\cos 2\\theta\\sin\\theta$", "answer": "O"}, # Example 17 (sin(A+B))
        {"text": r"$\\sin^{{2}}\\theta + \\cos^{{2}}\\theta = 1$", "answer": "O"}, # Pythagorean identity
        {"text": r"$\\frac{{\\sin\\theta}}{{\\cos\\theta}} = \\tan\\theta$", "answer": "O"}, # Quotient identity
        {"text": r"$\\cos(A+B) = \\cos A \\cos B - \\sin A \\sin B$", "answer": "O"}, # Cosine sum formula
        {"text": r"$\\tan(45^{{\\circ}}) = 1$", "answer": "O"}, # Basic value
        {"text": r"$\\sin(30^{{\\circ}}) = \\frac{{1}}{{2}}$", "answer": "O"}, # Basic value
        {"text": r"$\\cos(60^{{\\circ}}) = \\frac{{1}}{{2}}$", "answer": "O"}, # Basic value
    ]
    
    chosen_statement = random.choice(statements)
    question_text = f"下列敘述對的打「○」，錯的打「╳」。<br>$\square$ {chosen_statement['text']}"
    correct_answer = chosen_statement['answer']
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_trigonometric_calculation():
    """
    生成三角函數值計算題目，例如已知 sinA = 3/5，求 cosA 的值。
    會考慮象限。
    """
    pythagorean_triples = [
        (3, 4, 5),
        (5, 12, 13),
        (7, 24, 25),
        (8, 15, 17)
    ]
    x_abs, y_abs, r = random.choice(pythagorean_triples)
    
    # Randomly assign x_abs, y_abs to be the 'x' and 'y' magnitudes
    if random.random() < 0.5:
        x_abs, y_abs = y_abs, x_abs

    quadrant_choice = random.choice(['Q1', 'Q2'])
    
    # Determine signs based on quadrant
    # In Q1: x > 0, y > 0
    # In Q2: x < 0, y > 0
    x_coord = x_abs if quadrant_choice == 'Q1' else -x_abs
    y_coord = y_abs # y is always positive in Q1 and Q2
    
    given_ratio_type = random.choice(['sin', 'cos', 'tan'])
    find_ratio_type = random.choice(['sin', 'cos', 'tan'])
    while given_ratio_type == find_ratio_type: # Ensure finding a different ratio
        find_ratio_type = random.choice(['sin', 'cos', 'tan'])

    question_text_parts = []
    correct_answer_value = None
    
    # Construct the "given" part
    if given_ratio_type == 'sin':
        # Given sin(theta) = y_coord / r
        question_text_parts.append(f"$\\sin\\theta = \\frac{{{y_coord}}}{{{r}}}$")
    elif given_ratio_type == 'cos':
        # Given cos(theta) = x_coord / r
        question_text_parts.append(f"$\\cos\\theta = \\frac{{{x_coord}}}{{{r}}}$")
    else: # given_ratio_type == 'tan'
        # Given tan(theta) = y_coord / x_coord
        question_text_parts.append(f"$\\tan\\theta = \\frac{{{y_coord}}}{{{x_coord}}}$")

    # Determine the correct answer value for the "find" part
    if find_ratio_type == 'sin':
        correct_answer_value = Fraction(y_coord, r)
        question_text_parts.append(f"求 $\\sin\\theta$ 的值。")
    elif find_ratio_type == 'cos':
        correct_answer_value = Fraction(x_coord, r)
        question_text_parts.append(f"求 $\\cos\\theta$ 的值。")
    else: # find_ratio_type == 'tan'
        correct_answer_value = Fraction(y_coord, x_coord)
        question_text_parts.append(f"求 $\\tan\\theta$ 的值。")
    
    quadrant_desc = ""
    if quadrant_choice == 'Q1':
        quadrant_desc = "已知 $\\theta$ 為銳角"
    else: # Q2
        quadrant_desc = "已知 $\\theta$ 為第二象限角"
        
    question_text = f"{quadrant_desc}，{question_text_parts[0]}，{question_text_parts[1]}"
    correct_answer = str(correct_answer_value)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    支援數值 (包含分數) 和特定文字 (例如 'O', 'X', 'a^N' 形式) 的比較。
    """
    user_answer_cleaned = user_answer.strip()
    correct_answer_cleaned = correct_answer.strip()
    
    is_correct = False

    # 1. Try exact string comparison (for 'O'/'X', 'a', '1', 'a^N' etc.)
    if user_answer_cleaned.upper() == correct_answer_cleaned.upper():
        is_correct = True
    else:
        # 2. Try converting to Fraction for exact numerical comparison
        try:
            user_frac = Fraction(user_answer_cleaned)
            correct_frac = Fraction(correct_answer_cleaned)
            if user_frac == correct_frac:
                is_correct = True
        except ValueError:
            # 3. If not a valid fraction, try float comparison with tolerance
            try:
                user_float = float(user_answer_cleaned)
                correct_float = float(correct_answer_cleaned)
                # Allow a small tolerance for float comparisons
                if abs(user_float - correct_float) < 1e-9:
                    is_correct = True
            except ValueError:
                # If all numerical conversions fail, rely solely on initial string comparison
                pass

    result_text = f"完全正確！答案是 ${correct_answer_cleaned}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer_cleaned}$"
    
    # Special handling for algebraic answers to format the result text without extra '$' if it's already a symbol.
    if "a^" in correct_answer_cleaned or correct_answer_cleaned in ["a", "1"]:
        result_text = f"完全正確！答案是 {correct_answer_cleaned}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer_cleaned}"

    return {"correct": is_correct, "result": result_text, "next_question": True}