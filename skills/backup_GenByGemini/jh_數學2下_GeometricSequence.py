import random
from fractions import Fraction
import math

def format_number_latex(num):
    """Formats a number into a LaTeX string for display."""
    if isinstance(num, float):
        if num.is_integer():
            num = int(num)
        else:
            # Convert float to a reasonable fraction for LaTeX display
            try:
                num = Fraction(num).limit_denominator(1000)
            except (ValueError, OverflowError):
                return str(num) # Fallback for complex floats

    if isinstance(num, int):
        return str(num)
    
    if isinstance(num, Fraction):
        if num.denominator == 1:
            return str(num.numerator)
        if num.numerator == 0:
            return "0"
        sign = "-" if num.numerator < 0 else ""
        return f"{sign} \\frac{{{abs(num.numerator)}}}{{{num.denominator}}}"
    
    return str(num)

def format_number_plain(num):
    """Formats a number into a plain string for the answer key."""
    if isinstance(num, float):
        if num.is_integer():
            return str(int(num))
        return str(num)

    if isinstance(num, int):
        return str(num)
    
    if isinstance(num, Fraction):
        if num.denominator == 1:
            return str(num.numerator)
        return f"{num.numerator}/{num.denominator}"
        
    return str(num)

def normalize_answer(text):
    """Normalizes user answer for comparison by removing spaces and parentheses."""
    return text.strip().replace(" ", "").replace("(", "").replace(")", "")

def generate_identify_sequence_problem():
    """
    Generates a problem asking to identify a geometric sequence and its common ratio.
    Example: 判斷下列數列是否為等比數列。如果是，寫出公比。
    """
    is_geometric = random.random() < 0.75
    
    a1 = random.randint(1, 10) * random.choice([-1, 1])

    r_type = random.choice(['int', 'frac', 'decimal', 'one'])
    if r_type == 'int':
        r = random.choice([-3, -2, 2, 3])
    elif r_type == 'decimal':
        a1 = random.choice([1, 2, 4, 5]) # Use a nice starting term for decimals
        r = random.choice([0.1, 0.5, -0.5, -0.2])
    elif r_type == 'one':
        r = 1
    else: # frac
        r_num = random.randint(1, 3) * random.choice([-1, 1])
        r_den = random.randint(2, 4)
        r = Fraction(r_num, r_den)
        if abs(r.numerator) == r.denominator: # Avoid r = 1 or -1
            r = Fraction(1,2) * random.choice([-1,1])
            
    seq = []
    current_term = a1
    for _ in range(4):
        seq.append(current_term)
        # Handle potential floating point inaccuracies
        if isinstance(r, float):
            current_term = round(current_term * r, 10)
        else:
            current_term *= r

    question_seq = seq
    if not is_geometric:
        original_last = question_seq[-1]
        perturbation = random.randint(1, 2)
        if isinstance(original_last, Fraction):
            question_seq[-1] += Fraction(perturbation)
        else:
            question_seq[-1] += perturbation
        if question_seq[-1] == original_last: # Ensure it's different
            question_seq[-1] += 1
            
        plain_answer = "不是"
        latex_answer = "不是"
    else:
        plain_answer = format_number_plain(r)
        latex_answer = format_number_latex(r)

    formatted_seq_latex = ", ".join([format_number_latex(n) for n in question_seq])
    
    question_text = f"判斷下列數列是否為等比數列？<br>如果是，請寫出它的公比；如果不是，請回答「不是」。<br>$ {formatted_seq_latex} $"
    answer = f"{plain_answer}|{latex_answer}"
    
    return {
        "question_text": question_text,
        "answer": answer,
        "correct_answer": answer
    }

def generate_find_term_problem():
    """
    Generates a problem asking to find terms of a geometric sequence.
    Example: 首項為 5，公比為 2，寫出前 4 項。 or 第 5 項。
    """
    a1 = random.randint(1, 10) * random.choice([-1, 1])
    r = random.choice([-3, -2, 2, 3])
    
    problem_subtype = random.choice(['list_terms', 'find_nth_term'])
    
    if problem_subtype == 'list_terms':
        n = random.choice([3, 4])
        seq = [a1 * (r**i) for i in range(n)]
        
        question_text = f"若一等比數列的首項為 ${a1}$，公比為 ${r}$，請寫出此數列的前 ${n}$ 項。<br>(請用逗號分隔答案，例如: 1,2,4)"
        
        plain_answer = ", ".join(map(str, seq))
        latex_answer = plain_answer.replace(",", ",\\ ")
        
    else: # find_nth_term
        n = random.choice([4, 5])
        nth_term = a1 * (r**(n-1))
        
        question_text = f"若一等比數列的首項為 ${a1}$，公比為 ${r}$，求此數列的第 ${n}$ 項。"
        
        plain_answer = str(nth_term)
        latex_answer = str(nth_term)
        
    answer = f"{plain_answer}|{latex_answer}"
    return {
        "question_text": question_text,
        "answer": answer,
        "correct_answer": answer
    }

def generate_fill_blanks_problem():
    """
    Generates a problem asking to fill in the blanks of a geometric sequence.
    Example: ___, 2, 8, ___.
    """
    subtype = random.choice(['numeric', 'variable'])
    
    if subtype == 'numeric':
        r_type = random.choice(['int', 'frac'])
        if r_type == 'int':
            r = random.choice([-3, -2, 2, 3])
            s1 = r * random.randint(1, 5) * random.choice([-1, 1])
        else: # frac
            r = Fraction(random.choice([-1, 1]) * random.randint(1, 3), random.randint(2, 4))
            # Ensure s1 is a multiple of r's denominator so s0 is an integer
            s1 = r.denominator * random.randint(1, 3) * random.choice([-1, 1])

        s2 = s1 * r
        s0 = s1 / r
        s3 = s2 * r
        
        question_text = f"在下列空格中填入適當的數，使數列成為等比數列：<br>$ \\_\\_\\_ , {format_number_latex(s1)} , {format_number_latex(s2)} , \\_\\_\\_ $<br>(請依序填入兩個空格的數，並用逗號分隔)"
        
        plain_answer = f"{format_number_plain(s0)},{format_number_plain(s3)}"
        latex_answer = f"{format_number_latex(s0)},\\ {format_number_latex(s3)}"

    else: # variable
        c1 = random.randint(2, 7)
        c2 = random.randint(2, 7)
        while math.gcd(c1, c2) != 1:
            c1 = random.randint(2, 7)
            c2 = random.randint(2, 7)
        if random.random() < 0.5: # Randomly make one negative
            c1 *= -1

        s1_str = f"{c1}a"
        s2_str = f"{c2}a"
        
        r = Fraction(c2, c1)
        
        s0_coeff = c1 / r
        s3_coeff = c2 * r
        
        question_text = f"在下列空格中填入適當的數，使數列成為等比數列 ($ a \\neq 0 $)：<br>$ \\_\\_\\_ , {s1_str} , {s2_str} , \\_\\_\\_ $<br>(請依序填入兩個空格的數，並用逗號分隔，例如: 5/2a,-3a)"
        
        plain_answer = f"{format_number_plain(s0_coeff)}a,{format_number_plain(s3_coeff)}a"
        latex_answer = f"{format_number_latex(s0_coeff)}a,\\ {format_number_latex(s3_coeff)}a"
        
    answer = f"{plain_answer}|{latex_answer}"
    return {
        "question_text": question_text,
        "answer": answer,
        "correct_answer": answer
    }

def generate(level=1):
    """
    生成「等比數列」相關題目。
    包含：
    1. 判斷等比數列與求公比
    2. 給定首項與公比，求特定項或前n項
    3. 在數列中填空
    """
    problem_type = random.choice(['identify', 'find_term', 'fill_blanks'])
    
    if problem_type == 'identify':
        return generate_identify_sequence_problem()
    elif problem_type == 'find_term':
        return generate_find_term_problem()
    else: # 'fill_blanks'
        return generate_fill_blanks_problem()

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    if '|' in correct_answer:
        plain_answer, latex_answer = correct_answer.split('|', 1)
    else:
        plain_answer, latex_answer = correct_answer, correct_answer

    normalized_user = normalize_answer(user_answer)
    normalized_correct = normalize_answer(plain_answer)

    user_parts = normalized_user.split(',')
    correct_parts = normalized_correct.split(',')
    
    is_correct = False
    if len(user_parts) == len(correct_parts):
        all_parts_match = True
        for u_part, c_part in zip(user_parts, correct_parts):
            try:
                # Handle cases with variables like 'a' separately
                if 'a' in u_part or 'a' in c_part:
                    if u_part != c_part:
                        all_parts_match = False
                        break
                    continue

                # For numeric parts, compare as fractions for equivalence (e.g., 0.5 == 1/2)
                if Fraction(u_part) != Fraction(c_part):
                    all_parts_match = False
                    break
            except (ValueError, ZeroDivisionError):
                # If conversion fails (e.g., for "不是"), fall back to string comparison
                if u_part != c_part:
                    all_parts_match = False
                    break
        is_correct = all_parts_match

    result_text = f"完全正確！答案是 ${latex_answer}$。" if is_correct else f"答案不正確。正確答案應為：${latex_answer}$"
    
    return {"correct": is_correct, "result": result_text, "next_question": True}