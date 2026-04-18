import random
from fractions import Fraction
import math

def _format_fraction(f, latex=True, mixed=True):
    """
    Helper to format Fraction objects into strings (LaTeX or plain).
    Handles mixed numbers and signs.
    e.g., Fraction(-5, 3) -> "$-1\\frac{{2}}{{3}}$" (latex, mixed)
          Fraction(5, 3) -> "5/3" (plain, not mixed)
          Fraction(3, 4) -> "$\\frac{{3}}{{4}}$" (latex)
    """
    if not isinstance(f, Fraction):
        f = Fraction(f)

    if f.denominator == 1:
        return str(f.numerator)

    sign = ""
    if f.numerator < 0:
        sign = "-"
    
    abs_f = abs(f)
    num = abs_f.numerator
    den = abs_f.denominator
    
    integer_part = num // den
    remainder = num % den
    
    if remainder == 0:
        return f"{sign}{integer_part}"

    # Use improper fraction format if not mixed or it's a proper fraction
    if not mixed or integer_part == 0:
        if latex:
            return f"${sign}\\frac{{{num}}}{{{den}}}$"
        else:
            return f"{sign}{num}/{den}"
    else:  # Format as a mixed number
        if latex:
            return f"${sign}{integer_part}\\frac{{{remainder}}}{{{den}}}$"
        else:
            # e.g., "-1 2/3"
            return f"{sign}{integer_part} {remainder}/{den}"

def generate_simplification_problem():
    """
    Generates a problem asking to simplify a fraction, or to identify
    if it's already a simplest fraction. Corresponds to textbook example 1.
    """
    # 40% chance of generating a fraction that is already in its simplest form
    if random.random() < 0.4:
        n = random.randint(2, 19)
        d = random.randint(n + 1, 20)
        # Ensure they are coprime
        while math.gcd(n, d) != 1:
            n = random.randint(2, 19)
            d = random.randint(n + 1, 20)

        is_negative = random.choice([True, False])
        
        display_num = n
        display_den = d
        if is_negative:
            # Randomly place the negative sign on the numerator or denominator for variety
            if random.choice([True, False]):
                display_num = -n
            else:
                display_den = -d
        
        question_text = f"判斷分數 $\\frac{{{display_num}}}{{{display_den}}}$ 是否為最簡分數？若不是，請化為最簡分數。"
        correct_answer = "是最簡分數"

        return {
            "question_text": question_text,
            "answer": correct_answer,
            "correct_answer": correct_answer
        }
    else:
        # Generate a fraction that can be simplified
        n = random.randint(1, 10)
        d = random.randint(n + 1, 12)
        while math.gcd(n, d) != 1:
             n = random.randint(1, 10)
             d = random.randint(n + 1, 12)
        
        k = random.randint(2, 7) # Common factor
        
        num = n * k
        den = d * k
        
        f_simple = Fraction(n, d)
        
        # Randomly make it negative
        if random.random() < 0.5:
            num = -num
            f_simple = -f_simple

        question_text = f"請將分數 $\\frac{{{num}}}{{{den}}}$ 化為最簡分數。"
        # The answer should be an improper fraction if applicable, not mixed.
        correct_answer = _format_fraction(f_simple, latex=False, mixed=False)

        return {
            "question_text": question_text,
            "answer": correct_answer,
            "correct_answer": correct_answer
        }

def generate_comparison_problem():
    """
    Generates a problem asking to compare 2 or 3 fractions.
    Corresponds to textbook examples 2, 3, 4, 5.
    """
    num_fractions = random.choice([2, 3])
    fractions = set()
    while len(fractions) < num_fractions:
        # Generate a reasonably simple fraction
        is_mixed = random.random() < 0.5 # 50% chance of being > 1
        d = random.randint(2, 12)
        if is_mixed:
            i_part = random.randint(1, 3)
            n_part = random.randint(1, d - 1)
            n = i_part * d + n_part
        else:
            # Proper fraction
            n = random.randint(1, d - 1)
        
        f = Fraction(n, d)
        
        # 50% chance of being negative
        if random.random() < 0.5:
            f = -f
            
        fractions.add(f)
    
    fractions_list = list(fractions)
    random.shuffle(fractions_list)
    
    # Use mixed numbers for display in the question
    question_fractions_str = [_format_fraction(f, latex=True, mixed=True) for f in fractions_list]

    sorted_fractions = sorted(fractions_list)
    
    # Randomly choose between ascending (<) or descending (>) order
    use_ascending = random.choice([True, False])
    
    if use_ascending:
        direction = "小到大"
        op = "<"
        ordered_list = sorted_fractions
    else:
        direction = "大到小"
        op = ">"
        ordered_list = sorted_fractions[::-1]
        
    question_text = f"請將下列各數由**{direction}**排列，並用 '{op}' 連接：{', '.join(question_fractions_str)}"
    
    # Create a map from fraction object to its plain string representation for the answer key
    frac_map = {f: _format_fraction(f, latex=False, mixed=True) for f in fractions_list}
    
    answer_parts = [frac_map[f] for f in ordered_list]
    correct_answer = f" {op} ".join(answer_parts)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    主生成函數，隨機選擇一種「最簡分數與比較」的題型。
    包含：
    1. 化為最簡分數或判斷是否為最簡分數。
    2. 比較 2 個或 3 個分數的大小。
    """
    problem_type = random.choice(['simplification', 'comparison'])
    
    if problem_type == 'simplification':
        return generate_simplification_problem()
    else: # comparison
        return generate_comparison_problem()

def check(user_answer, correct_answer):
    """
    檢查使用者答案是否正確。
    - 對於「是最簡分數」的判斷，檢查關鍵字。
    - 對於分數和比較題，標準化字串後進行比較。
    """
    user_ans = user_answer.strip()
    correct_ans = correct_answer.strip()

    is_correct = False
    
    # Case 1: Answer is a keyword phrase
    if correct_ans == "是最簡分數":
        if "是" in user_ans or "最簡" in user_ans:
            is_correct = True
    # Case 2: Answer is a fraction or a comparison string
    else:
        # Normalize by removing all whitespace for a robust comparison
        norm_user = "".join(user_ans.split())
        norm_correct = "".join(correct_ans.split())
        if norm_user == norm_correct:
            is_correct = True

    result_text = f"完全正確！答案是 {correct_ans}。" if is_correct else f"答案不正確。正確答案應為：{correct_ans}"
    return {"correct": is_correct, "result": result_text, "next_question": True}
