import random
from fractions import Fraction

def generate(level=1):
    """
    生成「向量表示」相關題目。
    包含：
    1. 向量相等定義判斷 (幾何描述)
    2. 點座標表示向量
    3. 平行四邊形補點問題
    """
    problem_type = random.choice([
        'geometric_equality_definition',
        'vector_from_points',
        'find_parallelogram_vertex'
    ])
    
    if problem_type == 'geometric_equality_definition':
        return generate_geometric_equality_definition_problem()
    elif problem_type == 'vector_from_points':
        return generate_vector_from_points_problem()
    else: # 'find_parallelogram_vertex'
        return generate_find_parallelogram_vertex_problem()

def generate_geometric_equality_definition_problem():
    """
    生成判斷向量相等定義的題目。
    要求學生根據向量的大小和方向來判斷是否相等。
    """
    mag1 = random.randint(3, 10)
    mag2_different = random.choice([True, False]) # Whether magnitude of v is different
    
    mag2 = random.randint(3, 10)
    if not mag2_different:
        mag2 = mag1 # Magnitudes are equal
    else:
        while mag2 == mag1: # Ensure it's different if intended
            mag2 = random.randint(3, 10)

    directions = ['東', '西', '南', '北', '東北', '西北', '東南', '西南']
    dir1 = random.choice(directions)
    
    # Define opposite directions for parallelism check
    opposite_dirs = {
        '東': '西', '西': '東', '南': '北', '北': '南',
        '東北': '西南', '西北': '東南', '東南': '西北', '西南': '東北'
    }

    direction_scenario = random.choice(['same', 'opposite', 'different'])
    
    if direction_scenario == 'same':
        dir2 = dir1
    elif direction_scenario == 'opposite':
        dir2 = opposite_dirs.get(dir1, dir1) # Fallback to dir1 if no opposite defined (shouldn't happen here)
    else: # 'different'
        # Pick a direction that is neither dir1 nor its opposite
        possible_dirs = [d for d in directions if d != dir1 and d != opposite_dirs.get(dir1, '')]
        if possible_dirs:
            dir2 = random.choice(possible_dirs)
        else: # Fallback, should not be needed with 8 directions
            dir2 = random.choice([d for d in directions if d != dir1])


    # The actual equality condition: same magnitude AND same direction
    is_equal = (mag1 == mag2) and (dir1 == dir2)

    question_text = (
        f"令向量 $\\vec{{u}}$ 的大小為 ${mag1}$ 單位，方向為{dir1}方。<br>"
        f"令向量 $\\vec{{v}}$ 的大小為 ${mag2}$ 單位，方向為{dir2}方。<br>"
        f"請問向量 $\\vec{{u}}$ 和 $\\vec{{v}}$ 是否相等？ (請回答「是」或「否」)"
    )
    
    correct_answer = "是" if is_equal else "否"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_vector_from_points_problem():
    """
    生成從兩點座標計算向量分量的題目。
    """
    # Generate coordinates for two points A and B
    ax, ay = random.randint(-10, 10), random.randint(-10, 10)
    bx, by = random.randint(-10, 10), random.randint(-10, 10)

    # Calculate vector AB components
    vec_ab_x = bx - ax
    vec_ab_y = by - ay

    question_text = (
        f"已知坐標平面上的兩點 $A({ax}, {ay})$ 與 $B({bx}, {by})$。<br>"
        f"請問向量 $\\vec{{AB}}$ 為何？ (請以 $(x,y)$ 格式回答)"
    )
    
    correct_answer = f"({vec_ab_x},{vec_ab_y})"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_find_parallelogram_vertex_problem():
    """
    生成在平行四邊形中尋找缺失頂點座標的題目。
    """
    # Generate coordinates for three points A, B, C
    ax, ay = random.randint(-10, 10), random.randint(-10, 10)
    bx, by = random.randint(-10, 10), random.randint(-10, 10)
    cx, cy = random.randint(-10, 10), random.randint(-10, 10)

    # Ensure points are not collinear to form a valid parallelogram.
    # If A, B, C are collinear, then vector AB is parallel to BC.
    # Cross product (B-A) x (C-B) will be zero.
    # (bx-ax)*(cy-by) - (by-ay)*(cx-bx) should not be zero.
    while (bx - ax) * (cy - by) - (by - ay) * (cx - bx) == 0:
        ax, ay = random.randint(-10, 10), random.randint(-10, 10)
        bx, by = random.randint(-10, 10), random.randint(-10, 10)
        cx, cy = random.randint(-10, 10), random.randint(-10, 10)

    # For parallelogram ABCD, we have vector AB = vector DC
    # This means (Bx - Ax, By - Ay) = (Cx - Dx, Cy - Dy)
    # So Dx = Cx - (Bx - Ax) = Cx + Ax - Bx
    # And Dy = Cy - (By - Ay) = Cy + Ay - By
    dx = cx + ax - bx
    dy = cy + ay - by
    
    # It's also possible to calculate D using AD = BC, which gives D = A + (C-B) = (Ax + Cx - Bx, Ay + Cy - By)
    # Wait, the example uses AD = BC. Let's follow that.
    # AD = BC means (Dx - Ax, Dy - Ay) = (Cx - Bx, Cy - By)
    # So Dx = Ax + (Cx - Bx)
    # And Dy = Ay + (Cy - By)
    dx = ax + cx - bx
    dy = ay + cy - by

    question_text = (
        f"已知坐標平面上的三點 $A({ax},{ay})$、$B({bx},{by})$ 與 $C({cx},{cy})$，"
        f"且 $ABCD$ 為平行四邊形。<br>"
        f"求 $D$ 點的坐標。(請以 $(x,y)$ 格式回答)"
    )
    
    correct_answer = f"({dx},{dy})"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip().replace(" ", "") # Remove spaces for easier comparison
    correct_answer = correct_answer.strip().replace(" ", "")

    is_correct = (user_answer.lower() == correct_answer.lower()) # Case-insensitive for "是/否"

    if not is_correct:
        # For coordinate answers, try parsing them
        try:
            # Expected format: (x,y)
            if user_answer.startswith('(') and user_answer.endswith(')'):
                user_coords_str = user_answer[1:-1].split(',')
                correct_coords_str = correct_answer[1:-1].split(',')
                
                if len(user_coords_str) == 2 and len(correct_coords_str) == 2:
                    user_x = int(user_coords_str[0])
                    user_y = int(user_coords_str[1])
                    correct_x = int(correct_coords_str[0])
                    correct_y = int(correct_coords_str[1])
                    
                    if user_x == correct_x and user_y == correct_y:
                        is_correct = True
        except ValueError:
            pass # Not a valid coordinate format, or parsing failed

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}