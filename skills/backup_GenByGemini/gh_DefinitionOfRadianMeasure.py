import random
import math
from fractions import Fraction

# Constants for LaTeX display and calculations
PI_STR_LATEX = r"\\pi" # For displaying pi in LaTeX math mode
PI_VAL = math.pi      # For numerical calculations

def generate(level=1):
    """
    生成「弧度定義與單位換算」相關題目。
    包含：
    1. 弧度與度的近似轉換 (多選一)
    2. 度數轉換為弧度 (分數形式)
    3. 弧度轉換為度數 (整數或小數)
    4. 廣義角與同界角 (多選)
    """
    problem_type = random.choice([
        'approx_rad_to_deg',  # 給弧度，選最接近的度數
        'approx_deg_to_rad',  # 給度數，選最接近的弧度
        'deg_to_rad_exact',   # 度數轉弧度 (精確分數形式)
        'rad_to_deg_frac_pi', # 弧度 (pi分數) 轉度數 (精確整數)
        'rad_to_deg_naked_rad', # 弧度 (裸值) 轉度數 (近似小數)
        'coterminal_radians', # 尋找弧度制的同界角
        'coterminal_degrees'  # 尋找度數制的同界角
    ])

    if problem_type == 'approx_rad_to_deg':
        return _generate_approx_rad_to_deg_problem(level)
    elif problem_type == 'approx_deg_to_rad':
        return _generate_approx_deg_to_rad_problem(level)
    elif problem_type == 'deg_to_rad_exact':
        return _generate_deg_to_rad_problem(level)
    elif problem_type == 'rad_to_deg_frac_pi':
        return _generate_rad_to_deg_problem(level, type='fraction_pi')
    elif problem_type == 'rad_to_deg_naked_rad':
        return _generate_rad_to_deg_problem(level, type='naked_rad')
    elif problem_type == 'coterminal_radians':
        return _generate_coterminal_angles_problem(level, unit='radians')
    elif problem_type == 'coterminal_degrees':
        return _generate_coterminal_angles_problem(level, unit='degrees')

def _generate_approx_rad_to_deg_problem(level):
    """生成弧度轉度數的近似選擇題。"""
    radian_val = random.uniform(1.5, 6.5)
    if level <= 2:
        radian_val = round(radian_val)  # 2, 3, 4 rad
    else:
        radian_val = round(radian_val * 2) / 2 # 2.0, 2.5, 3.0 rad

    correct_degree_val = radian_val * (180 / PI_VAL)
    
    options = []
    options.append(int(round(correct_degree_val))) # Correct option, rounded to nearest integer

    distractor_range = 10 if level == 1 else 5
    while len(options) < 5: # Generate 4 distractors
        offset = random.choice([-2, -1, 1, 2]) * random.randint(distractor_range // 2, distractor_range)
        distractor = int(round(correct_degree_val + offset))
        # Ensure distractors are not too close, within 0-360 range, and distinct
        if all(abs(distractor - opt) > 5 for opt in options) and 0 <= distractor <= 360:
            options.append(distractor)
    random.shuffle(options)

    correct_idx = -1
    for i, opt_val in enumerate(options):
        # Find the index of the closest option, allowing for floating point differences
        if abs(opt_val - correct_degree_val) < 0.01:
            correct_idx = i
            break
    
    option_letters = ['(1)', '(2)', '(3)', '(4)', '(5)']
    option_strings = [f"{option_letters[i]} ${opt}^{{r\\circ}}$" for i, opt in enumerate(options)]
    
    question_text = (
        f"下列哪一個角度最接近 ${radian_val}$ 弳？\n" +
        " ".join(option_strings)
    )
    
    # Payload for check function
    correct_answer_payload = (
        f"TYPE:APPROX_MCQ_RAD_TO_DEG|"
        f"CORRECT_OPTION:{correct_idx + 1}|"
        f"CORRECT_DEG_VALUE:{correct_degree_val:.2f}"
    )
    
    return {
        "question_text": question_text,
        "answer": str(correct_idx + 1), # The expected user answer (option number)
        "correct_answer": correct_answer_payload # Full payload for check
    }

def _generate_approx_deg_to_rad_problem(level):
    """生成度數轉弧度的近似選擇題。"""
    degree_val = random.randint(30, 330)
    if level <= 2:
        degree_val = round(degree_val / 30) * 30 # Multiples of 30
    else:
        degree_val = round(degree_val / 15) * 15 # Multiples of 15

    correct_radian_val = degree_val * (PI_VAL / 180)

    options_rad_val = []
    options_rad_val.append(correct_radian_val)

    distractor_range_rad = 0.5 if level == 1 else 0.2
    while len(options_rad_val) < 5:
        offset = random.choice([-1, 1]) * random.uniform(distractor_range_rad / 2, distractor_range_rad)
        distractor = correct_radian_val + offset
        # Ensure distractors are not too close and are positive
        if all(abs(distractor - opt) > 0.1 for opt in options_rad_val) and distractor > 0:
            options_rad_val.append(distractor)
    random.shuffle(options_rad_val)
    
    formatted_options = [f"${val:.2f}$ 弳" for val in options_rad_val] # Display with 2 decimal places
    
    correct_idx = -1
    for i, opt_val in enumerate(options_rad_val):
        if abs(opt_val - correct_radian_val) < 0.01:
            correct_idx = i
            break

    option_letters = ['(1)', '(2)', '(3)', '(4)', '(5)']
    display_option_strings = [f"{option_letters[i]} {formatted_options[i]}" for i in range(len(formatted_options))]

    question_text = (
        f"下列哪一個弧度最接近 ${degree_val}^{{r\\circ}}$？\n" +
        " ".join(display_option_strings)
    )
    
    correct_answer_payload = (
        f"TYPE:APPROX_MCQ_DEG_TO_RAD|"
        f"CORRECT_OPTION:{correct_idx + 1}|"
        f"CORRECT_RAD_VALUE:{correct_radian_val:.2f}"
    )
    
    return {
        "question_text": question_text,
        "answer": str(correct_idx + 1),
        "correct_answer": correct_answer_payload
    }

def _get_fraction_rad_display(num, den):
    """Helper to format fractions of pi for LaTeX display."""
    if num == 0:
        return f"$0$"
    if den == 1:
        if num == 1: return f"${PI_STR_LATEX}$"
        if num == -1: return f"$-{PI_STR_LATEX}$"
        return f"${num}{PI_STR_LATEX}$"
    if num == 1:
        return f"$\\frac{{{PI_STR_LATEX}}}{{{den}}}$"
    if num == -1:
        return f"$-\\frac{{{PI_STR_LATEX}}}{{{den}}}$"
    return f"$\\frac{{{num}{PI_STR_LATEX}}}{{{den}}}$"

def _generate_deg_to_rad_problem(level):
    """生成度數轉換為弧度 (精確分數形式) 的題目。"""
    degree_val = random.randint(-1800, 1800) # Allow large/negative angles
    
    # Ensure it's a multiple of a base angle for common fractions
    base_angles = [15, 30, 45, 60, 90]
    if level >= 2:
        base_angles.extend([10, 20])
    degree_val = round(degree_val / random.choice(base_angles)) * random.choice(base_angles)
    
    fraction_val = Fraction(degree_val, 180).limit_denominator(200)
    num_pi = fraction_val.numerator
    den = fraction_val.denominator
    
    display_question_angle = _get_fraction_rad_display(num_pi, den)
    
    question_text = f"試問 ${degree_val}^{{r\\circ}}$ 為多少弳？"
    
    # Store "num/den" string for accurate checking
    correct_fraction_str = f"{num_pi}/{den}"
    if num_pi == 0: correct_fraction_str = "0"
    
    correct_answer_payload = (
        f"TYPE:DEG_TO_RAD_EXACT|"
        f"CORRECT_FRACTION_STR:{correct_fraction_str}"
    )
    
    return {
        "question_text": question_text,
        "answer": f"{num_pi}/{den}", # A representative answer for internal storage
        "correct_answer": correct_answer_payload
    }

def _generate_rad_to_deg_problem(level, type):
    """生成弧度轉換為度數的題目 (精確整數或近似小數)。"""
    if type == 'fraction_pi':
        possible_denominators = [2, 3, 4, 6]
        if level >= 2:
            possible_denominators.extend([5, 8, 9, 10, 12, 15, 18, 20])
        
        den = random.choice(possible_denominators)
        num = random.randint(-2 * den, 2 * den)
        
        fraction_val = Fraction(num, den)
        num = fraction_val.numerator
        den = fraction_val.denominator
        
        radian_display = _get_fraction_rad_display(num, den)
        correct_degree = fraction_val * 180
        
        question_text = f"試問 {radian_display} 弳為多少度？"
        correct_answer_payload = (
            f"TYPE:RAD_TO_DEG_EXACT|"
            f"CORRECT_DEGREE:{int(correct_degree)}"
        )
        return {
            "question_text": question_text,
            "answer": str(int(correct_degree)),
            "correct_answer": correct_answer_payload
        }
    else: # type == 'naked_rad'
        radian_val = random.uniform(0.5, 6.5)
        if level <= 2:
            radian_val = random.randint(1, 6)
        else:
            radian_val = round(radian_val * 2) / 2
        
        radian_display = f"${radian_val}$ 弳"
        correct_degree = radian_val * (180 / PI_VAL)
        
        question_text = f"試問 {radian_display} 為多少度？"
        correct_answer_payload = (
            f"TYPE:RAD_TO_DEG_APPROX|"
            f"CORRECT_DEGREE_APPROX:{correct_degree:.2f}"
        )
        return {
            "question_text": question_text,
            "answer": f"{correct_degree:.2f}",
            "correct_answer": correct_answer_payload
        }

def _generate_coterminal_angles_problem(level, unit='radians'):
    """生成同界角的題目，可選弧度或度數制。"""
    num_options = 4
    option_labels = ['(1)', '(2)', '(3)', '(4)']
    
    if unit == 'radians':
        den = random.choice([2, 3, 4, 6])
        if level >= 2:
            den = random.choice([2, 3, 4, 5, 6, 8, 10, 12])
        num = random.randint(1, den * 3 // 2)
        base_angle_frac = Fraction(num, den)
        
        base_angle_display = _get_fraction_rad_display(base_angle_frac.numerator, base_angle_frac.denominator)
        
        options_frac = []
        is_coterminal = []
        
        num_correct = random.choice([1, 2])
        for _ in range(num_correct):
            k = random.choice([-2, -1, 1, 2]) # Add/subtract 2*pi multiples
            coterminal_frac = base_angle_frac + Fraction(2 * k, 1)
            coterminal_frac = coterminal_frac.limit_denominator(20) # Simplify fraction
            if coterminal_frac not in options_frac: # Ensure options are unique
                options_frac.append(coterminal_frac)
                is_coterminal.append(True)
            else:
                _ -= 1 # Try generating another correct option if duplicate
        
        while len(options_frac) < num_options:
            distractor_type = random.choice(['non_coterminal_pi_multiple', 'non_coterminal_offset'])
            
            if distractor_type == 'non_coterminal_pi_multiple': # e.g., base + pi or base + 3pi
                k_odd = random.choice([-1, 1, 3])
                distractor_frac = base_angle_frac + Fraction(k_odd, 1)
                distractor_frac = distractor_frac.limit_denominator(20)
                if distractor_frac not in options_frac and distractor_frac != base_angle_frac:
                    options_frac.append(distractor_frac)
                    is_coterminal.append(False)
            else: # Random, unrelated angle
                new_den = random.choice([2, 3, 4, 6])
                new_num = random.randint(-new_den * 2, new_den * 2)
                random_frac = Fraction(new_num, new_den).limit_denominator(20)
                if random_frac not in options_frac and random_frac != base_angle_frac:
                    options_frac.append(random_frac)
                    is_coterminal.append(False)
        
        combined = list(zip(options_frac, is_coterminal))
        random.shuffle(combined)
        options_frac, is_coterminal = zip(*combined)
        
        display_options = []
        correct_option_indices = []
        for i, (opt_frac, is_cot) in enumerate(zip(options_frac, is_coterminal)):
            display_options.append(f"{option_labels[i]} {_get_fraction_rad_display(opt_frac.numerator, opt_frac.denominator)}")
            if is_cot:
                correct_option_indices.append(str(i + 1))
        
        question_text = f"選出所有 {base_angle_display} 弳的同界角。\n" + " ".join(display_options)
        
        correct_answer_payload = (
            f"TYPE:COTERMINAL_MCQ|"
            f"UNIT:RADIANS|"
            f"BASE_ANGLE_DISPLAY:{base_angle_display}|"
            f"CORRECT_OPTIONS:{','.join(sorted(correct_option_indices))}"
        )

    else: # unit == 'degrees'
        base_angle_deg = random.randint(-1000, 1000)
        base_angle_deg = round(base_angle_deg / 15) * 15 # Make it a multiple of 15
        
        base_angle_display = f"${base_angle_deg}^{{r\\circ}}$"
        
        options_deg = []
        is_coterminal = []
        
        num_correct = random.choice([1, 2])
        for _ in range(num_correct):
            k = random.choice([-2, -1, 1, 2]) # Add/subtract 360 multiples
            coterminal_deg = base_angle_deg + 360 * k
            if coterminal_deg not in options_deg: # Ensure uniqueness
                options_deg.append(coterminal_deg)
                is_coterminal.append(True)
            else:
                _ -= 1
        
        while len(options_deg) < num_options:
            distractor_type = random.choice(['non_coterminal_half_rot', 'non_coterminal_offset'])
            
            if distractor_type == 'non_coterminal_half_rot': # e.g., base + 180 + 360k
                k_half = random.choice([-1, 0, 1])
                distractor_deg = base_angle_deg + 180 + 360 * k_half
                if distractor_deg not in options_deg:
                    options_deg.append(distractor_deg)
                    is_coterminal.append(False)
            else: # Random, unrelated angle
                random_deg = random.randint(-1500, 1500)
                random_deg = round(random_deg / 15) * 15
                if random_deg not in options_deg and random_deg % 360 != base_angle_deg % 360:
                    options_deg.append(random_deg)
                    is_coterminal.append(False)
        
        combined = list(zip(options_deg, is_coterminal))
        random.shuffle(combined)
        options_deg, is_coterminal = zip(*combined)
        
        display_options = []
        correct_option_indices = []
        for i, (opt_deg, is_cot) in enumerate(zip(options_deg, is_coterminal)):
            display_options.append(f"{option_labels[i]} ${opt_deg}^{{r\\circ}}$")
            if is_cot:
                correct_option_indices.append(str(i + 1))
        
        question_text = f"選出所有 {base_angle_display} 的同界角。\n" + " ".join(display_options)
        
        correct_answer_payload = (
            f"TYPE:COTERMINAL_MCQ|"
            f"UNIT:DEGREES|"
            f"BASE_ANGLE_DISPLAY:{base_angle_display}|"
            f"CORRECT_OPTIONS:{','.join(sorted(correct_option_indices))}"
        )
        
    return {
        "question_text": question_text,
        "answer": correct_answer_payload, # Internal storage
        "correct_answer": correct_answer_payload # Full payload for check
    }

def _parse_payload(payload_str):
    """Helper to parse the string-based payload back into a dictionary."""
    parts = payload_str.split('|')
    payload_dict = {}
    for part in parts:
        if ':' in part:
            key, value = part.split(':', 1)
            payload_dict[key.strip()] = value.strip()
    return payload_dict

def _format_fraction_for_feedback_display(fraction_str_num_den, pi_sym):
    """Helper to format a fraction string (e.g., "1/3") into LaTeX for feedback."""
    if fraction_str_num_den == "0":
        return "$0$"
    try:
        f = Fraction(fraction_str_num_den)
        if f.denominator == 1:
            if f.numerator == 1: return f"${pi_sym}$"
            if f.numerator == -1: return f"$-{pi_sym}$"
            return f"${f.numerator}{pi_sym}$"
        if f.numerator == 1:
            return f"$\\frac{{{pi_sym}}}{{{f.denominator}}}$"
        if f.numerator == -1:
            return f"$-\\frac{{{pi_sym}}}{{{f.denominator}}}$"
        return f"$\\frac{{{f.numerator}{pi_sym}}}{{{f.denominator}}}$"
    except (ValueError, ZeroDivisionError):
        return f"${fraction_str_num_den}$" # Fallback if not a parsable fraction string

def check(user_answer, correct_answer_payload):
    """
    檢查使用者答案是否正確。
    correct_answer_payload 是由 generate 函數生成的字符串，包含所有檢查所需的資訊。
    """
    user_ans = user_answer.strip().lower()
    payload = _parse_payload(correct_answer_payload)
    
    problem_type = payload.get('TYPE')
    is_correct = False
    result_text = ""
    
    # --- 1. 弧度與度的近似轉換 (多選一) ---
    if problem_type == 'APPROX_MCQ_RAD_TO_DEG':
        correct_option = payload.get('CORRECT_OPTION')
        correct_deg_value = payload.get('CORRECT_DEG_VALUE')
        if user_ans == correct_option:
            is_correct = True
            result_text = f"完全正確！答案是選項 {correct_option}。"
        else:
            result_text = f"答案不正確。正確答案應為選項 {correct_option}（約 ${correct_deg_value}^{{r\\circ}}$）。"
    
    elif problem_type == 'APPROX_MCQ_DEG_TO_RAD':
        correct_option = payload.get('CORRECT_OPTION')
        correct_rad_value = payload.get('CORRECT_RAD_VALUE')
        if user_ans == correct_option:
            is_correct = True
            result_text = f"完全正確！答案是選項 {correct_option}。"
        else:
            result_text = f"答案不正確。正確答案應為選項 {correct_option}（約 ${correct_rad_value}$ 弳）。"

    # --- 2. 度數轉換為弧度 (分數形式) ---
    elif problem_type == 'DEG_TO_RAD_EXACT':
        correct_fraction_str = payload.get('CORRECT_FRACTION_STR')
        
        # Normalize user input (remove "pi", "\\pi", spaces for fraction parsing)
        user_ans_normalized = user_ans.replace('pi', '').replace(r'\\pi', '').replace(' ', '')
        if user_ans_normalized == "": user_ans_normalized = "1" # "pi" implies "1/1"
        
        try:
            user_frac = Fraction(user_ans_normalized) if '/' in user_ans_normalized else Fraction(int(user_ans_normalized), 1)
            correct_frac = Fraction(correct_fraction_str) if '/' in correct_fraction_str else Fraction(int(correct_fraction_str), 1)
            
            if user_frac == correct_frac:
                is_correct = True
                result_text = f"完全正確！答案是 {_format_fraction_for_feedback_display(correct_fraction_str, PI_STR_LATEX)} 弳。"
            else:
                result_text = f"答案不正確。正確答案應為 {_format_fraction_for_feedback_display(correct_fraction_str, PI_STR_LATEX)} 弳。"
        except (ValueError, ZeroDivisionError):
            result_text = f"輸入格式不正確或答案不符。正確答案應為 {_format_fraction_for_feedback_display(correct_fraction_str, PI_STR_LATEX)} 弳。"
            
    # --- 3. 弧度轉換為度數 (精確整數或近似小數) ---
    elif problem_type == 'RAD_TO_DEG_EXACT':
        correct_degree = payload.get('CORRECT_DEGREE')
        try:
            if int(user_ans) == int(correct_degree):
                is_correct = True
                result_text = f"完全正確！答案是 ${correct_degree}^{{r\\circ}}$。"
            else:
                result_text = f"答案不正確。正確答案應為 ${correct_degree}^{{r\\circ}}$。"
        except ValueError:
            result_text = f"輸入格式不正確。正確答案應為 ${correct_degree}^{{r\\circ}}$。"

    elif problem_type == 'RAD_TO_DEG_APPROX':
        correct_degree_approx = payload.get('CORRECT_DEGREE_APPROX')
        try:
            # Compare floats with a small tolerance
            if abs(float(user_ans) - float(correct_degree_approx)) < 0.01:
                is_correct = True
                result_text = f"完全正確！答案是約 ${correct_degree_approx}^{{r\\circ}}$。"
            else:
                result_text = f"答案不正確。正確答案應為約 ${correct_degree_approx}^{{r\\circ}}$。"
        except ValueError:
            result_text = f"輸入格式不正確。正確答案應為約 ${correct_degree_approx}^{{r\\circ}}$。"

    # --- 4. 廣義角與同界角 (多選) ---
    elif problem_type == 'COTERMINAL_MCQ':
        correct_options_str = payload.get('CORRECT_OPTIONS')
        base_angle_display = payload.get('BASE_ANGLE_DISPLAY')
        
        # Parse user's comma-separated answer into a set
        user_options = set(x.strip() for x in user_ans.split(',') if x.strip())
        correct_options = set(x.strip() for x in correct_options_str.split(',') if x.strip())
        
        if user_options == correct_options:
            is_correct = True
            result_text = f"完全正確！所有 {base_angle_display} 的同界角選項為：{correct_options_str}。"
        else:
            result_text = f"答案不正確。所有 {base_angle_display} 的同界角選項應為：{correct_options_str}。"
            
    return {"correct": is_correct, "result": result_text, "next_question": True}