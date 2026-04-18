import random
from fractions import Fraction

def format_table(x_vals, y_vals):
    """Formats x and y values into a string table for display."""
    # Convert all values to strings to measure length
    x_strs = [str(v) for v in x_vals]
    y_strs = [str(v) for v in y_vals]
    
    # Find the maximum width needed for any cell
    max_len = 0
    for s in x_strs + y_strs:
        if len(s) > max_len:
            max_len = len(s)

    # Build the table rows
    header_x_row = " x |"
    data_y_row   = " y |"
    
    for x_str in x_strs:
        header_x_row += f" {x_str:^{max_len}} |"
    
    for y_str in y_strs:
        data_y_row += f" {y_str:^{max_len}} |"
        
    return f"{header_x_row}\n{'-' * len(header_x_row)}\n{data_y_row}"

def generate_equation_problem():
    """Generates a problem based on a mathematical equation."""
    problem_types = [
        'linear', 'constant', 'inverse', 'quadratic', 
        'absolute_y', 'not_func_y_squared', 'not_func_absolute_x'
    ]
    problem_type = random.choice(problem_types)
    
    equation = ""
    is_function = True

    if problem_type == 'linear':
        a = random.randint(-5, 5)
        while a == 0:
            a = random.randint(-5, 5)
        b = random.randint(-10, 10)
        
        op = "+" if b >= 0 else "-"
        abs_b = abs(b)
        
        if a == 1:
            a_str = ""
        elif a == -1:
            a_str = "-"
        else:
            a_str = str(a)
            
        if b == 0:
            equation = f"y = {a_str}x"
        else:
            equation = f"y = {a_str}x {op} {abs_b}"
        is_function = True
        
    elif problem_type == 'constant':
        b = random.randint(-20, 20)
        equation = f"y = {b}"
        is_function = True
        
    elif problem_type == 'inverse':
        k = random.choice([12, 18, 24, 30, 36, 48, 60])
        if random.random() < 0.5:
            equation = f"xy = {k}"
        else:
            # Note: double braces {{}} are used to escape braces in f-strings
            equation = f"y = \\frac{{{k}}}{{x}}"
        is_function = True
        
    elif problem_type == 'quadratic':
        a = random.randint(-3, 3)
        while a == 0:
            a = random.randint(-3, 3)
        
        if a == 1:
            equation = "y = x^2"
        elif a == -1:
            equation = "y = -x^2"
        else:
            equation = f"y = {a}x^2"
        is_function = True

    elif problem_type == 'absolute_y':
        equation = "y = |x|"
        is_function = True

    elif problem_type == 'not_func_y_squared':
        equation = "x = y^2"
        is_function = False

    elif problem_type == 'not_func_absolute_x':
        equation = "x = |y|"
        is_function = False

    question_text = f"給定變數 $x$、$y$ 的關係式為 ${equation}$，請問 $y$ 是否為 $x$ 的函數？ (請回答「是」或「否」)"
    correct_answer = "是" if is_function else "否"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_scenario_problem():
    """Generates a problem based on a real-world scenario."""
    scenarios = [
        {
            "context": "小翊用 360 元購買飲料。",
            "x_var": "每杯飲料 $x$ 元",
            "y_var": "可購買的杯數 $y$ 杯",
            "is_function": True
        },
        {
            "context": "攝氏度數 (°C) 和華氏度數 (°F) 的關係為：華氏度數 = $\\frac{9}{5} \\times$ 攝氏度數 $+ 32$。",
            "x_var": "攝氏度數 $x$",
            "y_var": "華氏度數 $y$",
            "is_function": True
        },
        {
            "context": "小妍與小翊兩人合力將學校剛買進的 100 本新書做編碼。",
            "x_var": "小妍完成的本數 $x$ 本",
            "y_var": "小翊完成的本數 $y$ 本",
            "is_function": True
        },
        {
            "context": "小恩使用某家電信公司的網路，月繳 800 元可以不限時數上網。",
            "x_var": "小恩每月上網的時間 $x$ (分鐘)",
            "y_var": "小恩該月應繳的上網費用 $y$ (元)",
            "is_function": True
        },
        {
            "context": "珍新鮮壽司店推出「299 吃到飽」的促銷活動。",
            "x_var": "小靖所吃的壽司盤數 $x$",
            "y_var": "小靖所需支付的金額 $y$ (元)",
            "is_function": True
        },
        {
            "context": "在平年中(一年有 365 天)。",
            "x_var": "月份 $x$",
            "y_var": "該月份的天數 $y$",
            "is_function": True
        },
        {
            "context": "有一個正方形。",
            "x_var": "邊長為 $x$ 公分",
            "y_var": "面積為 $y$ 平方公分",
            "is_function": True
        },
        {
            "context": "某班級學生的身高與體重紀錄。",
            "x_var": "身高 $x$ (公分)",
            "y_var": "體重 $y$ (公斤)",
            "is_function": False
        },
        {
            "context": "某城市一天的氣溫紀錄。",
            "x_var": "時間 $x$ (點)",
            "y_var": "當時的氣溫 $y$ (度C)",
            "is_function": True
        },
        {
            "context": "某城市一天的氣溫紀錄。",
            "x_var": "氣溫 $x$ (度C)",
            "y_var": "當時的時間 $y$ (點)",
            "is_function": False
        }
    ]
    
    selected_scenario = random.choice(scenarios)
    
    question_text = (
        f"{selected_scenario['context']}\n"
        f"若以「{selected_scenario['x_var']}」為 $x$，以「{selected_scenario['y_var']}」為 $y$，"
        f"請問 $y$ 是否為 $x$ 的函數？ (請回答「是」或「否」)"
    )
    
    correct_answer = "是" if selected_scenario['is_function'] else "否"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }
    
def generate_table_problem():
    """Generates a problem based on a table of values."""
    is_function = random.choice([True, True, False])
    x_vals = []
    y_vals = []
    
    if is_function:
        # Create a table that represents a function
        func_type = random.choice(['linear', 'inverse', 'constant', 'quadratic'])
        x_start = random.randint(1, 5)
        x_vals = [x_start + i for i in range(5)]
        
        if func_type == 'linear':
            a = random.randint(2, 5) * random.choice([-1, 1])
            b = random.randint(-10, 10)
            y_vals = [a * x + b for x in x_vals]
        elif func_type == 'inverse':
            k = random.choice([24, 30, 36, 48, 60, 72])
            divisors = [i for i in range(1, 13) if k % i == 0]
            x_vals = random.sample(divisors, min(5, len(divisors)))
            x_vals.sort()
            y_vals = [k // x for x in x_vals]
        elif func_type == 'constant':
            c = random.randint(10, 50)
            y_vals = [c for _ in x_vals]
        elif func_type == 'quadratic':
            x_start = random.randint(-2, 2)
            x_vals = [x_start + i for i in range(5)]
            y_vals = [x**2 for x in x_vals]
            
    else:
        # Create a table that does NOT represent a function
        x_base = random.sample(range(1, 20), 4)
        repeated_x = random.choice(x_base)
        x_vals = x_base + [repeated_x]
        
        y_pool = list(range(5, 50))
        random.shuffle(y_pool)
        
        # Assign unique y values to the unique x values
        y_map = {x: y for x, y in zip(x_base, y_pool[:4])}
        
        # Assign a different y value to the repeated x
        y_for_repeated_x = y_pool[4]
        
        y_vals = [y_map.get(x) for x in x_vals[:-1]] + [y_for_repeated_x]

        # Shuffle the pairs to hide the pattern
        pairs = list(zip(x_vals, y_vals))
        random.shuffle(pairs)
        x_vals, y_vals = zip(*pairs)

    table_str = format_table(list(x_vals), list(y_vals))
    question_text = (
        "請觀察下表中變數 $x$ 與 $y$ 的對應關係，並判斷 $y$ 是否為 $x$ 的函數？ (請回答「是」或「否」)\n\n"
        f"```\n{table_str}\n```"
    )
    
    correct_answer = "是" if is_function else "否"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    生成「函數的判斷」相關題目。
    包含：
    1. 從關係式判斷
    2. 從生活情境判斷
    3. 從表格判斷
    """
    problem_type = random.choice(['equation', 'scenario', 'table'])
    
    if problem_type == 'equation':
        return generate_equation_problem()
    elif problem_type == 'scenario':
        return generate_scenario_problem()
    else: # table
        return generate_table_problem()

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip()
    
    is_correct = (user_answer == correct_answer)
    
    if is_correct:
        result_text = f"完全正確！答案是「{correct_answer}」。"
    else:
        result_text = f"答案不正確。正確答案應為「{correct_answer}」。"

    # Provide a brief explanation for "why"
    if correct_answer == "是":
        result_text += "\n\n函數的定義是：對於每一個給定的 $x$ 值，都「恰好」有一個 $y$ 值與它對應 (一對一或多對一)。"
    else:
        result_text += "\n\n函數的定義是：對於每一個給定的 $x$ 值，都「恰好」有一個 $y$ 值與它對應。在此情況中，至少有一個 $x$ 值對應到兩個或以上不同的 $y$ 值 (一對多)，所以 $y$ 不是 $x$ 的函數。"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}