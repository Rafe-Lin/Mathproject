import random
import math
from fractions import Fraction
import re

# Constants for common angles and their sin/cos values
DEG_TO_RAD = math.pi / 180

# List of common angles in degrees for Phi (principal argument of the complex number 'a')
COMMON_PHIS = [
    0, 30, 45, 60, 90, 120, 135, 150, 180,
    210, 225, 240, 270, 300, 315, 330
]

# Helper function to format a real number (x or y component) into a string,
# potentially including square roots like N*sqrt(M).
def format_real_part(value, tol=1e-9):
    if math.isclose(value, 0, abs_tol=tol):
        return "0"
    if math.isclose(value, round(value), abs_tol=tol):
        return str(int(round(value)))
    
    # Check for multiples of sqrt(2)
    coeff_sqrt2 = value / math.sqrt(2)
    if math.isclose(coeff_sqrt2, round(coeff_sqrt2), abs_tol=tol):
        int_coeff = int(round(coeff_sqrt2))
        if int_coeff == 1: return r"\\sqrt{{2}}"
        if int_coeff == -1: return r"-\\sqrt{{2}}"
        return f"{int_coeff}\\sqrt{{2}}"

    # Check for multiples of sqrt(3)
    coeff_sqrt3 = value / math.sqrt(3)
    if math.isclose(coeff_sqrt3, round(coeff_sqrt3), abs_tol=tol):
        int_coeff = int(round(coeff_sqrt3))
        if int_coeff == 1: return r"\\sqrt{{3}}"
        if int_coeff == -1: return r"-\\sqrt{{3}}"
        return f"{int_coeff}\\sqrt{{3}}"
            
    # Fallback for other cases (should be rare with chosen parameters for R and Phi)
    return f"{value:.5f}" 

# Helper function to convert polar coordinates (R, Phi_deg) to a string
# in rectangular form (x+yi), handling special cases for x, y.
def format_complex_number_polar_to_rect(R, Phi_deg):
    x_val_exact = R * math.cos(math.radians(Phi_deg))
    y_val_exact = R * math.sin(math.radians(Phi_deg))

    x_str = format_real_part(x_val_exact)
    y_str = format_real_part(y_val_exact)

    if x_str == "0" and y_str == "0":
        return "0"
    
    # Handle pure imaginary numbers (e.g., "i", "-i", "2i", "-sqrt{3}i")
    if x_str == "0":
        if y_str == "1": return "i"
        if y_str == "-1": return "-i"
        if y_str.startswith('-'):
            return f"{y_str}i"
        return f"{y_str}i"

    # Handle pure real numbers (e.g., "1", "-1", "2")
    if y_str == "0":
        return x_str
    
    # Handle general complex numbers (x+yi)
    # y_str could be "1", "\\sqrt{3}", "-1", "-\\sqrt{3}", etc.
    if y_str == "1":
        return f"{x_str}+i"
    if y_str == "-1":
        return f"{x_str}-i"
    if y_str.startswith('-'):
        return f"{x_str}{y_str}i"
    return f"{x_str}+{y_str}i"


def generate(level=1):
    n = random.randint(3, 6) # N-th root: 3rd, 4th, 5th, or 6th root

    if level == 1:
        # Level 1: Simpler cases - roots of 1, i, -1, -i
        root_r_val = 1 # Modulus of the roots will be 1
        a_choices = [
            (1, 0),    # Complex number 1
            (1, 90),   # Complex number i
            (1, 180),  # Complex number -1
            (1, 270)   # Complex number -i
        ]
        R, Phi_deg = random.choice(a_choices)
    else: # For level 2 and higher, generate more general complex numbers
        # `root_r_val` is the modulus of the N-th roots.
        # `R` (modulus of 'a') will be `root_r_val` raised to the power of `n`.
        root_r_val = random.randint(1, 3) # e.g., 1, 2, or 3
        R = root_r_val ** n
        
        # Principal argument of 'a' (Phi_deg) is chosen from common angles.
        Phi_deg = random.choice(COMMON_PHIS)
        
    # Format the complex number 'a' into rectangular form for the question text.
    question_complex_str = format_complex_number_polar_to_rect(R, Phi_deg)

    question_text = (
        f"求複數 ${question_complex_str}$ 的 ${n}$ 次方根，並以極式 $r(\\cos\\theta^\\circ+i\\sin\\theta^\\circ)$ 表示，"
        f"其中 $\\theta$ 取主輻角 (即 $0^\\circ \\le \\theta < 360^\\circ$)。請將所有根列出，例如 $z_0, z_1, \\dots$。"
    )

    roots = []
    # Calculate each of the 'n' roots using De Moivre's Theorem for roots.
    for k in range(n):
        # Angle for the k-th root
        theta_k_deg = (Phi_deg + 360 * k) / n
        
        # Normalize the angle to be within [0, 360) and round to integer if very close.
        theta_k_deg_normalized = theta_k_deg % 360
        if theta_k_deg_normalized < 0: 
            theta_k_deg_normalized += 360
        
        if abs(theta_k_deg_normalized - round(theta_k_deg_normalized)) < 1e-9:
            theta_k_deg_normalized = int(round(theta_k_deg_normalized))

        # Format the k-th root string in polar form.
        roots.append(
            f"z_{{ {k} }} = {root_r_val}(\\cos{theta_k_deg_normalized}^\\circ+i\\sin{theta_k_deg_normalized}^\\circ)"
        )
    
    # The correct answer is a semicolon-separated string of all roots.
    correct_answer = "; ".join(roots)

    return {
        "question_text": question_text,
        "answer": correct_answer, # The expected input from user is this full string.
        "correct_answer": correct_answer
    }


def check(user_answer, correct_answer):
    """
    檢查使用者答案是否正確。
    `correct_answer` 預期格式為 "z_0 = r(cosA+isinA); z_1 = r(cosB+isinB); ..."。
    使用者答案應為類似格式，且不區分順序。
    """
    # Regex pattern to parse a single root string. It's flexible for user input:
    # - `z_k =` prefix is optional.
    # - `r` and `angle` can be integers or floats.
    root_pattern = re.compile(
        r"^(?:z_\{\s*\d+\s*\}\s*=\s*)?" # Optional "z_k =" prefix (non-capturing)
        r"(\d+(?:\.\d+)?)\s*"           # Capture modulus 'r' (Group 1)
        r"\(\s*\\cos\s*(\d+(?:\.\d+)?)\^\\circ\s*\+\s*i\\sin\s*(?:\d+(?:\.\d+)?)\^\\circ\s*\)$" # Capture angle 'theta' (Group 2), sin angle is not captured as it should be identical.
    )

    def parse_root_string(root_str):
        """Parses a single root string and returns (r, normalized_angle) tuple, or None if invalid."""
        match = root_pattern.match(root_str.strip())
        if not match:
            return None # Invalid format
        
        r = float(match.group(1))
        angle = float(match.group(2))
        
        # Normalize angle to [0, 360) and round r and angle for robust floating-point comparison.
        return (round(r, 6), round(angle % 360, 6)) 

    # Split user's input and correct answer into individual root strings.
    user_roots_raw = [r.strip() for r in user_answer.split(';') if r.strip()]
    correct_roots_raw = [r.strip() for r in correct_answer.split(';') if r.strip()]

    # Parse all user roots. If any root has an invalid format, return an error.
    parsed_user_roots = []
    for ur in user_roots_raw:
        parsed = parse_root_string(ur)
        if parsed is None:
            return {
                "correct": False, 
                "result": f"您的答案格式似乎有誤：'{ur}'。請確保每個根都以 $r(\\cos\\theta^\\circ+i\\sin\\theta^\\circ)$ 格式表示，且 $\\theta$ 為數字。", 
                "next_question": True
            }
        parsed_user_roots.append(parsed)

    # Parse all correct roots. This should ideally not fail as `correct_answer` is internally generated.
    parsed_correct_roots = []
    for cr in correct_roots_raw:
        parsed = parse_root_string(cr)
        if parsed is None:
            # This indicates an internal issue with problem generation or parsing.
            return {"correct": False, "result": "內部錯誤：無法解析正確答案。", "next_question": True}
        parsed_correct_roots.append(parsed)
    
    # Check if the number of roots provided by the user matches the correct number.
    if len(parsed_user_roots) != len(parsed_correct_roots):
        return {
            "correct": False, 
            "result": f"答案不正確。您列出了 {len(parsed_user_roots)} 個根，但應有 {len(parsed_correct_roots)} 個。", 
            "next_question": True
        }

    # Convert lists of parsed roots into sets for order-independent comparison.
    correct_set = set(parsed_correct_roots)
    user_set = set(parsed_user_roots)

    is_correct = (correct_set == user_set)

    if is_correct:
        result_text = f"完全正確！所有 ${len(parsed_correct_roots)}$ 個根都找到了。"
    else:
        # Provide specific feedback if the answer is incorrect.
        missing_roots = correct_set - user_set
        extra_roots = user_set - correct_set
        feedback = "答案不正確。"
        
        if missing_roots:
            first_missing_r, first_missing_angle = list(missing_roots)[0]
            feedback += f"您遺漏了部分根。例如，模數為 ${first_missing_r}$、輻角為 ${first_missing_angle}^\\circ$ 的根。"
        if extra_roots:
            first_extra_r, first_extra_angle = list(extra_roots)[0]
            if not missing_roots:
                 feedback += f"您列出了一些錯誤的根。例如，模數為 ${first_extra_r}$、輻角為 ${first_extra_angle}^\\circ$ 的根是不正確的。"
            else: # If there are both missing and extra roots.
                feedback += f" 此外，您也列出了一些錯誤的根。"
        
        feedback += f" 正確答案應為：${correct_answer}$。"

    return {"correct": is_correct, "result": result_text if is_correct else feedback, "next_question": True}