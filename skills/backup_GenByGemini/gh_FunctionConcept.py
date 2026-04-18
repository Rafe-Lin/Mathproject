import random
import math
from fractions import Fraction

def generate(level=1):
    """
    生成「函數概念」相關題目。
    包含：
    1. 函數值計算 (多項式、絕對值、分段函數)
    2. 定義域判斷 (有理函數、根號函數)
    3. 判斷是否為函數 (序對集合)
    4. 實務情境中的自變數/應變數識別
    """
    problem_type = random.choice([
        'evaluate_polynomial',
        'evaluate_absolute_value',
        'evaluate_piecewise',
        'identify_domain_rational',
        'identify_domain_sqrt',
        'is_relation_function',
        'identify_variables_real_world'
    ])

    if problem_type == 'evaluate_polynomial':
        return generate_evaluate_polynomial(level)
    elif problem_type == 'evaluate_absolute_value':
        return generate_evaluate_absolute_value(level)
    elif problem_type == 'evaluate_piecewise':
        return generate_evaluate_piecewise(level)
    elif problem_type == 'identify_domain_rational':
        return generate_identify_domain_rational(level)
    elif problem_type == 'identify_domain_sqrt':
        return generate_identify_domain_sqrt(level)
    elif problem_type == 'is_relation_function':
        return generate_is_relation_function(level)
    elif problem_type == 'identify_variables_real_world':
        return generate_identify_variables_real_world(level)
    else:
        # Fallback to a default type
        return generate_evaluate_polynomial(level)

def generate_evaluate_polynomial(level):
    # 題型：已知函數 f(x) = ax^2 + bx + c，請計算 f(k) 的值。
    # Level 1: 偏重線性函數 (a=0) 或簡單二次函數 (a=1, -1)
    # Level 2+: 包含更複雜的二次函數
    
    a = 0
    b = 0
    c = random.randint(-10, 10)
    
    if level == 1:
        if random.random() < 0.7: # 大部分為線性函數
            b = random.choice([-3, -2, -1, 1, 2, 3]) # 確保 b 不為 0
        else: # 簡單二次函數
            a = random.choice([1, -1])
            b = random.randint(-3, 3)
    else: # Level 2+
        a = random.choice([-3, -2, -1, 1, 2, 3])
        while a == 0: # 確保 a 不為 0 (真正的二次函數)
            a = random.choice([-3, -2, -1, 1, 2, 3])
        b = random.randint(-5, 5)

    k = random.randint(-5, 5) # 計算函數值的點

    parts = []

    # 處理 ax^2 項
    if a != 0:
        if a == 1:
            parts.append(r"x^{{2}}")
        elif a == -1:
            parts.append(r"-x^{{2}}")
        else:
            parts.append(f"{a}x^{{2}}")
            
    # 處理 bx 項
    if b != 0:
        if b > 0 and parts: # 如果不是第一項且為正，加 '+'
            if b == 1: parts.append(r"+x")
            else: parts.append(f"+{b}x")
        elif b < 0: # 如果是負數，直接加符號
            if b == -1: parts.append(r"-x")
            else: parts.append(f"{b}x")
        else: # 如果是第一項且為正
            if b == 1: parts.append(r"x")
            else: parts.append(f"{b}x")

    # 處理常數 c 項
    if c != 0:
        if c > 0 and parts: # 如果不是第一項且為正，加 '+'
            parts.append(f"+{c}")
        elif c < 0: # 如果是負數，直接加符號
            parts.append(f"{c}")
        else: # 如果是第一項且為正
            parts.append(f"{c}")

    if not parts: # 如果所有係數都為 0 (f(x) = 0)
        func_str = "0"
    else:
        func_str = "".join(parts).replace("+-", "-") # 清理 "+-" 變成 "-"

    # 計算正確答案
    correct_answer_val = a * (k**2) + b * k + c

    question_text = f"已知函數 $f(x) = {func_str}$，請計算 $f({k})$ 的值。"
    correct_answer = str(correct_answer_val)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_evaluate_absolute_value(level):
    # 題型：已知函數 f(x) = |x - a| + b，請計算 f(k) 的值。
    a = random.randint(-5, 5)
    b = random.randint(-5, 5)
    k = random.randint(-10, 10)

    # 構建絕對值項的字串表示
    if a == 0:
        abs_term = r"|x|"
    elif a > 0:
        abs_term = f"|x - {a}|"
    else: # a < 0
        abs_term = f"|x + {-a}|"

    # 構建完整函數的字串表示
    if b == 0:
        func_str = abs_term
    elif b > 0:
        func_str = f"{abs_term} + {b}"
    else: # b < 0
        func_str = f"{abs_term} {b}" # 例如：|x|-3

    correct_answer_val = abs(k - a) + b

    question_text = f"已知函數 $f(x) = {func_str}$，請計算 $f({k})$ 的值。"
    correct_answer = str(correct_answer_val)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_evaluate_piecewise(level):
    # 題型：簡單分段函數，計算 f(k) 的值。
    # f(x) = (mx + a) if x < c
    # f(x) = (nx + b) if x >= c
    
    m = random.choice([-2, -1, 1, 2]) if level > 1 else random.choice([-1, 1]) # Level 1 m=+-1, Level 2+ more coeffs
    n = random.choice([-2, -1, 1, 2]) if level > 1 else random.choice([-1, 1])
    
    a = random.randint(-5, 5)
    b = random.randint(-5, 5)
    c = random.randint(-3, 3) # 分段的閾值
    
    k = random.randint(-5, 5) # 要計算函數值的點

    # 確保兩段函數不同，避免 trivial 問題
    while (m == n and a == b) or (m * c + a == n * c + b):
        n = random.choice([-2, -1, 1, 2]) if level > 1 else random.choice([-1, 1])
        b = random.randint(-5, 5)
    
    # 輔助函數：格式化線性部分 (mx + c')
    def format_linear_part(coeff_x, const_y):
        parts = []
        if coeff_x != 0:
            if coeff_x == 1: parts.append("x")
            elif coeff_x == -1: parts.append("-x")
            else: parts.append(f"{coeff_x}x")
        
        if const_y != 0:
            if const_y > 0 and parts: parts.append(f"+{const_y}")
            elif const_y < 0 and parts: parts.append(f"{const_y}")
            elif const_y > 0: parts.append(f"{const_y}") # 第一項為正數常數
            elif const_y < 0: parts.append(f"{const_y}") # 第一項為負數常數
            
        if not parts: return "0"
        return "".join(parts).replace("+-", "-")
    
    part1_str = format_linear_part(m, a)
    part2_str = format_linear_part(n, b)
    
    func_str = r"\begin{{cases}} " \
               f"{part1_str}, & \\text{{當 }} x < {c} \\\\ " \
               f"{part2_str}, & \\text{{當 }} x \\ge {c} " \
               r"\end{{cases}}"
    
    # 根據 k 的值計算正確答案
    if k < c:
        correct_answer_val = m * k + a
    else:
        correct_answer_val = n * k + b

    question_text = f"已知函數 $f(x) = {func_str}$，請計算 $f({k})$ 的值。"
    correct_answer = str(correct_answer_val)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_identify_domain_rational(level):
    # 題型：判斷有理函數 f(x) = N(x)/D(x) 的定義域。
    # D(x) 通常為 (x - a)
    
    a = random.randint(-5, 5)
    
    # 分子可以是常數、x、或 (x+b)
    numerator_type = random.choice(['const', 'x', 'x_plus_b'])
    if level == 1: numerator_type = random.choice(['const', 'x']) # Level 1 分子較簡單

    if numerator_type == 'const':
        numerator_str = str(random.choice([1, 2, 3, -1, -2, -3]))
    elif numerator_type == 'x':
        numerator_str = "x"
    else: # 'x_plus_b'
        b = random.randint(-5, 5)
        if b == 0:
            numerator_str = "x"
        elif b > 0:
            numerator_str = f"x + {b}"
        else:
            numerator_str = f"x {b}" # 例如：x-3
    
    # 分母通常為 (x - a)
    if a == 0:
        denominator_str = "x"
    elif a > 0:
        denominator_str = f"x - {a}"
    else: # a < 0
        denominator_str = f"x + {-a}"
        
    func_str = r"\\frac{{{numerator_str}}}{{{denominator_str}}}"
    
    # 定義域：分母不能為 0，所以 x != a
    if a == 0:
        correct_answer = r"$x \\neq 0$"
    else:
        correct_answer = f"$x \\neq {a}$"

    question_text = f"請判斷函數 $f(x) = {func_str}$ 的定義域。"
    question_text += r"<br>(請以 LaTeX 格式回答，例如：$x \\neq 1$)"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_identify_domain_sqrt(level):
    # 題型：判斷根號函數 f(x) = sqrt(expr) 的定義域。
    # expr 可能是 (x - a), (a - x), 或 (kx - a)
    a = random.randint(-5, 5)
    
    if level == 1 or random.random() < 0.7: # Level 1 或大部分情況為簡單型
        if random.random() < 0.5: # sqrt(x - a)
            expr_str = f"x {'-' if a >= 0 else '+'}{abs(a)}" if a != 0 else "x"
            correct_answer_val = f"$x \\ge {a}$"
        else: # sqrt(a - x)
            expr_str = f"{a} - x"
            correct_answer_val = f"$x \\le {a}$"
    else: # Level 2+ 考慮 sqrt(kx - a)
        k = random.choice([2, 3, -2, -3]) # k 為非零整數
        if k > 0:
            expr_str = f"{k}x {'-' if a >= 0 else '+'}{abs(a)}" if a != 0 else f"{k}x"
            # kx - a >= 0 => kx >= a => x >= a/k
            frac_val = Fraction(a, k)
            if frac_val.denominator == 1:
                correct_answer_val = f"$x \\ge {frac_val.numerator}$"
            else:
                correct_answer_val = f"$x \\ge \\frac{{{frac_val.numerator}}}{{{frac_val.denominator}}}$"
        else: # k < 0
            expr_str = f"{k}x {'-' if a >= 0 else '+'}{abs(a)}" if a != 0 else f"{k}x"
            # kx - a >= 0 => kx >= a => x <= a/k (不等式方向改變)
            frac_val = Fraction(a, k)
            if frac_val.denominator == 1:
                correct_answer_val = f"$x \\le {frac_val.numerator}$"
            else:
                correct_answer_val = f"$x \\le \\frac{{{frac_val.numerator}}}{{{frac_val.denominator}}}$"
        
    func_str = r"\\sqrt{{{expr_str}}}"
    
    question_text = f"請判斷函數 $f(x) = {func_str}$ 的定義域。"
    question_text += r"<br>(請以 LaTeX 格式回答，例如：$x \\ge 1$ 或 $x \\le 1$)"
    
    correct_answer = correct_answer_val
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_is_relation_function(level):
    # 題型：給定一組序對，判斷它是否表示一個函數。
    # 函數的定義：每個 x 值只能對應唯一一個 y 值。
    
    num_pairs = random.randint(3, 5)
    pairs = []
    
    is_function_choice = random.choice([True, False])
    
    if is_function_choice:
        # 生成一個函數 (x 值唯一)
        x_coords = random.sample(range(-5, 5), num_pairs)
        for x in x_coords:
            y = random.randint(-10, 10)
            pairs.append(f"({x}, {y})")
        correct_answer = "是"
    else:
        # 生成一個不是函數的關係 (至少有一個 x 值對應多個 y 值)
        duplicate_x = random.randint(-5, 5)
        y1 = random.randint(-10, 10)
        y2 = random.randint(-10, 10)
        while y1 == y2: # 確保 y 值不同
            y2 = random.randint(-10, 10)
            
        pairs.append(f"({duplicate_x}, {y1})")
        pairs.append(f"({duplicate_x}, {y2})")
        
        # 添加剩餘的唯一序對
        x_coords_used = {duplicate_x}
        while len(x_coords_used) < num_pairs:
            new_x = random.randint(-5, 5)
            if new_x not in x_coords_used:
                x_coords_used.add(new_x)
                y = random.randint(-10, 10)
                pairs.append(f"({new_x}, {y})")
        
        random.shuffle(pairs) # 打亂順序，使重複的 x 不那麼明顯
        correct_answer = "否"

    question_text = f"請問下列集合是否表示一個函數？<br>${{ {', '.join(pairs)} }}$<br>(請回答「是」或「否」)"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_identify_variables_real_world(level):
    # 題型：在真實情境中識別自變數和應變數。
    scenarios = [
        {
            "description": "購買雞蛋的總價錢會隨著購買的雞蛋數量而改變。",
            "independent": "購買的雞蛋數量",
            "dependent": "購買雞蛋的總價錢"
        },
        {
            "description": "一個正方形的周長會隨著其邊長而改變。",
            "independent": "正方形的邊長",
            "dependent": "正方形的周長"
        },
        {
            "description": "一個人跑步的總距離會隨著跑步的時間而改變。",
            "independent": "跑步的時間",
            "dependent": "跑步的總距離"
        },
        {
            "description": "從水龍頭流出的水量會隨著水龍頭開啟的時間而改變。",
            "independent": "水龍頭開啟的時間",
            "dependent": "從水龍頭流出的水量"
        },
        {
            "description": "氣球內空氣的體積會隨著氣球充氣的程度而改變。",
            "independent": "氣球充氣的程度",
            "dependent": "氣球內空氣的體積"
        },
        {
            "description": "植物的高度會隨著施肥的量而改變。",
            "independent": "施肥的量",
            "dependent": "植物的高度"
        },
        {
            "description": "圓形的面積會隨著其半徑而改變。",
            "independent": "圓形的半徑",
            "dependent": "圓形的面積"
        }
    ]
    
    scenario = random.choice(scenarios)
    
    question_part = random.choice(['independent', 'dependent'])
    
    if question_part == 'independent':
        question_text = f"在「{scenario['description']}」這個情境中，請指出自變數（獨立變數）是什麼？"
        correct_answer = scenario["independent"]
    else:
        question_text = f"在「{scenario['description']}」這個情境中，請指出應變數（依賴變數）是什麼？"
        correct_answer = scenario["dependent"]
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查使用者答案是否正確。
    處理數字比較和字符串（包括 LaTeX 格式）的規範化比較。
    """
    user_answer_raw = user_answer.strip()
    correct_answer_raw = correct_answer.strip()

    is_correct = False
    result_text = ""

    # 首先嘗試數值比較 (適用於計算函數值的題目)
    try:
        user_num = float(user_answer_raw)
        correct_num = float(correct_answer_raw)
        if abs(user_num - correct_num) < 1e-9: # 浮點數比較容忍度
            is_correct = True
    except ValueError:
        # 如果不是純數字答案，則進行字符串比較
        pass

    if not is_correct:
        # 規範化字符串以便比較 (忽略大小寫、空格、並轉換 LaTeX 符號)
        def normalize_string_for_comparison(s):
            s = s.replace('$', '') # 移除 LaTeX $ 符號
            s = s.replace(' ', '') # 移除所有空格
            s = s.replace('　', '') # 移除全形空格
            s = s.upper() # 轉換為大寫以忽略大小寫

            # 轉換常見的 LaTeX 比較符號為標準符號
            s = s.replace(r'\GE', '>=')
            s = s.replace(r'\LE', '<=')
            s = s.replace(r'\NE', '!=')
            s = s.replace('GE', '>=') # 有些用戶可能直接輸入 GE
            s = s.replace('LE', '<=')
            s = s.replace('NE', '!=')
            s = s.replace('X', 'x') # 標準化變數為小寫 'x'
            
            # 簡化分數表示 \\frac{num}{den} -> num/den
            s = s.replace(r'\\FRAC{{', '(').replace(r'}}{{', '/').replace('}}', ')') # 對於正確答案
            s = s.replace(r'FRAC{', '(').replace('}{', '/').replace('}', ')') # 對於用戶可能輸入的簡化格式
            s = s.replace('(', '').replace(')', '') # 移除轉換後可能留下的括號
            
            s = s.replace(r'\\TEXT{當}', '當') # 處理分段函數中的中文文本
            
            return s
        
        user_answer_normalized = normalize_string_for_comparison(user_answer_raw)
        correct_answer_normalized = normalize_string_for_comparison(correct_answer_raw)

        # 直接比較規範化後的字符串
        is_correct = (user_answer_normalized == correct_answer_normalized)
        
        # 對於不等式，額外處理 'x >= A' 與 'A <= x' 等價的情況
        if not is_correct:
            if '>=' in correct_answer_normalized:
                parts = correct_answer_normalized.split('>=')
                if len(parts) == 2:
                    val = parts[1]
                    var = parts[0]
                    alt_correct_format = f"{val}<={var}" # 生成 A <= x 形式
                    if user_answer_normalized == alt_correct_format:
                        is_correct = True
            elif '<=' in correct_answer_normalized:
                parts = correct_answer_normalized.split('<=')
                if len(parts) == 2:
                    val = parts[1]
                    var = parts[0]
                    alt_correct_format = f"{val}>={var}" # 生成 A >= x 形式
                    if user_answer_normalized == alt_correct_format:
                        is_correct = True
            
    if is_correct:
        result_text = f"完全正確！答案是 ${correct_answer_raw}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer_raw}$"
    
    return {"correct": is_correct, "result": result_text, "next_question": True}