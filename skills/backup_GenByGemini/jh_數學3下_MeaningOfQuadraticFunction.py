import random
from fractions import Fraction

def generate(level=1):
    """
    生成「二次函數的意義」相關題目。
    技能ID: jh_數學3下_MeaningOfQuadraticFunction
    介紹二次函數的定義 y＝ax^2＋bx＋c (a≠0)，並透過實例與一次、常數函數區別。
    
    包含：
    1. 從關係式判斷是否為二次函數。
    2. 從應用問題情境判斷兩變數的關係是否為二次函數。
    """
    problem_type = random.choice(['identification', 'word_problem'])
    
    if problem_type == 'identification':
        return generate_identification_problem()
    else: # 'word_problem'
        return generate_word_problem_problem()

def generate_quadratic_expression():
    """Helper function to generate a random quadratic expression string."""
    form = random.choice(['standard', 'vertex', 'factored'])
    a = random.randint(1, 5) * random.choice([-1, 1])
    
    # Standard form: y = ax^2 + bx + c
    if form == 'standard':
        b = random.randint(-7, 7)
        c = random.randint(-7, 7)
        
        # Build the string representation
        if a == 1:
            expr = "x^2"
        elif a == -1:
            expr = "-x^2"
        else:
            expr = f"{a}x^2"

        if b != 0:
            if b > 0:
                if len(expr) > 0 and expr != "-x^2" and not expr.startswith('-'): # Avoid "+ -"
                    expr += " + "
                expr += f"{b}x" if b != 1 else "x"
            else: # b < 0
                expr += f" - {-b}x" if b != -1 else " - x"
        
        if c != 0:
            if c > 0:
                if len(expr) > 0 and not expr.startswith('-'):
                     expr += " + "
                expr += f"{c}"
            else: # c < 0
                expr += f" - {-c}"
        
        if b == 0 and c == 0:
            pass # Already handled by the initial part
            
        return f"y = {expr}"

    # Vertex form: y = a(x-h)^2 + k
    elif form == 'vertex':
        h = random.randint(-5, 5)
        k = random.randint(-5, 5)
        
        if h == 0:
            h_str = "x"
        elif h > 0:
            h_str = f"(x - {h})"
        else:
            h_str = f"(x + {-h})"

        if a == 1:
            a_str = ""
        elif a == -1:
            a_str = "-"
        else:
            a_str = str(a)
            
        if k > 0:
            k_str = f" + {k}"
        elif k < 0:
            k_str = f" - {-k}"
        else:
            k_str = ""
        
        return f"y = {a_str}{h_str}^2{k_str}"
        
    # Factored form: y = a(x-p)(x-q)
    else: # 'factored'
        p = random.randint(-5, 5)
        q = random.randint(-5, 5)
        
        p_str = f"(x - {p})" if p > 0 else f"(x + {-p})"
        if p == 0: p_str = "x"
        
        q_str = f"(x - {q})" if q > 0 else f"(x + {-q})"
        if q == 0: q_str = "x"

        a_str = ""
        if a == -1: a_str = "-"
        elif a != 1: a_str = str(a)
        
        if p == 0 and q == 0:
            return f"y = {a}x^2"
            
        return f"y = {a_str}{p_str}{q_str}"

def generate_non_quadratic_expression():
    """Helper function to generate a random non-quadratic expression string."""
    form = random.choice(['linear', 'constant', 'rational', 'cubic', 'cancel_out'])
    
    if form == 'linear':
        m = random.randint(1, 9) * random.choice([-1, 1])
        c = random.randint(-9, 9)
        m_str = f"{m}x"
        if m == 1: m_str = "x"
        if m == -1: m_str = "-x"
        
        c_str = ""
        if c > 0: c_str = f" + {c}"
        elif c < 0: c_str = f" - {-c}"
        return f"y = {m_str}{c_str}"
        
    elif form == 'constant':
        c = random.randint(-20, 20)
        return f"y = {c}"
        
    elif form == 'rational':
        num = random.randint(1, 9) * random.choice([-1, 1])
        power = random.choice(['', '^2'])
        return f"y = \\frac{{{num}}}{{x{power}}}"
        
    elif form == 'cubic':
        a = random.randint(1, 3) * random.choice([-1, 1])
        b = random.randint(-5, 5)
        a_str = f"{a}x^3" if a != 1 else "x^3"
        if a == -1: a_str = "-x^3"
        
        b_str = ""
        if b != 0:
            if b > 0: b_str = f" + {b}x"
            else: b_str = f" - {-b}x"
        return f"y = {a_str}{b_str}"

    elif form == 'cancel_out': # looks quadratic but isn't
        a = random.randint(2, 5)
        b = random.randint(1, 5) * random.choice([-1, 1])
        c = random.randint(1, 5) * random.choice([-1, 1])
        b_str = f"+ {b}x" if b > 0 else f"- {-b}x"
        c_str = f"+ {c}" if c > 0 else f"- {-c}"
        return f"y = {a}x^2 {b_str} {c_str} - {a}x^2"

def generate_identification_problem():
    """
    生成「從關係式判斷」的題型。
    隨機生成一個關係式，要求學生判斷是否為二次函數。
    """
    # 50% chance of being quadratic, 50% chance of not.
    is_quadratic = random.choice([True, False])
    
    if is_quadratic:
        expression = generate_quadratic_expression()
        correct_answer = "是"
    else:
        expression = generate_non_quadratic_expression()
        correct_answer = "否"
        
    question_text = f"判斷下列關係式中，$y$ 是否為 $x$ 的二次函數？ (請回答「是」或「否」)<br>${expression}$"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_word_problem_problem():
    """
    生成「從應用問題判斷」的題型。
    提供一個情境，要求學生判斷兩變數間的關係是否為二次函數。
    """
    problem_type = random.choice(['m_shape', 'teams', 'perimeter', 'rectangle_area', 'number_product'])
    
    if problem_type == 'm_shape':
        length = random.randint(20, 150)
        question_text = (
            f"某餐廳為防疫，將長 ${length}$ 公分的長板，圍成一個ㄇ形隔板，"
            f"其中兩側長均為 $x$ 公分。若隔板圍成的長方形面積為 $y$ 平方公分，"
            f"請問 $y$ 是否為 $x$ 的二次函數？ (請回答「是」或「否」)"
        )
        # y = x(length - 2x) = -2x^2 + length*x. It is quadratic.
        correct_answer = "是"

    elif problem_type == 'teams':
        diff = random.randint(3, 10)
        question_text = (
            f"某校畢業旅行共分成 $x$ 隊，每隊的學生人數比隊數少 ${diff}$ 人。"
            f"若參加的學生共有 $y$ 人，請問 $y$ 是否為 $x$ 的二次函數？ (請回答「是」或「否」)"
        )
        # y = x(x - diff) = x^2 - diff*x. It is quadratic.
        correct_answer = "是"
        
    elif problem_type == 'perimeter':
        shape = random.choice(['正方形', '正三角形'])
        if shape == '正方形':
            multiplier = 4
        else: # 正三角形
            multiplier = 3
        question_text = (
            f"一個{shape}的邊長為 $x$ 公分，其周長為 $y$ 公分。"
            f"請問 $y$ 是否為 $x$ 的二次函數？ (請回答「是」或「否」)"
        )
        # y = 4x or y = 3x. It is linear.
        correct_answer = "否"

    elif problem_type == 'rectangle_area':
        diff = random.randint(2, 8)
        relation = random.choice(['多', '少'])
        if relation == '多':
            # 長比寬多 diff. 寬是x, 長是 x+diff
            question_text = (
                f"一個長方形的寬為 $x$ 公分，長比寬多 ${diff}$ 公分。"
                f"若此長方形的面積為 $y$ 平方公分，請問 $y$ 是否為 $x$ 的二次函數？ (請回答「是」或「否」)"
            )
            # y = x(x+diff) = x^2 + diff*x. It is quadratic.
            correct_answer = "是"
        else: # 少
            question_text = (
                f"一個長方形的寬為 $x$ 公分，長比寬少 ${diff}$ 公分 (假設 $x > {diff}$)。"
                f"若此長方形的面積為 $y$ 平方公分，請問 $y$ 是否為 $x$ 的二次函數？ (請回答「是」或「否」)"
            )
            # y = x(x-diff) = x^2 - diff*x. It is quadratic.
            correct_answer = "是"

    else: # number_product
        relation = random.choice(['consecutive', 'diff'])
        if relation == 'consecutive':
            question_text = (
                "有兩個連續正整數，較小的數為 $x$。若這兩數的乘積為 $y$，"
                "請問 $y$ 是否為 $x$ 的二次函數？ (請回答「是」或「否」)"
            )
            # y = x(x+1) = x^2 + x. It is quadratic.
            correct_answer = "是"
        else: # diff
            diff = random.randint(2, 10)
            question_text = (
                f"有兩個數，其中一數為 $x$，另一數比 $x$ 大 ${diff}$。"
                f"若這兩數的乘積為 $y$，請問 $y$ 是否為 $x$ 的二次函數？ (請回答「是」或「否」)"
            )
            # y = x(x+diff) = x^2 + diff*x. It is quadratic.
            correct_answer = "是"
            
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip()
    is_correct = (user_answer == correct_answer)
    
    if is_correct:
        result_text = f"完全正確！答案是「{correct_answer}」。"
    else:
        result_text = f"不正確。正確答案應為：「{correct_answer}」。"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}