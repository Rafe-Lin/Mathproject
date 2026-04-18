import random
import math
import re # For parsing coordinate strings

# Helper function to generate a 3D point (x, y, z)
def _generate_3d_point(min_val=-5, max_val=5):
    x = random.randint(min_val, max_val)
    y = random.randint(min_val, max_val)
    z = random.randint(min_val, max_val)
    return (x, y, z)

# Helper function to format a 3D point as a string for LaTeX display
def _format_point(point):
    x, y, z = point
    return f"({{x}}, {{y}}, {{z}})"

# Helper function to format a vector as a string for LaTeX display
def _format_vector(vector):
    x, y, z = vector
    return f"({{x}}, {{y}}, {{z}})"

# Helper function to calculate vector magnitude and format
def _calculate_and_format_magnitude(vector):
    x, y, z = vector
    magnitude_squared = x**2 + y**2 + z**2
    magnitude = math.sqrt(magnitude_squared)
    
    if magnitude.is_integer():
        return str(int(magnitude))
    else:
        # Round to 2 decimal places for non-integer magnitudes
        return f"{magnitude:.2f}"


def generate(level=1):
    """
    生成「空間向量坐標化」相關題目。
    包含：
    1. 位置向量的坐標表示法。
    2. 由兩點坐標表示向量的方法。
    3. 計算向量的長度 (大小)。
    4. 平行四邊形頂點坐標。
    """
    problem_type = random.choice([
        'position_vector', 
        'two_point_vector', 
        'vector_magnitude_from_points', 
        'vector_magnitude_from_components',
        'parallelogram_vertex'
    ])
    
    if level == 1:
        min_coord, max_coord = -5, 5
    elif level == 2:
        min_coord, max_coord = -8, 8
    else: # level 3 and higher
        min_coord, max_coord = -10, 10

    if problem_type == 'position_vector':
        return _generate_position_vector_problem(min_coord, max_coord)
    elif problem_type == 'two_point_vector':
        return _generate_two_point_vector_problem(min_coord, max_coord)
    elif problem_type == 'vector_magnitude_from_points':
        return _generate_vector_magnitude_problem(min_coord, max_coord, from_points=True, level=level)
    elif problem_type == 'vector_magnitude_from_components':
        return _generate_vector_magnitude_problem(min_coord, max_coord, from_points=False, level=level)
    elif problem_type == 'parallelogram_vertex':
        return _generate_parallelogram_problem(min_coord, max_coord)

def _generate_position_vector_problem(min_coord, max_coord):
    p_point = _generate_3d_point(min_coord, max_coord)
    
    question_text = f"若空間中有一點 $P{_format_point(p_point)}$，求向量 $\\vec{{OP}}$ 的坐標表示法。"
    correct_answer = _format_vector(p_point)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def _generate_two_point_vector_problem(min_coord, max_coord):
    a_point = _generate_3d_point(min_coord, max_coord)
    b_point = _generate_3d_point(min_coord, max_coord)
    
    vector_ab = (b_point[0] - a_point[0], b_point[1] - a_point[1], b_point[2] - a_point[2])
    
    question_text = (
        f"空間中兩點 $A{_format_point(a_point)}$、$B{_format_point(b_point)}$，"
        f"求向量 $\\vec{{AB}}$ 的坐標表示法。"
    )
    correct_answer = _format_vector(vector_ab)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def _generate_vector_magnitude_problem(min_coord, max_coord, from_points=True, level=1):
    if from_points:
        a_point = _generate_3d_point(min_coord, max_coord)
        b_point = _generate_3d_point(min_coord, max_coord)
        vector_components = (b_point[0] - a_point[0], b_point[1] - a_point[1], b_point[2] - a_point[2])
        
        question_text = (
            f"空間中兩點 $A{_format_point(a_point)}$、$B{_format_point(b_point)}$，"
            f"求向量 $\\vec{{AB}}$ 的長度 $|\\vec{{AB}}|$。"
        )
    else:
        # Generate vector components directly. Try to make magnitude an integer for lower levels.
        if level <= 2 and random.random() < 0.7: # High chance to get integer magnitude
            # Pythagorean triples or simple variations
            triples = [(3, 4, 0), (1, 2, 2), (2, 2, 1), (0, 3, 4), (4, 0, 3), (2, 1, 2)]
            choice = random.choice(triples)
            vector_components = tuple(c * random.choice([-1, 1]) for c in choice)
            
            # Add a small random offset to occasionally break perfect squares
            if random.random() < 0.2:
                 vector_components = (
                    vector_components[0] + random.randint(-1,1) if vector_components[0] != 0 else random.randint(-1,1),
                    vector_components[1] + random.randint(-1,1) if vector_components[1] != 0 else random.randint(-1,1),
                    vector_components[2] + random.randint(-1,1) if vector_components[2] != 0 else random.randint(-1,1)
                )
        else: # General random components
            vector_components = _generate_3d_point(min_coord, max_coord)
        
        # Ensure not zero vector unless coordinates are all zero
        if all(c == 0 for c in vector_components):
             vector_components = (random.choice([-1, 1]), random.randint(-1, 1), random.randint(-1, 1)) # default to a non-zero vector

        question_text = f"已知向量 $\\vec{{v}} = {_format_vector(vector_components)}$，求 $|\\vec{{v}}|$ 的值。"

    correct_answer = _calculate_and_format_magnitude(vector_components)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def _generate_parallelogram_problem(min_coord, max_coord):
    a_point = _generate_3d_point(min_coord, max_coord)
    b_point = _generate_3d_point(min_coord, max_coord)
    c_point = _generate_3d_point(min_coord, max_coord)

    # Ensure A, B, C are distinct to avoid trivial or degenerate cases
    while a_point == b_point or b_point == c_point or a_point == c_point:
        b_point = _generate_3d_point(min_coord, max_coord)
        c_point = _generate_3d_point(min_coord, max_coord)

    # For parallelogram ABCD, vector AD = vector BC
    # This means D = A + vector BC
    # vector BC = (Cx - Bx, Cy - By, Cz - Bz)
    vec_bc = (c_point[0] - b_point[0], c_point[1] - b_point[1], c_point[2] - b_point[2])
    
    d_point = (a_point[0] + vec_bc[0], a_point[1] + vec_bc[1], a_point[2] + vec_bc[2])
    
    question_text = (
        f"空間中，已知 $A{_format_point(a_point)}$，$B{_format_point(b_point)}$，$C{_format_point(c_point)}$ "
        f"為平行四邊形 $ABCD$ 的三個頂點。求 $D$ 點的坐標。"
    )
    correct_answer = _format_point(d_point)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip().replace(' ', '')
    correct_answer = correct_answer.strip().replace(' ', '')
    
    is_correct = False
    feedback = ""

    # Try to parse as a coordinate tuple
    # This regex handles both integers and floats for each coordinate
    coord_pattern = r"\((-?\d+(\.\d+)?),(-?\d+(\.\d+)?),(-?\d+(\.\d+)?)\)"
    
    user_match = re.match(coord_pattern, user_answer)
    correct_match = re.match(coord_pattern, correct_answer)

    if user_match and correct_match:
        # Extract numerical parts (groups 1, 3, 5 are the full numbers, e.g., -5 or 3.14)
        user_coords = tuple(float(user_match.group(i)) for i in [1, 3, 5])
        correct_coords = tuple(float(correct_match.group(i)) for i in [1, 3, 5])
        
        # Compare coordinates with a small tolerance for floating point numbers
        if all(math.isclose(uc, cc, rel_tol=1e-9, abs_tol=1e-9) for uc, cc in zip(user_coords, correct_coords)):
            is_correct = True
            feedback = f"完全正確！答案是 ${correct_answer}$。"
        else:
            feedback = f"答案不正確。正確答案應為：${correct_answer}$"
    else:
        # If not coordinates, try to parse as a single float (for magnitude problems)
        try:
            user_val = float(user_answer)
            correct_val = float(correct_answer)
            if math.isclose(user_val, correct_val, rel_tol=1e-9, abs_tol=1e-9):
                is_correct = True
                feedback = f"完全正確！答案是 ${correct_answer}$。"
            else:
                feedback = f"答案不正確。正確答案應為：${correct_answer}$"
        except ValueError:
            # Fallback for exact string comparison if float conversion fails
            # This covers cases where user might input in a non-parseable format
            # or if correct_answer was some specific string.
            if user_answer.lower() == correct_answer.lower():
                 is_correct = True
                 feedback = f"完全正確！答案是 ${correct_answer}$。"
            else:
                feedback = f"答案不正確。正確答案應為：${correct_answer}$"

    return {"correct": is_correct, "result": feedback, "next_question": True}