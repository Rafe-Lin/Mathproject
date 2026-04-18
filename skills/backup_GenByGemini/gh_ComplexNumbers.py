import random
from fractions import Fraction
import re

# Helper function to format complex numbers consistently for display and correct_answer
def format_complex_output(real_part, imag_part):
    """
    Formats a complex number (given its real and imaginary parts) into a string
    in the standard a+bi form, handling fractions and special cases like pure real,
    pure imaginary, or i/-i.
    """
    # Convert to Fraction to ensure exactness and proper formatting if not integer
    # Use limit_denominator to prevent extremely complex fractions for display
    real_f = Fraction(real_part).limit_denominator(100)
    imag_f = Fraction(imag_part).limit_denominator(100)

    # Convert to string, handling common cases
    real_str = str(real_f)
    imag_str = str(imag_f)

    if imag_f == 0:
        return real_str
    
    if real_f == 0:
        if imag_f == 1:
            return "i"
        elif imag_f == -1:
            return "-i"
        else:
            return f"{imag_str}i"
    else: # Both real and imaginary parts are non-zero
        if imag_f > 0:
            if imag_f == 1:
                return f"{real_str}+i"
            else:
                return f"{real_str}+{imag_str}i"
        else: # imag_f < 0
            # str(imag_f) already includes the minus sign.
            # Example: real=1, imag=-1/2 -> "1-1/2i"
            if imag_f == -1:
                return f"{real_str}-i"
            else:
                return f"{real_str}{imag_str}i"

# Helper function to parse user input string into a complex number (Python's built-in complex type)
def parse_complex_input(s):
    """
    Parses a string representing a complex number (e.g., "1+2i", "3", "i")
    into a Python complex number object. Handles common user input variations.
    """
    s = s.strip().lower().replace(" ", "")
    
    if not s: # Empty string
        return None

    # Specific handling for "i" and "-i" as Python's complex() expects "j"
    if s == "i":
        return complex(0, 1)
    if s == "-i":
        return complex(0, -1)
    
    # Replace 'i' with 'j' for Python's complex() constructor
    s = s.replace("i", "j")
    
    try:
        return complex(s)
    except ValueError:
        return None # Parsing failed

def generate_real_imag_parts_problem():
    """
    Generates a problem asking for the real or imaginary part of a given complex number.
    """
    real = random.randint(-10, 10)
    imag = random.randint(-10, 10)
    
    # Ensure variety: purely real, purely imaginary, or full complex
    problem_choice = random.choice(['full', 'pure_real', 'pure_imag'])
    
    if problem_choice == 'pure_real':
        imag = 0
    elif problem_choice == 'pure_imag':
        real = 0
        while imag == 0: # Ensure it's not 0+0i
            imag = random.randint(-10, 10)
    
    z_str = format_complex_output(real, imag)
    
    part_to_ask = random.choice(['實部', '虛部'])
    
    if part_to_ask == '實部':
        correct_answer_val = real
    else: # '虛部'
        correct_answer_val = imag
        
    question_text = fr"請問複數 ${z_str}$ 的{part_to_ask}為何？"
    
    # The answer for this type is a simple number, not a complex number string
    correct_answer_str = str(Fraction(correct_answer_val).limit_denominator(100))
    
    return {
        "question_text": question_text,
        "answer": correct_answer_str,
        "correct_answer": correct_answer_str
    }

def generate_equality_problem():
    """
    Generates a problem involving the equality of two complex numbers,
    requiring solving for two real variables (a and b).
    """
    val_a = random.randint(-5, 5)
    val_b = random.randint(-5, 5)
    
    left_real_offset = random.randint(-3, 3)
    left_imag_offset = random.randint(-3, 3)
    
    coeff_a_lhs = random.choice([1, 2, 3, -1, -2]) # Coefficient for 'a'
    coeff_b_lhs = random.choice([1, 2, 3, -1, -2]) # Coefficient for 'b'
    
    # Right side values based on val_a, val_b
    right_real_val = left_real_offset + coeff_a_lhs * val_a
    right_imag_val = left_imag_offset + coeff_b_lhs * val_b
    
    # Construct left side expressions
    a_var_str = f"{coeff_a_lhs}a" if abs(coeff_a_lhs) != 1 else ("a" if coeff_a_lhs == 1 else "-a")
    b_var_str = f"{coeff_b_lhs}b" if abs(coeff_b_lhs) != 1 else ("b" if coeff_b_lhs == 1 else "-b")
    
    left_real_expr = a_var_str
    if left_real_offset != 0:
        # Use + or - directly if offset is positive or negative
        left_real_expr = f"{a_var_str}{'+' if left_real_offset > 0 else ''}{left_real_offset}"
    
    left_imag_expr = b_var_str
    if left_imag_offset != 0:
        left_imag_expr = f"{b_var_str}{'+' if left_imag_offset > 0 else ''}{left_imag_offset}"

    right_complex_str = format_complex_output(right_real_val, right_imag_val)

    question_text = fr"已知實數 $a, b$ 滿足 $({left_real_expr}) + ({left_imag_expr})i = {right_complex_str}$，求 $a,b$ 的值。"
    
    # Expected answer format: "a=X,b=Y"
    correct_answer = f"a={val_a},b={val_b}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_add_sub_problem():
    """
    Generates a problem for addition or subtraction of two complex numbers.
    """
    z1_real = random.randint(-10, 10)
    z1_imag = random.randint(-10, 10)
    z2_real = random.randint(-10, 10)
    z2_imag = random.randint(-10, 10)
    
    op_symbol = random.choice(['+', '-'])
    
    z1_str = format_complex_output(z1_real, z1_imag)
    z2_str = format_complex_output(z2_real, z2_imag)
    
    question_text = fr"已知複數 $z_1 = {z1_str}$, $z_2 = {z2_str}$，求 $z_1 {op_symbol} z_2$ 的值。"
    
    # Convert to Python's complex type for calculation
    z1_complex = complex(z1_real, z1_imag)
    z2_complex = complex(z2_real, z2_imag)
    
    if op_symbol == '+':
        result_complex = z1_complex + z2_complex
    else: # op_symbol == '-'
        result_complex = z1_complex - z2_complex
        
    correct_answer = format_complex_output(result_complex.real, result_complex.imag)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_multiplication_problem():
    """
    Generates a problem for multiplication of two complex numbers.
    """
    z1_real = random.randint(-5, 5)
    z1_imag = random.randint(-5, 5)
    z2_real = random.randint(-5, 5)
    z2_imag = random.randint(-5, 5)
    
    # Ensure variety: at least one imaginary part is non-zero, and neither complex number is zero.
    attempts = 0
    while ((z1_real == 0 and z1_imag == 0) or 
           (z2_real == 0 and z2_imag == 0) or 
           (z1_imag == 0 and z2_imag == 0)) and attempts < 5:
        z1_real = random.randint(-5, 5)
        z1_imag = random.randint(-5, 5)
        z2_real = random.randint(-5, 5)
        z2_imag = random.randint(-5, 5)
        attempts += 1
    # If still trivial after attempts, force non-trivial numbers
    if attempts == 5:
        z1_real = random.choice([1, 2, -1, -2])
        z1_imag = random.choice([1, 2, -1, -2])
        z2_real = random.choice([1, 2, -1, -2])
        z2_imag = random.choice([1, 2, -1, -2])

    z1_str = format_complex_output(z1_real, z1_imag)
    z2_str = format_complex_output(z2_real, z2_imag)
    
    # Use parentheses for multiplication to avoid ambiguity
    question_text = fr"求下列各式的值：<br>$({z1_str})({z2_str})$"
    
    # Convert to Python's complex type for calculation
    z1_complex = complex(z1_real, z1_imag)
    z2_complex = complex(z2_real, z2_imag)
    
    result_complex = z1_complex * z2_complex
    
    correct_answer = format_complex_output(result_complex.real, result_complex.imag)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_powers_of_i_problem():
    """
    Generates a problem about powers of i, either a single power (i^n)
    or a sum of powers (i + i^2 + ... + i^n).
    """
    problem_type = random.choice(['single_power', 'sum_powers'])
    
    if problem_type == 'single_power':
        n = random.randint(1, 100) # Exponent up to 100
        
        remainder = n % 4
        
        if remainder == 1:
            result = "i"
        elif remainder == 2:
            result = "-1"
        elif remainder == 3:
            result = "-i"
        else: # remainder == 0 (i^4, i^8, ...)
            result = "1"
        
        question_text = fr"求 $i^{{{n}}}$ 的值。"
        correct_answer = result
        
    else: # sum_powers
        # Sum i^1 + ... + i^N
        # If N is a multiple of 4, sum is 0.
        # Otherwise, it's i, i-1, i-1-i for N%4 = 1, 2, 3 respectively
        
        N = random.randint(4, 100) # Start from 4 to ensure cycle is included, up to 100
        
        remainder = N % 4
        
        if remainder == 0:
            result = "0"
        elif remainder == 1: # i^1 + ... + i^(4k+1) = i
            result = "i"
        elif remainder == 2: # i^1 + ... + i^(4k+2) = i + (-1) = -1+i
            result = "-1+i"
        else: # remainder == 3 (i^1 + ... + i^(4k+3) = i + (-1) + (-i) = -1
            result = "-1"
            
        question_text = fr"求 $i + i^{{2}} + i^{{3}} + \dots + i^{{{N}}}$ 的值。"
        correct_answer = result
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_division_problem():
    """
    Generates a problem for division of two complex numbers,
    requiring the result to be in a+bi form.
    """
    num_real = random.randint(-5, 5)
    num_imag = random.randint(-5, 5)
    den_real = random.randint(-5, 5)
    den_imag = random.randint(-5, 5)
    
    # Ensure denominator is not zero
    while den_real == 0 and den_imag == 0:
        den_real = random.randint(-5, 5)
        den_imag = random.randint(-5, 5)

    # Ensure numerator is not 0+0i unless denominator is simple (e.g. 1+0i)
    # This prevents trivial "0 / Z" problems where Z is complex.
    while (num_real == 0 and num_imag == 0) and (den_real != 1 or den_imag != 0):
        num_real = random.randint(-5, 5)
        num_imag = random.randint(-5, 5)
    
    # Convert to Python complex type for easy calculation
    numerator = complex(num_real, num_imag)
    denominator = complex(den_real, den_imag)
    
    result_complex = numerator / denominator
    
    correct_answer = format_complex_output(result_complex.real, result_complex.imag)
    
    num_str = format_complex_output(num_real, num_imag)
    den_str = format_complex_output(den_real, den_imag)
    
    question_text = fr"將下列各複數表示成 $a+bi$ （其中 $a,b$ 為實數）的形式。<br>$\\frac{{{num_str}}}{{{den_str}}}$"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    Generates a random problem related to complex numbers based on the specified skill.
    The level parameter is currently unused but can be extended for difficulty scaling.
    """
    problem_types = [
        'real_imag_parts',
        'equality',
        'add_sub',
        'multiplication',
        'powers_of_i',
        'division'
    ]
    
    problem_type = random.choice(problem_types)
    
    if problem_type == 'real_imag_parts':
        return generate_real_imag_parts_problem()
    elif problem_type == 'equality':
        return generate_equality_problem()
    elif problem_type == 'add_sub':
        return generate_add_sub_problem()
    elif problem_type == 'multiplication':
        return generate_multiplication_problem()
    elif problem_type == 'powers_of_i':
        return generate_powers_of_i_problem()
    elif problem_type == 'division':
        return generate_division_problem()

def check(user_answer, correct_answer):
    """
    Checks if the user's answer is correct for a given complex numbers problem.
    Handles different answer formats: complex numbers (a+bi), single numbers,
    and a=X,b=Y for equality problems.
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()

    is_correct = False
    
    # Case 1: Equality problem (a=X,b=Y format)
    # Regex to match "a=digits,b=digits" or "b=digits,a=digits"
    equality_re = r"^[ab]\s*=\s*[-]?\d+(\.\d+)?(\/\d+)?\s*,\s*[ab]\s*=\s*[-]?\d+(\.\d+)?(\/\d+)?$"
    if re.fullmatch(equality_re, correct_answer, re.IGNORECASE):
        user_parts = {}
        # Parse user answer parts, allowing for "a=X,b=Y" or "b=Y,a=X"
        for part in user_answer.split(','):
            match = re.match(r"([ab])\s*=\s*([-]?\d+(\.\d+)?(\/\d+)?)", part.strip(), re.IGNORECASE)
            if match:
                var_name = match.group(1).lower()
                var_val = Fraction(match.group(2))
                user_parts[var_name] = var_val
        
        correct_parts = {}
        for part in correct_answer.split(','):
            match = re.match(r"([ab])\s*=\s*([-]?\d+(\.\d+)?(\/\d+)?)", part.strip(), re.IGNORECASE)
            if match:
                var_name = match.group(1).lower()
                var_val = Fraction(match.group(2))
                correct_parts[var_name] = var_val
        
        # Check if both 'a' and 'b' values match, order doesn't matter for user input
        if len(user_parts) == 2 and \
           user_parts.get('a') == correct_parts.get('a') and \
           user_parts.get('b') == correct_parts.get('b'):
            is_correct = True

    # Case 2: Real/Imaginary Part problems (single number or fraction answer)
    elif re.fullmatch(r"[-+]?\d+(\.\d+)?(\/\d+)?", correct_answer): 
        try:
            user_val = Fraction(user_answer).limit_denominator(100)
            correct_val = Fraction(correct_answer).limit_denominator(100)
            if user_val == correct_val:
                is_correct = True
        except ValueError:
            pass

    # Case 3: Complex number problems (a+bi form, including i, -i, pure real, pure imag)
    else:
        user_complex = parse_complex_input(user_answer)
        correct_complex = parse_complex_input(correct_answer)
        
        if user_complex is not None and correct_complex is not None:
            # Convert real/imaginary parts to Fraction for exact comparison
            user_real_f = Fraction(user_complex.real).limit_denominator(100)
            user_imag_f = Fraction(user_complex.imag).limit_denominator(100)
            correct_real_f = Fraction(correct_complex.real).limit_denominator(100)
            correct_imag_f = Fraction(correct_complex.imag).limit_denominator(100)

            if user_real_f == correct_real_f and user_imag_f == correct_imag_f:
                is_correct = True

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}