import random
import re
import math # For math.gcd in Python 3.5+

# Helper function to format an equation Ax + By + C = 0 into a string
# E.g., (2, 3, 6) -> "2x+3y+6=0"
# (1, -2, -4) -> "x-2y-4=0"
# (1, 0, -5) -> "x-5=0"
# (0, 1, 3) -> "y+3=0"
# (-1, 1, 0) -> "-x+y=0"
def _format_equation(A, B, C):
    parts = []
    
    # Handle Ax term
    if A != 0:
        if A == 1:
            parts.append("x")
        elif A == -1:
            parts.append("-x")
        else:
            parts.append(f"{A}x")
    
    # Handle By term
    if B != 0:
        if B == 1:
            if parts: # If previous term (Ax) exists
                parts.append("+y")
            else:
                parts.append("y")
        elif B == -1:
            parts.append("-y")
        else: # B != 1 and B != -1
            if B > 0:
                if parts: # If previous term (Ax) exists
                    parts.append(f"+{B}y")
                else:
                    parts.append(f"{B}y")
            else: # B < 0
                parts.append(f"{B}y")
                
    # Handle C term
    if C != 0:
        if C > 0:
            if parts: # If previous term (Ax or By) exists
                parts.append(f"+{C}")
            else:
                parts.append(f"{C}")
        else: # C < 0
            parts.append(f"{C}")
            
    if not parts: # This should ideally not happen for a valid line (A and B cannot both be 0)
        return "0=0" # Fallback, though generation logic prevents A=0, B=0
    
    return "".join(parts) + "=0"

# Helper function to parse an equation string and normalize its coefficients (A, B, C)
# Normalization: divide by GCD and make the first non-zero coefficient positive.
def _parse_and_normalize_equation(equation_str):
    # Remove all spaces for easier parsing
    equation_str = equation_str.replace(" ", "")
    
    # Remove "=0" if present, for more flexible parsing of user input
    equation_str = equation_str.split("=0")[0]

    # Robust regex to capture Ax, By, and C terms.
    # It handles cases like "x", "-x", "2x", "y", "-y", "3y", "5", "-5",
    # and combinations like "x+y", "x-5", "y+3", "-x-y-1".
    match = re.match(r"([-+]?\d*x)?([-+]?\d*y)?([-+]?\d+)?$", equation_str)
    
    if not match:
        return None, None, None # Invalid format

    ax_str, by_str, c_str = match.groups()

    A, B, C = 0, 0, 0

    if ax_str:
        if ax_str == "x": A = 1
        elif ax_str == "-x": A = -1
        else: A = int(ax_str[:-1]) # remove 'x', parse integer
    
    if by_str:
        if by_str == "y": B = 1
        elif by_str == "-y": B = -1
        else: B = int(by_str[:-1]) # remove 'y', parse integer
            
    if c_str:
        C = int(c_str)

    # If A and B are both zero, it's not a valid line equation (e.g., "5=0" or just "0")
    if A == 0 and B == 0:
        return None, None, None
    
    # Calculate GCD of absolute values of A, B, C.
    # math.gcd(x, 0) == abs(x), so this handles cases where C is 0 correctly.
    common_divisor = abs(math.gcd(A, math.gcd(B, C)))
    
    # Avoid division by zero if A, B, C are all 0 (though checked above, defensive programming)
    if common_divisor == 0:
        common_divisor = 1
    
    A = A // common_divisor
    B = B // common_divisor
    C = C // common_divisor
    
    # Ensure canonical form: the first non-zero coefficient is positive.
    # If A is negative, or A is zero and B is negative, negate all coefficients.
    if A < 0 or (A == 0 and B < 0):
        A, B, C = -A, -B, -C
        
    return A, B, C

# Generates random coefficients for Ax + By + C = 0
def _generate_coefficients(level):
    if level == 1:
        A_choices = [-2, -1, 1, 2]
        B_choices = [-2, -1, 1, 2]
        C_range = [-5, 5]
    else: # level 2 and up
        A_choices = [-3, -2, -1, 0, 1, 2, 3] # Allow A or B to be 0 for level 2+
        B_choices = [-3, -2, -1, 0, 1, 2, 3]
        C_range = [-10, 10]

    A = random.choice(A_choices)
    B = random.choice(B_choices)
    
    # Ensure A and B are not both zero (must be a line)
    while A == 0 and B == 0:
        A = random.choice(A_choices)
        B = random.choice(B_choices)
        
    C = random.randint(C_range[0], C_range[-1])
    
    return A, B, C

# Generates random horizontal and vertical shifts
def _generate_shifts(level):
    if level == 1:
        shift_vals = [-2, -1, 1, 2] # Exclude 0
    else: # level 2 and up
        shift_vals = [-3, -2, -1, 1, 2, 3] # Exclude 0
    
    h_shift = random.choice(shift_vals)
    v_shift = random.choice(shift_vals)
    
    return h_shift, v_shift

# Generates a descriptive string for a shift (e.g., "往左平移3單位")
def _get_shift_description(shift_val, is_horizontal):
    abs_shift = abs(shift_val)
    if is_horizontal:
        direction = "右" if shift_val > 0 else "左"
        return f"往{direction}平移${{{abs_shift}}}$單位"
    else: # is_vertical
        direction = "上" if shift_val > 0 else "下"
        return f"往{direction}平移${{{abs_shift}}}$單位"

def generate(level=1):
    """
    生成「直線平移」相關題目。
    包含：
    1. 給定原始直線和平移量，求平移後的直線方程式。
    2. 給定平移後的直線和平移量，求原始直線方程式。
    """
    problem_type = random.choice(['forward', 'reverse']) # 'forward': original -> translated; 'reverse': translated -> original

    A, B, C = _generate_coefficients(level)
    h_shift, v_shift = _generate_shifts(level)

    # Calculate the constant term of the *translated* line based on original A, B, C and shifts
    # Original line: Ax + By + C = 0
    # Translated by (h_shift, v_shift): A(x - h_shift) + B(y - v_shift) + C = 0
    # This simplifies to Ax + By + (C - A*h_shift - B*v_shift) = 0
    C_translated = C - A * h_shift - B * v_shift

    question_text = ""
    
    # Initialize the coefficients for the *correct answer*
    correct_A_val, correct_B_val, correct_C_val = A, B, C 

    if problem_type == 'forward':
        # Problem Type 1: Given original line, find translated line
        original_equation_str = _format_equation(A, B, C)
        
        h_desc = _get_shift_description(h_shift, is_horizontal=True)
        v_desc = _get_shift_description(v_shift, is_horizontal=False)

        # Construct the question text using f-string with double curly braces for LaTeX variables
        question_text = f"將直線 ${{original_equation_str}}$ {h_desc}，再{v_desc}。求平移後的直線方程式。"
        
        # The correct answer is the translated line's coefficients
        correct_A_val = A
        correct_B_val = B
        correct_C_val = C_translated
        
    else: # problem_type == 'reverse'
        # Problem Type 2: Given translated line, find original line L
        # The given translated line has coefficients A, B, C_translated
        translated_equation_str = _format_equation(A, B, C_translated)

        # For reverse problem, the question describes a shift, but to find the original line,
        # we effectively apply the *inverse* of that shift to the given translated line.
        # Inverse shift of (h_shift, v_shift) is (-h_shift, -v_shift).
        # Applying inverse shift to A*x + B*y + C_translated = 0:
        # A(x - (-h_shift)) + B(y - (-v_shift)) + C_translated = 0
        # A(x + h_shift) + B(y + v_shift) + C_translated = 0
        # A*x + B*y + (C_translated + A*h_shift + B*v_shift) = 0
        # Note: (C_translated + A*h_shift + B*v_shift) simplifies back to C.
        
        h_desc = _get_shift_description(h_shift, is_horizontal=True)
        v_desc = _get_shift_description(v_shift, is_horizontal=False)

        question_text = f"將直線$L$ {h_desc}，再{v_desc}後，所得的直線為 ${{translated_equation_str}}$。求直線$L$的方程式。"
        
        # The correct answer is the original line's coefficients
        correct_A_val = A
        correct_B_val = B
        correct_C_val = C # The initial C value

    # Normalize the coefficients for the correct answer to a canonical form
    # This step ensures consistent representation for comparison and display
    normalized_correct_A, normalized_correct_B, normalized_correct_C = \
        _parse_and_normalize_equation(_format_equation(correct_A_val, correct_B_val, correct_C_val))
    
    # Format the canonical correct answer into a string
    correct_answer_str = _format_equation(normalized_correct_A, normalized_correct_B, normalized_correct_C)

    return {
        "question_text": question_text,
        "answer": correct_answer_str,
        "correct_answer": correct_answer_str
    }

def check(user_answer, correct_answer):
    """
    檢查使用者答案是否正確。
    解析使用者答案和正確答案，將其標準化為 (A, B, C) 係數元組後進行比較。
    """
    user_A, user_B, user_C = _parse_and_normalize_equation(user_answer)
    correct_A, correct_B, correct_C = _parse_and_normalize_equation(correct_answer)
    
    # If parsing the user's answer failed, it means the format was incorrect.
    if user_A is None or user_B is None or user_C is None:
        result_text = "您的答案格式不正確，請確保答案為 $Ax+By+C=0$ 的形式 (例如 $x+2y-3=0$ 或 $x-5=0$ 等)。"
        return {"correct": False, "result": result_text, "next_question": False}
        
    is_correct = (user_A == correct_A and user_B == correct_B and user_C == correct_C)
    
    result_text = f"完全正確！答案是 ${{correct_answer}}$。" if is_correct else f"答案不正確。正確答案應為：${{correct_answer}}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}