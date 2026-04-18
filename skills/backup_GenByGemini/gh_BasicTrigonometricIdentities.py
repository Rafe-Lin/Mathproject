import random
import math
from fractions import Fraction

def _get_fraction_string(num, den=1):
    """
    Helper to format fractions nicely for LaTeX output, or integers.
    Uses Fraction class to simplify if possible.
    """
    if den == 0:
        return r"\text{undefined}"
    if den == 1:
        return str(num)
    
    f = Fraction(num, den)
    if f.denominator == 1:
        return str(f.numerator)
    return r"\\frac{{{}}}{{{}}}".format(f.numerator, f.denominator)

def generate(level=1):
    """
    生成「基本三角比關係」相關題目。
    根據 level 參數生成不同難度的題目。
    Level 1: 直接應用單一基本關係式或簡單計算。
    Level 2: 結合多個關係式、基本代數運算或簡單幾何應用。
    Level 3: 多步驟代數運算、複雜幾何應用。
    """
    problem_funcs = []

    if level == 1:
        problem_funcs = [
            generate_identity_verification_level1,
            generate_calculate_value_level1,
            generate_solve_for_trig_ratio_level1,
        ]
    elif level == 2:
        problem_funcs = [
            generate_identity_verification_level2,
            generate_calculate_value_level2,
            generate_algebraic_identity_problem_level2,
            generate_geometric_application_level2,
        ]
    elif level == 3:
        problem_funcs = [
            generate_algebraic_identity_problem_level3,
            generate_geometric_application_level3,
        ]
    
    selected_func = random.choice(problem_funcs)
    return selected_func()

# --- Problem Type Implementations ---

def generate_identity_verification_level1():
    """
    Level 1: 直接真假判斷基本三角關係式。
    例如: tan 10° ⋅ cos 10° = sin 10° (商數關係)
          sin 47° = cos 43° (餘角關係)
          sin² 20° = 1 − cos² 20° (平方關係)
    """
    problem_type = random.choice([
        "quotient_identity_mult",        # tanθ * cosθ = sinθ
        "pythagorean_identity_rearrange", # sin²θ = 1 - cos²θ
        "complementary_identity_sincos",  # sin(90°-θ) = cosθ
        "complementary_identity_tan"      # tan(90°-θ) = 1/tanθ
    ])

    angle_deg = random.randint(5, 85) # 銳角

    if problem_type == "quotient_identity_mult":
        is_correct = random.choice([True, False])
        if is_correct:
            question_text = f"選出以下正確的選項：<br>(1) $ \\tan {angle_deg}{{\\circ}} \\cdot \\cos {angle_deg}{{\\circ}} = \\sin {angle_deg}{{\\circ}}$"
            correct_answer = "(1)"
        else:
            # 錯誤選項: tanθ * sinθ = cosθ
            question_text = f"選出以下正確的選項：<br>(1) $ \\tan {angle_deg}{{\\circ}} \\cdot \\sin {angle_deg}{{\\circ}} = \\cos {angle_deg}{{\\circ}}$"
            correct_answer = "None"
        
    elif problem_type == "pythagorean_identity_rearrange":
        trig_func = random.choice(['sin', 'cos'])
        is_correct = random.choice([True, False])
        
        if trig_func == 'sin':
            if is_correct:
                question_text = f"選出以下正確的選項：<br>(1) $ \\sin^{{2}} {angle_deg}{{\\circ}} = 1 - \\cos^{{2}} {angle_deg}{{\\circ}}$"
                correct_answer = "(1)"
            else:
                question_text = f"選出以下正確的選項：<br>(1) $ \\sin^{{2}} {angle_deg}{{\\circ}} = 1 + \\cos^{{2}} {angle_deg}{{\\circ}}$"
                correct_answer = "None"
        else: # trig_func == 'cos'
            if is_correct:
                question_text = f"選出以下正確的選項：<br>(1) $ \\cos^{{2}} {angle_deg}{{\\circ}} = 1 - \\sin^{{2}} {angle_deg}{{\\circ}}$"
                correct_answer = "(1)"
            else:
                question_text = f"選出以下正確的選項：<br>(1) $ \\cos^{{2}} {angle_deg}{{\\circ}} = 1 + \\sin^{{2}} {angle_deg}{{\\circ}}$"
                correct_answer = "None"
        
    elif problem_type == "complementary_identity_sincos":
        is_correct = random.choice([True, False])
        complement_angle = 90 - angle_deg
        
        if is_correct:
            question_text = f"選出以下正確的選項：<br>(1) $ \\sin {angle_deg}{{\\circ}} = \\cos {complement_angle}{{\\circ}}$"
            correct_answer = "(1)"
        else:
            wrong_func = random.choice(['sin', 'tan'])
            question_text = f"選出以下正確的選項：<br>(1) $ \\sin {angle_deg}{{\\circ}} = \\{wrong_func} {complement_angle}{{\\circ}}$"
            correct_answer = "None"
            
    elif problem_type == "complementary_identity_tan":
        is_correct = random.choice([True, False])
        complement_angle = 90 - angle_deg
        
        if is_correct:
            question_text = f"選出以下正確的選項：<br>(1) $ \\tan {angle_deg}{{\\circ}} \\cdot \\tan {complement_angle}{{\\circ}} = 1 $"
            correct_answer = "(1)"
        else:
            question_text = f"選出以下正確的選項：<br>(1) $ \\tan {angle_deg}{{\\circ}} \\cdot \\sin {complement_angle}{{\\circ}} = 1 $"
            correct_answer = "None"
            
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_identity_verification_level2():
    """
    Level 2: 判斷包含多個關係式或角度變化的敘述。
    例如: sin 70° / cos 70° = tan 20° (錯誤，角度不符)
          sin² 50° = 1 − sin² 40° (正確，餘角關係 + 平方關係)
    """
    problem_type = random.choice([
        "quotient_identity_false_angle",    # sinθ/cosθ = tan(other_angle)
        "pythagorean_complementary_combo",  # sin²θ = 1 − sin²(90°-θ)
    ])

    angle_deg = random.randint(5, 85) 

    if problem_type == "quotient_identity_false_angle":
        angle_on_right = random.randint(5, 85)
        while angle_on_right == angle_deg: # 確保角度不同
            angle_on_right = random.randint(5, 85)
        
        question_text = f"選出以下正確的選項：<br>(1) $ \\frac{{\\sin {angle_deg}{{\\circ}}}}{{\\cos {angle_deg}{{\\circ}}}} = \\tan {angle_on_right}{{\\circ}}$"
        correct_answer = "None" 

    elif problem_type == "pythagorean_complementary_combo":
        is_correct = random.choice([True, False])
        complement_angle = 90 - angle_deg

        if is_correct:
            question_text = f"選出以下正確的選項：<br>(1) $ \\sin^{{2}} {angle_deg}{{\\circ}} = 1 - \\sin^{{2}} {complement_angle}{{\\circ}}$"
            correct_answer = "(1)"
        else:
            question_text = f"選出以下正確的選項：<br>(1) $ \\sin^{{2}} {angle_deg}{{\\circ}} = 1 + \\sin^{{2}} {complement_angle}{{\\circ}}$"
            correct_answer = "None"
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_calculate_value_level1():
    """
    Level 1: 計算使用基本關係式的表達式的值。
    例如: cos² 34° + cos² 56° = 1
          tan 63° − sin 63° / cos 63° = 0
    """
    problem_type = random.choice([
        "pythagorean_complementary_sum", # cos²θ + cos²(90-θ) = 1
        "quotient_identity_subtraction", # tanθ − sinθ / cosθ = 0
    ])

    angle_deg = random.randint(10, 80)

    if problem_type == "pythagorean_complementary_sum":
        complement_angle = 90 - angle_deg
        func_choice = random.choice(['cos', 'sin'])
        
        if func_choice == 'cos':
            question_text = f"求下列各式的值：<br>(1) $ \\cos^{{2}} {angle_deg}{{\\circ}} + \\cos^{{2}} {complement_angle}{{\\circ}}$"
        else:
            question_text = f"求下列各式的值：<br>(1) $ \\sin^{{2}} {angle_deg}{{\\circ}} + \\sin^{{2}} {complement_angle}{{\\circ}}$"
        
        correct_answer = "1"
        
    elif problem_type == "quotient_identity_subtraction":
        question_text = f"求下列各式的值：<br>(1) $ \\tan {angle_deg}{{\\circ}} - \\frac{{\\sin {angle_deg}{{\\circ}}}}{{\\cos {angle_deg}{{\\circ}}}}$"
        correct_answer = "0"
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_calculate_value_level2():
    """
    Level 2: 更複雜的代數運算與關係式結合。
    例如: (sin 20° + cos 20°)² + (sin 20° − cos 20°)² = 2
          (1 + tan²θ) * cos²θ = 1
    """
    problem_type = random.choice([
        "squared_sum_diff",          # (sinθ + cosθ)² + (sinθ - cosθ)²
        "sec_pythagorean_identity",  # (1 + tan²θ) * cos²θ
    ])

    angle_deg = random.randint(10, 80) 

    if problem_type == "squared_sum_diff":
        # (sinθ + cosθ)² + (sinθ - cosθ)² = (1 + 2sinθcosθ) + (1 - 2sinθcosθ) = 2
        question_text = f"求下列各式的值：<br>(1) $ (\\sin {angle_deg}{{\\circ}} + \\cos {angle_deg}{{\\circ}})^{{2}} + (\\sin {angle_deg}{{\\circ}} - \\cos {angle_deg}{{\\circ}})^{{2}}$"
        correct_answer = "2"
        
    elif problem_type == "sec_pythagorean_identity":
        # (1 + tan²θ) * cos²θ = sec²θ * cos²θ = (1/cos²θ) * cos²θ = 1
        question_text = f"求下列各式的值：<br>(1) $ (1 + \\tan^{{2}} {angle_deg}{{\\circ}}) \\cdot \\cos^{{2}} {angle_deg}{{\\circ}}$"
        correct_answer = "1"
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def generate_solve_for_trig_ratio_level1():
    """
    Level 1: 已知一個三角比的值，求其他三角比的值。
    例如: cos θ = 1/3，求 sin θ 和 tan θ。
    """
    # 使用勾股數產生分數值，確保答案為有理數
    triples = [
        (3, 4, 5),
        (5, 12, 13),
        (8, 15, 17),
        (7, 24, 25),
    ]
    
    a, b, c = random.choice(triples)
    
    # 隨機指定 sinθ 或 cosθ 為 a/c 或 b/c
    if random.random() < 0.5: # sinθ = a/c
        given_trig = "sin"
        given_val_num = a
        given_val_den = c
        sin_val = Fraction(a, c)
        cos_val = Fraction(b, c)
    else: # cosθ = a/c
        given_trig = "cos"
        given_val_num = a
        given_val_den = c
        sin_val = Fraction(b, c)
        cos_val = Fraction(a, c)
        
    tan_val = sin_val / cos_val

    find_trig_funcs = []
    if given_trig == "sin":
        find_trig_funcs = ["cos", "tan"]
    else: # given_trig == "cos"
        find_trig_funcs = ["sin", "tan"]

    random.shuffle(find_trig_funcs)
    
    # 題目可能只要求一個值，或兩個值
    num_to_find = random.choice([1, 2])
    find_trig_funcs = find_trig_funcs[:num_to_find]
    
    if num_to_find == 1:
        target_func = find_trig_funcs[0]
        question_text = f"已知 $ \\theta $ 為銳角且 $ \\{given_trig} \\theta = {_get_fraction_string(given_val_num, given_val_den)} $，求 $ \\{target_func} \\theta $ 的值。"
        
        if target_func == "sin":
            correct_answer = _get_fraction_string(sin_val.numerator, sin_val.denominator)
        elif target_func == "cos":
            correct_answer = _get_fraction_string(cos_val.numerator, cos_val.denominator)
        else: # target_func == "tan"
            correct_answer = _get_fraction_string(tan_val.numerator, tan_val.denominator)
        
    else: # num_to_find == 2
        func1 = find_trig_funcs[0]
        func2 = find_trig_funcs[1]
        
        question_text = f"已知 $ \\theta $ 為銳角且 $ \\{given_trig} \\theta = {_get_fraction_string(given_val_num, given_val_den)} $，求 $ \\{func1} \\theta $ 和 $ \\{func2} \\theta $ 的值。"
        
        ans1_val = ""
        if func1 == "sin": ans1_val = _get_fraction_string(sin_val.numerator, sin_val.denominator)
        elif func1 == "cos": ans1_val = _get_fraction_string(cos_val.numerator, cos_val.denominator)
        else: ans1_val = _get_fraction_string(tan_val.numerator, tan_val.denominator)

        ans2_val = ""
        if func2 == "sin": ans2_val = _get_fraction_string(sin_val.numerator, sin_val.denominator)
        elif func2 == "cos": ans2_val = _get_fraction_string(cos_val.numerator, cos_val.denominator)
        else: ans2_val = _get_fraction_string(tan_val.numerator, tan_val.denominator)
        
        # 允許多個答案順序
        correct_answer = (f"{ans1_val}, {ans2_val}", f"{ans2_val}, {ans1_val}")

    return {
        "question_text": question_text,
        "answer": correct_answer[0] if isinstance(correct_answer, tuple) else correct_answer, # Store primary for display
        "correct_answer": correct_answer
    }

def generate_algebraic_identity_problem_level2():
    """
    Level 2: 代數化簡結合三角關係式，通常可化簡為一個數字。
    例如: (sinθ/cosθ) + (cosθ/sinθ) = 1/(sinθcosθ) 
          此題型將提供可簡化為數字的表達式
    """
    problem_type = random.choice([
        "sum_of_reciprocal_tangents", # (sinθ/cosθ) + (cosθ/sinθ) = 1/(sinθcosθ) (requires sinθcosθ)
        "pythagorean_denominator",    # (1 - sin²θ) / cos²θ = 1
    ])

    angle_deg = random.randint(10, 80)

    if problem_type == "sum_of_reciprocal_tangents":
        # 需額外條件才能求出數字。此處將其改為：若已知 sinθcosθ。
        # 不如選一個可以直接化簡的。
        # 題目應為 `(sinθ/cosθ) + (cosθ/sinθ)` 的值。
        # 答案是 `1/(sinθcosθ)`。如果沒有提供 `sinθcosθ`，無法得到數字。
        # 為了保持L2的數字答案，此題型暫不使用此變體。
        # 改為 `(sinθ/cosθ) + (cosθ/sinθ)` in terms of (sinθ+cosθ).
        # (sinθ/cosθ) + (cosθ/sinθ) = (sin^2θ + cos^2θ)/(sinθcosθ) = 1/(sinθcosθ)
        # This requires `sinθcosθ` from `(sinθ+cosθ)^2`. More like L3.

        # Let's use simpler form: (1-sin^2θ) / (1-cos^2θ) * tan^2θ.
        # This equals (cos^2θ / sin^2θ) * tan^2θ = cot^2θ * tan^2θ = 1.
        question_text = f"求下列各式的值：<br>(1) $ \\frac{{1 - \\sin^{{2}} {angle_deg}{{\\circ}}}}{{1 - \\cos^{{2}} {angle_deg}{{\\circ}}}} \\cdot \\tan^{{2}} {angle_deg}{{\\circ}}$"
        correct_answer = "1"
        
    elif problem_type == "pythagorean_denominator":
        # (1 - sin²θ) / cos²θ = cos²θ / cos²θ = 1
        question_text = f"求下列各式的值：<br>(1) $ \\frac{{1 - \\sin^{{2}} {angle_deg}{{\\circ}}}}{{\\cos^{{2}} {angle_deg}{{\\circ}}}}$"
        correct_answer = "1"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_algebraic_identity_problem_level3():
    """
    Level 3: 給定 sinθ + cosθ 的值，求 sinθcosθ 或 sin³θ + cos³θ。
    需代數運算 (平方、立方和公式) 和三角關係式。
    """
    # 使用勾股數產生有理數 sinθ, cosθ
    a, b, c = random.choice([(3, 4, 5), (5, 12, 13)])
    
    # 確保 sinθcosθ 不為 0
    sin_val = Fraction(a, c)
    cos_val = Fraction(b, c)
    
    sum_sincos = sin_val + cos_val # (a+b)/c
    prod_sincos = sin_val * cos_val # ab/c^2
    
    problem_choice = random.choice([
        "find_prod_sincos",
        "find_cubed_sum"
    ])

    if problem_choice == "find_prod_sincos":
        question_text = f"已知 $ \\theta $ 為銳角，且 $ \\sin \\theta + \\cos \\theta = {_get_fraction_string(sum_sincos.numerator, sum_sincos.denominator)} $ ，求 $ \\sin \\theta \\cos \\theta $ 的值。"
        correct_answer = _get_fraction_string(prod_sincos.numerator, prod_sincos.denominator)
        
    elif problem_choice == "find_cubed_sum":
        # sin³θ + cos³θ = (sinθ + cosθ)(sin²θ - sinθcosθ + cos²θ)
        # = (sinθ + cosθ)(1 - sinθcosθ)
        cubed_sum = sum_sincos * (1 - prod_sincos)
        
        question_text = f"已知 $ \\theta $ 為銳角，且 $ \\sin \\theta + \\cos \\theta = {_get_fraction_string(sum_sincos.numerator, sum_sincos.denominator)} $ ，求 $ \\sin^{{3}} \\theta + \\cos^{{3}} \\theta $ 的值。"
        correct_answer = _get_fraction_string(cubed_sum.numerator, cubed_sum.denominator)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_geometric_application_level2():
    """
    Level 2: 基本幾何應用題，通常涉及單個直角三角形和 tanθ。
    例如: 影子長度求 tanθ 和高度。
    """
    problem_type = random.choice([
        "shadow_height_tan", # 求 tanθ，再求另一個高度
        "slope_definition",  # 給定坡度 (tanθ) 和水平長度，求垂直高度
    ])

    if problem_type == "shadow_height_tan":
        height = random.randint(100, 200) # 公分
        # 選擇一個讓影子長度為整數的 tanθ 比例
        ratio_choices = [Fraction(3,4), Fraction(4,5), Fraction(1,2), Fraction(2,3)]
        tan_theta_frac = random.choice(ratio_choices)
        
        # 讓 shadow_length 也是整數
        shadow_length = round(height / tan_theta_frac)
        
        question_text = f"早上升旗時，陽光與地面形成固定的角度 $ \\theta $，某生身高為 ${height}$ 公分，測得影子長度為 ${shadow_length}$ 公分。<br>(1) 求 $ \\tan \\theta $ 的值。<br>(2) 已知升旗桿影子長度為 ${shadow_length * 2}$ 公分，求升旗桿的高度。"
        
        # Calculate answers
        tan_theta_val = Fraction(height, shadow_length)
        pole_height_val = tan_theta_val * (shadow_length * 2)
        
        correct_answer = f"{_get_fraction_string(tan_theta_val.numerator, tan_theta_val.denominator)}, {_get_fraction_string(pole_height_val.numerator, pole_height_val.denominator)}"

    elif problem_type == "slope_definition":
        tan_theta_raw = random.choice([Fraction(1,5), Fraction(1,4), Fraction(3,10)]) # 例如 0.2, 0.25, 0.3
        slope_percent = int(tan_theta_raw * 100)
        
        horizontal_len = random.randint(5, 20) * 10 # 50, 100, 200 公尺
        
        height_val = tan_theta_raw * horizontal_len
        
        question_text = f"坡度定義為 $ \\tan \\theta \\times 100\\% $。某道路坡度為 ${slope_percent}\\%$，其水平長度為 ${horizontal_len}$ 公尺，求該道路的高度變化量（垂直高度）。"
        correct_answer = _get_fraction_string(height_val.numerator, height_val.denominator)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_geometric_application_level3():
    """
    Level 3: 複雜幾何應用題，通常涉及多個直角三角形、仰角/俯角。
    例如: 大樓頂端測量地面物體仰角/俯角。
    此類題目答案可能包含根號，為了簡化檢查，答案以四捨五入到小數點後兩位的浮點數表示。
    """
    problem_type = random.choice([
        "two_angles_elevation_height", # 從一點測量大樓上兩個點的仰角，求大樓高度
        "building_tree_depression",    # 從大樓頂測量樹的頂部和底部俯角，求樹的高度
    ])

    if problem_type == "two_angles_elevation_height":
        # O 點測量大樓外牆金剛招牌 B 腳 A 手。
        # 仰角 BOC, AOB。求大樓高 AC。
        
        angles_choices = [
            (30, 45), # BOC=30, AOC=45, AOB=15
            (45, 60), # BOC=45, AOC=60, AOB=15
            (30, 60), # BOC=30, AOC=60, AOB=30
        ]
        
        angle_boc_deg, angle_aoc_deg = random.choice(angles_choices)
        sign_length = random.randint(3, 10) * 2 # 招牌長度

        question_text = f"某健身中心將身長 ${sign_length}$ 公尺的金剛招牌掛在大樓外牆，金剛的手攀於大樓頂端的 $A$ 點，而腳踏在正下方的 $B$ 點。今從平地上的 $O$ 點測得金剛腳底 $B$ 點的仰角為 ${angle_boc_deg}{{\\circ}}$ 及 $ \\angle AOB = {angle_aoc_deg - angle_boc_deg}{{\\circ}} $ ，求大樓的高度。"
        
        tan_aoc = math.tan(math.radians(angle_aoc_deg))
        tan_boc = math.tan(math.radians(angle_boc_deg))
        
        # h = sign_length * tan(AOC) / (tan(AOC) - tan(BOC))
        h_val_float = sign_length * tan_aoc / (tan_aoc - tan_boc)
        
        correct_answer = str(round(h_val_float, 2)) 

    elif problem_type == "building_tree_depression":
        # 從大樓頂端 A 測量樹頂 E 和樹底 D 的俯角。
        # 大樓高 AC。求樹高 DE。
        
        building_height = random.randint(15, 30) * 3 # 建築高度
        
        # 俯角 (從高處向下看): 樹頂俯角 < 樹底俯角
        # 為簡化計算，通常使用特殊角
        angle_top_deg, angle_base_deg = (30, 60) # 樹頂俯角30, 樹底俯角60

        question_text = f"如右圖所示，從大樓的頂端測量地面的一棵大樹，得樹底的俯角為 ${angle_base_deg}{{\\circ}}$，樹頂的俯角為 ${angle_top_deg}{{\\circ}}$。已知大樓高 ${building_height}$ 公尺，求樹的高度。"

        tan_base = math.tan(math.radians(angle_base_deg)) 
        tan_top = math.tan(math.radians(angle_top_deg))   
        
        # 樹高 = 大樓高 * (1 - tan(樹頂俯角) / tan(樹底俯角))
        tree_height_val_float = building_height * (1 - tan_top / tan_base)
        correct_answer = str(round(tree_height_val_float, 2))

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer_info):
    """
    檢查使用者答案是否正確。
    correct_answer_info 可以是單一字串 (str) 或包含多個可接受答案的元組 (tuple)。
    支援數字、分數（如 "1/2" 或 LaTeX 格式）、浮點數的比較。
    """
    is_correct = False
    feedback = ""

    # Helper to normalize answer strings for comparison
    def normalize_answer(ans_str):
        if not isinstance(ans_str, str):
            return str(ans_str) # Ensure it's a string
        
        # Remove LaTeX math delimiters and spaces
        normalized = ans_str.strip().replace('$', '').replace(' ', '')
        
        # Try to parse LaTeX fractions to Fraction objects
        if r'\\frac' in normalized:
            try:
                # This is a bit complex for direct eval, simplify by just removing the \\frac structure.
                # A more robust solution might involve a dedicated LaTeX parser or regex.
                # For basic cases like \\frac{A}{B}, we convert to A/B string for Fraction() constructor.
                parts = normalized.split(r'\\frac{')
                result_parts = []
                for p in parts:
                    if '}{' in p and p.endswith('}'):
                        num_den = p[:-1].split('}{')
                        if len(num_den) == 2:
                            result_parts.append(f"Fraction({num_den[0]}, {num_den[1]})")
                        else:
                            result_parts.append(p) # Fallback if not standard \\frac{A}{B}
                    else:
                        result_parts.append(p)
                normalized = "".join(result_parts)
            except Exception:
                pass # Failed to parse as LaTeX fraction, keep original
        
        return normalized

    user_ans_norm = normalize_answer(user_answer)
    
    candidate_correct_answers = []
    if isinstance(correct_answer_info, tuple):
        candidate_correct_answers = [normalize_answer(ans) for ans in correct_answer_info]
    else:
        candidate_correct_answers = [normalize_answer(correct_answer_info)]

    for correct_ans_norm in candidate_correct_answers:
        if user_ans_norm == correct_ans_norm:
            is_correct = True
            break
        
        try:
            # Try to compare as fractions
            if 'Fraction(' in user_ans_norm and 'Fraction(' in correct_ans_norm:
                # Needs `Fraction` to be imported for `eval`
                if eval(user_ans_norm, {'Fraction': Fraction}) == eval(correct_ans_norm, {'Fraction': Fraction}):
                    is_correct = True
                    break
            
            # Try to compare as floats (for rounded answers or general numbers)
            user_float = float(user_ans_norm)
            correct_float = float(correct_ans_norm)
            if abs(user_float - correct_float) < 1e-6: # Use tolerance for float comparison
                is_correct = True
                break
        except (ValueError, SyntaxError, NameError):
            continue # Not a numeric/fractional answer, continue to next comparison or conclude false

    if is_correct:
        feedback = "完全正確！"
    else:
        # Determine the string to show for correct answer in feedback
        display_correct = correct_answer_info[0] if isinstance(correct_answer_info, tuple) else correct_answer_info
        feedback = f"答案不正確。正確答案應為：${display_correct}$"

    return {"correct": is_correct, "result": feedback, "next_question": True}