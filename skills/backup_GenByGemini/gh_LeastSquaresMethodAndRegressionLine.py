import random
from fractions import Fraction
import re

# Helper function to format numbers as fractions or decimals for display
def format_number_as_string(num_obj, as_decimal_if_possible=False):
    """
    Formats a number (Fraction, float, int) into a string.
    If `as_decimal_if_possible` is True, it will attempt to represent
    terminating decimals as such (e.g., 0.5 instead of 1/2).
    Otherwise, it prefers fractions for Fraction objects.
    """
    if isinstance(num_obj, Fraction):
        if num_obj.denominator == 1:
            return str(num_obj.numerator)
        if as_decimal_if_possible:
            # Check if it's a terminating decimal (denominator is a power of 2, 5, or 10)
            temp_denom = num_obj.denominator
            while temp_denom % 2 == 0:
                temp_denom //= 2
            while temp_denom % 5 == 0:
                temp_denom //= 5
            if temp_denom == 1: # It's a terminating decimal
                return str(float(num_obj))
        return r"\\frac{{{}}}{{{}}}".format(num_obj.numerator, num_obj.denominator)
    elif isinstance(num_obj, float):
        if num_obj.is_integer():
            return str(int(num_obj))
        return str(num_obj)
    # Assume int
    return str(num_obj)

# Helper function for regression line coefficients (always formatted as fraction)
def format_coefficient(frac_obj):
    """
    Formats a Fraction object as a string, always preferring fraction form
    unless it's an integer. Used for coefficients in equations.
    """
    if frac_obj.denominator == 1:
        return str(frac_obj.numerator)
    else:
        return r"\\frac{{{}}}{{{}}}".format(frac_obj.numerator, frac_obj.denominator)

def parse_equation(eq_str):
    """
    Parses a regression line equation of the form y = mx + b or y = b
    into (slope, intercept) as Fraction objects.
    """
    eq_str = eq_str.replace(" ", "").lower().strip()
    
    # Handle y = b (horizontal line)
    match_b_only = re.match(r"y=(?P<b>[+-]?\d+(/\d+)?)", eq_str)
    if match_b_only:
        b_val = Fraction(match_b_only.group('b'))
        return Fraction(0), b_val # slope is 0

    # Handle y = mx + b or y = mx - b
    match_mx_plus_b = re.match(r"y=(?P<m>[+-]?(\d+(/\d+)?)?)x(?P<op>[+-])(?P<b>\d+(/\d+)?)", eq_str)
    if match_mx_plus_b:
        m_str = match_mx_plus_b.group('m')
        b_str = match_mx_plus_b.group('b')
        op = match_mx_plus_b.group('op')

        m_val = Fraction(1) if m_str == "" else (Fraction(-1) if m_str == "-" else Fraction(m_str))
        b_val = Fraction(b_str) if op == '+' else -Fraction(b_str)
        return m_val, b_val
    
    # Handle y = mx
    match_mx_only = re.match(r"y=(?P<m>[+-]?(\d+(/\d+)?)?)x", eq_str)
    if match_mx_only:
        m_str = match_mx_only.group('m')
        m_val = Fraction(1) if m_str == "" else (Fraction(-1) if m_str == "-" else Fraction(m_str))
        return m_val, Fraction(0)

    raise ValueError(f"Could not parse equation: {eq_str}")


def generate(level=1):
    """
    生成「最小平方法與迴歸直線」相關題目。
    """
    problem_type_choices = [
        'regression_line_from_stats',
        'correlation_from_point',
        'regression_line_from_data_table',
        'true_false_properties',
        'prediction_from_equation'
    ]
    problem_type = random.choice(problem_type_choices)

    if problem_type == 'regression_line_from_stats':
        return generate_regression_line_from_stats(level)
    elif problem_type == 'correlation_from_point':
        return generate_correlation_from_point(level)
    elif problem_type == 'regression_line_from_data_table':
        return generate_regression_line_from_data_table(level)
    elif problem_type == 'true_false_properties':
        return generate_true_false_properties(level)
    elif problem_type == 'prediction_from_equation':
        return generate_prediction_from_equation(level)

def generate_regression_line_from_stats(level):
    """
    題型: 已知 μx, μy, σx, σy, r，求迴歸直線方程式 y = ax + b。
    """
    mu_x = random.randint(-5, 5)
    mu_y = random.randint(-5, 5)
    sigma_x = random.randint(1, 4)
    sigma_y = random.randint(1, 4)

    # Use a wider range of r for higher levels
    r_options = [Fraction(val, 10) for val in range(-9, 10) if val != 0] # e.g. -0.9, -0.8, ..., 0.8, 0.9
    if level >= 2:
        # Include more complex fractions for r
        r_options.extend([Fraction(1, 3), Fraction(2, 3), Fraction(-1, 3), Fraction(-2, 3), 
                          Fraction(1, 4), Fraction(3, 4), Fraction(-1, 4), Fraction(-3, 4)])
        r_options = list(set(r_options)) # Remove duplicates

    r = random.choice(r_options)

    # Calculate slope m = r * (σy / σx)
    m = r * Fraction(sigma_y, sigma_x)

    # Calculate y-intercept b = μy - m * μx
    b = Fraction(mu_y) - m * Fraction(mu_x)

    # Format the equation y = mx + b
    m_str = format_coefficient(m)
    b_str = ""
    if b > 0:
        b_str = f" + {format_coefficient(b)}"
    elif b < 0:
        b_str = f" - {format_coefficient(abs(b))}"

    # Handle special cases for m
    if m == 0: # r = 0, so slope is 0
        equation_str = f"y = {format_coefficient(Fraction(mu_y))}"
    elif m == 1 and b == 0:
        equation_str = "y = x"
    elif m == -1 and b == 0:
        equation_str = "y = -x"
    elif m == 1:
        equation_str = f"y = x{b_str}"
    elif m == -1:
        equation_str = f"y = -x{b_str}"
    else:
        equation_str = f"y = {m_str}x{b_str}"

    r_display = format_number_as_string(r, as_decimal_if_possible=True)

    question_text = (
        f"已知兩變量$x$與$y$的平均數分別為 $\\mu_x={{{mu_x}}}$ 與 $\\mu_y={{{mu_y}}}$，"
        f"標準差分別為 $\\sigma_x={{{sigma_x}}}$ 與 $\\sigma_y={{{sigma_y}}}$，"
        f"且$x$與$y$的相關係數為 $r = {r_display}$，"
        f"求$y$對$x$的迴歸直線方程式。(請以 $y = ax+b$ 形式表示，係數為分數時請使用約分後的最簡分數)"
    )
    correct_answer = equation_str

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_correlation_from_point(level):
    """
    題型: 已知 μx, μy, σx, σy, 及迴歸直線上的一點 (x0, y0)，求相關係數 r。
    """
    mu_x = random.randint(-5, 5)
    mu_y = random.randint(-5, 5)
    sigma_x = random.randint(1, 4)
    sigma_y = random.randint(1, 4)

    r_options = [Fraction(val, 10) for val in range(-9, 10) if val != 0]
    if level >= 2:
        r_options.extend([Fraction(1, 3), Fraction(2, 3), Fraction(-1, 3), Fraction(-2, 3), 
                          Fraction(1, 4), Fraction(3, 4), Fraction(-1, 4), Fraction(-3, 4)])
        r_options = list(set(r_options))

    true_r = random.choice(r_options)

    # Calculate slope m = true_r * (σy / σx)
    m = true_r * Fraction(sigma_y, sigma_x)

    # Pick an x0, then calculate y0 on the line using y - μy = m(x - μx)
    x0 = mu_x + random.randint(-3, 3) # Keep x0 close to μx
    y0 = Fraction(mu_y) + m * (Fraction(x0) - Fraction(mu_x))

    y0_display = format_number_as_string(y0, as_decimal_if_possible=True)
    x0_display = str(x0)
    
    r_display = format_number_as_string(true_r, as_decimal_if_possible=True)

    question_text = (
        f"已知兩變量$x$與$y$的平均數分別為 $\\mu_x={{{mu_x}}}$ 與 $\\mu_y={{{mu_y}}}$，"
        f"標準差分別為 $\\sigma_x={{{sigma_x}}}$ 與 $\\sigma_y={{{sigma_y}}}$，"
        f"且點 $({{{x0_display}}}, {{{y0_display}}})$ 在$y$對$x$的迴歸直線上，"
        f"求$x$與$y$的相關係數 $r$。(請以約分後的最簡分數或小數表示)"
    )
    correct_answer = r_display

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def generate_regression_line_from_data_table(level):
    """
    題型: 給定數據點表格，求迴歸直線方程式。可選附帶預測。
    """
    num_points = 4 if level == 1 else 5 # 4 or 5 points

    x_base = random.randint(15, 30)
    y_base = random.randint(5, 15)

    x_deviations = []
    if num_points == 4:
        dev_magnitude = random.choice([1, 2, 3])
        x_deviations = sorted([-3 * dev_magnitude, -dev_magnitude, dev_magnitude, 3 * dev_magnitude])
    else: # num_points == 5
        dev_magnitude = random.choice([1, 2])
        x_deviations = sorted([-2 * dev_magnitude, -dev_magnitude, 0, dev_magnitude, 2 * dev_magnitude])

    # True slope and intercept for generating y_i
    m_true_options = [Fraction(1, 2), Fraction(2, 3), Fraction(3, 2), Fraction(-1, 2), Fraction(-2, 3), Fraction(-3, 2), Fraction(1), Fraction(-1)]
    m_true = random.choice(m_true_options)
    b_true_for_generation = Fraction(random.randint(-5, 5))

    x_coords = [x_base + dev for dev in x_deviations]
    y_coords = []
    
    # Generate y_coords with some integer noise for non-perfect correlation
    for x_val in x_coords:
        y_ideal = m_true * Fraction(x_val) + b_true_for_generation
        noise = random.randint(-1, 1) # Small integer noise
        y_coords.append(int(round(float(y_ideal + noise)))) # Ensure y_coords are integers

    # Calculate actual statistics from generated data (using Fractions for precision)
    mu_x_frac = Fraction(sum(x_coords), num_points)
    mu_y_frac = Fraction(sum(y_coords), num_points)

    sum_xy_minus_means = Fraction(0)
    sum_x_minus_mux_sq = Fraction(0)

    for i in range(num_points):
        x_diff = Fraction(x_coords[i]) - mu_x_frac
        y_diff = Fraction(y_coords[i]) - mu_y_frac
        sum_xy_minus_means += x_diff * y_diff
        sum_x_minus_mux_sq += x_diff * x_diff

    # Handle cases where all x values are the same (sum_x_minus_mux_sq = 0)
    if sum_x_minus_mux_sq == 0:
        # This implies all x_i are identical, retry generating data
        return generate_regression_line_from_data_table(level)

    # Calculate slope m
    m = sum_xy_minus_means / sum_x_minus_mux_sq

    # Calculate y-intercept b
    b = mu_y_frac - m * mu_x_frac

    # Format the equation y = mx + b
    m_str = format_coefficient(m)
    b_str = ""
    if b > 0:
        b_str = f" + {format_coefficient(b)}"
    elif b < 0:
        b_str = f" - {format_coefficient(abs(b))}"

    if m == 0:
        equation_str = f"y = {format_coefficient(b)}"
    elif m == 1 and b == 0:
        equation_str = "y = x"
    elif m == -1 and b == 0:
        equation_str = "y = -x"
    elif m == 1:
        equation_str = f"y = x{b_str}"
    elif m == -1:
        equation_str = f"y = -x{b_str}"
    else:
        equation_str = f"y = {m_str}x{b_str}"

    # Construct the table for the question
    x_coords_latex = [str(x) for x in x_coords]
    y_coords_latex = [str(y) for y in y_coords]
    
    table_rows = []
    table_rows.append("| " + " | ".join([f"$x$({i+1})" for i in range(num_points)]) + " |")
    table_rows.append("|" + " --- |" * num_points)
    table_rows.append("| " + " | ".join(x_coords_latex) + " |")
    table_rows.append("| " + " | ".join(y_coords_latex) + " |")
    table_str = "\n".join(table_rows)

    question_text = (
        f"已知兩變量$x$與$y$的數據如下表：<br>"
        f"{table_str}<br><br>"
        f"(1) 求$y$對$x$的迴歸直線方程式。(請以 $y = ax+b$ 形式表示，係數為分數時請使用約分後的最簡分數)"
    )
    correct_answer = equation_str

    # Optional: Add a prediction part for level 2
    if level >= 2 and random.random() < 0.7: # 70% chance to add prediction for level 2
        # Generate a value for x to predict
        if random.random() < 0.5: # Predict an existing x
            pred_x_val = random.choice(x_coords)
        else: # Predict a new x near the range
            # Generate a value near the mean of x, possibly slightly outside range
            min_x_val, max_x_val = min(x_coords), max(x_coords)
            range_x = max_x_val - min_x_val
            pred_x_val = random.randint(min_x_val - range_x // 4, max_x_val + range_x // 4)
            # Ensure it's not already in x_coords, unless by chance or limited options
            if pred_x_val in x_coords and len(set(x_coords)) == range_x + 1: # All ints in range are taken
                pred_x_val += random.choice([-1, 1]) # Slightly adjust if taken

        predicted_y = m * Fraction(pred_x_val) + b
        
        predicted_y_float = float(predicted_y)
        if predicted_y_float.is_integer():
            predicted_y_answer = str(int(predicted_y_float))
        else:
            predicted_y_answer = str(round(predicted_y_float, 1))

        question_text += (
            f"<br><br>"
            f"(2) 已知某次的$x$值為 ${{{pred_x_val}}}$，利用迴歸直線估計其對應的$y$值。"
            f"(答案請四捨五入到小數點以下第1位，如果答案為整數則直接填入整數)"
        )
        correct_answer = f"(1) {equation_str}\n(2) {predicted_y_answer}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_prediction_from_equation(level):
    """
    題型: 給定迴歸直線方程式和一個 x 值，求估計的 y 值。
    """
    # Generate a regression line equation parameters
    mu_x = random.randint(-5, 5)
    mu_y = random.randint(-5, 5)
    sigma_x = random.randint(1, 4)
    sigma_y = random.randint(1, 4)

    r_options = [Fraction(val, 10) for val in range(-9, 10) if val != 0]
    if level >= 2:
        r_options.extend([Fraction(1, 3), Fraction(2, 3), Fraction(-1, 3), Fraction(-2, 3), 
                          Fraction(1, 4), Fraction(3, 4), Fraction(-1, 4), Fraction(-3, 4)])
        r_options = list(set(r_options))

    r = random.choice(r_options)
    m = r * Fraction(sigma_y, sigma_x)
    b_val = Fraction(mu_y) - m * Fraction(mu_x)

    # Format the equation string for display
    m_str = format_coefficient(m)
    b_str = ""
    if b_val > 0:
        b_str = f" + {format_coefficient(b_val)}"
    elif b_val < 0:
        b_str = f" - {format_coefficient(abs(b_val))}"

    if m == 0:
        equation_str = f"y = {format_coefficient(b_val)}"
    elif m == 1 and b_val == 0:
        equation_str = "y = x"
    elif m == -1 and b_val == 0:
        equation_str = "y = -x"
    elif m == 1:
        equation_str = f"y = x{b_str}"
    elif m == -1:
        equation_str = f"y = -x{b_str}"
    else:
        equation_str = f"y = {m_str}x{b_str}"

    # Generate a value for x to predict
    pred_x = random.randint(mu_x - 5, mu_x + 5)
    
    predicted_y = m * Fraction(pred_x) + b_val

    predicted_y_float = float(predicted_y)
    if predicted_y_float.is_integer():
        predicted_y_answer = str(int(predicted_y_float))
    else:
        predicted_y_answer = str(round(predicted_y_float, 1))

    question_text = (
        f"已知$y$對$x$的迴歸直線方程式為 $y = {equation_str}$。"
        f"若某次的$x$值為 ${{{pred_x}}}$，利用迴歸直線估計其對應的$y$值。"
        f"(答案請四捨五入到小數點以下第1位，如果答案為整數則直接填入整數)"
    )
    correct_answer = predicted_y_answer

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def generate_true_false_properties(level):
    """
    題型: 判斷關於相關係數和迴歸直線性質的敘述是否正確。
    """
    statements = [
        # (Statement, Correct Answer)
        (r"散布圖上的點愈多，其相關程度愈高。", "X"),
        (r"若$x$與$y$的相關係數$r > 0$，則$y$對$x$的迴歸直線的斜率$m > 0$。", "O"), # Assumes sigma_x, sigma_y > 0
        (r"若$x$與$y$的標準差相等，則其相關係數與$y$對$x$迴歸直線的斜率也相等。", "O"), # m = r * (sigma_y / sigma_x). If sigma_x = sigma_y, then m = r.
        (r"相關係數$r$滿足$-1 \le r \le 1$。", "O"),
        (r"若散布圖的所有點都在直線 $y=2x-1$ 上，則相關係數為1。", "O"), # Positive slope means r=1
        (r"迴歸直線一定會通過資料點的平均點 $(\\mu_x, \\mu_y)$。", "O"),
        (r"相關係數為0表示兩個變量之間沒有任何關係。", "X"), # Only implies no *linear* relationship
        (r"迴歸直線的斜率 $m = r \\frac{{\\sigma_y}}{{\\sigma_x}}$。", "O"),
        (r"若$x$與$y$的相關係數 $r=0$，則迴歸直線為水平線 $y = \\mu_y$。", "O"),
        (r"若將所有$x$資料點乘以一個正數 $c$，則相關係數 $r$ 會改變。", "X") # r is scale invariant (for positive scale)
    ]

    statement, correct_ans = random.choice(statements)
    question_text = f"判斷下列敘述是否正確。(請填入「O」或「X」)<br>□ {statement}"
    
    return {
        "question_text": question_text,
        "answer": correct_ans,
        "correct_answer": correct_ans
    }

def check(user_answer, correct_answer):
    """
    檢查使用者答案是否正確。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()

    is_correct = False
    feedback = ""

    # Check for multi-part answers (e.g., from generate_regression_line_from_data_table)
    if "\n" in correct_answer and "\n" in user_answer:
        correct_parts = correct_answer.split('\n')
        user_parts = user_answer.split('\n')
        
        if len(correct_parts) == len(user_parts):
            all_parts_correct = True
            part_feedback = []
            for i in range(len(correct_parts)):
                cp = correct_parts[i].strip()
                up = user_parts[i].strip()
                
                # Check for (1) Ans, (2) Ans format
                if cp.startswith(f"({i+1}) ") and up.startswith(f"({i+1}) "):
                    cp_val = cp[len(f"({i+1}) "):].strip()
                    up_val = up[len(f"({i+1}) "):].strip()
                else: # Assume direct answer if no (1) (2) prefix, e.g. "Ans" not "(1) Ans"
                    cp_val = cp
                    up_val = up

                if _compare_individual_answer(up_val, cp_val):
                    part_feedback.append(f"第({i+1})題正確。")
                else:
                    all_parts_correct = False
                    part_feedback.append(f"第({i+1})題不正確，正確答案應為 ${cp_val}$。")
            
            is_correct = all_parts_correct
            feedback = "<br>".join(part_feedback)
            if all_parts_correct:
                feedback = "所有部分都正確！" + feedback
        else:
            feedback = "答案格式不正確，請提供所有部分的答案。"
            
    else: # Single part answer
        if _compare_individual_answer(user_answer, correct_answer):
            is_correct = True
            feedback = f"完全正確！答案是 ${correct_answer}$。"
        else:
            feedback = f"答案不正確。正確答案應為：${correct_answer}$"

    return {"correct": is_correct, "result": feedback, "next_question": True}

def _compare_individual_answer(user_ans_str, correct_ans_str):
    """
    Helper function to compare a single user answer string with a correct answer string.
    Handles fractions, floats (with rounding tolerance), equations, and O/X.
    """
    user_ans_str = user_ans_str.replace(" ", "").replace("$", "")
    correct_ans_str = correct_ans_str.replace(" ", "").replace("$", "")

    # Handle True/False (O/X)
    if user_ans_str.upper() in ["O", "X"] and correct_ans_str.upper() in ["O", "X"]:
        return user_ans_str.upper() == correct_ans_str.upper()

    # Try comparing as fractions first for precision
    try:
        user_frac = Fraction(user_ans_str)
        correct_frac = Fraction(correct_ans_str)
        if user_frac == correct_frac:
            return True
    except ValueError:
        pass # Not a simple fraction

    # Try comparing as floats for decimals, especially with rounding (e.g., to 1 decimal place)
    try:
        user_float = float(user_ans_str)
        correct_float = float(correct_ans_str)
        # Allow for small floating point errors, or exact match for given rounding (e.g., 0.05 for 1 decimal place)
        return abs(user_float - correct_float) < 0.05
    except ValueError:
        pass # Not a float

    # Try to parse as equations (y = mx + b)
    if "y=" in user_ans_str.lower() or "y=" in correct_ans_str.lower():
        try:
            user_m, user_b = parse_equation(user_ans_str)
            correct_m, correct_b = parse_equation(correct_ans_str)
            if user_m == correct_m and user_b == correct_b:
                return True
        except ValueError: # Catch any parsing errors for equations
            pass

    # Final fallback: direct string comparison (case-insensitive for some parts)
    return user_ans_str == correct_ans_str