import random
import math
from fractions import Fraction

# Helper function for matrix-vector multiplication
def multiply_matrix_vector(matrix, vector):
    x, y = vector
    # Matrix is assumed to be 2x2: [[a, b], [c, d]]
    # Vector: [x, y]
    # Result: [a*x + b*y, c*x + d*y]
    
    new_x = matrix[0][0] * x + matrix[0][1] * y
    new_y = matrix[1][0] * x + matrix[1][1] * y
    return (new_x, new_y)

# Helper function to format a number for LaTeX (e.g., \\frac{1}{2})
def format_number_latex(n):
    if isinstance(n, int):
        return str(n)
    if isinstance(n, Fraction):
        if n.denominator == 1:
            return str(n.numerator)
        # Using double braces for LaTeX fraction in f-string
        return f"\\frac{{{n.numerator}}}{{{n.denominator}}}"
    if isinstance(n, float):
        if n.is_integer():
            return str(int(n))
        # Try to convert float to fraction for better representation if simple
        try:
            f = Fraction(n).limit_denominator(100)
            if abs(f - n) < 1e-9: # Check if fraction is a good approximation
                return f"\\frac{{{f.numerator}}}{{{f.denominator}}}"
        except Exception:
            pass # Fallback to float string
        return f"{n:.4f}" # Default to 4 decimal places for floats
    return str(n) # Fallback for other types

# Helper function to format a number for clean string answer (e.g., "1/2", not "\\frac{1}{2}")
def format_number_clean(n):
    if isinstance(n, int):
        return str(n)
    if isinstance(n, Fraction):
        if n.denominator == 1:
            return str(n.numerator)
        return f"{n.numerator}/{n.denominator}"
    if isinstance(n, float):
        if n.is_integer():
            return str(int(n))
        try:
            f = Fraction(n).limit_denominator(100)
            if abs(f - n) < 1e-9:
                return f"{f.numerator}/{f.denominator}"
        except Exception:
            pass
        return f"{n:.4f}"
    return str(n)

# Helper function to format a point (x, y) into LaTeX
def format_point_latex(point):
    x_str = format_number_latex(point[0])
    y_str = format_number_latex(point[1])
    return f"$({x_str}, {y_str})$"

# Helper function to format a point (x, y) into a clean string for answer checking
def format_point_clean_answer(point):
    x_str = format_number_clean(point[0])
    y_str = format_number_clean(point[1])
    return f"({x_str}, {y_str})"

def generate_scaling_problem():
    shape_type = random.choice(['point', 'rectangle'])
    
    if shape_type == 'point':
        px = random.randint(-10, 10)
        py = random.randint(-10, 10)
        
        # Ensure the point is not the origin for a more engaging problem
        if px == 0 and py == 0:
            px = random.randint(1, 5) 
            py = random.randint(1, 5)
        
        # Scaling factors
        sx = Fraction(random.randint(1, 4), random.choice([1, 2, 3, 4]))
        sy = Fraction(random.randint(1, 4), random.choice([1, 2, 3, 4]))
        
        # Ensure at least one scaling factor is not 1 for a non-trivial transformation
        if sx == 1 and sy == 1:
            if random.random() < 0.5:
                sx = Fraction(random.choice([2, 3]))
            else:
                sy = Fraction(random.choice([2, 3]))
            # Fallback to guarantee non-trivial if random choice still resulted in (1,1)
            if sx == 1 and sy == 1: 
                sx = Fraction(2,1) 
        
        matrix = [[sx, 0], [0, sy]]
        p_prime = multiply_matrix_vector(matrix, (px, py))
        
        question_text = (
            f"點 $P{format_point_latex((px, py))}$ 經過伸縮變換，"
            f"沿 $x$ 軸方向伸縮 ${format_number_latex(sx)}$ 倍，沿 $y$ 軸方向伸縮 ${format_number_latex(sy)}$ 倍，"
            f"求變換後點 $P'$ 的坐標。"
        )
        correct_answer_str = format_point_clean_answer(p_prime)
        
        return {
            "question_text": question_text,
            "answer": correct_answer_str,
            "correct_answer": correct_answer_str
        }
        
    else: # rectangle (for area or multiple points)
        x1 = random.randint(-5, 5)
        y1 = random.randint(-5, 5)
        width = random.randint(2, 8)
        height = random.randint(2, 8)
        
        p = (x1, y1)
        q = (x1 + width, y1)
        r = (x1 + width, y1 + height)
        s = (x1, y1 + height)
        
        sx = Fraction(random.choice([1, 2, 3]), random.choice([1, 2]))
        sy = Fraction(random.choice([1, 2, 3]), random.choice([1, 2]))
        
        if sx == 1 and sy == 1: 
            if random.random() < 0.5:
                sx = Fraction(random.choice([2, 3]))
            else:
                sy = Fraction(random.choice([2, 3]))

        matrix = [[sx, 0], [0, sy]]
        
        p_prime = multiply_matrix_vector(matrix, p)
        q_prime = multiply_matrix_vector(matrix, q)
        r_prime = multiply_matrix_vector(matrix, r)
        s_prime = multiply_matrix_vector(matrix, s)
        
        original_area = abs(width * height)
        transformed_area = original_area * (sx * sy)
        
        chosen_question = random.choice(['coordinates', 'area'])
        
        if chosen_question == 'coordinates':
            target_point_label = random.choice(['P', 'Q', 'R', 'S'])
            if target_point_label == 'P': transformed_target_point = p_prime
            elif target_point_label == 'Q': transformed_target_point = q_prime
            elif target_point_label == 'R': transformed_target_point = r_prime
            else: transformed_target_point = s_prime
            
            question_text = (
                f"已知矩形 $PQRS$ 的頂點坐標為 $P{format_point_latex(p)}$, $Q{format_point_latex(q)}$, "
                f"$R{format_point_latex(r)}$, $S{format_point_latex(s)}$。將此矩形以原點 $O$ 為中心，"
                f"沿著 $x$ 軸方向伸縮 ${format_number_latex(sx)}$ 倍，沿著 $y$ 軸方向伸縮 ${format_number_latex(sy)}$ 倍，"
                f"求變換後點 ${target_point_label}'$ 的坐標。"
            )
            correct_answer_str = format_point_clean_answer(transformed_target_point)

        else: # chosen_question == 'area'
            question_text = (
                f"已知矩形 $PQRS$ 的頂點坐標為 $P{format_point_latex(p)}$, $Q{format_point_latex(q)}$, "
                f"$R{format_point_latex(r)}$, $S{format_point_latex(s)}$。將此矩形以原點 $O$ 為中心，"
                f"沿著 $x$ 軸方向伸縮 ${format_number_latex(sx)}$ 倍，沿著 $y$ 軸方向伸縮 ${format_number_latex(sy)}$ 倍，"
                f"求變換後四邊形 $P'Q'R'S'$ 的面積。"
            )
            correct_answer_str = format_number_clean(transformed_area)
            
        return {
            "question_text": question_text,
            "answer": correct_answer_str,
            "correct_answer": correct_answer_str
        }

def generate_rotation_problem():
    px = random.randint(-8, 8)
    py = random.randint(-8, 8)
    
    # Ensure point is not origin for a non-trivial rotation problem
    if px == 0 and py == 0:
        px = random.randint(1, 5)
        py = random.randint(1, 5)
    
    # Use angles that result in exact sin/cos values (0, 90, 180, 270 degrees)
    # Avoid 0 degrees as it's a trivial rotation.
    angle_degrees = random.choice([90, -90, 180, -180, 270, -270]) 
    
    angle_rad = math.radians(angle_degrees)
    
    # Round to avoid floating point inaccuracies for 0, 1, -1 values
    cos_val = round(math.cos(angle_rad), 5)
    sin_val = round(math.sin(angle_rad), 5)

    rotation_matrix = [
        [cos_val, -sin_val],
        [sin_val, cos_val]
    ]
    
    p_prime = multiply_matrix_vector(rotation_matrix, (px, py))
    
    direction = "逆時針" if angle_degrees > 0 else "順時針"
    abs_angle = abs(angle_degrees)
    
    question_text = (
        f"點 $P{format_point_latex((px, py))}$ 以原點 $O$ 為中心，"
        f"{direction}旋轉 ${abs_angle}°$ 後得到 $P'$ 點，求 $P'$ 點的坐標。"
    )
    correct_answer_str = format_point_clean_answer(p_prime)
    
    return {
        "question_text": question_text,
        "answer": correct_answer_str,
        "correct_answer": correct_answer_str
    }

def generate_reflection_problem():
    px = random.randint(-8, 8)
    py = random.randint(-8, 8)
    
    reflection_type = random.choice(['x_axis', 'y_axis', 'y=x', 'y=-x'])
    
    # Ensure point is not on the reflection line for a non-trivial transformation result
    if reflection_type == 'x_axis':
        matrix = [[1, 0], [0, -1]]
        line_desc = "$x$ 軸"
        if py == 0: # Point on x-axis, move it off
             py = random.choice([-5, 5]) 
        
    elif reflection_type == 'y_axis':
        matrix = [[-1, 0], [0, 1]]
        line_desc = "$y$ 軸"
        if px == 0: # Point on y-axis, move it off
            px = random.choice([-5, 5]) 
            
    elif reflection_type == 'y=x':
        matrix = [[0, 1], [1, 0]]
        line_desc = "直線 $y=x$"
        if px == py: # Point on y=x, move it off
             px += random.choice([-1, 1])
             py -= random.choice([-1, 1]) 
        
    else: # y=-x
        matrix = [[0, -1], [-1, 0]]
        line_desc = "直線 $y=-x$"
        if px == -py: # Point on y=-x, move it off
             px += random.choice([-1, 1])
             py += random.choice([-1, 1])
    
    p_prime = multiply_matrix_vector(matrix, (px, py))
    
    question_text = (
        f"點 $P{format_point_latex((px, py))}$ 對{line_desc}鏡射後得到 $P'$ 點，求 $P'$ 點的坐標。"
    )
    correct_answer_str = format_point_clean_answer(p_prime)
    
    return {
        "question_text": question_text,
        "answer": correct_answer_str,
        "correct_answer": correct_answer_str
    }

def generate_shear_problem():
    shape_type = random.choice(['point', 'rectangle'])
    
    shear_direction = random.choice(['horizontal', 'vertical'])
    k = random.choice([-3, -2, -1, 1, 2, 3]) # Shear factor (non-zero for a non-trivial shear)
    
    if shape_type == 'point':
        px = random.randint(-10, 10)
        py = random.randint(-10, 10)
        
        if shear_direction == 'horizontal':
            matrix = [[1, k], [0, 1]]
            shear_desc = f"水平推移 $y$ 坐標的 ${format_number_latex(k)}$ 倍"
        else: # vertical
            matrix = [[1, 0], [k, 1]]
            shear_desc = f"垂直推移 $x$ 坐標的 ${format_number_latex(k)}$ 倍"
            
        p_prime = multiply_matrix_vector(matrix, (px, py))
        
        question_text = (
            f"點 $P{format_point_latex((px, py))}$ 經過{shear_desc}變換，求變換後點 $P'$ 的坐標。"
        )
        correct_answer_str = format_point_clean_answer(p_prime)
        
        return {
            "question_text": question_text,
            "answer": correct_answer_str,
            "correct_answer": correct_answer_str
        }
    else: # rectangle (for area or multiple points)
        x1 = random.randint(-5, 5)
        y1 = random.randint(-5, 5)
        width = random.randint(2, 8)
        height = random.randint(2, 8)
        
        p = (x1, y1)
        q = (x1 + width, y1)
        r = (x1 + width, y1 + height)
        s = (x1, y1 + height)
        
        if shear_direction == 'horizontal':
            matrix = [[1, k], [0, 1]]
            shear_desc = f"水平推移 $y$ 坐標的 ${format_number_latex(k)}$ 倍"
        else: # vertical
            matrix = [[1, 0], [k, 1]]
            shear_desc = f"垂直推移 $x$ 坐標的 ${format_number_latex(k)}$ 倍"
            
        p_prime = multiply_matrix_vector(matrix, p)
        q_prime = multiply_matrix_vector(matrix, q)
        r_prime = multiply_matrix_vector(matrix, r)
        s_prime = multiply_matrix_vector(matrix, s)
        
        original_area = abs(width * height)
        # Determinant of shear matrix is 1, so area remains the same.
        transformed_area = original_area
        
        chosen_question = random.choice(['coordinates', 'area'])
        
        if chosen_question == 'coordinates':
            target_point_label = random.choice(['P', 'Q', 'R', 'S'])
            if target_point_label == 'P': transformed_target_point = p_prime
            elif target_point_label == 'Q': transformed_target_point = q_prime
            elif target_point_label == 'R': transformed_target_point = r_prime
            else: transformed_target_point = s_prime
            
            question_text = (
                f"已知矩形 $PQRS$ 的頂點坐標為 $P{format_point_latex(p)}$, $Q{format_point_latex(q)}$, "
                f"$R{format_point_latex(r)}$, $S{format_point_latex(s)}$。將此矩形以原點 $O$ 為基準，"
                f"經過{shear_desc}變換，求變換後點 ${target_point_label}'$ 的坐標。"
            )
            correct_answer_str = format_point_clean_answer(transformed_target_point)

        else: # chosen_question == 'area'
            question_text = (
                f"已知矩形 $PQRS$ 的頂點坐標為 $P{format_point_latex(p)}$, $Q{format_point_latex(q)}$, "
                f"$R{format_point_latex(r)}$, $S{format_point_latex(s)}$。將此矩形以原點 $O$ 為基準，"
                f"經過{shear_desc}變換，求變換後四邊形 $P'Q'R'S'$ 的面積。"
            )
            correct_answer_str = format_number_clean(transformed_area)
            
        return {
            "question_text": question_text,
            "answer": correct_answer_str,
            "correct_answer": correct_answer_str
        }

def generate(level=1):
    problem_type = random.choice(['scaling', 'rotation', 'reflection', 'shear'])
    
    if problem_type == 'scaling':
        return generate_scaling_problem()
    elif problem_type == 'rotation':
        return generate_rotation_problem()
    elif problem_type == 'reflection':
        return generate_reflection_problem()
    elif problem_type == 'shear':
        return generate_shear_problem()

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    user_answer and correct_answer are strings.
    The format for coordinates is "(x,y)", and for area is "value".
    Numbers can be integers, fractions like "1/2", or decimals.
    """
    user_answer = user_answer.strip().replace(" ", "")
    correct_answer = correct_answer.strip().replace(" ", "")
    
    is_correct = False
    
    # Try to parse as coordinates (x,y)
    if user_answer.startswith('(') and user_answer.endswith(')'):
        try:
            user_parts = user_answer[1:-1].split(',')
            correct_parts = correct_answer[1:-1].split(',')
            
            if len(user_parts) == 2 and len(correct_parts) == 2:
                # Use float(Fraction(string)) to handle integers, floats, and fractions robustly
                # Fraction constructor can handle "1/2", "0.5", "1", "-3", etc.
                ux = float(Fraction(user_parts[0]))
                uy = float(Fraction(user_parts[1]))
                cx = float(Fraction(correct_parts[0]))
                cy = float(Fraction(correct_parts[1]))
                
                # Compare with a tolerance for floats to account for precision issues
                if abs(ux - cx) < 1e-6 and abs(uy - cy) < 1e-6:
                    is_correct = True
        except (ValueError, ZeroDivisionError):
            pass # Parsing failed, not a valid coordinate answer
    
    # Try to parse as a single number (for area)
    if not is_correct:
        try:
            user_val = float(Fraction(user_answer))
            correct_val = float(Fraction(correct_answer))
            if abs(user_val - correct_val) < 1e-6:
                is_correct = True
        except (ValueError, ZeroDivisionError):
            pass # Parsing failed, not a valid number answer
            
    # As a final fallback, check for exact string match.
    # This can catch cases like "1/2" == "1/2" if float comparison wasn't exact enough for display.
    if not is_correct:
        is_correct = (user_answer == correct_answer)
        
    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}