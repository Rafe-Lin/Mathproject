import random
from fractions import Fraction

# Common description for the geometric setup of a transversal cutting two lines.
# The angles are numbered 1-4 on the top intersection (L1) and 5-8 on the bottom one (L2),
# starting from the top-left and going clockwise.
angle_setup_description = (
    "設定兩直線 $L_1$、$L_2$ 被截線 $L$ 所截。"
    "在 $L$ 與 $L_1$ 的交點周圍，四個角由左上角順時針方向依序為 $\\angle 1, \\angle 2, \\angle 3, \\angle 4$。"
    "在 $L$ 與 $L_2$ 的交點周圍，四個角由左上角順時針方向依序為 $\\angle 5, \\angle 6, \\angle 7, \\angle 8$。"
)
# This numbering corresponds to:
# Top: 1(TL), 2(TR), 3(BR), 4(BL)
# Bottom: 5(TL), 6(TR), 7(BR), 8(BL)
#
# Angle Relationships based on this numbering:
# Corresponding (同位角): {1: 5, 2: 6, 4: 8, 3: 7}
# Alternate Interior (內錯角): {4: 6, 3: 5}
# Consecutive Interior (同側內角): {4: 5, 3: 6}
# Alternate Exterior: {1: 7, 2: 8}
# Vertical (對頂角): {1: 3, 2: 4, 5: 7, 6: 8}

def generate_identify_angle_type_problem():
    """
    Generates a question asking to identify an angle type (corresponding, alternate interior, etc.).
    """
    corresponding = {1: 5, 5: 1, 2: 6, 6: 2, 4: 8, 8: 4, 3: 7, 7: 3}
    alternate_interior = {4: 6, 6: 4, 3: 5, 5: 3}
    consecutive_interior = {4: 5, 5: 4, 3: 6, 6: 3}
    
    q_type_str, angle_map = random.choice([
        ('同位角', corresponding),
        ('內錯角', alternate_interior),
        ('同側內角', consecutive_interior)
    ])
    
    source_angle = random.choice(list(angle_map.keys()))
    answer_angle = angle_map[source_angle]
        
    question_text = f"{angle_setup_description}\n\n請問 $\\angle {source_angle}$ 的{q_type_str}是哪一個角？(請填入角的數字)"
    correct_answer = str(answer_angle)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_calculate_from_one_angle_problem():
    """
    Generates a question where L1 || L2, one angle is given, and another must be calculated.
    """
    # Randomly select a base angle measure (acute)
    acute_angle = random.randint(20, 80)
    obtuse_angle = 180 - acute_angle
    
    # Assign measures to angles based on standard numbering
    # Group 1: Angles 1, 3, 5, 7
    # Group 2: Angles 2, 4, 6, 8
    # In our numbering, if 1 is acute, group 1 is acute and group 2 is obtuse.
    vals = {}
    if random.random() < 0.5: # Group 1 is acute
        for i in [1, 3, 5, 7]: vals[i] = acute_angle
        for i in [2, 4, 6, 8]: vals[i] = obtuse_angle
    else: # Group 1 is obtuse
        for i in [1, 3, 5, 7]: vals[i] = obtuse_angle
        for i in [2, 4, 6, 8]: vals[i] = acute_angle

    angles = list(range(1, 9))
    given_angle_num = random.choice(angles)
    target_angle_num = random.choice([a for a in angles if a != given_angle_num])
    
    given_angle_val = vals[given_angle_num]
    target_angle_val = vals[target_angle_num]
    
    question_text = f"{angle_setup_description}\n\n已知 $L_1 // L_2$ 且 $\\angle {given_angle_num} = {given_angle_val}^{{\\circ}}$，求 $\\angle {target_angle_num}$ 的度數。(答案只需填數字)"
    correct_answer = str(target_angle_val)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def _format_expr(coeff_x, const):
    """Helper to format algebraic expressions like '3x - 5'."""
    if coeff_x == 0:
        return str(const)
        
    if coeff_x == 1:
        x_part = "x"
    elif coeff_x == -1:
        x_part = "-x"
    else:
        x_part = f"{coeff_x}x"
        
    if const == 0:
        return x_part
    elif const > 0:
        return f"{x_part} + {const}"
    else: # const < 0
        return f"{x_part} - {-const}"

def generate_find_unknown_from_equation_problem():
    """
    Generates a problem where angle measures are given as algebraic expressions, requiring solving for x.
    """
    case = random.choice(['equal', 'supplementary'])
    x = random.randint(10, 35)

    if case == 'equal':
        angle_val = random.randint(30, 150)
        
        # Create first expression ax+b = angle_val
        a = random.randint(2, 5)
        b = angle_val - a * x
        
        # Create second expression cx+d = angle_val
        c = random.randint(1, a)
        if c == a: c -= 1 # ensure c is different from a for more interesting problems
        d = angle_val - c * x
        
        # Pick two angles that must be equal
        group1 = [1, 3, 5, 7]
        group2 = [2, 4, 6, 8]
        chosen_group = random.choice([group1, group2])
        angle_num1, angle_num2 = random.sample(chosen_group, 2)
        
    else: # case == 'supplementary'
        angle1_val = random.randint(30, 80)
        angle2_val = 180 - angle1_val

        # Create first expression ax+b = angle1_val
        a = random.randint(1, 4)
        b = angle1_val - a * x

        # Create second expression cx+d = angle2_val
        c = random.randint(1, 4)
        d = angle2_val - c * x

        # Pick two angles that must be supplementary
        group1 = [1, 3, 5, 7]
        group2 = [2, 4, 6, 8]
        angle_num1 = random.choice(group1)
        angle_num2 = random.choice(group2)

    angle1_expr = _format_expr(a, b)
    angle2_expr = _format_expr(c, d)

    question_text = f"{angle_setup_description}\n\n已知 $L_1 // L_2$，且 $\\angle {angle_num1} = ({angle1_expr})^{{\\circ}}$，$\\angle {angle_num2} = ({angle2_expr})^{{\\circ}}$。求 $x$ 的值。"
    correct_answer = str(x)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_two_parallel_pairs_problem():
    """
    Generates a problem with two pairs of parallel lines (L1//L2, M1//M2).
    """
    description = (
        "已知 $L_1 // L_2$ 且 $M_1 // M_2$。這四條線相交形成一個小的平行四邊形。"
        "我們關注在此平行四邊形四個頂點的內角。"
        "左上角的內角為 $\\angle A$，右上角的內角為 $\\angle B$，"
        "右下角的內角為 $\\angle C$，左下角的內角為 $\\angle D$。"
    )
    
    # In a parallelogram, opposite angles are equal, adjacent angles are supplementary.
    # A=C, B=D, A+B=180, B+C=180, etc.
    
    acute_angle = random.randint(40, 80)
    obtuse_angle = 180 - acute_angle
    
    # Assign values
    angles = {'A': acute_angle, 'C': acute_angle, 'B': obtuse_angle, 'D': obtuse_angle}
    if random.random() < 0.5: # Swap them
        angles = {'A': obtuse_angle, 'C': obtuse_angle, 'B': acute_angle, 'D': acute_angle}
        
    labels = ['A', 'B', 'C', 'D']
    given_label = random.choice(labels)
    target_label = random.choice([l for l in labels if l != given_label])
    
    given_val = angles[given_label]
    target_val = angles[target_label]
    
    question_text = f"{description}\n\n若 $\\angle {given_label} = {given_val}^{{\\circ}}$，求 $\\angle {target_label}$ 的度數。(答案只需填數字)"
    correct_answer = str(target_val)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def generate(level=1):
    """
    生成「平行線與截角」相關題目。
    題型包含：
    1. 指認同位角、內錯角、同側內角。
    2. 在平行線條件下，由已知一角計算另一角。
    3. 透過代數式表示角度，建立方程式解未知數 x。
    4. 兩組平行線相交的問題。
    """
    problem_type = random.choice([
        'identify_angle_type', 
        'calculate_from_one_angle', 
        'find_unknown_from_equation',
        'two_parallel_pairs'
    ])
    
    if problem_type == 'identify_angle_type':
        return generate_identify_angle_type_problem()
    elif problem_type == 'calculate_from_one_angle':
        return generate_calculate_from_one_angle_problem()
    elif problem_type == 'find_unknown_from_equation':
        return generate_find_unknown_from_equation_problem()
    else: # 'two_parallel_pairs'
        return generate_two_parallel_pairs_problem()

def check(user_answer, correct_answer):
    """
    檢查使用者答案是否正確。
    """
    # Normalize user answer by removing common non-numeric characters and converting to lowercase
    # This handles inputs like "∠5", "angle 5", or just "5"
    user_ans_normalized = ''.join(filter(str.isdigit, str(user_answer)))
    # For answers that might be algebraic solutions (like x=...), we do a simple strip and lower
    user_ans_simple = str(user_answer).strip().lower()
    
    # The correct answer is always a string of a number in this script
    correct_ans_normalized = str(correct_answer).strip()

    is_correct = (user_ans_normalized == correct_ans_normalized) or \
                 (user_ans_simple == correct_ans_normalized)
    
    # Allow for floating point comparison if direct string match fails
    if not is_correct:
        try:
            if float(user_ans_simple) == float(correct_ans_normalized):
                is_correct = True
        except (ValueError, TypeError):
            pass

    # Provide feedback with LaTeX formatting
    if '\\' in correct_answer or 'angle' in correct_answer.lower():
        # This case is not currently used as answers are numeric strings, but kept for robustness
        feedback_answer = correct_answer
    else:
        feedback_answer = f"{correct_answer}"

    result_text = f"完全正確！答案是 ${feedback_answer}$。" if is_correct else f"答案不正確。正確答案應為：${feedback_answer}$"
    
    return {"correct": is_correct, "result": result_text, "next_question": True}