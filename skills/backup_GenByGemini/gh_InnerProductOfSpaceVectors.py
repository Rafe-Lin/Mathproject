import random
import math
from fractions import Fraction

def generate(level=1):
    """
    生成「空間向量的內積」相關題目。
    包含：
    1. 計算兩向量的內積。
    2. 計算兩向量的夾角。
    3. 判斷兩向量垂直並求解未知數 s (在向量分量中)。
    4. 判斷向量組合與某向量垂直並求解未知數 t (在向量組合中)。
    """
    problem_type = random.choice([
        'inner_product',
        'angle_between_vectors',
        'perpendicular_find_s',
        'perpendicular_find_t'
    ])

    if problem_type == 'inner_product':
        return generate_inner_product_problem(level)
    elif problem_type == 'angle_between_vectors':
        return generate_angle_between_vectors_problem(level)
    elif problem_type == 'perpendicular_find_s':
        return generate_perpendicular_find_s_problem(level)
    elif problem_type == 'perpendicular_find_t':
        return generate_perpendicular_find_t_problem(level)

def create_random_vector(max_coord=5, include_zero=True):
    """
    生成一個隨機的三維向量。
    """
    coords = []
    for _ in range(3):
        val = random.randint(-max_coord, max_coord)
        if not include_zero and val == 0:
            while val == 0:
                val = random.randint(-max_coord, max_coord)
        coords.append(val)
    return tuple(coords)

def dot_product(v1, v2):
    """
    計算兩個向量的內積。
    """
    return sum(c1 * c2 for c1, c2 in zip(v1, v2))

def magnitude_squared(v):
    """
    計算向量長度的平方。
    """
    return sum(c**2 for c in v)

def format_vector(v):
    """
    將向量格式化為 LaTeX 字符串，例如 (1, 2, 3)。
    """
    return f"({v[0]}, {v[1]}, {v[2]})"

def generate_inner_product_problem(level):
    """
    生成計算兩向量內積的問題。
    """
    max_coord = 5 + level * 2
    vec_a = create_random_vector(max_coord=max_coord, include_zero=True)
    vec_b = create_random_vector(max_coord=max_coord, include_zero=True)

    result = dot_product(vec_a, vec_b)

    question_text = (
        fr"已知空間向量 $\vec{{a}} = {format_vector(vec_a)}$ 和 $\vec{{b}} = {format_vector(vec_b)}$。<br>"
        fr"求 $\vec{{a}} \\cdot \vec{{b}}$ 的值。"
    )
    correct_answer = str(result)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_angle_between_vectors_problem(level):
    """
    生成計算兩向量夾角的問題，答案四捨五入到整數位。
    """
    max_coord = 3 + level
    while True:
        vec_a = create_random_vector(max_coord=max_coord, include_zero=True)
        vec_b = create_random_vector(max_coord=max_coord, include_zero=True)
        
        # 確保向量為非零向量
        if magnitude_squared(vec_a) == 0 or magnitude_squared(vec_b) == 0:
            continue
        
        dp = dot_product(vec_a, vec_b)
        mag_a = math.sqrt(magnitude_squared(vec_a))
        mag_b = math.sqrt(magnitude_squared(vec_b))

        # 避免除以零 (已通過檢查非零向量避免)
        # 確保 cos_theta_val 在 [-1, 1] 之間，以處理浮點數精度問題
        cos_theta_val = dp / (mag_a * mag_b)
        cos_theta_val = max(-1.0, min(1.0, cos_theta_val))
        
        theta_radians = math.acos(cos_theta_val)
        theta_degrees = math.degrees(theta_radians)
        
        # 四捨五入到最接近的整數度數
        rounded_angle = round(theta_degrees)
        
        # 確保題目有意義，例如避免過多完全相同的向量導致 0 度或 180 度
        # 對於初級題目，這並非嚴格要求，但可增加變化性。
        # 如果是 0 或 180 度，可以稍微增加坐標範圍
        if (rounded_angle == 0 or rounded_angle == 180) and level < 3:
            if random.random() < 0.5: # 50% chance to retry for 0/180 at lower levels
                continue
        break 

    question_text = (
        fr"已知空間向量 $\vec{{a}} = {format_vector(vec_a)}$ 和 $\vec{{b}} = {format_vector(vec_b)}$。<br>"
        fr"求 $\vec{{a}}$ 與 $\vec{{b}}$ 的夾角 (度數四捨五入到整數位)。"
    )
    correct_answer = str(rounded_angle)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_perpendicular_find_s_problem(level):
    """
    生成已知兩向量垂直，求解向量中未知數 s 的問題。
    """
    max_coord = 4 + level
    while True:
        vec_a = create_random_vector(max_coord=max_coord, include_zero=True)
        # 確保 vec_a 不是零向量
        if magnitude_squared(vec_a) == 0:
            continue

        # 選擇 's' 出現在向量 b 的哪些位置 (1 或 2 個位置)
        s_indices = random.sample([0, 1, 2], random.randint(1, 2))
        
        b_coeffs = [0, 0, 0]        # 向量 b 分量中 's' 的係數
        b_constants = [0, 0, 0]     # 向量 b 分量中的常數部分

        for i in range(3):
            if i in s_indices:
                b_coeffs[i] = 1 # 該分量為 's'
            else:
                b_constants[i] = random.randint(-max_coord + 1, max_coord - 1) # 該分量為常數
        
        # 根據內積為零的條件建立方程：a . b = 0
        # a . (s * B_coeffs_vector + B_constants_vector) = 0
        # s * Sum(a_i * b_coeff_i) + Sum(a_i * b_const_i) = 0
        
        sum_a_b_coeff = 0 # 該項為 s 的係數
        sum_a_b_const = 0 # 該項為常數
        for i in range(3):
            sum_a_b_coeff += vec_a[i] * b_coeffs[i]
            sum_a_b_const += vec_a[i] * b_constants[i]
        
        # 避免 s 的係數為零，這會導致無解或無限多解
        if sum_a_b_coeff == 0:
            continue 

        # 解 s: s = -sum_a_b_const / sum_a_b_coeff
        s_val_fraction = Fraction(-sum_a_b_const, sum_a_b_coeff).limit_denominator(10)
        
        # 確保生成的 s 值不會導致所有 b 分量為零，讓問題更具挑戰性
        if s_val_fraction == 0 and sum(b_constants) == 0:
             continue

        # 構建向量 b 的字符串表示
        vec_b_parts = []
        for i in range(3):
            if i in s_indices:
                vec_b_parts.append('s')
            else:
                vec_b_parts.append(str(b_constants[i]))
        vec_b_str = f"({', '.join(vec_b_parts)})"

        question_text = (
            fr"設向量 $\vec{{a}} = {format_vector(vec_a)}$, $\vec{{b}} = {vec_b_str}$。<br>"
            fr"已知 $\vec{{a}} \\perp \vec{{b}}$，求實數 $s$ 的值。"
        )
        correct_answer = str(s_val_fraction)
        break 

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_perpendicular_find_t_problem(level):
    """
    生成已知向量組合與某向量垂直，求解未知數 t 的問題。
    形式為 $(\vec{a} + t\vec{c}) \\perp \vec{c}$。
    """
    max_coord = 4 + level
    while True:
        vec_a = create_random_vector(max_coord=max_coord, include_zero=True)
        vec_c = create_random_vector(max_coord=max_coord - 1, include_zero=True)
        
        mag_c_sq = magnitude_squared(vec_c)
        if mag_c_sq == 0: # 確保 vec_c 不是零向量
            continue

        dot_ac = dot_product(vec_a, vec_c)
        
        # 根據內積為零的條件： (a + t*c) . c = 0  =>  a.c + t * (c.c) = 0
        # => t = -(a.c) / (c.c)
        t_val_fraction = Fraction(-dot_ac, mag_c_sq).limit_denominator(10)
        
        question_text = (
            fr"設向量 $\vec{{a}} = {format_vector(vec_a)}$, $\vec{{c}} = {format_vector(vec_c)}$。<br>"
            fr"已知 $(\vec{{a}} + t\vec{{c}}) \\perp \vec{{c}}$，求實數 $t$ 的值。"
        )
        correct_answer = str(t_val_fraction)
        break

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查用戶答案是否正確。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()

    is_correct = False
    result_text = ""

    try:
        # 嘗試將答案解析為分數進行精確比較
        user_fraction = Fraction(user_answer)
        correct_fraction = Fraction(correct_answer)
        if user_fraction == correct_fraction:
            is_correct = True
        else:
            # 如果分數不完全匹配，對於可能存在浮點數誤差的答案（如角度），
            # 嘗試進行浮點數比較。
            try:
                user_float = float(user_answer)
                correct_float = float(correct_answer)
                # 對於角度等通常四捨五入的答案，使用較小的容忍度
                if abs(user_float - correct_float) < 0.01:
                    is_correct = True
            except ValueError:
                pass # 無法解析為浮點數
    except ValueError:
        # 如果用戶答案無法解析為分數，則執行原始字符串比較 (例如，如果答案不是數字)
        if user_answer.lower() == correct_answer.lower():
            is_correct = True

    if is_correct:
        result_text = fr"完全正確！答案是 ${correct_answer}$。"
    else:
        result_text = fr"答案不正確。正確答案應為：${correct_answer}$"

    return {"correct": is_correct, "result": result_text, "next_question": True}