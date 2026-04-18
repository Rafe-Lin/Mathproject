import random
import re # For robust string normalization in check function

def generate(level=1):
    """
    生成「頂點在原點(0,0)，對稱軸為x軸或y軸的拋物線標準方程式」相關題目。
    包含：
    1. 根據焦點求拋物線方程式
    2. 根據準線求拋物線方程式
    3. 根據方程式求頂點、焦點、準線
    """
    problem_type = random.choice([
        'find_equation_from_focus',
        'find_equation_from_directrix',
        'find_properties_from_equation'
    ])

    if problem_type == 'find_equation_from_focus':
        return generate_equation_from_focus_problem()
    elif problem_type == 'find_equation_from_directrix':
        return generate_equation_from_directrix_problem()
    else: # 'find_properties_from_equation'
        return generate_properties_from_equation_problem()

def get_non_zero_c():
    """生成一個非零的整數 c 值。"""
    c = 0
    while c == 0:
        # c 可以是 -5 到 5 之間的非零整數，避免生成太大的係數
        c = random.randint(-5, 5) 
    return c

def generate_equation_from_focus_problem():
    """生成根據焦點求拋物線方程式的問題。"""
    c = get_non_zero_c()
    axis_type = random.choice(['x', 'y']) # 對稱軸為 x 軸或 y 軸

    if axis_type == 'y': # 對稱軸為 y 軸: x^2 = 4cy, 焦點 (0, c), 準線 y = -c
        focus_coord = (0, c)
        correct_equation = f"x^{{2}} = {4 * c}y"
    else: # 對稱軸為 x 軸: y^2 = 4cx, 焦點 (c, 0), 準線 x = -c
        focus_coord = (c, 0)
        correct_equation = f"y^{{2}} = {4 * c}x"

    question_text = f"求頂點為 $(0,0)$，焦點為 $({focus_coord[0]},{focus_coord[1]})$ 的拋物線方程式。"
    
    return {
        "question_text": question_text,
        "answer": correct_equation, # 儲存答案以便檢查
        "correct_answer": correct_equation
    }

def generate_equation_from_directrix_problem():
    """生成根據準線求拋物線方程式的問題。"""
    c = get_non_zero_c()
    axis_type = random.choice(['x', 'y']) # 對稱軸為 x 軸或 y 軸

    if axis_type == 'y': # 對稱軸為 y 軸: x^2 = 4cy, 焦點 (0, c), 準線 y = -c
        directrix_equation_str = f"y = {-c}"
        correct_equation = f"x^{{2}} = {4 * c}y"
    else: # 對稱軸為 x 軸: y^2 = 4cx, 焦點 (c, 0), 準線 x = -c
        directrix_equation_str = f"x = {-c}"
        correct_equation = f"y^{{2}} = {4 * c}x"

    question_text = f"求頂點為 $(0,0)$，準線為 ${directrix_equation_str}$ 的拋物線方程式。"
    
    return {
        "question_text": question_text,
        "answer": correct_equation,
        "correct_answer": correct_equation
    }

def generate_properties_from_equation_problem():
    """生成根據方程式求頂點、焦點、準線的問題。"""
    c = get_non_zero_c()
    axis_type = random.choice(['x', 'y']) # 對稱軸為 x 軸或 y 軸

    if axis_type == 'y': # x^2 = 4cy
        given_equation_str = f"x^{{2}} = {4 * c}y"
        focus_coord_str = f"(0,{c})"
        directrix_equation_str = f"y = {-c}"
    else: # y^2 = 4cx
        given_equation_str = f"y^{{2}} = {4 * c}x"
        focus_coord_str = f"({c},0)"
        directrix_equation_str = f"x = {-c}"

    vertex_str = "(0,0)"
    
    question_text = f"求拋物線 ${given_equation_str}$ 的頂點、焦點與準線方程式。"
    
    # 標準答案格式: 頂點:(0,0), 焦點:(-3,0), 準線:x=3
    correct_answer_structured = f"頂點:{vertex_str}, 焦點:{focus_coord_str}, 準線:{directrix_equation_str}"

    return {
        "question_text": question_text,
        "answer": correct_answer_structured, # 儲存結構化答案以便檢查
        "correct_answer": correct_answer_structured
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    user_answer: 學生提交的答案字串。
    correct_answer: 題目生成的正確答案字串，可能是方程式或結構化屬性。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()

    is_correct = False
    feedback = ""

    # 輔助函數：標準化方程式字串，以便比較
    def normalize_equation_string(eq_str):
        eq_str = eq_str.replace(' ', '').lower() # 移除空格並轉為小寫
        eq_str = eq_str.replace('^2', '**2') # 標準化平方符號 (x^2 -> x**2)
        
        # 處理係數 1 或 -1 的情況，例如 'x' -> '1x', '-x' -> '-1x'
        # 但要注意不要影響 x**2
        eq_str = re.sub(r'(?<!\d|^)([xy])(?!\*\*|\d)', r'1\1', eq_str) # Add 1 if no digit before and not power
        eq_str = re.sub(r'(?<!\d|^)-([xy])(?!\*\*|\d)', r'-1\1', eq_str) # Add -1 if no digit before and not power
        
        return eq_str

    # 輔助函數：標準化結構化答案，例如 "頂點:(0,0), 焦點:(-3,0), 準線:x=3"
    def normalize_structured_answer(ans_str):
        parts = ans_str.split(',')
        normalized_parts = {}
        for part in parts:
            if '頂點' in part:
                normalized_parts['vertex'] = part.split(':')[-1].strip().replace(' ', '')
            elif '焦點' in part:
                normalized_parts['focus'] = part.split(':')[-1].strip().replace(' ', '')
            elif '準線' in part:
                normalized_parts['directrix'] = normalize_equation_string(part.split(':')[-1].strip())
        return normalized_parts

    # 判斷是方程式題型還是屬性題型
    # 檢查 correct_answer 中是否包含 'x^2' 或 'y^2' 樣式的方程式
    if any(s in correct_answer for s in ["x^2", "y^2", "x**2", "y**2"]):
        # 方程式題型
        try:
            norm_user = normalize_equation_string(user_answer)
            norm_correct = normalize_equation_string(correct_answer)
            
            # 嘗試分割左右兩邊
            correct_sides = norm_correct.split('=', 1)
            user_sides = norm_user.split('=', 1)

            if len(correct_sides) == 2 and len(user_sides) == 2:
                # 檢查是否兩邊匹配 (考慮左右兩邊對調的情況)
                match1 = (correct_sides[0] == user_sides[0] and correct_sides[1] == user_sides[1])
                match2 = (correct_sides[0] == user_sides[1] and correct_sides[1] == user_sides[0])
                is_correct = match1 or match2
            else: # 如果用戶答案不是標準的 A=B 形式
                is_correct = False

            if is_correct:
                feedback = f"完全正確！答案是 ${correct_answer}$。"
            else:
                feedback = f"答案不正確。正確答案應為：${correct_answer}$"
        except Exception: # 捕獲任何解析錯誤
            feedback = f"您的方程式格式似乎不正確。請確保使用 $x^{{2}}=4cy$ 或 $y^{{2}}=4cx$ 格式。<br>正確答案應為：${correct_answer}$"
            is_correct = False
    elif "頂點" in correct_answer and "焦點" in correct_answer and "準線" in correct_answer:
        # 結構化屬性題型 (頂點、焦點、準線)
        try:
            user_parts = normalize_structured_answer(user_answer)
            correct_parts = normalize_structured_answer(correct_answer)
            
            is_correct = (user_parts.get('vertex') == correct_parts.get('vertex') and
                          user_parts.get('focus') == correct_parts.get('focus') and
                          user_parts.get('directrix') == correct_parts.get('directrix'))
            
            if is_correct:
                feedback = f"完全正確！答案是 ${correct_answer}$。"
            else:
                feedback = f"答案不正確。正確答案應為：${correct_answer}$"
        except Exception: # 捕獲解析錯誤
            feedback = f"您的答案格式似乎不正確，請參考正確答案格式：頂點:(0,0), 焦點:(-3,0), 準線:x=3<br>正確答案應為：${correct_answer}$"
            is_correct = False
    else:
        # 處理未預期的答案類型，作為通用字串比較
        is_correct = (user_answer.lower() == correct_answer.lower())
        if is_correct:
            feedback = f"完全正確！答案是 ${correct_answer}$。"
        else:
            feedback = f"答案不正確。正確答案應為：${correct_answer}$"

    return {"correct": is_correct, "result": feedback, "next_question": True}