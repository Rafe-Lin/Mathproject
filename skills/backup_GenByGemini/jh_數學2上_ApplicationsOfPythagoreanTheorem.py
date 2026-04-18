import random
import math
from fractions import Fraction

def simplify_sqrt(n):
    """
    Simplifies a square root to the form a*sqrt(b).
    Returns the simplified string representation for LaTeX.
    Example: simplify_sqrt(45) -> "3\\sqrt{5}"
    Example: simplify_sqrt(16) -> "4"
    """
    if n < 0:
        raise ValueError("Input must be non-negative")
    if n == 0:
        return "0"

    i = int(math.sqrt(n))
    while i > 1:
        if n % (i * i) == 0:
            coeff = i
            radicand = n // (i * i)
            if radicand == 1:
                return str(coeff)
            else:
                return f"{coeff}\\sqrt{{{radicand}}}"
        i -= 1

    # No perfect square factor found (other than 1)
    if n == 1:
        return "1"
    return f"\\sqrt{{{n}}}"


def generate_altitude_on_hypotenuse():
    """
    Generates a problem about finding the altitude on the hypotenuse of a right triangle.
    """
    triples = [(3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25)]
    base_triple = random.choice(triples)
    k = random.randint(1, 4)

    leg1, leg2, hypotenuse = [k * x for x in base_triple]

    # Randomly assign legs to AB and BC
    if random.random() < 0.5:
        ab, bc = leg1, leg2
    else:
        ab, bc = leg2, leg1

    altitude_frac = Fraction(ab * bc, hypotenuse)
    if altitude_frac.denominator == 1:
        altitude_str = str(altitude_frac.numerator)
    else:
        altitude_str = f"\\frac{{{altitude_frac.numerator}}}{{{altitude_frac.denominator}}}"

    question_text = (
        f"如圖，一個直角三角形兩股長分別為 ${ab}$ 與 ${bc}$，求：<br>"
        "⑴ 斜邊的長度為多少？<br>"
        "⑵ 斜邊上的高為多少？<br>"
        "(答案請依序作答，並用逗號分隔，分數請以最簡分數表示)"
    )
    correct_answer = f"{hypotenuse}, {altitude_str}"
    # The answer key for checking will not have latex commands
    answer_key = f"{hypotenuse}, {altitude_frac.numerator}/{altitude_frac.denominator}" if altitude_frac.denominator != 1 else f"{hypotenuse}, {altitude_frac.numerator}"


    return {
        "question_text": question_text,
        "answer": answer_key,
        "correct_answer": correct_answer
    }


def generate_isosceles_triangle():
    """
    Generates a problem about the height and area of an isosceles triangle.
    """
    triples = [(3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25)]
    # Use triples where 'a' is height, 'b' is half-base, 'c' is equal side
    height_part, half_base_part, side_part = random.choice(triples)
    k = random.randint(1, 5)

    equal_side = k * side_part
    base = 2 * k * half_base_part
    height = k * height_part
    area = int(0.5 * base * height)

    question_text = (
        f"已知一個等腰三角形的腰長為 ${equal_side}$，底邊長為 ${base}$，求：<br>"
        "⑴ 底邊上的高為多少？<br>"
        "⑵ 此等腰三角形的面積為何？<br>"
        "(答案請依序作答，並用逗號分隔)"
    )
    correct_answer = f"{height}, {area}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def generate_equilateral_triangle():
    """
    Generates a problem about the height and area of an equilateral triangle.
    """
    side = random.randint(2, 12) * 2  # Use even numbers for cleaner results
    height_coeff = side // 2
    area_coeff = (side ** 2) // 4

    height_str = f"{height_coeff}\\sqrt{{3}}"
    area_str = f"{area_coeff}\\sqrt{{3}}"

    question_text = (
        f"已知一個正三角形的邊長為 ${side}$，求此正三角形的高與面積分別為多少？<br>"
        "(答案請依序作答，並用逗號分隔，例如：$1\\sqrt{{3}}, 2\\sqrt{{3}}$)"
    )
    correct_answer = f"{height_str}, {area_str}"
    
    # User might not type the LaTeX, so the key is for matching.
    answer_key = f"{height_coeff}sqrt(3), {area_coeff}sqrt(3)"

    return {
        "question_text": question_text,
        "answer": answer_key,
        "correct_answer": correct_answer
    }


def generate_rectangle_diagonal():
    """
    Generates a problem about finding the diagonal of a rectangle.
    """
    contexts = [
        ("一個長方形的球場", "公尺"),
        ("一張長方形的畫紙", "公分"),
        ("一個電視螢幕", "吋")
    ]
    context, unit = random.choice(contexts)
    l = random.randint(3, 20)
    w = random.randint(3, 20)
    while l == w:
        w = random.randint(3, 20)

    diagonal_sq = l*l + w*w
    diagonal_str = simplify_sqrt(diagonal_sq)
    
    # Answer key for checking
    if "\\sqrt" in diagonal_str:
        answer_key = diagonal_str.replace("\\sqrt{", "sqrt(").replace("}",")")
    else:
        answer_key = diagonal_str

    question_text = (
        f"{context}長為 ${l}$ {unit}，寬為 ${w}$ {unit}，其對角線長度為多少{unit}？<br>"
        "(答案請化為最簡根式，例如：$5\\sqrt{{2}}$)"
    )
    
    return {
        "question_text": question_text,
        "answer": answer_key,
        "correct_answer": diagonal_str
    }


def generate_ladder_problem():
    """
    Generates a problem about a sliding ladder.
    """
    ladders = [
        (25, (7, 24), (15, 20)),
        (50, (14, 48), (30, 40)),
        (65, (25, 60), (39, 52)),
        (85, (36, 77), (40, 75))
    ]
    length, state1, state2 = random.choice(ladders)
    
    # Randomly choose initial state
    states = [state1, state2]
    random.shuffle(states)
    (d1, h1), (d2, h2) = states

    # Determine movement direction
    if d2 > d1:
        horiz_dir = "向外"
        vert_dir = "下滑"
    else:
        horiz_dir = "向內"
        vert_dir = "上滑"

    horiz_move = abs(d1 - d2)
    vert_move = abs(h1 - h2)
    
    problem_type = random.choice(['find_height', 'find_slide'])
    
    if problem_type == 'find_height':
        question_text = (
            f"一支長 ${length}$ 公尺的梯子斜靠在一面垂直的牆上，"
            f"若梯腳距離牆底 ${d1}$ 公尺，則此時梯頂距離地面多少公尺？"
        )
        correct_answer = str(h1)
        return {
            "question_text": question_text,
            "answer": correct_answer,
            "correct_answer": correct_answer
        }
    else: # find_slide
        question_text = (
            f"一支長 ${length}$ 公尺的梯子斜靠在一面垂直的牆上，"
            f"起初梯頂距離地面 ${h1}$ 公尺。若將梯腳{horiz_dir}移動 ${horiz_move}$ 公尺，"
            f"則梯頂會{vert_dir}多少公尺？"
        )
        correct_answer = str(vert_move)
        return {
            "question_text": question_text,
            "answer": correct_answer,
            "correct_answer": correct_answer
        }


def generate(level=1):
    """
    Generates a problem for 'Applications of Pythagorean Theorem'.
    """
    problem_type = random.choice([
        'altitude_on_hypotenuse',
        'isosceles_triangle',
        'equilateral_triangle',
        'rectangle_diagonal',
        'ladder_problem'
    ])

    if problem_type == 'altitude_on_hypotenuse':
        return generate_altitude_on_hypotenuse()
    elif problem_type == 'isosceles_triangle':
        return generate_isosceles_triangle()
    elif problem_type == 'equilateral_triangle':
        return generate_equilateral_triangle()
    elif problem_type == 'rectangle_diagonal':
        return generate_rectangle_diagonal()
    else: # ladder_problem
        return generate_ladder_problem()


def check(user_answer, correct_answer):
    """
    Checks if the user's answer is correct.
    `correct_answer` is the key for checking logic, not for display.
    The function should refer to the 'correct_answer' field from the generate function for display.
    Here, the template passes the 'answer' field as correct_answer.
    """
    # Normalize user input
    user_ans_cleaned = user_answer.strip().replace(" ", "").replace("，", ",").lower()
    user_ans_cleaned = user_ans_cleaned.replace("sqrt(", "sqrt").replace(")", "")
    
    # Normalize correct answer key
    correct_ans_cleaned = correct_answer.strip().replace(" ", "").lower()
    correct_ans_cleaned = correct_ans_cleaned.replace("sqrt(", "sqrt").replace(")", "")
    
    is_correct = (user_ans_cleaned == correct_ans_cleaned)

    # Allow for fraction vs decimal equivalence if it's a simple number
    if not is_correct:
        try:
            parts_user = user_ans_cleaned.split(',')
            parts_correct = correct_ans_cleaned.split(',')
            if len(parts_user) == len(parts_correct):
                all_match = True
                for u_part, c_part in zip(parts_user, parts_correct):
                    # Evaluate fractions like "120/13"
                    val_u = float(Fraction(u_part))
                    val_c = float(Fraction(c_part))
                    if not math.isclose(val_u, val_c):
                        all_match = False
                        break
                if all_match:
                    is_correct = True
        except (ValueError, ZeroDivisionError):
            pass # Not a simple number or fraction, rely on string match

    # The feedback text should use the pretty LaTeX version, which we assume is what the user wants to see.
    # The `generate` function returns both a checkable `answer` and a displayable `correct_answer`.
    # However, this check function only gets the checkable one. We'll have to re-format it for display.
    # This is a limitation of the template. For now, we'll just show the simplified answer.
    
    # Re-format the correct_answer for display
    display_answer = correct_answer.replace("sqrt(", "\\sqrt{").replace(")", "}")
    
    if "/" in display_answer and "," not in display_answer: # It's a single fraction
        try:
            num, den = display_answer.split('/')
            display_answer = f"\\frac{{{num}}}{{{den}}}"
        except:
            pass
    elif "/" in display_answer and "," in display_answer: # It's a list with a fraction
        parts = display_answer.split(',')
        new_parts = []
        for part in parts:
            if "/" in part:
                 try:
                    num, den = part.split('/')
                    new_parts.append(f"\\frac{{{num}}}{{{den}}}")
                 except:
                    new_parts.append(part)
            else:
                new_parts.append(part)
        display_answer = ", ".join(new_parts)

    result_text = f"完全正確！答案是 ${display_answer}$。" if is_correct else f"答案不正確。正確答案應為：${display_answer}$"
    
    return {"correct": is_correct, "result": result_text, "next_question": True}