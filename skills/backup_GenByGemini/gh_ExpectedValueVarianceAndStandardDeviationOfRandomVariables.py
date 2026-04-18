import random
from fractions import Fraction
import math
import re

# Helper function to convert fraction to string for LaTeX
def _fraction_to_latex(f):
    if not isinstance(f, Fraction):
        # Convert float to fraction if it's a float, limit denominator to avoid huge fractions from imprecise floats
        f = Fraction(f).limit_denominator(10000) 
    if f.denominator == 1:
        return str(f.numerator)
    return r"\\frac{{{}}}{{{}}}".format(f.numerator, f.denominator)

# Helper function to format a number for display (handles Fraction, float, int)
def _format_number_for_display(num):
    if isinstance(num, Fraction):
        return _fraction_to_latex(num)
    elif isinstance(num, float):
        # Round floats for display if they are not exact, but keep enough precision
        # And if it's an integer as a float (e.g., 5.0), display as integer
        if num.is_integer():
            return str(int(num))
        # Keep a reasonable number of decimal places for display, e.g., 2 or 3
        return f"{num:.3f}".rstrip('0').rstrip('.') # Remove trailing zeros
    else:
        return str(num)

# Helper function to parse user answer (supports fraction, float, integer)
def _parse_numeric_answer(ans_str):
    ans_str = ans_str.strip()
    # Try parsing as a fraction first
    if '/' in ans_str:
        try:
            parts = ans_str.split('/')
            if len(parts) == 2:
                numerator = int(parts[0])
                denominator = int(parts[1])
                if denominator == 0: return None # Avoid division by zero
                return Fraction(numerator, denominator)
        except ValueError:
            pass # Fall through to float parsing

    # Then try parsing as a float/integer
    try:
        f_val = float(ans_str)
        if f_val.is_integer():
            return int(f_val)
        return f_val
    except ValueError:
        return None # Not a valid number

# --- Problem Generators ---

def _generate_basic_ex_problem(level):
    """
    Generates a problem to calculate E(X) from a given probability distribution.
    """
    num_values = random.randint(2, 3) if level == 1 else random.randint(3, 4)
    x_values = sorted(random.sample(range(0, 10 * level + 5), num_values)) # Add 5 to range for more variety

    # Generate probabilities with a common denominator
    denominator = random.choice([4, 6, 8, 10, 12, 16, 20, 24, 30])
         
    numerator_parts = []
    attempts = 0
    # Loop until valid numerators are generated that sum to denominator and are all positive
    while True:
        attempts += 1
        if attempts > 100: # Fallback to a simpler generation if stuck
            denominator = max(num_values, random.randint(num_values, num_values * 3)) # Ensure enough 'parts' for each x
            
        remaining_sum = denominator
        current_numerator_parts = []
        possible = True
        for i in range(num_values):
            if i == num_values - 1: # Last part
                current_numerator_parts.append(remaining_sum)
            else:
                max_part = remaining_sum - (num_values - 1 - i) # Ensure remaining parts can be at least 1
                if max_part <= 0: 
                    possible = False
                    break
                part = random.randint(1, max_part)
                current_numerator_parts.append(part)
                remaining_sum -= part
        
        if possible and sum(current_numerator_parts) == denominator and all(p > 0 for p in current_numerator_parts):
            numerator_parts = current_numerator_parts
            break
        # Reset for next attempt
        numerator_parts = []


    probabilities = [Fraction(p, denominator) for p in numerator_parts]
    random.shuffle(probabilities) # Shuffle to not correlate with x_values order

    # Calculate E(X)
    e_x = Fraction(0)
    for i in range(num_values):
        e_x += x_values[i] * probabilities[i]

    # Build the probability distribution table for LaTeX
    x_row = " & ".join([_format_number_for_display(x) for x in x_values])
    p_x_row = " & ".join([_format_number_for_display(p) for p in probabilities])

    table = r"""
\begin{{array}}{{|c|{}}}
\hline
x & {} \\
\hline
P(X=x) & {} \\
\hline
\end{{array}}
""".format('c' * num_values, x_row, p_x_row)

    question_text = f"已知隨機變數 $X$ 的機率分布表如下，求 $X$ 的期望值 $E(X)$。<br>{table}"
    correct_answer = _format_number_for_display(e_x)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "type": "basic_ex"
    }

def _generate_basic_var_std_problem(level):
    """
    Generates a problem to calculate E(X), Var(X), and Std(X).
    """
    num_values = random.randint(3, 4) if level <= 2 else random.randint(4, 5)
    x_values = sorted(random.sample(range(0, 8 * level + 5), num_values))
    
    denominator = random.choice([4, 6, 8, 10, 12, 16, 20, 24, 30])
    
    numerator_parts = []
    attempts = 0
    while True:
        attempts += 1
        if attempts > 100: # Fallback
            denominator = max(num_values, random.randint(num_values, num_values * 3))
        
        remaining_sum = denominator
        current_numerator_parts = []
        possible = True
        for i in range(num_values):
            if i == num_values - 1:
                current_numerator_parts.append(remaining_sum)
            else:
                max_part = remaining_sum - (num_values - 1 - i)
                if max_part <= 0:
                    possible = False
                    break
                part = random.randint(1, max_part)
                current_numerator_parts.append(part)
                remaining_sum -= part
        
        if possible and sum(current_numerator_parts) == denominator and all(p > 0 for p in current_numerator_parts):
            numerator_parts = current_numerator_parts
            break
        numerator_parts = []

    probabilities = [Fraction(p, denominator) for p in numerator_parts]
    random.shuffle(probabilities)

    # Calculate E(X)
    e_x = sum(x_values[i] * probabilities[i] for i in range(num_values))

    # Calculate Var(X)
    # Using Var(X) = E(X^2) - (E(X))^2
    e_x_squared = sum((x_values[i]**2) * probabilities[i] for i in range(num_values))
    var_x = e_x_squared - e_x**2

    # Calculate Std(X)
    std_x = math.sqrt(float(var_x))

    # Build the probability distribution table for LaTeX
    x_row = " & ".join([_format_number_for_display(x) for x in x_values])
    p_x_row = " & ".join([_format_number_for_display(p) for p in probabilities])

    table = r"""
\begin{{array}}{{|c|{}}}
\hline
x & {} \\
\hline
P(X=x) & {} \\
\hline
\end{{array}}
""".format('c' * num_values, x_row, p_x_row)

    question_text = f"已知隨機變數 $X$ 的機率分布表如下，求 $X$ 的期望值 $E(X)$、變異數 $Var(X)$ 與標準差 $\\sigma(X)$。<br>{table}"
    
    e_x_str = _format_number_for_display(e_x)
    var_x_str = _format_number_for_display(var_x)
    std_x_str = f"{std_x:.3f}".rstrip('0').rstrip('.') if std_x % 1 != 0 else str(int(std_x))

    # Removed dollar signs from here, for easier parsing in check function
    correct_answer = f"E(X) = {e_x_str}, Var(X) = {var_x_str}, \\sigma(X) = {std_x_str}" 

    return {
        "question_text": question_text,
        "answer": correct_answer, 
        "correct_answer": correct_answer,
        "type": "basic_var_std",
    }

def _generate_find_unknown_problem(level):
    """
    Generates a problem to find an unknown count 'n' given E(X).
    Example: Bag with different coins/items, one type has 'n' items.
    """
    # Generate item values (money/points)
    x_values = sorted(random.sample([10, 20, 50, 100, 200, 500], 3)) # Choose 3 distinct values

    # Generate two known counts
    known_counts = [random.randint(2, 6), random.randint(2, 6)]
    # The actual unknown count 'n' to be solved for
    n_actual = random.randint(3, 10)

    # Randomly decide which position 'n' will be in the question text
    pos_n = random.randint(0, 2)
    
    # Create the list of counts for each x_value, with 'n_actual' at pos_n
    all_counts_for_calc = [0, 0, 0]
    known_idx = 0
    for i in range(3):
        if i == pos_n:
            all_counts_for_calc[i] = n_actual
        else:
            all_counts_for_calc[i] = known_counts[known_idx]
            known_idx += 1
            
    # Calculate the total actual expected value for this setup
    total_items_actual = sum(all_counts_for_calc)
    e_x_target_numerator = sum(x_values[i] * all_counts_for_calc[i] for i in range(3))
    e_x_target = Fraction(e_x_target_numerator, total_items_actual)

    # Construct the question text with 'n' as the unknown
    item_descriptions = []
    for i in range(3):
        value_str = _format_number_for_display(x_values[i])
        if i == pos_n:
            item_descriptions.append(f"${value_str}$ 元代幣 $n$ 枚")
        else:
            item_descriptions.append(f"${value_str}$ 元代幣 ${all_counts_for_calc[i]}$ 枚")
    
    question_text = f"袋中有 {item_descriptions[0]}、{item_descriptions[1]} 與 {item_descriptions[2]}。" \
                    f"從袋中抽出一枚代幣，且每枚代幣被取到的機會均等，並令隨機變數 $X$ 表示抽出代幣的金額。" \
                    f"已知 $X$ 的期望值為 ${_format_number_for_display(e_x_target)}$ 元，求 $n$ 的值。"
    
    correct_answer = str(n_actual)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "type": "find_unknown"
    }

def _generate_linear_transform_problem(level):
    """
    Generates a problem involving Y = aX + b transformation.
    """
    # Start with a simple X distribution (e.g., number of heads in 2 coin flips)
    x_values = [0, 1, 2]
    # For fair coins
    probabilities = [Fraction(1, 4), Fraction(2, 4), Fraction(1, 4)] 
    
    e_x = sum(x_values[i] * probabilities[i] for i in range(len(x_values)))
    e_x_squared = sum((x_values[i]**2) * probabilities[i] for i in range(len(x_values)))
    var_x = e_x_squared - e_x**2
    std_x = math.sqrt(float(var_x))

    # Generate a and b for Y = aX + b
    # Ensure 'a' is not zero and 'b' can be zero
    a = random.choice([-5, -2, 2, 5, 10, 20]) # Multiplier for X
    b = random.choice([-10, -5, 0, 5, 10, 20]) # Constant offset
    
    e_y = a * e_x + b
    var_y = Fraction(a**2 * var_x) # Var(aX+b) = a^2 Var(X)
    std_y = abs(a) * std_x # Std(aX+b) = |a| Std(X)

    # Build the probability distribution table for X for LaTeX
    # This table is fixed for the 2 coin flip example.
    table_x = r"""
\begin{{array}}{{|c|c|c|c|}}
\hline
x & 0 & 1 & 2 \\
\hline
P(X=x) & \\frac{{1}}{{4}} & \\frac{{2}}{{4}} & \\frac{{1}}{{4}} \\
\hline
\end{{array}}
""" 

    question_text = f"同時丟兩枚均勻的硬幣一次，設隨機變數 $X$ 表示正面出現的枚數。其機率分布表如下。<br>{table_x}<br>" \
                    f"設隨機變數 $Y = {a}X + {b}$，求 $Y$ 的期望值 $E(Y)$ 與標準差 $\\sigma(Y)$。"
    
    e_y_str = _format_number_for_display(e_y)
    std_y_str = f"{std_y:.3f}".rstrip('0').rstrip('.') if std_y % 1 != 0 else str(int(std_y))

    # Removed dollar signs from here, for easier parsing in check function
    correct_answer = f"E(Y) = {e_y_str}, \\sigma(Y) = {std_y_str}" 

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "type": "linear_transform",
    }


def generate(level=1):
    """
    Generates problems related to Expected Value, Variance, and Standard Deviation of Random Variables.
    """
    problem_type_choices = ['basic_ex']
    if level >= 2:
        problem_type_choices.extend(['basic_var_std', 'find_unknown'])
    if level >= 3:
        problem_type_choices.append('linear_transform')

    problem_type = random.choice(problem_type_choices)

    if problem_type == 'basic_ex':
        return _generate_basic_ex_problem(level)
    elif problem_type == 'basic_var_std':
        return _generate_basic_var_std_problem(level)
    elif problem_type == 'find_unknown':
        return _generate_find_unknown_problem(level)
    elif problem_type == 'linear_transform':
        return _generate_linear_transform_problem(level)
    else: # Fallback, should not happen with current choices
        return _generate_basic_ex_problem(level)


def check(user_answer, correct_answer):
    """
    Checks the user's answer against the correct answer.
    Handles multiple parts of an answer (e.g., E(X), Var(X), Std(X)).
    The correct_answer string is expected to be in a format like "E(X) = val1, Var(X) = val2"
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()

    # Determine if it's a single value or multi-part answer based on the correct_answer format
    if " = " not in correct_answer: # Single value answer
        parsed_user = _parse_numeric_answer(user_answer)
        parsed_correct = _parse_numeric_answer(correct_answer)
        is_correct = False
        if parsed_user is not None and parsed_correct is not None:
            if isinstance(parsed_user, float) or isinstance(parsed_correct, float):
                is_correct = math.isclose(float(parsed_user), float(parsed_correct), rel_tol=1e-3, abs_tol=1e-5)
            else:
                is_correct = (parsed_user == parsed_correct)
        
        result_text = f"完全正確！答案是 ${_format_number_for_display(parsed_correct)}$。" if is_correct else f"答案不正確。正確答案應為：${_format_number_for_display(parsed_correct)}$"
        return {"correct": is_correct, "result": result_text, "next_question": True}

    # Multi-part answer processing
    correct_parts_map = {}
    for part_str in correct_answer.split(', '):
        if ' = ' in part_str:
            key, value_str = part_str.split(' = ', 1)
            correct_parts_map[key.strip()] = _parse_numeric_answer(value_str.strip())

    is_correct_overall = True
    feedback_parts = []
    
    # Try to extract named parts from user answer using regex
    # Pattern to find "KEY = VALUE" or "KEY: VALUE" or just "VALUE" in list
    # Keys can be like E(X), Var(X), \\sigma(X), E(Y), \\sigma(Y)
    
    # This regex is for extracting specific key-value pairs (e.g., "E(X)=10", "\\sigma(X)=2.5")
    user_named_parts_matches = re.findall(r'([a-zA-Z\(\)\\\_]+)\s*[=:]\s*([+\-]?\d+(?:/\d+)?(?:\.\d*)?)', user_answer)
    
    user_parsed_values_map = {}
    for key, value_str in user_named_parts_matches:
        user_parsed_values_map[key.strip()] = _parse_numeric_answer(value_str.strip())

    if user_named_parts_matches and len(user_named_parts_matches) == len(correct_parts_map):
        # User provided answers with explicit keys matching the number of correct parts
        for key in correct_parts_map:
            correct_val = correct_parts_map[key]
            user_val = user_parsed_values_map.get(key)
            
            part_is_correct = False
            if user_val is not None and correct_val is not None:
                if isinstance(user_val, float) or isinstance(correct_val, float):
                    part_is_correct = math.isclose(float(user_val), float(correct_val), rel_tol=1e-3, abs_tol=1e-5)
                else:
                    part_is_correct = (user_val == correct_val)
            
            if not part_is_correct:
                is_correct_overall = False
            
            feedback_parts.append(f"${key} = {_format_number_for_display(user_val or '無效輸入')}$ ({'正確' if part_is_correct else '錯誤'}，正確答案為 ${_format_number_for_display(correct_val)}$)")
    else: 
        # If user did not provide named parts or number of named parts don't match,
        # fallback to extracting all numbers and comparing in order.
        numeric_values_user_str = re.findall(r'([+\-]?\d+(?:/\d+)?(?:\.\d*)?)', user_answer)
        user_parsed_values = [_parse_numeric_answer(v) for v in numeric_values_user_str]

        if len(user_parsed_values) != len(correct_parts_map):
            is_correct_overall = False
            feedback_parts.append(f"您的答案格式不符合要求或缺少部分答案。正確答案需包含 {len(correct_parts_map)} 個數值。")
        else:
            for i, key in enumerate(correct_parts_map.keys()): # Iterate through correct keys in order
                correct_val = correct_parts_map[key]
                user_val = user_parsed_values[i]
                
                part_is_correct = False
                if user_val is not None and correct_val is not None:
                    if isinstance(user_val, float) or isinstance(correct_val, float):
                        part_is_correct = math.isclose(float(user_val), float(correct_val), rel_tol=1e-3, abs_tol=1e-5)
                    else:
                        part_is_correct = (user_val == correct_val)
                else:
                    part_is_correct = False
                
                if not part_is_correct:
                    is_correct_overall = False
                feedback_parts.append(f"${key} = {_format_number_for_display(user_val or '無效輸入')}$ ({'正確' if part_is_correct else '錯誤'}，正確答案為 ${_format_number_for_display(correct_val)}$)")

    result_text = "您的答案：" + ", ".join(feedback_parts)
    if is_correct_overall:
        result_text = f"完全正確！{result_text}"
    else:
        result_text = f"答案不完全正確。<br>{result_text}<br>正確答案應為：{correct_answer}"

    return {"correct": is_correct_overall, "result": result_text, "next_question": True}