import random
import math
from fractions import Fraction

def format_line_equation(A, B, C):
    """Formats Ax + By + C = 0 into a LaTeX string."""
    parts = []

    # Handle Ax term
    if A == 1:
        parts.append("x")
    elif A == -1:
        parts.append("-x")
    elif A != 0:
        parts.append(f"{A}x")

    # Handle By term
    if B != 0:
        if B == 1:
            parts.append("+ y" if parts else "y")
        elif B == -1:
            parts.append("- y" if parts else "-y")
        elif B > 0:
            parts.append(f"+ {B}y" if parts else f"{B}y")
        else: # B < 0
            parts.append(f"{B}y") # Negative sign is part of the number

    # Handle C term
    if C != 0:
        if C > 0:
            parts.append(f"+ {C}" if parts else f"{C}")
        else: # C < 0
            parts.append(f"{C}") # Negative sign is part of the number

    # This case should be prevented by generate_coefficients, but for robustness
    if not parts: 
        # This means A=0, B=0, C=0, which is not a valid line equation typically
        # Or A=0, B=0, C!=0 which results in "C = 0", but A,B cannot be both zero.
        return "0 = 0" 

    return " ".join(parts) + " = 0"

def generate_coefficients(level):
    """Generates (A, B, C) for a line, ensuring A and B are not both zero."""
    A, B = 0, 0
    while A == 0 and B == 0:
        if level == 1:
            A = random.randint(-4, 4)
            B = random.randint(-4, 4)
        else: # Higher levels might have larger ranges
            A = random.randint(-7, 7)
            B = random.randint(-7, 7)
    
    if level == 1:
        C = random.randint(-5, 5)
    else:
        C = random.randint(-10, 10)
    
    return A, B, C

def generate(level=1):
    """
    生成「兩直線夾角」相關題目。
    利用法向量的內積計算兩相交直線的夾角。
    """
    # Generate coefficients for two lines L1: A1x + B1y + C1 = 0 and L2: A2x + B2y + C2 = 0
    A1, B1, C1 = generate_coefficients(level)
    A2, B2, C2 = generate_coefficients(level)

    # Normal vectors
    n1 = (A1, B1)
    n2 = (A2, B2)

    # Calculate dot product: n1 . n2
    dot_product = n1[0] * n2[0] + n1[1] * n2[1]

    # Calculate magnitudes of normal vectors
    mag_n1_sq = n1[0]**2 + n1[1]**2
    mag_n2_sq = n2[0]**2 + n2[1]**2
    
    mag_n1 = math.sqrt(mag_n1_sq)
    mag_n2 = math.sqrt(mag_n2_sq)

    # This condition should ideally not be met due to generate_coefficients ensuring A or B is non-zero.
    # If it does, it implies a vector has zero magnitude (0,0), which isn't a valid normal vector.
    # Regenerate problem if such a degenerate case occurs, though unlikely.
    if mag_n1 == 0 or mag_n2 == 0:
        return generate(level)

    # Cosine of the angle between normal vectors (theta_vec)
    cos_theta_vec = dot_product / (mag_n1 * mag_n2)

    # The angle between two lines is usually defined as the acute angle.
    # We take the absolute value of cos_theta_vec to get the cosine of the acute angle between the lines.
    cos_theta_lines = abs(cos_theta_vec)

    # Clamp cos_theta_lines to [-1, 1] due to potential floating point inaccuracies
    cos_theta_lines = max(-1.0, min(1.0, cos_theta_lines))

    # Calculate the angle in radians, then convert to degrees
    angle_rad = math.acos(cos_theta_lines)
    angle_deg = math.degrees(angle_rad)

    # Format the angle for the answer string.
    # Special handling for common exact angles (0, 30, 45, 60, 90 degrees) to display as integers.
    # Otherwise, round to one decimal place.
    angle_str = ""
    if abs(angle_deg - 0) < 1e-6:
        angle_str = "0"
    elif abs(angle_deg - 30) < 1e-6:
        angle_str = "30"
    elif abs(angle_deg - 45) < 1e-6:
        angle_str = "45"
    elif abs(angle_deg - 60) < 1e-6:
        angle_str = "60"
    elif abs(angle_deg - 90) < 1e-6:
        angle_str = "90"
    else:
        angle_str = f"{angle_deg:.1f}"
    
    # Construct LaTeX for line equations
    line1_latex = format_line_equation(A1, B1, C1)
    line2_latex = format_line_equation(A2, B2, C2)

    question_text = (
        f"求兩直線 $L_1: {line1_latex}$ 與 $L_2: {line2_latex}$ 的夾角。<br>"
        r"請以度為單位，並四捨五入至小數點後一位。若為 $0^{{\\circ}}, 30^{{\\circ}}, 45^{{\\circ}}, 60^{{\\circ}}, 90^{{\\circ}}$ 等特殊角度，請填入整數。"
    )
    
    # The 'answer' and 'correct_answer' keys store the string representation of the degree value
    correct_answer = angle_str

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip().upper()
    correct_answer = correct_answer.strip().upper()
    
    is_correct = (user_answer == correct_answer)
    
    if not is_correct:
        try:
            # Allow for floating point comparison with a tolerance
            user_float = float(user_answer)
            correct_float = float(correct_answer)
            # Using a small tolerance for floating point comparisons
            is_correct = math.isclose(user_float, correct_float, rel_tol=1e-3, abs_tol=1e-3)
        except ValueError:
            pass # If conversion to float fails, it's not a numerical match

    result_text = f"完全正確！答案是 ${correct_answer}^{{\\circ}}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}^{{\\circ}}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}