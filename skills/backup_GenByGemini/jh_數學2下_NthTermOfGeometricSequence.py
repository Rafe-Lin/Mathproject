import random
from fractions import Fraction

def _format_fraction_for_latex(f):
    """Helper to format a Fraction object into a LaTeX string."""
    if f.denominator == 1:
        return str(f.numerator)
    
    # Put negative sign outside the fraction for better rendering
    if f.numerator < 0:
        return f"-\\frac{{{abs(f.numerator)}}}{{{f.denominator}}}"
    else:
        return f"\\frac{{{f.numerator}}}{{{f.denominator}}}"

def generate_find_an_problem():
    """
    Generates a problem to find the n-th term given the first term and common ratio.
    (例題 1: 若等比數列的首項為 3，公比為 2，求此等比數列的第 5 項。)
    """
    a1 = random.choice(list(range(-5, 0)) + list(range(2, 6))) # Avoid a1=1
    r = random.choice([-4, -3, -2, 2, 3, 4]) # Avoid r=0, 1, -1
    n = random.randint(3, 6)
    
    an = a1 * (r ** (n - 1))
    
    question_text = f"若一等比數列的首項為 ${a1}$，公比為 ${r}$，求此數列的第 ${n}$ 項。"
    correct_answer = str(an)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_find_an_from_sequence_problem():
    """
    Generates a problem to find the n-th term given the first few terms of a sequence.
    (例題 2: 有一等比數列 1 , 10 , 100 , ……，求此等比數列的第 7 項。)
    """
    a1 = random.choice([-5, -4, -3, -2, 1, 2, 3, 4, 5])
    r = random.choice([-3, -2, 2, 3, 10])
    n = random.randint(5, 7)
    
    # Avoid results that are too large, unless r=10 (scientific notation is common)
    if r != 10 and abs(a1 * (r ** (n - 1))) > 10000:
        n = random.randint(4, 5)

    term1 = a1
    term2 = a1 * r
    term3 = a1 * r * r
    
    an = a1 * (r ** (n - 1))
    
    question_text = f"有一等比數列 ${term1}, {term2}, {term3}, \\ldots$，求此等比數列的第 ${n}$ 項。"
    correct_answer = str(an)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_find_n_problem():
    """
    Generates a problem to find the term number 'n' given a1, r, and an.
    (例題 3: 首項 1, 公比 3, ... 第幾層為 243?)
    """
    a1 = random.choice([-3, -2, -1, 1, 2, 3])
    r = random.choice([-3, -2, 2, 3])
    
    # To ensure an is an integer power of r*a1, we work backwards
    power = random.randint(2, 4) # This will be n-1
    n = power + 1
    
    an = a1 * (r ** power)
    
    question_text = f"一等比數列的首項為 ${a1}$，公比為 ${r}$。若此數列的某一項為 ${an}$，請問這是第幾項？"
    correct_answer = str(n)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_find_an_fraction_problem():
    """
    Generates a problem to find the n-th term with a fractional common ratio.
    """
    den = random.choice([2, 3, 4])
    num = random.choice([1, -1])
    r = Fraction(num, den)
    n = random.randint(3, 5)
    
    # Choose a1 to be a multiple of den^(n-2) to keep some terms as integers
    # This makes the sequence look more natural, e.g., 16, 8, 4, ...
    multiplier = random.choice([1, 2, 3])
    a1 = multiplier * (den ** random.randint(n - 2, n))

    an = a1 * (r ** (n - 1))
    
    r_latex = _format_fraction_for_latex(r)
    
    question_text = f"若一等比數列的首項為 ${a1}$，公比為 ${r_latex}$，求此數列的第 ${n}$ 項。"
    
    # The answer can be an integer or a fraction
    if an.denominator == 1:
        correct_answer = str(an.numerator)
    else:
        correct_answer = str(an) # Format as 'p/q'
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    Generates a problem about finding the n-th term of a geometric sequence.
    
    Topic Description:
    若一個等比數列的首項為 a1，公比為 r (r≠0)，則此數列的第 n 項 an 的公式為 an = a1 × r^(n-1)。
    這個公式可以直接計算出數列中任何一項的值，而不需要將前面的項一一列出。
    """
    problem_type = random.choice([
        'find_an', 
        'find_an_from_seq', 
        'find_n', 
        'find_an_fraction'
    ])
    
    if problem_type == 'find_an':
        return generate_find_an_problem()
    elif problem_type == 'find_an_from_seq':
        return generate_find_an_from_sequence_problem()
    elif problem_type == 'find_n':
        return generate_find_n_problem()
    else: # 'find_an_fraction'
        return generate_find_an_fraction_problem()

def check(user_answer, correct_answer):
    """
    Checks if the user's answer for a geometric sequence problem is correct.
    Handles integers and fractional answers (e.g., 'p/q').
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    
    is_correct = False
    
    try:
        # Direct string comparison (for integers and basic fractions 'p/q')
        if user_answer == correct_answer:
            is_correct = True
        
        # If not matched, try numerical comparison
        else:
            # For fraction answers, compare Fraction objects
            # This correctly handles unsimplified fractions like user='4/6' vs correct='2/3'
            if '/' in correct_answer or '/' in user_answer:
                if Fraction(user_answer) == Fraction(correct_answer):
                    is_correct = True
            # For integer/float answers, compare as floats
            else:
                if float(user_answer) == float(correct_answer):
                    is_correct = True
    except (ValueError, ZeroDivisionError):
        # Handle cases where user input is not a valid number or fraction
        is_correct = False

    # Format the correct answer for display in the feedback
    try:
        f_correct = Fraction(correct_answer)
        formatted_correct_answer = _format_fraction_for_latex(f_correct)
    except ValueError:
        formatted_correct_answer = correct_answer

    if is_correct:
        result_text = f"完全正確！答案是 ${formatted_correct_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${formatted_correct_answer}$"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}