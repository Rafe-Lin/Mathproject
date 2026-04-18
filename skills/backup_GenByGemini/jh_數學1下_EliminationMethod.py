import random

def _format_term(coeff, var, is_first_term=False):
    """
    Formats a single term (e.g., '2x', '-y', '+ 5z') for an equation string.
    Handles signs, and coefficients of 1 and -1.
    """
    if coeff == 0:
        return ""
    
    # Determine the sign part
    if is_first_term:
        sign = "-" if coeff < 0 else ""
    else:
        sign = " - " if coeff < 0 else " + "
        
    # Determine the coefficient part
    abs_coeff = abs(coeff)
    coeff_str = str(abs_coeff) if abs_coeff != 1 else ""
    
    return f"{sign}{coeff_str}{var}"

def _generate_equation_str(a, b, c):
    """
    Generates a formatted string for the equation ax + by = c.
    """
    x_term = _format_term(a, 'x', is_first_term=True)
    y_term = _format_term(b, 'y')
    
    # If x's coefficient is zero, y becomes the first term
    if a == 0:
        y_term = _format_term(b, 'y', is_first_term=True)

    # If y's coefficient is zero, there is no space between x_term and '='
    if b == 0:
        return f"{x_term} = {c}"

    return f"{x_term}{y_term} = {c}"

def generate(level=1):
    """
    生成「加減消去法」解二元一次聯立方程式的相關題目。
    包含：
    1. 直接相加/減即可消去一元
    2. 將其中一式乘以一個倍數後可消去一元
    3. 需將兩式各乘以不同倍數後方可消去一元
    """
    # 根據難易度可以調整題型比例，此處隨機選擇
    problem_type = random.choice(['direct', 'one_step', 'two_step'])
    
    if problem_type == 'direct':
        return _generate_direct_elimination_problem()
    elif problem_type == 'one_step':
        return _generate_one_step_multiplication_problem()
    else:
        return _generate_two_step_multiplication_problem()

def _generate_direct_elimination_problem():
    """題型1: 觀察後可直接加減消去"""
    x_sol = random.choice([i for i in range(-5, 6) if i != 0])
    y_sol = random.choice([i for i in range(-5, 6) if i != 0])
    
    a = random.choice([i for i in range(-5, 6) if i != 0])
    b = random.choice([i for i in range(-5, 6) if i != 0])
    
    # 隨機決定要消去 x 還是 y
    if random.random() < 0.5: # 消去 y，令 y 係數互為相反數
        e = -b
        d = random.choice([i for i in range(-5, 6) if i != 0 and abs(i) != abs(a)])
    else: # 消去 x，令 x 係數互為相反數
        d = -a
        e = random.choice([i for i in range(-5, 6) if i != 0 and abs(i) != abs(b)])
        
    c = a * x_sol + b * y_sol
    f = d * x_sol + e * y_sol
    
    eq1_str = _generate_equation_str(a, b, c)
    eq2_str = _generate_equation_str(d, e, f)
    
    if random.random() < 0.5:
        eq1_str, eq2_str = eq2_str, eq1_str
    
    question_text = f"解二元一次聯立方程式：<br>$\\begin{{cases}} {eq1_str} \\\\ {eq2_str} \\end{{cases}}$"
    correct_answer = f"x={x_sol},y={y_sol}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def _generate_one_step_multiplication_problem():
    """題型2: 其中一式需乘以一個倍數"""
    x_sol = random.choice([i for i in range(-5, 6) if i != 0])
    y_sol = random.choice([i for i in range(-5, 6) if i != 0])
    k = random.choice([-3, -2, 2, 3])
    
    # 生成較簡單的式子
    d = random.choice([i for i in range(-4, 5) if i != 0])
    e = random.choice([i for i in range(-4, 5) if i != 0])
    f = d * x_sol + e * y_sol
    
    # 生成需要乘法的那條式子
    if random.random() < 0.5: # 讓 x 係數成倍數
        a = d * k
        b = random.choice([i for i in range(-7, 8) if i != 0 and (abs(e) == 1 or i % e != 0)])
    else: # 讓 y 係數成倍數
        b = e * k
        a = random.choice([i for i in range(-7, 8) if i != 0 and (abs(d) == 1 or i % d != 0)])
        
    c = a * x_sol + b * y_sol
    
    eq1_str = _generate_equation_str(a, b, c)
    eq2_str = _generate_equation_str(d, e, f)
    
    if random.random() < 0.5:
        eq1_str, eq2_str = eq2_str, eq1_str

    question_text = f"解二元一次聯立方程式：<br>$\\begin{{cases}} {eq1_str} \\\\ {eq2_str} \\end{{cases}}$"
    correct_answer = f"x={x_sol},y={y_sol}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def _generate_two_step_multiplication_problem():
    """題型3: 兩式皆須乘以倍數"""
    x_sol = random.choice([i for i in range(-4, 5) if i != 0])
    y_sol = random.choice([i for i in range(-4, 5) if i != 0])
    
    coprime_pairs = [(2, 3), (2, 5), (3, 4), (3, 5)]
    
    # 隨機決定要消去 x 或 y，並為其設定互質係數
    if random.random() < 0.5:
        pair1 = random.choice(coprime_pairs)
        pair2 = random.sample([i for i in range(-5, 6) if i != 0], 2)
        a, d = pair1[0], pair1[1]
        b, e = pair2[0], pair2[1]
    else:
        pair1 = random.choice(coprime_pairs)
        pair2 = random.sample([i for i in range(-5, 6) if i != 0], 2)
        b, e = pair1[0], pair1[1]
        a, d = pair2[0], pair2[1]

    # 隨機增添負號增加變化
    if random.random() < 0.5: a *= -1
    if random.random() < 0.5: b *= -1
    if random.random() < 0.5: d *= -1
    if random.random() < 0.5: e *= -1

    # 避免意外產生更簡單的題型或無解/無限多解
    if abs(a) == abs(d) or abs(b) == abs(e) or (a*e == b*d):
        return _generate_two_step_multiplication_problem() # 重新生成

    c = a * x_sol + b * y_sol
    f = d * x_sol + e * y_sol
    
    eq1_str = _generate_equation_str(a, b, c)
    eq2_str = _generate_equation_str(d, e, f)
    
    question_text = f"解二元一次聯立方程式：<br>$\\begin{{cases}} {eq1_str} \\\\ {eq2_str} \\end{{cases}}$"
    correct_answer = f"x={x_sol},y={y_sol}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。能容忍空格、大小寫、x與y順序顛倒。
    """
    def parse_answer(ans_str):
        try:
            ans_str = ans_str.replace(" ", "").lower()
            parts = ans_str.split(',')
            if len(parts) != 2: return None
            
            ans_dict = {}
            for part in parts:
                var, val = part.split('=')
                ans_dict[var] = int(val)
            
            if 'x' in ans_dict and 'y' in ans_dict:
                return ans_dict
            return None
        except (ValueError, IndexError):
            return None

    user_dict = parse_answer(user_answer)
    correct_dict = parse_answer(correct_answer)
    
    is_correct = (user_dict is not None and correct_dict is not None and user_dict == correct_dict)
    
    latex_answer = f"x = {correct_dict['x']}, y = {correct_dict['y']}"
    
    if is_correct:
        result_text = f"完全正確！答案是 ${latex_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${latex_answer}$"
    
    return {"correct": is_correct, "result": result_text, "next_question": True}
