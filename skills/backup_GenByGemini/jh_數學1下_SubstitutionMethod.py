import random
import re

def generate(level=1):
    """
    生成「代入消去法」相關題目 (標準 LaTeX 範本)。
    包含：
    1. 一式已整理為 y=mx+k 或 x=my+k 的顯式題型。
    2. 兩式均為 ax+by=c 的標準式，需先移項的隱式題型。
    """
    return generate_substitution_problem()

def generate_substitution_problem():
    """
    生成一個二元一次聯立方程式，適合使用代入消去法解題。
    """
    
    # 步驟 1：決定整數解
    while True:
        x_sol = random.randint(-9, 9)
        y_sol = random.randint(-9, 9)
        # 避免解為 0，讓題目稍微複雜一點
        if x_sol != 0 and y_sol != 0 and abs(x_sol) != abs(y_sol):
            break

    # 步驟 2：決定題型 (顯式或隱式)
    problem_type = random.choice(['explicit', 'implicit'])

    if problem_type == 'explicit':
        # --- 生成顯式題型 (e.g., y = 3x + 5) ---
        isolated_var = random.choice(['x', 'y'])
        
        # 係數 m 不為 0, 1, -1，避免過於簡單
        m = random.choice([-4, -3, -2, 2, 3, 4])
        
        if isolated_var == 'x':
            # 形式: x = my + k
            k = x_sol - m * y_sol
            
            # 格式化第一條方程式 (x = ...)
            m_str = f"{m}y" if m not in [1, -1] else ("y" if m == 1 else "-y")
            if k == 0:
                eq1_str = f"x = {m_str}"
            else:
                op_str = "+" if k > 0 else "-"
                eq1_str = f"x = {m_str} {op_str} {abs(k)}"
            
            # 隨機生成第二條標準式方程式: a*x + b*y = c
            while True:
                a2 = random.randint(-5, 5)
                b2 = random.randint(-5, 5)
                if a2 != 0 and b2 != 0: break
            c2 = a2 * x_sol + b2 * y_sol
            eq2_str = build_eq_str(a2, b2, c2)

        else: # isolated_var == 'y'
            # 形式: y = mx + k
            k = y_sol - m * x_sol
            
            # 格式化第一條方程式 (y = ...)
            m_str = f"{m}x" if m not in [1, -1] else ("x" if m == 1 else "-x")
            if k == 0:
                eq1_str = f"y = {m_str}"
            else:
                op_str = "+" if k > 0 else "-"
                eq1_str = f"y = {m_str} {op_str} {abs(k)}"
                
            # 隨機生成第二條標準式方程式: a*x + b*y = c
            while True:
                a2 = random.randint(-5, 5)
                b2 = random.randint(-5, 5)
                if a2 != 0 and b2 != 0: break
            c2 = a2 * x_sol + b2 * y_sol
            eq2_str = build_eq_str(a2, b2, c2)

    else: # problem_type == 'implicit'
        # --- 生成隱式題型 (ax+by=c) ---
        # 其中一條方程式的 x 或 y 係數會是 1 或 -1，方便使用者移項
        
        # 生成第一條方程式
        if random.random() < 0.5: # x 的係數為 +/- 1
            a1 = random.choice([1, -1])
            b1 = random.randint(-5, 5)
            while b1 == 0: b1 = random.randint(-5, 5)
        else: # y 的係數為 +/- 1
            b1 = random.choice([1, -1])
            a1 = random.randint(-5, 5)
            while a1 == 0: a1 = random.randint(-5, 5)
        
        c1 = a1 * x_sol + b1 * y_sol
        eq1_str = build_eq_str(a1, b1, c1)
        
        # 生成第二條方程式
        while True:
            a2 = random.randint(-5, 5)
            b2 = random.randint(-5, 5)
            # 確保係數不為零且不成比例
            if a2 != 0 and b2 != 0 and (a1 * b2 != a2 * b1):
                break
        c2 = a2 * x_sol + b2 * y_sol
        eq2_str = build_eq_str(a2, b2, c2)

    # [關鍵修正] 使用正確的 LaTeX 跳脫字元
    # \\begin -> \begin
    # \\\\ -> \\ (換行)
    # \\end -> \end
    latex_system = f"$\\begin{{cases}} {eq1_str} \\\\ {eq2_str} \\end{{cases}}$"
    
    question_text = f"利用代入消去法，解二元一次聯立方程式：<br>{latex_system}"

    # 答案格式
    correct_answer = f"x={x_sol}, y={y_sol}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def build_eq_str(a, b, c):
    """一個輔助函式，用來將係數 (a, b, c) 轉換為 'ax + by = c' 的字串格式"""
    parts = []
    # 處理 x 項
    if a == 1: parts.append("x")
    elif a == -1: parts.append("-x")
    elif a != 0: parts.append(f"{a}x")
    
    # 處理 y 項
    if b != 0:
        sign = "+" if b > 0 else "-"
        val = abs(b)
        # 如果 x 項存在，則必須顯示符號
        if parts:
            if val == 1: parts.append(f"{sign} y")
            else: parts.append(f"{sign} {val}y")
        # 如果 x 項不存在，則只有負號時顯示
        else:
            if val == 1: parts.append(f"{'y' if sign == '+' else '-y'}")
            else: parts.append(f"{b}y")
            
    return f"{' '.join(parts)} = {c}"

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    def parse_answer(answer_str):
        try:
            answer_str = answer_str.lower().replace(" ", "")
            matches = re.findall(r'([xy])=([-\d.]+)', answer_str)
            
            if len(matches) != 2: return None
            
            result = {var: float(val) for var, val in matches}
            if 'x' not in result or 'y' not in result: return None
                
            return result
        except:
            return None

    user_dict = parse_answer(user_answer)
    correct_dict = parse_answer(correct_answer)
    
    is_correct = False
    if user_dict and correct_dict:
        if abs(user_dict['x'] - correct_dict['x']) < 1e-9 and \
           abs(user_dict['y'] - correct_dict['y']) < 1e-9:
            is_correct = True
    
    pretty_answer = correct_answer.replace(',', ', ')
    result_text = f"完全正確！答案是 ${pretty_answer}$。" if is_correct else f"答案不正確。正確答案應為：${pretty_answer}$"
    
    return {"correct": is_correct, "result": result_text, "next_question": True}