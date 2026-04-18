import random
from fractions import Fraction
import math
import re

# Helper function to convert a fraction to its decimal representation string
# This function handles both terminating and repeating decimals and formats them
# into a string, using LaTeX's \\overline for repeating parts.
def fraction_to_decimal_str(numerator, denominator):
    if denominator == 0:
        raise ValueError("Denominator cannot be zero.")

    frac = Fraction(numerator, denominator)
    numerator = frac.numerator
    denominator = frac.denominator

    sign_str = ""
    if numerator < 0:
        sign_str = "-"
        numerator = abs(numerator)

    integer_part = numerator // denominator
    remainder = numerator % denominator

    if remainder == 0:
        return f"{sign_str}{integer_part}" # e.g., 4/2 = 2

    # Check for terminating decimal: denominator has only prime factors 2 and 5
    temp_denom = denominator
    while temp_denom % 2 == 0:
        temp_denom //= 2
    while temp_denom % 5 == 0:
        temp_denom //= 5

    if temp_denom == 1:
        # Terminating decimal
        # Use float division and string formatting to get the decimal string.
        # .rstrip('0').rstrip('.') handles cases like 0.200 -> 0.2 and 5.0 -> 5
        return f"{sign_str}{float(numerator) / denominator}".rstrip('0').rstrip('.')
    else:
        # Repeating decimal
        decimal_parts = []
        remainders = {} # Stores {remainder: position_in_decimal_parts}
        position = 0

        current_remainder = remainder
        # Max iterations to prevent infinite loop for very large denominators,
        # but large enough to find common repeats. The cycle length is at most denominator - 1.
        max_iterations = 2 * denominator # A safe upper bound for length of non-repeating + repeating parts

        while current_remainder != 0 and position < max_iterations:
            if current_remainder in remainders:
                start_repeat_pos = remainders[current_remainder]
                non_repeating_part = "".join(decimal_parts[:start_repeat_pos])
                repeating_part = "".join(decimal_parts[start_repeat_pos:])
                
                # Format with LaTeX \\overline
                if non_repeating_part:
                    return f"{sign_str}{integer_part}.{non_repeating_part}\\{'overline'}{{{repeating_part}}}"
                else:
                    # If integer part is 0 and no non_repeating, should be 0.\\overline{...}
                    # e.g. 1/3 -> 0.\\overline{3}
                    return f"{sign_str}{integer_part}.\\{'overline'}{{{repeating_part}}}"
            
            remainders[current_remainder] = position
            current_remainder *= 10
            decimal_parts.append(str(current_remainder // denominator))
            current_remainder %= denominator
            position += 1
        
        # Fallback for very long non-repeating/repeating parts not captured by max_iterations
        # This branch should ideally not be reached if the `temp_denom == 1` check is robust and max_iterations is sufficient.
        # However, for safety, return a truncated decimal representation.
        decimal_part_str = "".join(decimal_parts)
        if decimal_part_str:
            return f"{sign_str}{integer_part}.{decimal_part_str}"
        else: # Should mean it was an integer already caught by `remainder == 0`
            return f"{sign_str}{integer_part}"


# Helper function to convert a decimal string (finite or repeating with \\overline) to Fraction
def decimal_str_to_fraction(decimal_str):
    # Handle negative sign
    sign = 1
    if decimal_str.startswith('-'):
        sign = -1
        decimal_str = decimal_str[1:]

    # Check for \\overline notation (escaped backslash)
    # Regex captures integer part, optional non-repeating part, and repeating block
    overline_match = re.match(r"(\d*)(?:\.(\d*))?\\overline{(\d+)}", decimal_str)
    if overline_match:
        integer_part_str, non_repeating_str, repeating_str = overline_match.groups()
        
        integer_part = int(integer_part_str) if integer_part_str else 0
        
        # Ensure non_repeating_str and repeating_str are handled correctly if None
        non_repeating_str = non_repeating_str if non_repeating_str is not None else ""
        repeating_str = repeating_str if repeating_str is not None else ""

        len_non_repeating = len(non_repeating_str)
        len_repeating = len(repeating_str)

        if not repeating_str: # If \\overline{} is empty, treat as finite decimal
             return Fraction(sign * float(f"{integer_part}.{non_repeating_str}"))

        # Formula for repeating decimals: (ABC - AB) / (10^(m+n) - 10^m)
        # where A is integer part, B is non-repeating part, C is repeating part.
        
        # Number formed by A.B C (integer part + non-repeating + repeating block)
        full_num_str = f"{integer_part}{non_repeating_str}{repeating_str}"
        # Number formed by A.B (integer part + non-repeating block)
        non_repeat_prefix_str = f"{integer_part}{non_repeating_str}" if non_repeating_str else str(integer_part)
        
        num_up_to_repeat = int(full_num_str) if full_num_str else 0
        num_up_to_non_repeat = int(non_repeat_prefix_str) if non_repeat_prefix_str else 0
        
        numerator_val = num_up_to_repeat - num_up_to_non_repeat
        denominator_val = (10**(len_non_repeating + len_repeating)) - (10**len_non_repeating)
        
        # Handle edge case like 0.\\overline{0} which simplifies to 0
        if numerator_val == 0 and denominator_val == 0:
            return Fraction(0)

        return sign * Fraction(numerator_val, denominator_val)

    # If no \\overline, treat as finite decimal or simple fraction string
    try:
        if '/' in decimal_str: # Already a fraction string "N/D"
            n, d = map(int, decimal_str.split('/'))
            return Fraction(sign * n, d)
        
        # For long decimals (user might input approximation of repeating decimal),
        # use limit_denominator to find a nearby simple fraction.
        # This is a heuristic that works well for common repeating decimals if enough digits are provided.
        if '.' in decimal_str and len(decimal_str.split('.')[1]) > 10: # Heuristic for "long" decimals
            return Fraction(sign * float(decimal_str)).limit_denominator(1000000) # Increased limit for robustness
        
        return Fraction(sign * float(decimal_str)) # Handles finite decimals accurately
    except ValueError:
        raise ValueError(f"無法將 '{decimal_str}' 轉換為有理數。請確保格式正確。")


def generate(level=1):
    """
    生成「有理數」相關題目。
    包含：
    1. 分數轉小數 (有限小數或循環小數)
    2. 小數轉分數 (有限小數或循環小數)
    """
    problem_type = random.choice([
        'fraction_to_decimal',
        'decimal_to_fraction'
    ])

    if problem_type == 'fraction_to_decimal':
        return generate_fraction_to_decimal_problem(level)
    elif problem_type == 'decimal_to_fraction':
        return generate_decimal_to_fraction_problem(level)

def generate_fraction_to_decimal_problem(level):
    # Roughly half terminating, half repeating decimals
    is_terminating = random.choice([True, False])

    if is_terminating:
        # Generate terminating decimal
        # Denominator should only have prime factors 2 and/or 5
        pow_2 = random.randint(1, min(level + 1, 4)) # e.g., max 2^4 = 16
        pow_5 = random.randint(0, min(level + 1, 3)) # e.g., max 5^3 = 125
        
        denominator = (2**pow_2) * (5**pow_5)
        
        # Ensure a reasonable denominator range (e.g., between 4 and 1000)
        if denominator < 4: 
            denominator *= 4 
        if denominator > 1000: 
            denominator //= random.choice([2, 5]) 
        if denominator == 0: 
            denominator = 1 # Fallback for edge cases

        # Allow improper fractions up to 3 times the denominator's value
        numerator_range = random.randint(1, 3) * denominator 
        numerator = random.randint(1, numerator_range) 
        
        # Simplify the fraction
        frac = Fraction(numerator, denominator)
        numerator, denominator = frac.numerator, frac.denominator
        
        question_text = f"將有理數 $\\frac{{{numerator}}}{{{denominator}}}$ 化成小數。"
        correct_answer_decimal_str = fraction_to_decimal_str(numerator, denominator)
        
        return {
            "question_text": question_text,
            "answer": correct_answer_decimal_str, # e.g. "0.275" as expected output
            "correct_answer": str(frac) # Store as simplified fraction string for robust check
        }
    else:
        # Generate repeating decimal
        # Denominator should have prime factors other than 2 or 5
        # Pre-selected list of denominators that result in repeating decimals (avoiding very long cycles for lower levels)
        possible_denominators = [3, 6, 7, 9, 11, 12, 13, 14, 15, 17, 18, 19, 21, 22, 23, 26, 27, 28, 33, 34, 35, 37, 39, 41, 42, 43, 44, 45, 46, 47, 48, 51, 52, 55, 56, 57, 58, 63, 65, 66, 68, 69, 70, 74, 75, 76, 77, 78, 82, 84, 85, 87, 88, 91, 92, 93, 94, 95, 96, 99, 101, 102, 105, 111, 114, 117, 119, 121, 123, 126, 130, 133, 136, 143, 153, 154, 156, 161, 165, 170, 182, 187, 195, 203, 204, 209, 210, 221, 231, 238, 247, 255]
        
        # Filter denominators based on level to manage complexity
        max_denom_for_level = 30 + level * 20 
        suitable_denominators = [d for d in possible_denominators if d <= max_denom_for_level]
        
        if not suitable_denominators: # Fallback if filtering results in an empty list
            suitable_denominators = [3, 7, 9, 11, 13, 17, 19, 21, 23, 27, 33, 37]
        
        denominator = random.choice(suitable_denominators)
        
        # Allow improper fractions
        numerator_range = random.randint(1, 3) * denominator
        numerator = random.randint(1, numerator_range)
        
        # Simplify the fraction
        frac = Fraction(numerator, denominator)
        numerator, denominator = frac.numerator, frac.denominator
        
        question_text = f"將有理數 $\\frac{{{numerator}}}{{{denominator}}}$ 化成小數。"
        correct_answer_decimal_str = fraction_to_decimal_str(numerator, denominator)
        
        return {
            "question_text": question_text,
            "answer": correct_answer_decimal_str, # e.g. "0.\\overline{18}" as expected output
            "correct_answer": str(frac) # Store as simplified fraction string for robust check
        }

def generate_decimal_to_fraction_problem(level):
    # Roughly half terminating, half repeating decimals
    is_repeating = random.choice([True, False])

    if not is_repeating:
        # Generate terminating decimal
        integer_part = random.randint(0, min(level + 1, 5)) # Integer part up to 5
        decimal_places = random.randint(1, min(level + 1, 4)) # 1 to 4 decimal places
        
        frac_val = random.randint(1, 10**decimal_places - 1)
        
        # For higher levels, try to avoid trivial decimal parts (e.g., 0.20 instead of 0.2)
        if level > 1 and decimal_places > 1:
            while frac_val % 10 == 0: # If it ends in 0, it means it can be shortened
                frac_val = random.randint(1, 10**decimal_places - 1)
            # Make sure it's not a very simple fraction like 0.5 (1/2) unless level is low
            if decimal_places >= 2 and frac_val in [25, 50, 75]:
                 frac_val = random.randint(1, 10**decimal_places - 1)


        # Format with leading zeros for fractional part if needed (e.g., 0.05)
        decimal_str = f"{integer_part}.{frac_val:0{decimal_places}d}"
        
        frac = Fraction(decimal_str) # Fraction class handles direct conversion
        question_text = f"將小數 ${decimal_str}$ 化成最簡分數。"
        
        return {
            "question_text": question_text,
            "answer": f"\\frac{{{frac.numerator}}}{{{frac.denominator}}}", # e.g. "\\frac{7}{25}" as expected output
            "correct_answer": str(frac) # Store as simplified fraction string for robust check
        }
    else:
        # Generate repeating decimal (can be pure or mixed)
        is_mixed_repeating = random.choice([True, False])
        
        integer_part = random.randint(0, min(level + 1, 3)) # Integer part up to 3
        
        if not is_mixed_repeating:
            # Pure repeating like 0.\\overline{32}
            repeating_len = random.randint(1, min(level + 1, 2)) # 1 or 2 digits in repeat
            repeating_block = random.randint(1, 10**repeating_len - 1)
            if repeating_block == 0: 
                repeating_block = 1 # Avoid 0.\\overline{0}
            
            decimal_str_latex = f"{integer_part}.\\{'overline'}{{{repeating_block:0{repeating_len}d}}}"
            
        else:
            # Mixed repeating like 1.4\\overline{3}
            non_repeating_len = random.randint(1, min(level + 1, 2)) # 1 or 2 non-repeating digits
            repeating_len = random.randint(1, min(level + 1, 2)) # 1 or 2 repeating digits
            
            non_repeating_part = random.randint(0, 10**non_repeating_len - 1)
            repeating_block = random.randint(1, 10**repeating_len - 1)
            if repeating_block == 0: 
                repeating_block = 1 # Avoid repeating block of all zeros

            # Ensure non_repeating_part isn't just zero for a more meaningful "mixed" decimal
            if non_repeating_part == 0 and non_repeating_len > 0:
                if random.random() < 0.7: # High chance to make it non-zero if it was 0
                    non_repeating_part = random.randint(1, 10**non_repeating_len - 1)

            decimal_str_latex = f"{integer_part}.{non_repeating_part:0{non_repeating_len}d}\\{'overline'}{{{repeating_block:0{repeating_len}d}}}"
        
        frac = decimal_str_to_fraction(decimal_str_latex)
        question_text = f"將小數 ${decimal_str_latex}$ 化成最簡分數。"
        
        return {
            "question_text": question_text,
            "answer": f"\\frac{{{frac.numerator}}}{{{frac.denominator}}}", # e.g. "\\frac{43}{30}" as expected output
            "correct_answer": str(frac) # Store as simplified fraction string for robust check
        }


def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    user_answer: 用戶輸入的答案字符串 (可以是分數, 有限小數, 或帶有\\overline的循環小數)
    correct_answer: generate函數返回的正確答案（內部儲存的簡化分數的字符串形式，例如 "2/11"）
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip() 

    is_correct = False
    result_text = ""

    try:
        # Convert user's input to a Fraction object using the robust helper function
        user_fraction = decimal_str_to_fraction(user_answer)
        # Convert the internally stored correct_answer string (e.g., "2/11") to a Fraction object
        correct_fraction = Fraction(correct_answer) 
        
        if user_fraction == correct_fraction:
            is_correct = True
            # For feedback, display the simplified correct fraction using LaTeX \\frac
            result_text = f"完全正確！答案是 $\\frac{{{correct_fraction.numerator}}}{{{correct_fraction.denominator}}}$。"
        else:
            result_text = f"答案不正確。正確答案應為：$\\frac{{{correct_fraction.numerator}}}{{{correct_fraction.denominator}}}$"

    except ValueError as e:
        # If conversion to Fraction failed, it means user input wasn't in a recognizable format.
        result_text = f"答案格式不正確或數值錯誤。錯誤訊息：{e}"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}