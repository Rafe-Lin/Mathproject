import random
import math
from fractions import Fraction

# Helper function for calculating Euclidean distance between two points
def distance(p1, p2):
    """Calculates the Euclidean distance between two 2D points."""
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

# Helper function to generate parameters for an ellipse centered at (0,0) with foci on the x-axis.
# Uses Pythagorean triples to ensure 'a', 'b', 'c' are integers, leading to clean distances.
def get_ellipse_params():
    """
    Generates integer ellipse parameters (a, b, c) and focal coordinates (F1, F2).
    Foci are on the x-axis, centered at the origin.
    'a' is half the major axis length, 'b' is half the minor axis length,
    'c' is half the focal distance. Relationship: a^2 = b^2 + c^2.
    """
    # Use Pythagorean triples (leg1, leg2, hypotenuse) for (c, b, a)
    triples = [
        (3, 4, 5),    # c=3, b=4, a=5
        (4, 3, 5),    # c=4, b=3, a=5 (swapped b and c for variety in axis lengths)
        (5, 12, 13),
        (12, 5, 13),
        (8, 15, 17),
        (15, 8, 17),
        (7, 24, 25),
        (24, 7, 25)
    ]
    
    c_base, b_base, a_base = random.choice(triples)
    
    # Randomly scale the triple to get different, larger integer values
    scale = random.randint(1, 2)
    a = a_base * scale
    b = b_base * scale
    c = c_base * scale
    
    f1 = (c, 0)
    f2 = (-c, 0)
    
    return f1, f2, a, b, c

def generate_ellipse_point_check_problem(level):
    """
    Generates a problem where the user must identify which point lies on a given ellipse.
    Similar to example 1.
    """
    f1, f2, a, b, c = get_ellipse_params()
    
    # Decide which point is the "known" point P (e.g., a vertex)
    # And which is the *other* correct candidate point (another vertex)
    if random.choice([True, False]):
        # P is a minor vertex (0, +/-b), correct candidate is a major vertex (+/-a, 0)
        p_known = (0, b) if random.choice([True, False]) else (0, -b)
        correct_candidate_coords = (a, 0) if random.choice([True, False]) else (-a, 0)
    else:
        # P is a major vertex (+/-a, 0), correct candidate is a minor vertex (0, +/-b)
        p_known = (a, 0) if random.choice([True, False]) else (-a, 0)
        correct_candidate_coords = (0, b) if random.choice([True, False]) else (0, -b)
        
    # The sum of distances to foci for any point on the ellipse is 2a (the major axis length).
    two_a_sum = 2 * a
    
    candidates = {}
    
    # Assign unique labels for P and the correct candidate
    all_labels = ['A', 'B', 'C', 'D', 'E']
    random.shuffle(all_labels)
    
    p_label = all_labels.pop(0)
    correct_candidate_label = all_labels.pop(0)
    
    candidates[p_label] = p_known
    candidates[correct_candidate_label] = correct_candidate_coords
    
    # Generate 1 or 2 incorrect candidate points
    num_incorrect = random.randint(1, 2)
    for _ in range(num_incorrect):
        label = all_labels.pop(0)
        
        # Generate an incorrect point by slightly shifting a known vertex
        base_point_type = random.choice(['major', 'minor'])
        if base_point_type == 'major':
            base_point = (a, 0) if random.choice([True, False]) else (-a, 0)
        else: # 'minor'
            base_point = (0, b) if random.choice([True, False]) else (0, -b)
        
        shift_x = random.choice([-1, 1]) * random.randint(1, 2)
        shift_y = random.choice([-1, 1]) * random.randint(1, 2)
        
        incorrect_coords = (base_point[0] + shift_x, base_point[1] + shift_y)
        
        # Ensure the generated incorrect point is truly off the ellipse and not a duplicate
        while abs(distance(incorrect_coords, f1) + distance(incorrect_coords, f2) - two_a_sum) < 1e-6 \
              or incorrect_coords in candidates.values():
            shift_x = random.choice([-1, 1]) * random.randint(1, 3)
            shift_y = random.choice([-1, 1]) * random.randint(1, 3)
            incorrect_coords = (base_point[0] + shift_x, base_point[1] + shift_y)
            
        candidates[label] = incorrect_coords
    
    foci_desc = f"$F_1({f1[0]}, {f1[1]})$、$F_2({f2[0]}, {f2[1]})$"
    
    candidate_descs = []
    # Sort candidates by label for consistent display
    sorted_labels = sorted(candidates.keys())
    for label in sorted_labels:
        coord = candidates[label]
        candidate_descs.append(f"${label}({coord[0]}, {coord[1]})$")
        
    all_points_str = ', '.join(candidate_descs)
    
    question_text = (
        f"已知一橢圓以 {foci_desc} 為焦點且通過 $P({p_known[0]}, {p_known[1]})$，"
        f"試問下列哪一個點也在此橢圓上？"
        f"<br>點的座標為：{all_points_str}"
    )
    
    correct_answer = correct_candidate_label
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "explanation_data": { # Store data for detailed explanation later
            "f1": f1, "f2": f2, "p_known": p_known,
            "two_a": two_a_sum, "candidates": candidates, "correct_label": correct_candidate_label
        }
    }

def explain_ellipse_point_check(explanation_data):
    """Generates a detailed explanation for the ellipse point check problem."""
    f1 = explanation_data["f1"]
    f2 = explanation_data["f2"]
    p_known = explanation_data["p_known"]
    two_a = explanation_data["two_a"]
    candidates = explanation_data["candidates"]
    correct_label = explanation_data["correct_label"]

    explanation = (
        f"根據橢圓的定義，橢圓上任一點到兩焦點的距離和為定值。"
        f"此定值為橢圓的長軸長 $2a$。"
        f"<br>已知橢圓通過 $P({p_known[0]}, {p_known[1]})$ 且焦點為 $F_1({f1[0]}, {f1[1]})$、$F_2({f2[0]}, {f2[1]})$。"
    )
    
    dist_p_f1 = distance(p_known, f1)
    dist_p_f2 = distance(p_known, f2)
    
    explanation += (
        f"<br>所以橢圓上任一點到兩焦點的距離和（即長軸長 $2a$）為 "
        f"$PF_1 + PF_2 = \\sqrt{{({p_known[0]}-{f1[0]})^2+({p_known[1]}-{f1[1]})^2}} + \\sqrt{{({p_known[0]}-{f2[0]})^2+({p_known[1]}-{f2[1]})^2}}$"
        f"<br>$= {dist_p_f1:.2f} + {dist_p_f2:.2f} = {two_a:.2f}$。"
    )

    # Check each candidate point
    sorted_labels = sorted(candidates.keys())
    for label in sorted_labels:
        cand_coords = candidates[label]
        dist_cand_f1 = distance(cand_coords, f1)
        dist_cand_f2 = distance(cand_coords, f2)
        sum_dist = dist_cand_f1 + dist_cand_f2
        
        explanation += (
            f"<br><br>對於點 ${label}({cand_coords[0]}, {cand_coords[1]})$："
            f"<br>${label}F_1 + {label}F_2 = \\sqrt{{({cand_coords[0]}-{f1[0]})^2+({cand_coords[1]}-{f1[1]})^2}} + \\sqrt{{({cand_coords[0]}-{f2[0]})^2+({cand_coords[1]}-{f2[1]})^2}}$"
            f"<br>$= {dist_cand_f1:.2f} + {dist_cand_f2:.2f} = {sum_dist:.2f}$。"
        )
        # Use a small tolerance for floating point comparison
        if abs(sum_dist - two_a) < 1e-6:
            explanation += f"<br>由於其距離和約為 ${sum_dist:.2f}$，與長軸長 $2a={two_a:.2f}$ 相符，故 ${label}$ 點在此橢圓上。"
        else:
            explanation += f"<br>由於其距離和約為 ${sum_dist:.2f}$，與長軸長 $2a={two_a:.2f}$ 不符，故 ${label}$ 點不在橢圓上。"

    explanation += f"<br><br>因此，${correct_label}$ 點也在此橢圓上。"
    return explanation

def generate_ellipse_properties_problem(level):
    """
    Generates a problem to find a missing ellipse property (2a, 2b, or 2c)
    given two other properties, using the relation a^2 = b^2 + c^2.
    Similar to example 3.
    """
    _, _, a, b, c = get_ellipse_params() # Only need a, b, c values
    
    problem_type_sub = random.choice(['find_2c', 'find_2b', 'find_2a'])
    
    question_text = ""
    correct_answer = ""
    explanation_steps = []
    
    if problem_type_sub == 'find_2c':
        given_2a = 2 * a
        given_2b = 2 * b
        question_text = f"已知一橢圓的長軸長為 ${given_2a}$ 單位，短軸長為 ${given_2b}$ 單位，求該橢圓兩焦點之間的距離。"
        correct_answer = str(2 * c)
        explanation_steps = [
            f"長軸長 $2a={given_2a}$，故 $a={given_2a // 2}$。",
            f"短軸長 $2b={given_2b}$，故 $b={given_2b // 2}$。",
            f"設兩焦點之間的距離為 $2c$。利用橢圓關係式 $a^2=b^2+c^2$，可得 ${a}^2 = {b}^2 + c^2$。",
            f"${a**2} = {b**2} + c^2$",
            f"$c^2 = {a**2} - {b**2} = {a**2 - b**2}$",
            f"$c = \\sqrt{{{a**2 - b**2}}} = {c}$",
            f"故橢圓兩焦點之間的距離為 $2c={2*c}$（單位）。"
        ]
        
    elif problem_type_sub == 'find_2b':
        given_2a = 2 * a
        given_2c = 2 * c
        question_text = f"已知一橢圓的長軸長為 ${given_2a}$ 單位，兩焦點之間的距離為 ${given_2c}$ 單位，求該橢圓的短軸長。"
        correct_answer = str(2 * b)
        explanation_steps = [
            f"長軸長 $2a={given_2a}$，故 $a={given_2a // 2}$。",
            f"兩焦點之間的距離為 $2c={given_2c}$，故 $c={given_2c // 2}$。",
            f"設短軸長為 $2b$。利用橢圓關係式 $a^2=b^2+c^2$，可得 ${a}^2 = b^2 + {c}^2$。",
            f"${a**2} = b^2 + {c**2}$",
            f"$b^2 = {a**2} - {c**2} = {a**2 - c**2}$",
            f"$b = \\sqrt{{{a**2 - c**2}}} = {b}$",
            f"故橢圓的短軸長為 $2b={2*b}$（單位）。"
        ]
        
    else: # 'find_2a'
        given_2b = 2 * b
        given_2c = 2 * c
        question_text = f"已知一橢圓的短軸長為 ${given_2b}$ 單位，兩焦點之間的距離為 ${given_2c}$ 單位，求該橢圓的長軸長。"
        correct_answer = str(2 * a)
        explanation_steps = [
            f"短軸長 $2b={given_2b}$，故 $b={given_2b // 2}$。",
            f"兩焦點之間的距離為 $2c={given_2c}$，故 $c={given_2c // 2}$。",
            f"設長軸長為 $2a$。利用橢圓關係式 $a^2=b^2+c^2$，可得 $a^2 = {b}^2 + {c}^2$。",
            f"$a^2 = {b**2} + {c**2} = {b**2 + c**2}$",
            f"$a = \\sqrt{{{b**2 + c**2}}} = {a}$",
            f"故橢圓的長軸長為 $2a={2*a}$（單位）。"
        ]
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "explanation_data": {"steps": explanation_steps}
    }

def explain_ellipse_properties(explanation_data):
    """Generates a detailed explanation for the ellipse properties problem."""
    return "<br>".join(explanation_data["steps"])

def generate_ellipse_orbit_problem(level):
    """
    Generates a problem related to an elliptical orbit, involving nearest/farthest points
    and the definition of the major axis (2a) and focal distance (2c).
    Similar to example 4 (parts 1 and 2).
    """
    # Generate 'a' and 'c' values, ensuring a > c
    a_val = random.randint(10, 50)
    c_val = random.randint(1, a_val - 5) # Ensure c is significantly smaller than a
    
    # Calculate nearest point distance (pericenter/perihelion) and farthest point distance (apocenter/aphelion)
    near_dist = a_val - c_val
    far_dist = a_val + c_val
    
    question_parts = []
    explanation_steps = []
    correct_answer = ""
    
    # Choose between two sub-problems for level 1
    problem_type_sub = random.choice(['part1_lengths', 'part2_other_focus_dist'])
    
    if problem_type_sub == 'part1_lengths':
        # Ask for long axis length (2a) and focal distance (2c)
        question_parts.append(f"某行星的橢圓軌道以恆星為焦點。當它位於近日點時，距離恆星約為 ${near_dist}$ 天文單位；當它位於遠日點時，距離恆星約為 ${far_dist}$ 天文單位。")
        question_parts.append(f"求此橢圓軌道的長軸長與兩焦點之距離。(請依序回答長軸長和焦點距離，以逗號分隔，不需寫單位)")
        
        ans_2a = 2 * a_val
        ans_2c = 2 * c_val
        correct_answer = f"{ans_2a}, {ans_2c}" # User input example: "80, 10"
        
        explanation_steps = [
            f"設橢圓軌道長軸長為 $2a$，兩焦點的距離為 $2c$。",
            f"由題意可知，近日點距離為 $a-c={near_dist}$，遠日點距離為 $a+c={far_dist}$。",
            f"將兩式相加：$(a-c) + (a+c) = {near_dist} + {far_dist} \\implies 2a = {near_dist + far_dist} = {ans_2a}$。",
            f"將兩式相減：$(a+c) - (a-c) = {far_dist} - {near_dist} \\implies 2c = {far_dist - near_dist} = {ans_2c}$。",
            f"故此橢圓軌道的長軸長為 ${ans_2a}$（天文單位），兩焦點之距離為 ${ans_2c}$（天文單位）。"
        ]
        
    else: # 'part2_other_focus_dist'
        # Ask to express the distance to the other focus given one distance 'x'
        question_parts.append(f"某行星的橢圓軌道以恆星為焦點。當它位於近日點時，距離恆星約為 ${near_dist}$ 天文單位；當它位於遠日點時，距離恆星約為 ${far_dist}$ 天文單位。")
        question_parts.append(f"設該行星與恆星的距離為 $x$，試以 $x$ 表示它與另一個焦點的距離。(不需寫單位)")
        
        # Calculate 2a for the explanation and correct answer
        two_a_val = (near_dist + far_dist)
        correct_answer = f"{two_a_val}-x" # User input example: "80-x"
        
        explanation_steps = [
            f"設橢圓軌道長軸長為 $2a$。",
            f"由題意可知，近日點距離為 $a-c={near_dist}$，遠日點距離為 $a+c={far_dist}$。",
            f"將兩式相加，可得 $2a = (a-c) + (a+c) = {near_dist} + {far_dist} = {two_a_val}$。",
            f"根據橢圓定義，行星到兩焦點的距離和為長軸長 $2a={two_a_val}$。",
            f"若行星與一個焦點的距離為 $x$，則它與另一個焦點的距離為 ${two_a_val}-x$（天文單位）。"
        ]
        
    question_text = "<br>".join(question_parts)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "explanation_data": {"steps": explanation_steps}
    }

def explain_ellipse_orbit(explanation_data):
    """Generates a detailed explanation for the ellipse orbit problem."""
    return "<br>".join(explanation_data["steps"])


def generate(level=1):
    """
    Generates a problem related to the geometric definition and properties of an ellipse.
    Problem types include:
    1. Identifying if a point is on an ellipse given foci and a known point.
    2. Finding an ellipse property (long axis, short axis, or focal distance) from two others.
    3. Solving orbital mechanics problems involving nearest/farthest points.
    """
    problem_type = random.choice([
        'ellipse_point_check',
        'ellipse_properties',
        'ellipse_orbit_dist_sum'
    ])
    
    if problem_type == 'ellipse_point_check':
        problem_output = generate_ellipse_point_check_problem(level)
        problem_output["explanation"] = explain_ellipse_point_check(problem_output["explanation_data"])
        return problem_output
    elif problem_type == 'ellipse_properties':
        problem_output = generate_ellipse_properties_problem(level)
        problem_output["explanation"] = explain_ellipse_properties(problem_output["explanation_data"])
        return problem_output
    elif problem_type == 'ellipse_orbit_dist_sum':
        problem_output = generate_ellipse_orbit_problem(level)
        problem_output["explanation"] = explain_ellipse_orbit(problem_output["explanation_data"])
        return problem_output
    
    return {
        "question_text": "An error occurred generating the problem.",
        "answer": "",
        "correct_answer": "",
        "explanation": ""
    }

def check(user_answer, correct_answer):
    """
    Checks if the user's answer is correct for ellipse problems.
    Handles numerical, comma-separated, and algebraic (X-x) answers.
    """
    user_answer = user_answer.strip().lower()
    correct_answer = correct_answer.strip().lower()
    
    is_correct = False
    
    # Direct string comparison
    if user_answer == correct_answer:
        is_correct = True
    else:
        # Numeric comparison for simple integer/float answers
        try:
            if float(user_answer) == float(correct_answer):
                is_correct = True
        except ValueError:
            pass
        
        # Specific handling for "long_axis, focal_distance" format (e.g., "80, 10")
        if ',' in correct_answer and ',' in user_answer:
            try:
                ua_parts = [p.strip() for p in user_answer.split(',')]
                ca_parts = [p.strip() for p in correct_answer.split(',')]
                if len(ua_parts) == len(ca_parts) == 2:
                    if float(ua_parts[0]) == float(ca_parts[0]) and float(ua_parts[1]) == float(ca_parts[1]):
                        is_correct = True
            except ValueError:
                pass
        
        # Specific handling for "2a-x" format (e.g., "80-x")
        if '-x' in correct_answer and '-x' in user_answer:
            try:
                ca_val = float(correct_answer.replace('-x', ''))
                ua_val = float(user_answer.replace('-x', ''))
                if ca_val == ua_val:
                    is_correct = True
            except ValueError:
                pass

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}