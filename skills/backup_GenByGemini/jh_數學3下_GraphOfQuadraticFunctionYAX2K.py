import random
from fractions import Fraction
import uuid
import os

def generate(level=1):
    """
    生成關於 y = ax^2 + k 形式的二次函數圖形的問題。
    題型包含：
    1. 判斷圖形性質 (頂點、開口方向)
    2. 比較開口寬窄
    3. 描述圖形平移
    4. 從性質辨識方程式 (選擇題)
    """
    problem_type = random.choice(['properties', 'compare_width', 'translation', 'identify_equation'])
    
    if problem_type == 'properties':
        return generate_properties_problem()
    elif problem_type == 'compare_width':
        return generate_compare_width_problem()
    elif problem_type == 'translation':
        return generate_translation_problem()
    else: # identify_equation
        return generate_identify_equation_problem()

def _generate_params():
    """生成二次函數 y = ax^2 + k 的參數 a 和 k。"""
    # 生成 a (可以是非1的整數或分數)
    if random.random() < 0.6:  # 60% 的機率為整數
        a = random.choice([-4, -3, -2, 2, 3, 4])
    else:  # 40% 的機率為分數
        sign = random.choice([-1, 1])
        num = random.randint(1, 4)
        den = random.randint(num + 1, 6) # 確保為真分數且分母稍大
        a = Fraction(sign * num, den)

    # 生成 k
    k = random.randint(-10, 10)
    
    return a, k

def _format_coeff(val):
    """將係數格式化為 LaTeX 字串。"""
    if val == 1:
        return ""
    if val == -1:
        return "-"
    
    if isinstance(val, Fraction):
        if val.denominator == 1:
            return str(val.numerator)
        
        # 處理負號位置
        if val.numerator < 0:
            return f"-\\frac{{{-val.numerator}}}{{{val.denominator}}}"
        else:
            return f"\\frac{{{val.numerator}}}{{{val.denominator}}}"
            
    if val == int(val):
        return str(int(val))
    
    return str(val)

def _format_equation(a, k):
    """將 y = ax^2 + k 格式化為 LaTeX 字串。"""
    a_str = _format_coeff(a)
    x_squared_part = f"{a_str}x^2"
    
    if k == 0:
        return f"y = {x_squared_part}"
    
    op_str = "+" if k > 0 else "-"
    k_val = abs(k)
    
    if k_val == int(k_val):
        k_val = int(k_val)

    return f"y = {x_squared_part} {op_str} {k_val}"

def generate_properties_problem():
    """
    題型：判斷圖形性質 (頂點、開口方向)
    """
    a, k = _generate_params()
    equation = _format_equation(a, k)
    
    direction = "向上" if a > 0 else "向下"
    
    question_text = f"請問二次函數 ${equation}$ 的頂點座標與開口方向為何？<br>(請用頓號、分隔答案，例如：(0,-5)、向下)"
    correct_answer = f"({0},{k})、{direction}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_compare_width_problem():
    """
    題型：比較開口寬窄
    """
    a1, k1 = _generate_params()
    
    # 確保 a2 的絕對值與 a1 不同
    while True:
        a2, k2 = _generate_params()
        if abs(a1) != abs(a2):
            break
            
    eq1 = _format_equation(a1, k1)
    eq2 = _format_equation(a2, k2)
    
    comparison_word = random.choice(["寬", "窄"])
    
    if comparison_word == "寬":
        # |a| 越小，開口越寬
        correct_label = "A" if abs(a1) < abs(a2) else "B"
    else: # 窄
        # |a| 越大，開口越窄
        correct_label = "A" if abs(a1) > abs(a2) else "B"

    question_text = f"比較 $A: {eq1}$ 與 $B: {eq2}$ 兩個二次函數的圖形，何者的開口較**{comparison_word}**？<br>(請填代號 A 或 B)"
    
    return {
        "question_text": question_text,
        "answer": correct_label,
        "correct_answer": correct_label
    }

def generate_translation_problem():
    """
    題型：描述圖形平移
    """
    a, k = _generate_params()
    # 確保有平移
    while k == 0:
        a, k = _generate_params()
        
    eq_base = _format_equation(a, 0)
    eq_translated = _format_equation(a, k)
    
    direction = "向上" if k > 0 else "向下"
    distance = abs(k)
    
    question_text = f"二次函數 ${eq_translated}$ 的圖形，可由 ${eq_base}$ 的圖形向{direction}平移多少單位而得？"
    
    if distance == int(distance):
        distance = int(distance)
        
    correct_answer = str(distance)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_identify_equation_problem():
    """
    題型：從性質辨識方程式 (選擇題)
    """
    a, k = _generate_params()
    vertex_str = f"(0, {k})"
    direction = "向上" if a > 0 else "向下"

    question_text = f"某二次函數的圖形為一條拋物線，其頂點為 ${vertex_str}$，且開口{direction}。下列何者可能為此二次函數的方程式？"
    
    correct_eq = _format_equation(a, k)
    
    # 產生干擾選項
    distractors = set()
    
    # 1. k 錯誤
    wrong_k = -k if k != 0 else k + random.randint(1,5)
    distractors.add(_format_equation(a, wrong_k))
    
    # 2. a 的正負號錯誤
    distractors.add(_format_equation(-a, k))
    
    # 3. a 的正負號和 k 都錯誤
    distractors.add(_format_equation(-a, wrong_k))

    # 確保有三個獨立的干擾項
    while len(distractors) < 3:
        new_a, new_k = _generate_params()
        # 確保生成的干擾項不符合題目條件
        if (new_a > 0 and a < 0) or (new_a < 0 and a > 0) or (new_k != k):
            distractors.add(_format_equation(new_a, new_k))
            
    options = [correct_eq] + list(distractors)
    random.shuffle(options)
    
    correct_answer_letter = chr(ord('A') + options.index(correct_eq))
    
    options_text = ""
    for i, opt in enumerate(options):
        letter = chr(ord('A') + i)
        options_text += f"({letter}) ${opt}$ <br>"

    question_text += f"<br>{options_text}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer_letter,
        "correct_answer": correct_answer_letter
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    # 標準化答案：去除空白、統一標點符號、轉為大寫
    user_ans_norm = user_answer.strip().upper()
    user_ans_norm = user_ans_norm.replace(' ', '').replace('　', '')
    user_ans_norm = user_ans_norm.replace('，', ',').replace('、', ',')
    user_ans_norm = user_ans_norm.replace('（', '(').replace('）', ')')

    corr_ans_norm = correct_answer.strip().upper()
    corr_ans_norm = corr_ans_norm.replace(' ', '').replace('　', '')
    corr_ans_norm = corr_ans_norm.replace('，', ',').replace('、', ',')
    corr_ans_norm = corr_ans_norm.replace('（', '(').replace('）', ')')

    is_correct = (user_ans_norm == corr_ans_norm)
    
    # 為了顯示，將頓號加回去
    if '、' in correct_answer:
        display_correct_answer = correct_answer.replace('、', '、 ')
    else:
        display_correct_answer = correct_answer

    if is_correct:
        result_text = f"完全正確！答案是 ${display_correct_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${display_correct_answer}$"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}