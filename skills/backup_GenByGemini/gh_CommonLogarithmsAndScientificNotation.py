import random
import math
import re # Added re for parsing bases from text in helper functions

# Predefined common logarithm constants and derived values based on log2, log3, log7
# Note: log5 is derived from log(10/2) = log10 - log2 = 1 - log2
LOG_CONSTANTS = {
    2: 0.3010,
    3: 0.4771,
    7: 0.8451,
    4: 2 * 0.3010,      # log(2^2) = 2log2
    5: 1 - 0.3010,      # log(10/2) = log10 - log2
    6: 0.3010 + 0.4771, # log(2*3) = log2 + log3
    8: 3 * 0.3010,      # log(2^3) = 3log2
    9: 2 * 0.4771       # log(3^2) = 2log3
}

def get_log10_from_constants(num):
    """
    Get log10 value for a given number using predefined constants or derivatives.
    This function strictly uses the LOG_CONSTANTS dictionary and basic log properties.
    """
    if num == 1:
        return 0.0 # log1 is always 0
    if num == 10:
        return 1.0 # log10 is always 1
    
    # If the number is a float like 0.5, 0.25, etc., attempt to convert to 1/X and use -logX
    if isinstance(num, float) and 0 < num < 1:
        # Check if 1/num is a recognizable integer that we have log for
        reciprocal = round(1/num)
        if abs(1/num - reciprocal) < 1e-9 and reciprocal in LOG_CONSTANTS:
            return -LOG_CONSTANTS[reciprocal]
        
    if num in LOG_CONSTANTS:
        return LOG_CONSTANTS[num]
    
    # This should ideally not be reached if problem generation adheres to bases
    # whose logs can be derived from the prime factors 2, 3, 5, 7.
    raise ValueError(f"Logarithm for base {num} not explicitly defined or derivable from constants.")

def get_relevant_log_bases(numbers):
    """
    Given a list of numbers (bases), identify which of the primary log constants (2, 3, 7)
    are strictly necessary to compute their logarithms, based on prime factorization.
    """
    relevant_primes = set()
    for num in numbers:
        if num == 1: continue # log1 is 0, no constant needed
        
        # If num is a float (e.g., 0.5), convert to its integer reciprocal for factorization
        if isinstance(num, float) and 0 < num < 1:
            reciprocal = round(1/num)
            if abs(1/num - reciprocal) < 1e-9:
                num = reciprocal # Now num is an integer (e.g., 2 for 0.5)
            else:
                # If not a simple reciprocal (e.g. 0.3), means it might be A/10 form.
                # For `log(A/B)`, both A and B are passed as integers.
                continue

        temp_num = int(num) # Ensure it's an integer for factorization
        
        if temp_num == 1: continue # Already handled, but double check for factored down numbers
        
        # Check for factor 2
        if temp_num % 2 == 0:
            relevant_primes.add(2)
            while temp_num > 1 and temp_num % 2 == 0: temp_num //= 2
        # Check for factor 3
        if temp_num % 3 == 0:
            relevant_primes.add(3)
            while temp_num > 1 and temp_num % 3 == 0: temp_num //= 3
        # Check for factor 7
        if temp_num % 7 == 0:
            relevant_primes.add(7)
            while temp_num > 1 and temp_num % 7 == 0: temp_num //= 7
        # Check for factor 5 (derived from log2 via log(10/2))
        if temp_num % 5 == 0:
            relevant_primes.add(2) # log5 requires log2 (1-log2)
            while temp_num > 1 and temp_num % 5 == 0: temp_num //= 5
        
        # If temp_num > 1 at this point, it means there are prime factors other than 2, 3, 5, 7.
        # This should ideally not happen for valid problem generation based on the given constants.
    
    return sorted(list(relevant_primes))

def format_log_constants(primes_needed):
    """Formats the log constants string for the question based on needed primes."""
    if not primes_needed:
        return ""
    log_parts = []
    for p in primes_needed:
        if p in LOG_CONSTANTS: # Only include if it's one of the primary ones
            log_parts.append(f"log{p} \\approx {LOG_CONSTANTS[p]:.4f}")
    if log_parts:
        return r" (已知 " + ", ".join(log_parts) + r")"
    return ""

def generate(level=1):
    problem_type = random.choice([
        'large_number_digits',
        'large_number_leading_digit',
        'small_number_position',
        'small_number_value_digit'
    ])
    
    if level == 1:
        # Simpler problems: single base^exponent
        if problem_type == 'large_number_digits':
            return generate_large_number_digits(single_term=True)
        elif problem_type == 'large_number_leading_digit':
            return generate_large_number_leading_digit(single_term=True)
        elif problem_type == 'small_number_position':
            return generate_small_number_position(single_term=True)
        else: # small_number_value_digit
            return generate_small_number_value_digit(single_term=True)
    elif level == 2:
        # More complex: mixed terms or slightly larger exponents
        single_term = random.random() < 0.5 # 50% chance for single term, 50% for multiple
        if problem_type == 'large_number_digits':
            return generate_large_number_digits(single_term=single_term)
        elif problem_type == 'large_number_leading_digit':
            return generate_large_number_leading_digit(single_term=single_term)
        elif problem_type == 'small_number_position':
            return generate_small_number_position(single_term=single_term)
        else: # small_number_value_digit
            return generate_small_number_value_digit(single_term=single_term)
    else: # level 3 - can ask for both digits/position AND leading/value
        choice = random.choice(['large_both', 'small_both'])
        if choice == 'large_both':
            return generate_large_number_both()
        else:
            return generate_small_number_both()

# --- Helper functions for specific problem types ---

def generate_large_number_digits(single_term=True):
    question_text = ""
    log_value = 0.0
    used_bases_for_calculation = set() # To track all integer bases involved

    if single_term:
        base = random.choice([2, 3, 4, 5, 6, 7, 8, 9])
        exponent = random.randint(20, 150)
        log_value = exponent * get_log10_from_constants(base)
        question_text = f"請問 ${base}^{{{exponent}}}$ 是幾位數？"
        used_bases_for_calculation.add(base)
    else: # multiple terms
        base1 = random.choice([2, 3, 4, 5, 6, 7])
        exp1 = random.randint(50, 200)
        
        base2 = random.choice([b for b in [2, 3, 4, 5, 6, 7] if b != base1])
        exp2 = random.randint(50, 200)

        log_value = exp1 * get_log10_from_constants(base1) + exp2 * get_log10_from_constants(base2)
        question_text = f"請問 ${base1}^{{{exp1}}} \\times {base2}^{{{exp2}}}$ 是幾位數？"
        used_bases_for_calculation.add(base1)
        used_bases_for_calculation.add(base2)

    characteristic = math.floor(log_value)
    num_digits = characteristic + 1
    correct_answer = str(num_digits)

    log_info = format_log_constants(get_relevant_log_bases(list(used_bases_for_calculation)))
    question_text = f"{question_text}{log_info}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_large_number_leading_digit(single_term=True):
    question_text = ""
    log_value = 0.0
    used_bases_for_calculation = set()

    if single_term:
        base = random.choice([2, 3, 4, 5, 6, 7, 8, 9])
        exponent = random.randint(20, 150)
        log_value = exponent * get_log10_from_constants(base)
        question_text = f"請問 ${base}^{{{exponent}}}$ 的最高位數字為何？"
        used_bases_for_calculation.add(base)
    else: # multiple terms
        base1 = random.choice([2, 3, 4, 5, 6, 7])
        exp1 = random.randint(50, 200)
        
        base2 = random.choice([b for b in [2, 3, 4, 5, 6, 7] if b != base1])
        exp2 = random.randint(50, 200)

        log_value = exp1 * get_log10_from_constants(base1) + exp2 * get_log10_from_constants(base2)
        question_text = f"請問 ${base1}^{{{exp1}}} \\times {base2}^{{{exp2}}}$ 的最高位數字為何？"
        used_bases_for_calculation.add(base1)
        used_bases_for_calculation.add(base2)

    mantissa = log_value - math.floor(log_value)
    leading_digit = math.floor(10**mantissa)
    correct_answer = str(int(leading_digit))
    
    log_info = format_log_constants(get_relevant_log_bases(list(used_bases_for_calculation)))
    question_text = f"{question_text}{log_info}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_small_number_position(single_term=True):
    question_text = ""
    log_value = 0.0
    used_bases_for_calculation = set()

    if single_term:
        # Base between 0 and 1, e.g., 0.2, 0.25, 0.5
        reciprocal_base = random.choice([2, 4, 5]) # e.g., 1/2, 1/4, 1/5
        base_float = 1 / reciprocal_base
        exponent = random.randint(50, 200)
        
        log_value = exponent * get_log10_from_constants(base_float) # get_log10_from_constants handles float reciprocals
        question_text = f"將 ${base_float}^{{{exponent}}}$ 表示成小數時，從小數點後第幾位開始出現不為0的數字？"
        used_bases_for_calculation.add(reciprocal_base) # Add the reciprocal base
    else: # multiple terms / fractional form
        base1_num = random.choice([1, 2, 3, 4, 6]) # Numerator (1 is special for log1=0)
        base1_den = random.choice([2, 3, 4, 5, 7, 8, 9, 10]) # Denominator
        # Ensure base1_num < base1_den for a value < 1
        while base1_num >= base1_den:
             base1_num = random.choice([1, 2, 3, 4, 6])
             base1_den = random.choice([2, 3, 4, 5, 7, 8, 9, 10]) # Adding 10 for log(X/10) cases
        
        exponent = random.randint(50, 200)

        # Calculate log of the fraction (log_num - log_den)
        log_base1_num = get_log10_from_constants(base1_num)
        log_base1_den = get_log10_from_constants(base1_den)
        log_value = exponent * (log_base1_num - log_base1_den)
        
        # Format the fraction string for LaTeX
        if base1_num == 1:
            fraction_str = r"\\frac{{1}}{{{base1_den}}}".format(base1_den=base1_den)
        else:
            fraction_str = r"\\frac{{{}}}{{{}}}".format(base1_num, base1_den)
        
        question_text = f"將 $({fraction_str})^{{{exponent}}}$ 表示成小數時，從小數點後第幾位開始出現不為0的數字？"
        used_bases_for_calculation.add(base1_num)
        used_bases_for_calculation.add(base1_den)

    characteristic = math.floor(log_value)
    position = abs(characteristic) 
    correct_answer = str(position)

    log_info = format_log_constants(get_relevant_log_bases(list(used_bases_for_calculation)))
    question_text = f"{question_text}{log_info}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_small_number_value_digit(single_term=True):
    question_text = ""
    log_value = 0.0
    used_bases_for_calculation = set()

    if single_term:
        reciprocal_base = random.choice([2, 4, 5])
        base_float = 1 / reciprocal_base
        exponent = random.randint(50, 200)
        
        log_value = exponent * get_log10_from_constants(base_float)
        question_text = f"將 ${base_float}^{{{exponent}}}$ 表示成小數時，從小數點後首次出現不為0的數字為何？"
        used_bases_for_calculation.add(reciprocal_base)
    else: # multiple terms / fractional form
        base1_num = random.choice([1, 2, 3, 4, 6])
        base1_den = random.choice([2, 3, 4, 5, 7, 8, 9, 10])
        while base1_num >= base1_den:
             base1_num = random.choice([1, 2, 3, 4, 6])
             base1_den = random.choice([2, 3, 4, 5, 7, 8, 9, 10])
        
        exponent = random.randint(50, 200)

        log_base1_num = get_log10_from_constants(base1_num)
        log_base1_den = get_log10_from_constants(base1_den)
        log_value = exponent * (log_base1_num - log_base1_den)
        
        if base1_num == 1:
            fraction_str = r"\\frac{{1}}{{{base1_den}}}".format(base1_den=base1_den)
        else:
            fraction_str = r"\\frac{{{}}}{{{}}}".format(base1_num, base1_den)
        
        question_text = f"將 $({fraction_str})^{{{exponent}}}$ 表示成小數時，從小數點後首次出現不為0的數字為何？"
        used_bases_for_calculation.add(base1_num)
        used_bases_for_calculation.add(base1_den)

    mantissa = log_value - math.floor(log_value)
    first_non_zero_digit = math.floor(10**mantissa)
    correct_answer = str(int(first_non_zero_digit))

    log_info = format_log_constants(get_relevant_log_bases(list(used_bases_for_calculation)))
    question_text = f"{question_text}{log_info}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_large_number_both():
    base = random.choice([2, 3, 4, 5, 6, 7])
    exponent = random.randint(60, 250)
    
    log_val = exponent * get_log10_from_constants(base)
    
    characteristic = math.floor(log_val)
    num_digits = characteristic + 1
    
    mantissa = log_val - characteristic
    leading_digit = math.floor(10**mantissa)
    
    question_text = f"請問 ${base}^{{{exponent}}}$ 是幾位數？最高位數字為何？"
    correct_answer = f"{num_digits}位數, 最高位數字為{int(leading_digit)}"
    
    log_info = format_log_constants(get_relevant_log_bases([base]))
    question_text = f"{question_text}{log_info}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_small_number_both():
    reciprocal_base = random.choice([2, 4, 5])
    base_float = 1 / reciprocal_base
    exponent = random.randint(60, 250)
    
    log_val = exponent * get_log10_from_constants(base_float)
    
    characteristic = math.floor(log_val)
    position = abs(characteristic)
    
    mantissa = log_val - characteristic
    first_non_zero_digit = math.floor(10**mantissa)
    
    question_text = f"將 ${base_float}^{{{exponent}}}$ 表示成小數時，從小數點後第幾位開始出現不為0的數字？此不為0的數字為何？"
    correct_answer = f"第{position}位, 數字為{int(first_non_zero_digit)}"

    log_info = format_log_constants(get_relevant_log_bases([reciprocal_base]))
    question_text = f"{question_text}{log_info}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip().lower().replace(" ", "").replace("最高位數字為", "數字為")
    correct_answer = correct_answer.strip().lower().replace(" ", "").replace("最高位數字為", "數字為")
    
    is_correct = False

    # Try exact match first
    if user_answer == correct_answer:
        is_correct = True
    else:
        # For numerical answers, try parsing. This block handles single answers.
        try:
            # Check for "X位數"
            if "位數" in correct_answer and "位數" in user_answer:
                ua_digits = "".join(filter(str.isdigit, user_answer.split('位數')[0]))
                ca_digits = "".join(filter(str.isdigit, correct_answer.split('位數')[0]))
                if ua_digits and ca_digits and int(ua_digits) == int(ca_digits):
                    is_correct = True
            # Check for "第X位"
            elif "第" in correct_answer and "位" in correct_answer and \
                 "第" in user_answer and "位" in user_answer:
                ua_pos = "".join(filter(str.isdigit, user_answer.split('第')[1].split('位')[0]))
                ca_pos = "".join(filter(str.isdigit, correct_answer.split('第')[1].split('位')[0]))
                if ua_pos and ca_pos and int(ua_pos) == int(ca_pos):
                    is_correct = True
            # Check for "數字為Y" (after replacing "最高位數字為" with "數字為")
            elif "數字為" in correct_answer and "數字為" in user_answer:
                ua_val = "".join(filter(str.isdigit, user_answer.split('數字為')[1]))
                ca_val = "".join(filter(str.isdigit, correct_answer.split('數字為')[1]))
                if ua_val and ca_val and int(ua_val) == int(ca_val):
                    is_correct = True
            else: # Try simple float/int comparison for pure numbers (e.g. if answer is just "3")
                try:
                    if float(user_answer) == float(correct_answer):
                        is_correct = True
                except ValueError:
                    pass
        except Exception:
            pass # Parsing failed for single answer, proceed to compound check

        if not is_correct: # If still not correct, try parsing as compound answer
            # For level 3 questions, where answer is "X位數, 數字為Y" or "第X位, 數字為Y"
            if "," in correct_answer and "," in user_answer:
                ca_parts = [p.strip() for p in correct_answer.split(',')]
                ua_parts = [p.strip() for p in user_answer.split(',')]

                if len(ca_parts) == len(ua_parts) == 2:
                    # Check first part (digits/position)
                    is_part1_correct = False
                    if "位數" in ca_parts[0] and "位數" in ua_parts[0]:
                        ua_digits = "".join(filter(str.isdigit, ua_parts[0].split('位數')[0]))
                        ca_digits = "".join(filter(str.isdigit, ca_parts[0].split('位數')[0]))
                        if ua_digits and ca_digits and int(ua_digits) == int(ca_digits):
                            is_part1_correct = True
                    elif "第" in ca_parts[0] and "位" in ca_parts[0] and \
                         "第" in ua_parts[0] and "位" in ua_parts[0]:
                        ua_pos = "".join(filter(str.isdigit, ua_parts[0].split('第')[1].split('位')[0]))
                        ca_pos = "".join(filter(str.isdigit, ca_parts[0].split('第')[1].split('位')[0]))
                        if ua_pos and ca_pos and int(ua_pos) == int(ca_pos):
                            is_part1_correct = True
                    
                    # Check second part (leading/first non-zero digit)
                    is_part2_correct = False
                    if "數字為" in ca_parts[1] and "數字為" in ua_parts[1]:
                        ua_val = "".join(filter(str.isdigit, ua_parts[1].split('數字為')[1]))
                        ca_val = "".join(filter(str.isdigit, ca_parts[1].split('數字為')[1]))
                        if ua_val and ca_val and int(ua_val) == int(ca_val):
                            is_part2_correct = True
                    
                    if is_part1_correct and is_part2_correct:
                        is_correct = True

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}