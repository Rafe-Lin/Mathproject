import random
from fractions import Fraction

# Helper to format a number (integer or fraction) into a LaTeX string
def format_number(num):
    if isinstance(num, Fraction):
        if num.denominator == 1:
            return str(num.numerator)
        if num < 0:
            return r"-\\frac{{{}}}{{{}}}".format(abs(num.numerator), num.denominator)
        return r"\\frac{{{}}}{{{}}}".format(num.numerator, num.denominator)
    return str(num) # Should ideally be an integer if not Fraction

# Helper to format coordinates (x, y) into a LaTeX string
def format_point(x, y):
    x_str = format_number(x)
    y_str = format_number(y)
    return f"({x_str}, {y_str})"

# Helper to format a parabola equation in standard form into a LaTeX string
# (x-h)^2 = 4c(y-k) or (y-k)^2 = 4c(x-h)
def format_parabola_equation_str(h, k, c, axis_type):
    # Left side (squared term)
    if axis_type == 'vertical': # (x-h)^2 = 4c(y-k)
        if h == 0:
            lhs = r"x^{{2}}"
        elif h > 0:
            lhs = r"(x-{})^2".format(format_number(h))
        else: # h < 0
            lhs = r"(x+{})^2".format(format_number(abs(h)))
        
        # Right side (linear term)
        four_c_val = 4 * c
        
        # Determine the coefficient for the linear term (4c).
        # Special handling for 1 and -1 to avoid '1y' or '-1y' and just show 'y' or '-y'.
        if four_c_val == 1:
            four_c_str_prefix = ""
        elif four_c_val == -1:
            four_c_str_prefix = "-"
        else:
            four_c_str_prefix = format_number(four_c_val)

        if k == 0:
            rhs_linear_term = "y"
        elif k > 0:
            rhs_linear_term = r"(y-{})".format(format_number(k))
        else: # k < 0
            rhs_linear_term = r"(y+{})".format(format_number(abs(k)))
            
        rhs = f"{four_c_str_prefix}{rhs_linear_term}"
        return f"{lhs} = {rhs}"

    else: # horizontal (y-k)^2 = 4c(x-h)
        if k == 0:
            lhs = r"y^{{2}}"
        elif k > 0:
            lhs = r"(y-{})^2".format(format_number(k))
        else: # k < 0
            lhs = r"(y+{})^2".format(format_number(abs(k)))
        
        # Right side (linear term)
        four_c_val = 4 * c
        
        if four_c_val == 1:
            four_c_str_prefix = ""
        elif four_c_val == -1:
            four_c_str_prefix = "-"
        else:
            four_c_str_prefix = format_number(four_c_val)
        
        if h == 0:
            rhs_linear_term = "x"
        elif h > 0:
            rhs_linear_term = r"(x-{})".format(format_number(h))
        else: # h < 0
            rhs_linear_term = r"(x+{})".format(format_number(abs(h)))
            
        rhs = f"{four_c_str_prefix}{rhs_linear_term}"
        return f"{lhs} = {rhs}"

# Helper to get vertex, focus, and directrix from h, k, c, axis_type
def get_parabola_properties(h, k, c, axis_type):
    vertex = (h, k)
    if axis_type == 'vertical': # (x-h)^2 = 4c(y-k)
        focus = (h, k + c)
        directrix = f"y = {format_number(k - c)}"
    else: # horizontal (y-k)^2 = 4c(x-h)
        focus = (h + c, k)
        directrix = f"x = {format_number(h - c)}"
    return {"vertex": vertex, "focus": focus, "directrix": directrix}


def generate(level=1):
    """
    生成「拋物線的標準式與一般式」相關題目。
    """
    problem_type = random.choice([
        'find_equation_vertex_focus',       # 給定頂點和焦點，求方程式
        'find_equation_vertex_directrix',   # 給定頂點和準線，求方程式
        'find_equation_focus_directrix',    # 給定焦點和準線，求方程式
        'find_properties_from_std_form',    # 給定標準式，求頂點、焦點、準線
        'find_properties_from_general_form' # 給定一般式，求頂點、焦點、準線
    ])

    # Generate h, k, c values, ensuring they are Fractions to prevent float issues
    # Level influences complexity (larger range, potential for fractions)
    h_int, k_int = random.randint(-5, 5), random.randint(-5, 5)
    c_int = random.choice([-3, -2, -1, 1, 2, 3]) # Ensure c is not zero

    h, k, c_val = Fraction(h_int), Fraction(k_int), Fraction(c_int)
    
    axis_type = random.choice(['vertical', 'horizontal'])

    if level >= 2:
        h_int, k_int = random.randint(-8, 8), random.randint(-8, 8)
        c_int = random.choice([-4, -3, -2, -1, 1, 2, 3, 4])
        h, k, c_val = Fraction(h_int), Fraction(k_int), Fraction(c_int)

    if level == 3:
        # Introduce fractions for c, h, k
        if random.random() < 0.6: # 60% chance for c to be a fraction
            c_val = Fraction(random.choice([-5, -3, -2, 2, 3, 5]), random.choice([2, 3, 4]))
        if random.random() < 0.4: # 40% chance for h to be a fraction
            h = Fraction(random.randint(-10, 10), random.choice([2, 3, 4]))
        if random.random() < 0.4: # 40% chance for k to be a fraction
            k = Fraction(random.randint(-10, 10), random.choice([2, 3, 4]))

    # Calculate core properties using the generated h, k, c_val
    properties = get_parabola_properties(h, k, c_val, axis_type)
    vertex_coords = properties["vertex"]
    focus_coords = properties["focus"]
    directrix_eq_str = properties["directrix"] # This is already a formatted string like "y = N" or "x = N"
    
    vertex_str = format_point(vertex_coords[0], vertex_coords[1])
    focus_str = format_point(focus_coords[0], focus_coords[1])
    
    question_text = ""
    correct_answer = ""

    if problem_type == 'find_equation_vertex_focus':
        question_text = f"求滿足下列條件的拋物線方程式：頂點為 ${vertex_str}$，焦點為 ${focus_str}$。"
        correct_answer = format_parabola_equation_str(h, k, c_val, axis_type)

    elif problem_type == 'find_equation_vertex_directrix':
        # Directrix equation is already formatted from get_parabola_properties
        question_text = f"求滿足下列條件的拋物線方程式：頂點為 ${vertex_str}$，準線為 ${directrix_eq_str}$。"
        correct_answer = format_parabola_equation_str(h, k, c_val, axis_type)
    
    elif problem_type == 'find_equation_focus_directrix':
        # For this problem type, h, k, c_val are *derived* from the given focus and directrix.
        # This ensures the generated problem is consistent.
        # We use the previously computed properties to *present* the problem,
        # but the answer calculation is based on re-deriving h,k,c from the presented F and D.
        
        # Get actual focus and directrix values for the problem statement
        actual_focus_x, actual_focus_y = focus_coords[0], focus_coords[1]
        
        if axis_type == 'vertical':
            # Directrix is y = D, so extract D. The D_val is (k-c_val)
            D_val = k - c_val 
            # Re-derive h,k,c from these values (actual_focus_x, actual_focus_y, D_val)
            h_derived = actual_focus_x
            k_derived = Fraction(actual_focus_y + D_val, 2)
            c_derived = actual_focus_y - k_derived
            
            question_text = f"求滿足下列條件的拋物線方程式：焦點為 ${focus_str}$，準線為 ${directrix_eq_str}$。"
            correct_answer = format_parabola_equation_str(h_derived, k_derived, c_derived, axis_type)

        else: # horizontal
            # Directrix is x = D, so extract D. The D_val is (h-c_val)
            D_val = h - c_val
            # Re-derive h,k,c from these values (actual_focus_x, actual_focus_y, D_val)
            k_derived = actual_focus_y
            h_derived = Fraction(actual_focus_x + D_val, 2)
            c_derived = actual_focus_x - h_derived
            
            question_text = f"求滿足下列條件的拋物線方程式：焦點為 ${focus_str}$，準線為 ${directrix_eq_str}$。"
            correct_answer = format_parabola_equation_str(h_derived, k_derived, c_derived, axis_type)

    elif problem_type == 'find_properties_from_std_form':
        equation_str = format_parabola_equation_str(h, k, c_val, axis_type)
        question_text = f"求拋物線方程式 ${equation_str}$ 的頂點、焦點與準線方程式。"
        
        answer_parts = []
        answer_parts.append(f"頂點: ${vertex_str}$")
        answer_parts.append(f"焦點: ${focus_str}$")
        answer_parts.append(f"準線方程式: ${directrix_eq_str}$")
        correct_answer = "; ".join(answer_parts)
    
    elif problem_type == 'find_properties_from_general_form':
        # Convert standard form to general form.
        # (x-h)^2 = 4c(y-k)  => x^2 - 2hx + h^2 = 4cy - 4ck => x^2 - 2hx - 4cy + h^2 + 4ck = 0
        # (y-k)^2 = 4c(x-h)  => y^2 - 2ky + k^2 = 4cx - 4ch => y^2 - 2ky - 4cx + k^2 + 4ch = 0

        # General form coefficients for x^2 + Dx + Ey + F = 0 or y^2 + Dx + Ey + F = 0
        gen_D, gen_E, gen_F = Fraction(0), Fraction(0), Fraction(0)

        if axis_type == 'vertical': # x^2 + Dx + Ey + F = 0
            # Standard form (x-h)^2 = 4c(y-k)
            # Expand: x^2 - 2hx + h^2 = 4cy - 4ck
            # Rearrange: x^2 + (-2h)x + (-4c)y + (h^2 + 4ck) = 0
            gen_D = -2 * h
            gen_E = -4 * c_val
            gen_F = h * h + 4 * c_val * k
            
            eq_terms = []
            eq_terms.append(r"x^{{2}}")
            if gen_D != 0:
                eq_terms.append(f"{'+' if gen_D > 0 else '-'}{abs(format_number(gen_D))}x")
            if gen_E != 0:
                eq_terms.append(f"{'+' if gen_E > 0 else '-'}{abs(format_number(gen_E))}y")
            if gen_F != 0:
                eq_terms.append(f"{'+' if gen_F > 0 else '-'}{abs(format_number(gen_F))}")
            
            question_text = f"求拋物線方程式 ${' '.join(eq_terms).replace('+-', '-').replace('--', '+')} = 0$ 的頂點、焦點與準線方程式。"
            
        else: # horizontal: y^2 + Dx + Ey + F = 0
            # Standard form (y-k)^2 = 4c(x-h)
            # Expand: y^2 - 2ky + k^2 = 4cx - 4ch
            # Rearrange: y^2 + (-4c)x + (-2k)y + (k^2 + 4ch) = 0
            gen_D = -4 * c_val # coefficient of x
            gen_E = -2 * k    # coefficient of y
            gen_F = k * k + 4 * c_val * h

            eq_terms = []
            eq_terms.append(r"y^{{2}}")
            if gen_E != 0: # y term first after y^2, matches example style (y^2-4y+2x-4=0)
                eq_terms.append(f"{'+' if gen_E > 0 else '-'}{abs(format_number(gen_E))}y")
            if gen_D != 0: # x term after y term
                eq_terms.append(f"{'+' if gen_D > 0 else '-'}{abs(format_number(gen_D))}x")
            if gen_F != 0:
                eq_terms.append(f"{'+' if gen_F > 0 else '-'}{abs(format_number(gen_F))}")
            
            question_text = f"求拋物線方程式 ${' '.join(eq_terms).replace('+-', '-').replace('--', '+')} = 0$ 的頂點、焦點與準線方程式。"

        # Answer is the same as 'find_properties_from_std_form' after conversion
        answer_parts = []
        answer_parts.append(f"頂點: ${vertex_str}$")
        answer_parts.append(f"焦點: ${focus_str}$")
        answer_parts.append(f"準線方程式: ${directrix_eq_str}$")
        correct_answer = "; ".join(answer_parts)
    
    return {
        "question_text": question_text,
        "answer": correct_answer, # Store the canonical answer
        "correct_answer": correct_answer # Also store it as correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    # Normalize user answer and correct answer for robust comparison
    # This involves removing spaces, converting to lowercase, and standardizing fraction/negative sign representations.
    
    def normalize_string(s):
        s = s.strip().replace(" ", "").lower()
        # Standardize LaTeX fraction negative signs: -\\frac{a}{b} vs \\frac{-a}{b}
        s = s.replace(r"\\frac{-", r"-\\frac{") 
        # Handle cases like x^2+1y=0 -> x^2+y=0
        s = s.replace("1x", "x").replace("1y", "y")
        # Ensure proper use of double braces for LaTeX commands with arguments if user input has single
        s = s.replace(r"\\frac{", r"\\frac{{") # Add { to start of numerator
        s = s.replace("}{", "}}{{") # Add { between num and den
        s = s.replace("}}", "}}") # Ensure closing brace is there
        return s

    user_answer_cleaned = normalize_string(user_answer)
    correct_answer_cleaned = normalize_string(correct_answer)
    
    is_correct = (user_answer_cleaned == correct_answer_cleaned)

    # For this skill, answers are complex algebraic strings, not simple numbers.
    # Therefore, the float comparison logic from the template is not applicable.

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}