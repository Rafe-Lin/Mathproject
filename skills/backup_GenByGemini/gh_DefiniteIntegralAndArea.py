import random
from fractions import Fraction
import math

def definite_integral_polynomial(coeffs, lower_bound, upper_bound):
    """
    Calculates the definite integral of a polynomial function.
    The polynomial is represented by its coefficients in descending order of power.
    e.g., [a, b, c] for ax^2 + bx + c.
    """
    def antiderivative(x_val):
        x_val_frac = Fraction(x_val)
        result = Fraction(0)
        # Iterate from the constant term up to the highest power term
        # If coeffs = [a, b, c], reversed(coeffs) = [c, b, a]
        for i, coeff in enumerate(reversed(coeffs)):
            power = i # Power of x for the current term (starts from 0 for constant)
            if coeff != 0:
                # Term is coeff * x^power
                # Antiderivative term is (coeff / (power + 1)) * x^(power + 1)
                result += (Fraction(coeff) / Fraction(power + 1)) * (x_val_frac**(power + 1))
        return result

    return antiderivative(upper_bound) - antiderivative(lower_bound)

def format_polynomial(coeffs, var='x'):
    """
    Formats a list of coefficients into a LaTeX-friendly polynomial string.
    coeffs = [a, b, c] for ax^2 + bx + c
    coeffs = [m, c] for mx + c
    """
    if not coeffs:
        return "0"
    
    terms = []
    degree = len(coeffs) - 1 # Highest degree of the polynomial
    
    for i, coeff in enumerate(coeffs):
        if coeff == 0:
            continue
        
        current_degree = degree - i # Current term's degree
        coeff_str = ""
        
        # Add '+' sign for positive terms that are not the first term
        if coeff > 0 and len(terms) > 0:
            coeff_str += "+"
            
        # Handle coefficients of 1 or -1, and constant terms
        if abs(coeff) == 1 and current_degree != 0:
            coeff_str += "-" if coeff == -1 else ""
        elif current_degree == 0: # Constant term
            coeff_str += str(coeff)
        else: # Other coefficients
            coeff_str += str(coeff)
            
        # Add variable and power
        if current_degree == 1:
            coeff_str += var
        elif current_degree > 1:
            coeff_str += f"{var}^{{{current_degree}}}"
        
        terms.append(coeff_str)
        
    return "".join(terms) if terms else "0"

def generate_linear_function_problem(level):
    """
    Generates a problem involving a linear function f(x) = mx + c.
    Can be either definite integral (net area) or total area.
    """
    m = random.randint(-3, 3)
    while m == 0: # Ensure m is not zero for a linear function
        m = random.randint(-3, 3)
    c = random.randint(-5, 5)

    # Ensure L < R, and interval often crosses x-axis for interesting total area problems
    L = random.randint(-5, 0)
    R = random.randint(1, 5)
    while R <= L: 
        L = random.randint(-5, 0)
        R = random.randint(1, 5)

    f_x_str = format_polynomial([m, c])

    problem_type = random.choice(['net_area_linear', 'total_area_linear'])

    if problem_type == 'net_area_linear':
        question_text = f"計算定積分 $\\int_{{{L}}}^{{{R}}} ({f_x_str}) dx$。"
        correct_answer_frac = definite_integral_polynomial([m, c], L, R)
    else: # total_area_linear
        question_text = f"計算函數 $f(x) = {f_x_str}$ 的圖形與 $x$ 軸在區間 $[{L}, {R}]$ 所圍成的區域面積。"
        
        # Find root: mx + c = 0 => x = -c/m
        root = Fraction(-c, m)
        
        intervals = []
        if L < root < R: # If root is within the interval, split it
            intervals.append((L, root))
            intervals.append((root, R))
        else: # Otherwise, integrate over the whole interval
            intervals.append((L, R))
        
        total_area_frac = Fraction(0)
        for sub_L, sub_R in intervals:
            integral_val = definite_integral_polynomial([m, c], sub_L, sub_R)
            total_area_frac += abs(integral_val) # Take absolute value for area

        correct_answer_frac = total_area_frac
    
    # Format answer for display (LaTeX fraction or integer)
    if correct_answer_frac.denominator == 1:
        correct_answer_display = str(correct_answer_frac.numerator)
    else:
        correct_answer_display = f"\\frac{{{correct_answer_frac.numerator}}}{{{correct_answer_frac.denominator}}}"

    return {
        "question_text": question_text,
        "answer": str(correct_answer_frac), # Store as string representation of Fraction for internal check
        "correct_answer": f"${correct_answer_display}$" # Display in LaTeX math mode
    }

def generate_quadratic_function_problem(level):
    """
    Generates a problem involving a quadratic function f(x) = ax^2 + bx + c.
    Can be either definite integral (net area) or total area.
    Functions are typically generated with integer roots for solvability.
    """
    # Generate quadratic with integer roots for easier solving
    # f(x) = a(x-r1)(x-r2) = a(x^2 - (r1+r2)x + r1*r2)
    a = random.randint(-2, 2)
    while a == 0:
        a = random.randint(-2, 2)
    
    r1 = random.randint(-3, 3)
    r2 = random.randint(-3, 3)
    # Ensure distinct roots for interesting crossing behavior
    while r1 == r2: 
        r2 = random.randint(-3, 3)
    
    b_coeff = -a * (r1 + r2)
    c_coeff = a * r1 * r2

    coeffs = [a, b_coeff, c_coeff] # [a, b, c] for ax^2+bx+c
    f_x_str = format_polynomial(coeffs)

    # Generate integration interval L, R to encompass or be near the roots
    min_root = min(r1, r2)
    max_root = max(r1, r2)
    L = random.randint(min_root - 3, min_root + 1)
    R = random.randint(max_root - 1, max_root + 3)
    
    # Ensure L < R and not too close
    if L >= R: 
        L = min_root - 2
        R = max_root + 2
        if L >= R: # Fallback for very close roots or small ranges
            L -= 1
            R += 1

    problem_type = random.choice(['net_area_quadratic', 'total_area_quadratic'])

    if problem_type == 'net_area_quadratic':
        question_text = f"計算定積分 $\\int_{{{L}}}^{{{R}}} ({f_x_str}) dx$。"
        correct_answer_frac = definite_integral_polynomial(coeffs, L, R)
    else: # total_area_quadratic
        question_text = f"計算函數 $f(x) = {f_x_str}$ 的圖形與 $x$ 軸在區間 $[{L}, {R}]$ 所圍成的區域面積。"
        
        roots = sorted([r1, r2]) 
        
        # Collect all critical points: interval bounds and roots within bounds
        critical_points = sorted(list(set([L, R, roots[0], roots[1]])))
        
        # Filter critical points to be strictly within [L, R] or equal to bounds
        valid_critical_points = [p for p in critical_points if L <= p <= R]
        valid_critical_points = sorted(list(set(valid_critical_points))) # Remove duplicates and sort again

        total_area_frac = Fraction(0)
        # Integrate over sub-intervals defined by critical points
        for i in range(len(valid_critical_points) - 1):
            sub_L = valid_critical_points[i]
            sub_R = valid_critical_points[i+1]
            if sub_L == sub_R: # Skip zero-length intervals
                continue
            
            integral_val = definite_integral_polynomial(coeffs, sub_L, sub_R)
            total_area_frac += abs(integral_val) # Add absolute value to total area

        correct_answer_frac = total_area_frac
    
    # Format answer for display (LaTeX fraction or integer)
    if correct_answer_frac.denominator == 1:
        correct_answer_display = str(correct_answer_frac.numerator)
    else:
        correct_answer_display = f"\\frac{{{correct_answer_frac.numerator}}}{{{correct_answer_frac.denominator}}}"

    return {
        "question_text": question_text,
        "answer": str(correct_answer_frac),
        "correct_answer": f"${correct_answer_display}$"
    }

def generate(level=1):
    """
    Generates a definite integral and area problem.
    Level 1 primarily focuses on linear functions and basic quadratic functions.
    """
    # Randomly choose between linear and quadratic functions
    problem_choice = random.choice(['linear', 'quadratic'])
    
    if problem_choice == 'linear':
        return generate_linear_function_problem(level)
    else: # quadratic
        return generate_quadratic_function_problem(level)

def check(user_answer, correct_answer):
    """
    Checks if the user's answer is correct.
    Answers are compared as fractions for precision.
    """
    try:
        # Convert user input and correct answer to Fraction objects
        user_frac = Fraction(user_answer.strip())
        # The stored correct_answer is already a string representation of Fraction
        correct_frac = Fraction(correct_answer.strip())
        
        is_correct = (user_frac == correct_frac)
        
        # The correct_answer parameter here is the internal string "Fraction(num,den)",
        # which needs to be converted back to the displayable LaTeX format for feedback.
        # This requires re-parsing the correct_answer. A better design might store both
        # internal and display answer in the problem dict.
        # For now, let's assume `correct_answer` in check is the stored internal fraction string.
        # We'll use the originally generated `correct_answer` (LaTeX formatted) for display feedback.
        # This might be slightly inconsistent with the template's `check` function, but it's
        # necessary to compare the exact fraction values. Let's adjust `correct_answer` parameter
        # to be the raw fraction string, and rely on `generate` to provide the displayable format.

        # Let's re-format the `correct_frac` for display in the feedback message.
        if correct_frac.denominator == 1:
            correct_answer_display = str(correct_frac.numerator)
        else:
            correct_answer_display = f"\\frac{{{correct_frac.numerator}}}{{{correct_frac.denominator}}}"
        
        if is_correct:
            result_text = f"完全正確！答案是 ${correct_answer_display}$。"
        else:
            result_text = f"答案不正確。正確答案應為：${correct_answer_display}$"
        
        return {"correct": is_correct, "result": result_text, "next_question": True}
    except ValueError:
        return {"correct": False, "result": "請輸入有效數字或分數。", "next_question": False}
    except Exception as e:
        # Catch any other unexpected errors during check
        return {"correct": False, "result": f"檢查答案時發生錯誤: {e}", "next_question": False}