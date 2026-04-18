import random
from fractions import Fraction
import re

def generate(level=1):
    """
    生成「多項式函數的反導函數」相關題目。
    包含：
    1. 計算多項式函數的不定積分。
    2. 反導函數不唯一性（常數C）的概念性問題。
    """
    problem_type = random.choice(['indefinite_integral', 'constant_concept'])

    if problem_type == 'indefinite_integral':
        return _generate_indefinite_integral_problem(level)
    elif problem_type == 'constant_concept':
        return _generate_constant_concept_problem(level)

def _generate_indefinite_integral_problem(level):
    """
    生成計算多項式函數不定積分的題目。
    """
    num_terms = random.randint(1, 3) if level == 1 else random.randint(2, 4)
    
    max_coeff = 5 if level == 1 else 10
    min_coeff = -5 if level == 1 else -10
    
    max_exp_f_x = 3 if level == 1 else 5 # For f(x), max power of x.
    min_exp_f_x = 0 # Polynomials always have non-negative integer exponents.
    
    original_terms = _generate_polynomial_terms(num_terms, max_coeff, min_coeff, max_exp_f_x, min_exp_f_x)
    
    f_x_string = _format_polynomial_terms_string(original_terms)
    
    antiderivative_terms = _get_antiderivative_terms(original_terms)
    F_x_string = _format_polynomial_terms_string(antiderivative_terms, include_c=True)
    
    # Question variations
    question_formats = [
        f"求函數 $f(x) = {f_x_string}$ 的反導函數，並以不定積分符號表示。",
        f"請計算不定積分 $\\int ({f_x_string}) dx$。",
        f"找出滿足 $F'(x) = {f_x_string}$ 的所有函數 $F(x)$。"
    ]
    question_text = random.choice(question_formats)
    
    return {
        "question_text": question_text,
        "answer": F_x_string, # Store the canonical form
        "correct_answer": F_x_string
    }

def _generate_constant_concept_problem(level):
    """
    生成關於反導函數常數C的概念性問題。
    """
    question_text = random.choice([
        r"請問不定積分 $\\int f(x) dx$ 中的 $+C$ 代表什麼？",
        r"若 $F'(x) = f(x)$，且 $G'(x) = f(x)$，請問 $F(x)$ 和 $G(x)$ 之間可能存在什麼關係？",
        r"為何多項式函數的反導函數不唯一？請簡要說明。",
        r"若函數 $f(x)$ 有一個反導函數為 $F(x)$，則 $f(x)$ 的所有反導函數可以如何表示？"
    ])
    
    # For conceptual questions, store a precise canonical answer for `check` to match against.
    # The `check` function will also use keyword matching for flexibility.
    if "代表什麼" in question_text or "如何表示" in question_text:
        canonical_answer = "代表任意常數"
    elif "關係" in question_text:
        canonical_answer = "相差一個常數"
    else: # "為何不唯一"
        canonical_answer = "因為常數項的微分為零"

    return {
        "question_text": question_text,
        "answer": canonical_answer, 
        "correct_answer": canonical_answer
    }

def _gcd(a, b):
    """計算兩個整數的最大公約數 (Greatest Common Divisor)。"""
    while b:
        a, b = b, a % b
    return a

def _format_fraction(frac):
    """
    將分數格式化為字串，若為整數則直接返回整數字串。
    例如：Fraction(1, 2) -> "1/2", Fraction(2, 1) -> "2"
    """
    if frac.denominator == 1:
        return str(frac.numerator)
    # 確保分數是最簡形式
    g = _gcd(abs(frac.numerator), frac.denominator)
    simplified_frac = Fraction(frac.numerator // g, frac.denominator // g)
    return f"{simplified_frac.numerator}/{simplified_frac.denominator}"

def _format_polynomial_terms_string(terms, include_c=False):
    """
    將多項式項列表 (係數, 指數) 格式化為 LaTeX 字串。
    """
    # Sort terms by exponent in descending order
    terms.sort(key=lambda t: t[1], reverse=True)
    
    parts = []
    
    # Filter out zero coefficient terms first
    non_zero_terms = [t for t in terms if t[0] != Fraction(0)]

    if not non_zero_terms:
        if include_c:
            return "$C$"
        return "$0$" 

    for i, (coeff, exp) in enumerate(non_zero_terms):
        coeff_abs_str = _format_fraction(abs(coeff))
        
        term_str = ""
        if exp == 0: # Constant term
            term_str = coeff_abs_str
        elif exp == 1: # x term
            if coeff_abs_str == "1":
                term_str = "x"
            else:
                term_str = f"{coeff_abs_str}x"
        else: # x^n, n > 1
            if coeff_abs_str == "1":
                term_str = f"x^{{{exp}}}"
            else:
                term_str = f"{coeff_abs_str}x^{{{exp}}}"
        
        # Add sign
        if coeff < 0:
            parts.append(f" - {term_str}")
        else:
            if i > 0: # Not the first term and positive, add '+'
                parts.append(f" + {term_str}")
            else: # First term and positive, no leading '+'
                parts.append(term_str)
                
    final_string = "".join(parts).strip()
    
    # Handle leading '-' if the first term was negative (strip the extra space added by " - ")
    if final_string.startswith("- "):
        final_string = "-" + final_string[2:]
    
    if include_c:
        final_string += " + C"

    return f"${final_string}$"

def _generate_polynomial_terms(num_terms, max_coeff, min_coeff, max_exp, min_exp):
    """
    生成多項式項列表 (係數, 指數)，確保指數唯一且係數不為零。
    """
    terms = []
    exponents = set()
    
    # Ensure a valid range for random.randint
    if min_exp > max_exp:
        min_exp, max_exp = max_exp, min_exp
    if min_coeff > max_coeff:
        min_coeff, max_coeff = max_coeff, min_coeff

    while len(terms) < num_terms:
        exp = random.randint(min_exp, max_exp)
        if exp in exponents:
            continue
        
        coeff = random.randint(min_coeff, max_coeff)
        if coeff == 0: # Coefficient cannot be zero for a distinct term
            continue
        
        terms.append((Fraction(coeff), exp))
        exponents.add(exp)
        
    return terms

def _get_antiderivative_terms(original_terms):
    """
    計算給定多項式項列表的反導函數項列表。
    """
    antiderivative_terms = []
    for coeff, exp in original_terms:
        # Antiderivative of ax^n is (a/(n+1))x^(n+1)
        # For polynomials, exponents are non-negative integers. So n+1 will always be >= 1.
        new_exp = exp + 1
        new_coeff = coeff / Fraction(new_exp)
        antiderivative_terms.append((new_coeff, new_exp))
    return antiderivative_terms


def check(user_answer, correct_answer):
    """
    檢查用戶答案是否正確。
    """
    # 1. 概念性問題的檢查
    # correct_answer for conceptual questions starts with "代表", "相差", "因為"
    if correct_answer.startswith("代表") or correct_answer.startswith("相差") or correct_answer.startswith("因為"):
        user_answer_lower = user_answer.strip().lower().replace(" ", "")
        
        is_correct = False
        feedback = ""
        
        # Keyword matching for flexibility
        if ("常數" in user_answer_lower or "c" in user_answer_lower) and \
           ("任意" in user_answer_lower or "一個" in user_answer_lower or "差異" in user_answer_lower or "零" in user_answer_lower or "皆為" in user_answer_lower):
            is_correct = True
            feedback = "完全正確！您理解了反導函數與常數的關係。"
        elif "相差" in user_answer_lower and ("常數" in user_answer_lower or "c" in user_answer_lower):
            is_correct = True
            feedback = "正確！兩個反導函數之間只會相差一個常數。"
        elif ("微分" in user_answer_lower or "導函數" in user_answer_lower) and \
             ("常數" in user_answer_lower or "c" in user_answer_lower) and "零" in user_answer_lower:
            is_correct = True
            feedback = "正確！因為常數項的微分為零，所以反導函數會存在一個任意常數。"
        else:
            is_correct = False
            feedback = f"答案不夠完整或不夠精確。正確答案應包含對「常數」或「不唯一性」的解釋。例如：{correct_answer}"
            
        return {"correct": is_correct, "result": feedback, "next_question": True}

    # 2. 計算不定積分問題的檢查
    # Correct answer format: $poly + C$
    user_answer_cleaned = user_answer.strip().replace(" ", "")
    correct_answer_no_dollar = correct_answer.strip().replace("$", "").replace(" ", "") 
    
    # Check for '+C' in user's answer
    has_user_c = False
    user_poly_part = user_answer_cleaned
    if user_poly_part.endswith("+C") or user_poly_part.endswith("+c"):
        user_poly_part = user_poly_part[:-2] # Remove '+C'
        has_user_c = True

    # Remove '+C' from correct_answer for polynomial comparison
    correct_poly_part = correct_answer_no_dollar
    if correct_poly_part.endswith("+C"):
        correct_poly_part = correct_poly_part[:-2]
    
    # Parse the polynomial parts into canonical (coeff, exp) lists
    parsed_user_terms = _parse_polynomial_string_for_check(user_poly_part)
    parsed_correct_terms = _parse_polynomial_string_for_check(correct_poly_part)

    # Convert to a dictionary for easy comparison (exponent -> coefficient)
    user_poly_dict = {exp: coeff for coeff, exp in parsed_user_terms}
    correct_poly_dict = {exp: coeff for coeff, exp in parsed_correct_terms}
    
    # Compare polynomial parts
    poly_matches = (user_poly_dict == correct_poly_dict)
    
    # Provide feedback based on comparison
    if poly_matches and has_user_c:
        feedback = f"完全正確！答案是 ${correct_answer_no_dollar}$。"
        is_correct = True
    elif poly_matches and not has_user_c:
        feedback = f"反導函數的項都正確，但別忘了加上任意常數 $C$！正確答案是 ${correct_answer_no_dollar}$。"
        is_correct = False 
    else: # Polynomial parts don't match
        feedback = f"答案不正確。請檢查多項式的各項積分是否正確，並記得加上任意常數 $C$。正確答案應為：${correct_answer_no_dollar}$"
        is_correct = False

    return {"correct": is_correct, "result": feedback, "next_question": True}

def _parse_polynomial_string_for_check(poly_str):
    """
    將多項式字串解析為標準化後的 (Fraction, int) 項列表，用於答案檢查。
    能夠處理 "3x^2", "-x", "1/2x", "5" 等形式。
    """
    poly_str = poly_str.replace(" ", "") # Remove all spaces
    if not poly_str:
        return []

    # Prepend '+' if the string doesn't start with a sign, to simplify splitting
    if poly_str[0] not in ['+', '-']:
        poly_str = "+" + poly_str
        
    # Split the string into individual signed terms
    raw_terms = re.findall(r'([+-][^+-]*)', poly_str)
    
    parsed_terms = []
    
    for term_raw in raw_terms:
        # Determine sign
        sign = 1
        if term_raw.startswith('-'):
            sign = -1
            term_str = term_raw[1:]
        elif term_raw.startswith('+'):
            sign = 1
            term_str = term_raw[1:]
        else: # Should not happen with prepended +
            term_str = term_raw

        coeff_val = Fraction(1) # Default coefficient is 1 for terms like x or x^2
        exp_val = 0 # Default exponent for constant terms

        # Match pattern: coefficient x^exponent (e.g., "3x^{2}", "1/2x^{3}")
        match = re.match(r'((?:\d+(?:/\d+)?)?)x\^\{(\d+)\}', term_str)
        if match:
            coeff_part = match.group(1)
            exp_val = int(match.group(2))
            if coeff_part:
                coeff_val = Fraction(coeff_part)
            else: # Implicit coefficient of 1 (e.g., "x^{2}")
                coeff_val = Fraction(1)
            parsed_terms.append((sign * coeff_val, exp_val))
            continue
        
        # Match pattern: coefficient x (exponent 1) (e.g., "2x", "x", "1/2x")
        match = re.match(r'((?:\d+(?:/\d+)?)?)x', term_str)
        if match:
            coeff_part = match.group(1)
            exp_val = 1
            if coeff_part:
                coeff_val = Fraction(coeff_part)
            else: # Implicit coefficient of 1 (e.g., "x")
                coeff_val = Fraction(1)
            parsed_terms.append((sign * coeff_val, exp_val))
            continue
            
        # Match pattern: just a constant (exponent 0) (e.g., "5", "1/4")
        match = re.match(r'(\d+(?:/\d+)?)', term_str)
        if match:
            coeff_part = match.group(1)
            if coeff_part:
                coeff_val = Fraction(coeff_part)
            exp_val = 0 # Constant term
            parsed_terms.append((sign * coeff_val, exp_val))
            continue
            
        # If nothing matched, it's an unparseable term. For robustness, skip it.
        # This can happen if the user inputs something completely malformed.

    # Combine like terms (sum coefficients for the same exponent)
    combined_terms_dict = {}
    for coeff, exp in parsed_terms:
        combined_terms_dict[exp] = combined_terms_dict.get(exp, Fraction(0)) + coeff
        
    # Filter out terms with zero coefficients and convert back to list
    final_terms = [(coeff, exp) for exp, coeff in combined_terms_dict.items() if coeff != Fraction(0)]
    
    return final_terms