import random
import math
import re
from fractions import Fraction

def generate(level=1):
    """
    生成「橢圓的幾何應用」相關題目。
    包含：
    1. 橢圓參數式 (中心在原點或平移)
    2. 伸縮變換後的橢圓方程式
    3. 橢圓的基本幾何性質 (中心、軸長)
    """
    problem_type = random.choice([
        'parametric_std_origin',
        'parametric_std_shifted',
        'parametric_general_origin',
        'parametric_general_shifted',
        'scaling_transformation',
        'geometric_properties_center_axes'
    ])

    if problem_type == 'parametric_std_origin':
        return generate_parametric_std_origin()
    elif problem_type == 'parametric_std_shifted':
        return generate_parametric_std_shifted()
    elif problem_type == 'parametric_general_origin':
        return generate_parametric_general_origin()
    elif problem_type == 'parametric_general_shifted':
        return generate_parametric_general_shifted()
    elif problem_type == 'scaling_transformation':
        return generate_scaling_transformation()
    else: # 'geometric_properties_center_axes'
        return generate_geometric_properties_center_axes()

def _format_param_expr(offset_val, coeff_val, func_name):
    """
    Helper to format a single parametric expression part (e.g., '1+3cos{theta}').
    coeff_val (a_val or b_val) is guaranteed to be >= 1 for this skill.
    """
    offset_str = ""
    if offset_val != 0:
        offset_str = str(offset_val)
    
    trig_str = ""
    if coeff_val == 1:
        trig_str = f"\\{func_name}{{\\theta}}"
    else: # coeff_val is > 1
        trig_str = f"{coeff_val}\\{func_name}{{\\theta}}"
    
    if offset_str and trig_str:
        if offset_val > 0:
            return f"{offset_str}+{trig_str}"
        else: # offset_val < 0
            return f"{offset_str}{trig_str}" # e.g. -3+2sin(theta)
    elif offset_str: # only offset
        return offset_str
    else: # only trig (offset_val is 0)
        return trig_str

def generate_parametric_std_origin():
    # 題型：求橢圓 $\\frac{x^2}{A} + \\frac{y^2}{B} = 1$ 的參數式
    # 答案：$x = \\sqrt{A}\\cos\\theta, y = \\sqrt{B}\\sin\\theta$

    a_param = random.randint(2, 6) # Semi-axis length
    b_param = random.randint(2, 6)
    
    # 20% 機率生成圓
    if random.random() < 0.2:
        b_param = a_param
    
    a_sq_val = a_param * a_param
    b_sq_val = b_param * b_param
    
    # 確保如果 a_param != b_param，則 a_sq_val 和 b_sq_val 不重複分配給 x 和 y
    # 避免 x^2/16 + y^2/9 和 x^2/9 + y^2/16 生成相同參數式 (雖然實際上會不同)
    if a_param != b_param and random.random() < 0.5:
        a_param, b_param = b_param, a_param
        a_sq_val, b_sq_val = b_sq_val, a_sq_val
            
    # 建立題目字串
    if a_sq_val == 1 and b_sq_val == 1:
        question_text = f"求圓 ${{x^2 + y^2 = 1}}$ 的參數式。"
    elif a_sq_val == 1:
        question_text = f"求橢圓 ${{x^2 + \\frac{{y^2}}{{{b_sq_val}}} = 1}}$ 的參數式。"
    elif b_sq_val == 1:
        question_text = f"求橢圓 ${{\\frac{{x^2}}{{{a_sq_val}}} + y^2 = 1}}$ 的參數式。"
    else:
        question_text = f"求橢圓 ${{\\frac{{x^2}}{{{a_sq_val}}} + \\frac{{y^2}}{{{b_sq_val}}} = 1}}$ 的參數式。"
        
    x_param_eq_core = _format_param_expr(0, a_param, "cos")
    y_param_eq_core = _format_param_expr(0, b_param, "sin")

    correct_answer_check = f"x={x_param_eq_core}, y={y_param_eq_core}"
    correct_answer_display = f"$x={x_param_eq_core}, y={y_param_eq_core} (0 \\le \\theta < 2\\pi)$"

    return {
        "question_text": question_text,
        "answer": correct_answer_check,
        "correct_answer": correct_answer_display
    }

def generate_parametric_std_shifted():
    # 題型：求橢圓 $\\frac{(x-h)^2}{A} + \\frac{(y-k)^2}{B} = 1$ 的參數式
    # 答案：$x = h + \\sqrt{A}\\cos\\theta, y = k + \\sqrt{B}\\sin\\theta$

    h = random.randint(-5, 5)
    k = random.randint(-5, 5)
    a_param = random.randint(2, 6)
    b_param = random.randint(2, 6)
    
    if random.random() < 0.2:
        b_param = a_param

    a_sq_val = a_param * a_param
    b_sq_val = b_param * b_param

    if a_param != b_param and random.random() < 0.5:
        a_param, b_param = b_param, a_param
        a_sq_val, b_sq_val = b_sq_val, a_sq_val

    # 建立 (x-h) 和 (y-k) 的平方項字串
    x_term_paren = f"(x{'+' if h < 0 else '-'}{abs(h)})" if h != 0 else "x"
    y_term_paren = f"(y{'+' if k < 0 else '-'}{abs(k)})" if k != 0 else "y"

    # 處理分母為1的情況 (e.g., x^2 + y^2/B = 1)
    x_denom_str = f"\\frac{{{x_term_paren}^2}}{{{a_sq_val}}}" if a_sq_val != 1 else f"{x_term_paren}^2"
    y_denom_str = f"\\frac{{{y_term_paren}^2}}{{{b_sq_val}}}" if b_sq_val != 1 else f"{y_term_paren}^2"
    
    question_text = f"求橢圓 ${{{x_denom_str} + {y_denom_str} = 1}}$ 的參數式。"

    x_param_eq_core = _format_param_expr(h, a_param, "cos")
    y_param_eq_core = _format_param_expr(k, b_param, "sin")
    
    correct_answer_check = f"x={x_param_eq_core}, y={y_param_eq_core}"
    correct_answer_display = f"$x={x_param_eq_core}, y={y_param_eq_core} (0 \\le \\theta < 2\\pi)$"

    return {
        "question_text": question_text,
        "answer": correct_answer_check,
        "correct_answer": correct_answer_display
    }

def generate_parametric_general_origin():
    # 題型：求橢圓 $C_1x^2 + C_2y^2 = D$ 的參數式
    # 答案：$x = \\sqrt{D/C_1}\\cos\\theta, y = \\sqrt{D/C_2}\\sin\\theta$

    # 選擇標準形式下的分母 A_denom, B_denom
    A_denom = random.randint(2, 10)
    B_denom = random.randint(2, 10)
    
    if random.random() < 0.2:
        B_denom = A_denom
    
    # 選擇 D 作為 A_denom 和 B_denom 的公倍數，以確保 C1, C2 為整數
    lcm_val = math.lcm(A_denom, B_denom)
    D = lcm_val * random.randint(2, 4) # 乘以一個倍數，讓 C1, C2 通常不為 1

    C1 = D // A_denom
    C2 = D // B_denom
    
    # 確保 C1, C2 都不為 1，以符合「一般式」的感覺
    while C1 == 1 or C2 == 1:
        A_denom = random.randint(2, 10)
        B_denom = random.randint(2, 10)
        if random.random() < 0.2:
            B_denom = A_denom
        lcm_val = math.lcm(A_denom, B_denom)
        D = lcm_val * random.randint(2, 4)
        C1 = D // A_denom
        C2 = D // B_denom
    
    question_text = f"求橢圓 ${{{C1}x^2 + {C2}y^2 = {D}}}$ 的參數式。"
    
    # 參數式中的 a, b 值為標準式分母的平方根
    a_param = int(math.sqrt(D / C1))
    b_param = int(math.sqrt(D / C2))

    x_param_eq_core = _format_param_expr(0, a_param, "cos")
    y_param_eq_core = _format_param_expr(0, b_param, "sin")

    correct_answer_check = f"x={x_param_eq_core}, y={y_param_eq_core}"
    correct_answer_display = f"$x={x_param_eq_core}, y={y_param_eq_core} (0 \\le \\theta < 2\\pi)$"

    return {
        "question_text": question_text,
        "answer": correct_answer_check,
        "correct_answer": correct_answer_display
    }

def generate_parametric_general_shifted():
    # 題型：求橢圓 $C_1(x-h)^2 + C_2(y-k)^2 = D$ 的參數式
    # 答案：$x = h + \\sqrt{D/C_1}\\cos\\theta, y = k + \\sqrt{D/C_2}\\sin\\theta$

    h = random.randint(-5, 5)
    k = random.randint(-5, 5)

    A_denom = random.randint(2, 10)
    B_denom = random.randint(2, 10)
    
    if random.random() < 0.2:
        B_denom = A_denom
    
    lcm_val = math.lcm(A_denom, B_denom)
    D = lcm_val * random.randint(2, 4)

    C1 = D // A_denom
    C2 = D // B_denom
    
    while C1 == 1 or C2 == 1:
        A_denom = random.randint(2, 10)
        B_denom = random.randint(2, 10)
        if random.random() < 0.2:
            B_denom = A_denom
        lcm_val = math.lcm(A_denom, B_denom)
        D = lcm_val * random.randint(2, 4)
        C1 = D // A_denom
        C2 = D // B_denom

    x_h_term = f"(x{'+' if h < 0 else '-'}{abs(h)})"
    y_k_term = f"(y{'+' if k < 0 else '-'}{abs(k)})"
    
    question_text = f"求橢圓 ${{{C1}{x_h_term}^2 + {C2}{y_k_term}^2 = {D}}}$ 的參數式。"
    
    a_param = int(math.sqrt(D / C1))
    b_param = int(math.sqrt(D / C2))
    
    x_param_eq_core = _format_param_expr(h, a_param, "cos")
    y_param_eq_core = _format_param_expr(k, b_param, "sin")

    correct_answer_check = f"x={x_param_eq_core}, y={y_param_eq_core}"
    correct_answer_display = f"$x={x_param_eq_core}, y={y_param_eq_core} (0 \\le \\theta < 2\\pi)$"

    return {
        "question_text": question_text,
        "answer": correct_answer_check,
        "correct_answer": correct_answer_display
    }

def generate_scaling_transformation():
    # 題型：已知圓 $\Gamma: x^2+y^2=R^2$ 經伸縮變換得到橢圓 $\Gamma'$，求 $\Gamma'$ 方程式。
    
    R = random.randint(1, 5) # 圓的半徑
    Rx_scale = random.randint(2, 5) # x軸方向伸縮倍數
    Ry_scale = random.randint(2, 5) # y軸方向伸縮倍數
    
    # 確保伸縮倍數不同，以形成橢圓
    while Rx_scale == Ry_scale:
        Ry_scale = random.randint(2, 5)

    question_text = (
        f"已知圓 $\\Gamma: x^2+y^2={{{R*R}}}$ 以原點O為中心，沿著x軸方向伸縮{{{Rx_scale}}}倍、沿著y軸方向伸縮{{{Ry_scale}}}倍，得到橢圓 $\\Gamma'$。<br>"
        f"求橢圓 $\\Gamma'$ 的方程式。"
    )
    
    # 伸縮後的橢圓方程式為 $\\frac{x^2}{(R \\cdot R_x)^2} + \\frac{y^2}{(R \\cdot R_y)^2} = 1$
    new_a_sq_denom = R*R * Rx_scale*Rx_scale
    new_b_sq_denom = R*R * Ry_scale*Ry_scale
    
    # 標準化答案字串，移除 \\frac{} 以便於檢查
    correct_answer_check = f"frac{{x^2}}{{{new_a_sq_denom}}}+frac{{y^2}}{{{new_b_sq_denom}}}=1"
    correct_answer_display = f"$\\frac{{x^2}}{{{new_a_sq_denom}}} + \\frac{{y^2}}{{{new_b_sq_denom}}} = 1$"

    return {
        "question_text": question_text,
        "answer": correct_answer_check,
        "correct_answer": correct_answer_display
    }

def generate_geometric_properties_center_axes():
    # 題型：給定橢圓方程式，求中心坐標或長短軸長。
    
    h = random.randint(-5, 5)
    k = random.randint(-5, 5)
    
    # 生成兩個不同的半軸平方值
    val1 = random.randint(4, 25) 
    val2 = random.randint(1, val1 - 1)
    
    # 隨機決定長軸方向 (x軸或y軸平行)
    is_horizontal_major = random.choice([True, False])
    if is_horizontal_major:
        major_a_sq_denom = val1 # 較大的分母對應長軸
        minor_b_sq_denom = val2 # 較小的分母對應短軸
    else:
        major_a_sq_denom = val2
        minor_b_sq_denom = val1

    # 建立橢圓方程式字串
    x_term_sq = f"(x{'+' if h < 0 else '-'}{abs(h)})^2" if h != 0 else "x^2"
    y_term_sq = f"(y{'+' if k < 0 else '-'}{abs(k)})^2" if k != 0 else "y^2"

    equation_str = f"$\\frac{{{x_term_sq}}}{{{major_a_sq_denom}}} + \\frac{{{y_term_sq}}}{{{minor_b_sq_denom}}} = 1$"
    
    # 隨機選擇要問的問題類型
    prop_to_ask = random.choice(['center', 'major_axis_length', 'minor_axis_length'])
    
    question_text = ""
    correct_answer_check = ""
    correct_answer_display = ""

    if prop_to_ask == 'center':
        question_text = f"已知橢圓方程式為 ${equation_str}$，求其中心坐標。"
        correct_answer_check = f"({h},{k})"
        correct_answer_display = f"$({h},{k})$"
    elif prop_to_ask == 'major_axis_length':
        question_text = f"已知橢圓方程式為 ${equation_str}$，求其長軸長。"
        # 長軸長為 2 * 較大半軸長
        major_axis_length = 2 * int(math.sqrt(max(major_a_sq_denom, minor_b_sq_denom)))
        correct_answer_check = str(major_axis_length)
        correct_answer_display = f"${major_axis_length}$"
    else: # minor_axis_length
        question_text = f"已知橢圓方程式為 ${equation_str}$，求其短軸長。"
        # 短軸長為 2 * 較小半軸長
        minor_axis_length = 2 * int(math.sqrt(min(major_a_sq_denom, minor_b_sq_denom)))
        correct_answer_check = str(minor_axis_length)
        correct_answer_display = f"${minor_axis_length}$"
        
    return {
        "question_text": question_text,
        "answer": correct_answer_check,
        "correct_answer": correct_answer_display
    }


def parse_parametric_expression(expression):
    """
    解析一個參數式子部分，例如 '1+3cos{theta}' 或 '2sin{theta}'。
    返回 (h_val, coeff_val, func_type) 元組。
    h_val: 偏移量, coeff_val: 三角函數的係數, func_type: 'cos' 或 'sin'
    """
    expression = expression.strip().lower().replace(' ', '')
    expression = expression.replace('\\cos', 'cos').replace('\\sin', 'sin').replace('\\theta', 'theta')

    h_val = 0
    coeff_val = 0
    func_type = None

    # 嘗試尋找 'cos(theta)' 或 'sin(theta)'
    trig_match = re.search(r"([+-]?\d*)?(cos|sin)(theta)", expression)
    
    if trig_match:
        func_type = trig_match.group(2)
        full_trig_term = trig_match.group(0) # 完整匹配到的三角函數部分，例如 "3cos(theta)"

        trig_coeff_str = trig_match.group(1)
        if trig_coeff_str == '':
            coeff_val = 1
        elif trig_coeff_str == '+':
            coeff_val = 1
        elif trig_coeff_str == '-':
            coeff_val = -1
        else:
            try:
                coeff_val = int(trig_coeff_str)
            except ValueError:
                return None # 係數格式錯誤

        # 從表達式中移除三角函數部分，剩下的應該是常數偏移量
        constant_expression = expression.replace(full_trig_term, '')
        
        if constant_expression:
            try:
                h_val = int(constant_expression)
            except ValueError:
                return None # 常數部分格式錯誤
    else: # 沒有找到三角函數，假設整個表達式就是一個常數
        try:
            h_val = int(expression)
            coeff_val = 0 # 沒有三角函數部分
        except ValueError:
            return None # 既不是常數也不是識別的三角函數形式

    return (h_val, coeff_val, func_type)

def normalize_parametric_term(term_str):
    """將單個參數式項 (例如 'x=1+3cos{theta}') 規範化為 (變數名, (h, a/b, func_type))。"""
    term_str = term_str.strip().replace(' ', '')
    
    parts = term_str.split('=', 1)
    if len(parts) != 2:
        return None, None # 格式不正確
    
    var_name = parts[0].lower() # 變數名 'x' 或 'y'
    expression = parts[1]

    parsed_data = parse_parametric_expression(expression)
    if parsed_data is None:
        return None, None
    
    return var_name, parsed_data

def check_parametric_answer(user_answer, correct_answer_check):
    """檢查參數式答案，例如 "x=..., y=..." """
    user_parts = [p.strip() for p in user_answer.split(',')]
    correct_parts = [p.strip() for p in correct_answer_check.split(',')]

    if len(user_parts) != 2 or len(correct_parts) != 2:
        return {"correct": False, "result": "參數式應包含x和y兩部分，以逗號分隔。", "next_question": False}

    user_parsed = {}
    for part in user_parts:
        var, parsed_data = normalize_parametric_term(part)
        if var and parsed_data:
            user_parsed[var] = parsed_data
        else:
            return {"correct": False, "result": "您的參數式格式不正確，請檢查每個部分的寫法。", "next_question": False}
    
    correct_parsed = {}
    for part in correct_parts: # correct_answer_check 已經是標準格式
        var, parsed_data = normalize_parametric_term(part)
        if var and parsed_data:
            correct_parsed[var] = parsed_data
        else:
            # 系統生成的答案不應出現解析錯誤
            return {"correct": False, "result": "系統答案解析錯誤，請聯繫管理員。", "next_question": False}

    is_correct = True
    # 比較 x 部分
    if 'x' in user_parsed and 'x' in correct_parsed:
        if user_parsed['x'] != correct_parsed['x']:
            is_correct = False
    else:
        is_correct = False # 缺少 x 或 y 部分
    
    # 比較 y 部分
    if 'y' in user_parsed and 'y' in correct_parsed:
        if user_parsed['y'] != correct_parsed['y']:
            is_correct = False
    else:
        is_correct = False # 缺少 x 或 y 部分
    
    result_text = f"完全正確！答案是 ${correct_answer_check}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer_check}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}

def check_equation_answer(user_answer, correct_answer_check):
    """檢查方程式答案，例如 "x^2/A + y^2/B = 1" """
    
    user_ans_clean = user_answer.strip().lower().replace(' ', '')
    correct_ans_clean = correct_answer_check.strip().lower().replace(' ', '')

    # 針對標準橢圓方程式格式: frac{x^2}{A}+frac{y^2}{B}=1
    # 注意這裡的 regex 需要匹配 'x^2' 或 'xprime^2' 等，以及 'y^2' 或 'yprime^2'
    # 為了簡化，目前生成的答案只有 'x^2' 和 'y^2'
    pattern_std = r"frac\{(x\^2|xprime\^2)\}\{(\d+)\}\+frac\{(y\^2|yprime\^2)\}\{(\d+)\}=1"
    
    match_user = re.fullmatch(pattern_std, user_ans_clean)
    match_correct = re.fullmatch(pattern_std, correct_ans_clean)

    is_correct = False
    
    if match_user and match_correct:
        user_x_denom = int(match_user.group(2))
        user_y_denom = int(match_user.group(4))
        
        correct_x_denom = int(match_correct.group(2))
        correct_y_denom = int(match_correct.group(4))

        # 對於伸縮變換題，x 和 y 的分母位置是固定的，不能互換
        if (user_x_denom == correct_x_denom and user_y_denom == correct_y_denom):
            is_correct = True
    else:
        # 如果 regex 不匹配，則進行直接字串比較 (這適用於更複雜的方程式或用戶輸入了其他形式)
        if user_ans_clean == correct_ans_clean:
            is_correct = True

    result_text = f"完全正確！答案是 ${correct_answer_check}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer_check}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}

def check_coordinate_answer(user_answer, correct_answer_check):
    """檢查坐標答案，例如 "(h,k)" """
    
    user_ans_clean = user_answer.strip().replace(' ', '')
    correct_ans_clean = correct_answer_check.strip().replace(' ', '')

    coord_pattern = r"\(([-+]?\d+),([-+]?\d+)\)"
    
    match_user = re.fullmatch(coord_pattern, user_ans_clean)
    match_correct = re.fullmatch(coord_pattern, correct_ans_clean)

    is_correct = False

    if match_user and match_correct:
        user_h = int(match_user.group(1))
        user_k = int(match_user.group(2))
        correct_h = int(match_correct.group(1))
        correct_k = int(match_correct.group(2))

        if user_h == correct_h and user_k == correct_k:
            is_correct = True
    
    result_text = f"完全正確！答案是 ${correct_answer_check}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer_check}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}


def check_numeric_answer(user_answer, correct_answer_check):
    """檢查數值答案，例如 '5' """
    
    try:
        user_val = float(user_answer)
        correct_val = float(correct_answer_check)
        is_correct = (abs(user_val - correct_val) < 1e-9) # 浮點數比較
    except ValueError:
        # 如果不是簡單的浮點數，則嘗試字串比較 (例如，為了處理根號表達式，但目前沒有生成)
        user_ans_clean = user_answer.strip().lower().replace(' ', '')
        correct_ans_clean = correct_answer_check.strip().lower().replace(' ', '')
        is_correct = (user_ans_clean == correct_ans_clean)

    result_text = f"完全正確！答案是 ${correct_answer_check}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer_check}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}


def check(user_answer, correct_answer_check):
    """
    檢查答案是否正確。
    `correct_answer_check` 參數是 generate 函數返回的 `answer` 字段，
    用於內部比較，而非顯示用的 `correct_answer` 字段。
    """
    if 'cos{\\theta}' in correct_answer_check or 'sin{\\theta}' in correct_answer_check:
        return check_parametric_answer(user_answer, correct_answer_check)
    elif 'frac{' in correct_answer_check and '=' in correct_answer_check:
        return check_equation_answer(user_answer, correct_answer_check)
    elif correct_answer_check.startswith('(') and correct_answer_check.endswith(')'):
        return check_coordinate_answer(user_answer, correct_answer_check)
    else: # 數值答案 (例如軸長)
        return check_numeric_answer(user_answer, correct_answer_check)