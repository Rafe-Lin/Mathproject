import random
import math

# --- Helper Functions ---

def simplify_sqrt(n):
    """
    Simplifies a square root into the form a * sqrt(b).
    Returns a tuple (a, b).
    Example: simplify_sqrt(75) -> (5, 3)
    """
    if not isinstance(n, int) or n < 0:
        raise ValueError("Input must be a non-negative integer.")
    if n == 0:
        return 0, 0
    
    largest_square_factor = 1
    i = int(math.sqrt(n))
    while i > 1:
        if n % (i * i) == 0:
            largest_square_factor = i * i
            break
        i -= 1
        
    a = int(math.sqrt(largest_square_factor))
    b = n // largest_square_factor
    return a, b

def format_sqrt(outside, inside):
    """
    Formats the (a, b) tuple from simplify_sqrt into a LaTeX string.
    """
    if inside == 0 or outside == 0:
        return "0"
    if inside == 1:
        return str(outside)
    if outside == 1:
        return f"\\sqrt{{{inside}}}"
    return f"{outside}\\sqrt{{{inside}}}"

# Store triples as (smaller_leg, larger_leg, hypotenuse) to simplify application problems
PYTHAGOREAN_TRIPLES = [
    (3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25),
    (9, 40, 41), (20, 21, 29), (12, 35, 37)
]

# --- Main Generation Function ---

def generate(level=1):
    """
    生成「弦與弦心距」相關題目。
    包含：
    1. 已知半徑、弦心距，求弦長。
    2. 已知弦長、弦心距，求半徑。
    3. 兩弦問題：利用一弦資訊求半徑，再求另一弦的未知量。
    4. 應用問題：隧道、圓拱橋等截面問題。
    """
    # For this skill, difficulty is similar across types, so level is not used.
    problem_type = random.choice([
        'find_chord',
        'find_radius',
        'two_chords',
        'application'
    ])

    if problem_type == 'find_chord':
        return generate_find_chord_problem()
    elif problem_type == 'find_radius':
        return generate_find_radius_problem()
    elif problem_type == 'two_chords':
        return generate_two_chords_problem()
    else:  # application
        return generate_application_problem()

# --- Problem Type Generators ---

def generate_find_chord_problem():
    """
    題型：已知半徑、弦心距，求弦長。 (參考例題2)
    """
    triple = random.choice(PYTHAGOREAN_TRIPLES)
    k = random.randint(1, 4)
    a, b, c = [k * x for x in triple]  # a is smaller leg, b is larger leg

    radius = c
    # chord distance can be a or b
    distance = random.choice([a, b])

    if distance == a:
        half_chord = b
    else:
        half_chord = a

    chord_length = 2 * half_chord
    units = random.choice(["公分", "公尺", "cm"])

    question_text = f"在一個半徑為 ${radius}$ {units}的圓中，若有一弦的弦心距為 ${distance}$ {units}，則此弦的長度為多少{units}？"
    correct_answer = str(chord_length)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_find_radius_problem():
    """
    題型：已知弦長、弦心距，求半徑。 (例題2的變化題)
    """
    triple = random.choice(PYTHAGOREAN_TRIPLES)
    k = random.randint(1, 4)
    a, b, c = [k * x for x in triple]

    sides = [a, b]
    random.shuffle(sides)
    distance = sides[0]
    half_chord = sides[1]

    chord_length = 2 * half_chord
    radius = c
    units = random.choice(["公分", "公尺", "cm"])

    question_text = f"在一個圓中，若有一長度為 ${chord_length}$ {units}的弦，其弦心距為 ${distance}$ {units}，則此圓的半徑為多少{units}？"
    correct_answer = str(radius)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_two_chords_problem():
    """
    題型：兩弦問題，需先求出半徑。 (參考例題3)
    """
    triple1 = random.choice(PYTHAGOREAN_TRIPLES)
    k = random.randint(1, 3)
    d1, h1, r = [k * x for x in triple1]
    chord1_len = 2 * h1

    # Generate second chord's info
    d2 = random.randint(1, r - 1)
    while d2 == d1 or d2 == h1:  # ensure it's a new distance
        d2 = random.randint(1, r - 1)

    h2_squared = r**2 - d2**2
    out, ins = simplify_sqrt(h2_squared)

    # We want the length of the second chord, which is 2 * h2
    final_out = 2 * out
    correct_answer = format_sqrt(final_out, ins)

    question_text = (f"圓 $O$ 中有兩弦 $\\overline{{AB}}$ 與 $\\overline{{CD}}$，"
                     f"其弦心距分別為 $\\overline{{OM}}$ 與 $\\overline{{ON}}$。"
                     f"已知 $\\overline{{CD}} = {chord1_len}$，"
                     f"$\\overline{{ON}} = {d1}$。"
                     f"若 $\\overline{{OM}} = {d2}$，"
                     f"則 $\\overline{{AB}}$ 的長度為何？")

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_application_problem():
    """
    題型：應用問題，如隧道、圓拱橋等。 (參考例題4, 5)
    """
    triple = random.choice(PYTHAGOREAN_TRIPLES)
    k = random.randint(2, 10)  # scale can be larger for real-world scenarios
    d, w_half, r = [k * x for x in triple]  # d is the smaller leg

    width = 2 * w_half
    # height of the arc segment (distance from chord to arc top)
    height = r - d

    contexts = [
        {"name": "隧道", "width_item": "路面寬度", "height_item": "隧道的最大高度"},
        {"name": "水管屋民宿", "width_item": "內部地板寬度", "height_item": "地板到屋頂的最高高度"},
        {"name": "圓拱橋", "width_item": "橋面寬", "height_item": "橋拱頂點到橋面的高度"},
        {"name": "古老的破裂圓盤", "width_item": "最長弦的長度", "height_item": "該弦的中點到圓弧的垂直距離"}
    ]
    context = random.choice(contexts)
    units = random.choice(["公尺", "公分"])

    question_text = (f"某個{context['name']}的橫切面為一個圓弧。已知其{context['width_item']}為 ${width}$ {units}，"
                     f"且{context['height_item']}為 ${height}$ {units}。"
                     f"試問此圓弧所在圓的半徑為多少{units}？")

    correct_answer = str(r)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

# --- Answer Checking Function ---

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    Handles integer, decimal, and simple LaTeX radical answers.
    """
    user_answer = user_answer.strip().replace(" ", "")
    correct_answer_str = correct_answer.strip().replace(" ", "")

    is_correct = (user_answer.lower() == correct_answer_str.lower())
    
    if not is_correct:
        try:
            # Check for numerical equivalence, e.g., user entered a decimal for a radical answer
            user_val = float(user_answer)
            correct_val = None
            
            if "\\sqrt" in correct_answer_str:
                parts = correct_answer_str.split("\\sqrt")
                coeff_str = parts[0]
                rad_str = parts[1].strip("{}")
                
                coeff = float(coeff_str) if coeff_str else 1.0
                rad = float(rad_str)
                correct_val = coeff * math.sqrt(rad)
            else:
                correct_val = float(correct_answer_str)
            
            if correct_val is not None and math.isclose(user_val, correct_val, rel_tol=1e-2):
                is_correct = True
        except (ValueError, IndexError):
            # Parsing or float conversion failed, rely on initial string comparison
            pass

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}