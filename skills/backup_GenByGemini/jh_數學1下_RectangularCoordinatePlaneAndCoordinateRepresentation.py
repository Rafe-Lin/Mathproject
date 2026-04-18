import random
from fractions import Fraction

def generate(level=1):
    """
    生成「直角坐標平面與坐標表示法」相關題目 (標準 LaTeX 範本)。
    包含：
    1. 坐標與距離
    2. 點的平移
    3. 點的逆向平移
    4. 象限判斷
    5. 坐標軸判斷
    """
    problem_type = random.choice(['identify_and_distance', 'translation', 'reverse_translation', 'quadrant', 'axis_location'])
    
    if problem_type == 'identify_and_distance':
        return generate_identify_and_distance_problem()
    elif problem_type == 'translation':
        return generate_translation_problem()
    elif problem_type == 'reverse_translation':
        return generate_reverse_translation_problem()
    elif problem_type == 'quadrant':
        return generate_quadrant_problem()
    else: # axis_location
        return generate_axis_location_problem()

def generate_identify_and_distance_problem():
    # 題型：如果數對 ( x, y ) 表示 P 點的位置，那麼 P 點的 x 坐標是 __ ， y 坐標是 __ 。 P 點到 x 軸的距離是 __ ，到 y 軸的距離是 __ 。
    x = random.randint(-10, 10)
    y = random.randint(-10, 10)
    
    # 確保 x, y 不為 0，讓距離問題有意義
    while x == 0:
        x = random.randint(-10, 10)
    while y == 0:
        y = random.randint(-10, 10)
        
    dist_to_x_axis = abs(y)
    dist_to_y_axis = abs(x)
    
    question_text = f"如果數對 $({x}, {y})$ 表示 $P$ 點的位置，那麼 $P$ 點的 x 坐標是 _____ ， y 坐標是 _____ 。<br>$P$ 點到 x 軸的距離是 _____ ，到 y 軸的距離是 _____ 。(請依序填寫並以逗號分隔)"
    correct_answer = f"{x},{y},{dist_to_x_axis},{dist_to_y_axis}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_translation_problem():
    # 題型：坐標平面上有一點 A (x, y)，若從 A 點出發，先...再...，到達 B 點，則 B 點的坐標為何？
    start_x = random.randint(-10, 10)
    start_y = random.randint(-10, 10)
    end_x, end_y = start_x, start_y
    
    moves = []
    num_moves = random.choice([1, 2])
    
    # 確保平移方向不重複
    directions_to_use = random.sample(['horizontal', 'vertical'], num_moves)
    
    for direction in directions_to_use:
        dist = random.randint(1, 8)
        if direction == 'horizontal':
            h_dir_str = random.choice(['左', '右'])
            if h_dir_str == '右':
                end_x += dist
            else:
                end_x -= dist
            moves.append(f"向{h_dir_str} {dist} 單位")
        else: # vertical
            v_dir_str = random.choice(['上', '下'])
            if v_dir_str == '上':
                end_y += dist
            else:
                end_y -= dist
            moves.append(f"向{v_dir_str} {dist} 單位")
            
    moves_str = "，再".join(moves)
    question_text = f"坐標平面上有一點 $A({start_x}, {start_y})$，若從 $A$ 點出發，{moves_str}，到達 $B$ 點，則 $B$ 點的坐標為何？(請用數對表示法作答，例如：(x,y))"
    correct_answer = f"({end_x},{end_y})"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_reverse_translation_problem():
    # 題型：從 E 點出發，先...再...，到達 F (x, y)，則 E 點的坐標為何？
    end_x = random.randint(-10, 10)
    end_y = random.randint(-10, 10)
    start_x, start_y = end_x, end_y

    moves = []
    num_moves = random.choice([1, 2])
    
    directions_to_use = random.sample(['horizontal', 'vertical'], num_moves)
    
    for direction in directions_to_use:
        dist = random.randint(1, 8)
        if direction == 'horizontal':
            h_dir_str = random.choice(['左', '右'])
            if h_dir_str == '右':
                start_x -= dist  # Reverse logic
            else:
                start_x += dist  # Reverse logic
            moves.append(f"向{h_dir_str} {dist} 單位")
        else: # vertical
            v_dir_str = random.choice(['上', '下'])
            if v_dir_str == '上':
                start_y -= dist  # Reverse logic
            else:
                start_y += dist  # Reverse logic
            moves.append(f"向{v_dir_str} {dist} 單位")

    moves_str = "，再".join(moves)
    question_text = f"坐標平面上有一點 $E$，若從 $E$ 點出發，{moves_str}，最後到達一點 $F({end_x}, {end_y})$，則 $E$ 點的坐標為何？(請用數對表示法作答，例如：(x,y))"
    correct_answer = f"({start_x},{start_y})"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_quadrant_problem():
    # 題型：坐標平面上有一點 P (x, y)，請問 P 點在哪一個象限？
    x = random.randint(-10, 10)
    y = random.randint(-10, 10)

    # 確保點不在坐標軸上
    while x == 0:
        x = random.randint(-10, 10)
    while y == 0:
        y = random.randint(-10, 10)

    if x > 0 and y > 0:
        quadrant = "一"
    elif x < 0 and y > 0:
        quadrant = "二"
    elif x < 0 and y < 0:
        quadrant = "三"
    else: # x > 0 and y < 0
        quadrant = "四"

    question_text = f"坐標平面上有一點 $P({x}, {y})$，請問 $P$ 點在哪一個象限？(請填國字數字，例如：一、二、三、四)"
    correct_answer = quadrant

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_axis_location_problem():
    # 題型：坐標平面上有一點 P (x, y)，請問 P 點在哪一個坐標軸上？
    if random.random() < 0.5:
        x = 0
        y = random.randint(-10, 10)
        while y == 0: # 避免原點
             y = random.randint(-10, 10)
    else:
        x = random.randint(-10, 10)
        y = 0
        while x == 0: # 避免原點
             x = random.randint(-10, 10)
    
    location = "y 軸" if x == 0 else "x 軸"

    question_text = f"坐標平面上有一點 $P({x}, {y})$，請問 $P$ 點在哪一個坐標軸上？"
    correct_answer = location

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()

    # 針對數對 (x,y) 格式進行正規化
    if correct_answer.startswith('('):
        user_answer = user_answer.replace(" ", "").replace("（", "(").replace("）", ")").replace("，", ",")
    # 針對逗號分隔的列表進行正規化
    elif ',' in correct_answer:
        user_answer = user_answer.replace(" ", "").replace("，", ",")
    # 針對坐標軸答案進行正規化
    elif '軸' in correct_answer:
        user_answer = user_answer.replace(" ", "").upper()
        correct_answer = correct_answer.replace(" ", "").upper()
    
    is_correct = (user_answer == correct_answer)

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}
