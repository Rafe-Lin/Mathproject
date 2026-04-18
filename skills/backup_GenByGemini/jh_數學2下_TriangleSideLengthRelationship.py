import random
import math

def generate_check_sets_problem():
    """
    Generates a problem asking which of three sets of side lengths can form a triangle.
    """
    # Create one set that can form a triangle
    s1_ok = random.randint(5, 15)
    s2_ok = random.randint(5, 15)
    lower_ok = abs(s1_ok - s2_ok)
    upper_ok = s1_ok + s2_ok
    # Ensure there's a possible integer side length
    if upper_ok <= lower_ok + 1:
        s1_ok += 2
        lower_ok = abs(s1_ok - s2_ok)
        upper_ok = s1_ok + s2_ok
    s3_ok = random.randint(lower_ok + 1, upper_ok - 1)
    correct_set = sorted([s1_ok, s2_ok, s3_ok])

    # Create one set where a + b = c
    s1_eq = random.randint(5, 15)
    s2_eq = random.randint(5, 15)
    s3_eq = s1_eq + s2_eq
    incorrect_set1 = sorted([s1_eq, s2_eq, s3_eq])
    
    # Ensure this set is different from the correct one
    while incorrect_set1 == correct_set:
        s1_eq = random.randint(5, 15)
        s2_eq = random.randint(5, 15)
        s3_eq = s1_eq + s2_eq
        incorrect_set1 = sorted([s1_eq, s2_eq, s3_eq])


    # Create one set where a + b < c
    s1_lt = random.randint(4, 12)
    s2_lt = random.randint(4, 12)
    s3_lt = s1_lt + s2_lt + random.randint(1, 5)
    incorrect_set2 = sorted([s1_lt, s2_lt, s3_lt])
    
    # Ensure this set is different from the others
    while incorrect_set2 == correct_set or incorrect_set2 == incorrect_set1:
        s1_lt = random.randint(4, 12)
        s2_lt = random.randint(4, 12)
        s3_lt = s1_lt + s2_lt + random.randint(1, 5)
        incorrect_set2 = sorted([s1_lt, s2_lt, s3_lt])

    sets = [correct_set, incorrect_set1, incorrect_set2]
    random.shuffle(sets)

    correct_answer_index = sets.index(correct_set) + 1
    
    options = []
    labels = ["⑴", "⑵", "⑶"]
    for i, s in enumerate(sets):
        options.append(f"{labels[i]} {s[0]}、{s[1]}、{s[2]}")

    question_text = f"下列各組的 3 個數分別代表三線段的長度，哪幾組數可以構成三角形？<br>{'<br>'.join(options)}"
    correct_answer = str(correct_answer_index)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_find_range_problem(use_decimals=False):
    """
    Generates a problem asking for the possible integer lengths of the third side, given two sides.
    """
    if use_decimals:
        a = random.randint(20, 150) / 10.0
        b = random.randint(20, 150) / 10.0
        while a == b:
             b = random.randint(20, 150) / 10.0
    else:
        a = random.randint(2, 20)
        b = random.randint(2, 20)
        while a == b:
            b = random.randint(2, 20)

    lower_bound = abs(a - b)
    upper_bound = a + b

    min_x = math.floor(lower_bound) + 1
    max_x = math.ceil(upper_bound) - 1
    
    possible_integers = list(range(min_x, max_x + 1))
    
    # Ensure there is a solution. If not, regenerate.
    if not possible_integers:
        return generate_find_range_problem(use_decimals)

    correct_answer = ",".join(map(str, possible_integers))
    
    question_text = f"若 ${a}$、${b}$ 是一個三角形的兩邊長，且第三邊的邊長是整數，請列出所有符合條件的第三邊長。(請由小到大，並用逗號分隔)"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_isosceles_check_problem():
    """
    Generates a problem about forming an isosceles triangle given two sides.
    """
    case = random.choice(['only_A', 'only_B', 'both'])
    
    if case == 'only_B':
        # Sides are a, 2a. Check third side as a or 2a.
        # (a,a,2a) -> a+a = 2a (No)
        # (a,2a,2a) -> a+2a > 2a (Yes)
        s1 = random.randint(3, 10)
        s2 = 2 * s1
        correct_answer = "只有乙正確"
    elif case == 'only_A':
        # Sides are 2b, b. Check third side as 2b or b.
        # (2b,b,2b) -> b+2b > 2b (Yes)
        # (2b,b,b) -> b+b = 2b (No)
        s2 = random.randint(3, 10)
        s1 = 2 * s2
        correct_answer = "只有甲正確"
    else: # 'both'
        # Sides a, b where a < b < 2a
        # (a,b,a) -> a+a > b (Yes)
        # (a,b,b) -> a+b > b (Yes)
        s1 = random.randint(5, 10)
        s2 = random.randint(s1 + 1, 2 * s1 - 1)
        correct_answer = "甲、乙皆正確"
    
    # Randomly swap s1 and s2 to vary the presentation
    if random.random() < 0.5:
        s1, s2 = s2, s1
        if case == 'only_A': correct_answer = "只有乙正確"
        elif case == 'only_B': correct_answer = "只有甲正確"
        
    question_text = (
        f"已知有長 ${s1}$ 公分、${s2}$ 公分的兩線段，下列甲、乙的敘述何者正確？<br>"
        f"甲：若另有一長為 ${s1}$ 公分的線段，則此三線段可構成等腰三角形。<br>"
        f"乙：若另有一長為 ${s2}$ 公分的線段，則此三線段可構成等腰三角形。"
    )
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_diagonal_range_problem():
    """
    Generates a problem about the possible integer length of a diagonal in a quadrilateral.
    """
    while True:
        ab = random.randint(5, 30)
        bc = random.randint(5, 30)
        cd = random.randint(5, 30)
        ad = random.randint(5, 30)

        # Range from triangle ABC
        lower1 = abs(ab - bc)
        upper1 = ab + bc
        
        # Range from triangle ADC
        lower2 = abs(ad - cd)
        upper2 = ad + cd

        # Intersection of the two ranges
        final_lower = max(lower1, lower2)
        final_upper = min(upper1, upper2)
        
        # Ensure there is at least one integer in the range to form a valid question
        if final_upper > final_lower + 1:
            break

    min_ac = math.floor(final_lower) + 1
    max_ac = math.ceil(final_upper) - 1

    q_type = random.choice(['max', 'min', 'both'])
    
    base_question = f"四邊形 ABCD 中，已知 $\\overline{{AB}}=${ab}$、$\\overline{{BC}}=${bc}$、$\\overline{{CD}}=${cd}$、$\\overline{{AD}}=${ad}$，若對角線 $\\overline{{AC}}$ 的長度為整數，"
    
    if q_type == 'max':
        question_text = base_question + "則 $\\overline{AC}$ 的最大值為何？"
        correct_answer = str(max_ac)
    elif q_type == 'min':
        question_text = base_question + "則 $\\overline{AC}$ 的最小值為何？"
        correct_answer = str(min_ac)
    else: # 'both'
        question_text = base_question + "則 $\\overline{AC}$ 的最大值與最小值分別為多少？(請用逗號分隔最大值,最小值)"
        correct_answer = f"{max_ac},{min_ac}"
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    Generates a problem about the triangle side length relationship.
    
    Level 1: Basic checks (can it form a triangle?) and integer side ranges.
    Level 2: More complex checks (isosceles) and decimal side ranges.
    Level 3: Application problems (quadrilateral diagonal).
    """
    if level == 1:
        problem_type = random.choice(['check_sets', 'find_range_int'])
    elif level == 2:
        problem_type = random.choice(['isosceles_check', 'find_range_dec'])
    else: # level 3
        problem_type = 'diagonal_range'

    if problem_type == 'check_sets':
        return generate_check_sets_problem()
    elif problem_type == 'find_range_int':
        return generate_find_range_problem(use_decimals=False)
    elif problem_type == 'find_range_dec':
        return generate_find_range_problem(use_decimals=True)
    elif problem_type == 'isosceles_check':
        return generate_isosceles_check_problem()
    else: # diagonal_range
        return generate_diagonal_range_problem()

def check(user_answer, correct_answer):
    """
    Checks if the user's answer is correct.
    Handles single numbers, lists of numbers, and text answers.
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    is_correct = False
    
    # Try to parse as list of numbers first (covers single numbers too)
    try:
        user_parts = sorted([int(x.strip()) for x in user_answer.replace('，', ',').split(',')])
        correct_parts = sorted([int(x.strip()) for x in correct_answer.replace('，', ',').split(',')])
        if user_parts == correct_parts:
            is_correct = True
    except (ValueError, AttributeError):
        # Fallback to string comparison for non-numeric answers
        # Also normalizes answers like '⑴' to '1'
        user_answer_norm = user_answer.upper().replace('(', '').replace(')', '')
        user_answer_norm = user_answer_norm.replace('⑴', '1').replace('⑵', '2').replace('⑶', '3')
        
        correct_answer_norm = correct_answer.upper().replace('(', '').replace(')', '')
        correct_answer_norm = correct_answer_norm.replace('⑴', '1').replace('⑵', '2').replace('⑶', '3')

        if user_answer_norm == correct_answer_norm:
            is_correct = True

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}