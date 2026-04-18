import random
from fractions import Fraction
import math

def generate_perfect_square_int():
    """
    Generates a problem for finding the square root of a perfect square integer.
    Example: √81 = 9
    """
    base = random.randint(2, 25)
    num_inside_root = base ** 2
    
    question_text = f"求出 $\\sqrt{{{num_inside_root}}}$ 的值。"
    correct_answer = str(base)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_perfect_square_rational():
    """
    Generates a problem for finding the square root of a perfect square fraction or decimal.
    Example: √(9/25) = 3/5 or √1.69 = 1.3
    """
    if random.random() < 0.5: # Decimal
        base_int = random.randint(11, 25)
        # Avoid integers like 2.0
        if base_int % 10 == 0:
            base_int += 1
        
        base_float = base_int / 10.0
        num_inside_root = base_float * base_float
        
        # Format to avoid floating point inaccuracies, e.g., 1.4400000001
        num_inside_root_str = f"{num_inside_root:.4f}".rstrip('0').rstrip('.')
        
        question_text = f"求出 $\\sqrt{{{num_inside_root_str}}}$ 的值。"
        correct_answer = f"{base_float:.1f}".rstrip('0').rstrip('.')
    else: # Fraction
        num = random.randint(1, 10)
        den = random.randint(num + 1, 12)
        
        # Simplify the fraction to be in lowest terms
        f = Fraction(num, den)
        num = f.numerator
        den = f.denominator
        
        num_sq = num ** 2
        den_sq = den ** 2
        
        question_text = f"求出 $\\sqrt{{\\frac{{{num_sq}}}{{{den_sq}}}}}$ 的值。"
        correct_answer = f"{num}/{den}"
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_exponent_law():
    """
    Generates a problem for finding the square root using exponent laws.
    Example: √(2^8) = 2^4 = 16
    """
    base = random.choice([2, 3, 5, 7])
    exponent_half = random.randint(2, 5)
    exponent = exponent_half * 2
    
    answer_val = base ** exponent_half
    
    question_text = f"求出 $\\sqrt{{{base}^{{{exponent}}}}}$ 的值。"
    correct_answer = str(answer_val)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_prime_factorization():
    """
    Generates a problem requiring prime factorization for a larger perfect square.
    Example: √784 = 28
    """
    primes1 = [2, 3]
    primes2 = [5, 7, 11]
    
    p1 = random.choice(primes1)
    p2 = random.choice(primes2)
    
    e1 = random.randint(1, 2)
    e2 = 1
    
    base = (p1 ** e1) * (p2 ** e2)
    num_inside_root = base ** 2
    
    # Ensure the number is not too trivial or too large
    if num_inside_root < 200 or num_inside_root > 4000:
        return generate_prime_factorization() # Retry for a better number

    question_text = f"利用質因數分解，求出 $\\sqrt{{{num_inside_root}}}$ 的值。"
    correct_answer = str(base)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_bisection_method():
    """
    Generates a problem asking for approximation using the bisection method (十分逼近法).
    Example: √5 ≈ 2.2
    """
    num_inside_root = random.randint(3, 100)
    # Ensure it's not a perfect square
    while int(math.sqrt(num_inside_root)) ** 2 == num_inside_root:
        num_inside_root = random.randint(3, 100)
        
    true_value = math.sqrt(num_inside_root)
    # Round to 1 decimal place as per the examples
    answer_val = round(true_value, 1)
    
    question_text = f"試以十分逼近法求 $\\sqrt{{{num_inside_root}}}$ 的近似值。(以四捨五入法求到小數點後第 1 位)"
    correct_answer = f"{answer_val:.1f}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }
    
def generate_calculator_approximation():
    """
    Generates a problem asking for approximation using a calculator.
    Example: √2.6 ≈ 1.6125 (to 4 decimal places)
    """
    precision = random.choice([2, 3])
    problem_subtype = random.choice(['integer', 'decimal', 'fraction'])

    if problem_subtype == 'integer':
        num_inside_root = random.randint(2, 200)
        while int(math.sqrt(num_inside_root)) ** 2 == num_inside_root:
            num_inside_root = random.randint(2, 200)
        value_to_sqrt = num_inside_root
        num_str = str(num_inside_root)

    elif problem_subtype == 'decimal':
        value_to_sqrt = round(random.uniform(1.1, 99.9), 1)
        num_str = str(value_to_sqrt)

    else: # fraction
        num = random.randint(1, 10)
        den = random.randint(num + 1, 12)
        f = Fraction(num, den)
        num = f.numerator
        den = f.denominator
        value_to_sqrt = num / den
        num_str = f"\\frac{{{num}}}{{{den}}}"

    answer_val = round(math.sqrt(value_to_sqrt), precision)
    
    question_text = f"利用計算機求 $\\sqrt{{{num_str}}}$ 的近似值。(以四捨五入法求到小數點後第 {precision} 位)"
    correct_answer = f"{answer_val:.{precision}f}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    Generates a question about finding the value of a square root.

    This skill covers several methods:
    1.  Direct evaluation for perfect squares (integers, fractions, decimals).
    2.  Using prime factorization for larger numbers.
    3.  Using exponent laws.
    4.  Approximation using the bisection method (十分逼近法).
    5.  Approximation using a calculator.
    """
    # Create a weighted list of problem types to make perfect squares more common.
    problem_type_pool = [
        'perfect_square_int', 'perfect_square_int', 'perfect_square_int',
        'perfect_square_rational', 'perfect_square_rational',
        'exponent_law',
        'prime_factorization',
        'bisection_method',
        'calculator_approximation'
    ]
    problem_type = random.choice(problem_type_pool)

    if problem_type == 'perfect_square_int':
        return generate_perfect_square_int()
    elif problem_type == 'perfect_square_rational':
        return generate_perfect_square_rational()
    elif problem_type == 'exponent_law':
        return generate_exponent_law()
    elif problem_type == 'prime_factorization':
        return generate_prime_factorization()
    elif problem_type == 'bisection_method':
        return generate_bisection_method()
    else: # 'calculator_approximation'
        return generate_calculator_approximation()

def check(user_answer, correct_answer):
    """
    Checks if the user's answer is correct.
    Handles integers, decimals, and fractions.
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    
    is_correct = False
    
    # Direct string comparison (works for integers and fraction format "a/b")
    if user_answer == correct_answer:
        is_correct = True
    else:
        # Try comparing as floats for numerical equivalence
        # e.g., user enters "0.6" for correct answer "3/5"
        # e.g., user enters "6.0" for correct answer "6"
        try:
            user_float = float(user_answer)
            
            # Convert correct answer to float
            if '/' in correct_answer:
                num, den = map(int, correct_answer.split('/'))
                correct_float = num / den
            else:
                correct_float = float(correct_answer)
            
            # Compare floats with a small tolerance
            if math.isclose(user_float, correct_float):
                is_correct = True
        except (ValueError, ZeroDivisionError):
            # If conversion fails, the answer is incorrect
            pass

    if is_correct:
        result_text = f"完全正確！答案是 ${correct_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer}$"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}