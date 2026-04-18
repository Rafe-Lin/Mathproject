import random
import math
from fractions import Fraction

def generate(level=1):
    """
    生成「橢圓標準式」相關題目。
    包含：
    1. 給定焦點和長軸長，求橢圓參數
    2. 給定頂點和焦點，求橢圓參數
    3. 給定一般式，求橢圓參數
    """
    problem_type = random.choice([
        'foci_major_axis',
        'vertices_focus',
        'general_form_to_params'
    ])

    if problem_type == 'foci_major_axis':
        return generate_foci_major_axis_problem(level)
    elif problem_type == 'vertices_focus':
        return generate_vertices_focus_problem(level)
    else: # general_form_to_params
        return generate_general_form_problem(level)

def generate_foci_major_axis_problem(level):
    """
    生成「給定兩焦點及長軸長，求橢圓參數」的問題。
    """
    is_horizontal = random.choice([True, False]) # 長軸平行x軸或y軸

    h = random.randint(-5, 5) # 中心點x座標
    k = random.randint(-5, 5) # 中心點y座標

    if level == 1:
        c_val = random.randint(1, 3) # 焦點半距 c
        a_val = c_val + random.randint(1, 2) # 長軸半長 a, 確保 a > c
    else: # level 2 允許更大的值
        c_val = random.randint(1, 5)
        a_val = c_val + random.randint(1, 3)

    b_squared = a_val**2 - c_val**2 # 短軸半長b的平方

    # 計算焦點坐標
    if is_horizontal:
        f1_x, f1_y = h - c_val, k
        f2_x, f2_y = h + c_val, k
    else: # 垂直
        f1_x, f1_y = h, k - c_val
        f2_x, f2_y = h, k + c_val

    major_axis_len = 2 * a_val # 長軸長

    # 問題選項
    question_options = [
        ("中心點的 $x$ 座標為何？", h),
        ("中心點的 $y$ 座標為何？", k),
        (r"長軸半長 $a$ 的平方 ($a^2$) 為何？", a_val**2),
        (r"短軸半長 $b$ 的平方 ($b^2$) 為何？", b_squared),
        (r"焦點半距 $c$ 的平方 ($c^2$) 為何？", c_val**2)
    ]

    question_text_part, correct_answer = random.choice(question_options)

    question_text = (
        f"求兩焦點為 $F_1({f1_x},{f1_y})$ 與 $F_2({f2_x},{f2_y})$，長軸長為 ${major_axis_len}$ 的橢圓，"
        f"其{question_text_part}"
    )

    return {
        "question_text": question_text,
        "answer": str(correct_answer),
        "correct_answer": str(correct_answer)
    }

def generate_vertices_focus_problem(level):
    """
    生成「給定兩頂點及一焦點，求橢圓參數」的問題。
    """
    is_horizontal = random.choice([True, False]) # 長軸平行x軸或y軸

    h = random.randint(-5, 5) # 中心點x座標
    k = random.randint(-5, 5) # 中心點y座標

    if level == 1:
        c_val = random.randint(1, 3)
        a_val = c_val + random.randint(1, 2)
    else: # level 2 允許更大的值
        c_val = random.randint(1, 5)
        a_val = c_val + random.randint(1, 3)

    b_squared = a_val**2 - c_val**2

    # 計算頂點和其中一個焦點坐標
    if is_horizontal:
        v1_x, v1_y = h - a_val, k
        v2_x, v2_y = h + a_val, k
        f_x, f_y = h + c_val, k # 選擇其中一個焦點
    else: # 垂直
        v1_x, v1_y = h, k - a_val
        v2_x, v2_y = h, k + a_val
        f_x, f_y = h, k + c_val # 選擇其中一個焦點

    # 問題選項
    question_options = [
        ("中心點的 $x$ 座標為何？", h),
        ("中心點的 $y$ 座標為何？", k),
        (r"長軸半長 $a$ 的平方 ($a^2$) 為何？", a_val**2),
        (r"短軸半長 $b$ 的平方 ($b^2$) 為何？", b_squared),
        (r"焦點半距 $c$ 的平方 ($c^2$) 為何？", c_val**2)
    ]

    question_text_part, correct_answer = random.choice(question_options)

    question_text = (
        f"求其中兩個頂點為 $({v1_x},{v1_y})$ 與 $({v2_x},{v2_y})$，其中一個焦點為 $({f_x},{f_y})$ 的橢圓，"
        f"其{question_text_part}"
    )

    return {
        "question_text": question_text,
        "answer": str(correct_answer),
        "correct_answer": str(correct_answer)
    }

def generate_general_form_problem(level):
    """
    生成「給定橢圓一般式，求橢圓參數」的問題。
    """
    h = random.randint(-4, 4) # 中心點x座標
    k = random.randint(-4, 4) # 中心點y座標

    # 確保 a > b
    if level == 1:
        b_val = random.randint(1, 2) # 短軸半長 b
        a_val = b_val + random.randint(1, 2) # 長軸半長 a
    else: # level 2
        b_val = random.randint(1, 3)
        a_val = b_val + random.randint(1, 3)

    a_squared = a_val**2
    b_squared = b_val**2
    c_squared = a_squared - b_squared
    c_val = math.sqrt(c_squared) # 焦點半距 c (可能為無理數)

    is_horizontal = random.choice([True, False]) # 長軸平行x軸或y軸

    # 橢圓一般式: coeff_x2 * (x-h)^2 + coeff_y2 * (y-k)^2 = coeff_x2 * coeff_y2
    # 若長軸平行x軸: (x-h)^2/a^2 + (y-k)^2/b^2 = 1 => b^2(x-h)^2 + a^2(y-k)^2 = a^2b^2
    # => coeff_x2 = b^2, coeff_y2 = a^2
    # 若長軸平行y軸: (x-h)^2/b^2 + (y-k)^2/a^2 = 1 => a^2(x-h)^2 + b^2(y-k)^2 = a^2b^2
    # => coeff_x2 = a^2, coeff_y2 = b^2
    if is_horizontal:
        coeff_x2 = b_squared
        coeff_y2 = a_squared
    else: # 垂直
        coeff_x2 = a_squared
        coeff_y2 = b_squared

    # 展開為一般式: Ax^2 + Cy^2 + Dx + Ey + F = 0
    # coeff_x2*x^2 + coeff_y2*y^2 - (2*coeff_x2*h)*x - (2*coeff_y2*k)*y + (coeff_x2*h^2 + coeff_y2*k^2 - coeff_x2*coeff_y2) = 0
    D = -2 * coeff_x2 * h
    E = -2 * coeff_y2 * k
    F = coeff_x2 * h**2 + coeff_y2 * k**2 - coeff_x2 * coeff_y2

    # 建構一般式字串
    general_eq_str_parts = []
    if coeff_x2 == 1:
        general_eq_str_parts.append(r"x^2")
    else:
        general_eq_str_parts.append(f"{coeff_x2}x^2")

    if coeff_y2 == 1:
        general_eq_str_parts.append(r"+y^2")
    else:
        general_eq_str_parts.append(f"+{coeff_y2}y^2")

    if D != 0:
        if D > 0:
            general_eq_str_parts.append(f"+{D}x")
        else:
            general_eq_str_parts.append(f"{D}x")

    if E != 0:
        if E > 0:
            general_eq_str_parts.append(f"+{E}y")
        else:
            general_eq_str_parts.append(f"{E}y")

    if F != 0:
        if F > 0:
            general_eq_str_parts.append(f"+{F}")
        else:
            general_eq_str_parts.append(f"{F}")

    general_eq_str = "".join(general_eq_str_parts).replace("+-", "-")
    question_eq_display = f"${general_eq_str}=0$"

    # 問題選項
    question_options = [
        ("中心點的 $x$ 座標為何？", h),
        ("中心點的 $y$ 座標為何？", k),
        (r"長軸半長 $a$ 的平方 ($a^2$) 為何？", a_squared),
        (r"短軸半長 $b$ 的平方 ($b^2$) 為何？", b_squared),
    ]

    # 若 c_val 為整數，則可詢問焦點或頂點座標
    if math.isclose(c_val, round(c_val)): # 檢查 c_val 是否接近整數
        c_val_int = int(round(c_val))
        if is_horizontal:
            focus_x1, focus_y1 = h - c_val_int, k
            focus_x2, focus_y2 = h + c_val_int, k
            vertex_x1, vertex_y1 = h - a_val, k
            vertex_x2, vertex_y2 = h + a_val, k
            cvertex_x1, cvertex_y1 = h, k - b_val # 短軸頂點
            cvertex_x2, cvertex_y2 = h, k + b_val
        else: # 垂直
            focus_x1, focus_y1 = h, k - c_val_int
            focus_x2, focus_y2 = h, k + c_val_int
            vertex_x1, vertex_y1 = h, k - a_val
            vertex_x2, vertex_y2 = h, k + a_val
            cvertex_x1, cvertex_y1 = h - b_val, k
            cvertex_x2, cvertex_y2 = h + b_val, k

        question_options.extend([
            (r"其中一個頂點的 $x$ 座標為何？", random.choice([vertex_x1, vertex_x2, cvertex_x1, cvertex_x2])),
            (r"其中一個頂點的 $y$ 座標為何？", random.choice([vertex_y1, vertex_y2, cvertex_y1, cvertex_y2])),
            (r"其中一個焦點的 $x$ 座標為何？", random.choice([focus_x1, focus_x2])),
            (r"其中一個焦點的 $y$ 座標為何？", random.choice([focus_y1, focus_y2])),
        ])

    question_text_part, correct_answer = random.choice(question_options)

    question_text = (
        f"求橢圓 {question_eq_display} 的{question_text_part}"
    )

    return {
        "question_text": question_text,
        "answer": str(correct_answer),
        "correct_answer": str(correct_answer)
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    
    is_correct = False
    try:
        # 使用 math.isclose 比較浮點數，以處理潛在的浮點精度問題
        if math.isclose(float(user_answer), float(correct_answer), rel_tol=1e-9, abs_tol=1e-9):
            is_correct = True
    except ValueError:
        # 如果無法轉換為浮點數，則進行字串比較 (例如，答案可能是文字)
        is_correct = (user_answer.upper() == correct_answer.upper())

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}