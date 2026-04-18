import random
from fractions import Fraction

# --- Main Generator ---
def generate(level=1):
    """
    生成「角的分類與關係」相關題目。
    包含：
    1. 基本角的運算 (直角、平角、周角)
    2. 餘角與補角的基本與進階計算
    3. 角度代數應用題
    4. 相交線形成的角 (對頂角、平角)
    """
    problem_type = random.choice([
        'basic_angle_arithmetic', 
        'complementary_supplementary',
        'angle_algebra',
        'intersecting_lines'
    ])
    
    if problem_type == 'basic_angle_arithmetic':
        return _generate_basic_angle_arithmetic()
    elif problem_type == 'complementary_supplementary':
        return _generate_complementary_supplementary()
    elif problem_type == 'angle_algebra':
        return _generate_angle_algebra()
    else: # intersecting_lines
        return _generate_intersecting_lines()

# --- Helper Functions for Problem Generation ---

def _generate_basic_angle_arithmetic():
    """
    題型：基本角的倍數或分數計算。
    例如：直角的 2 倍=___度。
    """
    angles = [("直角", 90), ("平角", 180), ("周角", 360)]
    ops = [("的 2 倍", 2), ("的 3 倍", 3), ("的 $\\frac{1}{2}$ 倍", Fraction(1, 2)), 
           ("的 $\\frac{1}{3}$ 倍", Fraction(1, 3)), ("的一半", Fraction(1, 2))]
    
    while True:
        angle_name, angle_val = random.choice(angles)
        op_text, op_val = random.choice(ops)
        result = angle_val * op_val
        if result == int(result): # Ensure the result is an integer
            break
            
    question_text = f"{angle_name}{op_text} = ___ 度。"
    correct_answer = str(int(result))
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def _generate_complementary_supplementary():
    """
    題型：餘角與補角的計算。
    包含簡單計算、連鎖關係、混合關係、大小比較。
    """
    sub_type = random.choice(['simple_chain', 'mixed', 'comparison'])

    if sub_type == 'simple_chain':
        # 題型：若∠A=34°，∠A和∠B互餘，∠B和∠C也互餘，則...
        angle_a = random.randint(10, 80)
        angle_b = 90 - angle_a
        angle_c = 90 - angle_b # which is angle_a
        question_text = f"若 $\\angle A={angle_a}^\\circ$，$\\angle A$ 和 $\\angle B$ 互餘，且 $\\angle B$ 和 $\\angle C$ 也互餘，則 $\\angle B$ 和 $\\angle C$ 分別為多少度？(答案請用逗號分隔，例如 50,40)"
        correct_answer = f"{angle_b},{angle_c}"

    elif sub_type == 'mixed':
        # 題型：若∠A=40°，∠B和∠A互餘，∠C和∠B互補，則...
        angle_a = random.randint(10, 80)
        angle_b = 90 - angle_a
        angle_c = 180 - angle_b
        question_text = f"若 $\\angle A={angle_a}^\\circ$，$\\angle B$ 和 $\\angle A$ 互餘，$\\angle C$ 和 $\\angle B$ 互補，則 $\\angle B$、$\\angle C$ 分別為多少度？(答案請用逗號分隔)"
        correct_answer = f"{angle_b},{angle_c}"

    else: # comparison
        # 題型：∠A 的補角比∠B 的餘角大或小多少度？
        angle_a = random.randint(91, 170)
        angle_b = random.randint(10, 80)
        supp_a = 180 - angle_a
        comp_b = 90 - angle_b
        diff = supp_a - comp_b
        question_text = f"已知 $\\angle A={angle_a}^\\circ$、$\\angle B={angle_b}^\\circ$，則 $\\angle A$ 的補角比 $\\angle B$ 的餘角大多少度？(若較小請填負數)"
        correct_answer = str(diff)
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def _generate_angle_algebra():
    """
    題型：需要設立未知數 x 來解的角度問題。
    """
    sub_type = random.choice(['system_of_relations', 'complex_word_problem'])
    
    if sub_type == 'system_of_relations':
        # 題型：若∠A和∠B互補，∠A和∠C互餘，且∠B＋∠C=140°，則...
        angle_a = random.randint(20, 70)
        # B = 180 - A
        # C = 90 - A
        # B + C = 270 - 2A
        total = 270 - 2 * angle_a
        question_text = f"若 $\\angle A$ 和 $\\angle B$ 互補，$\\angle A$ 和 $\\angle C$ 互餘，且 $\\angle B＋\\angle C={total}^\\circ$，則 $\\angle A$ 為多少度？"
        correct_answer = str(angle_a)
        
    else: # complex_word_problem
        # 題型：一個角的餘角的 2 倍和它補角的 1/2 互為補角...
        # We pre-calculate solutions to ensure nice numbers.
        # Case 1: 2(90-x) + 0.5(180-x) = 180  => x = 36
        # Case 2: (90-x) + (1/3)(180-x) = 90  => x = 45
        case = random.choice([1, 2])
        if case == 1:
            question_text = "若一個角的餘角的 2 倍和它補角的 $\\frac{1}{2}$ 互為補角，則這個角的度數為何？"
            correct_answer = "36"
        else:
            question_text = "若一個角的餘角與它補角的 $\\frac{1}{3}$ 互為餘角，則這個角的度數為何？"
            correct_answer = "45"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def _format_algebraic_term(coeff, const, var='x'):
    """Helper to format algebraic terms like (3x-10)"""
    expr = ""
    if coeff != 0:
        if coeff == 1:
            expr += var
        elif coeff == -1:
            expr += f"-{var}"
        else:
            expr += f"{coeff}{var}"
    
    if const != 0:
        if const > 0:
            if expr:
                expr += f"＋{const}"
            else:
                expr += str(const)
        else: # const < 0
            expr += f"{const}"
    
    if not expr:
        return "0"
    return expr

def _generate_intersecting_lines():
    """
    題型：相交線所形成的對頂角與平角問題，常結合代數。
    """
    sub_type = random.choice(['numeric_angles_on_line', 'algebraic_angles_on_line', 'algebraic_vertical_angles'])

    if sub_type == 'numeric_angles_on_line':
        # 題型：L, M, N 交於 O, ∠1=100°, ∠3=42°, 求 ∠2。
        angle1 = random.randint(80, 120)
        angle3 = random.randint(20, 50)
        if angle1 + angle3 >= 180:
            angle1 = 100
            angle3 = 40
        angle2 = 180 - angle1 - angle3
        question_text = f"三條直線相交於一點，形成一個平角，此平角被分割成三個相鄰的角 $\\angle 1, \\angle 2, \\angle 3$。若 $\\angle 1={angle1}^\\circ$，$\\angle 3={angle3}^\\circ$，則 $\\angle 2$ 為多少度？"
        correct_answer = str(angle2)

    elif sub_type == 'algebraic_angles_on_line':
        # 題型：三個代數角形成平角，求 x。
        x = random.randint(10, 25)
        
        a, c, e = random.sample(range(1, 6), 3)
        total_x_coeff = a + c + e
        
        total_const = 180 - total_x_coeff * x
        b = random.randint(-20, 20)
        d = random.randint(-20, 20)
        f = total_const - b - d

        expr1 = _format_algebraic_term(a, b)
        expr2 = _format_algebraic_term(c, d)
        expr3 = _format_algebraic_term(e, f)
        
        question_text = f"一直線上三個相鄰角分別為 $({expr1})^\\circ$、$({expr2})^\\circ$ 及 $({expr3})^\\circ$，求 x 的值。"
        correct_answer = str(x)

    else: # algebraic_vertical_angles
        # 題型：∠1=(3x)°, ∠2=(2x+5)°, ∠3=(2y+25)°，求 x, y
        x = random.randint(20, 40)
        y = random.randint(20, 40)
        
        # Create supplementary angles with x: angle1 + angle2 = 180
        a, c = random.sample(range(2, 6), 2)
        total_x_coeff = a + c
        total_const = 180 - total_x_coeff * x
        b = random.randint(-25, 25)
        d = total_const - b
        
        expr1 = _format_algebraic_term(a, b)
        expr2 = _format_algebraic_term(c, d)

        # Create vertical angle with y: angle3 = angle1
        angle1_val = a * x + b
        e = random.randint(2, 6)
        f = angle1_val - e * y
        expr3 = _format_algebraic_term(e, f, var='y')

        question_text = f"兩直線 L 與 M 相交，形成四個角。其中一對鄰角分別為 $\\angle 1=({expr1})^\\circ$ 和 $\\angle 2=({expr2})^\\circ$。$\\angle 1$ 的對頂角 $\\angle 3=({expr3})^\\circ$。求出 x 和 y 的值。(答案請用逗號分隔)"
        correct_answer = f"{x},{y}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

# --- Checker ---
def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_parts = [part.strip() for part in user_answer.split(',')]
    correct_parts = [part.strip() for part in correct_answer.split(',')]

    is_correct = False
    if len(user_parts) == len(correct_parts):
        try:
            # Convert parts to float for comparison, if possible
            user_nums = [float(p) for p in user_parts]
            correct_nums = [float(p) for p in correct_parts]
            
            # Check if all pairs of numbers are close enough (handles potential floating point issues)
            if all(abs(u - c) < 1e-9 for u, c in zip(user_nums, correct_nums)):
                is_correct = True
        except ValueError:
            # If conversion fails, compare as strings (case-insensitive)
            user_strings = [p.upper() for p in user_parts]
            correct_strings = [p.upper() for p in correct_parts]
            if user_strings == correct_strings:
                is_correct = True
    
    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}