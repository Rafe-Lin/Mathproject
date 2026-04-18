import random
from fractions import Fraction

# --- Helper Functions ---

def _format_number(num):
    """
    Formats a number (int, float, Fraction) into a LaTeX-compatible string.
    Handles integers, decimals, and mixed fractions.
    """
    if isinstance(num, Fraction):
        if num.denominator == 1:
            return str(num.numerator)
        
        sign = "-" if num < 0 else ""
        num_abs = abs(num)
        
        if num_abs.numerator > num_abs.denominator:
            whole_part = num_abs.numerator // num_abs.denominator
            frac_part = num_abs - whole_part
            
            # Safe f-string formatting for LaTeX
            fp_num_str = f"{frac_part.numerator}"
            fp_den_str = f"{frac_part.denominator}"
            return f"{sign}{whole_part} \\frac{{{fp_num_str}}}{{{fp_den_str}}}"
        else:
            # Safe f-string formatting for LaTeX
            num_str = f"{num_abs.numerator}"
            den_str = f"{num_abs.denominator}"
            return f"{sign}\\frac{{{num_str}}}{{{den_str}}}"
            
    elif isinstance(num, float):
        # Avoid unnecessary .0 for integers represented as floats
        return str(int(num)) if num.is_integer() else str(num)
        
    return str(num)

def _get_location(x, y):
    """Determines the quadrant or axis of a point (x, y)."""
    if x > 0 and y > 0: return "第一象限"
    if x < 0 and y > 0: return "第二象限"
    if x < 0 and y < 0: return "第三象限"
    if x > 0 and y < 0: return "第四象限"
    if x == 0 and y != 0: return "y 軸"
    if x != 0 and y == 0: return "x 軸"
    if x == 0 and y == 0: return "原點"
    return "未知"

def _generate_random_coord(allow_zero=False):
    """
    Generates a random coordinate value (int, float, or Fraction).
    Ensures non-zero value if allow_zero is False.
    """
    val = 0
    # Loop until a valid value is generated based on allow_zero
    while val == 0 and not allow_zero:
        rand_type = random.choice(['int', 'frac', 'float'])
        if rand_type == 'int':
            val = random.randint(-10, 10)
        elif rand_type == 'float':
            val = round(random.uniform(-10.0, 10.0), 1)
        else: # frac
            den = random.randint(2, 9)
            num = random.randint(-15, 15)
            # Avoid creating a whole number unintentionally
            if num != 0 and num % den == 0:
                num += random.choice([-1, 1])
            val = Fraction(num, den)
            
    return val

# --- Main Generator Function ---

def generate(level=1):
    """
    生成「坐標平面象限」相關題目。
    包含：
    1. 直接判別：給定數字座標，判斷所在象限或坐標軸。
    2. 抽象判別：給定變數座標的象限，判斷衍生點的象限。
    """
    # Randomly select one of the two problem types
    problem_type = random.choice(['direct_identification', 'abstract_identification'])
    
    if problem_type == 'direct_identification':
        return generate_direct_identification_problem()
    else: # abstract_identification
        return generate_abstract_identification_problem()

# --- Problem Type Generators ---

def generate_direct_identification_problem():
    """
    題型：判別 A(x, y) 的象限或所在坐標軸。
    """
    point_label = random.choice(['A', 'B', 'C', 'P', 'Q'])
    
    # 25% chance of the point being on an axis
    on_axis = random.random() < 0.25
    
    if on_axis:
        if random.choice([True, False]): # x-axis
            x = _generate_random_coord(allow_zero=False)
            y = 0
        else: # y-axis
            x = 0
            y = _generate_random_coord(allow_zero=False)
    else: # In a quadrant
        x = _generate_random_coord(allow_zero=False)
        y = _generate_random_coord(allow_zero=False)
        
    x_str = _format_number(x)
    y_str = _format_number(y)
    
    correct_answer = _get_location(x, y)
    
    # [教學示範] 正確使用 f-string 與 LaTeX 座標表示法
    question_text = f"請問點 ${point_label}({x_str}, {y_str})$ 在哪一象限內或哪一坐標軸上？"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_abstract_identification_problem():
    """
    題型：已知 P(a,b) 在某象限，判斷 Q(f(a,b), g(a,b)) 的象限。
    """
    quadrants = {
        1: ("第一象限", 1, 1),
        2: ("第二象限", -1, 1),
        3: ("第三象限", -1, -1),
        4: ("第四象限", 1, -1),
    }
    start_quadrant_num = random.randint(1, 4)
    start_quadrant_name, a_sign, b_sign = quadrants[start_quadrant_num]

    # Pool of transformations for the new point's coordinates
    # Each tuple is (display_string, sign_function)
    trans_pool = [
        ('a', lambda sa, sb: sa),
        ('-a', lambda sa, sb: -sa),
        ('b', lambda sa, sb: sb),
        ('-b', lambda sa, sb: -sb),
        ('|a|', lambda sa, sb: 1),
        ('|b|', lambda sa, sb: 1),
        ('ab', lambda sa, sb: sa * sb),
        ('\\frac{{a}}{{b}}', lambda sa, sb: sa * sb), # sign of a/b is same as a*b
        ('a^{{2}}', lambda sa, sb: 1), # a^2 is always positive
        ('b^{{2}}', lambda sa, sb: 1),
        ('-a^{{2}}', lambda sa, sb: -1),
        ('-b^{{2}}', lambda sa, sb: -1)
    ]
    
    # Select transformations for x and y, ensuring it's not the trivial P(a,b) case
    x_trans_display, x_trans_func = random.choice(trans_pool)
    y_trans_display, y_trans_func = random.choice(trans_pool)
    while x_trans_display == 'a' and y_trans_display == 'b':
        x_trans_display, x_trans_func = random.choice(trans_pool)
        y_trans_display, y_trans_func = random.choice(trans_pool)

    new_x_sign = x_trans_func(a_sign, b_sign)
    new_y_sign = y_trans_func(a_sign, b_sign)
    
    # A dummy point with the correct signs to use the location helper
    correct_answer = _get_location(new_x_sign, new_y_sign)

    # [教學示範] 使用變數建構複雜的 LaTeX 字串
    question_text = f"已知點 $P(a, b)$ 在{start_quadrant_name}，則點 $Q({x_trans_display}, {y_trans_display})$ 在哪一象限內？"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

# --- Checker Function ---

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    接受多種輸入格式，例如「一」、「1」、「第一象限」都會被視為相同答案。
    """
    user_ans = user_answer.strip().replace(" ", "")
    correct_ans = correct_answer.strip()
    
    # Shorthand mapping for user-friendliness
    shorthands = {
        '1': '第一象限', '一': '第一象限',
        '2': '第二象限', '二': '第二象限',
        '3': '第三象限', '三': '第三象限',
        '4': '第四象限', '四': '第四象限',
        'x': 'x軸', 'X': 'x軸',
        'y': 'y軸', 'Y': 'y軸',
        '原點': '原點', '0': '原點'
    }
    
    # Normalize user answer if it's a known shorthand
    normalized_user_answer = shorthands.get(user_ans, user_ans)

    # Normalize correct answer to match shorthand targets (e.g., "x 軸" -> "x軸")
    normalized_correct_answer = correct_ans.replace(" ", "")
    
    is_correct = (normalized_user_answer == normalized_correct_answer)
    
    # [教學示範] 回傳結果不使用 LaTeX，因為答案是中文
    result_text = f"完全正確！答案是 {correct_ans}。" if is_correct else f"答案不正確。正確答案應為：${correct_ans}。"
    
    return {"correct": is_correct, "result": result_text, "next_question": True}