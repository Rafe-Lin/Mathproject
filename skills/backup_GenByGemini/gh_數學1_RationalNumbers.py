import random
from fractions import Fraction
import math

def _to_repeating_decimal_str(numerator, denominator):
    """
    Converts a fraction to its decimal representation, using overline for repeating parts.
    e.g., 2/11 -> "0.\\overline{18}"
    """
    if denominator == 0:
        raise ValueError("Denominator cannot be zero.")
    
    n, d = numerator, denominator
    
    sign = ''
    if n * d < 0:
        sign = '-'
    n, d = abs(n), abs(d)

    integer_part = n // d
    remainder = n % d

    if remainder == 0:
        return f"{sign}{integer_part}"

    decimal_part = []
    remainders_map = {} # Store remainder -> position

    while remainder != 0 and remainder not in remainders_map:
        remainders_map[remainder] = len(decimal_part)
        remainder *= 10
        decimal_part.append(str(remainder // d))
        remainder %= d

    if remainder == 0: # Terminating
        result = f"{sign}{integer_part}.{''.join(decimal_part)}"
    else: # Repeating
        repeat_start_pos = remainders_map[remainder]
        non_repeating = "".join(decimal_part[:repeat_start_pos])
        repeating = "".join(decimal_part[repeat_start_pos:])
        if non_repeating:
            result = f"{sign}{integer_part}.{non_repeating}\\overline{{{repeating}}}"
        else:
            result = f"{sign}{integer_part}.\\overline{{{repeating}}}"
    
    return result

def generate_frac_to_decimal_problem():
    """
    Generates a problem converting a fraction to a decimal (terminating or repeating).
    """
    if random.random() < 0.5:
        # Generate a fraction that results in a terminating decimal
        # Denominator's prime factors are only 2 and 5
        pow2 = random.randint(1, 4)
        pow5 = random.randint(0, 4)
        if pow2 == 0 and pow5 == 0: pow2 = 1 # Ensure denominator is not 1
        den = (2**pow2) * (5**pow5)
        num = random.randint(1, den - 1)
        
        f = Fraction(num, den)
        question_text = f"將下列有理數化成小數：<br>$\\frac{{{f.numerator}}}{{{f.denominator}}}$"
        # Standard float division is sufficient for terminating decimals
        correct_answer = f"{f.numerator / f.denominator}"
        
    else:
        # Generate a fraction that results in a repeating decimal
        # Denominator has prime factors other than 2 or 5
        den_base = random.choice([3, 7, 9, 11, 13, 17, 33, 37, 99])
        # Mix in some 2s or 5s to create mixed repeating decimals
        den = den_base * (2**random.randint(0, 2)) * (5**random.randint(0,1))
        num = random.randint(1, den - 1)

        f = Fraction(num, den)
        question_text = f"將下列有理數化成循環小數：<br>$\\frac{{{f.numerator}}}{{{f.denominator}}}$<br>(請用循環節表示法，例如 $0.\\overline{{3}}$ 或 $1.2\\overline{{34}}$)"
        correct_answer = _to_repeating_decimal_str(f.numerator, f.denominator)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_decimal_to_frac_problem():
    """
    Generates a problem converting a decimal (terminating or repeating) to a fraction.
    """
    if random.random() < 0.4:
        # Generate a terminating decimal
        decimal_places = random.randint(1, 3)
        den = 10**decimal_places
        # Allow numbers greater than 1
        num = random.randint(1, 2*den)
        decimal_val = num / den
        
        f = Fraction(num, den) # Automatically simplifies
        
        question_text = f"將下列小數化成最簡分數：<br>${decimal_val}$"
        correct_answer = f"{f.numerator}/{f.denominator}"
    
    else:
        # Generate a repeating decimal (pure or mixed)
        if random.random() < 0.5:
            # Pure repeating: I.\\overline{R}
            integer_part = random.randint(0, 5)
            repeating_len = random.randint(1, 2)
            # Avoid all 9s which is equivalent to a terminating decimal, and avoid 0
            repeating_num = random.randint(1, 10**repeating_len - 2) if repeating_len > 1 else random.randint(1, 8)
            repeating_str = str(repeating_num).zfill(repeating_len)

            question_text = f"將下列循環小數化成最簡分數：<br>${integer_part}.\\overline{{{repeating_str}}}$"
            
            den = 10**repeating_len - 1
            num = integer_part * den + repeating_num
            f = Fraction(num, den)
            correct_answer = f"{f.numerator}/{f.denominator}"

        else:
            # Mixed repeating: I.N\\overline{R}
            integer_part = random.randint(0, 5)
            non_repeating_len = random.randint(1, 2)
            repeating_len = random.randint(1, 2)

            non_repeating_num = random.randint(0, 10**non_repeating_len - 1)
            # Avoid all 9s and 0
            repeating_num = random.randint(1, 10**repeating_len - 2) if repeating_len > 1 else random.randint(1, 8)
            
            non_repeating_str = str(non_repeating_num).zfill(non_repeating_len)
            repeating_str = str(repeating_num).zfill(repeating_len)
            
            # Avoid cases like 0.0...0 repeating
            if non_repeating_num == 0 and repeating_num == 0 and integer_part == 0:
                integer_part = 1

            question_text = f"將下列循環小數化成最簡分數：<br>${integer_part}.{non_repeating_str}\\overline{{{repeating_str}}}$"
            
            # Use formula: (TotalNumber - NonRepeatingPart) / (9...90...0)
            full_num_str = str(integer_part) + non_repeating_str + repeating_str
            non_repeating_part_str = str(integer_part) + non_repeating_str
            
            num = int(full_num_str) - int(non_repeating_part_str)
            den = (10**repeating_len - 1) * (10**non_repeating_len)
            
            f = Fraction(num, den)
            correct_answer = f"{f.numerator}/{f.denominator}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    生成「有理數」相關題目。
    包含：
    1. 分數化小數 (有限與循環)
    2. 小數化分數 (有限與循環)
    """
    problem_type = random.choice(['frac_to_decimal', 'decimal_to_frac'])
    
    if problem_type == 'frac_to_decimal':
        return generate_frac_to_decimal_problem()
    else: # 'decimal_to_frac'
        return generate_decimal_to_frac_problem()

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。能處理分數、小數與循環小數表示法。
    """
    user_ans = user_answer.strip()
    correct_ans = correct_answer.strip()
    
    is_correct = (user_ans == correct_ans)
    result_text = ""

    if is_correct:
        result_text = f"完全正確！答案是 ${correct_ans}$。"
    else:
        # Check for non-simplified fraction or equivalent float representation
        try:
            if '/' in correct_ans:
                user_frac = Fraction(user_ans)
                correct_frac = Fraction(correct_ans)
                if user_frac == correct_frac:
                    result_text = f"答案 ${user_ans}$ 的值是正確的，但題目要求的是**最簡分數**。正確答案應為：${correct_ans}$"
                else:
                    result_text = f"答案不正確。正確答案應為：${correct_ans}$"
            elif '.' in correct_ans and '\\' not in correct_ans:
                 # Check for float equivalence (e.g., 0.5 vs 0.50)
                 if abs(float(user_ans) - float(correct_ans)) < 1e-9:
                     is_correct = True
                     result_text = f"完全正確！答案是 ${correct_ans}$。"
                 else:
                     result_text = f"答案不正確。正確答案應為：${correct_ans}$"
            else: # For repeating decimals, only exact string match counts
                result_text = f"答案不正確。正確答案應為：${correct_ans}$"
        except (ValueError, ZeroDivisionError):
             # User input was not a valid number/fraction
             result_text = f"答案不正確。正確答案應為：${correct_ans}$"

    return {"correct": is_correct, "result": result_text, "next_question": True}