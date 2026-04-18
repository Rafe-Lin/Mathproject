import random

def generate(level=1):
    """
    生成「整數的加減運算」相關題目 (標準 LaTeX 範本)。
    根據參考例題，涵蓋以下題型：
    1. 基本三數運算
    2. 使用交換律/結合律簡化運算
    3. 包含絕對值的運算
    4. 去括號規則的運算
    5. 兩式結果的比較
    """
    # 根據例題類型分配權重，讓計算題出現頻率較高
    problem_types = [
        'basic_calc', 'basic_calc', 'basic_calc',
        'smart_calc',
        'abs_val_calc', 'abs_val_calc',
        'parentheses_calc',
        'comparison'
    ]
    problem_type = random.choice(problem_types)
    
    if problem_type == 'basic_calc':
        return generate_basic_calc_problem()
    elif problem_type == 'smart_calc':
        return generate_smart_calc_problem()
    elif problem_type == 'abs_val_calc':
        return generate_abs_val_calc_problem()
    elif problem_type == 'parentheses_calc':
        return generate_parentheses_calc_problem()
    elif problem_type == 'comparison':
        return generate_comparison_problem()
    else:
        # 備用，指向最基本的題型
        return generate_basic_calc_problem()

def _format_num(n):
    """輔助函數：將負數用括號包起來。"""
    return f"({n})" if n < 0 else str(n)

def generate_basic_calc_problem():
    """生成基本的三數加減運算。"""
    a = random.randint(-100, 100)
    b = random.randint(-100, 100)
    c = random.randint(-100, 100)

    # 確保不會出現 0，讓題目更有挑戰性
    while a == 0 or b == 0 or c == 0:
        a = random.randint(-100, 100)
        b = random.randint(-100, 100)
        c = random.randint(-100, 100)

    op1 = random.choice(['+', '-'])
    op2 = random.choice(['+', '-'])

    question_text = f"計算下列各式的值。\n$ {_format_num(a)} {op1} {_format_num(b)} {op2} {_format_num(c)} $"
    # 使用 eval 計算答案，因為運算式由我們自己安全地生成
    correct_answer = str(eval(f"{a} {op1} {b} {op2} {c}"))

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_smart_calc_problem():
    """生成可使用交換律/結合律簡化的題目。"""
    # 創造兩個相近或相反的數
    n1 = random.randint(100, 999)
    n2 = -n1 + random.randint(-20, 20)
    n3 = random.randint(-150, 150)

    terms = [n1, n2, n3]
    random.shuffle(terms)
    a, b, c = terms
    
    op1 = random.choice(['+', '-'])
    op2 = random.choice(['+', '-'])
    
    # 為了讓題目符合簡化計算的模式，隨機調整運算符和數值符號
    if random.random() < 0.5:
        # e.g., (-652) + 125 - (-552)
        b = abs(b)
        op1 = '+'
        op2 = '-'
        c = -c

    question_text = f"計算下列各式的值。\n$ {_format_num(a)} {op1} {_format_num(b)} {op2} {_format_num(c)} $"
    correct_answer = str(eval(f"{a} {op1} {b} {op2} {c}"))

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_abs_val_calc_problem():
    """生成包含絕對值的運算。"""
    pattern = random.choice(['pattern1', 'pattern2'])

    if pattern == 'pattern1':
        # 格式：｜-25｜-｜-75｜-18
        a = random.randint(-100, 100)
        b = random.randint(-100, 100)
        c = random.randint(-50, 50)
        op1 = random.choice(['+', '-'])
        op2 = random.choice(['+', '-'])

        question_text = f"計算下列各式的值。\n$ |{a}| {op1} |{b}| {op2} {_format_num(c)} $"
        correct_answer = str(eval(f"abs({a}) {op1} abs({b}) {op2} {c}"))
    else:
        # 格式：30＋｜(-64 )＋14｜-25
        a = random.randint(10, 50)
        b = random.randint(-100, 100)
        c = random.randint(-100, 100)
        d = random.randint(10, 50)
        op1 = random.choice(['+', '-'])
        op2 = random.choice(['+', '-'])

        question_text = f"計算下列各式的值。\n$ {a} + |{_format_num(b)} {op1} {_format_num(c)}| - {d} $"
        correct_answer = str(eval(f"{a} + abs({b} {op1} {c}) - {d}"))

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_parentheses_calc_problem():
    """生成去括號規則的運算題目。"""
    a = random.randint(200, 1999)
    b = random.randint(20, 199)

    templates = [
        (f"{a} - ( {b} + {a} )", -b),
        (f"{_format_num(-a)} - ( {b} - {a} )", -b),
        (f"{a} + ( {b} - {a} )", b),
        (f"( {a} + {b} ) - {a}", b)
    ]

    expr, ans = random.choice(templates)

    question_text = f"計算下列各式的值。\n$ {expr} $"
    correct_answer = str(ans)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_comparison_problem():
    """生成比較兩式結果是否相同的題目。"""
    a = random.randint(2, 25)
    b = random.randint(2, 25)
    c = random.randint(2, 25)

    # 確保 a 和 b 不相等，避免 (a-b) 和 (b-a) 都等於 0 的情況
    while a == b:
        b = random.randint(2, 25)

    templates = [
        (f"-({a} + {b})", f"-{a} - {b}", "相同"),
        (f"-({a} - {b})", f"-{a} + {b}", "相同"),
        (f"-(-{a} - {b})", f"{a} + {b}", "相同"),
        (f"{c} - ({a} - {b})", f"{c} - {a} + {b}", "相同"),
        (f"-(-{a} + {b})", f"{a} - {b}", "相同"),
        (f"-({a} + {b})", f"-{a} + {b}", "不同"),
        (f"-({a} - {b})", f"-{a} - {b}", "不同"),
        (f"{c} - ({a} + {b})", f"{c} - {a} + {b}", "不同"),
        (f"({a} - {b})", f"({b} - {a})", "不同")
    ]

    expr1_str, expr2_str, correct_answer = random.choice(templates)

    question_text = f"比較下列各題中，兩式的運算結果是否相同？ (請填 相同 或 不同)\n$ {expr1_str} $ 和 $ {expr2_str} $"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確，能處理數字和特定文字（相同/不同）。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    is_correct = False

    if correct_answer in ["相同", "不同"]:
        if correct_answer == "相同" and user_answer in ["相同", "一樣", "相等"]:
            is_correct = True
        elif correct_answer == "不同" and user_answer in ["不同", "不一樣", "不相等"]:
            is_correct = True
    else:
        if user_answer.upper() == correct_answer.upper():
            is_correct = True
        else:
            try:
                if float(user_answer) == float(correct_answer):
                    is_correct = True
            except (ValueError, TypeError):
                pass

    # 根據答案類型決定是否使用 LaTeX 格式
    try:
        num_ans = float(correct_answer)
        if num_ans == int(num_ans):
            answer_display = f"${int(num_ans)}$"
        else:
            answer_display = f"${num_ans}$"
    except (ValueError, TypeError):
        answer_display = correct_answer

    result_text = f"完全正確！答案是 {answer_display}。" if is_correct else f"答案不正確。正確答案應為：${answer_display}"
    return {"correct": is_correct, "result": result_text, "next_question": True}
