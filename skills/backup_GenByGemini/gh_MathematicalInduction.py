import random
from fractions import Fraction
import re

def generate(level=1):
    """
    生成「數學歸納法」相關題目。
    包含：
    1. 數列遞迴關係與一般項猜測
    2. 整數性質證明（倍數問題）
    """
    problem_type = random.choice(['sequence_guess', 'divisibility_proof'])

    if problem_type == 'sequence_guess':
        return generate_sequence_guess_problem(level)
    else: # divisibility_proof
        return generate_divisibility_proof_problem(level)

def generate_sequence_guess_problem(level):
    """
    生成數列遞迴關係與一般項猜測題目。
    要求學生計算前幾項或猜測一般項公式。
    """
    # Define problem types with their recursive definition and general term
    problems = [
        { # Type 1: a_n = 1/(n+1)
            "a1": Fraction(1, 2),
            "recursive_relation": r"$a_{{n+1}} = \\frac{{a_n}}{{a_n+1}}$",
            "general_term": r"\\frac{{1}}{{n+1}}",
            "check_term_func": lambda n: Fraction(1, n + 1)
        },
        { # Type 2: a_n = (n+1)/n
            "a1": Fraction(2, 1),
            "recursive_relation": r"$a_{{n+1}} = 2 - \\frac{{1}}{{a_n}}$",
            "general_term": r"\\frac{{n+1}}{{n}}",
            "check_term_func": lambda n: Fraction(n + 1, n)
        },
        { # Type 3: a_n = 2 * 3^(n-1) - 1
            "a1": Fraction(1, 1),
            "recursive_relation": r"$a_{{n+1}} = 3a_n + 2$",
            "general_term": r"2 \cdot 3^{{n-1}} - 1",
            "check_term_func": lambda n: Fraction(2 * (3**(n - 1)) - 1)
        }
    ]

    chosen_problem = random.choice(problems)

    a1_val = chosen_problem["a1"]
    recursive_rel_str = chosen_problem["recursive_relation"]
    general_term_str = chosen_problem["general_term"]
    
    # Calculate a2, a3, a4
    a_terms = [a1_val]
    for i in range(1, 4): # Calculate up to a4
        n = i
        current_a = a_terms[n-1]
        if chosen_problem["recursive_relation"] == r"$a_{{n+1}} = \\frac{{a_n}}{{a_n+1}}$":
            next_term = current_a / (current_a + 1)
        elif chosen_problem["recursive_relation"] == r"$a_{{n+1}} = 2 - \\frac{{1}}{{a_n}}$":
            # Handle potential division by zero if a_n becomes 0. For these specific problems, a_n > 0 for n >= 1.
            next_term = 2 - (Fraction(1,1) / current_a)
        elif chosen_problem["recursive_relation"] == r"$a_{{n+1}} = 3a_n + 2$":
            next_term = 3 * current_a + 2
        a_terms.append(next_term)

    # Format the terms for question and answer
    formatted_terms_a2_a3_a4 = [format_fraction(term) for term in a_terms[1:4]] # a2, a3, a4
    
    # Randomly choose between asking for specific terms or the general formula
    question_mode = random.choice(['terms', 'formula'])

    if question_mode == 'terms':
        question_text = (
            f"設數列 $a_n$ 的遞迴關係式為 $a_1 = {format_fraction(a1_val)}$，{recursive_rel_str} ($n \\ge 1$)。<br>"
            f"請問 $a_2, a_3, a_4$ 的值分別為何？請以逗號分隔，並使用最簡分數表示。<br>"
            r"例如：$\\frac{{1}}{{2}}, 3, \\frac{{4}}{{5}}$"
        )
        correct_answer_value = ", ".join(formatted_terms_a2_a3_a4)
        # Store a marker to indicate this is a 'terms' problem
        correct_answer_id = f"sequence_terms_ans__{correct_answer_value}" 
    else: # formula
        # Generate some terms to help the user guess
        example_terms = [format_fraction(a_terms[i]) for i in range(min(4, len(a_terms)))]
        
        question_text = (
            f"設數列 $a_n$ 的遞迴關係式為 $a_1 = {format_fraction(a1_val)}$，{recursive_rel_str} ($n \\ge 1$)。<br>"
            f"觀察數列前幾項：$a_1={example_terms[0]}, a_2={example_terms[1]}, a_3={example_terms[2]}, \\dots$<br>"
            f"請猜測一般項 $a_n$ 的公式，並寫出其 LaTeX 數學式。例如：$\\frac{{n}}{{n+1}}$ 或 $2n+1$。"
        )
        correct_answer_value = f"${general_term_str}$" # Correct answer should be the LaTeX string
        correct_answer_id = f"sequence_formula_ans__{normalize_latex_expression(correct_answer_value)}"

    return {
        "question_text": question_text,
        "answer": correct_answer_value, # The student's answer should match this
        "correct_answer": correct_answer_id, # This is for internal check function to know the type
        "problem_type": problem_type
    }

def generate_divisibility_proof_problem(level):
    """
    生成數學歸納法證明整數性質（倍數問題）的題目。
    要求學生回答要證明的敘述。
    """
    # Predefined working divisibility patterns
    div_problems = [
        {"statement": r"$4^n+2$ 恆為 $6$ 的倍數"},
        {"statement": r"$3^n+1$ 恆為 $2$ 的倍數"},
        {"statement": r"$5^n+3$ 恆為 $4$ 的倍數"},
        {"statement": r"$6^n+4$ 恆為 $10$ 的倍數"},
        # General form: A^n - 1 is divisible by A-1
        {"statement": r"${{A}}^n-1$ 恆為 ${{A-1}}$ 的倍數", "params": {"A": random.choice([3, 4, 5, 6])}},
        # Corrected example from reference: x^(2n+1) + y^(2n) is divisible by M
        {"statement": r"$3^{{2n+1}}+5^{{2n}}$ 恆為 $4$ 的倍數"} 
    ]

    chosen_problem_template = random.choice(div_problems)
    
    statement = chosen_problem_template["statement"]
    
    # If it's the general A^n-1 form, substitute A
    if "params" in chosen_problem_template:
        A_val = chosen_problem_template["params"]["A"]
        M_val = A_val - 1
        # Use f-string for substitution, ensure double braces for literal LaTeX braces
        statement = f"${{A_val}}^{{n}}-1$ 恆為 ${M_val}$ 的倍數"
    
    question_text = (
        f"請使用數學歸納法證明：對於所有的正整數 $n$，{statement}。<br>"
        f"請寫出此數學歸納法要證明的敘述，包含必要的 LaTeX 符號。"
    )
    correct_answer_value = f"${statement}$" # The statement itself is the correct answer.
    correct_answer_id = f"divisibility_proof_ans__{normalize_latex_expression(correct_answer_value)}"

    return {
        "question_text": question_text,
        "answer": correct_answer_value,
        "correct_answer": correct_answer_id, # For internal check
        "problem_type": problem_type
    }

def format_fraction(frac):
    """Formats a Fraction object as a LaTeX string."""
    if frac.denominator == 1:
        return str(frac.numerator)
    return r"\\frac{{{}}}{{{}}}".format(frac.numerator, frac.denominator)

def normalize_latex_expression(expression):
    """
    Normalizes a LaTeX mathematical expression string for consistent comparison.
    - Removes whitespace
    - Standardizes exponent/subscript braces where possible without a full parser.
    """
    s = str(expression).strip()
    # Remove leading/trailing dollar signs
    if s.startswith('$') and s.endswith('$'):
        s = s[1:-1]
    
    s = s.replace(" ", "") # Remove all whitespace
    s = s.replace(r"\cdot", r"*") # Normalize multiplication symbol
    
    # Normalize fractions: \\frac{num}{den} -> (num)/(den) conceptually
    # This is a simplification and might not cover all LaTeX frac cases
    s = re.sub(r'\\frac\{(.*?)\}\{(.*?)\}', r'(\1)/(\2)', s)
    s = re.sub(r'\\frac(\w)(\w)', r'(\1)/(\2)', s) # Handle single char frac without braces if present

    # Normalize exponents and subscripts to always use braces
    s = re.sub(r'([a-zA-Z0-9])\^([a-zA-Z0-9\-\+\(\)]+)', r'\1^{\2}', s) # Covers x^2, x^{n-1}, x^{2n+1}
    s = re.sub(r'([a-zA-Z0-9])_([a-zA-Z0-9\-\+\(\)]+)', r'\1_{\2}', s)

    # Remove LaTeX backslashes for simple text comparison, keep braces
    s = s.replace(r"\left", "")
    s = s.replace(r"\right", "")
    s = s.replace(r"\text", "")
    s = s.replace(r"\\", "") # Remove double backslashes, if any

    # Replace common LaTeX structures with more programmatic equivalents for comparison
    s = s.replace("^{{n-1}}", "^{n-1}") # Example specific, normalize
    s = s.replace("^{{2n}}", "^{2n}")
    s = s.replace("^{{2n+1}}", "^{2n+1}")
    
    return s.lower() # Case insensitive comparison

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    user_answer: 學生提交的答案字串。
    correct_answer: 正確答案字串 (由 generate 函數提供，包含類型標識)。
    """
    is_correct = False
    feedback = ""

    # Determine problem type from correct_answer_id
    if correct_answer.startswith("sequence_terms_ans__"):
        actual_correct_value = correct_answer.split("__", 1)[1]
        try:
            user_terms = [Fraction(s.strip()) for s in user_answer.split(',')]
            correct_terms = [Fraction(s.strip()) for s in actual_correct_value.split(',')]
            
            if len(user_terms) == len(correct_terms):
                is_correct = all(u == c for u, c in zip(user_terms, correct_terms))
            else:
                is_correct = False
            
            if is_correct:
                feedback = f"完全正確！答案是 ${actual_correct_value}$。"
            else:
                feedback = f"答案不正確。請檢查每個數值是否正確，並使用最簡分數表示。正確答案應為：${actual_correct_value}$"
        except (ValueError, ZeroDivisionError):
            feedback = f"輸入格式不正確，請確保答案為逗號分隔的最簡分數。正確答案應為：${actual_correct_value}$"
            is_correct = False

    elif correct_answer.startswith("sequence_formula_ans__") or correct_answer.startswith("divisibility_proof_ans__"):
        actual_correct_normalized = correct_answer.split("__", 1)[1]
        user_answer_normalized = normalize_latex_expression(user_answer)
        
        is_correct = (user_answer_normalized == actual_correct_normalized)
        
        if is_correct:
            # Reconstruct original LaTeX for display if correct
            original_correct_latex = user_answer # Assume user's correct answer is close enough to show
            if not original_correct_latex.startswith('$'):
                original_correct_latex = f"${original_correct_latex}$"
            feedback = f"完全正確！答案是 {original_correct_latex}。"
        else:
            # For incorrect answers, show the normalized form of the correct answer for debugging/hint
            original_correct_latex = correct_answer.split("__", 1)[0].replace("_ans", "").replace("formula", "").replace("divisibilityproof", "證明敘述")
            feedback = f"答案不正確。請檢查你的公式或敘述是否完全符合題意和 LaTeX 格式。正確答案應為：${actual_correct_normalized}$"

    else:
        # Fallback for unexpected correct_answer format
        is_correct = False
        feedback = f"發生內部錯誤，無法檢查答案。請聯繫管理員。您的答案: {user_answer}, 正確答案: {correct_answer}"

    return {"correct": is_correct, "result": feedback, "next_question": True}