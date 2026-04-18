import random
import math
import re
from fractions import Fraction

# --- Helper functions for formatting ---

def _format_coord_value(val_squared):
    """
    Formats a squared numerical value for display as a coordinate component.
    If val_squared is a perfect square, it returns the integer square root.
    Otherwise, it returns the square root in LaTeX format (e.g., r"\\sqrt{7}").
    Assumes val_squared is non-negative.
    """
    if val_squared == 0:
        return "0"
    
    # Check if it's a perfect square for integers
    if isinstance(val_squared, int) or val_squared.is_integer():
        int_val_squared = int(val_squared)
        sqrt_int = math.isqrt(int_val_squared) # integer square root
        if sqrt_int * sqrt_int == int_val_squared:
            return str(sqrt_int)
    
    # Otherwise, display as square root, assuming it's for values like c^2
    return rf"\\sqrt{{{int(val_squared)}}}"


def _format_coords_display_string(x_val_or_sq, y_val_or_sq, is_foci=False):
    """
    Formats coordinates as a display string, handling different cases for vertices/foci.
    x_val_or_sq, y_val_or_sq represent the *squared* value if it's derived from c^2,
    or the direct integer value if it's for a or b. `_format_coord_value` handles this distinction.
    `is_foci` helps decide presentation for non-integer square roots (e.g., separate points).
    """
    x_str = _format_coord_value(x_val_or_sq) if x_val_or_sq != 0 else "0"
    y_str = _format_coord_value(y_val_or_sq) if y_val_or_sq != 0 else "0"

    # Determine if the value is a perfect square for decision making
    x_is_perfect_sq = (math.isqrt(int(x_val_or_sq))**2 == int(x_val_or_sq)) if x_val_or_sq != 0 else True
    y_is_perfect_sq = (math.isqrt(int(y_val_or_sq))**2 == int(y_val_or_sq)) if y_val_or_sq != 0 else True

    if x_val_or_sq != 0 and y_val_or_sq == 0: # Like (±A, 0) or (±C, 0)
        # Use \\pm if it's a perfect square or not a focus (e.g., vertices)
        if x_is_perfect_sq or not is_foci:
            return rf"($\\pm${x_str}, 0)"
        else: # Foci with non-perfect square c (e.g., sqrt(7)), typically listed as separate points
            return rf"($-{x_str}$, 0) 與 (${x_str}$, 0)"
    elif x_val_or_sq == 0 and y_val_or_sq != 0: # Like (0, ±A) or (0, ±C)
        if y_is_perfect_sq or not is_foci:
            return rf"(0, $\\pm${y_str})"
        else: # Foci with non-perfect square c
            return rf"(0, $-{y_str}$) 與 (0, ${y_str}$)"
    elif x_val_or_sq == 0 and y_val_or_sq == 0:
        return "(0,0)"
    else: # This case is not expected for standard ellipse properties (foci, vertices) at origin
        return rf"($\\pm${x_str}, $\\pm${y_str})" # Fallback, unlikely to be used


def _format_denominator(val_sq):
    """Formats a squared value for the denominator in the ellipse equation, ensuring integer strings."""
    if val_sq == int(val_sq):
        return str(int(val_sq))
    # This path should ideally not be hit if a^2 and b^2 are always integers.
    frac_val = Fraction(val_sq).limit_denominator(100)
    if frac_val.denominator != 1:
        return rf"\\frac{{{frac_val.numerator}}}{{{frac_val.denominator}}}"
    return str(int(frac_val.numerator))


def _format_equation_str(a_sq, b_sq, major_axis_on_x):
    """
    Formats the standard ellipse equation string.
    a_sq is the semi-major axis squared, b_sq is the semi-minor axis squared.
    """
    if major_axis_on_x:
        x_den = _format_denominator(a_sq)
        y_den = _format_denominator(b_sq)
    else: # major_axis_on_y
        x_den = _format_denominator(b_sq)
        y_den = _format_denominator(a_sq)

    return rf"$\\frac{{x^{{2}}}}{{{x_den}}} + \\frac{{y^{{2}}}}{{{y_den}}} = 1$"

# --- Problem generation functions ---

def _generate_equation_from_properties(level):
    """Generates a problem to find the ellipse equation from given properties."""
    major_axis_on_x = random.choice([True, False])

    # Generate a, b (semi-major, semi-minor axes) as integers.
    # a > b, a > c, b > 0, c > 0
    a = random.randint(5, 12 + level * 2) # a >= 5 to allow for varied b, c
    b = random.randint(1, a - 1)          # b >= 1 and b < a

    a_sq = a * a
    b_sq = b * b
    c_sq = a_sq - b_sq # c_sq can be a non-perfect square

    # Ensure c_sq is not 0 (i.e., not a circle)
    while c_sq == 0:
        a = random.randint(5, 12 + level * 2)
        b = random.randint(1, a - 1)
        a_sq = a * a
        b_sq = b * b
        c_sq = a_sq - b_sq

    # Randomly choose which properties to give in the question
    property_given_choice = random.choice(['foci_major_axis_len', 'foci_minor_axis_len'])

    question_text = ""
    if property_given_choice == 'foci_major_axis_len':
        major_axis_len = 2 * a
        foci_display_str = _format_coords_display_string(c_sq, 0, is_foci=True) if major_axis_on_x else _format_coords_display_string(0, c_sq, is_foci=True)
        question_text = rf"求中心在原點，焦點為 ${{foci_display_str}}$，長軸長為 ${major_axis_len}$ 的橢圓方程式。"
    else: # 'foci_minor_axis_len'
        minor_axis_len = 2 * b
        foci_display_str = _format_coords_display_string(c_sq, 0, is_foci=True) if major_axis_on_x else _format_coords_display_string(0, c_sq, is_foci=True)
        question_text = rf"求中心在原點，焦點為 ${{foci_display_str}}$，短軸長為 ${minor_axis_len}$ 的橢圓方程式。"
            
    correct_equation_str = _format_equation_str(a_sq, b_sq, major_axis_on_x)

    return {
        "question_text": question_text,
        "answer": correct_equation_str,
        "correct_answer": correct_equation_str
    }


def _generate_properties_from_equation(level):
    """Generates a problem to find ellipse properties from its equation."""
    major_axis_on_x = random.choice([True, False])

    # Generate a, b as integers.
    a = random.randint(3, 10 + level) # semi-major axis length
    b = random.randint(1, a - 1)      # semi-minor axis length
    
    a_sq = a * a
    b_sq = b * b
    c_sq = a_sq - b_sq # c_sq can be a non-perfect square

    # Regenerate if c_sq is 0 (would be a circle)
    while c_sq == 0:
        a = random.randint(3, 10 + level)
        b = random.randint(1, a - 1)
        a_sq = a * a
        b_sq = b * b
        c_sq = a_sq - b_sq
        
    equation_str = _format_equation_str(a_sq, b_sq, major_axis_on_x)
    
    question_text_base = rf"已知橢圓方程式為 ${equation_str}$。"
    
    # Randomly choose what property to ask for
    property_to_ask = random.choice(['major_vertices', 'minor_vertices', 'foci'])
    
    correct_answer_str = ""
    if property_to_ask == 'major_vertices':
        if major_axis_on_x:
            correct_answer_str = _format_coords_display_string(a_sq, 0, is_foci=False) # Pass a_sq for _format_coord_value to simplify
        else:
            correct_answer_str = _format_coords_display_string(0, a_sq, is_foci=False)
        question_text = question_text_base + rf" 求其長軸頂點坐標。"
    elif property_to_ask == 'minor_vertices':
        if major_axis_on_x:
            correct_answer_str = _format_coords_display_string(0, b_sq, is_foci=False)
        else:
            correct_answer_str = _format_coords_display_string(b_sq, 0, is_foci=False)
        question_text = question_text_base + rf" 求其短軸頂點坐標。"
    else: # 'foci'
        if major_axis_on_x:
            correct_answer_str = _format_coords_display_string(c_sq, 0, is_foci=True)
        else:
            correct_answer_str = _format_coords_display_string(0, c_sq, is_foci=True)
        question_text = question_text_base + rf" 求其焦點坐標。"
        
    return {
        "question_text": question_text,
        "answer": correct_answer_str,
        "correct_answer": correct_answer_str
    }

def generate(level=1):
    """
    生成「中心在原點的橢圓標準方程式」相關題目。
    包含：
    1. 從橢圓性質推導方程式
    2. 從橢圓方程式推導其性質 (頂點、焦點)
    """
    problem_type = random.choice(['equation_from_properties', 'properties_from_equation'])

    if problem_type == 'equation_from_properties':
        return _generate_equation_from_properties(level)
    else:
        return _generate_properties_from_equation(level)

# --- Answer checking functions ---

def _parse_equation_string(eq_str):
    """
    Parses an ellipse equation string into (x_denominator, y_denominator) tuple.
    Returns (D1, D2) for x^2/D1 + y^2/D2 = 1, or None if parsing fails.
    """
    # Remove all spaces and '$' signs for easier regex matching
    clean_str = eq_str.replace(" ", "").replace("$", "")

    # Regex patterns for x^2/D1 + y^2/D2 = 1 and y^2/D2 + x^2/D1 = 1
    # Group 1 is denominator for x^2, Group 2 is for y^2
    re_eq_x_first = r'\\frac{{x\^\{{2}}\}}{{\s*(\S+?)\s*}}\+\\frac{{y\^\{{2}}\}}{{\s*(\S+?)\s*}}=1'
    re_eq_y_first = r'\\frac{{y\^\{{2}}\}}{{\s*(\S+?)\s*}}\+\\frac{{x\^\{{2}}\}}{{\s*(\S+?)\s*}}=1'

    match_x_first = re.search(re_eq_x_first, clean_str)
    if match_x_first:
        den_x = match_x_first.group(1).replace('{', '').replace('}', '')
        den_y = match_x_first.group(2).replace('{', '').replace('}', '')
        try:
            return (float(den_x), float(den_y))
        except ValueError:
            return None

    match_y_first = re.search(re_eq_y_first, clean_str)
    if match_y_first:
        # If y^2 comes first, extract its denominator as den_y, then x^2's as den_x
        den_y = match_y_first.group(1).replace('{', '').replace('}', '')
        den_x = match_y_first.group(2).replace('{', '').replace('}', '')
        try:
            return (float(den_x), float(den_y))
        except ValueError:
            return None
    
    return None


def _parse_numeric_value(s):
    """
    Parses a string (e.g., "4", "r'\\sqrt{7}'", "-4") into a float.
    Handles LaTeX sqrt notation.
    """
    s = s.replace('{', '').replace('}', '').strip()
    if s.startswith(r'\\sqrt'):
        try:
            return math.sqrt(float(s[len(r'\\sqrt'):]))
        except ValueError:
            return None
    try:
        return float(s)
    except ValueError:
        return None


def _parse_coords_to_set_for_check(coord_string):
    """
    Parses a coordinate string (e.g., "($\\pm$4, 0)" or "(-$\\sqrt{7}$, 0) 與 ($\\sqrt{7}$, 0)")
    into a frozenset of (float, float) tuples for robust comparison.
    """
    coord_set = set()
    clean_string = coord_string.replace('$', '').strip() # Remove math delimiters and outer spaces

    # Split by " 與 " (and) if multiple points are listed
    point_strings = re.split(r'\s*與\s*', clean_string)

    for ps in point_strings:
        # Check for "\\pm" within the coordinate part itself, e.g., "($\\pm$4, 0)"
        pm_x_match = re.match(r'\(r"\\pm"(.+?),\s*(.+?)\)', ps)
        pm_y_match = re.match(r'\((.+?),\s*r"\\pm"(.+?)\)', ps)
        
        if pm_x_match:
            x_val = _parse_numeric_value(pm_x_match.group(1).replace(r'\\pm', ''))
            y_val = _parse_numeric_value(pm_x_match.group(2))
            if x_val is not None and y_val is not None:
                coord_set.add((x_val, y_val))
                coord_set.add((-x_val, y_val))
        elif pm_y_match:
            x_val = _parse_numeric_value(pm_y_match.group(1))
            y_val = _parse_numeric_value(pm_y_match.group(2).replace(r'\\pm', ''))
            if x_val is not None and y_val is not None:
                coord_set.add((x_val, y_val))
                coord_set.add((x_val, -y_val))
        else: # Standard (X, Y) format (e.g., "($\\sqrt{7}$, 0)")
            match = re.match(r'\(([^,]+?),\s*([^)]+?)\)', ps)
            if match:
                x_val = _parse_numeric_value(match.group(1))
                y_val = _parse_numeric_value(match.group(2))
                if x_val is not None and y_val is not None:
                    coord_set.add((x_val, y_val))
    return frozenset(coord_set) # Use frozenset for robust comparison


def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    Handles both ellipse equation strings and coordinate strings, allowing for minor variations.
    """
    # Normalize inputs: strip whitespace. Do not uppercase as LaTeX is case-sensitive.
    user_answer_norm = user_answer.strip()
    correct_answer_norm = correct_answer.strip()

    is_correct = False

    # 1. Try to parse and compare as equations
    ca_eq_parsed = _parse_equation_string(correct_answer_norm)
    ua_eq_parsed = _parse_equation_string(user_answer_norm)

    if ca_eq_parsed and ua_eq_parsed:
        # Compare (x_denominator, y_denominator) tuples using a tolerance for floats
        if abs(ca_eq_parsed[0] - ua_eq_parsed[0]) < 1e-9 and \
           abs(ca_eq_parsed[1] - ua_eq_parsed[1]) < 1e-9:
            is_correct = True
    
    # 2. If not an equation match, try to parse and compare as coordinate sets
    if not is_correct:
        ca_coords_parsed = _parse_coords_to_set_for_check(correct_answer_norm)
        ua_coords_parsed = _parse_coords_to_set_for_check(user_answer_norm)
        
        if ca_coords_parsed and ua_coords_parsed: # Ensure both parsed successfully and are not empty
            # Compare the frozensets of (x,y) tuples
            if ca_coords_parsed == ua_coords_parsed:
                is_correct = True

    # 3. Fallback to exact string match if specific parsing/comparisons fail
    if not is_correct:
        if user_answer_norm == correct_answer_norm:
            is_correct = True

    result_text = f"完全正確！答案是 ${correct_answer_norm}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer_norm}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}