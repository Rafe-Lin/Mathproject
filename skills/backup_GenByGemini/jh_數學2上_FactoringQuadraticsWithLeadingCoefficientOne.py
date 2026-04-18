import random
import re
from collections import Counter

def _format_polynomial(p, q):
    """
    Formats the coefficients p and q into a polynomial string of the form x^2 + px + q.
    Handles special cases for coefficients being 1, -1, or 0.
    """
    poly_str = "x^2"

    # Format the x term (coefficient p)
    if p == 1:
        poly_str += " + x"
    elif p == -1:
        poly_str += " - x"
    elif p > 1:
        poly_str += f" + {p}x"
    elif p < -1:
        poly_str += f" - {-p}x"
    # If p is 0, the x term is omitted

    # Format the constant term (q)
    if q > 0:
        poly_str += f" + {q}"
    elif q < 0:
        poly_str += f" - {-q}"
    # If q is 0, the constant term is omitted (though we avoid this case)

    return poly_str

def _format_factor(val):
    """
    Formats an integer value into a factor string (x + val).
    Handles positive and negative values correctly, e.g., (x + 5) or (x - 3).
    """
    if val > 0:
        return f"(x + {val})"
    elif val < 0:
        return f"(x - {-val})"
    else: # Should not happen in this skill
        return "x"

def generate(level=1):
    """
    Generates a question for factoring a quadratic polynomial x^2 + px + q.

    The function creates a variety of problems by controlling the signs of the
    factors, ensuring coverage of all cases in the cross-multiplication method.
    It also includes special cases like perfect squares and the difference of squares.
    """
    # Choose a problem type with weighted probabilities to ensure a good mix.
    problem_type = random.choices(
        ['pos_pos', 'neg_neg', 'pos_neg', 'perfect_square', 'diff_squares'],
        weights=[0.25, 0.25, 0.3, 0.1, 0.1],
        k=1
    )[0]

    # Case 1: q>0, p>0. Factors are (x+a)(x+b) with a,b > 0.
    if problem_type == 'pos_pos':
        a = random.randint(1, 12)
        b = random.randint(1, 12)
        while a == b: # Avoid perfect squares for this general category
             b = random.randint(1, 12)

    # Case 2: q>0, p<0. Factors are (x-a)(x-b). Corresponds to two negative integers.
    elif problem_type == 'neg_neg':
        a = random.randint(-12, -1)
        b = random.randint(-12, -1)
        while a == b: # Avoid perfect squares for this general category
             b = random.randint(-12, -1)

    # Case 3: q<0. Factors have opposite signs, e.g., (x+a)(x-b).
    elif problem_type == 'pos_neg':
        a = random.randint(2, 15)
        b = random.randint(-15, -2)
        while a == -b: # Avoid difference of squares for this general category
            a = random.randint(2, 15)

    # Case 4: Perfect square trinomial, (x+a)^2 or (x-a)^2.
    elif problem_type == 'perfect_square':
        a = random.choice(list(range(-12, -1)) + list(range(2, 13)))
        b = a
    
    # Case 5: Difference of squares, (x+a)(x-a) = x^2 - a^2.
    else: # 'diff_squares'
        a = random.randint(2, 15)
        b = -a

    p = a + b
    q = a * b

    polynomial_str = _format_polynomial(p, q)
    question_text = f"因式分解 ${polynomial_str}$。"

    # The order of factors in the answer does not matter. Shuffle for variety.
    factors = [a, b]
    random.shuffle(factors)
    factor1_str = _format_factor(factors[0])
    factor2_str = _format_factor(factors[1])

    correct_answer = f"{factor1_str}{factor2_str}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def _parse_answer_factors(answer_string):
    """
    Parses a string like "(x+a)(x+b)" into a list of numbers [a, b].
    This is a robust parser that handles various user inputs like (a+x), (x-b),
    and even (b-x) by correctly identifying the terms.
    Returns a list of two numbers, or None if the format is invalid.
    """
    try:
        s = answer_string.replace(" ", "").lower()
        # Find all expressions within parentheses
        factors_str = re.findall(r'\(([^)]+)\)', s)
        if len(factors_str) != 2:
            return None

        final_numbers = []
        for f_str in factors_str:
            # For each factor string, find the constant term and the sign of 'x'
            
            # Find the number part (integer)
            num_match = re.search(r'([+\-]?\d+)', f_str)
            if not num_match: return None
            num = int(num_match.group(0))

            # Find 'x' and its sign by analyzing what's left
            x_part = f_str.replace(num_match.group(0), '', 1)
            if x_part in ['x', '+x']:
                x_sign = 1
            elif x_part == '-x':
                x_sign = -1
            else:
                return None # Malformed expression for x

            # A factor (c1*x + c0) can be written as c1*(x + c0/c1).
            # The number 'a' in the standard form (x+a) is c0/c1.
            # Here, c1 is x_sign and c0 is num.
            val = num / x_sign
            final_numbers.append(val)

        # Ensure we got two valid integer numbers
        if len(final_numbers) != 2 or not all(isinstance(n, float) and n.is_integer() for n in final_numbers):
             return None

        return [int(n) for n in final_numbers]

    except Exception:
        return None

def check(user_answer, correct_answer):
    """
    Checks if the user's factored form is mathematically equivalent to the correct one.
    It handles commutativity (order of factors) and different but valid input formats.
    """
    user_nums = _parse_answer_factors(user_answer)
    correct_nums = _parse_answer_factors(correct_answer)
    
    is_correct = False
    
    # This should not happen if generate() is correct, but as a safeguard.
    if correct_nums is None:
        return {"correct": False, "result": "內部錯誤：標準答案格式不符。", "next_question": True}
        
    if user_nums is None:
        result_text = f"您的答案格式不正確，請使用 $(x+a)(x+b)$ 的格式，例如 $(x+3)(x-5)$。正確答案是 ${correct_answer}$。"
    else:
        # Use collections.Counter to compare the two lists of numbers.
        # This correctly handles both order and duplicates (for perfect squares).
        if Counter(user_nums) == Counter(correct_nums):
            is_correct = True
            result_text = f"完全正確！答案是 ${correct_answer}$。"
        else:
            result_text = f"答案不正確。正確答案應為 ${correct_answer}$。"

    return {"correct": is_correct, "result": result_text, "next_question": True}