import random
from fractions import Fraction

def generate(level=1):
    """
    生成「平方根的意義」相關題目。
    包含：
    1. 求一數的平方根
    2. 已知平方根反推未知數
    """
    problem_type = random.choice(['find_sqrt', 'solve_for_x'])
    
    if problem_type == 'find_sqrt':
        return generate_find_sqrt_problem()
    else:
        return generate_solve_for_x_problem()

def generate_find_sqrt_problem():
    """
    題型：寫出下列各數的平方根。
    涵蓋：完全平方整數、分數、小數，以及非完全平方數與 0。
    """
    sub_type = random.choice(['perfect_int', 'perfect_frac', 'perfect_dec', 'non_perfect_int', 'zero'])
    
    if sub_type == 'perfect_int':
        base = random.randint(2, 20)
        num = base**2
        question_text = f"寫出 ${num}$ 的平方根。"
        correct_answer = f"\\pm{base}"
        
    elif sub_type == 'perfect_frac':
        # 生成一個不會化簡的分數
        while True:
            num_base = random.randint(2, 9)
            den_base = random.randint(2, 9)
            if num_base != den_base and Fraction(num_base, den_base).denominator == den_base:
                break
        
        frac = Fraction(num_base, den_base)
        num_sq = frac.numerator**2
        den_sq = frac.denominator**2
        
        question_text = f"寫出 $\\frac{{{num_sq}}}{{{den_sq}}}$ 的平方根。"
        correct_answer = f"\\pm\\frac{{{frac.numerator}}}{{{frac.denominator}}}"

    elif sub_type == 'perfect_dec':
        base = random.choice([i for i in range(2, 16) if i % 10 != 0])
            
        num = base**2 / 100.0
        num_str = f"{num:.2f}".rstrip('0').rstrip('.')
        
        dec_base = base / 10.0
        dec_base_str = f"{dec_base:.1f}".rstrip('0').rstrip('.')

        question_text = f"寫出 ${num_str}$ 的平方根。"
        correct_answer = f"\\pm{dec_base_str}"
        
    elif sub_type == 'non_perfect_int':
        perfect_squares = {i**2 for i in range(2, 11)}
        num = random.randint(2, 60)
        while num in perfect_squares:
            num = random.randint(2, 60)
        
        question_text = f"寫出 ${num}$ 的平方根。"
        correct_answer = f"\\pm\\sqrt{{{num}}}"
        
    else: # sub_type == 'zero'
        question_text = "寫出 $0$ 的平方根。"
        correct_answer = "0"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_solve_for_x_problem():
    """
    題型：若 b 是 ax+c 的平方根，求 x。
    """
    base = random.randint(2, 12)
    root = random.choice([base, -base])
    
    a = random.randint(2, 5)
    c = random.randint(-20, 20)
    number_to_be_rooted = root**2
    
    # 確保題目有解且不為零，且 c 不等於 number_to_be_rooted，避免 ax=0 的 trivial case
    while c == number_to_be_rooted or (number_to_be_rooted - c) == 0:
        c = random.randint(-20, 20)
    
    # 建構題目文字
    root_type_str = "正" if root > 0 else "負"
    
    if c == 0:
        expression_str = f"{a}x"
    elif c > 0:
        expression_str = f"{a}x + {c}"
    else: # c < 0
        expression_str = f"{a}x - {-c}"
        
    question_text = f"若 ${root}$ 是 ${expression_str}$ 的{root_type_str}平方根，求 $x$ 的值。"
    
    # 計算答案
    x_num = number_to_be_rooted - c
    x_den = a
    ans_frac = Fraction(x_num, x_den)
    
    if ans_frac.denominator == 1:
        correct_answer = str(ans_frac.numerator)
    else:
        correct_answer = f"{ans_frac.numerator}/{ans_frac.denominator}"
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    # 標準化使用者輸入：去除空白，並統一 ± 符號
    user_answer_norm = user_answer.strip().replace(" ", "")
    user_answer_norm = user_answer_norm.replace("+-", "±").replace("+/-", "±")

    # 標準化正確答案以進行比對 (將 LaTeX 轉為純文字)
    correct_answer_plain = correct_answer.strip().replace(" ", "")
    correct_answer_plain = correct_answer_plain.replace("\\pm", "±")
    correct_answer_plain = correct_answer_plain.replace("\\sqrt", "sqrt")
    if "\\frac" in correct_answer_plain:
        # e.g., \\pm\\frac{3}{5} -> ±3/5
        correct_answer_plain = correct_answer_plain.replace("\\frac{", "").replace("}{", "/").replace("}", "")

    # 主要比對：純文字字串比對
    is_correct = (user_answer_norm == correct_answer_plain)
    
    # 輔助比對：若主要比對失敗，對純數字/分數的答案嘗試進行數值比對
    if not is_correct:
        try:
            # 數值比對只適用於不含符號的答案
            if '±' not in correct_answer_plain and 'sqrt' not in correct_answer_plain:
                # 從正確答案計算目標數值
                target_value = float(Fraction(correct_answer_plain))
                
                # 從使用者答案計算其數值
                user_value = float(Fraction(user_answer_norm))

                # 使用容忍度來比較浮點數
                if abs(user_value - target_value) < 1e-9:
                    is_correct = True
        except (ValueError, ZeroDivisionError):
            # 若轉換失敗，表示格式不符，維持 is_correct = False
            pass

    if is_correct:
        result_text = f"完全正確！答案是 ${correct_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer}$"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}