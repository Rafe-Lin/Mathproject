import random
import math

def generate(level=1):
    """
    生成「二元一次方程式」相關題目 (標準 LaTeX 範本)。
    包含：
    1. 依題意列式
    2. 判斷是否為解
    3. 給定一數求另一數
    4. 非負整數解個數
    """
    problem_type = random.choice([
        'translate_word_problem',
        'verify_solution',
        'find_y_given_x',
        'count_non_negative_integer_solutions'
    ])

    if problem_type == 'translate_word_problem':
        return generate_translate_word_problem()
    elif problem_type == 'verify_solution':
        return generate_verify_solution_problem()
    elif problem_type == 'find_y_given_x':
        return generate_find_y_given_x_problem()
    else:
        return generate_count_non_negative_integer_solutions_problem()

def _format_equation(a, b, c):
    """Helper function to format an equation ax + by = c nicely."""
    term_a = ""
    if a == 1:
        term_a = "x"
    elif a == -1:
        term_a = "-x"
    elif a != 0:
        term_a = f"{a}x"

    term_b = ""
    op = "+" if b > 0 else "-"
    abs_b = abs(b)
    if abs_b == 1:
        term_b = "y"
    elif abs_b != 0:
        term_b = f"{abs_b}y"

    if term_a and term_b:
        full_str = f"{term_a} {op} {term_b}"
    elif term_a:
        full_str = term_a
    elif term_b:
        if b < 0:
            full_str = f"-{term_b}"
        else:
            full_str = term_b
    else:
        full_str = "0"

    return f"{full_str} = {c}"

def generate_translate_word_problem():
    items = random.choice([("原子筆", "鉛筆", "枝"), ("蘋果", "香蕉", "個"), ("餅乾", "糖果", "包")])
    item1_name, item2_name, unit = items
    price1 = random.randint(5, 50)
    price2 = random.randint(5, 50)
    while price1 == price2:
        price2 = random.randint(5, 50)

    qty1 = random.randint(3, 12)
    qty2 = random.randint(3, 12)
    total_qty = qty1 + qty2
    total_cost = price1 * qty1 + price2 * qty2

    problem_subtype = random.choice(['quantity', 'cost'])

    question_base = f"已知{item1_name}每{unit} ${price1}$ 元，{item2_name}每{unit} ${price2}$ 元，若買了 $x$ {unit}的{item1_name}和 $y$ {unit}的{item2_name}，請依下列題意列出二元一次方程式。<br>"

    if problem_subtype == 'quantity':
        sub_question = f"⑴ 兩種共買了 ${total_qty}$ {unit}。"
        correct_answer = f"x+y={total_qty}"
    else:
        sub_question = f"⑵ 總共花了 ${total_cost}$ 元。"
        p1_str = "" if price1 == 1 else str(price1)
        p2_str = "" if price2 == 1 else str(price2)
        correct_answer = f"{p1_str}x+{p2_str}y={total_cost}"

    question_text = question_base + sub_question + "<br>(請以 $x, y$ 表示，並寫成如 $3x+5y=15$ 的形式)"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_verify_solution_problem():
    a = random.randint(1, 5) * random.choice([-1, 1])
    b = random.randint(1, 5) * random.choice([-1, 1])
    x0 = random.randint(-5, 5)
    y0 = random.randint(-5, 5)
    c = a * x0 + b * y0

    is_correct_case = random.choice([True, False])

    if is_correct_case:
        xt, yt = x0, y0
        correct_answer = "是"
    else:
        xt = x0 + random.choice([-2, -1, 1, 2])
        yt = y0
        if random.random() < 0.5:
             yt = y0 + random.choice([-2, -1, 1, 2])
        if xt == x0 and yt == y0: # Ensure it's not accidentally correct
            xt += 1
        correct_answer = "否"

    equation_str = _format_equation(a, b, c)
    question_text = f"判斷 $x={xt}$、$y={yt}$ 是否為二元一次方程式 ${equation_str}$ 的解？ (請填 是 或 否)"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_find_y_given_x_problem():
    a = random.randint(2, 7)
    b = random.choice([-1, 1])  # Guarantees integer solution for y
    x_given = random.randint(-10, 10)
    y_ans = random.randint(-10, 10)
    c = a * x_given + b * y_ans

    equation_str = _format_equation(a, b, c)
    question_text = f"若二元一次方程式 ${equation_str}$，當 $x={x_given}$ 時，$y$ 的值為何？"
    correct_answer = str(y_ans)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_count_non_negative_integer_solutions_problem():
    a = random.randint(2, 8)
    b = random.randint(2, 8)
    while a == b or math.gcd(a, b) != 1:
        b = random.randint(2, 8)

    num_solutions = random.randint(3, 5)
    k = num_solutions - 1
    c = k * a * b

    items = random.choice([("彈珠糖", "牛奶糖", "顆"), ("雞蛋糕", "紅豆餅", "個"), ("鉛筆", "原子筆", "枝")])
    item1, item2, unit = items

    question_text = f"小盈到柑仔店想買{item1}及{item2}兩種零食，已知{item1} 1 {unit} ${a}$ 元、{item2} 1 {unit} ${b}$ 元，若他共消費了 ${c}$ 元，且零食可只買一種，則他有幾種可能的買法？"
    correct_answer = str(num_solutions)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip().upper()
    correct_answer = correct_answer.strip().upper()
    
    # For equation type problems, we need a more robust check.
    # However, for this generator, we will stick to strict string comparison.
    # A simple normalization for equations could be removing spaces.
    user_answer = user_answer.replace(" ", "")
    correct_answer = correct_answer.replace(" ", "")
    
    is_correct = (user_answer == correct_answer)
    
    if not is_correct:
        try:
            if float(user_answer) == float(correct_answer):
                is_correct = True
        except ValueError:
            pass

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}
