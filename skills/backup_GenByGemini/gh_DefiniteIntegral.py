import random
from fractions import Fraction
import math

def generate(level=1):
    """
    生成關於定積分基本概念、性質的題目。
    包含：
    1. 定積分的定義（淨有向面積，非單純面積）
    2. 定積分值的正負判斷 (對於簡單函數)
    3. 定積分的區間可加性
    4. 定積分與黎曼和的關係 (極限概念)
    """
    problem_type_choices = []

    if level == 1:
        problem_type_choices = ['concept_net_signed_area', 'sign_prediction_simple', 'riemann_limit_concept']
    elif level == 2:
        problem_type_choices = ['concept_net_signed_area', 'sign_prediction_linear', 'property_additivity', 'riemann_limit_concept']
    else: # Default to level 1 for any unexpected level value
        problem_type_choices = ['concept_net_signed_area', 'sign_prediction_simple', 'riemann_limit_concept']

    problem_type = random.choice(problem_type_choices)

    if problem_type == 'concept_net_signed_area':
        return generate_concept_net_signed_area_problem()
    elif problem_type == 'sign_prediction_simple':
        return generate_sign_prediction_simple_problem()
    elif problem_type == 'sign_prediction_linear':
        return generate_sign_prediction_linear_problem()
    elif problem_type == 'property_additivity':
        return generate_property_additivity_problem()
    else: # riemann_limit_concept
        return generate_riemann_limit_concept_problem()

def generate_concept_net_signed_area_problem():
    """
    生成關於定積分意義的題目，強調「淨有向面積」或其超越「面積」的特性。
    """
    question_type = random.choice(['definition_direct', 'true_false_area_only'])

    if question_type == 'definition_direct':
        question_text = r"對於一個在區間 $[a,b]$ 上連續的函數 $f(x)$，定積分 $\\int_{{a}}^{{b}} f(x) \, dx$ 的意義是？" \
                        r"<br>(請回答兩個字或三個字，例如：面積、淨有向面積、累積量)"
        correct_answer = "淨有向面積"
    else: # true_false_area_only
        question_text = r"判斷以下敘述是否正確：<br>「定積分 $\\int_{{a}}^{{b}} f(x) \, dx$ 總是代表函數 $f(x)$ 與 $x$ 軸所圍成的『面積』。」" \
                        r"<br>(請回答『是』或『否』)"
        correct_answer = "否"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_sign_prediction_simple_problem():
    """
    生成關於定積分正負判斷的題目，使用簡單的常數函數 $f(x) = C$。
    """
    constant_val = random.choice([-5, -3, -1, 0, 1, 2, 4]) # Include 0 for "零" case
    
    # Generate interval [a, b] such that a < b
    a = random.randint(-5, 2)
    b = random.randint(a + 1, 7) # Ensure b > a

    question_text = fr"對於函數 $f(x) = {constant_val}$，在區間 $[{a},{b}]$ 上的定積分 $\\int_{{{a}}}^{{{b}}} {constant_val} \, dx$ 會是正數、負數還是零？"
    
    if constant_val > 0:
        correct_answer = "正數"
    elif constant_val < 0:
        correct_answer = "負數"
    else: # constant_val == 0
        correct_answer = "零"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_sign_prediction_linear_problem():
    """
    生成關於定積分正負判斷的題目，使用簡單的線性函數 $f(x) = x$ 或 $f(x) = -x$。
    """
    func_type = random.choice(['x', 'neg_x'])
    
    # Generate interval [a, b] such that a < b
    a_val = random.randint(-4, 2)
    b_val = random.randint(a_val + 1, 6) 
    
    if func_type == 'x':
        f_x_str = "x"
        if b_val <= 0: # e.g., [-3, -1], integral is negative
            correct_answer = "負數"
        elif a_val >= 0: # e.g., [1, 3], integral is positive
            correct_answer = "正數"
        else: # a_val < 0 < b_val, depends on symmetry
            if abs(a_val) < b_val: # e.g., [-2, 3], positive area (right side) is larger
                correct_answer = "正數"
            elif abs(a_val) > b_val: # e.g., [-3, 2], negative area (left side) is larger
                correct_answer = "負數"
            else: # abs(a_val) == b_val, e.g., [-2, 2], symmetric around 0
                correct_answer = "零"
    else: # func_type == 'neg_x' (f(x) = -x)
        f_x_str = "-x"
        if b_val <= 0: # e.g., [-3, -1], integral is positive
            correct_answer = "正數"
        elif a_val >= 0: # e.g., [1, 3], integral is negative
            correct_answer = "負數"
        else: # a_val < 0 < b_val
            if abs(a_val) < b_val: # e.g., [-2, 3], negative area (right side) is larger
                correct_answer = "負數"
            elif abs(a_val) > b_val: # e.g., [-3, 2], positive area (left side) is larger
                correct_answer = "正數"
            else: # abs(a_val) == b_val, e.g., [-2, 2], symmetric around 0
                correct_answer = "零"

    question_text = fr"對於函數 $f(x) = {f_x_str}$，在區間 $[{a_val},{b_val}]$ 上的定積分 $\\int_{{{a_val}}}^{{{b_val}}} {f_x_str} \, dx$ 會是正數、負數還是零？"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_property_additivity_problem():
    """
    生成關於定積分區間可加性 ($\\int_a^c f(x) dx = \\int_a^b f(x) dx + \\int_b^c f(x) dx$) 的題目。
    """
    # Generate three distinct ordered points a, b, c
    points = sorted(random.sample(range(-10, 10), 3))
    a, b, c = points[0], points[1], points[2]

    # Generate values for K1 and K2
    k1 = random.randint(-10, 10)
    k2 = random.randint(-10, 10)
    
    question_text = fr"已知 $\\int_{{{a}}}^{{{b}}} f(x) \, dx = {k1}$ 且 $\\int_{{{b}}}^{{{c}}} f(x) \, dx = {k2}$，" \
                    fr"請問 $\\int_{{{a}}}^{{{c}}} f(x) \, dx$ 的值為何？"
    
    correct_answer = str(k1 + k2)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_riemann_limit_concept_problem():
    """
    生成關於定積分作為黎曼和極限的題目。
    """
    keyword_options = [
        ("當區間分割數 $n$ 趨近於 ______ 時的極限。", "無限大"),
        ("定積分被定義為當黎曼和的子區間數量 $n$ 趨於 ______ 時的極限。", "無窮大"),
        ("定積分 $\\int_{{a}}^{{b}} f(x) \, dx$ 是黎曼和在子區間寬度 $\\Delta x$ 趨近於 ______ 時的極限。", "零")
    ]
    
    question_template, correct_answer_template = random.choice(keyword_options)
    
    question_text = fr"定積分是將黎曼和{question_template}"
    correct_answer = correct_answer_template
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip().lower()
    correct_answer = correct_answer.strip().lower()
    
    is_correct = False
    feedback_message = ""

    # Specific checks for common string answers
    if correct_answer in ["正數", "負數", "零", "是", "否", "無限大", "無窮大", "淨有向面積"]:
        if user_answer == correct_answer:
            is_correct = True
            feedback_message = f"完全正確！答案是「{correct_answer}」。"
        else:
            is_correct = False
            feedback_message = f"答案不正確。正確答案應為：「{correct_answer}」。"
    else: # Numerical answers (e.g., from property_additivity)
        try:
            user_num = float(user_answer)
            correct_num = float(correct_answer)
            if abs(user_num - correct_num) < 1e-9: # Compare floats with tolerance
                is_correct = True
                feedback_message = f"完全正確！答案是 ${correct_answer}$。"
            else:
                is_correct = False
                feedback_message = f"答案不正確。正確答案應為：${correct_answer}$。"
        except ValueError:
            is_correct = False
            feedback_message = f"答案格式不正確或內容有誤。正確答案應為：${correct_answer}$。"

    return {"correct": is_correct, "result": feedback_message, "next_question": True}