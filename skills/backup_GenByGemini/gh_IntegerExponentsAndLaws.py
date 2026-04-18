import random
from fractions import Fraction
import math

# Helper to format a number (integer or Fraction) as a string, possibly LaTeX for fractions
def format_number_for_display(num):
    if isinstance(num, Fraction):
        if num.denominator == 1:
            return str(num.numerator)
        else:
            # Use \\frac for fractions
            return fr"\\frac{{{num.numerator}}}{{{num.denominator}}}"
    elif isinstance(num, int):
        return str(num)
    elif isinstance(num, float):
        # Convert float to fraction to avoid trailing .0 or precision issues if it's an exact fraction
        frac_num = Fraction(num).limit_denominator(1000) # Limit denominator to keep it simple
        if frac_num.denominator == 1:
            return str(frac_num.numerator)
        else:
            return fr"\\frac{{{frac_num.numerator}}}{{{frac_num.denominator}}}"
    return str(num)

def format_base_for_display(base):
    # Add parentheses if base is negative or a fraction or a float
    if isinstance(base, int):
        if base < 0:
            return f"({base})"
        else:
            return str(base)
    elif isinstance(base, Fraction):
        if base.denominator == 1: # It's an integer
            if base.numerator < 0:
                return f"({base.numerator})"
            else:
                return str(base.numerator)
        else:
            return fr"\\left({format_number_for_display(base)}\\right)"
    elif isinstance(base, float):
        if base < 0:
            return f"({base})"
        else:
            return str(base)
    return str(base)


def generate_evaluate_exponent_problem():
    sub_type = random.choice(['zero_exponent', 'negative_integer_exponent'])
    
    if sub_type == 'zero_exponent':
        # (base)^0 = 1
        base_type = random.choice(['integer', 'fraction', 'expression'])
        
        if base_type == 'integer':
            base_val = random.choice([x for x in range(-10, 11) if x != 0]) # Exclude 0
            question_text = fr"求 ${format_base_for_display(base_val)}^{{0}}$ 的值。"
            correct_answer = "1"
        elif base_type == 'fraction':
            numerator = random.choice([x for x in range(-5, 6) if x != 0])
            denominator = random.choice([x for x in range(2, 7)])
            base_val = Fraction(numerator, denominator)
            question_text = fr"求 ${format_base_for_display(base_val)}^{{0}}$ 的值。"
            correct_answer = "1"
        else: # expression, ensuring base is not 0
            expression_parts = []
            if random.random() < 0.5: # Include irrational number (like pi)
                expression_parts.append(r"\\pi")
                expression_parts.append(random.choice(['+', '-']))
                expression_parts.append(str(random.randint(1, 100)))
            else: # Include radical
                expression_parts.append(str(random.randint(1, 20)))
                expression_parts.append(random.choice(['+', '-']))
                expression_parts.append(r"\\sqrt{" + str(random.randint(2,10)) + r"}")
            
            expression_str = " ".join(expression_parts)
            question_text = fr"求 $\\left({expression_str}\\right)^{{0}}$ 的值。"
            correct_answer = "1"
            
    else: # negative_integer_exponent
        # a^(-n) = 1/a^n
        
        # Base can be integer or fraction, but not 0, 1, -1 for interesting results.
        # Integer bases
        base_val = random.choice([x for x in range(-5, 6) if x not in [0, 1, -1]]) 
        
        if random.random() < 0.5: # Randomly choose to use a fraction as base
            numerator = random.choice([x for x in range(1, 6) if x != 1])
            denominator = random.choice([x for x in range(2, 7) if x != numerator])
            base_val = Fraction(numerator, denominator)
            if base_val == 1: # Avoid base 1 again
                base_val = Fraction(numerator, denominator + random.choice([1,-1]))
                if base_val.denominator == 0: base_val = Fraction(numerator, denominator+2)

        exponent = random.randint(-3, -1) # Always negative exponent
        
        question_text = fr"求 ${format_base_for_display(base_val)}^{{{exponent}}}$ 的值。"
        
        # Calculate correct answer using fractions for precision
        base_frac = Fraction(base_val)
        correct_frac = base_frac**exponent
        
        correct_answer = format_number_for_display(correct_frac)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "solution": fr"詳解: ${question_text.replace('求 ', '').replace(' 的值。', '')} = {correct_answer}$"
    }

def generate_exponent_law_problem():
    law_type = random.choice(['product_of_powers', 'power_of_a_power', 'power_of_a_product', 'quotient_of_powers'])
    
    if law_type == 'product_of_powers': # a^m * a^n = a^(m+n)
        base = random.choice([x for x in range(2, 6)]) # Base >= 2
        exp1 = random.randint(-3, 3)
        exp2 = random.randint(-3, 3)
        
        # Ensure sum_exp is not too large or too trivial
        sum_exp = exp1 + exp2
        while abs(sum_exp) > 5 or sum_exp == 0 and (exp1 != 0 or exp2 != 0):
            exp1 = random.randint(-3, 3)
            exp2 = random.randint(-3, 3)
            sum_exp = exp1 + exp2

        question_text = fr"利用指數律求 ${base}^{{{exp1}}} \\times {base}^{{{exp2}}}$ 的值。"
        correct_value = Fraction(base)**sum_exp
        solution_steps = fr"${base}^{{{exp1}}} \\times {base}^{{{exp2}}} = {base}^{{{exp1} + ({exp2})}} = {base}^{{{sum_exp}}} = {format_number_for_display(correct_value)}$"

    elif law_type == 'power_of_a_power': # (a^m)^n = a^(m*n)
        base = random.choice([x for x in range(2, 5)]) # Base >= 2
        exp1 = random.randint(-2, 2)
        exp2 = random.randint(-2, 2)
        
        # Avoid trivial cases like (a^0)^n or (a^m)^0
        prod_exp = exp1 * exp2
        while prod_exp == 0 or abs(prod_exp) > 4: # Keep result small enough
            exp1 = random.randint(-2, 2)
            exp2 = random.randint(-2, 2)
            prod_exp = exp1 * exp2
            
        question_text = fr"利用指數律求 $\\left({base}^{{{exp1}}}\\right)^{{{exp2}}}$ 的值。"
        correct_value = Fraction(base)**prod_exp
        solution_steps = fr"$\\left({base}^{{{exp1}}}\\right)^{{{exp2}}} = {base}^{{({exp1}) \\times ({exp2})}} = {base}^{{{prod_exp}}} = {format_number_for_display(correct_value)}$"

    elif law_type == 'power_of_a_product': # (ab)^n = a^n b^n
        base1 = random.choice([x for x in range(2, 5)])
        base2 = random.choice([x for x in range(2, 5) if x != base1])
        exponent = random.randint(-2, 2)
        
        # Avoid trivial exponent 0
        if exponent == 0:
            exponent = random.choice([-1, 1, 2])
            
        prod_base = base1 * base2
        
        question_text = fr"利用指數律求 ${base1}^{{{exponent}}} \\times {base2}^{{{exponent}}}$ 的值。"
        correct_value = Fraction(prod_base)**exponent
        solution_steps = fr"${base1}^{{{exponent}}} \\times {base2}^{{{exponent}}} = ({base1} \\times {base2})^{{{exponent}}} = {prod_base}^{{{exponent}}} = {format_number_for_display(correct_value)}$"

    else: # quotient_of_powers: a^m / a^n = a^(m-n)
        base = random.choice([x for x in range(2, 6)])
        exp1 = random.randint(-3, 3)
        exp2 = random.randint(-3, 3)
        
        # Ensure difference is not too large or trivial (difference is not 0)
        diff_exp = exp1 - exp2
        while abs(diff_exp) > 5 or diff_exp == 0:
            exp1 = random.randint(-3, 3)
            exp2 = random.randint(-3, 3)
            diff_exp = exp1 - exp2

        question_text = fr"利用指數律求 $\\frac{{{base}^{{{exp1}}}}}{{{base}^{{{exp2}}}}}$ 的值。"
        correct_value = Fraction(base)**diff_exp
        solution_steps = fr"$\\frac{{{base}^{{{exp1}}}}}{{{base}^{{{exp2}}}}} = {base}^{{{exp1} - ({exp2})}} = {base}^{{{diff_exp}}} = {format_number_for_display(correct_value)}$"

    correct_answer = format_number_for_display(correct_value)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "solution": fr"詳解: {solution_steps}"
    }

def generate_algebraic_expression_problem():
    # Given a + a^{-1} = k, find a^2 + a^{-2} or a^3 + a^{-3}
    k = random.randint(3, 5) # Use k >= 3 to ensure positive results for k^2-2
    
    sub_type = random.choice(['square', 'cube'])
    
    question_prefix = fr"已知 $a \\neq 0$ 且 $a + a^{{-1}} = {k}$，求"
    
    if sub_type == 'square':
        # (a + a^{-1})^2 = a^2 + 2(a)(a^{-1}) + a^{-2} = a^2 + 2 + a^{-2}
        # k^2 = a^2 + a^{-2} + 2 => a^2 + a^{-2} = k^2 - 2
        target_value = k**2 - 2
        question_text = question_prefix + fr" $a^{{2}} + a^{{-2}}$ 的值。"
        
        solution_steps = [
            fr"將 $a + a^{{-1}} = {k}$ 兩邊平方，得",
            fr"$\\left(a + a^{{-1}}\\right)^{{2}} = {k}^{{2}}$",
            fr"展開得 $a^{{2}} + 2(a)(a^{{-1}}) + a^{{-2}} = {k**2}$",
            fr"即 $a^{{2}} + 2 + a^{{-2}} = {k**2}$",
            fr"故 $a^{{2}} + a^{{-2}} = {k**2} - 2 = {target_value}$。"
        ]
        
    else: # cube
        # (a + a^{-1})^3 = a^3 + 3a^2(a^{-1}) + 3a(a^{-1})^2 + a^{-3}
        # = a^3 + 3a + 3a^{-1} + a^{-3}
        # = a^3 + a^{-3} + 3(a + a^{-1})
        # k^3 = a^3 + a^{-3} + 3k => a^3 + a^{-3} = k^3 - 3k
        target_value = k**3 - 3*k
        question_text = question_prefix + fr" $a^{{3}} + a^{{-3}}$ 的值。"
        
        solution_steps = [
            fr"將 $a + a^{{-1}} = {k}$ 兩邊三次方，得",
            fr"$\\left(a + a^{{-1}}\\right)^{{3}} = {k}^{{3}}$",
            fr"展開得 $a^{{3}} + 3a^{{2}}(a^{{-1}}) + 3a(a^{{-1}})^{{2}} + a^{{-3}} = {k**3}$",
            fr"$a^{{3}} + 3a + 3a^{{-1}} + a^{{-3}} = {k**3}$",
            fr"$a^{{3}} + a^{{-3}} + 3(a + a^{{-1}}) = {k**3}$",
            fr"即 $a^{{3}} + a^{{-3}} = {k**3} - 3(a + a^{{-1}}) = {k**3} - 3 \\times {k} = {target_value}$。"
        ]
    
    correct_answer = str(target_value)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "solution": r"詳解: " + r"<br>".join(solution_steps)
    }

def generate_word_problem():
    # Example: E = C * d^(-n)
    C = random.choice([100, 200, 300, 400, 500])
    exponent_n = random.choice([2, 3]) # d^(-2) or d^(-3)
    
    # d as a decimal that can be converted to a simple fraction
    decimal_options = [0.2, 0.25, 0.4, 0.5, 0.8]
    d_val_float = random.choice(decimal_options)
    d_val_frac = Fraction(d_val_float)
    
    question_text = fr"設某物體與光源的距離為 $d$ 公尺時，其照度為 $E$ 勒克斯，且 $E$ 與 $d$ 的關係式為 $E = {C}d^{{-{exponent_n}}}$。<br>"
    question_text += fr"已知此光源高度為 ${format_number_for_display(d_val_float)}$ 公尺，求放置於桌面上時，光源正下方的照度 $E$ 的值。"
    
    # Calculation: E = C * d^(-n) = C * (1/d)^n
    
    # Using fractions for calculation to ensure accuracy
    d_inverse = Fraction(1, d_val_frac)
    e_value = C * (d_inverse**exponent_n)
    
    correct_answer = format_number_for_display(e_value)
    
    solution_steps = [
        fr"將 $d={format_number_for_display(d_val_float)}$ 代入 $E = {C}d^{{-{exponent_n}}}$，得",
        fr"$E = {C} \\times \\left({format_number_for_display(d_val_float)}\\right)^{{-{exponent_n}}}$",
        fr"$E = {C} \\times \\left({format_number_for_display(d_val_frac)}\\right)^{{-{exponent_n}}}$",
        fr"$E = {C} \\times \\left({format_number_for_display(Fraction(d_val_frac.denominator, d_val_frac.numerator))}\\right)^{{{exponent_n}}}$",
        fr"$E = {C} \\times {format_number_for_display(Fraction(d_val_frac.denominator, d_val_frac.numerator)**exponent_n)}$",
        fr"$E = {format_number_for_display(e_value)}$ （勒克斯）。"
    ]
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "solution": r"詳解: " + r"<br>".join(solution_steps)
    }


def generate(level=1):
    problem_types = [
        generate_evaluate_exponent_problem,
        generate_exponent_law_problem,
        generate_algebraic_expression_problem,
        generate_word_problem
    ]
    
    selected_problem_func = random.choice(problem_types)
    return selected_problem_func()


def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    
    is_correct = False
    result_text = ""

    try:
        # Try converting to Fraction for robust comparison, handling potential LaTeX fraction input
        def parse_fraction_string(s):
            if r'\\frac' in s:
                # Basic parsing for \\frac{num}{den}
                parts = s.replace(r'\\frac{', '').replace('}{', ',').replace('}', '').split(',')
                return Fraction(int(parts[0]), int(parts[1]))
            else:
                return Fraction(s)

        user_frac = parse_fraction_string(user_answer)
        correct_frac = parse_fraction_string(correct_answer)
        
        if user_frac == correct_frac:
            is_correct = True
    except ValueError:
        # If Fraction conversion fails, try direct string comparison
        if user_answer == correct_answer:
            is_correct = True
        else:
            # Try float comparison as a last resort if both are not fractions and not matching strings
            try:
                if abs(float(user_answer) - float(correct_answer)) < 1e-9:
                    is_correct = True
            except ValueError:
                pass # Still not matching
            
    if is_correct:
        result_text = f"完全正確！答案是 ${correct_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer}$"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}