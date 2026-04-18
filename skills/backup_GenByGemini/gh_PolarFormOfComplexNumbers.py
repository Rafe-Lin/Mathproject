import random
import math
import cmath
from fractions import Fraction
import re

# Global dict for common angles in degrees and their exact (cos, sin) values.
COMMON_ANGLE_DATA = [
    {"deg": 0,   "rad": 0,           "cos": 1,          "sin": 0},
    {"deg": 30,  "rad": math.pi/6,   "cos": math.sqrt(3)/2, "sin": 0.5},
    {"deg": 45,  "rad": math.pi/4,   "cos": math.sqrt(2)/2, "sin": math.sqrt(2)/2},
    {"deg": 60,  "rad": math.pi/3,   "cos": 0.5,        "sin": math.sqrt(3)/2},
    {"deg": 90,  "rad": math.pi/2,   "cos": 0,          "sin": 1},
    {"deg": 120, "rad": 2*math.pi/3, "cos": -0.5,       "sin": math.sqrt(3)/2},
    {"deg": 135, "rad": 3*math.pi/4, "cos": -math.sqrt(2)/2, "sin": math.sqrt(2)/2},
    {"deg": 150, "rad": 5*math.pi/6, "cos": -math.sqrt(3)/2, "sin": 0.5},
    {"deg": 180, "rad": math.pi,     "cos": -1,         "sin": 0},
    {"deg": 210, "rad": 7*math.pi/6, "cos": -math.sqrt(3)/2, "sin": -0.5},
    {"deg": 225, "rad": 5*math.pi/4, "cos": -math.sqrt(2)/2, "sin": -math.sqrt(2)/2},
    {"deg": 240, "rad": 4*math.pi/3, "cos": -0.5,       "sin": -math.sqrt(3)/2},
    {"deg": 270, "rad": 3*math.pi/2, "cos": 0,          "sin": -1},
    {"deg": 300, "rad": 5*math.pi/3, "cos": 0.5,        "sin": -math.sqrt(3)/2},
    {"deg": 315, "rad": 7*math.pi/4, "cos": math.sqrt(2)/2, "sin": -math.sqrt(2)/2},
    {"deg": 330, "rad": 11*math.pi/6,"cos": math.sqrt(3)/2, "sin": -0.5},
]

# Helper function to parse LaTeX-like numeric strings (e.g., "\\sqrt{3}", "\\frac{1}{2}")
def _parse_latex_num_string(s):
    if not s: return 0.0
    s = s.strip().replace(' ', '').replace('+-', '-')
    s = s.replace(r'\\sqrt', 'math.sqrt').replace(r'\\frac', 'Fraction').replace('{', '(').replace('}', ')').replace(r'\\pi', 'math.pi')
    try:
        return float(eval(s, {'math': math, 'Fraction': Fraction}))
    except (ValueError, SyntaxError, TypeError, NameError):
        return None

# Helper function to parse user input string into a complex number
def _parse_complex_input(user_input):
    user_input_clean = user_input.strip().replace(' ', '').lower()
    
    # 1. Try Python's built-in complex() constructor for simple forms (a+bi, a-bi, bi, -bi, a, i, -i)
    try:
        if user_input_clean == 'i': return complex(0, 1)
        if user_input_clean == '-i': return complex(0, -1)
        # Python uses 'j' for imaginary unit in complex literals
        return complex(user_input_clean.replace('i', 'j'))
    except ValueError:
        pass # Not a simple a+bi form

    # 2. Try parsing a+bi form with LaTeX sqrt/fraction
    match_rect_latex = re.fullmatch(
        r"^\$?(?:([+-]?\S*(?:\\sqrt{\d+})?(?:\\frac{\S*(?:\\sqrt{\d+})?}{\S+})?)(?:([+-])(\S*(?:\\sqrt{\d+})?(?:\\frac{\S*(?:\\sqrt{\d+})?}{\S+})?)i)?|([+-]?\S*(?:\\sqrt{\d+})?(?:\\frac{\S*(?:\\sqrt{\d+})?}{\S+})?)i)\$?",
        user_input.strip()
    )
    if match_rect_latex:
        real_str, op_str, imag_val_str, pure_imag_str = match_rect_latex.groups()
        
        real_part = 0.0
        imag_part = 0.0

        if pure_imag_str: # Purely imaginary (e.g., "i", "-i", "2\\sqrt{3}i")
            imag_part = _parse_latex_num_string(pure_imag_str)
            if imag_part is None: return None
        elif real_str: # Real part exists
            real_part = _parse_latex_num_string(real_str)
            if real_part is None: return None
            if imag_val_str: # Imaginary part also exists
                imag_part_val = _parse_latex_num_string(imag_val_str)
                if imag_part_val is None: return None
                if op_str == '-':
                    imag_part = -imag_part_val
                else: # Default or explicit '+'
                    imag_part = imag_part_val
        return complex(real_part, imag_part)

    # 3. Try parsing polar form: r(cosθ+isinθ) or similar with LaTeX
    match_polar_latex = re.fullmatch(r"^\$?(?:(\S*))\s*\(\s*cos\s*(\S+)\s*(?:°|\\circ)?\s*\+\s*i\s*sin\s*(\S+)\s*(?:°|\\circ)?\s*\)\$?", user_input.strip())
    if match_polar_latex:
        try:
            r_str_polar, cos_angle_str_polar, sin_angle_str_polar = match_polar_latex.groups()
            
            r_val_polar = 1.0
            if r_str_polar:
                r_val_polar = _parse_latex_num_string(r_str_polar)
                if r_val_polar is None: return None
            
            # Assume cos and sin angles are the same
            angle_str_polar = cos_angle_str_polar
            
            # Determine if radians or degrees from string content
            is_radians = 'pi' in angle_str_polar or 'rad' in user_input.lower()
            angle_val_polar = _parse_latex_num_string(angle_str_polar)
            if angle_val_polar is None: return None

            if is_radians:
                angle_deg_polar = math.degrees(angle_val_polar)
            else:
                angle_deg_polar = angle_val_polar

            return polar_to_complex(r_val_polar, angle_deg_polar)
        except (ValueError, SyntaxError, TypeError, NameError):
            pass

    # 4. Try parsing (x,y) coordinates for geometric problems
    match_coords = re.fullmatch(r"^\$?\(\s*([+-]?\S*(?:\\sqrt{\d+})?(?:\\frac{\S*(?:\\sqrt{\d+})?}{\S+})?)\s*,\s*([+-]?\S*(?:\\sqrt{\d+})?(?:\\frac{\S*(?:\\sqrt{\d+})?}{\S+})?)\s*\)\$?", user_input.strip())
    if match_coords:
        x_str, y_str = match_coords.groups()
        x_val = _parse_latex_num_string(x_str)
        y_val = _parse_latex_num_string(y_str)
        if x_val is not None and y_val is not None:
            return complex(x_val, y_val)
    
    return None # Failed to parse

# Helper function to format a number, possibly with sqrt or fractions
def format_num_with_sqrt(val):
    if math.isclose(val, 0):
        return "0"
    
    sign_str = "-" if val < 0 else ""
    abs_val = abs(val)

    # Check for integer
    if abs_val.is_integer():
        return f"{sign_str}{int(abs_val)}"
    
    # Check for N*sqrt(S)
    for s_val in [2, 3, 5, 7]:
        sqrt_s = math.sqrt(s_val)
        if not math.isclose(sqrt_s, 0):
            coeff = abs_val / sqrt_s
            if coeff.is_integer() and coeff != 0:
                coeff_int = int(coeff)
                if coeff_int == 1:
                    return f"{sign_str}\\sqrt{{{s_val}}}"
                return f"{sign_str}{coeff_int}\\sqrt{{{s_val}}}"

    # Check for (N*sqrt(S))/D or N/D
    # Prioritize N*sqrt(S)/D for common sqrt values
    for s_val in [2, 3]: # Check for sqrt(2) or sqrt(3) in fraction forms
        sqrt_s = math.sqrt(s_val)
        if not math.isclose(sqrt_s, 0):
            for denom in [2, 3, 4, 5, 6, 8]: # Common denominators
                num_part = abs_val * denom
                coeff = num_part / sqrt_s
                if coeff.is_integer() and coeff != 0:
                    coeff_int = int(coeff)
                    if coeff_int == 1:
                        return f"{sign_str}\\frac{{\\sqrt{{{s_val}}}}}{{{denom}}}"
                    return f"{sign_str}\\frac{{{coeff_int}\\sqrt{{{s_val}}}}}{{{denom}}}"
    
    # Fallback to simple rational fraction if no sqrt is involved
    frac_val = Fraction(abs_val).limit_denominator(1000)
    if frac_val.denominator != 1:
        return f"{sign_str}\\frac{{{frac_val.numerator}}}{{{frac_val.denominator}}}"
        
    # Default to float with reasonable precision if no exact representation found
    return f"{sign_str}{abs_val:.4f}".rstrip('0').rstrip('.')

# Helper function to format a complex number a+bi
def format_complex_rectangular(a, b):
    a_str = format_num_with_sqrt(a)
    b_str = format_num_with_sqrt(b)

    if math.isclose(b, 0): # Purely real
        return f"${{{a_str}}}$"
    elif math.isclose(a, 0): # Purely imaginary
        if math.isclose(b, 1):
            return "$i$"
        elif math.isclose(b, -1):
            return "$-i$"
        return f"${{{b_str}}}i$"
    else: # a+bi form
        op = "+" if b > 0 else "-"
        abs_b_str = format_num_with_sqrt(abs(b))
        if math.isclose(abs(b), 1):
            return f"${{{a_str}}}{op}i$"
        return f"${{{a_str}}}{op}{{{abs_b_str}}}i$"

# Helper function to format a complex number r(cosθ + i sinθ)
def format_complex_polar(r, theta_deg, format_type='degrees'):
    r_str = format_num_with_sqrt(r)
    
    if format_type == 'radians':
        theta_rad = math.radians(theta_deg)
        # Find a common denominator for fractions of pi
        theta_str = f"{theta_rad:.4f}" # Fallback
        for denom in [1, 2, 3, 4, 6]:
            coeff = round(theta_rad / (math.pi / denom))
            if math.isclose(theta_rad, coeff * math.pi / denom):
                if coeff == 0:
                    theta_str = "0"
                elif coeff == 1 and denom == 1:
                    theta_str = "\\pi"
                elif coeff == 1:
                    theta_str = f"\\frac{{\\pi}}{{{denom}}}"
                elif denom == 1:
                    theta_str = f"{coeff}\\pi"
                else:
                    theta_str = f"\\frac{{{coeff}\\pi}}{{{denom}}}"
                break
        
        if r_str == "1":
            return f"$(cos{{{theta_str}}} + i sin{{{theta_str}}})$"
        return f"${{{r_str}}}(cos{{{theta_str}}} + i sin{{{theta_str}}})$"
    else: # degrees
        if r_str == "1":
            return f"$(cos{{{theta_deg}}}^{{\\circ}} + i sin{{{theta_deg}}}^{{\\circ}})$"
        return f"${{{r_str}}}(cos{{{theta_deg}}}^{{\\circ}} + i sin{{{theta_deg}}}^{{\\circ}})$"

# Convert polar to complex(a+bi)
def polar_to_complex(r, theta_deg):
    theta_rad = math.radians(theta_deg)
    return complex(r * math.cos(theta_rad), r * math.sin(theta_rad))

# Convert complex(a+bi) to polar (r, theta_deg)
def complex_to_polar(z):
    r = abs(z)
    theta_rad = cmath.phase(z)
    theta_deg = math.degrees(theta_rad)
    # Ensure 0 <= theta_deg < 360
    theta_deg = theta_deg % 360
    if theta_deg < 0:
        theta_deg += 360
    return r, theta_deg

# Round to nearest common angle if very close
def round_to_nearest_common_angle(theta_deg):
    for angle_data in COMMON_ANGLE_DATA:
        if abs(theta_deg - angle_data["deg"]) < 1e-6: # Within a very small tolerance
            return angle_data["deg"]
    return theta_deg


def generate_to_polar_problem():
    """將 z=a+bi 轉換為極式 z=r(cosθ + i sinθ)"""
    angle_data = random.choice(COMMON_ANGLE_DATA)
    theta_deg = angle_data["deg"]

    r_options = [random.randint(1, 5)]
    # Add sqrt(2) or 2*sqrt(3) multipliers for r to generate common a, b values
    if theta_deg % 90 != 0: 
        if random.random() < 0.5:
            r_options.append(math.sqrt(2) * random.randint(1,2))
        else:
            r_options.append(2 * random.randint(1,3)) 
    r_val = random.choice(r_options)
    
    a = r_val * angle_data["cos"]
    b = r_val * angle_data["sin"]

    # Normalize a,b to integers or exact sqrt forms due to float precision
    if math.isclose(a, 0): a = 0
    if math.isclose(b, 0): b = 0
    if math.isclose(a, round(a)): a = round(a)
    if math.isclose(b, round(b)): b = round(b)

    # Recalculate r and theta from the (possibly corrected) a,b to ensure consistency
    z_complex = complex(a,b)
    r_actual, calculated_theta_deg = complex_to_polar(z_complex)
    theta_actual = round_to_nearest_common_angle(calculated_theta_deg)

    z_rect_str = format_complex_rectangular(a, b)
    
    format_type = random.choice(['degrees', 'radians'])
    if format_type == 'radians':
        question_text = f"將複數 ${{z}} = {{{z_rect_str}}}$ 表為極式（輻角取主輻角，以弧度表示）。"
    else:
        question_text = f"將複數 ${{z}} = {{{z_rect_str}}}$ 表為極式（輻角取主輻角）。"
        
    correct_polar_str = format_complex_polar(r_actual, theta_actual, format_type)

    return {
        "question_text": question_text,
        "answer": correct_polar_str,
        "correct_answer": z_complex
    }

def generate_standardize_polar_problem():
    """將非標準極式轉換為標準極式 r(cosθ + i sinθ)"""
    angle_data = random.choice(COMMON_ANGLE_DATA)
    r = random.randint(1, 5)

    initial_theta_deg = angle_data["deg"]
    
    problem_form_type = random.choice(['sin_cos', 'neg_sin', 'both_non_standard'])

    question_text_template = ""
    correct_theta_deg = 0

    if problem_form_type == 'sin_cos':
        # r(sinθ' + i cosθ') -> r(cos(90-θ') + i sin(90-θ'))
        offset_angle = random.choice([30, 45, 60, 90])
        display_angle = (initial_theta_deg + offset_angle) % 360
        question_text_template = r"${{{r}}}(sin{{{display_angle}}}^{{\\circ}} + i cos{{{display_angle}}}^{{\\circ}})$"
        correct_theta_deg = (90 - display_angle) % 360
        if correct_theta_deg < 0: correct_theta_deg += 360
        
    elif problem_form_type == 'neg_sin':
        # r(cosθ' - i sinθ') -> r(cos(-θ') + i sin(-θ'))
        display_angle = initial_theta_deg 
        question_text_template = r"${{{r}}}(cos{{{display_angle}}}^{{\\circ}} - i sin{{{display_angle}}}^{{\\circ}})$"
        correct_theta_deg = (-display_angle) % 360
        if correct_theta_deg < 0: correct_theta_deg += 360

    else: # 'both_non_standard': r(sinθ' - i cosθ') -> r(cos(θ'-90) + i sin(θ'-90))
        offset_angle = random.choice([30, 45, 60, 90])
        display_angle = (initial_theta_deg + offset_angle) % 360
        question_text_template = r"${{{r}}}(sin{{{display_angle}}}^{{\\circ}} - i cos{{{display_angle}}}^{{\\circ}})$"
        correct_theta_deg = (display_angle - 90) % 360
        if correct_theta_deg < 0: correct_theta_deg += 360

    question_text = f"將下列複數表為極式（輻角取主輻角）：<br>{question_text_template.format(r=format_num_with_sqrt(r), display_angle=display_angle)}"
    
    correct_polar_str = format_complex_polar(r, correct_theta_deg)
    correct_z_val = polar_to_complex(r, correct_theta_deg)

    return {
        "question_text": question_text,
        "answer": correct_polar_str,
        "correct_answer": correct_z_val
    }

def generate_polar_operation_problem():
    """複數極式的乘法與除法運算"""
    num_terms = random.choice([2, 3]) # Number of complex numbers involved (e.g., z1*z2 or z1*z2/z3)
    
    # Generate angles and moduli such that the final result is a "nice" common angle
    final_deg = -1
    while final_deg == -1 or final_deg not in [a["deg"] for a in COMMON_ANGLE_DATA]:
        terms = []
        for _ in range(num_terms):
            r = random.randint(1, 4)
            angle_data = random.choice(COMMON_ANGLE_DATA)
            terms.append({"r": r, "deg": angle_data["deg"]})
        
        # Test a sequence of operations
        current_r = 1.0
        current_deg = 0.0
        
        operations = [] # Store operations for question text
        z_complex_terms = []

        # Start with the first term
        current_r = terms[0]["r"]
        current_deg = terms[0]["deg"]
        z_complex_terms.append(polar_to_complex(current_r, current_deg))

        for i in range(1, num_terms):
            op_type = random.choice(['multiply', 'divide'])
            operations.append(op_type)
            
            term_r = terms[i]["r"]
            term_deg = terms[i]["deg"]
            z_complex_terms.append(polar_to_complex(term_r, term_deg))

            if op_type == 'multiply':
                current_r *= term_r
                current_deg += term_deg
            else: # 'divide'
                # Ensure we don't divide by zero r, which is guaranteed by randint(1,4)
                current_r /= term_r
                current_deg -= term_deg
        
        current_deg = current_deg % 360
        if current_deg < 0: current_deg += 360
        final_deg = round_to_nearest_common_angle(current_deg)

    # Construct question text with the chosen terms and operations
    question_parts = []
    
    # First term
    question_parts.append(format_complex_polar(terms[0]["r"], terms[0]["deg"]).strip('$'))
    
    correct_z_val = polar_to_complex(terms[0]["r"], terms[0]["deg"])

    for i in range(1, num_terms):
        op_type = operations[i-1]
        term_polar_str = format_complex_polar(terms[i]["r"], terms[i]["deg"]).strip('$')
        if op_type == 'multiply':
            question_parts.append(f"\\times {{{term_polar_str}}}")
            correct_z_val *= polar_to_complex(terms[i]["r"], terms[i]["deg"])
        else: # 'divide'
            # If it's division, use \\frac to group terms
            if i == 1: # First operation is division
                question_parts = [f"\\frac{{{question_parts[0]}}}{{{term_polar_str}}}"]
            else: # Subsequent division
                question_parts.append(f"\\div {{{term_polar_str}}}") # Simple div symbol is fine

            correct_z_val /= polar_to_complex(terms[i]["r"], terms[i]["deg"])
            
    question_text = f"求下列各式的值：<br>${{{''.join(question_parts)}}}$"

    # Format the answer as a+bi if it's a simple exact value, otherwise polar.
    # The example answers are often in a+bi form when simplified.
    final_r, final_deg_for_format = complex_to_polar(correct_z_val)
    
    if final_deg_for_format in [0, 90, 180, 270]: # Pure real/imaginary
        correct_answer_str = format_complex_rectangular(correct_z_val.real, correct_z_val.imag)
    elif final_deg_for_format in [30, 45, 60, 120, 135, 150, 210, 225, 240, 300, 315, 330]:
        correct_answer_str = format_complex_rectangular(correct_z_val.real, correct_z_val.imag)
    else: # Fallback to polar form
        correct_answer_str = format_complex_polar(final_r, final_deg_for_format)

    return {
        "question_text": question_text,
        "answer": correct_answer_str,
        "correct_answer": correct_z_val
    }


def generate_geometric_transform_problem():
    """幾何意義：旋轉與伸縮"""
    a = random.randint(-5, 5)
    b = random.randint(-5, 5)
    while a == 0 and b == 0: 
        a = random.randint(-5, 5)
        b = random.randint(-5, 5)
    
    z_initial = complex(a, b)
    initial_point_str = f"$A({a},{b})$"
    
    rotation_angle = random.choice([30, 45, 60, 90, 120, 135, 150, 180, 210, 225, 240, 270, 300, 315, 330])
    scaling_factor = random.choice([1, 2, 3, 0.5]) 

    if random.random() < 0.5: 
        rotation_angle *= -1
        rotation_direction = "順時針"
    else:
        rotation_direction = "逆時針"
    
    transform_z = polar_to_complex(scaling_factor, rotation_angle)
    
    z_final = z_initial * transform_z
    
    question_text = f"在複數平面上，設一點 ${{A}}$ 坐標為 $({a},{b})$。<br>"
    question_text += f"若將 ${{A}}$ 點以原點為中心，{rotation_direction}方向旋轉 ${{{abs(rotation_angle)}}}^{{\\circ}}$，"
    if scaling_factor != 1:
        question_text += f"並將其與原點的距離伸縮為 ${{{format_num_with_sqrt(scaling_factor)}}}$ 倍，"
    question_text += f"求轉換後點的坐標。"

    final_x = z_final.real
    final_y = z_final.imag

    correct_answer_str = f"$({{{format_num_with_sqrt(final_x)}}},{{{format_num_with_sqrt(final_y)}}})$"

    return {
        "question_text": question_text,
        "answer": correct_answer_str,
        "correct_answer": z_final 
    }

def generate_geometric_square_problem():
    """幾何意義：正方形性質"""
    z1_real = random.randint(-5, 5)
    z1_imag = random.randint(-5, 5)
    z1 = complex(z1_real, z1_imag)

    side_len = random.randint(1, 5)
    vector_angle_deg = random.choice([0, 30, 45, 60, 90, 120, 135, 150, 180, 210, 225, 240, 270, 300, 315, 330])
    
    z2_minus_z1 = polar_to_complex(side_len, vector_angle_deg)
    z2 = z1 + z2_minus_z1
    
    z3_minus_z2 = z2_minus_z1 * polar_to_complex(1, 90)
    z3 = z2 + z3_minus_z2
    
    z4_minus_z3 = z3_minus_z2 * polar_to_complex(1, 90)
    z4 = z3 + z4_minus_z3

    z_coords = {
        'A': z1,
        'B': z2,
        'C': z3,
        'D': z4
    }
    
    points_desc = []
    for label, z_val in z_coords.items():
        points_desc.append(f"${label}({format_complex_rectangular(z_val.real, z_val.imag).strip('$')})$")

    question_text = f"已知複數平面上的四點 {', '.join(points_desc)}，且 ${{ABCD}}$ 依逆時針方向可連成一個正方形。求下列各式的值。<br>"
    
    sub_problem_type = random.choice(['ratio_vector', 'ratio_diag_side'])

    if sub_problem_type == 'ratio_vector':
        question_expression = f"$\\frac{{z_4 - z_1}}{{z_2 - z_3}}$"
        correct_z_val = complex(-1, 0)
        correct_answer_str = "$-1$"
    else: 
        question_expression = f"$\\frac{{z_3 - z_1}}{{z_2 - z_1}}$"
        correct_z_val = polar_to_complex(math.sqrt(2), 45) 
        correct_answer_str = "$1+i$"

    question_text += f"{question_expression}"

    return {
        "question_text": question_text,
        "answer": correct_answer_str,
        "correct_answer": correct_z_val
    }

def generate(level=1):
    problem_types = [
        'to_polar',
        'standardize_polar',
        'polar_operation',
        'geometric_transform',
        'geometric_square'
    ]
    problem_type = random.choice(problem_types)
    
    if problem_type == 'to_polar':
        return generate_to_polar_problem()
    elif problem_type == 'standardize_polar':
        return generate_standardize_polar_problem()
    elif problem_type == 'polar_operation':
        return generate_polar_operation_problem()
    elif problem_type == 'geometric_transform':
        return generate_geometric_transform_problem()
    elif problem_type == 'geometric_square':
        return generate_geometric_square_problem()
    
    return generate_to_polar_problem() # Fallback

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    user_answer 可以是 a+bi 形式的字串，也可以是 r(cosθ+isinθ) 形式的字串，或 (x,y) 坐標形式。
    correct_answer 是 generate 函數返回的 complex 數字。
    """
    user_z = _parse_complex_input(user_answer)
    
    is_correct = False
    result_text = ""

    if user_z is None:
        result_text = f"你的答案格式似乎不正確，請檢查。<br>預期的格式可以是 $a+bi$ 或 $r(cos{{\\theta}}^{{\\circ}} + i sin{{\\theta}}^{{\\circ}} )$ 或 $r(cos{{\\theta}} + i sin{{\\theta}} )$。"
    else:
        if math.isclose(user_z.real, correct_answer.real, rel_tol=1e-6, abs_tol=1e-9) and \
           math.isclose(user_z.imag, correct_answer.imag, rel_tol=1e-6, abs_tol=1e-9):
            is_correct = True
            result_text = f"完全正確！答案是 ${{{format_complex_rectangular(correct_answer.real, correct_answer.imag).strip('$')}}}$。"
        else:
            result_text = f"答案不正確。正確答案應為：${{{format_complex_rectangular(correct_answer.real, correct_answer.imag).strip('$')}}}$"
            # Provide polar form as an alternative in feedback
            r_corr, deg_corr = complex_to_polar(correct_answer)
            result_text += f" (或極式 ${{{format_complex_polar(r_corr, deg_corr).strip('$')}}}$)"

    return {"correct": is_correct, "result": result_text, "next_question": True}