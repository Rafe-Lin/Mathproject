import random

def generate(level=1):
    """
    生成「二元一次聯立方程式」相關題目。
    包含：
    1. 選擇題：從選項中找出聯立方程式的解。
    2. 計算題：直接求解聯立方程式。
    """
    problem_type = random.choice(['find_solution_mcq', 'solve_system'])
    
    if problem_type == 'find_solution_mcq':
        return generate_find_solution_mcq_problem()
    else: # 'solve_system'
        return generate_solve_system_problem()

def _format_equation(a, b, c):
    """
    將係數 a, b 和常數 c 格式化為 'ax + by = c' 的字串形式。
    處理係數為 1, -1, 0 的情況。
    """
    terms = []
    # 處理 x 項
    if a != 0:
        if a == 1:
            terms.append("x")
        elif a == -1:
            terms.append("-x")
        else:
            terms.append(f"{a}x")
    
    # 處理 y 項
    if b != 0:
        sign = " + " if b > 0 else " - "
        val = abs(b)
        
        if val == 1:
            y_term = "y"
        else:
            y_term = f"{val}y"
            
        # 如果 x 項為 0 且 y 項為正，則不加前導 '+' 號
        if not terms and b > 0:
            terms.append(y_term)
        else:
            terms.append(f"{sign}{y_term}")

    # 如果 x, y 項都為 0
    if not terms:
        left_side = "0"
    else:
        left_side = "".join(terms)
        
    return f"{left_side} = {c}"

def generate_find_solution_mcq_problem():
    """
    題型：給定一個聯立方程式和四個選項，選出正確的解。
    """
    # 1. 生成一個整數解 (x, y)
    x = random.randint(-5, 5)
    y = random.randint(-5, 5)

    # 2. 生成係數 a, b, c, d，並確保方程組有唯一解
    while True:
        # 係數範圍小一點，題目較友善
        coeffs = [random.randint(-4, 4) for _ in range(4)]
        a, b, c, d = coeffs
        # 為簡化題目，避免係數為 0
        if 0 in coeffs:
            continue
        # 檢查行列式 ad - bc != 0，確保唯一解
        if a * d - b * c != 0:
            break

    # 3. 計算常數項 e, f
    e = a * x + b * y
    f = c * x + d * y

    # 4. 格式化方程式字串
    eq1_str = _format_equation(a, b, e)
    eq2_str = _format_equation(c, d, f)

    # 5. 建立正確選項和干擾項
    correct_option = f"x={x}、y={y}"
    options = {correct_option}
    
    # 干擾項 1：只滿足第一個方程式
    try:
        x_d1 = x + random.choice([-2, -1, 1, 2])
        if b != 0 and (e - a * x_d1) % b == 0:
            y_d1 = (e - a * x_d1) // b
            if (x_d1, y_d1) != (x, y):
                options.add(f"x={x_d1}、y={y_d1}")
    except Exception:
        pass

    # 干擾項 2：只滿足第二個方程式
    try:
        y_d2 = y + random.choice([-2, -1, 1, 2])
        if c != 0 and (f - d * y_d2) % c == 0:
            x_d2 = (f - d * y_d2) // c
            if (x_d2, y_d2) != (x, y):
                options.add(f"x={x_d2}、y={y_d2}")
    except Exception:
        pass

    # 若選項不足，用隨機數值補滿
    while len(options) < 4:
        x_rand = x + random.randint(-3, 3)
        y_rand = y + random.randint(-3, 3)
        if x_rand == x and y_rand == y: continue
        options.add(f"x={x_rand}、y={y_rand}")

    # 6. 格式化題目和選項
    options_list = list(options)
    random.shuffle(options_list)
    
    correct_label = chr(ord('A') + options_list.index(correct_option))

    options_text = []
    for i, opt in enumerate(options_list):
        label = chr(ord('A') + i)
        options_text.append(f"{label}) ${opt}$")
    
    options_str = "<br>".join(options_text)

    question_text = f"下列各選項中，何者是二元一次聯立方程式 $\\begin{{cases}} {eq1_str} \\\\ {eq2_str} \\end{{cases}}$ 的解？<br>{options_str}"

    return {
        "question_text": question_text,
        "answer": correct_label,
        "correct_answer": correct_label
    }

def generate_solve_system_problem():
    """
    題型：給定一個聯立方程式，直接求解 x 和 y。
    """
    # 1. 生成一個整數解 (x, y)
    x = random.randint(-7, 7)
    y = random.randint(-7, 7)
    
    # 2. 生成係數，並確保有係數為 1 或 -1 以利於代入消去法
    while True:
        a, b, c, d = [random.randint(-4, 4) for _ in range(4)]
        if 0 in [a, b, c, d]: continue
        if abs(a)!=1 and abs(b)!=1 and abs(c)!=1 and abs(d)!=1: continue
        if a * d - b * c != 0: break

    # 3. 計算常數項 e, f
    e = a * x + b * y
    f = c * x + d * y

    # 4. 格式化方程式字串
    eq1_str = _format_equation(a, b, e)
    eq2_str = _format_equation(c, d, f)

    # 5. 建立問題文字
    # [教學示範] 使用 <br> 換行，並在 LaTeX 中使用 \\ 換行
    question_text = f"請求解下列二元一次聯立方程式：<br>$\\begin{{cases}} {eq1_str} \\\\ {eq2_str} \\end{{cases}}$<br>(請以 $x=...$、$y=...$ 的格式作答)"

    # 6. 設定正確答案
    correct_answer = f"x={x}, y={y}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查使用者答案是否正確。
    - 對於選擇題，比對選項代號。
    - 對於計算題，解析 'x=..., y=...' 格式的答案。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    is_correct = False

    # 處理選擇題
    if len(correct_answer) == 1 and 'A' <= correct_answer.upper() <= 'D':
        is_correct = (user_answer.upper() == correct_answer.upper())
    # 處理計算題 (格式如 "x=a, y=b")
    else:
        try:
            # 正規化答案字串：去除空白、轉為小寫、以逗號分割並排序
            # 這樣可以處理 "y=b, x=a" 和 "x=a, y=b" 的順序問題
            user_parts = sorted([part.strip() for part in user_answer.lower().replace(" ", "").split(',')])
            correct_parts = sorted([part.strip() for part in correct_answer.lower().replace(" ", "").split(',')])
            
            if user_parts == correct_parts:
                is_correct = True
        except:
            # 如果解析出錯，代表格式不符，視為錯誤
            is_correct = False

    # [教學示範] 在回傳結果中也可以包含 LaTeX
    if is_correct:
        # 使用原始 correct_answer 以保留格式
        result_text = f"完全正確！答案是 ${correct_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer}$"

    return {"correct": is_correct, "result": result_text, "next_question": True}
