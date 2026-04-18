import random
import math
from fractions import Fraction

# Map angles (in degrees) to their slopes (as display string and numeric value)
# Using raw strings for LaTeX.
_ANGLE_INFO = {
    0: {'slope_display': '0', 'slope_numeric': 0.0},
    30: {'slope_display': r'\\frac{{\\sqrt{{3}}}}{{3}}', 'slope_numeric': math.sqrt(3)/3},
    45: {'slope_display': '1', 'slope_numeric': 1.0},
    60: {'slope_display': r'\\sqrt{{3}}', 'slope_numeric': math.sqrt(3)},
    90: {'slope_display': 'undefined', 'slope_numeric': float('inf')}, # Represents vertical line
    120: {'slope_display': r'-\\sqrt{{3}}', 'slope_numeric': -math.sqrt(3)},
    135: {'slope_display': '-1', 'slope_numeric': -1.0},
    150: {'slope_display': r'-\\frac{{\\sqrt{{3}}}}{{3}}', 'slope_numeric': -math.sqrt(3)/3},
    180: {'slope_display': '0', 'slope_numeric': 0.0} # Angle of inclination defined 0 <= theta < 180, but tan(180)=0
}

# The unique angles between 0 and 180 (exclusive of 180) that map to a slope.
# These are the standard angles of inclination.
_COMMON_ANGLES_FOR_INCLINATION = [angle for angle in _ANGLE_INFO if angle < 180]

# Pre-defined display and numeric values for slopes to help with parsing user input
_SLOPE_VALUES_CANONICAL = {
    '0': {'display': '0', 'numeric': 0.0},
    '1': {'display': '1', 'numeric': 1.0},
    '-1': {'display': '-1', 'numeric': -1.0},
    r'\\sqrt{{3}}': {'display': r'\\sqrt{{3}}', 'numeric': math.sqrt(3)},
    r'-\\sqrt{{3}}': {'display': r'-\\sqrt{{3}}', 'numeric': -math.sqrt(3)},
    r'\\frac{{\\sqrt{{3}}}}{{3}}': {'display': r'\\frac{{\\sqrt{{3}}}}{{3}}', 'numeric': math.sqrt(3)/3},
    r'-\\frac{{\\sqrt{{3}}}}{{3}}': {'display': r'-\\frac{{\\sqrt{{3}}}}{{3}}', 'numeric': -math.sqrt(3)/3},
    'undefined': {'display': 'undefined', 'numeric': float('inf')}
}

def generate(level=1):
    problem_type_options = {
        1: ['angle_from_slope', 'slope_from_angle', 'line_eq_from_angle_point', 'angle_between_two_lines'],
        2: ['line_eq_from_angle_point', 'angle_between_two_lines'],
        3: ['angle_between_two_lines']
    }
    
    problem_type = random.choice(problem_type_options.get(level, problem_type_options[1]))
    
    if problem_type == 'angle_from_slope':
        return generate_angle_from_slope_problem()
    elif problem_type == 'slope_from_angle':
        return generate_slope_from_angle_problem()
    elif problem_type == 'line_eq_from_angle_point':
        return generate_line_eq_from_angle_point_problem()
    elif problem_type == 'angle_between_two_lines':
        return generate_angle_between_two_lines_problem()

def generate_angle_from_slope_problem():
    """
    生成「已知斜率求斜角」的題目。
    """
    chosen_angle = random.choice(_COMMON_ANGLES_FOR_INCLINATION)
    slope_info = _ANGLE_INFO[chosen_angle]
    
    question_text = f"已知直線 $L$ 的斜率 $m = {slope_info['slope_display']}$，求斜角 $\\theta$ 的度數。"
    correct_answer = f"${chosen_angle}{{\\circ}}$"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_slope_from_angle_problem():
    """
    生成「已知斜角求斜率」的題目。
    """
    chosen_angle = random.choice(_COMMON_ANGLES_FOR_INCLINATION)
    slope_info = _ANGLE_INFO[chosen_angle]
    
    question_text = f"已知直線 $L$ 的斜角為 ${chosen_angle}{{\\circ}}$，求斜率 $m$ 的值。"
    correct_answer = slope_info['slope_display']
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_line_eq_from_angle_point_problem():
    """
    生成「已知斜角與一點，求直線方程式」的題目。
    為簡化答案形式，此題型僅使用斜率為 0, 1, -1, undefined 的角度。
    """
    rational_slope_angles = [0, 45, 90, 135] # Slopes: 0, 1, undefined, -1
    chosen_angle = random.choice(rational_slope_angles)
    slope_info = _ANGLE_INFO[chosen_angle]
    m_display = slope_info['slope_display']
    m_numeric = slope_info['slope_numeric']
    
    x1 = random.randint(-5, 5)
    y1 = random.randint(-5, 5)
    
    question_text = f"已知直線 $L$ 的斜角為 ${chosen_angle}{{\\circ}}$，且通過點 $P({x1}, {y1})$，求 $L$ 的方程式。"
    
    correct_answer = ""
    if m_display == 'undefined': # Vertical line x = x1
        correct_answer = f"$x = {x1}$"
    else: # y = mx + b form
        b_numeric = y1 - m_numeric * x1
        b_frac = Fraction(b_numeric).limit_denominator(100)
        
        b_str = ""
        if b_frac.denominator == 1:
            b_str = str(b_frac.numerator)
        else:
            b_str = r'\\frac{{{}}}{{{}}}'.format(b_frac.numerator, b_frac.denominator)
            
        if m_display == '0':
            correct_answer = f"$y = {b_str}$"
        elif m_display == '1':
            if b_str == '0':
                correct_answer = "$y = x$"
            elif b_frac.numerator < 0:
                correct_answer = f"$y = x {b_str}$" # b_str already contains '-'
            else:
                correct_answer = f"$y = x + {b_str}$"
        elif m_display == '-1':
            if b_str == '0':
                correct_answer = "$y = -x$"
            elif b_frac.numerator < 0:
                correct_answer = f"$y = -x {b_str}$"
            else:
                correct_answer = f"$y = -x + {b_str}$"
        # For other rational slopes (e.g., 1/2), the 'else' part would be:
        # else:
        #     ans_parts = [f"$y = {m_display}x$"]
        #     if b_frac.numerator != 0:
        #         if b_frac.numerator > 0: ans_parts.append(f" + {b_str}")
        #         else: ans_parts.append(f" {b_str}")
        #     correct_answer = "".join(ans_parts)
            
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_angle_between_two_lines_problem():
    """
    生成「求兩直線夾角」的題目。
    """
    # Choose two distinct angles of inclination
    angle1_deg = random.choice(_COMMON_ANGLES_FOR_INCLINATION)
    # Ensure angle2 is different from angle1 to avoid parallel lines initially,
    # though parallel lines will be handled by logic.
    angle2_deg = random.choice([a for a in _COMMON_ANGLES_FOR_INCLINATION if a != angle1_deg])
    
    slope1_info = _ANGLE_INFO[angle1_deg]
    slope2_info = _ANGLE_INFO[angle2_deg]
    
    m1_display = slope1_info['slope_display']
    m2_display = slope2_info['slope_display']
    
    # Generate line equations using simple y-intercepts
    b1 = random.randint(-3, 3)
    b2 = random.randint(-3, 3)
    
    line1_eq_str = ""
    line2_eq_str = ""

    # Format line equation string for L1
    if m1_display == 'undefined':
        x_val = random.randint(-5, 5) # vertical line x = C
        line1_eq_str = f"$L_1: x = {x_val}$"
    elif m1_display == '0':
        line1_eq_str = f"$L_1: y = {b1}$"
    else: # y = mx + b form
        b1_str = f" + {b1}" if b1 > 0 else (f" {b1}" if b1 < 0 else "")
        line1_eq_str = f"$L_1: y = {m1_display}x{b1_str}$"

    # Format line equation string for L2
    if m2_display == 'undefined':
        x_val = random.randint(-5, 5) # vertical line x = C
        line2_eq_str = f"$L_2: x = {x_val}$"
    elif m2_display == '0':
        line2_eq_str = f"$L_2: y = {b2}$"
    else: # y = mx + b form
        b2_str = f" + {b2}" if b2 > 0 else (f" {b2}" if b2 < 0 else "")
        line2_eq_str = f"$L_2: y = {m2_display}x{b2_str}$"

    question_text = f"求坐標平面上兩直線 {line1_eq_str} 與 {line2_eq_str} 夾角的度數。（兩解）"

    # Calculate angles between lines based on their angles of inclination
    angle_diff = abs(angle1_deg - angle2_deg)
    
    # The two angles between lines are angle_diff and 180 - angle_diff
    # Ensure the smaller angle is listed first.
    if angle_diff <= 90:
        correct_angle1 = angle_diff
        correct_angle2 = 180 - angle_diff
    else: # angle_diff > 90
        correct_angle1 = 180 - angle_diff
        correct_angle2 = angle_diff
    
    # Ensure answers are positive and sorted
    correct_angle1 = round(correct_angle1)
    correct_angle2 = round(correct_angle2)
    
    if correct_angle1 > correct_angle2:
        correct_angle1, correct_angle2 = correct_angle2, correct_angle1

    correct_answer = f"${correct_angle1}{{\\circ}}$ 或 ${correct_angle2}{{\\circ}}$"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    處理角度、斜率和直線方程式等多種答案格式。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()

    is_correct = False
    
    def get_numeric_slope_from_ans_string(ans_str):
        """Helper to convert slope strings (LaTeX, plain text) to numeric values."""
        ans_str_clean = ans_str.lower().strip().replace(' ', '').replace('$', '').replace('{', '').replace('}', '')

        # Handle 'undefined'
        if ans_str_clean in ['undefined', 'undef', '無', '無限', 'infinity']:
            return float('inf')
        
        # Handle specific string representations for common slopes
        if ans_str_clean == '0': return 0.0
        if ans_str_clean == '1': return 1.0
        if ans_str_clean == '-1': return -1.0
        
        if ans_str_clean in [r'\\sqrt{3}', 'sqrt(3)', 'root3', r'\\sqrt{{3}}']:
            return math.sqrt(3)
        if ans_str_clean in [r'-\\sqrt{3}', '-sqrt(3)', '-root3', r'-\\sqrt{{3}}']:
            return -math.sqrt(3)
        if ans_str_clean in [r'\\frac{\\sqrt{3}}{3}', 'sqrt(3)/3', 'root3/3', r'\\frac{{\\sqrt{{3}}}}{{3}}', r'\\frac{\\sqrt{3}}{3}']:
            return math.sqrt(3)/3
        if ans_str_clean in [r'-\\frac{\\sqrt{3}}{3}', '-sqrt(3)/3', '-root3/3', r'-\\frac{{\\sqrt{{3}}}}{{3}}', r'-\\frac{\\sqrt{3}}{3}']:
            return -math.sqrt(3)/3

        # Try converting to float
        try:
            return float(ans_str_clean)
        except ValueError:
            pass
        
        return None # Could not parse

    # --- Check Logic ---
    if '或' in correct_answer: # Angle between two lines (e.g., "$75^\\circ$ 或 $105^\\circ$")
        correct_parts_str = [p.replace(r'$', '').replace(r'{', '').replace(r'}', '').replace(r'\\circ', '').replace(' ', '').replace('度', '') for p in correct_answer.split('或')]
        user_parts_str = [p.replace(r'$', '').replace(r'{', '').replace(r'}', '').replace(r'\\circ', '').replace(' ', '').replace('度', '') for p in user_answer.split('或')]
        
        try:
            correct_nums = sorted([float(p) for p in correct_parts_str])
            user_nums = sorted([float(p) for p in user_parts_str])
            if len(correct_nums) == len(user_nums):
                is_correct = all(abs(c - u) < 1e-6 for c, u in zip(correct_nums, user_nums))
        except ValueError:
            is_correct = False

    elif r'\\circ' in correct_answer: # Single angle answer (e.g., "$45^\\circ$")
        correct_num = float(correct_answer.replace(r'$', '').replace(r'{', '').replace(r'}', '').replace(r'\\circ', '').replace(' ', '').replace('度', ''))
        user_num_str = user_answer.replace(r'$', '').replace(r'{', '').replace(r'}', '').replace(r'\\circ', '').replace(' ', '').replace('度', '')
        try:
            user_num = float(user_num_str)
            is_correct = abs(correct_num - user_num) < 1e-6
        except ValueError:
            is_correct = False
            
    elif 'y =' in correct_answer or 'x =' in correct_answer: # Line equation (e.g., "$y = x + 5$")
        # For line equations, perform a strict string comparison after normalization.
        # This expects the user to input the equation in a specific canonical form.
        norm_correct = correct_answer.replace(' ', '').replace('$', '').replace(r'{', '').replace(r'}', '')
        norm_user = user_answer.replace(' ', '').replace('$', '').replace(r'{', '').replace(r'}', '')
        is_correct = (norm_user == norm_correct)

    else: # Slope answer (e.g., "$1$", "$-\\sqrt{3}$", "undefined")
        correct_numeric_slope = get_numeric_slope_from_ans_string(correct_answer)
        user_numeric_slope = get_numeric_slope_from_ans_string(user_answer)
        
        if correct_numeric_slope is not None and user_numeric_slope is not None:
            if correct_numeric_slope == float('inf') and user_numeric_slope == float('inf'):
                is_correct = True
            elif abs(correct_numeric_slope - user_numeric_slope) < 1e-6:
                is_correct = True
        else:
            is_correct = False # One or both could not be parsed as a known numeric slope

    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}