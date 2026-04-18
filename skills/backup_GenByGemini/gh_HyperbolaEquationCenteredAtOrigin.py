import random
from fractions import Fraction
import re
import math

# Pythagorean triples (a, b, c) where c is hypotenuse, and a, b are legs.
# For hyperbola centered at origin: c_hyperbola^2 = a_hyperbola^2 + b_hyperbola^2.
# So (a_hyperbola, b_hyperbola, c_hyperbola) must be a Pythagorean triple.
P_TRIPLES = [(3, 4, 5), (5, 12, 13), (8, 15, 17)]

def get_hyperbola_params():
    """Generates a, b, c values for a hyperbola centered at origin."""
    leg1, leg2, hyp = random.choice(P_TRIPLES)
    
    # 'a' in hyperbola equation is related to vertices (half transverse axis length).
    # 'b' in hyperbola equation is related to conjugate axis (half conjugate axis length).
    # 'c' in hyperbola equation is related to foci (distance from center to focus).
    # The relationship is c^2 = a^2 + b^2.
    # Here, leg1 and leg2 will be used for a_val and b_val, and hyp for c_val.
    
    # Randomly assign which leg corresponds to 'a' and which to 'b' for the hyperbola.
    if random.choice([True, False]):
        a_val = leg1
        b_val = leg2
    else:
        a_val = leg2
        b_val = leg1
    
    c_val = hyp
    
    # Randomly choose if the transverse axis is on the x-axis or y-axis
    x_axis_transverse = random.choice([True, False])
    
    return a_val, b_val, c_val, x_axis_transverse

def format_hyperbola_equation(a_sq, b_sq, x_axis_transverse):
    """
    Formats the hyperbola equation string, simplifying denominators of 1.
    
    Args:
        a_sq (int): The square of 'a' value. Denominator for the positive term.
        b_sq (int): The square of 'b' value. Denominator for the negative term.
        x_axis_transverse (bool): True if transverse axis is on x-axis, False for y-axis.
    
    Returns:
        str: The LaTeX formatted hyperbola equation.
    """
    if x_axis_transverse:
        x_term_content = r"x^2"
        y_term_content = r"y^2"
    else:
        x_term_content = r"y^2"
        y_term_content = r"x^2"

    term1 = x_term_content if a_sq == 1 else rf"\\frac{{{x_term_content}}}{{{a_sq}}}"
    term2 = y_term_content if b_sq == 1 else rf"\\frac{{{y_term_content}}}{{{b_sq}}}"

    return rf"{term1} - {term2} = 1"

def format_asymptote_equation(a_val, b_val, x_axis_transverse):
    """
    Formats the asymptote equations string in Ax \\pm By = 0 form,
    or y = \\pm (M/N)x form depending on configuration, adhering to examples.
    
    For x^2/a^2 - y^2/b^2 = 1, asymptotes are y = +/- (b/a)x => bx +/- ay = 0
    For y^2/a^2 - x^2/b^2 = 1, asymptotes are y = +/- (a/b)x => ax +/- by = 0
    
    Args:
        a_val (int): The 'a' value of the hyperbola.
        b_val (int): The 'b' value of the hyperbola.
        x_axis_transverse (bool): True if transverse axis is on x-axis, False for y-axis.
        
    Returns:
        str: The LaTeX formatted asymptote equation string.
    """
    if x_axis_transverse: # Asymptotes y = +/- (b/a)x => bx +/- ay = 0
        return rf"{b_val}x \\pm {a_val}y = 0"
    else: # Asymptotes y = +/- (a/b)x => ax +/- by = 0
        return rf"{a_val}x \\pm {b_val}y = 0"

def format_coords_pair(val, is_x_coord):
    """
    Formats coordinates string for vertices or foci, e.g., (\\pm X, 0) or (0, \\pm Y).
    
    Args:
        val (int): The absolute coordinate value (a or c).
        is_x_coord (bool): True if coordinates are on x-axis, False for y-axis.
        
    Returns:
        str: The LaTeX formatted coordinate pair string.
    """
    if is_x_coord:
        return rf"(\\pm {val}, 0)"
    else:
        return rf"(0, \\pm {val})"

def generate(level=1):
    """
    生成關於中心在原點的雙曲線標準方程式、漸近線及相關性質的題目。
    
    Args:
        level (int): 難度等級 (目前未使用，預設為1)。
        
    Returns:
        dict: 包含 'question_text', 'answer', 'correct_answer' 的字典。
    """
    problem_type = random.choice([
        'eq_from_foci_transverse',       # 從焦點和貫軸長求方程式
        'eq_from_foci_conjugate',        # 從焦點和共軛軸長求方程式
        'eq_from_vertices_conjugate',    # 從頂點和共軛軸長求方程式
        'eq_from_vertices_foci',         # 從頂點和焦點求方程式
        'props_from_eq_vertices_foci',   # 從方程式求頂點和焦點
        'asymptotes_from_eq',            # 從方程式求漸近線
        'eq_from_asymptotes_focus'       # 從漸近線和焦點求方程式
    ])

    a_val, b_val, c_val, x_axis_transverse = get_hyperbola_params()
    a_sq = a_val**2
    b_sq = b_val**2

    question_text = ""
    correct_answer = ""

    if problem_type == 'eq_from_foci_transverse':
        # 給定焦點 (c) 和貫軸長 (2a)
        foci_coord_str = format_coords_pair(c_val, x_axis_transverse)
        transverse_len = 2 * a_val
        
        question_text = f"求滿足下列條件的雙曲線標準方程式：中心在原點，焦點為 ${foci_coord_str}$，貫軸長為 ${transverse_len}$。"
        correct_answer = format_hyperbola_equation(a_sq, b_sq, x_axis_transverse)

    elif problem_type == 'eq_from_foci_conjugate':
        # 給定焦點 (c) 和共軛軸長 (2b)
        foci_coord_str = format_coords_pair(c_val, x_axis_transverse)
        conjugate_len = 2 * b_val
        
        question_text = f"求滿足下列條件的雙曲線標準方程式：中心在原點，焦點為 ${foci_coord_str}$，共軛軸長為 ${conjugate_len}$。"
        correct_answer = format_hyperbola_equation(a_sq, b_sq, x_axis_transverse)

    elif problem_type == 'eq_from_vertices_conjugate':
        # 給定頂點 (a) 和共軛軸長 (2b)
        vertices_coord_str = format_coords_pair(a_val, x_axis_transverse)
        conjugate_len = 2 * b_val
        
        question_text = f"求滿足下列條件的雙曲線標準方程式：中心在原點，頂點為 ${vertices_coord_str}$，共軛軸長為 ${conjugate_len}$。"
        correct_answer = format_hyperbola_equation(a_sq, b_sq, x_axis_transverse)
        
    elif problem_type == 'eq_from_vertices_foci':
        # 給定頂點 (a) 和焦點 (c)
        vertices_coord_str = format_coords_pair(a_val, x_axis_transverse)
        foci_coord_str = format_coords_pair(c_val, x_axis_transverse)
        
        question_text = f"求滿足下列條件的雙曲線標準方程式：中心在原點，頂點為 ${vertices_coord_str}$，焦點為 ${foci_coord_str}$。"
        correct_answer = format_hyperbola_equation(a_sq, b_sq, x_axis_transverse)

    elif problem_type == 'props_from_eq_vertices_foci':
        # 給定方程式，求頂點和焦點
        equation_text = format_hyperbola_equation(a_sq, b_sq, x_axis_transverse)
        
        vertex_str = format_coords_pair(a_val, x_axis_transverse)
        focus_str = format_coords_pair(c_val, x_axis_transverse)
        
        question_text = f"求雙曲線方程式 ${equation_text}$ 的頂點與焦點坐標。"
        correct_answer = f"頂點：${vertex_str}$，焦點：${focus_str}$"

    elif problem_type == 'asymptotes_from_eq':
        # 給定方程式，求漸近線
        equation_text = format_hyperbola_equation(a_sq, b_sq, x_axis_transverse)
        
        question_text = f"求雙曲線方程式 ${equation_text}$ 的兩條漸近線方程式。"
        correct_answer = format_asymptote_equation(a_val, b_val, x_axis_transverse)

    elif problem_type == 'eq_from_asymptotes_focus':
        # 給定漸近線和其中一個焦點，求方程式
        asymptote_text = format_asymptote_equation(a_val, b_val, x_axis_transverse)
        
        # 隨機選擇一個焦點座標 (正或負)
        if x_axis_transverse:
            focus_coord_val = c_val if random.choice([True, False]) else -c_val
            focus_coord_str = f"({focus_coord_val}, 0)"
        else:
            focus_coord_val = c_val if random.choice([True, False]) else -c_val
            focus_coord_str = f"(0, {focus_coord_val})"
            
        question_text = f"求漸近線方程式為 ${asymptote_text}$ 且其中一個焦點為 ${focus_coord_str}$ 的雙曲線方程式。"
        correct_answer = format_hyperbola_equation(a_sq, b_sq, x_axis_transverse)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查使用者答案是否正確。

    Args:
        user_answer (str): 使用者提交的答案。
        correct_answer (str): 正確答案。

    Returns:
        dict: 包含 'correct' (bool) 和 'result' (feedback string) 的字典。
    """
    # 將使用者答案和正確答案標準化，移除空格並將 '+/-' 替換為 LaTeX 的 '\\pm'
    user_answer_norm = user_answer.strip().lower().replace(" ", "").replace("+/-", r"\\pm")
    correct_answer_norm = correct_answer.strip().lower().replace(" ", "").replace("+/-", r"\\pm")
    
    is_correct = (user_answer_norm == correct_answer_norm)
    
    # 由於題目答案涉及複雜的數學方程式和座標表示，
    # 這裡採用嚴格的字符串匹配。若匹配失敗，則浮點數轉換會因為非數字字符串而失敗，
    # 保持模板的原有邏輯，但實際上在此技能中不會觸發浮點數轉換。
    if not is_correct:
        try:
            # 嘗試浮點數比較，以防答案是純數字且格式略有不同
            if float(user_answer_norm) == float(correct_answer_norm):
                is_correct = True
        except ValueError:
            pass

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}