import random
import math

def generate(level=1):
    """
    Generates questions about the properties of trapezoids.
    The skill ID is jh_數學2下_PropertiesOfTrapezoids.
    """
    problem_types = [
        'median_segment_length', 
        'area_from_median', 
        'base_from_median', 
        'isosceles_angles',
        'isosceles_diagonal',
        'identify_isosceles'
    ]
    # More complex problems for higher levels, like those involving radicals
    if level > 1:
        problem_types.append('isosceles_diagonal_45deg')
        
    problem_type = random.choice(problem_types)

    if problem_type == 'median_segment_length':
        return generate_median_segment_length_problem()
    elif problem_type == 'area_from_median':
        return generate_area_from_median_problem()
    elif problem_type == 'base_from_median':
        return generate_base_from_median_problem()
    elif problem_type == 'isosceles_angles':
        return generate_isosceles_angles_problem()
    elif problem_type == 'isosceles_diagonal':
        return generate_isosceles_diagonal_problem()
    elif problem_type == 'isosceles_diagonal_45deg':
        return generate_isosceles_diagonal_45deg_problem()
    elif problem_type == 'identify_isosceles':
        return generate_identify_isosceles_problem()

def simplify_sqrt(n):
    """
    Simplifies a square root into the form a*sqrt(b).
    Returns a string formatted for LaTeX.
    """
    if n < 0:
        raise ValueError("Input must be non-negative")
    if n == 0:
        return "0"
    
    i = int(math.sqrt(n))
    if i * i == n:
        return str(i)

    limit = int(math.sqrt(n))
    largest_square_factor = 1
    for x in range(limit, 1, -1):
        if n % (x * x) == 0:
            largest_square_factor = x * x
            break
            
    if largest_square_factor == 1:
        return f"\\sqrt{{{n}}}"
    else:
        coeff = int(math.sqrt(largest_square_factor))
        radicand = n // largest_square_factor
        if radicand == 1:
             return str(coeff)
        return f"{coeff}\\sqrt{{{radicand}}}"

def generate_median_segment_length_problem():
    """
    Generates a problem asking for the length of a segment dividing the non-parallel sides.
    Based on Reference Example 1.
    """
    ad = random.randint(5, 15)
    # Ensure bc > ad and their sum is even for an integer or .5 median
    bc = ad + random.randint(3, 10) * 2
    
    fi = (ad + bc) / 2
    eh = (ad + fi) / 2
    gj = (fi + bc) / 2
    
    segments = {'EH': eh, 'FI': fi, 'GJ': gj}
    target_segment = random.choice(list(segments.keys()))
    
    answer = segments[target_segment]
    
    # Format answer to be integer if possible
    if answer.is_integer():
        answer_str = str(int(answer))
    else:
        answer_str = str(answer)

    question_text = (
        f"如右圖，梯形 ABCD 中，$AD // BC$，E、F、G 將 AB 四等分，H、I、J 將 DC 四等分。<br>"
        f"若 $AD={ad}$cm，$BC={bc}$cm，則 ${target_segment}$ 的長度為多少 cm？"
    )
    
    return {
        "question_text": question_text,
        "answer": answer_str,
        "correct_answer": answer_str
    }

def generate_area_from_median_problem():
    """
    Generates a problem to calculate the area from the median and height.
    Based on Reference Example 3.
    """
    median = random.randint(8, 25)
    height = random.randint(4, 12)
    area = median * height
    
    question_text = f"有一梯形兩腰中點的連線段長為 ${median}$ 公分，高為 ${height}$ 公分，求此梯形面積為多少平方公分？"
    
    return {
        "question_text": question_text,
        "answer": str(area),
        "correct_answer": str(area)
    }

def generate_base_from_median_problem():
    """
    Generates a problem to find a base given the other base and the median.
    Based on Reference Example 2.
    """
    base1 = random.randint(4, 15)
    # Ensure median is larger than base1
    median = base1 + random.randint(2, 10)
    base2 = 2 * median - base1
    
    question_text = f"梯形 ABCD 中，$AD // BC$，$EF$ 為兩腰中點的連線段。若 $AD={base1}$cm，$EF={median}$cm，則底邊 $BC$ 的長度為多少 cm？"
    
    return {
        "question_text": question_text,
        "answer": str(base2),
        "correct_answer": str(base2)
    }

def generate_isosceles_angles_problem():
    """
    Generates a problem about angle calculations in an isosceles trapezoid.
    Based on Reference Example 4.
    """
    angle_a = random.randint(95, 150)
    angle_d = angle_a
    angle_b = 180 - angle_a
    angle_c = angle_b

    q_type = random.choice(['sum_upper', 'given_upper', 'given_lower'])
    
    if q_type == 'sum_upper':
        sum_ad = angle_a + angle_d
        question_text = f"等腰梯形 ABCD 中，$AD // BC$。若 $\\angle A + \\angle D = {sum_ad}^\\circ$，求 $\\angle B$ 的度數。"
        answer = angle_b
    elif q_type == 'given_upper':
        question_text = f"等腰梯形 ABCD 中，$AD // BC$。若 $\\angle D = {angle_d}^\\circ$，求 $\\angle C$ 的度數。"
        answer = angle_c
    else: # given_lower
        question_text = f"等腰梯形 ABCD 中，$AD // BC$。若 $\\angle B = {angle_b}^\\circ$，求 $\\angle D$ 的度數。"
        answer = angle_d
        
    return {
        "question_text": question_text,
        "answer": str(answer),
        "correct_answer": str(answer)
    }

def generate_isosceles_diagonal_problem():
    """
    Generates a problem to calculate the diagonal length using the Pythagorean theorem.
    Based on Reference Example 5.
    """
    triples = [(3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25), (6, 8, 10)]
    p_triple = random.choice(triples)
    
    scale = random.randint(1, 2)
    a, b, c = [x * scale for x in p_triple]
    
    leg1, leg2 = sorted(random.sample([a, b], 2))
    diag = c
    
    h = leg1
    base_long_minus_x = leg2
    
    # Ensure x > 0 and base_short > 0
    x = random.randint(1, base_long_minus_x - 1)
    
    base_long = base_long_minus_x + x
    base_short = base_long - 2 * x

    question_text = f"等腰梯形 ABCD 中，$AD // BC$。若上底 $AD={base_short}$、下底 $BC={base_long}$、高為 ${h}$，則此梯形的對角線長度為多少？"
    
    return {
        "question_text": question_text,
        "answer": str(diag),
        "correct_answer": str(diag)
    }

def generate_isosceles_diagonal_45deg_problem():
    """
    Generates a problem to calculate the diagonal length with a 45-degree angle.
    Based on Reference Example 7.
    """
    base_short = random.randint(3, 10)
    # In a 45-deg isosceles trapezoid, height h = x where x = (base_long - base_short) / 2
    x = random.randint(2, 6)
    h = x
    base_long = base_short + 2 * x
    
    # Calculate diagonal AC. The right triangle is AEC. Legs are AE = h and EC = base_long - x
    leg_ae = h
    leg_ec = base_long - x
    
    ac_squared = leg_ae**2 + leg_ec**2
    answer = simplify_sqrt(ac_squared)
    
    question_text = (
        f"等腰梯形 ABCD 中，$AD // BC$。"
        f"若 $AD={base_short}$cm，$BC={base_long}$cm，且 $\\angle B=45^\\circ$，"
        f"則對角線 AC 的長度為多少 cm？（答案請以最簡根式表示）"
    )
    
    return {
        "question_text": question_text,
        "answer": answer,
        "correct_answer": answer
    }
    
def generate_identify_isosceles_problem():
    """
    Generates a problem to identify an isosceles trapezoid from a list of angles.
    Based on Reference Example 8.
    """
    options = []
    correct_option_angles = tuple()
    labels = ['甲', '乙', '丙', '丁']
    
    # Generate one correct isosceles trapezoid (AD // BC, angle B = angle C)
    b = random.randint(50, 85)
    a = 180 - b
    correct_option_angles = (a, b, b, a)
    options.append(correct_option_angles)

    # Distractor 1: Parallelogram (non-rectangle)
    b_p = random.randint(50, 85)
    a_p = 180 - b_p
    options.append((a_p, b_p, a_p, b_p))
    
    # Distractor 2: Non-isosceles trapezoid
    b_t = random.randint(50, 80)
    c_t = random.randint(b_t + 5, 95)
    a_t = 180 - b_t
    d_t = 180 - c_t
    options.append((a_t, b_t, c_t, d_t))

    # Distractor 3: General quadrilateral
    a_g, b_g = random.sample(range(70, 100), 2)
    c_g = random.randint(101, 120)
    d_g = 360 - (a_g + b_g + c_g)
    options.append((a_g, b_g, c_g, d_g))

    random.shuffle(options)
    
    question_lines = ["已知有四個四邊形，將它們的四個內角依 $\\angle A、\\angle B、\\angle C、\\angle D$ 的順序寫在下面，則哪一個選項必定是等腰梯形？"]
    correct_label = ""
    for i, angles in enumerate(options):
        label = labels[i]
        if angles == correct_option_angles:
            correct_label = label
        
        angle_str = '°、'.join(map(str, angles)) + '°'
        question_lines.append(f"{label}：${angle_str}$")
        
    question_text = "<br>".join(question_lines)
    
    return {
        "question_text": question_text,
        "answer": correct_label,
        "correct_answer": correct_label
    }

def check(user_answer, correct_answer):
    """
    Checks if the user's answer is correct.
    """
    user_answer_norm = user_answer.strip().replace(" ", "")
    correct_answer_norm = correct_answer.strip().replace(" ", "")

    is_correct = (user_answer_norm.upper() == correct_answer_norm.upper())
    
    if not is_correct and "\\" not in correct_answer_norm:
        try:
            # For numerical answers, compare as floats to handle e.g., 15 vs 15.0
            if abs(float(user_answer_norm) - float(correct_answer_norm)) < 1e-9:
                is_correct = True
        except (ValueError, TypeError):
            pass

    # Correctly escape backslashes for LaTeX rendering in the feedback string
    correct_answer_display = correct_answer.replace('\\', '\\\\')
    
    if is_correct:
        result_text = f"完全正確！答案是 ${correct_answer_display}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer_display}$"

    return {"correct": is_correct, "result": result_text, "next_question": True}