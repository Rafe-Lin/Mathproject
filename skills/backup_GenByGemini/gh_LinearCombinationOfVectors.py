import random
from fractions import Fraction
import math # For GCD for simplifying fractions if needed, or checking parallel vectors.

def generate(level=1):
    """
    生成「線性組合」相關題目。
    包含：
    1. 幾何向量分解 (平行四邊形)
    2. 座標向量線性組合
    3. 線性組合定義的區域 (點或形狀)
    """
    problem_type_options = []

    if level == 1:
        problem_type_options = [
            'geometric_decomposition_simple',
            'coordinate_combination',
            'region_single_point'
        ]
    elif level == 2:
        problem_type_options = [
            'geometric_decomposition_medium',
            'coordinate_combination',
            'region_single_point', # Include single point for variety
            'region_shape_description'
        ]
    else: # level 3 or higher
        problem_type_options = [
            'geometric_decomposition_medium',
            'coordinate_combination',
            'region_shape_description'
        ]
    
    problem_type = random.choice(problem_type_options)

    if problem_type == 'geometric_decomposition_simple':
        return generate_geometric_decomposition_simple()
    elif problem_type == 'geometric_decomposition_medium':
        return generate_geometric_decomposition_medium()
    elif problem_type == 'coordinate_combination':
        return generate_coordinate_combination()
    elif problem_type == 'region_single_point':
        return generate_region_single_point_problem()
    else: # 'region_shape_description'
        return generate_region_shape_description_problem()

def generate_geometric_decomposition_simple():
    """
    題型：在平行四邊形ABCD中，點E在AB或AD上，表示AE或DE等向量。
    (例如: AE = xAB + yAD, 其中 x=m/n, y=0)
    """
    direction = random.choice(['AB', 'AD'])
    numerator = random.randint(1, 3)
    denominator = random.randint(numerator + 1, 5) # denominator > numerator to keep E inside segment
    
    # Simplify fraction
    common = math.gcd(numerator, denominator)
    numerator //= common
    denominator //= common

    ratio_str = f"$\\frac{{{numerator}}}{{{denominator}}}$"
    
    if direction == 'AB':
        target_vec_str = r"$\vec{AE}$"
        base_vec_str = r"$\vec{AB}$"
        question_text = f"在平行四邊形 $ABCD$ 中，點 $E$ 在線段 $AB$ 上，且 $AE : EB = {numerator} : {denominator - numerator}$。"
        question_text += f"將向量 {target_vec_str} 表示成 $x\\vec{{AB}} + y\\vec{{AD}}$ 的形式，求 $x, y$ 的值。"
        x_val = Fraction(numerator, denominator)
        y_val = Fraction(0)
    else: # direction == 'AD'
        target_vec_str = r"$\vec{AF}$" # Using F for AD side to avoid conflict with E on AB
        base_vec_str = r"$\vec{AD}$"
        question_text = f"在平行四邊形 $ABCD$ 中，點 $F$ 在線段 $AD$ 上，且 $AF : FD = {numerator} : {denominator - numerator}$。"
        question_text += f"將向量 {target_vec_str} 表示成 $x\\vec{{AB}} + y\\vec{{AD}}$ 的形式，求 $x, y$ 的值。"
        x_val = Fraction(0)
        y_val = Fraction(numerator, denominator)

    correct_answer = f"x={x_val}, y={y_val}"
    
    # For display, if it's an integer, display as integer. Otherwise, fraction.
    x_display = str(x_val) if x_val.denominator != 1 else str(x_val.numerator)
    y_display = str(y_val) if y_val.denominator != 1 else str(y_val.numerator)

    if direction == 'AB':
        explanation = f"因為點 $E$ 在線段 $AB$ 上，且 $AE : EB = {numerator} : {denominator - numerator}$，所以 $\\vec{{AE}} = \\frac{{{numerator}}}{{{denominator}}}\\vec{{AB}}$。故 $\\vec{{AE}} = {x_display}\\vec{{AB}} + {y_display}\\vec{{AD}}$。"
    else:
        explanation = f"因為點 $F$ 在線段 $AD$ 上，且 $AF : FD = {numerator} : {denominator - numerator}$，所以 $\\vec{{AF}} = \\frac{{{numerator}}}{{{denominator}}}\\vec{{AD}}$。故 $\\vec{{AF}} = {x_display}\\vec{{AB}} + {y_display}\\vec{{AD}}$。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "explanation": explanation
    }

def generate_geometric_decomposition_medium():
    """
    題型：在平行四邊形ABCD中，點F在DC或BC上，表示AF或BF等向量。
    (例如: AF = AD + DF = AD + (m/n)AB, 所以 x=m/n, y=1)
    """
    side_target = random.choice(['DC', 'BC'])
    numerator = random.randint(1, 3)
    denominator = random.randint(numerator + 1, 5) # denominator > numerator to keep F inside segment

    common = math.gcd(numerator, denominator)
    numerator //= common
    denominator //= common

    ratio_str = f"$\\frac{{{numerator}}}{{{denominator}}}$"
    
    if side_target == 'DC':
        # AF = AD + DF = AD + (n/d)DC = AD + (n/d)AB
        target_vec_str = r"$\vec{AF}$"
        question_text = f"在平行四邊形 $ABCD$ 中，點 $F$ 在線段 $DC$ 上，且 $DF : FC = {numerator} : {denominator - numerator}$。"
        question_text += f"將向量 {target_vec_str} 表示成 $x\\vec{{AB}} + y\\vec{{AD}}$ 的形式，求 $x, y$ 的值。"
        x_val = Fraction(numerator, denominator)
        y_val = Fraction(1)
        explanation = f"利用向量分解，$\\vec{{AF}} = \\vec{{AD}} + \\vec{{DF}}$。因為點 $F$ 在線段 $DC$ 上，且 $DF : FC = {numerator} : {denominator - numerator}$，所以 $\\vec{{DF}} = \\frac{{{numerator}}}{{{denominator}}}\\vec{{DC}}$。又因為 $\\vec{{DC}} = \\vec{{AB}}$ (平行四邊形性質)，所以 $\\vec{{AF}} = \\vec{{AD}} + \\frac{{{numerator}}}{{{denominator}}}\\vec{{AB}}$。故 $x={x_val}, y=1$。"
    else: # side_target == 'BC'
        # AF = AB + BF = AB + (n/d)BC = AB + (n/d)AD
        target_vec_str = r"$\vec{AF}$"
        question_text = f"在平行四邊形 $ABCD$ 中，點 $F$ 在線段 $BC$ 上，且 $BF : FC = {numerator} : {denominator - numerator}$。"
        question_text += f"將向量 {target_vec_str} 表示成 $x\\vec{{AB}} + y\\vec{{AD}}$ 的形式，求 $x, y$ 的值。"
        x_val = Fraction(1)
        y_val = Fraction(numerator, denominator)
        explanation = f"利用向量分解，$\\vec{{AF}} = \\vec{{AB}} + \\vec{{BF}}$。因為點 $F$ 在線段 $BC$ 上，且 $BF : FC = {numerator} : {denominator - numerator}$，所以 $\\vec{{BF}} = \\frac{{{numerator}}}{{{denominator}}}\\vec{{BC}}$。又因為 $\\vec{{BC}} = \\vec{{AD}}$ (平行四邊形性質)，所以 $\\vec{{AF}} = \\vec{{AB}} + \\frac{{{numerator}}}{{{denominator}}}\\vec{{AD}}$。故 $x=1, y={y_val}$。"

    correct_answer = f"x={x_val}, y={y_val}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "explanation": explanation
    }


def generate_coordinate_combination():
    """
    題型：將向量 c 表成向量 a 與 b 的線性組合。
    """
    # Generate coefficients x, y first to ensure integer solutions
    x_val = random.randint(-3, 3)
    y_val = random.randint(-3, 3)

    # Generate non-parallel vectors a and b
    while True:
        ax = random.randint(-5, 5)
        ay = random.randint(-5, 5)
        bx = random.randint(-5, 5)
        by = random.randint(-5, 5)

        # Avoid zero vectors or vectors that are too simple
        if (ax, ay) == (0, 0) or (bx, by) == (0, 0):
            continue
        
        # Check if a and b are parallel (determinant should not be zero)
        if ax * by - ay * bx != 0:
            break

    cx = x_val * ax + y_val * bx
    cy = x_val * ay + y_val * by

    question_text = f"將向量 $c=({cx}, {cy})$ 表成向量 $a=({ax}, {ay})$ 與 $b=({bx}, {by})$ 的線性組合。"
    question_text += f"若 $c = x_0 a + y_0 b$，求 $x_0, y_0$ 的值。"
    
    correct_answer = f"x_0={x_val}, y_0={y_val}"

    explanation = f"設 $c = x_0 a + y_0 b$，即 $({cx},{cy}) = x_0({ax},{ay}) + y_0({bx},{by})$。"
    explanation += f"展開可得 $(x_0({ax})+y_0({bx}), x_0({ay})+y_0({by}))$。"
    explanation += f"解聯立方程式：\n"
    explanation += r"$\begin{cases} x_0({ax}) + y_0({bx}) = {cx} \\ x_0({ay}) + y_0({by}) = {cy} \end{cases}$"
    explanation += f"解得 $x_0={x_val}, y_0={y_val}$。故 $c={x_val}a + {y_val}b$。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "explanation": explanation
    }

def generate_region_single_point_problem():
    """
    題型：設 O(0,0), A, B 為坐標平面上三點，且令 OP=xOA+yOB。試依指定範圍標出P點。
    (只問單一點的座標)
    """
    # Generate distinct A and B coordinates, avoiding origin and making them non-parallel
    while True:
        ax = random.randint(-5, 5)
        ay = random.randint(-5, 5)
        bx = random.randint(-5, 5)
        by = random.randint(-5, 5)
        
        if (ax, ay) == (0,0) or (bx, by) == (0,0): continue
        if ax * by - ay * bx == 0: continue # Parallel vectors OA and OB
        break

    x_val = random.choice([1, 2, random.randint(-1, 2)])
    y_val = random.choice([1, 2, random.randint(-1, 2)])
    
    px = x_val * ax + y_val * bx
    py = x_val * ay + y_val * by

    question_text = f"設 $O(0,0)$, $A({ax},{ay})$, $B({bx},{by})$ 為坐標平面上三點，且令 $\\vec{{OP}} = x\\vec{{OA}} + y\\vec{{OB}}$。"
    question_text += f"當 $x={x_val}, y={y_val}$ 時，請問 $P$ 點的坐標為何？"
    
    correct_answer = f"({px},{py})"
    
    explanation = f"已知 $\\vec{{OA}} = ({ax},{ay})$, $\\vec{{OB}} = ({bx},{by})$。"
    explanation += f"當 $x={x_val}, y={y_val}$ 時，"
    explanation += f"$\\vec{{OP}} = {x_val}\\vec{{OA}} + {y_val}\\vec{{OB}} = {x_val}({ax},{ay}) + {y_val}({bx},{by})$"
    explanation += f"$= ({x_val * ax},{x_val * ay}) + ({y_val * bx},{y_val * by})$"
    explanation += f"$= ({x_val * ax + y_val * bx},{x_val * ay + y_val * by}) = ({px},{py})$。"
    explanation += f"所以 $P$ 點的坐標為 $({px},{py})$。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "explanation": explanation
    }

def generate_region_shape_description_problem():
    """
    題型：設 O(0,0), A, B 為坐標平面上三點，且令 OP=xOA+yOB。試依指定範圍標出所有P點所形成的區域。
    (問形成的區域名稱)
    """
    while True:
        ax = random.randint(1, 4) # Keep positive for simpler region visualization conceptually
        ay = random.randint(0, 4)
        bx = random.randint(-4, 4)
        by = random.randint(1, 4)

        if (ax, ay) == (0,0) or (bx, by) == (0,0): continue
        if ax * by - ay * bx == 0: continue # Parallel vectors OA and OB
        break
    
    # Always use 0 <= x <= 1, 0 <= y <= 1 for this problem type as per example
    x_range_str = r"$0 \\le x \\le 1$"
    y_range_str = r"$0 \\le y \\le 1$"
    
    question_text = f"設 $O(0,0)$, $A({ax},{ay})$, $B({bx},{by})$ 為坐標平面上三點，且令 $\\vec{{OP}} = x\\vec{{OA}} + y\\vec{{OB}}$。"
    question_text += f"試描述當 {x_range_str}, {y_range_str} 時，所有 $P$ 點所形成的區域形狀。"
    
    correct_answer = "平行四邊形區域" # As per example: 平行四邊形OAQB所圍成的區域
    
    # Calculate the fourth vertex (Q) for the explanation
    qx = ax + bx
    qy = ay + by
    
    explanation = f"當 $0 \\le x \\le 1, 0 \\le y \\le 1$ 時，所有 $P$ 點所形成的區域為以 $O(0,0)$, $A({ax},{ay})$, $B({bx},{by})$"
    explanation += f"以及向量 $\\vec{{OA}}$ 與 $\\vec{{OB}}$ 和所決定之第四點 $Q({qx},{qy})$ 為頂點的平行四邊形所圍成的區域（含邊界）。"
    explanation += f"因此，此區域的形狀為「平行四邊形區域」。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "explanation": explanation
    }


def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip().lower().replace(' ', '')
    correct_answer = correct_answer.strip().lower().replace(' ', '')
    
    is_correct = False
    feedback = ""

    # Specific handling for coordinate_combination / geometric_decomposition (x=val, y=val)
    if "x=" in correct_answer and "y=" in correct_answer:
        try:
            # Parse correct answer: x=1/2, y=1 or x_0=1, y_0=2
            parts_correct = correct_answer.split(',')
            
            correct_x_label = parts_correct[0].split('=')[0].strip()
            correct_x_val_str = parts_correct[0].split('=')[1].strip()
            
            correct_y_label = parts_correct[1].split('=')[0].strip()
            correct_y_val_str = parts_correct[1].split('=')[1].strip()
            
            # Parse user answer
            user_x_val = None
            user_y_val = None

            # Try to find x= and y= in user input
            if f"{correct_x_label}=" in user_answer and f"{correct_y_label}=" in user_answer:
                user_parts = user_answer.split(',')
                for p in user_parts:
                    if p.startswith(f'{correct_x_label}='):
                        user_x_val = p.split('=')[1].strip()
                    elif p.startswith(f'{correct_y_label}='):
                        user_y_val = p.split('=')[1].strip()
            else: # Assume order is x, y if no labels
                user_parts = user_answer.split(',')
                if len(user_parts) == 2:
                    user_x_val = user_parts[0].strip()
                    user_y_val = user_parts[1].strip()

            if user_x_val is not None and user_y_val is not None:
                # Convert to Fraction for comparison
                correct_x_frac = Fraction(correct_x_val_str)
                correct_y_frac = Fraction(correct_y_val_str)
                user_x_frac = Fraction(user_x_val)
                user_y_frac = Fraction(user_y_val)

                if correct_x_frac == user_x_frac and correct_y_frac == user_y_frac:
                    is_correct = True
                else:
                    feedback = f"您輸入的 {correct_x_label}, {correct_y_label} 值不正確。正確答案為 ${correct_answer}$。"

        except ValueError:
            feedback = f"請檢查您的輸入格式，應為 ${correct_x_label}=值, {correct_y_label}=值$ 或 $值1, 值2$。"
        except ZeroDivisionError:
             feedback = "請檢查您的分數表示式。"
        
    # Specific handling for coordinate point ( (px,py) )
    elif correct_answer.startswith('(') and correct_answer.endswith(')'):
        try:
            # Parse correct answer (px,py)
            correct_coords_str = correct_answer[1:-1].split(',')
            correct_px = int(correct_coords_str[0].strip())
            correct_py = int(correct_coords_str[1].strip())

            # Parse user answer, expecting (px,py)
            if user_answer.startswith('(') and user_answer.endswith(')'):
                user_coords_str = user_answer[1:-1].split(',')
                if len(user_coords_str) == 2:
                    user_px = int(user_coords_str[0].strip())
                    user_py = int(user_coords_str[1].strip())
                    
                    if user_px == correct_px and user_py == correct_py:
                        is_correct = True
                    else:
                        feedback = f"您輸入的坐標不正確。正確答案為 ${correct_answer}$。"
                else:
                    feedback = f"請輸入正確的坐標格式，例如 $(1,2)$。"
            else:
                 feedback = f"請輸入正確的坐標格式，例如 $(1,2)$。"

        except (ValueError, IndexError):
            feedback = f"請輸入正確的坐標格式，例如 $(1,2)$。"

    # Specific handling for region shape description
    elif correct_answer == "平行四邊形區域":
        # Accept variations like "平行四邊形"
        if "平行四邊形" in user_answer:
            is_correct = True
        else:
            feedback = f"您輸入的形狀描述不正確。正確答案應為「{correct_answer}」。"

    if is_correct:
        # Avoid repeating the answer if it's already explicitly mentioned in feedback for specific formats
        if not ("x=" in correct_answer or correct_answer.startswith('(') or "平行四邊形區域" == correct_answer):
            feedback = f"完全正確！答案是 ${correct_answer}$。"
        else:
            feedback = f"完全正確！"
    elif not feedback: # If no specific feedback was set, provide a generic one
        feedback = f"答案不正確。正確答案應為：${correct_answer}$"
    
    return {"correct": is_correct, "result": feedback, "next_question": True}