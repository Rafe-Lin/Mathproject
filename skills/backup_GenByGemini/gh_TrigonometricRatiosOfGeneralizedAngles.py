import random
import math
import re # For parsing user input
from fractions import Fraction

# Internal format for sin, cos values:
# (int_numerator, int_denominator) for rational numbers (e.g., (1, 2) for 1/2)
# (coeff, sqrt_val, den) for coeff*sqrt(sqrt_val)/den (e.g., (1, 3, 2) for sqrt(3)/2, (-1, 3, 1) for -sqrt(3))
#   coeff, sqrt_val, den are integers.
# "UNDEFINED_VALUE" for cases like tan(90)

UNDEFINED_VALUE = "未定義"

def _sign_change(value_tuple):
    """Changes the sign of an internal value tuple."""
    if value_tuple == UNDEFINED_VALUE:
        return UNDEFINED_VALUE
    if len(value_tuple) == 2: # (num, den)
        num, den = value_tuple
        return (-num, den)
    if len(value_tuple) == 3: # (coeff, sqrt_val, den)
        coeff, sqrt_val, den = value_tuple
        return (-coeff, sqrt_val, den)
    return value_tuple # Should not happen

def _format_value_to_latex(value_tuple):
    """Converts the internal value tuple to a LaTeX string."""
    if value_tuple == UNDEFINED_VALUE:
        return UNDEFINED_VALUE
    
    if len(value_tuple) == 2: # Rational: (num, den)
        num, den = value_tuple
        if den == 0: return UNDEFINED_VALUE
        frac = Fraction(num, den)
        if frac.denominator == 1:
            return str(frac.numerator)
        else:
            return r"\\frac{{{}}}}{{{}}}".format(frac.numerator, frac.denominator)
            
    if len(value_tuple) == 3: # Irrational: (coeff, sqrt_val, den)
        coeff, sqrt_val, den = value_tuple
        if den == 0: return UNDEFINED_VALUE
        if coeff == 0: return "0"
        
        # Simplify sqrt_val part (e.g., sqrt(12) -> 2*sqrt(3))
        current_coeff = 1
        temp_sqrt_val = sqrt_val
        i = 2
        while i * i <= temp_sqrt_val:
            if temp_sqrt_val % (i * i) == 0:
                current_coeff *= i
                temp_sqrt_val //= (i * i)
            else:
                i += 1
        
        final_coeff_num = coeff * current_coeff
        final_sqrt_val = temp_sqrt_val

        # Simplify rational part (final_coeff_num / den)
        if final_sqrt_val == 1: # Expression was rational after all (e.g., 2*sqrt(1))
            frac = Fraction(final_coeff_num, den)
            if frac.denominator == 1:
                return str(frac.numerator)
            else:
                return r"\\frac{{{}}}}{{{}}}".format(frac.numerator, frac.denominator)
        
        # Now format the combined expression
        frac_rational = Fraction(final_coeff_num, den)
        
        if frac_rational.numerator == 1 and frac_rational.denominator == 1:
            return r"\\sqrt{{{}}}".format(final_sqrt_val)
        elif frac_rational.numerator == 1: # e.g., sqrt(3)/2
            return r"\\frac{{\\sqrt{{{}}}}}{{{}}}".format(final_sqrt_val, frac_rational.denominator)
        elif frac_rational.denominator == 1: # e.g., 2*sqrt(3)
            return r"{}\\sqrt{{{}}}".format(frac_rational.numerator, final_sqrt_val)
        else: # e.g., 2*sqrt(3)/3
            return r"\\frac{{{}}\\sqrt{{{}}}}}{{{}}}".format(frac_rational.numerator, final_sqrt_val, frac_rational.denominator)
    
    return str(value_tuple) # Fallback

def _evaluate_value_to_float(value_tuple):
    """Converts the internal value tuple to a float for comparison."""
    if value_tuple == UNDEFINED_VALUE:
        return float('nan')
    
    if len(value_tuple) == 2: # Rational: (num, den)
        num, den = value_tuple
        if den == 0: return float('nan')
        return num / den
            
    if len(value_tuple) == 3: # Irrational: (coeff, sqrt_val, den)
        coeff, sqrt_val, den = value_tuple
        if den == 0: return float('nan')
        if coeff == 0: return 0.0
        return (coeff * math.sqrt(sqrt_val)) / den
            
    return float('nan') # Should not happen

def _parse_user_answer_to_float_and_string(s):
    """
    Parses a user's string answer into a float and returns the original string.
    Returns (float_value, string_representation)
    """
    original_s = s.strip()
    s_normalized = original_s.replace(" ", "").replace("\\", "").replace("sqrt", "SQRT")
    
    if s_normalized == UNDEFINED_VALUE or s_normalized.lower() in ["undefined", "und", "none"]:
        return float('nan'), original_s

    try: # Try to parse as float directly
        return float(s_normalized), original_s
    except ValueError:
        pass

    match_frac = re.match(r'(-?\d+)/(-?\d+)', s_normalized) # Try to parse as fraction: A/B
    if match_frac:
        num = float(match_frac.group(1))
        den = float(match_frac.group(2))
        if den == 0: return float('nan'), original_s
        return num / den, original_s

    # Try to parse as sqrt expression: (coeff)SQRT(val)(/den)
    match_sqrt_pattern = re.match(r'(-?\d*)\s*SQRT\((\d+)\)(?:/(-?\d+))?', s_normalized)
    if match_sqrt_pattern:
        coeff_str, sqrt_val_str, den_str = match_sqrt_pattern.groups()
        
        coeff = 1.0
        if coeff_str == '-':
            coeff = -1.0
        elif coeff_str:
            try: coeff = float(coeff_str)
            except ValueError: pass 
        
        try:
            sqrt_val = float(sqrt_val_str)
            if sqrt_val < 0: return float('nan'), original_s
            
            val = coeff * math.sqrt(sqrt_val)
            
            if den_str:
                den = float(den_str)
                if den == 0: return float('nan'), original_s
                val /= den
            return val, original_s
        except ValueError:
            pass
            
    return float('nan'), original_s # Parsing failed


def generate_point_on_terminal_side(level):
    """Generates problems where a point P(x, y) on the terminal side is given."""
    if level == 1:
        # P(x, y) with integer r (Pythagorean triples)
        valid_triples = [
            (3, 4), (4, 3), (6, 8), (8, 6),
            (5, 12), (12, 5),
            (7, 24), (24, 7),
            (8, 15), (15, 8)
        ]
        x_abs, y_abs = random.choice(valid_triples)
        
        # Randomize quadrant
        quadrant = random.randint(1, 4)
        x_sign = 1 if quadrant in [1, 4] else -1
        y_sign = 1 if quadrant in [1, 2] else -1
        
        x = x_abs * x_sign
        y = y_abs * y_sign

        r_sq = x**2 + y**2
        r_val = int(math.sqrt(r_sq)) # r_val is an integer here

        sin_val = (y, r_val)
        cos_val = (x, r_val)
        tan_val = (y, x) if x != 0 else UNDEFINED_VALUE
    else: # level 2 and above, allow r to be non-integer sqrt
        while True:
            x = random.randint(-10, 10)
            y = random.randint(-10, 10)
            if x == 0 and y == 0: # Cannot be origin
                continue
            r_sq = x**2 + y**2
            r_val_is_int = math.sqrt(r_sq).is_integer()

            if level == 2 and not r_val_is_int: # For level 2, sometimes non-integer r
                break
            if level == 3: # For level 3, it's fine for r to be integer or not
                break
            # Fallback if the loop doesn't break, primarily for testing level 1 path
            if level == 1 and r_val_is_int:
                break
            if level == 1 and not r_val_is_int:
                continue
            break
        
        # Now calculate values based on x, y, r_sq
        if r_val_is_int:
            r_val = int(math.sqrt(r_sq))
            sin_val = (y, r_val)
            cos_val = (x, r_val)
        else: # r is irrational (e.g. sqrt(5)), rationalize denominator in internal format
            sin_val = (y, r_sq, r_sq) # (coeff, sqrt_val, den) for y*sqrt(r_sq)/r_sq
            cos_val = (x, r_sq, r_sq) # (coeff, sqrt_val, den) for x*sqrt(r_sq)/r_sq
        
        tan_val = (y, x) if x != 0 else UNDEFINED_VALUE

    question_text = f"已知 $P({x}, {y})$ 為標準位置角 $\\theta$ 終邊上的一點，求 $\\sin\\theta$, $\\cos\\theta$ 及 $\\tan\\theta$ 的值。"
    
    answer_s = _format_value_to_latex(sin_val)
    answer_c = _format_value_to_latex(cos_val)
    answer_t = _format_value_to_latex(tan_val)
    
    correct_answer = f"$\\sin\\theta = {answer_s}$, $\\cos\\theta = {answer_c}$, $\\tan\\theta = {answer_t}$"
    
    return {
        "question_text": question_text,
        "answer": correct_answer, # This is the full formatted answer
        "correct_answer": { # Store individual components for robust checking
            "sin": sin_val,
            "cos": cos_val,
            "tan": tan_val
        }
    }


def generate_specific_angle_value(level):
    """Generates problems asking for trig ratios of a specific angle."""
    
    # Base special angles and quadrantal angles in Q1/axis (values are for reference angle)
    base_angle_data = {
        0: {"sin": (0,1), "cos": (1,1), "tan": (0,1)},
        30: {"sin": (1,2), "cos": (1,3,2), "tan": (1,3,3)}, # sqrt(3)/3
        45: {"sin": (1,2,2), "cos": (1,2,2), "tan": (1,1)}, # sqrt(2)/2
        60: {"sin": (1,3,2), "cos": (1,2), "tan": (1,3,1)}, # sqrt(3)
        90: {"sin": (1,1), "cos": (0,1), "tan": UNDEFINED_VALUE},
    }

    angle_options = list(base_angle_data.keys())
    
    # Select a base angle to use as a reference, then rotate it
    ref_angle_base = random.choice([0, 30, 45, 60, 90])
    
    # Determine the actual angle to ask for
    actual_angle = ref_angle_base
    
    # Add quadrant rotation for levels > 1, and co-terminal/negative for levels >= 2
    if level >= 1 and ref_angle_base not in [0, 90]: # for 30,45,60 degrees
        quadrant_multiplier = random.choice([0, 1, 2, 3]) # 0 for Q1 (no change), 1 for Q2, 2 for Q3, 3 for Q4
        actual_angle = (ref_angle_base + quadrant_multiplier * 90) # This does not always give correct reference angles relative to 180 or 360
        
        # A simpler way: pick a target quadrant directly, then reconstruct the angle
        quadrant = random.randint(1,4)
        if quadrant == 1:
            actual_angle = ref_angle_base
        elif quadrant == 2:
            actual_angle = 180 - ref_angle_base
        elif quadrant == 3:
            actual_angle = 180 + ref_angle_base
        elif quadrant == 4:
            actual_angle = 360 - ref_angle_base
        # Handle cases where ref_angle_base is 0 or 90
        if ref_angle_base == 0: actual_angle = random.choice([0, 180])
        if ref_angle_base == 90: actual_angle = random.choice([90, 270])

    if level >= 2: # Add full rotations or make negative
        if random.random() < 0.6: # Add full rotations
            actual_angle += random.choice([-2, -1, 1, 2]) * 360
        if random.random() < 0.4: # Make negative
            actual_angle *= -1
    
    angle_degrees_for_question = actual_angle
    
    # Normalize angle to [0, 360) for calculation logic
    norm_angle = actual_angle % 360
    if norm_angle < 0:
        norm_angle += 360
    
    # Determine quadrant and reference angle for calculation
    ref_angle_val = norm_angle
    quadrant = 0
    
    if 0 <= norm_angle < 90:
        quadrant = 1
        ref_angle_val = norm_angle
    elif 90 < norm_angle < 180:
        quadrant = 2
        ref_angle_val = 180 - norm_angle
    elif 180 <= norm_angle < 270: # 180 and 270 are specific axis cases
        quadrant = 3
        ref_angle_val = norm_angle - 180
    elif 270 <= norm_angle < 360:
        quadrant = 4
        ref_angle_val = 360 - norm_angle

    # Fetch reference values
    # If ref_angle_val is not a base angle (e.g. 180, 270), use the exact data for those
    if ref_angle_val in base_angle_data:
        ref_data = base_angle_data[ref_angle_val]
    elif norm_angle == 180:
        ref_data = {"sin": (0,1), "cos": (-1,1), "tan": (0,1)}
        quadrant = 0 # Quadrantal
    elif norm_angle == 270:
        ref_data = {"sin": (-1,1), "cos": (0,1), "tan": UNDEFINED_VALUE}
        quadrant = 0 # Quadrantal
    else: # Fallback for unexpected ref_angle_val, should not occur with chosen base_angles
        # This implies an issue with how `actual_angle` was created.
        # Re-generate if this happens to ensure valid special angle problem.
        return generate_specific_angle_value(level)

    sin_val = ref_data["sin"]
    cos_val = ref_data["cos"]
    tan_val = ref_data["tan"]
    
    # Apply signs based on quadrant if not a quadrantal angle (quadrant=0 means on axis)
    if quadrant == 1:
        pass # All positive
    elif quadrant == 2: # sin > 0, cos < 0, tan < 0
        cos_val = _sign_change(cos_val)
        tan_val = _sign_change(tan_val)
    elif quadrant == 3: # sin < 0, cos < 0, tan > 0
        sin_val = _sign_change(sin_val)
        cos_val = _sign_change(cos_val)
        # tan remains positive due to (-)/(-)
    elif quadrant == 4: # sin < 0, cos > 0, tan < 0
        sin_val = _sign_change(sin_val)
        tan_val = _sign_change(tan_val)

    question_text = f"利用廣義角三角比的定義，求 $\\sin{angle_degrees_for_question}°$, $\\cos{angle_degrees_for_question}°$ 及 $\\tan{angle_degrees_for_question}°$ 的值。"
    
    answer_s = _format_value_to_latex(sin_val)
    answer_c = _format_value_to_latex(cos_val)
    answer_t = _format_value_to_latex(tan_val)
    
    correct_answer = f"$\\sin{angle_degrees_for_question}° = {answer_s}$, $\\cos{angle_degrees_for_question}° = {answer_c}$, $\\tan{angle_degrees_for_question}° = {answer_t}$"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": {
            "sin": sin_val,
            "cos": cos_val,
            "tan": tan_val
        }
    }


def generate_one_ratio_and_quadrant(level):
    """Generates problems where one trig ratio and the quadrant are given."""
    
    given_ratio_type = random.choice(['sin', 'cos'])
    
    # Use Pythagorean triples
    pyth_triple = random.choice([(3,4,5), (5,12,13), (7,24,25)])
    a, b, c = pyth_triple
    
    # Choose which leg to use as numerator for the given ratio
    numerator_val_abs = random.choice([a, b])
    denominator_val = c # Hypotenuse is always positive denominator
    
    # Randomize sign for the given ratio, then find consistent quadrant
    possible_quadrants = []
    
    if given_ratio_type == 'sin':
        # sin=num/den, num can be positive or negative
        sign_for_given = random.choice([-1, 1])
        given_ratio_value = (numerator_val_abs * sign_for_given, denominator_val)
        if given_ratio_value[0] > 0: # sin > 0 in Q1, Q2
            possible_quadrants.extend([1, 2])
        else: # sin < 0 in Q3, Q4
            possible_quadrants.extend([3, 4])
    else: # given_ratio_type == 'cos'
        sign_for_given = random.choice([-1, 1])
        given_ratio_value = (numerator_val_abs * sign_for_given, denominator_val)
        if given_ratio_value[0] > 0: # cos > 0 in Q1, Q4
            possible_quadrants.extend([1, 4])
        else: # cos < 0 in Q2, Q3
            possible_quadrants.extend([2, 3])
            
    quadrant = random.choice(possible_quadrants)

    # Determine signs for sin, cos, tan in this quadrant
    sign_sin = 1 if quadrant in [1, 2] else -1
    sign_cos = 1 if quadrant in [1, 4] else -1
    
    # Calculate the missing ratio (the other leg)
    other_numerator_abs = a if numerator_val_abs == b else b
    other_ratio_value_magnitude = (other_numerator_abs, denominator_val)
    
    # Apply sign for the other ratio
    sin_final = None
    cos_final = None

    if given_ratio_type == 'sin':
        sin_final = given_ratio_value
        cos_final = (_sign_change(other_ratio_value_magnitude)) if sign_cos == -1 else other_ratio_value_magnitude
    else: # given_ratio_type == 'cos'
        cos_final = given_ratio_value
        sin_final = (_sign_change(other_ratio_value_magnitude)) if sign_sin == -1 else other_ratio_value_magnitude
        
    # Calculate tan_final = sin_final / cos_final
    tan_num = sin_final[0] * cos_final[1]
    tan_den = sin_final[1] * cos_final[0]
    tan_final = (tan_num, tan_den) if tan_den != 0 else UNDEFINED_VALUE

    # Construct question text
    quadrant_name = {1: '第一', 2: '第二', 3: '第三', 4: '第四'}[quadrant]
    given_ratio_str_latex = _format_value_to_latex(given_ratio_value)
    
    question_text_base = f"已知 $\\theta$ 是{quadrant_name}象限角且 $\\{given_ratio_type}\\theta = {given_ratio_str_latex}$，求 "
    
    correct_answer_text_parts = []
    correct_answer_dict = {}

    if given_ratio_type == 'sin':
        missing_s_latex = _format_value_to_latex(cos_final)
        missing_t_latex = _format_value_to_latex(tan_final)
        question_text = question_text_base + "$\\cos\\theta$ 和 $\\tan\\theta$ 的值。"
        correct_answer_text_parts.append(f"$\\cos\\theta = {missing_s_latex}$")
        correct_answer_text_parts.append(f"$\\tan\\theta = {missing_t_latex}$")
        correct_answer_dict = {"cos": cos_final, "tan": tan_final}
    else: # given_ratio_type == 'cos'
        missing_s_latex = _format_value_to_latex(sin_final)
        missing_t_latex = _format_value_to_latex(tan_final)
        question_text = question_text_base + "$\\sin\\theta$ 和 $\\tan\\theta$ 的值。"
        correct_answer_text_parts.append(f"$\\sin\\theta = {missing_s_latex}$")
        correct_answer_text_parts.append(f"$\\tan\\theta = {missing_t_latex}$")
        correct_answer_dict = {"sin": sin_final, "tan": tan_final}

    return {
        "question_text": question_text,
        "answer": ", ".join(correct_answer_text_parts),
        "correct_answer": correct_answer_dict
    }


def generate(level=1):
    problem_type = random.choices(
        ['point_on_terminal_side', 'specific_angle_value', 'one_ratio_and_quadrant'],
        weights=[0.4, 0.4, 0.2] if level <=2 else [0.3, 0.4, 0.3]
    )[0]
    
    if problem_type == 'point_on_terminal_side':
        return generate_point_on_terminal_side(level)
    elif problem_type == 'specific_angle_value':
        return generate_specific_angle_value(level)
    else: # 'one_ratio_and_quadrant'
        return generate_one_ratio_and_quadrant(level)

def check(user_answer, correct_answer_dict):
    """
    Checks the user's answer against the correct answer dictionary.
    `correct_answer_dict` contains keys like "sin", "cos", "tan" with internal value tuples.
    `user_answer` is a string, e.g., "sin=1/2, cos=sqrt(3)/2, tan=sqrt(3)/3"
    """
    user_answer = user_answer.strip().replace(" ", "")
    is_correct = True
    feedback_parts = []
    
    user_parsed_values = {}
    user_string_values = {} # Store original string representations

    # Regex to extract sin, cos, tan values from user_answer string
    # Patterns for: sin=VALUE, cos=VALUE, tan=VALUE
    # The `(?:,|$)` ensures we match until a comma or end of string.
    # `(-?.*?)` is a non-greedy match for the value.

    match_sin = re.search(r'sin(?:\\theta)?=(-?.*?)(?:,|$)'.replace(r'\s*', r'\s*'), user_answer, re.IGNORECASE)
    if match_sin:
        float_val, str_val = _parse_user_answer_to_float_and_string(match_sin.group(1))
        user_parsed_values['sin'] = float_val
        user_string_values['sin'] = str_val

    match_cos = re.search(r'cos(?:\\theta)?=(-?.*?)(?:,|$)'.replace(r'\s*', r'\s*'), user_answer, re.IGNORECASE)
    if match_cos:
        float_val, str_val = _parse_user_answer_to_float_and_string(match_cos.group(1))
        user_parsed_values['cos'] = float_val
        user_string_values['cos'] = str_val

    match_tan = re.search(r'tan(?:\\theta)?=(-?.*?)(?:,|$)'.replace(r'\s*', r'\s*'), user_answer, re.IGNORECASE)
    if match_tan:
        float_val, str_val = _parse_user_answer_to_float_and_string(match_tan.group(1))
        user_parsed_values['tan'] = float_val
        user_string_values['tan'] = str_val

    # Compare each value
    for key, correct_val_tuple in correct_answer_dict.items():
        correct_float_val = _evaluate_value_to_float(correct_val_tuple)
        user_float_val = user_parsed_values.get(key, float('nan'))
        user_string_repr = user_string_values.get(key, '未提供')

        # Check for NaN (undefined) explicitly
        if math.isnan(correct_float_val) and math.isnan(user_float_val):
            # Both are undefined, considered correct for this component
            feedback_parts.append(f"$\\ {key}\\theta $ 的值是 {UNDEFINED_VALUE}，您的回答也是 {user_string_repr}，正確。")
        elif math.isclose(correct_float_val, user_float_val, rel_tol=1e-9, abs_tol=1e-9):
            # Values are numerically close enough
            feedback_parts.append(f"$\\ {key}\\theta = {_format_value_to_latex(correct_val_tuple)}$，您的回答 {user_string_repr} 正確。")
        else:
            # Values don't match
            is_correct = False
            feedback_parts.append(f"$\\ {key}\\theta = {_format_value_to_latex(correct_val_tuple)}$，您的回答 {user_string_repr} 不正確。")
            
    result_text = " ".join(feedback_parts)
    if is_correct:
        result_text = "完全正確！" + result_text
    else:
        result_text = "您的答案不正確。" + result_text

    return {"correct": is_correct, "result": result_text, "next_question": True}