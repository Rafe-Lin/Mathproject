import random
import math
import re
from fractions import Fraction

def generate(level=1):
    """
    生成「立體圖形」相關題目。
    涵蓋：角柱、圓柱、角錐、圓錐的體積與表面積，以及相關應用。
    """
    problem_types = [
        'prism_parallelogram_vol_sa',
        'cylinder_vol_sa',
        'pyramid_square_sa',
        'cone_sa',
        'cone_net_angle',
        'space_diagonal'
    ]
    problem_type = random.choice(problem_types)

    if problem_type == 'prism_parallelogram_vol_sa':
        return generate_prism_parallelogram_vol_sa()
    elif problem_type == 'cylinder_vol_sa':
        return generate_cylinder_vol_sa()
    elif problem_type == 'pyramid_square_sa':
        return generate_pyramid_square_sa()
    elif problem_type == 'cone_sa':
        return generate_cone_sa()
    elif problem_type == 'cone_net_angle':
        return generate_cone_net_angle()
    else: # space_diagonal
        return generate_space_diagonal_problem()

def generate_prism_parallelogram_vol_sa():
    """
    題型：平行四邊形底角柱的體積與表面積
    """
    b = random.randint(8, 15)
    s = random.randint(4, b - 2)
    h_base = random.randint(3, s - 1)
    h_prism = random.randint(4, 10)

    volume = b * h_base * h_prism
    surface_area = 2 * (b * h_base) + (2 * b + 2 * s) * h_prism

    question_text = f"一個底面為平行四邊形的角柱，底邊長 ${b}$ 公分，另一邊長 ${s}$ 公分，底面平行四邊形的高為 ${h_base}$ 公分，柱高為 ${h_prism}$ 公分。請問此角柱的體積與表面積分別為何？<br>(請依序回答體積、表面積，並以逗號分隔，單位為立方公分與平方公分)"
    correct_answer = f"{volume},{surface_area}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_cylinder_vol_sa():
    """
    題型：圓柱的體積與表面積
    """
    r = random.randint(2, 8)
    h = random.randint(5, 15)

    volume_coeff = r**2 * h
    surface_area_coeff = 2 * r**2 + 2 * r * h

    question_text = f"一個底面半徑為 ${r}$ 公分，高為 ${h}$ 公分的圓柱，其體積與表面積分別為何？<br>(答案請以 $\\pi$ 表示，並依序回答體積、表面積，以逗號分隔)"
    correct_answer = f"{volume_coeff}π,{surface_area_coeff}π"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_pyramid_square_sa():
    """
    題型：正四角錐的表面積
    """
    s = random.randint(4, 12)
    if s % 2 != 0:
        s += 1  # Make it even for simpler geometry
    
    l = random.randint(s // 2 + 2, 20)

    base_area = s**2
    lateral_area = 2 * s * l
    surface_area = base_area + lateral_area

    question_text = f"一個正四角錐的底面是邊長為 ${s}$ 公分的正方形，側面等腰三角形的高（即斜高）為 ${l}$ 公分，則此正四角錐的表面積為何？ (單位：平方公分)"
    correct_answer = str(surface_area)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_cone_sa():
    """
    題型：圓錐的表面積
    """
    r = random.randint(2, 8)
    l = random.randint(r + 2, 15)

    surface_area_coeff = r**2 + r * l

    question_text = f"一個圓錐的底面半徑為 ${r}$ 公分，側面斜高為 ${l}$ 公分，試求此圓錐的表面積為何？ (答案請以 $\\pi$ 表示，單位：平方公分)"
    correct_answer = f"{surface_area_coeff}π"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_cone_net_angle():
    """
    題型：圓錐展開圖的扇形圓心角
    """
    fractions_data = [Fraction(1, 2), Fraction(1, 3), Fraction(2, 3), Fraction(1, 4), Fraction(3, 4), Fraction(1, 5), Fraction(2, 5), Fraction(3, 5), Fraction(4, 5)]
    frac = random.choice(fractions_data)
    
    n, d = frac.numerator, frac.denominator
    k = random.randint(2, 5)
    r = k * n
    R = k * d
    
    angle = int(360 * frac)

    question_text = f"一個圓錐的展開圖中，側面扇形半徑（即圓錐的斜高）為 ${R}$ 公分，底圓半徑為 ${r}$ 公分，則側面扇形的圓心角度數為何？ (單位：度)"
    correct_answer = str(angle)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_space_diagonal_problem():
    """
    題型：長方體內的最短飛行距離（空間對角線）
    """
    while True:
        l = random.randint(3, 9)
        w = random.randint(3, 9)
        h = random.randint(3, 9)
        d_squared = l**2 + w**2 + h**2
        # Ensure the result is not a perfect square to match the example style
        if math.isqrt(d_squared)**2 != d_squared:
            break
            
    question_text = f"一個長方體盒子，其長、寬、高分別為 ${l}$ 公分、${w}$ 公分、${h}$ 公分。若有一隻蜜蜂想從一個頂點直線飛到對角線距離最遠的另一個頂點，則此蜜蜂飛行的最短距離為何？"
    correct_answer = f"\\sqrt{{{d_squared}}}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    norm_user_answer = user_answer.strip().replace(' ', '').replace('，', ',')
    norm_correct_answer = correct_answer

    # Case 1: Answer contains π
    if 'π' in norm_correct_answer:
        norm_user_answer = norm_user_answer.replace('pi', 'π').replace('PI', 'π')
    
    # Case 2: Answer contains \\sqrt
    elif '\\sqrt' in norm_correct_answer:
        try:
            # Extract number from correct answer, e.g., '133' from '\\sqrt{133}'
            correct_num_str = norm_correct_answer.split('{')[1].split('}')[0]
            # Try to extract number from user answer, e.g., '133' from 'sqrt(133)' or '根號133'
            user_nums = re.findall(r'\d+', norm_user_answer)
            if user_nums and user_nums[0] == correct_num_str:
                # If number matches, standardize the user's answer format for a direct comparison.
                norm_user_answer = f"\\sqrt{{{correct_num_str}}}"
        except IndexError:
            # Fallback if parsing fails, the original string comparison will be used.
            pass
    
    is_correct = (norm_user_answer == norm_correct_answer)

    # For purely numerical answers, try a float comparison to handle cases like "340" vs "340.0"
    if not is_correct and 'π' not in norm_correct_answer and '\\sqrt' not in norm_correct_answer:
        try:
            # Handle comma-separated values
            user_parts = norm_user_answer.split(',')
            correct_parts = norm_correct_answer.split(',')
            if len(user_parts) == len(correct_parts):
                if all(float(u) == float(c) for u, c in zip(user_parts, correct_parts)):
                    is_correct = True
        except (ValueError, TypeError):
            pass

    if is_correct:
        result_text = f"完全正確！答案是 ${correct_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer}$"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}