import random
from fractions import Fraction
import math # For is_integer() and math.isclose

# Helper function to format numbers (int, float, or Fraction) for display in LaTeX math mode
def format_number(num):
    if isinstance(num, Fraction):
        if num.denominator == 1:
            return str(num.numerator)
        # Using double backslash for LaTeX command \\frac
        return r"\\frac{{{}}}{{{}}}".format(num.numerator, num.denominator)
    if isinstance(num, float):
        if num.is_integer():
            return str(int(num))
        # Ensure float formatting is reasonable for display
        return str(round(num, 4)) # Round to 4 decimal places for consistency
    return str(num)

# Helper function to format linear function string f(x) = ax + b
def format_linear_function(a, b):
    a_str = ""
    # Handle coefficient 'a'
    if a == 1 or (isinstance(a, Fraction) and a == Fraction(1,1)):
        a_str = "x"
    elif a == -1 or (isinstance(a, Fraction) and a == Fraction(-1,1)):
        a_str = "-x"
    elif a != 0 and not (isinstance(a, Fraction) and a == Fraction(0,1)):
        a_str = f"{format_number(a)}x"
    
    b_str = ""
    # Handle constant term 'b'
    if b > 0 or (isinstance(b, Fraction) and b > 0):
        b_str = f" + {format_number(b)}"
    elif b < 0 or (isinstance(b, Fraction) and b < 0):
        b_str = f" - {format_number(abs(b))}"
        
    # If a is zero, the function is just f(x) = b (horizontal line, but we enforce a != 0 for linear functions)
    if (a == 0 or (isinstance(a, Fraction) and a == Fraction(0,1))) and (b != 0 or (isinstance(b, Fraction) and b != Fraction(0,1))):
        return f"{format_number(b)}"
    
    return f"{a_str}{b_str}"

def generate_type1_problem():
    """
    生成題型1：已知兩點，求 f(x) 及函數值變化。
    Example: 已知一次函數 f(x) 滿足 f(2) = 1 , f(4) = 5 。(1)求 f(x) ，並描繪 f(x) 的圖形。(2)每當*x*增加3單位時，其相對應的函數值增加或減少多少單位？
    """
    # Generate integer coefficients for 'a' and 'b' to ensure clean solutions
    a_val = random.randint(-5, 5)
    while a_val == 0: # 'a' cannot be 0 for a linear function
        a_val = random.randint(-5, 5)
    b_val = random.randint(-10, 10)

    # Generate two distinct x-coordinates
    x1_val = random.randint(-5, 5)
    x2_val = random.randint(-5, 5)
    while x1_val == x2_val:
        x2_val = random.randint(-5, 5)
    
    # Calculate corresponding y-coordinates
    y1_val = a_val * x1_val + b_val
    y2_val = a_val * x2_val + b_val

    # Generate x-change for the second part of the question
    x_change = random.randint(1, 5)
    y_change = a_val * x_change
    
    # Determine if function value increases or decreases
    change_word = "增加" if y_change >= 0 else "減少"
    
    question_text = (
        f"已知一次函數 $f(x)$ 滿足 $f({format_number(x1_val)}) = {format_number(y1_val)}$, "
        f"$f({format_number(x2_val)}) = {format_number(y2_val)}$。"
        f"<br>(1) 求 $f(x)$。"
        f"<br>(2) 每當 $x$ 增加 ${format_number(x_change)}$ 單位時，其相對應的函數值{change_word}或減少多少單位？"
    )

    f_x_str = format_linear_function(a_val, b_val)
    
    ans_part1 = f"f(x) = {f_x_str}"
    ans_part2 = f"{change_word}{format_number(abs(y_change))}單位"

    correct_answer = f"(1) {ans_part1}, (2) {ans_part2}"

    return {
        "question_text": question_text,
        "answer": correct_answer, # For display purposes
        "correct_answer": correct_answer # For checking
    }

def generate_type2_problem():
    """
    生成題型2：多選題，關於一次函數的性質 (斜率、y截距、f(0)、變化率)。
    Example: 設一次函數 f(x) 滿足 f(1) = -1 , f(3) = 5 ，且 f(x) 的圖形是直線L，選出所有正確的選項。
    """
    # Generate integer coefficients for 'a' and 'b'
    a_val = random.randint(-5, 5)
    while a_val == 0:
        a_val = random.randint(-5, 5)
    b_val = random.randint(-10, 10)

    # Generate two distinct x-coordinates
    x1_val = random.randint(-5, 5)
    x2_val = random.randint(-5, 5)
    while x1_val == x2_val:
        x2_val = random.randint(-5, 5)
    
    # Calculate corresponding y-coordinates
    y1_val = a_val * x1_val + b_val
    y2_val = a_val * x2_val + b_val

    options_data = [] # List of tuples: (option_text, is_correct)

    # Option 1: f(0) value
    f0_val = b_val
    incorrect_f0_val = f0_val + random.choice([-2, -1, 1, 2])
    if random.random() < 0.7: # 70% chance to be correct
        options_data.append((f"(1) $f(0) = {format_number(f0_val)}$", True))
    else:
        options_data.append((f"(1) $f(0) = {format_number(incorrect_f0_val)}$", False))

    # Option 2: Slope sign
    slope_sign_desc = "正" if a_val > 0 else "負"
    incorrect_slope_sign_desc = "負" if a_val > 0 else "正"
    if random.random() < 0.7:
        options_data.append((f"(2) $L$ 的斜率為{slope_sign_desc}", True))
    else:
        options_data.append((f"(2) $L$ 的斜率為{incorrect_slope_sign_desc}", False))
        
    # Option 3: y-intercept value
    incorrect_y_intercept = b_val + random.choice([-2, -1, 1, 2])
    if random.random() < 0.7:
        options_data.append((f"(3) $L$ 的 $y$ 截距為 ${format_number(b_val)}$", True))
    else:
        options_data.append((f"(3) $L$ 的 $y$ 截距為 ${format_number(incorrect_y_intercept)}$", False))

    # Option 4: Slope formula (always correct, as per example)
    options_data.append((f"(4) $L$ 的斜率等於 $({format_number(y2_val)} - ({format_number(y1_val)})) / ({format_number(x2_val)} - {format_number(x1_val)})$", True))

    # Option 5: Rate of change
    x_change_for_option = random.randint(1, 3)
    y_change_for_option = a_val * x_change_for_option
    change_word_option = "增加" if y_change_for_option >= 0 else "減少"
    
    if random.random() < 0.7:
        options_data.append(
            (f"(5) 每當 $x$ 增加 ${format_number(x_change_for_option)}$ 單位時，"
            f"其相對應的函數值{change_word_option}{format_number(abs(y_change_for_option))}單位。", True)
        )
    else:
        # Generate an incorrect rate of change
        # Add or subtract 1 from the correct y_change to make it incorrect
        incorrect_y_change_for_option = y_change_for_option + random.choice([-1, 1])
        incorrect_change_word_option = "增加" if incorrect_y_change_for_option >= 0 else "減少"
        options_data.append(
            (f"(5) 每當 $x$ 增加 ${format_number(x_change_for_option)}$ 單位時，"
            f"其相對應的函數值{incorrect_change_word_option}{format_number(abs(incorrect_y_change_for_option))}單位。", False)
        )

    random.shuffle(options_data) # Shuffle options to avoid fixed order bias
    
    question_text_options = []
    correct_options_indices = []
    
    # Re-number options after shuffling and collect correct indices
    for i, (text, is_correct) in enumerate(options_data):
        # The text might contain original option number like "(1) ...". Remove it and use new index.
        # Find the first ')' and take the substring after it.
        # This assumes original option numbers are always followed by a ')'.
        new_text_content = text[text.find(')')+1:].strip() 
        new_option_text = f"({i+1}) {new_text_content}"
        question_text_options.append(new_option_text)
        if is_correct:
            correct_options_indices.append(str(i+1)) # Store new index

    question_text = (
        f"設一次函數 $f(x)$ 滿足 $f({format_number(x1_val)}) = {format_number(y1_val)}$, "
        f"$f({format_number(x2_val)}) = {format_number(y2_val)}$，且 $f(x)$ 的圖形是直線 $L$，選出所有正確的選項。"
        f"<br>{'<br>'.join(question_text_options)}"
    )
    
    correct_answer = ",".join(sorted(correct_options_indices))

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_type3_problem():
    """
    生成題型3：線性內插，已知兩點求第三點的函數值。
    Example: 已知一次函數 f(x) 滿足 f(1.23) = 2 , f(9.71) = 18 ，求 f(3.35) 的值。
    """
    # Choose two x values that can be decimals
    x1_val = round(random.uniform(-10.0, 5.0), 2)
    x2_val = round(random.uniform(6.0, 20.0), 2)
    
    # Choose two y values (can be integers or decimals for final result)
    y1_val = random.randint(-10, 10)
    y2_val = random.randint(-10, 10)
    while y1_val == y2_val: # Ensure non-zero slope
        y2_val = random.randint(-10, 10)
    
    # Ensure x1 < x2 for consistent interpolation logic
    if x1_val > x2_val:
        x1_val, x2_val = x2_val, x1_val
        y1_val, y2_val = y2_val, y1_val # Swap y values as well

    # Choose x3 such that x1 < x3 < x2 and it's distinct from x1, x2
    x3_val = round(random.uniform(x1_val + 0.1, x2_val - 0.1), 2)
    while math.isclose(x3_val, x1_val) or math.isclose(x3_val, x2_val):
        x3_val = round(random.uniform(x1_val + 0.1, x2_val - 0.1), 2)

    # Convert all inputs to Fraction for precise calculations to avoid floating point errors
    x1_frac = Fraction(str(x1_val))
    y1_frac = Fraction(y1_val)
    x2_frac = Fraction(str(x2_val))
    y2_frac = Fraction(y2_val)
    x3_frac = Fraction(str(x3_val))

    # Calculate slope 'a' and y-intercept 'b'
    a_frac = (y2_frac - y1_frac) / (x2_frac - x1_frac)
    b_frac = y1_frac - a_frac * x1_frac
    
    # Calculate f(x3)
    f_x3_val_frac = a_frac * x3_frac + b_frac
    
    # Format the answer: if it's an integer, display as integer; otherwise, display as float (rounded)
    if f_x3_val_frac.denominator == 1:
        correct_answer_str = str(f_x3_val_frac.numerator)
    else:
        correct_answer_str = str(round(float(f_x3_val_frac), 4)) # Round to 4 decimal places for consistency

    question_text = (
        f"已知一次函數 $f(x)$ 滿足 $f({format_number(x1_val)}) = {format_number(y1_val)}$, "
        f"$f({format_number(x2_val)}) = {format_number(y2_val)}$，求 $f({format_number(x3_val)})$ 的值。"
    )

    return {
        "question_text": question_text,
        "answer": correct_answer_str,
        "correct_answer": correct_answer_str
    }

def generate(level=1):
    """
    主生成函數，根據難度或其他邏輯隨機選擇題目類型。
    """
    problem_type = random.choice(['type1', 'type2', 'type3'])

    if problem_type == 'type1':
        return generate_type1_problem()
    elif problem_type == 'type2':
        return generate_type2_problem()
    else: # type3
        return generate_type3_problem()

def check(user_answer, correct_answer):
    """
    檢查使用者答案是否正確。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()

    is_correct = False
    result_text = ""

    # Helper to normalize strings for comparison (remove spaces, convert to lower)
    def normalize_str_for_comparison(s):
        # Remove all whitespace and convert to lowercase
        return s.replace(' ', '').lower()

    if "(1)" in correct_answer and "(2)" in correct_answer: # Type 1 problem: two parts
        try:
            # Example correct_answer: "(1) f(x) = 2x - 3, (2) 增加6單位"
            # Split the correct answer into two parts
            corr_parts = correct_answer.split(', (2)')
            corr_fx_part = normalize_str_for_comparison(corr_parts[0].replace('(1)', ''))
            corr_roc_part = normalize_str_for_comparison(corr_parts[1])

            # Attempt to split user answer with common separators
            user_parts_candidate = user_answer.split(',(2)') # Try with no space before (2)
            if len(user_parts_candidate) != 2:
                user_parts_candidate = user_answer.split(', (2)') # Try with space before (2)
            
            if len(user_parts_candidate) == 2:
                user_fx_part = normalize_str_for_comparison(user_parts_candidate[0].replace('(1)', ''))
                user_roc_part = normalize_str_for_comparison(user_parts_candidate[1])

                if user_fx_part == corr_fx_part and user_roc_part == corr_roc_part:
                    is_correct = True
                    result_text = f"完全正確！答案是 ${correct_answer}$。"
                else:
                    result_text = f"答案不完全正確。正確答案應為：${correct_answer}$"
            else:
                result_text = f"答案格式不正確。正確答案應包含兩部分，例如：(1) f(x) = ax + b, (2) 增加/減少 X 單位。您的答案: {user_answer}"
        except Exception:
            result_text = f"答案格式解析錯誤。請確保您的答案格式與範例相似。正確答案應為：${correct_answer}$"

    elif "," in correct_answer and not ("f(x)" in correct_answer or "=" in correct_answer): # Type 2 problem: comma-separated options (not an f(x)= equation)
        user_options = sorted([normalize_str_for_comparison(o) for o in user_answer.split(',') if o.strip()])
        correct_options = sorted([normalize_str_for_comparison(o) for o in correct_answer.split(',') if o.strip()])
        
        if user_options == correct_options:
            is_correct = True
            result_text = f"完全正確！答案是 ${correct_answer}$。"
        else:
            result_text = f"答案不正確。正確答案應為：${correct_answer}$"
    else: # Type 3 problem: single numerical value
        try:
            # Handle float comparison with tolerance
            correct_float = float(correct_answer)
            user_float = float(user_answer)
            
            if math.isclose(user_float, correct_float, rel_tol=1e-6, abs_tol=1e-9):
                is_correct = True
                result_text = f"完全正確！答案是 ${correct_answer}$。"
            else:
                result_text = f"答案不正確。正確答案應為：${correct_answer}$"
        except ValueError:
            result_text = f"答案不正確，請輸入數字。正確答案應為：${correct_answer}$"
        except Exception:
            result_text = f"答案解析錯誤，請檢查您的輸入。正確答案應為：${correct_answer}$"

    return {"correct": is_correct, "result": result_text, "next_question": True}