import random
from fractions import Fraction
import math

def format_equation_term(coeff, var, first_term=False):
    """
    Formats a single term for an equation (e.g., '3x', '-y', '+2x').
    Handles signs and '1x' vs 'x'.
    """
    if coeff == 0:
        return ""
    
    sign = ""
    if not first_term:
        sign = "+" if coeff > 0 else "-"
    elif coeff < 0:
        sign = "-"
        
    abs_coeff = abs(coeff)
        
    if abs_coeff == 1 and var != "": # For 'x', 'y' instead of '1x', '1y'
        return f"{sign}{var}"
    
    return f"{sign}{abs_coeff}{var}"

def generate(level=1):
    """
    生成「綜合練習題」相關題目。
    包含：
    1.  解二元一次聯立方程式
    2.  克拉瑪公式相關 (Delta_x 或 Delta_y 的值)
    3.  二階行列式計算
    4.  行列式性質應用 (純量乘法、行/列運算)
    5.  聯立方程式解的判斷 (唯一解、無解、無限多組解，含參數 k)
    6.  平行四邊形面積 (向量行列式應用)
    7.  文字應用題
    """
    problem_type = random.choice([
        'solve_system',
        'cramer_delta_value',
        'determinant_value_2x2',
        'determinant_property_scalar',
        'determinant_property_row_op',
        'system_solution_analysis_k',
        'geometric_area_parallelogram',
        'word_problem_age_or_weight'
    ])
    
    if problem_type == 'solve_system':
        return generate_solve_system()
    elif problem_type == 'cramer_delta_value':
        return generate_cramer_delta_value()
    elif problem_type == 'determinant_value_2x2':
        return generate_determinant_value_2x2()
    elif problem_type == 'determinant_property_scalar':
        return generate_determinant_property_scalar()
    elif problem_type == 'determinant_property_row_op':
        return generate_determinant_property_row_op()
    elif problem_type == 'system_solution_analysis_k':
        return generate_system_solution_analysis_k()
    elif problem_type == 'geometric_area_parallelogram':
        return generate_geometric_area_parallelogram()
    elif problem_type == 'word_problem_age_or_weight':
        return generate_word_problem_age_or_weight()
    
    # Fallback to a common type if something goes wrong (shouldn't happen with random.choice)
    return generate_solve_system()

def generate_solve_system():
    """
    生成解二元一次聯立方程式的題目。
    $a_1x + b_1y = c_1$
    $a_2x + b_2y = c_2$
    確保有唯一整數解。
    """
    x_sol = random.randint(-5, 5)
    y_sol = random.randint(-5, 5)

    # 避免解為 (0,0) 過於頻繁，或者係數過小導致平凡
    if x_sol == 0 and y_sol == 0:
        x_sol = random.choice([-1, 1])
        y_sol = random.choice([-1, 1])

    while True:
        a1 = random.randint(-3, 3)
        b1 = random.randint(-3, 3)
        a2 = random.randint(-3, 3)
        b2 = random.randint(-3, 3)

        # 避免行列式為零 (確保唯一解) 或係數皆為零 (無效方程式)
        if (a1 == 0 and b1 == 0) or (a2 == 0 and b2 == 0):
            continue
        det = a1 * b2 - a2 * b1
        if det != 0:
            break
            
    c1 = a1 * x_sol + b1 * y_sol
    c2 = a2 * x_sol + b2 * y_sol
    
    eq1_str = f"{format_equation_term(a1, 'x', first_term=True)}{format_equation_term(b1, 'y')}"
    eq2_str = f"{format_equation_term(a2, 'x', first_term=True)}{format_equation_term(b2, 'y')}"

    # 避免生成空白的方程式左側，在係數為0時 format_equation_term 返回空字串
    if not eq1_str: eq1_str = f"{b1}y" if b1 != 0 else f"{a1}x" # Should not happen with det!=0
    if not eq2_str: eq2_str = f"{b2}y" if b2 != 0 else f"{a2}x" # Should not happen with det!=0

    question_text = r"解下列聯立方程式：<br>" \
                    rf"$\begin{{cases}} {eq1_str} = {c1} \\ {eq2_str} = {c2} \end{{cases}}$"
    
    correct_answer = f"x={x_sol}, y={y_sol}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_cramer_delta_value():
    """
    生成克拉瑪公式中 $\\Delta_x$ 或 $\\Delta_y$ 值的題目。
    """
    a1, b1 = random.randint(-5, 5), random.randint(-5, 5)
    a2, b2 = random.randint(-5, 5), random.randint(-5, 5)
    c1, c2 = random.randint(-10, 10), random.randint(-10, 10)

    # 確保 Delta 不為零，克拉瑪公式才有唯一解適用
    while a1 * b2 - a2 * b1 == 0:
        a1, b1 = random.randint(-5, 5), random.randint(-5, 5)
        a2, b2 = random.randint(-5, 5), random.randint(-5, 5)
    
    delta_x = c1 * b2 - c2 * b1
    delta_y = a1 * c2 - a2 * c1
    
    target_delta = random.choice(['x', 'y'])
    
    eq1_str = f"{format_equation_term(a1, 'x', first_term=True)}{format_equation_term(b1, 'y')}"
    eq2_str = f"{format_equation_term(a2, 'x', first_term=True)}{format_equation_term(b2, 'y')}"

    if target_delta == 'x':
        question_text = r"考慮聯立方程式：<br>" \
                        rf"$\begin{{cases}} {eq1_str} = {c1} \\ {eq2_str} = {c2} \end{{cases}}$<br>" \
                        r"若使用克拉瑪公式，則 $\\Delta_x$ 的值為何？"
        correct_answer = str(delta_x)
    else: # target_delta == 'y'
        question_text = r"考慮聯立方程式：<br>" \
                        rf"$\begin{{cases}} {eq1_str} = {c1} \\ {eq2_str} = {c2} \end{{cases}}$<br>" \
                        r"若使用克拉瑪公式，則 $\\Delta_y$ 的值為何？"
        correct_answer = str(delta_y)
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_determinant_value_2x2():
    """
    生成計算二階行列式值的題目。
    """
    a = random.randint(-10, 10)
    b = random.randint(-10, 10)
    c = random.randint(-10, 10)
    d = random.randint(-10, 10)
    
    value = a * d - b * c
    
    question_text = r"求下列行列式的值：<br>" \
                    rf"$\begin{{vmatrix}} {a} & {b} \\ {c} & {d} \end{{vmatrix}}$"
    correct_answer = str(value)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_determinant_property_scalar():
    """
    生成應用行列式純量乘法性質的題目。
    """
    a = random.randint(-5, 5)
    b = random.randint(-5, 5)
    c = random.randint(-5, 5)
    d = random.randint(-5, 5)
    
    k = random.randint(2, 5) # 乘數 k
    
    det_val = a * d - b * c
    
    choice = random.choice(['row1', 'row2', 'col1', 'col2', 'all'])
    
    if choice == 'row1':
        question_text = rf"已知 $\begin{{vmatrix}} {a} & {b} \\ {c} & {d} \end{{vmatrix}} = {det_val}$，" \
                        rf"求 $\begin{{vmatrix}} {k*a} & {k*b} \\ {c} & {d} \end{{vmatrix}}$ 的值。"
        correct_answer = str(k * det_val)
    elif choice == 'row2':
        question_text = rf"已知 $\begin{{vmatrix}} {a} & {b} \\ {c} & {d} \end{{vmatrix}} = {det_val}$，" \
                        rf"求 $\begin{{vmatrix}} {a} & {b} \\ {k*c} & {k*d} \end{{vmatrix}}$ 的值。"
        correct_answer = str(k * det_val)
    elif choice == 'col1':
        question_text = rf"已知 $\begin{{vmatrix}} {a} & {b} \\ {c} & {d} \end{{vmatrix}} = {det_val}$，" \
                        rf"求 $\begin{{vmatrix}} {k*a} & {b} \\ {k*c} & {d} \end{{vmatrix}}$ 的值。"
        correct_answer = str(k * det_val)
    elif choice == 'col2':
        question_text = rf"已知 $\begin{{vmatrix}} {a} & {b} \\ {c} & {d} \end{{vmatrix}} = {det_val}$，" \
                        rf"求 $\begin{{vmatrix}} {a} & {k*b} \\ {c} & {k*d} \end{{vmatrix}}$ 的值。"
        correct_answer = str(k * det_val)
    else: # 'all' - 兩行/兩列都乘以 k，相當於 k^2 倍
        question_text = rf"已知 $\begin{{vmatrix}} {a} & {b} \\ {c} & {d} \end{{vmatrix}} = {det_val}$，" \
                        rf"求 $\begin{{vmatrix}} {k*a} & {k*b} \\ {k*c} & {k*d} \end{{vmatrix}}$ 的值。"
        correct_answer = str(k*k * det_val)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_determinant_property_row_op():
    """
    生成應用行列式行/列運算性質的題目 (某行/列加上另一行/列的 k 倍)。
    """
    a, b = random.randint(-5, 5), random.randint(-5, 5)
    c, d = random.randint(-5, 5), random.randint(-5, 5)
    k = random.randint(-3, 3)
    if k == 0: k = 1 # 避免 k=0 使運算無意義

    det_val = a * d - b * c

    choice = random.choice(['add_row', 'add_col'])

    if choice == 'add_row':
        target_row = random.choice([1, 2])
        if target_row == 1: # R1 -> R1 + k*R2
            question_text = rf"已知 $\begin{{vmatrix}} {a} & {b} \\ {c} & {d} \end{{vmatrix}} = {det_val}$，" \
                            rf"求 $\begin{{vmatrix}} {a+k*c} & {b+k*d} \\ {c} & {d} \end{{vmatrix}}$ 的值。"
        else: # R2 -> R2 + k*R1
            question_text = rf"已知 $\begin{{vmatrix}} {a} & {b} \\ {c} & {d} \end{{vmatrix}} = {det_val}$，" \
                            rf"求 $\begin{{vmatrix}} {a} & {b} \\ {c+k*a} & {d+k*b} \end{{vmatrix}}$ 的值。"
    else: # add_col
        target_col = random.choice([1, 2])
        if target_col == 1: # C1 -> C1 + k*C2
            question_text = rf"已知 $\begin{{vmatrix}} {a} & {b} \\ {c} & {d} \end{{vmatrix}} = {det_val}$，" \
                            rf"求 $\begin{{vmatrix}} {a+k*b} & {b} \\ {c+k*d} & {d} \end{{vmatrix}}$ 的值。"
        else: # C2 -> C2 + k*C1
            question_text = rf"已知 $\begin{{vmatrix}} {a} & {b} \\ {c} & {d} \end{{vmatrix}} = {det_val}$，" \
                            rf"求 $\begin{{vmatrix}} {a} & {b+k*a} \\ {c} & {d+k*c} \end{{vmatrix}}$ 的值。"
    
    correct_answer = str(det_val) # 這類行/列運算不改變行列式值
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_system_solution_analysis_k():
    """
    生成含參數 k 的聯立方程式解的判斷題目 (唯一解、無解、無限多組解)。
    """
    scenario = random.choice(['unique', 'no_solution', 'infinite_solutions'])
    
    if scenario == 'unique':
        # 構造一個行列式為 k^2 - N^2 的系統，使其在 k != +/-N 時有唯一解。
        N = random.randint(2, 4) # 決定 k 值的正負根
        q1_factor = random.choice([1, -1]) * random.randint(2, 5) # q1 不為0
        s1_factor = N * N // q1_factor 
        # 確保 s1_factor 是整數，且不為0
        while N*N % q1_factor != 0 or s1_factor == 0:
            q1_factor = random.choice([1, -1]) * random.randint(2, 5)
            s1_factor = N * N // q1_factor
        
        # 系統形式: kx + q1_factor*y = r1, s1_factor*x + ky = r2
        # 其係數行列式為 k*k - q1_factor*s1_factor = k^2 - N^2
        r1 = random.randint(-5, 5)
        r2 = random.randint(-5, 5)
        
        question_text = rf"已知聯立方程式 $\begin{{cases}} kx+{q1_factor}y={r1} \\ {s1_factor}x+ky={r2} \end{{cases}}$ 恰有一組解，求 $k$ 的範圍。"
        correct_answer = rf"$k \\neq {N}$ 且 $k \\neq {-N}$"
        
    else: # no_solution or infinite_solutions
        # 構造一個在特定 k0 值時，係數行列式為 0 的系統。
        # 系統形式: x + ky = C1, kx + k0^2y = C2
        # 在 k=k0 時，係數比為 1:k0, k0:k0^2 (即 k0 倍)，所以 Delta=0。
        # 此時根據 C1 與 C2 的關係判斷是無解還是無限多組解。
        k0 = random.randint(2, 4) * random.choice([-1, 1]) # 目標 k 值，不為 0
        
        C1_val = random.randint(3, 10) # 隨機常數
        
        if scenario == 'infinite_solutions':
            # 當 k=k0 時，第二式為第一式的 k0 倍，因此常數項也要是 k0 倍。
            C2_val = k0 * C1_val 
            question_text = rf"已知聯立方程式 $\begin{{cases}} x+ky={C1_val} \\ kx+{k0**2}y={C2_val} \end{{cases}}$ 有無限多組解，求 $k$ 的值。"
        else: # no_solution
            # 當 k=k0 時，第二式為第一式的 k0 倍，但常數項不為 k0 倍。
            # 確保 C2_val != k0 * C1_val
            offset = random.randint(1, 3) * random.choice([-1, 1])
            C2_val = k0 * C1_val + offset
            # 確保 offset 非零，且不因巧合讓 C2_val 再次等於 k0*C1_val (極不可能)
            while C2_val == k0 * C1_val: 
                offset = random.randint(1, 3) * random.choice([-1, 1])
                C2_val = k0 * C1_val + offset

            question_text = rf"已知聯立方程式 $\begin{{cases}} x+ky={C1_val} \\ kx+{k0**2}y={C2_val} \end{{cases}}$ 無解，求 $k$ 的值。"
            
        correct_answer = str(k0) # 這個 k0 是唯一的答案
            
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_geometric_area_parallelogram():
    """
    生成應用行列式計算平行四邊形面積的題目。
    已知向量 u, v 決定的面積，求 u, v 的線性組合向量決定的面積。
    """
    # 生成向量 u=(u1,u2), v=(v1,v2)
    u1, u2 = random.randint(-5, 5), random.randint(-5, 5)
    v1, v2 = random.randint(-5, 5), random.randint(-5, 5)

    # 確保初始向量不共線 (面積不為 0)
    while u1*v2 - u2*v1 == 0:
        u1, u2 = random.randint(-5, 5), random.randint(-5, 5)
        v1, v2 = random.randint(-5, 5), random.randint(-5, 5)
    
    # 構造新向量 w = p*u + q*v, z = r*u + s*v
    # 新平行四邊形面積 = |ps - rq| * 舊平行四邊形面積
    p = random.randint(1, 3)
    q = random.randint(-2, 2)
    r = random.randint(-2, 2)
    s = random.randint(1, 3)
    
    # 確保新向量決定的平行四邊形面積不為 0
    while p*s - r*q == 0:
        p = random.randint(1, 3)
        q = random.randint(-2, 2)
        r = random.randint(-2, 2)
        s = random.randint(1, 3)

    # 給定一個初始面積值
    given_area_val = random.randint(2, 10)
    
    # 格式化向量的線性組合表達式
    w_str_coeffs = []
    if p != 0: w_str_coeffs.append(f"{p}" + r"\vec{{u}}")
    if q != 0: w_str_coeffs.append(format_equation_term(q, r'\vec{{v}}'))
    w_str = "".join(w_str_coeffs).lstrip("+")
    if not w_str: w_str = r"0\vec{{u}}" # 避免空字串，理論上不會發生

    z_str_coeffs = []
    if r != 0: z_str_coeffs.append(f"{r}" + r"\vec{{u}}")
    if s != 0: z_str_coeffs.append(format_equation_term(s, r'\vec{{v}}'))
    z_str = "".join(z_str_coeffs).lstrip("+")
    if not z_str: z_str = r"0\vec{{u}}" # 避免空字串，理論上不會發生
    
    question_text = rf"已知由向量 $\vec{{u}}=({u1},{u2})$ 與 $\vec{{v}}=({v1},{v2})$ 所決定的平行四邊形面積為 ${given_area_val}$，" \
                    rf"求由向量 $\vec{{w}}={w_str}$ 與 $\vec{{z}}={z_str}$ 所決定的平行四邊形面積。"
    
    correct_answer = str(abs(p*s - r*q) * given_area_val)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_word_problem_age_or_weight():
    """
    生成經典的二元一次聯立方程式文字應用題 (例如年齡問題或重量問題)。
    """
    problem_choice = random.choice(['donkey_mule', 'father_son_age'])

    if problem_choice == 'donkey_mule':
        # 驢與騾背重物的問題，來自範例
        # 設驢重 D, 騾重 M
        # 驢說: D + T = mult1 * (M - T) => D - mult1*M = -(mult1+1)*T
        # 騾說: M + T = mult2 * (D - T) => -mult2*D + M = -(mult2+1)*T

        T = random.choice([50, 80, 100]) # 轉移的重量
        mult1 = random.choice([2, 3]) # 驢給騾 T 後，驢是騾的 mult1 倍
        mult2 = random.choice([2, 3]) # 騾給驢 T 後，騾是驢的 mult2 倍
        
        # 使用克拉瑪公式或代入消去法計算 D 和 M
        # D = T * (2*mult1 + 1 + mult1*mult2) / (mult1*mult2 - 1)
        # M = mult2*D - (mult2+1)*T
        
        # 確保結果為正整數
        try:
            donkey_weight_num = T * (2*mult1 + 1 + mult1*mult2)
            donkey_weight_den = (mult1*mult2 - 1)
            
            if donkey_weight_den == 0: # 避免除以零
                raise ValueError("Denominator is zero, regenerating.")
            
            donkey_weight = Fraction(donkey_weight_num, donkey_weight_den)
            mule_weight = Fraction(mult2 * donkey_weight - (mult2+1)*T)
            
            if not (donkey_weight > 0 and mule_weight > 0 and 
                    donkey_weight.denominator == 1 and mule_weight.denominator == 1):
                raise ValueError("Solutions are not positive integers, regenerating.")
        except ValueError:
            return generate_word_problem_age_or_weight() # 重新生成題目
        
        question_text = rf"驢與騾身上各背著重物，牠們互相埋怨，驢對騾說：「只要把你所背的重量給我 ${T}$ 公斤，" \
                        rf"我所背的重量就是你的 ${mult1}$ 倍。」騾回答說：「不錯，可是如果你背的重量給我 ${T}$ 公斤，" \
                        rf"我背的重量就是你的 ${mult2}$ 倍。」請問：驢與騾各背了多少公斤的重物？(請依序回答驢、騾的重量，以逗號分隔)"
        
        correct_answer = f"{int(donkey_weight)}, {int(mule_weight)}"
    
    else: # father_son_age
        # 父親和兒子的年齡問題
        # 設父親現在 F 歲，兒子現在 S 歲
        # F = X * S (現在父親是兒子的 X 倍)
        # F + Y = Z * (S + Y) (Y 年後父親是兒子的 Z 倍)
        
        # 確保生成整數解
        while True:
            son_age = random.randint(8, 15)
            father_age_mult_now = random.randint(3, 4) # 現在父親是兒子的 3 或 4 倍
            father_age_now = father_age_mult_now * son_age
            
            years_later = random.randint(3, 7)
            
            father_age_later = father_age_now + years_later
            son_age_later = son_age + years_later
            
            # 確保 Y 年後，父親年齡仍是兒子年齡的整數倍
            if (father_age_later % son_age_later == 0):
                father_age_mult_later = father_age_later // son_age_later
                if father_age_mult_later >= 2: # 確保父親依然比兒子大且倍數合理
                    break
        
        question_text = rf"父親現在的年齡是兒子的 ${father_age_mult_now}$ 倍。如果 ${years_later}$ 年後，" \
                        rf"父親的年齡會是兒子的 ${father_age_mult_later}$ 倍。請問父親和兒子現在的年齡各是多少？" \
                        r"(請依序回答父親、兒子的年齡，以逗號分隔)"
        
        correct_answer = f"{father_age_now}, {son_age}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    支援多種答案格式：
    - x=val, y=val (聯立方程式解)
    - k!=A 且 k!=B (k 的範圍)
    - k=val (k 的單一值)
    - val1, val2 (逗號分隔的數值，如文字題)
    - val (單一數值)
    """
    user_answer = user_answer.strip().lower().replace(' ', '')
    correct_answer = correct_answer.strip().lower().replace(' ', '')

    is_correct = False
    feedback = ""

    # 處理聯立方程式解 (x=..., y=...)
    if 'x=' in correct_answer and 'y=' in correct_answer:
        parts_correct = correct_answer.split(',')
        x_correct_str = parts_correct[0].split('=')[1]
        y_correct_str = parts_correct[1].split('=')[1]
        
        try:
            x_correct = Fraction(x_correct_str)
            y_correct = Fraction(y_correct_str)
        except ValueError:
            feedback = "內部錯誤：無法解析正確答案的數值。"
            return {"correct": False, "result": feedback, "next_question": False}

        user_x_val = None
        user_y_val = None
        
        user_parts = user_answer.split(',')
        for part in user_parts:
            if part.startswith('x='):
                try: user_x_val = Fraction(part.split('=')[1])
                except ValueError: pass
            elif part.startswith('y='):
                try: user_y_val = Fraction(part.split('=')[1])
                except ValueError: pass
        
        if user_x_val is not None and user_y_val is not None:
            if user_x_val == x_correct and user_y_val == y_correct:
                is_correct = True
                feedback = rf"完全正確！答案是 $x={x_correct}, y={y_correct}$。"
            else:
                feedback = rf"答案不正確。正確答案應為 $x={x_correct}, y={y_correct}$。"
        else:
            feedback = rf"答案格式不符，請以 $x=..., y=...$ 的形式回答。正確答案應為 $x={x_correct}, y={y_correct}$。"

    # 處理 k 範圍 (k != A 且 k != B)
    elif 'k!=' in correct_answer and '且' in correct_answer:
        # 正確答案格式: "k!=3 且 k!=-3" (順序可能不同)
        correct_parts = [p.strip() for p in correct_answer.replace('k!=', '').split('且')]
        user_parts = [p.strip() for p in user_answer.replace('k!=', '').split('且')]

        try:
            correct_nums = sorted([Fraction(p) for p in correct_parts])
            user_nums = sorted([Fraction(p) for p in user_parts])
            if correct_nums == user_nums:
                is_correct = True
                feedback = r"完全正確！答案是 $" + correct_answer.replace('k!=', 'k \\neq ') + r"$"
            else:
                feedback = r"答案不正確。正確答案應為 $" + correct_answer.replace('k!=', 'k \\neq ') + r"$"
        except (ValueError, IndexError):
            feedback = r"答案格式不符，請以 $k \\neq A$ 且 $k \\neq B$ 的形式回答。正確答案應為 $" + correct_answer.replace('k!=', 'k \\neq ') + r"$"

    # 處理 k 單一值 (k=...)
    elif correct_answer.startswith('k='):
        correct_k_str = correct_answer.split('=')[1]
        try:
            correct_k = Fraction(correct_k_str)
            user_k_input = user_answer.split('=')[1] if user_answer.startswith('k=') else user_answer
            user_k = Fraction(user_k_input)
            
            if user_k == correct_k:
                is_correct = True
                feedback = rf"完全正確！答案是 $k={correct_k}$。"
            else:
                feedback = rf"答案不正確。正確答案應為 $k={correct_k}$。"
        except (ValueError, IndexError):
            feedback = rf"答案格式不符，請以 $k=...$ 的形式回答，或直接輸入數值。正確答案應為 $k={correct_k_str}$。"

    # 處理逗號分隔的數值答案 (如文字題)
    elif ',' in correct_answer:
        correct_values = [Fraction(v.strip()) for v in correct_answer.split(',')]
        user_values = []
        try:
            user_values = [Fraction(v.strip()) for v in user_answer.split(',')]
        except ValueError:
            feedback = r"答案格式不符，請以逗號分隔數值。正確答案應為：" + ', '.join(map(str, correct_values))
            return {"correct": False, "result": feedback, "next_question": True}
        
        if len(user_values) == len(correct_values) and all(u == c for u, c in zip(user_values, correct_values)):
            is_correct = True
            feedback = r"完全正確！答案是 " + ', '.join(map(str, correct_values)) + r"。"
        else:
            feedback = r"答案不正確。正確答案應為：" + ', '.join(map(str, correct_values))
    
    # 處理單一數值答案
    else:
        try:
            user_val = Fraction(user_answer)
            correct_val = Fraction(correct_answer)
            
            if user_val == correct_val:
                is_correct = True
                feedback = rf"完全正確！答案是 ${correct_val}$。"
            else:
                feedback = rf"答案不正確。正確答案應為 ${correct_val}$。"
        except ValueError:
            # 如果不是數值，則進行字串比較
            if user_answer == correct_answer:
                is_correct = True
                feedback = rf"完全正確！答案是 {correct_answer}。"
            else:
                feedback = rf"答案不正確。正確答案應為 {correct_answer}。"
    
    return {"correct": is_correct, "result": feedback, "next_question": True}