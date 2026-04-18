import random
from fractions import Fraction

def generate_diff_of_squares():
    """
    Generates a problem based on the difference of squares formula: a^2 - b^2 = (a+b)(a-b).
    """
    subtype = random.choice(['simple', 'vars', 'complex_1', 'complex_2'])
    var1 = random.choice(['x', 'y'])
    var2 = 'y' if var1 == 'x' else 'x'
    
    if subtype == 'simple': # e.g., 9x^2 - 16
        k = random.randint(2, 9)
        m = random.randint(2, 9)
        while k == m:
            m = random.randint(2, 9)
        
        term1_sq = k*k
        term2_sq = m*m
        question_expr = f"{term1_sq}{var1}^2 - {term2_sq}"
        
        a = f"{k}{var1}"
        b = f"{m}"
        
        ans1 = f"({a}+{b})({a}-{b})"
        ans2 = f"({a}-{b})({a}+{b})"
        all_answers = f"{ans1};{ans2}"

    elif subtype == 'vars': # e.g., 4x^2 - 25y^2
        k = random.randint(2, 7)
        m = random.randint(2, 7)
        while k == m:
            m = random.randint(2, 7)
            
        term1_sq = k*k
        term2_sq = m*m
        question_expr = f"{term1_sq}{var1}^2 - {term2_sq}{var2}^2"
        
        a = f"{k}{var1}"
        b = f"{m}{var2}"
        
        ans1 = f"({a}+{b})({a}-{b})"
        ans2 = f"({a}-{b})({a}+{b})"
        all_answers = f"{ans1};{ans2}"
        
    elif subtype == 'complex_1': # e.g., (2x+1)^2 - 36
        k = random.randint(2, 5)
        c = random.randint(1, 5) * random.choice([-1, 1])
        m = random.randint(max(abs(c), k) + 1, 10)
        
        c_str = f"+{c}" if c > 0 else str(c)
        term_a_expr = f"({k}{var1}{c_str})"
        term_b_sq = m*m
        question_expr = f"{term_a_expr}^2 - {term_b_sq}"
        
        # Combine constants: (kx + c + m)(kx + c - m)
        const1 = c + m
        const2 = c - m
        term1_const_str = f"+{const1}" if const1 > 0 else str(const1) if const1 != 0 else ""
        term2_const_str = f"+{const2}" if const2 > 0 else str(const2) if const2 != 0 else ""

        final_term1 = f"{k}{var1}{term1_const_str}"
        final_term2 = f"{k}{var1}{term2_const_str}"
        
        ans1 = f"({final_term1})({final_term2})"
        ans2 = f"({final_term2})({final_term1})"
        all_answers = f"{ans1};{ans2}"
        
    else: # subtype == 'complex_2', e.g., 25 - (3x+5)^2
        k = random.randint(2, 5)
        m = random.randint(3, 8)
        c = m * random.choice([-1, 1]) # Force c=m or c=-m for a monomial factor
        
        c_str = f"+{c}" if c > 0 else str(c)
        term_b_expr = f"({k}{var1}{c_str})"
        term_a_sq = m*m
        question_expr = f"{term_a_sq} - {term_b_expr}^2"
        
        if c == m: # m^2 - (kx+m)^2 = [m+(kx+m)][m-(kx+m)] = (kx+2m)(-kx)
            term1 = f"-{k}{var1}"
            term2 = f"{k}{var1}+{2*m}"
        else: # c == -m: m^2 - (kx-m)^2 = [m+(kx-m)][m-(kx-m)] = (kx)(-kx+2m)
            term1 = f"{k}{var1}"
            term2 = f"-{k}{var1}+{2*m}"

        ans1 = f"{term1}({term2})"
        ans2 = f"({term2}){term1}"
        all_answers = f"{ans1};{ans2}"
    
    question_text = f"${question_expr}$"
    display_answer = all_answers.split(';')[0]
    return {"question_text": question_text, "display_answer": display_answer, "all_answers": all_answers}

def generate_perfect_square_sum():
    """
    Generates a problem based on the perfect square sum formula: a^2 + 2ab + b^2 = (a+b)^2.
    """
    var = random.choice(['x', 'y', 'z'])
    
    k_choices = [1] * 3 + list(range(2, 6)) # Make simple case (k=1) more likely
    k = random.choice(k_choices)
    m = random.randint(2, 9)
    
    if k > 3 and m > 5: # Avoid overly large middle term
        m = random.randint(2, 5)

    a_sq_term = f"{k*k}{var}^2" if k > 1 else f"{var}^2"
    ab2_term = 2*k*m
    b_sq_term = m*m
    question_expr = f"{a_sq_term} + {ab2_term}{var} + {b_sq_term}"
    
    a_term = f"{k}{var}" if k > 1 else var
    b_term = str(m)
    
    ans1 = f"({a_term}+{b_term})^2"
    ans2 = f"({a_term}+{b_term})({a_term}+{b_term})"
    ans3 = f"({b_term}+{a_term})^2"
    ans4 = f"({b_term}+{a_term})({b_term}+{a_term})"
    
    all_answers = f"{ans1};{ans2};{ans3};{ans4}"
    question_text = f"${question_expr}$"
    display_answer = ans1
    return {"question_text": question_text, "display_answer": display_answer, "all_answers": all_answers}

def generate_perfect_square_diff():
    """
    Generates a problem based on the perfect square difference formula: a^2 - 2ab + b^2 = (a-b)^2.
    """
    var = random.choice(['x', 'y', 'z'])
    
    k_choices = [1] * 3 + list(range(2, 8)) + [11] # Make k=1 likely, include example's 11
    k = random.choice(k_choices)
    m = random.randint(1, 9) # m=1 is a good case from example

    if k > 5 and m > 5: # Avoid overly large middle term
        m = random.randint(1, 5)
    
    a_sq_term = f"{k*k}{var}^2" if k > 1 else f"{var}^2"
    ab2_term = 2*k*m
    b_sq_term = m*m
    question_expr = f"{a_sq_term} - {ab2_term}{var} + {b_sq_term}"
    
    a_term = f"{k}{var}" if k > 1 else var
    b_term = str(m)
    
    ans1 = f"({a_term}-{b_term})^2"
    ans2 = f"({a_term}-{b_term})({a_term}-{b_term})"
    ans3 = f"({b_term}-{a_term})^2"
    ans4 = f"({b_term}-{a_term})({b_term}-{a_term})"
    
    all_answers = f"{ans1};{ans2};{ans3};{ans4}"
    question_text = f"${question_expr}$"
    display_answer = ans1
    return {"question_text": question_text, "display_answer": display_answer, "all_answers": all_answers}

def generate(level=1):
    """
    Generates a question for factorizing polynomials using multiplication formulas.
    """
    problem_type = random.choice(['diff_squares', 'perfect_square_sum', 'perfect_square_diff'])
    
    if problem_type == 'diff_squares':
        problem = generate_diff_of_squares()
    elif problem_type == 'perfect_square_sum':
        problem = generate_perfect_square_sum()
    else: # perfect_square_diff
        problem = generate_perfect_square_diff()
        
    question_text = f"因式分解下列各式。\n{problem['question_text']}"
    
    return {
        "question_text": question_text,
        "answer": problem['display_answer'],
        "correct_answer": problem['all_answers']
    }

def check(user_answer, correct_answer):
    """
    Checks if the user's factorization is correct.
    """
    # Normalize user input by removing spaces and handling different exponent notations
    user_ans_cleaned = user_answer.strip().replace(' ', '').replace('**', '^')
    
    possible_answers = correct_answer.split(';')
    
    is_correct = False
    for ans in possible_answers:
        # Also clean the possible answers for comparison
        cleaned_ans = ans.replace(' ', '')
        if user_ans_cleaned == cleaned_ans:
            is_correct = True
            break
            
    # Use the first answer in the list as the standard display answer
    display_answer = correct_answer.split(';')[0]
    
    if is_correct:
        result_text = f"完全正確！答案是 ${display_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${display_answer}$"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}