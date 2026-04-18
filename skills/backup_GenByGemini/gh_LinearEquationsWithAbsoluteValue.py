import random
from fractions import Fraction
import math

def format_fraction(f):
    """Formats a Fraction object as a string for LaTeX display."""
    if f.denominator == 1:
        return str(f.numerator)
    # Using \\frac for LaTeX fractions. Double braces are critical for f-strings.
    return f"\\frac{{{f.numerator}}}{{{f.denominator}}}"

def generate(level=1):
    """
    生成「含絕對值的一次方程式」題目。
    """
    problem_type = random.choice(['type1_single_abs', 'type2_two_abs'])
    
    if problem_type == 'type1_single_abs':
        return generate_type1_single_abs_problem(level)
    else: # type2_two_abs
        return generate_type2_two_abs_problem(level)

def generate_type1_single_abs_problem(level):
    """
    生成 |ax - b| = c 類型的題目。
    level 1: a=1, b, c 較小整數
    level 2: a 可能是 2, 3, b, c 範圍擴大
    level 3: b, c 可能導致分數解
    """
    if level == 1:
        a = 1
        b = random.randint(-5, 5)
        c = random.randint(1, 8)
    elif level == 2:
        a = random.choice([1, 2])
        b = random.randint(-8, 8)
        c = random.randint(1, 12)
    else: # level 3
        a = random.randint(1, 3)
        b = random.randint(-10, 10)
        c = random.randint(1, 15)

    # Ensure c is positive
    c = abs(c)
    if c == 0: # Ensure RHS is not 0 for interesting problems
        c = random.randint(1, 5)

    # Construct the term inside the absolute value
    term_str = ""
    # Decide if it's (ax - b) or (b - ax) if a=1
    if a == 1 and random.random() < 0.5: # Generates |b-x| or |-b-x| cases
        if b >= 0:
            term_str = f"{b} - x"
            # Effectively, |b-x| = |x-b|. So solutions are x = b + c, x = b - c.
            # For consistent algebraic solving: ax - b = c or ax - b = -c.
            # In |b-x|, it's |x-b|. So a=1, 'b' in the formula is b.
            # x = (c+b)/1, x = (-c+b)/1
            sol1_val = Fraction(c + b)
            sol2_val = Fraction(-c + b)
        else: # b < 0, e.g. |-5-x| which is |x+5|. This implies a=1, 'b' is -b.
            term_str = f"{-b} + x"
            # For |x+5|, 'b' in the formula is -5.
            sol1_val = Fraction(c + (-b)) # x + 5 = c => x = c - 5
            sol2_val = Fraction(-c + (-b)) # x + 5 = -c => x = -c - 5
            # So if term_str is like '5+x', it's |x+5|, so the 'b' value for ax-b is actually -5.
            # Re-evaluate b for the standard form `|ax - b| = c`
            b_effective = -b # If term_str is '5+x', then b_effective = -5
            sol1_val = Fraction(c + b_effective)
            sol2_val = Fraction(-c + b_effective)

    else: # Standard |ax-b| format
        if b >= 0:
            term_str = f"{a}x - {b}"
        else:
            term_str = f"{a}x + {abs(b)}"
        
        if a == 1 and term_str.startswith("1x"):
            term_str = term_str[1:] # Remove '1' from '1x' if a=1
        
        # Solutions for |ax - b| = c
        sol1_val = Fraction(c + b, a)
        sol2_val = Fraction(-c + b, a)

    solutions = sorted([sol1_val, sol2_val])
    
    correct_answer_parts = []
    for sol in solutions:
        correct_answer_parts.append(format_fraction(sol))
    
    # Construct question text, using <br> for line breaks outside LaTeX math.
    question_text = f"解下列方程式：<br>$|{term_str}| = {c}$"
    
    correct_answer_str = " 或 ".join(correct_answer_parts)
    
    return {
        "question_text": question_text,
        "answer": correct_answer_str, # Example answer for display, will be overridden by user input
        "correct_answer": correct_answer_str
    }

def generate_type2_two_abs_problem(level):
    """
    生成 |x-p| + |x-q| = c 類型的題目。
    p, q 應為整數，c 為整數
    通常為 |x| + |x+k| = c 或 |x-k| + |x| = c
    """
    # Let's use |x - p_val| + |x - q_val| = c
    # Ensure p_val < q_val
    p_val = random.randint(-5, 0)
    q_val = random.randint(p_val + 1, 5)

    distance_pq = q_val - p_val
    
    # Ensure c is large enough to guarantee two distinct solutions
    # c must be > distance_pq for two solutions
    # If c == distance_pq, any x in [p,q] is a solution (infinite solutions, usually not intended for single answer format)
    # If c < distance_pq, no solution
    c_min = distance_pq + 1
    c = random.randint(c_min, c_min + 7)

    # Construct the terms for the question string
    term1_str = ""
    if p_val == 0:
        term1_str = "|x|"
    elif p_val > 0:
        term1_str = f"|x - {p_val}|"
    else: # p_val < 0
        term1_str = f"|x + {abs(p_val)}|"

    term2_str = ""
    if q_val == 0:
        term2_str = "|x|"
    elif q_val > 0:
        term2_str = f"|x - {q_val}|"
    else: # q_val < 0
        term2_str = f"|x + {abs(q_val)}|"
    
    # Make sure the term with smaller 'constant' or just 'x' comes first for canonical display
    display_terms = sorted([term1_str, term2_str], key=lambda t: (len(t), t)) # Heuristic for sorting
    question_equation = f"{display_terms[0]} + {display_terms[1]}"

    # Solve by casework
    solutions = set()

    # Case 1: x < p_val
    # -(x - p_val) - (x - q_val) = c
    # -x + p_val - x + q_val = c
    # -2x + p_val + q_val = c
    # -2x = c - p_val - q_val
    # x_sol1 = (p_val + q_val - c) / 2
    x_sol1 = Fraction(p_val + q_val - c, 2)
    if x_sol1 < p_val:
        solutions.add(x_sol1)

    # Case 2: p_val <= x < q_val
    # (x - p_val) - (x - q_val) = c (since x-p_val >= 0 and x-q_val < 0)
    # x - p_val - x + q_val = c
    # q_val - p_val = c
    # This case only has solutions if q_val - p_val == c.
    # We ensured c > q_val - p_val by setting c_min = distance_pq + 1.
    # Therefore, no solutions in this range for the problems generated.
    
    # Case 3: x >= q_val
    # (x - p_val) + (x - q_val) = c
    # 2x - p_val - q_val = c
    # 2x = c + p_val + q_val
    # x_sol2 = (p_val + q_val + c) / 2
    x_sol2 = Fraction(p_val + q_val + c, 2)
    if x_sol2 >= q_val:
        solutions.add(x_sol2)

    correct_answer_parts = []
    for sol in sorted(list(solutions)):
        correct_answer_parts.append(format_fraction(sol))
    
    question_text = f"解方程式：<br>${question_equation} = {c}$"
    correct_answer_str = " 或 ".join(correct_answer_parts)

    return {
        "question_text": question_text,
        "answer": correct_answer_str,
        "correct_answer": correct_answer_str
    }


def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    user_answer 和 correct_answer 可能包含多個值，以 " 或 " 或 ',' 分隔。
    """
    # Normalize input by replacing "或" with "," and splitting
    user_answers_raw = [ans.strip() for ans in user_answer.replace("或", ",").split(',')]
    correct_answers_raw = [ans.strip() for ans in correct_answer.replace("或", ",").split(',')]

    def parse_answer(ans_str):
        # Handle fractions like '1/2' or integers '5'.
        # Remove LaTeX fraction formatting like \\frac{{1}}{{2}}
        ans_str = ans_str.replace("\\frac{{", "").replace("}}{{", "/").replace("}}", "")
        
        try:
            if '/' in ans_str:
                num, den = map(int, ans_str.split('/'))
                return Fraction(num, den)
            else:
                return Fraction(int(ans_str))
        except ValueError:
            return None # Indicate parsing error

    parsed_user_answers = set()
    for ua_raw in user_answers_raw:
        if ua_raw: # Avoid processing empty strings from extra commas
            parsed = parse_answer(ua_raw)
            if parsed is not None:
                parsed_user_answers.add(parsed)

    parsed_correct_answers = set()
    for ca_raw in correct_answers_raw:
        if ca_raw: # Avoid processing empty strings
            parsed = parse_answer(ca_raw)
            if parsed is not None:
                parsed_correct_answers.add(parsed)

    is_correct = (parsed_user_answers == parsed_correct_answers)
    
    # Feedback string, using double braces for LaTeX syntax within f-string
    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}