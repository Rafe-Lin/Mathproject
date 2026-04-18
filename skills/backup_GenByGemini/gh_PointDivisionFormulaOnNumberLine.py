import random
from fractions import Fraction

def generate(level=1):
    """
    生成「數線上分點公式」相關題目。
    包含：
    1. 內分點坐標
    2. 外分點坐標
    3. 中點坐標 (內分點特例)
    4. 已知分點和其中一點，求另一個端點坐標
    5. 解析分點公式表達式，判斷比值或類型
    6. 比較多個分點的坐標大小
    """
    problem_type_choices = [
        'internal_division',
        'external_division',
        'midpoint_formula',
        'find_endpoint_internal',
        'find_endpoint_external',
        'interpret_formula',
        'compare_division_points'
    ]
    
    # 根據 level 調整題型難度
    if level == 1:
        problem_type_choices = ['internal_division', 'midpoint_formula', 'interpret_formula']
    elif level == 2:
        problem_type_choices = ['internal_division', 'external_division', 'midpoint_formula', 'find_endpoint_internal']
    # level 3 and above includes all types

    problem_type = random.choice(problem_type_choices)

    if problem_type == 'internal_division':
        return generate_internal_division_problem(level)
    elif problem_type == 'external_division':
        return generate_external_division_problem(level)
    elif problem_type == 'midpoint_formula':
        return generate_midpoint_formula_problem(level)
    elif problem_type == 'find_endpoint_internal':
        return generate_find_endpoint_internal_problem(level)
    elif problem_type == 'find_endpoint_external':
        return generate_find_endpoint_external_problem(level)
    elif problem_type == 'interpret_formula':
        return generate_interpret_formula_problem(level)
    elif problem_type == 'compare_division_points':
        return generate_compare_division_points_problem(level)
    # Default fallback, should not be reached with proper problem_type_choices
    return generate_internal_division_problem(level)

def generate_internal_division_problem(level):
    """
    生成內分點坐標的題目。
    題目: 數線上兩點 A(x1), B(x2)，點 P 在 AB 上，且 AP:PB=m:n，求 P 點坐標。
    公式: P = (n*x1 + m*x2) / (m+n)
    """
    x1 = random.randint(-20, 20)
    x2 = random.randint(-20, 20)
    while x1 == x2: # 確保兩點不同
        x2 = random.randint(-20, 20)

    # 確保 x1 < x2 以便描述，但公式不受影響
    if x1 > x2:
        x1, x2 = x2, x1

    m = random.randint(1, 5 + level)
    n = random.randint(1, 5 + level)

    # 計算 P 點坐標
    numerator = n * x1 + m * x2
    denominator = m + n
    p_coord = Fraction(numerator, denominator)

    question_text = f"數線上兩點 $A({x1})$、$B({x2})$，點 $P$ 在 $\\overline{{AB}}$ 上，且 $\\overline{{AP}}:\\overline{{PB}} = {m}:{n}$，求 $P$ 點的坐標。"
    correct_answer = str(p_coord)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_external_division_problem(level):
    """
    生成外分點坐標的題目。
    題目: 數線上兩點 A(x1), B(x2)，點 Q 在 AB 外，且 AQ:BQ=m:n，求 Q 點坐標。
    公式: Q = (m*x2 - n*x1) / (m-n) (假設 AQ:BQ=m:n)
    """
    x1 = random.randint(-20, 20)
    x2 = random.randint(-20, 20)
    while x1 == x2: # 確保兩點不同
        x2 = random.randint(-20, 20)

    m = random.randint(1, 5 + level)
    n = random.randint(1, 5 + level)
    while m == n: # 外分點要求 m != n
        n = random.randint(1, 5 + level)

    # 計算 Q 點坐標 (Q divides AB externally in ratio m:n)
    # 根據 (x_Q - x1) / (x_Q - x2) = m/n 推導
    # => n(x_Q - x1) = m(x_Q - x2)
    # => n*x_Q - n*x1 = m*x_Q - m*x2
    # => m*x2 - n*x1 = (m-n)*x_Q
    # => x_Q = (m*x2 - n*x1) / (m-n)
    numerator = m * x2 - n * x1
    denominator = m - n
    q_coord = Fraction(numerator, denominator)

    question_text = f"數線上兩點 $A({x1})$、$B({x2})$，點 $Q$ 在 $\\overline{{AB}}$ 外，且 $\\overline{{AQ}}:\\overline{{BQ}} = {m}:{n}$，求 $Q$ 點的坐標。"
    correct_answer = str(q_coord)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_midpoint_formula_problem(level):
    """
    生成中點坐標的題目 (作為分點公式的特例)。
    題目: 數線上兩點 A(x1), B(x2)，求 AB 的中點 M 的坐標。
    公式: M = (x1 + x2) / 2
    """
    x1 = random.randint(-20, 20)
    x2 = random.randint(-20, 20)
    while x1 == x2: # 確保兩點不同
        x2 = random.randint(-20, 20)

    midpoint_coord = Fraction(x1 + x2, 2)

    question_text = f"數線上兩點 $A({x1})$、$B({x2})$，求 $\\overline{{AB}}$ 的中點 $M$ 的坐標。"
    correct_answer = str(midpoint_coord)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_find_endpoint_internal_problem(level):
    """
    生成已知內分點和其中一個端點，求另一個端點的題目。
    已知 P 點坐標、A 點坐標、AP:PB=m:n，求 B 點坐標。
    公式: x2 = ((m+n)*xp - n*x1) / m
    """
    x1 = random.randint(-20, 20)
    m = random.randint(1, 5 + level)
    n = random.randint(1, 5 + level)
    
    # 先隨機生成一個 x2_temp，計算出 xp，然後再將 x2_temp 作為未知數
    x2_temp = random.randint(-20, 20)
    while x1 == x2_temp:
        x2_temp = random.randint(-20, 20)
    
    xp = Fraction(n * x1 + m * x2_temp, m + n)

    # 隨機決定是要求 B 點還是 A 點
    find_B = random.choice([True, False])

    if find_B:
        # A(x1), P(xp), AP:PB = m:n. 求 B(x2).
        # xp = (n*x1 + m*x2) / (m+n) => (m+n)*xp = n*x1 + m*x2
        # => m*x2 = (m+n)*xp - n*x1 => x2 = ((m+n)*xp - n*x1) / m
        x2_actual = Fraction((m + n) * xp - n * x1, m)
        question_text = f"數線上點 $A({x1})$、點 $P({xp})$ 在 $\\overline{{AB}}$ 上，且 $\\overline{{AP}}:\\overline{{PB}} = {m}:{n}$，求 $B$ 點的坐標。"
        correct_answer = str(x2_actual)
    else:
        # B(x2_temp), P(xp), AP:PB = m:n. 求 A(x1).
        # xp = (n*x1 + m*x2) / (m+n) => (m+n)*xp = n*x1 + m*x2
        # => n*x1 = (m+n)*xp - m*x2 => x1 = ((m+n)*xp - m*x2) / n
        x1_actual = Fraction((m + n) * xp - m * x2_temp, n)
        question_text = f"數線上點 $B({x2_temp})$、點 $P({xp})$ 在 $\\overline{{AB}}$ 上，且 $\\overline{{AP}}:\\overline{{PB}} = {m}:{n}$，求 $A$ 點的坐標。"
        correct_answer = str(x1_actual)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_find_endpoint_external_problem(level):
    """
    生成已知外分點和其中一個端點，求另一個端點的題目。
    已知 Q 點坐標、A 點坐標、AQ:BQ=m:n，求 B 點坐標。
    公式: x2 = ((m-n)*xq + n*x1) / m (假設 AQ:BQ=m:n)
    """
    x1 = random.randint(-20, 20)
    m = random.randint(1, 5 + level)
    n = random.randint(1, 5 + level)
    while m == n: # 外分點要求 m != n
        n = random.randint(1, 5 + level)
    
    # 先隨機生成一個 x2_temp，計算出 xq，然後再將 x2_temp 作為未知數
    x2_temp = random.randint(-20, 20)
    while x1 == x2_temp:
        x2_temp = random.randint(-20, 20)
    
    xq = Fraction(m * x2_temp - n * x1, m - n)

    # 隨機決定是要求 B 點還是 A 點
    find_B = random.choice([True, False])

    if find_B:
        # A(x1), Q(xq), AQ:BQ = m:n. 求 B(x2).
        # xq = (m*x2 - n*x1) / (m-n) => (m-n)*xq = m*x2 - n*x1
        # => m*x2 = (m-n)*xq + n*x1 => x2 = ((m-n)*xq + n*x1) / m
        x2_actual = Fraction((m - n) * xq + n * x1, m)
        question_text = f"數線上點 $A({x1})$、點 $Q({xq})$ 在 $\\overline{{AB}}$ 外，且 $\\overline{{AQ}}:\\overline{{BQ}} = {m}:{n}$，求 $B$ 點的坐標。"
        correct_answer = str(x2_actual)
    else:
        # B(x2_temp), Q(xq), AQ:BQ = m:n. 求 A(x1).
        # xq = (m*x2 - n*x1) / (m-n) => (m-n)*xq = m*x2 - n*x1
        # => n*x1 = m*x2 - (m-n)*xq => x1 = (m*x2 - (m-n)*xq) / n
        x1_actual = Fraction(m * x2_temp - (m - n) * xq, n)
        question_text = f"數線上點 $B({x2_temp})$、點 $Q({xq})$ 在 $\\overline{{AB}}$ 外，且 $\\overline{{AQ}}:\\overline{{BQ}} = {m}:{n}$，求 $A$ 點的坐標。"
        correct_answer = str(x1_actual)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_interpret_formula_problem(level):
    """
    生成解析分點公式表達式，判斷其代表意義 (比值或類型) 的題目。
    題目: 給定 P = (na+mb)/(m+n) 的形式，問 AP:PB 的比值或 P 的類型 (中點/內分點)。
    """
    a = 'a'
    b = 'b'
    
    num_type = random.choice(['internal', 'midpoint']) # 目前不考慮外部點的公式解析，較複雜
    
    if num_type == 'internal':
        m = random.randint(1, 5 + level)
        n = random.randint(1, 5 + level)
        
        # 內分點公式 P = (n*A + m*B) / (m+n)，對應 AP:PB = m:n
        
        # 隨機選擇係數順序，不影響答案
        if random.random() < 0.5:
            expr_num = f"{n}{a} + {m}{b}"
            ratio_a = m # 這裡的 ratio_a 對應 AP
            ratio_b = n # 這裡的 ratio_b 對應 PB
        else:
            expr_num = f"{m}{a} + {n}{b}"
            ratio_a = n # 這裡的 ratio_a 對應 AP (因為公式是 m對A, n對B)
            ratio_b = m # 這裡的 ratio_b 對應 PB
            
        expr_den = m + n
        
        question_text = f"數線上 $P$ 點的坐標為 $\\frac{{{expr_num}}}{{{expr_den}}}$。若 $A$ 點坐標為 $a$， $B$ 點坐標為 $b$，請問 $P$ 點在 $\\overline{{AB}}$ 上，且 $\\overline{{AP}}:\\overline{{PB}}$ 的比值為何？(請填寫最簡分數或整數，例如 3/2 或 2)"
        correct_answer = str(Fraction(ratio_a, ratio_b))

    elif num_type == 'midpoint':
        expr_num = f"{a} + {b}"
        expr_den = 2
        question_text = f"數線上 $Q$ 點的坐標為 $\\frac{{{expr_num}}}{{{expr_den}}}$。若 $A$ 點坐標為 $a$， $B$ 點坐標為 $b$，請問 $Q$ 點是 $\\overline{{AB}}$ 的什麼點？(請填寫「中點」或「內分點」)"
        correct_answer = "中點"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_compare_division_points_problem(level):
    """
    生成比較多個分點坐標大小的題目。
    題目: 給定 A, B 點坐標和多個分點的公式表達式，比較這些分點的大小。
    """
    # 確保 a_val < b_val 以便比較點的位置
    a_val = random.randint(-10, 0)
    b_val = random.randint(1, 10)
    while a_val == b_val:
        b_val = random.randint(1, 10)
    
    points_info = [] # 儲存 (標籤, 點的公式係數 for a, 點的公式係數 for b)
    
    # 生成 3 個點: P, Q, R
    # Q: 中點 (1a+1b)/2
    points_info.append(('Q', 1, 1)) 
    
    # P: 內分點 (n1*a+m1*b)/(n1+m1)
    m1 = random.randint(1, 4)
    n1 = random.randint(1, 4)
    while m1 == n1: # 確保不是中點
        m1 = random.randint(1, 4)
    points_info.append(('P', n1, m1)) 

    # R: 另一個內分點 (n2*a+m2*b)/(n2+m2)
    m2 = random.randint(1, 4)
    n2 = random.randint(1, 4)
    # 確保 R 的比值與 P 和中點都不同
    while (m2 == n2) or (n2 == n1 and m2 == m1): 
        n2 = random.randint(1, 4)
    points_info.append(('R', n2, m2)) 

    # 打亂順序，避免 P,Q,R 總是按照特定順序出現
    random.shuffle(points_info)

    coords_map = {} # 儲存 {標籤: 實際坐標}
    formula_map = {} # 儲存 {標籤: 公式字串}
    
    question_parts = []
    
    for label, n_coeff, m_coeff in points_info:
        denominator = n_coeff + m_coeff
        coord = Fraction(n_coeff * a_val + m_coeff * b_val, denominator)
        coords_map[label] = coord
        # 這裡的 {n_coeff}a + {m_coeff}b 需要雙大括號包住變數，避免與 f-string 自身的 {} 衝突
        formula_map[label] = f"\\frac{{{n_coeff}a + {m_coeff}b}}{{{denominator}}}" 
        question_parts.append(f"${label} = {formula_map[label]}$")

    question_text = f"設 $A({a_val})$，$B({b_val})$ 為數線上兩點。已知 {', '.join(question_parts)}，請問 $P, Q, R$ 三點由小到大的順序為何？(請依序填寫代號，例如 P<Q<R)"
    
    # 根據計算出的坐標對點進行排序
    sorted_labels = sorted(coords_map, key=coords_map.get)
    correct_answer = "<".join(sorted_labels)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    支援分數、浮點數和字串的比較。
    """
    user_ans_str = user_answer.strip().replace(' ', '').upper()
    correct_ans_str = correct_answer.strip().replace(' ', '').upper()

    is_correct = False
    result_text = ""

    # 優先嘗試字串精確比對 (例如中點、排序結果)
    if user_ans_str == correct_ans_str:
        is_correct = True
    else:
        # 嘗試分數比對 (更精確)
        try:
            user_frac = Fraction(user_ans_str)
            correct_frac = Fraction(correct_ans_str)
            if user_frac == correct_frac:
                is_correct = True
        except ValueError:
            pass # 如果不是分數，則略過

        # 如果分數比對失敗，嘗試浮點數比對 (處理小數輸入)
        if not is_correct:
            try:
                if float(user_ans_str) == float(correct_ans_str):
                    is_correct = True
            except ValueError:
                pass # 如果不是浮點數，則略過

    if is_correct:
        result_text = f"完全正確！答案是 ${correct_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer}$"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}