import random
import math
import re
from fractions import Fraction

def generate(level=1):
    """
    生成「向量的加法與減法」相關題目。
    包含：
    1. 坐標表示法的向量加法/減法，並計算其長度。
    2. 坐標表示法的向量純量乘法與組合運算，並計算其長度。
    3. 利用向量分解計算三角形邊向量及周長。
    """
    problem_type = random.choice([
        'basic_addition_subtraction',
        'scalar_multiplication_combined',
        'vector_decomposition_perimeter'
    ])

    if problem_type == 'basic_addition_subtraction':
        return generate_basic_addition_subtraction_problem(level)
    elif problem_type == 'scalar_multiplication_combined':
        return generate_scalar_multiplication_combined_problem(level)
    else: # 'vector_decomposition_perimeter'
        return generate_vector_decomposition_perimeter_problem(level)

# Helper function to parse a sqrt string into its float value, coefficient, and radicand.
# This helps in numerical comparison for 'check' function.
# Examples: "5" -> (5.0, 5.0, 1.0)
# r"\\sqrt{2}" -> (1.414..., 1.0, 2.0)
# r"2\\sqrt{3}" -> (3.464..., 2.0, 3.0)
def parse_sqrt_string(s):
    s = s.strip()
    if not s:
        return None, None, None

    # Try integer/float first
    try:
        val = float(s)
        return val, val, 1.0 # (value, coeff, radicand)
    except ValueError:
        pass

    # Try sqrt format: \\sqrt{N}
    match_simple_sqrt = re.match(r'^\\sqrt\{(\d+)\}$', s)
    if match_simple_sqrt:
        radicand = int(match_simple_sqrt.group(1))
        val = math.sqrt(radicand)
        return val, 1.0, float(radicand)

    # Try combined format: A\\sqrt{N}
    match_coeff_sqrt = re.match(r'^(-?\d+)\\sqrt\{(\d+)\}$', s)
    if match_coeff_sqrt:
        coeff = int(match_coeff_sqrt.group(1))
        radicand = int(match_coeff_sqrt.group(2))
        val = coeff * math.sqrt(radicand)
        return val, float(coeff), float(radicand)
    
    # Try Fraction with sqrt (less common, but for completeness)
    match_frac_sqrt = re.match(r'^\\frac\{(-?\d+)\}\{(-?\d+)\}\\sqrt\{(\d+)\}$', s) # e.g. \\frac{1}{2}\\sqrt{3}
    if match_frac_sqrt:
        num = int(match_frac_sqrt.group(1))
        den = int(match_frac_sqrt.group(2))
        radicand = int(match_frac_sqrt.group(3))
        if den == 0: return None, None, None # Avoid division by zero
        val = (Fraction(num, den) * math.sqrt(radicand)).real
        return val, Fraction(num, den).real, float(radicand)

    return None, None, None # Failed to parse

# Helper function to simplify square roots into a string format.
# Returns a string like: "5", r"\\sqrt{2}", r"2\\sqrt{3}"
def simplify_sqrt_string(n):
    if not isinstance(n, int):
        return str(n)

    if n < 0:
        return r"\\sqrt{{{}}}".format(n) # For complex numbers, this would be i\\sqrt{-n}
    if n == 0:
        return "0"
    
    sqrt_n = int(math.sqrt(n))
    if sqrt_n * sqrt_n == n:
        return str(sqrt_n)

    coefficient = 1
    temp_n = n
    i = 2
    while i * i <= temp_n:
        while temp_n % (i * i) == 0:
            coefficient *= i
            temp_n //= (i * i)
        i += 1
    
    if coefficient == 1:
        return r"\\sqrt{{{}}}".format(temp_n)
    else:
        return f"{coefficient}" + r"\\sqrt{{{}}}".format(temp_n)

# Helper function to format a vector as (x,y)
def format_vector(v):
    return f"({v[0]},{v[1]})"

# Helper function to calculate and format magnitude as a simplified sqrt string.
def format_magnitude(v):
    x, y = v
    magnitude_sq = x*x + y*y
    return simplify_sqrt_string(magnitude_sq)


def generate_basic_addition_subtraction_problem(level):
    """
    生成基礎向量加法/減法及長度問題。
    """
    coord_range = (-level*2-1, level*2+1) 
    if level == 1: coord_range = (-5, 5)
    elif level == 2: coord_range = (-8, 8)
    else: coord_range = (-10, 10)

    u = (random.randint(*coord_range), random.randint(*coord_range))
    v = (random.randint(*coord_range), random.randint(*coord_range))

    operation_choice = random.choice(['add', 'subtract', 'both'])

    question_parts = [f"已知向量 $u={format_vector(u)}$，$v={format_vector(v)}$。"]
    correct_answers_check = [] # List of strings to check for `check` function
    correct_answers_display = [] # List of display strings for `correct_answer` field

    if operation_choice in ['add', 'both']:
        result_add = (u[0] + v[0], u[1] + v[1])
        magnitude_add_str = format_magnitude(result_add)
        question_parts.append(f"(1) 求向量 $u+v$ 及其長度。")
        correct_answers_display.append(f"$(1)\ u+v = {format_vector(result_add)}$。$|u+v| = {magnitude_add_str}$。")
        correct_answers_check.append(f"{format_vector(result_add)};{magnitude_add_str}")

    if operation_choice in ['subtract', 'both']:
        result_sub = (u[0] - v[0], u[1] - v[1])
        magnitude_sub_str = format_magnitude(result_sub)
        question_parts.append(f"(2) 求向量 $u-v$ 及其長度。")
        correct_answers_display.append(f"$(2)\ u-v = {format_vector(result_sub)}$。$|u-v| = {magnitude_sub_str}$。")
        correct_answers_check.append(f"{format_vector(result_sub)};{magnitude_sub_str}")

    question_text = "<br>".join(question_parts)
    # Use '|||' as a distinct separator for multiple parts of the answer when 'both' operations are requested.
    correct_answer_for_check = "|||".join(correct_answers_check)
    correct_answer_for_display = "<br>".join(correct_answers_display)

    return {
        "question_text": question_text,
        "answer": correct_answer_for_check,
        "correct_answer": correct_answer_for_display
    }


def generate_scalar_multiplication_combined_problem(level):
    """
    生成向量純量乘法及組合運算問題。
    """
    coord_range = (-level*2, level*2)
    if level == 1: coord_range = (-4, 4)
    elif level == 2: coord_range = (-6, 6)
    else: coord_range = (-8, 8)

    u = (random.randint(*coord_range), random.randint(*coord_range))
    v = (random.randint(*coord_range), random.randint(*coord_range))

    # Scalar coefficients, avoid -1, 0, 1 for more challenge
    a = random.choice([i for i in range(-3, 4) if i not in [-1, 0, 1]])
    b = random.choice([i for i in range(-3, 4) if i not in [-1, 0, 1]])

    result_x = a * u[0] + b * v[0]
    result_y = a * u[1] + b * v[1]
    result_vec = (result_x, result_y)
    magnitude_str = format_magnitude(result_vec)

    question_text = (
        f"已知向量 $u={format_vector(u)}$，$v={format_vector(v)}$。求向量 ${a}u + {b}v$ 及其長度。"
    )
    correct_answer_display = (
        f"${a}u + {b}v = {format_vector((a*u[0], a*u[1]))} + {format_vector((b*v[0], b*v[1]))} = {format_vector(result_vec)}$。<br>"
        f"$|{a}u + {b}v| = {magnitude_str}$。"
    )
    correct_answer_checkable = f"{format_vector(result_vec)};{magnitude_str}"

    return {
        "question_text": question_text,
        "answer": correct_answer_checkable,
        "correct_answer": correct_answer_display
    }


def generate_vector_decomposition_perimeter_problem(level):
    """
    生成利用向量分解計算三角形邊向量及周長問題。
    """
    coord_range = (-level*2-2, level*2+2)
    if level == 1: coord_range = (-6, 6)
    elif level == 2: coord_range = (-9, 9)
    else: coord_range = (-12, 12)

    # Ensure AB and AC are not collinear or zero vectors for a valid non-degenerate triangle
    while True:
        AB = (random.randint(*coord_range), random.randint(*coord_range))
        AC = (random.randint(*coord_range), random.randint(*coord_range))
        
        # Check for zero vectors
        if (AB[0] == 0 and AB[1] == 0) or (AC[0] == 0 and AC[1] == 0):
            continue
        
        # Check for collinearity (cross product for 2D is x1*y2 - x2*y1). Must not be 0.
        # This ensures A, B, C are not collinear.
        if (AB[0] * AC[1] - AB[1] * AC[0]) == 0:
            continue 
        
        # Calculate BC vector (BC = AC - AB)
        BC = (AC[0] - AB[0], AC[1] - AB[1])
        if BC[0] == 0 and BC[1] == 0: # Ensure BC is not a zero vector
            continue
        
        break

    mag_AB_str = format_magnitude(AB)
    mag_AC_str = format_magnitude(AC)
    mag_BC_str = format_magnitude(BC)

    # Calculate actual float values for perimeter
    mag_AB_val = math.sqrt(AB[0]**2 + AB[1]**2)
    mag_AC_val = math.sqrt(AC[0]**2 + AC[1]**2)
    mag_BC_val = math.sqrt(BC[0]**2 + BC[1]**2)
    perimeter_val = mag_AB_val + mag_BC_val + mag_AC_val

    question_text = (
        f"在 $\\triangle ABC$ 中，已知 $AB={format_vector(AB)}$，$AC={format_vector(AC)}$，"
        f"求 $BC$ 及 $\\triangle ABC$ 的周長。<br>(周長請計算至小數點後兩位)"
    )
    
    perimeter_display_parts = []
    if mag_AB_str != "0": perimeter_display_parts.append(mag_AB_str)
    if mag_BC_str != "0": perimeter_display_parts.append(mag_BC_str)
    if mag_AC_str != "0": perimeter_display_parts.append(mag_AC_str)
    
    perimeter_display = " + ".join(perimeter_display_parts)
    
    correct_answer_display = (
        f"利用向量的分解，得 $BC = AC - AB = {format_vector(AC)} - {format_vector(AB)} = {format_vector(BC)}$。<br>"
        f"$\\triangle ABC$ 的周長為 $|AB| + |BC| + |AC| = {perimeter_display} \\approx {perimeter_val:.2f}$。"
    )
    
    # For `check` function, we pass the BC vector string and the float value of perimeter.
    correct_answer_checkable = f"{format_vector(BC)};{perimeter_val:.4f}" # Use 4 decimal places for internal check

    return {
        "question_text": question_text,
        "answer": correct_answer_checkable,
        "correct_answer": correct_answer_display
    }


def check(user_answer, correct_answer_data):
    """
    檢查使用者答案是否正確。
    `correct_answer_data` 來自 `generate` 函數的 'answer' 欄位，
    可能包含多組答案，每組用 '|||' 分隔，每組內向量和長度用 ';' 分隔。
    例如: "(3,4);5|||(1,-6);\\sqrt{37}" 或 "(4,-3);20.0710"
    """
    
    # Handle multiple answer groups (e.g., for u+v and u-v)
    correct_answer_subparts_data = correct_answer_data.split('|||')
    user_answer_subparts = [p.strip() for p in user_answer.split('|||')]

    if len(user_answer_subparts) != len(correct_answer_subparts_data):
        return {"correct": False, "result": "答案格式不正確，請提供所有部分的答案，並用 '|||' 分隔 (如果有多組答案)。", "next_question": False}

    all_overall_correct = True
    overall_feedback_parts = []

    for i, (user_subpart, correct_subpart_data) in enumerate(zip(user_answer_subparts, correct_answer_subparts_data)):
        # Each subpart contains vector and magnitude/perimeter, separated by ';'
        user_parts = [p.strip() for p in user_subpart.split(';')]
        correct_parts = [p.strip() for p in correct_subpart_data.split(';')]

        if len(user_parts) != len(correct_parts):
            overall_feedback_parts.append(f"第 {i+1} 組答案格式不正確。請用 ';' 分隔向量坐標和長度/周長。")
            all_overall_correct = False
            continue

        part_is_correct_in_subpart = True
        feedback_parts_for_subpart = []

        for j, (user_ans, correct_ans) in enumerate(zip(user_parts, correct_parts)):
            component_correct = False

            # Check for vector coordinates (e.g., (x,y))
            if user_ans.startswith('(') and user_ans.endswith(')'):
                try:
                    user_coords_str = user_ans[1:-1].split(',')
                    user_coords = (int(user_coords_str[0].strip()), int(user_coords_str[1].strip()))
                    
                    correct_coords_str = correct_ans[1:-1].split(',')
                    correct_coords = (int(correct_coords_str[0].strip()), int(correct_coords_str[1].strip()))

                    if user_coords == correct_coords:
                        component_correct = True
                        feedback_parts_for_subpart.append(f"第 {j+1} 項 (向量坐標) 正確：${user_ans}$")
                    else:
                        feedback_parts_for_subpart.append(f"第 {j+1} 項 (向量坐標) 錯誤。你的答案是 ${user_ans}$，正確應為 ${correct_ans}$。")
                except (ValueError, IndexError):
                    feedback_parts_for_subpart.append(f"第 {j+1} 項 (向量坐標) 格式錯誤。你的答案是 ${user_ans}$，正確格式應為 $(x,y)$。")
            else: # Must be magnitude or perimeter (number or sqrt string)
                user_val_float, _, _ = parse_sqrt_string(user_ans)
                correct_val_float, _, _ = parse_sqrt_string(correct_ans)

                if user_val_float is not None and correct_val_float is not None:
                    # Use relative and absolute tolerance for float comparison
                    if math.isclose(user_val_float, correct_val_float, rel_tol=1e-3, abs_tol=1e-3):
                        component_correct = True
                        # Provide numeric approximation for context
                        feedback_parts_for_subpart.append(f"第 {j+1} 項 (長度/周長) 正確：${user_ans}$ (數值約為 ${correct_val_float:.2f}$)")
                    else:
                        feedback_parts_for_subpart.append(f"第 {j+1} 項 (長度/周長) 錯誤。你的答案是 ${user_ans}$，正確答案約為 ${correct_val_float:.2f}$。")
                elif user_ans == correct_ans: # Fallback for exact string match (e.g., if parse_sqrt_string fails for some edge cases, but strings are identical)
                     component_correct = True
                     feedback_parts_for_subpart.append(f"第 {j+1} 項 (長度/周長) 正確：${user_ans}$")
                else:
                    feedback_parts_for_subpart.append(f"第 {j+1} 項 (長度/周長) 格式或數值錯誤。你的答案是 ${user_ans}$，正確答案應為 ${correct_ans}$ (或其數值)。")

            if not component_correct:
                part_is_correct_in_subpart = False

        overall_feedback_parts.append(f"第 {i+1} 組答案： {'正確' if part_is_correct_in_subpart else '部分錯誤或格式錯誤'}<br>" + "<br>".join(feedback_parts_for_subpart))
        if not part_is_correct_in_subpart:
            all_overall_correct = False

    result_text = "<br>".join(overall_feedback_parts)
    if all_overall_correct:
        result_text = f"完全正確！<br>{result_text}"
    else:
        result_text = f"答案不正確。<br>{result_text}"

    return {"correct": all_overall_correct, "result": result_text, "next_question": all_overall_correct}