import random
import math
from fractions import Fraction

# Helper to format the coordinate part (e.g., -2 for (x-2), +3 for (y+3))
def format_coord(coord):
    if coord >= 0:
        return f"-{coord}"
    else:
        return f"+{-coord}"

# Helper to format a signed value for displaying in equations (e.g., +5x, -3y, +7)
def format_signed_val(val):
    if val >= 0:
        return f"+{val}"
    else:
        return str(val)

def generate_point_circle_relationship(level=1):
    h = random.randint(-4, 4)
    k = random.randint(-4, 4)
    r = random.randint(3, 7)
    r_sq = r**2

    # Choose between standard and general form for the circle equation based on level
    # General form is introduced at higher levels
    use_general_form = random.random() < 0.5 if level > 1 else False

    # Determine the circle equation string and the standard form for solution
    circle_eq = ""
    std_eq_str = ""

    if use_general_form:
        # Generate D, E, F for general form: x^2 + y^2 + Dx + Ey + F = 0
        D = -2 * h
        E = -2 * k
        F_val = h**2 + k**2 - r**2 # Using F_val to avoid conflict with function F

        # Build terms for the general form equation string
        terms_str = ""
        terms_str += r"$x^{{2}}$"
        terms_str += r" + $y^{{2}}$" # Always separated by +

        if D != 0:
            if D > 0: terms_str += f" + {D}x"
            else: terms_str += f" {D}x" # Negative sign naturally implies a space before it
        
        if E != 0:
            if E > 0: terms_str += f" + {E}y"
            else: terms_str += f" {E}y"
        
        if F_val != 0:
            if F_val > 0: terms_str += f" + {F_val}"
            else: terms_str += f" {F_val}"
        
        circle_eq = terms_str.strip() + " = 0"
        circle_eq = circle_eq.replace(" + -", " - ") # Clean up " + -X" to " - X"

        # Also generate standard form string for the solution
        x_part_std = f"(x {format_coord(h)})" if h != 0 else "x"
        y_part_std = f"(y {format_coord(k)})" if k != 0 else "y"
        
        if h == 0 and k == 0:
            std_eq_str = r"$x^{{2}} + y^{{2}} = $" + str(r_sq)
        elif h == 0:
            std_eq_str = r"$x^{{2}} + (y" + format_coord(k) + r")^{{2}} = $" + str(r_sq)
        elif k == 0:
            std_eq_str = r"$(x" + format_coord(h) + r")^{{2}} + y^{{2}} = $" + str(r_sq)
        else:
            std_eq_str = r"$(x" + format_coord(h) + r")^{{2}} + (y" + format_coord(k) + r")^{{2}} = $" + str(r_sq)

    else: # Standard form (used directly in question)
        x_part = f"(x {format_coord(h)})" if h != 0 else "x"
        y_part = f"(y {format_coord(k)})" if k != 0 else "y"
        
        if h == 0 and k == 0:
            circle_eq = r"$x^{{2}} + y^{{2}} = $" + str(r_sq)
        elif h == 0:
            circle_eq = r"$x^{{2}} + (y" + format_coord(k) + r")^{{2}} = $" + str(r_sq)
        elif k == 0:
            circle_eq = r"$(x" + format_coord(h) + r")^{{2}} + y^{{2}} = $" + str(r_sq)
        else:
            circle_eq = r"$(x" + format_coord(h) + r")^{{2}} + (y" + format_coord(k) + r")^{{2}} = $" + str(r_sq)
        
        std_eq_str = circle_eq # If question is standard form, std_eq_str is the same

    points_data = []
    point_labels = ['P', 'Q', 'R']
    categories_needed = ['on', 'inside', 'outside']
    
    # Generate points until we have one of each type
    generated_points_candidates = []
    attempts = 0
    max_attempts = 20 # Limit attempts to prevent infinite loops

    while (len(categories_needed) > 0 or len(generated_points_candidates) < 3) and attempts < max_attempts:
        temp_x = random.randint(h - r - 3, h + r + 3)
        temp_y = random.randint(k - r - 3, k + r + 3)
        
        dist_sq = (temp_x - h)**2 + (temp_y - k)**2
        
        if dist_sq < r_sq and 'inside' in categories_needed:
            generated_points_candidates.append({'coords': (temp_x, temp_y), 'type': 'inside'})
            categories_needed.remove('inside')
        elif dist_sq == r_sq and 'on' in categories_needed:
            generated_points_candidates.append({'coords': (temp_x, temp_y), 'type': 'on'})
            categories_needed.remove('on')
        elif dist_sq > r_sq and 'outside' in categories_needed:
            generated_points_candidates.append({'coords': (temp_x, temp_y), 'type': 'outside'})
            categories_needed.remove('outside')
        attempts += 1
            
    # If after attempts, we still don't have all categories, force them with simple points
    if 'on' in categories_needed:
        generated_points_candidates.append({'coords': (h + r, k), 'type': 'on'})
    if 'inside' in categories_needed:
        generated_points_candidates.append({'coords': (h + random.randint(1, r // 2) * random.choice([-1, 1]), k), 'type': 'inside'})
    if 'outside' in categories_needed:
        generated_points_candidates.append({'coords': (h + (r + 1) * random.choice([-1, 1]), k), 'type': 'outside'})

    random.shuffle(generated_points_candidates)
    
    # Select 3 distinct points for the question
    # Ensure points are distinct to avoid confusion
    final_points = []
    seen_coords = set()
    for p_info in generated_points_candidates:
        if len(final_points) == 3:
            break
        if p_info['coords'] not in seen_coords:
            final_points.append(p_info)
            seen_coords.add(p_info['coords'])
    
    # Assign labels
    for i, p_info in enumerate(final_points):
        label = point_labels[i]
        points_data.append({
            'label': label,
            'coords': p_info['coords'],
            'type': p_info['type']
        })

    question_points_str = ", ".join([f"${p['label']}({p['coords'][0]}, {p['coords'][1]})$" for p in points_data])

    question_text = f"已知圓 $C$ 的方程式為 ${circle_eq}$ ，分別判斷 {question_points_str} 三點與圓的關係（即點是在內部、外部還是圓上）。"
    
    solution_steps = []
    
    if use_general_form:
        solution_steps.append(f"將圓 $C$ 的方程式 ${circle_eq}$ 整理成標準式:")
        
        half_D = D / 2
        half_E = E / 2
        
        # Completing the square step
        solution_steps.append(r"$(x^{{2}}" + (f"{format_signed_val(D)}x" if D != 0 else "") + f"+({int(half_D)})^{{2}})$" + \
                            r" + $(y^{{2}}" + (f"{format_signed_val(E)}y" if E != 0 else "") + f"+({int(half_E)})^{{2}})$" + \
                            f" = $-{F_val} + ({int(half_D)})^{{2}} + ({int(half_E)})^{{2}}$")
        
        # Standard form result
        solution_steps.append(f"$(x {format_signed_val(int(half_D))})^{{2}} + (y {format_signed_val(int(half_E))})^{{2}} = {int(-F_val + half_D**2 + half_E**2)}$")
        
        solution_steps.append(f"因此圓心為 $M({h}, {k})$ ，半徑 $r = \\sqrt{{{r_sq}}} = {r}$。")
    else:
        solution_steps.append(f"圓 $C:{std_eq_str}$ 的圓心為 $M({h}, {k})$ ，半徑為 $r = \\sqrt{{{r_sq}}} = {r}$。")
    
    solution_steps.append(f"分別計算各點與圓心 $M({h}, {k})$ 的距離，得")

    results = []
    ans_parts = []
    for p_info in points_data:
        label = p_info['label']
        px, py = p_info['coords']
        
        diff_x_sq = (px - h)**2
        diff_y_sq = (py - k)**2
        dist_sq = diff_x_sq + diff_y_sq
        dist = math.sqrt(dist_sq)
        
        relation_txt = ""
        comparison_sym = "" # <, =, >
        if dist < r:
            relation_txt = "圓內"
            comparison_sym = "<"
        elif dist == r:
            relation_txt = "圓上"
            comparison_sym = "="
        else: # dist > r
            relation_txt = "圓外"
            comparison_sym = ">"
        
        dist_calc_str_parts = []
        dist_calc_str_parts.append(f"${label}M = \\sqrt{{({px}-{h})^{{2}} + ({py}-{k})^{{2}}}} = \\sqrt{{{diff_x_sq}+{diff_y_sq}}} = \\sqrt{{{dist_sq}}}")
        
        if dist.is_integer():
            dist_calc_str_parts.append(f" = {int(dist)}$")
            solution_steps.append("".join(dist_calc_str_parts) + f" {comparison_sym} {r}$")
        else:
            solution_steps.append("".join(dist_calc_str_parts) + f" {comparison_sym} {r}$") # Compare sqrt directly
        
        ans_parts.append(f"${label}$在{relation_txt}")
        results.append(relation_txt)

    final_answer = ", ".join(ans_parts)
    solution_steps.append(f"因此，{final_answer}。")
    
    correct_answer = final_answer
    
    full_solution = "\n".join(solution_steps)

    return {
        "question_text": question_text,
        "answer": final_answer,
        "correct_answer": correct_answer,
        "solution": full_solution
    }

def generate_max_min_distance(level=1):
    h = random.randint(-4, 4)
    k = random.randint(-4, 4)
    r = random.randint(3, 7)
    r_sq = r**2

    # Ensure PM is an integer and P is outside the circle
    dist_pm_int = random.randint(r + 2, r + 8) # d must be > r
    
    # Generate point P such that PM = dist_pm_int
    if random.random() < 0.5: # P is on the same horizontal line as M
        px = h + dist_pm_int * random.choice([-1, 1])
        py = k
    else: # P is on the same vertical line as M
        px = h
        py = k + dist_pm_int * random.choice([-1, 1])

    # Determine the circle equation string and the standard form for solution
    circle_eq = ""
    std_eq_str = ""

    use_general_form = random.random() < 0.5 if level > 1 else False

    if use_general_form:
        D = -2 * h
        E = -2 * k
        F_val = h**2 + k**2 - r**2

        terms_str = ""
        terms_str += r"$x^{{2}}$"
        terms_str += r" + $y^{{2}}$"

        if D != 0:
            if D > 0: terms_str += f" + {D}x"
            else: terms_str += f" {D}x"
        
        if E != 0:
            if E > 0: terms_str += f" + {E}y"
            else: terms_str += f" {E}y"
        
        if F_val != 0:
            if F_val > 0: terms_str += f" + {F_val}"
            else: terms_str += f" {F_val}"
        
        circle_eq = terms_str.strip() + " = 0"
        circle_eq = circle_eq.replace(" + -", " - ")

        x_part_std = f"(x {format_coord(h)})" if h != 0 else "x"
        y_part_std = f"(y {format_coord(k)})" if k != 0 else "y"
        
        if h == 0 and k == 0:
            std_eq_str = r"$x^{{2}} + y^{{2}} = $" + str(r_sq)
        elif h == 0:
            std_eq_str = r"$x^{{2}} + (y" + format_coord(k) + r")^{{2}} = $" + str(r_sq)
        elif k == 0:
            std_eq_str = r"$(x" + format_coord(h) + r")^{{2}} + y^{{2}} = $" + str(r_sq)
        else:
            std_eq_str = r"$(x" + format_coord(h) + r")^{{2}} + (y" + format_coord(k) + r")^{{2}} = $" + str(r_sq)
    else:
        x_part = f"(x {format_coord(h)})" if h != 0 else "x"
        y_part = f"(y {format_coord(k)})" if k != 0 else "y"
        
        if h == 0 and k == 0:
            circle_eq = r"$x^{{2}} + y^{{2}} = $" + str(r_sq)
        elif h == 0:
            circle_eq = r"$x^{{2}} + (y" + format_coord(k) + r")^{{2}} = $" + str(r_sq)
        elif k == 0:
            circle_eq = r"$(x" + format_coord(h) + r")^{{2}} + y^{{2}} = $" + str(r_sq)
        else:
            circle_eq = r"$(x" + format_coord(h) + r")^{{2}} + (y" + format_coord(k) + r")^{{2}} = $" + str(r_sq)
        
        std_eq_str = circle_eq

    point_str = f"$P({px}, {py})$"
    
    question_text = f"已知圓 $C:{circle_eq}$ 及點 {point_str} ，求 $P$ 點與圓 $C$ 上各點距離的最大值與最小值。"

    solution_steps = []
    
    if use_general_form:
        solution_steps.append(f"將圓 $C$ 的方程式 ${circle_eq}$ 整理成標準式:")
        
        half_D = D / 2
        half_E = E / 2
        
        solution_steps.append(r"$(x^{{2}}" + (f"{format_signed_val(D)}x" if D != 0 else "") + f"+({int(half_D)})^{{2}})$" + \
                            r" + $(y^{{2}}" + (f"{format_signed_val(E)}y" if E != 0 else "") + f"+({int(half_E)})^{{2}})$" + \
                            f" = $-{F_val} + ({int(half_D)})^{{2}} + ({int(half_E)})^{{2}}$")
        
        solution_steps.append(f"$(x {format_signed_val(int(half_D))})^{{2}} + (y {format_signed_val(int(half_E))})^{{2}} = {int(-F_val + half_D**2 + half_E**2)}$")
            
        solution_steps.append(f"因此圓 $C$ 的圓心為 $M({h}, {k})$ ，半徑 $r = \\sqrt{{{r_sq}}} = {r}$。")
    else:
        solution_steps.append(f"圓 $C:{std_eq_str}$ 的圓心為 $M({h}, {k})$ ，半徑為 $r = \\sqrt{{{r_sq}}} = {r}$。")
    
    diff_x_sq = (px - h)**2
    diff_y_sq = (py - k)**2
    dist_pm_sq = diff_x_sq + diff_y_sq # This should be dist_pm_int**2
    
    solution_steps.append(f"計算 $P({px}, {py})$ 到圓心 $M({h}, {k})$ 的距離：")
    solution_steps.append(f"$PM = \\sqrt{{({px}-{h})^{{2}} + ({py}-{k})^{{2}}}} = \\sqrt{{{diff_x_sq}+{diff_y_sq}}} = \\sqrt{{{dist_pm_sq}}} = {dist_pm_int}$")
    
    solution_steps.append(f"因為 $PM = {dist_pm_int} > r = {r}$ ，所以 $P$ 為圓外一點。")
    solution_steps.append(f"令直線 $PM$ 與圓 $C$ 分別交於 $A, B$ 二點，則圓上各點中與 $P$ 距離最遠者為 $A$，最近者為 $B$，且")
    solution_steps.append(f"$PA = PM + r = {dist_pm_int} + {r} = {dist_pm_int + r}$")
    solution_steps.append(f"$PB = PM - r = {dist_pm_int} - {r} = {dist_pm_int - r}$")
    
    max_dist = dist_pm_int + r
    min_dist = dist_pm_int - r
    
    solution_steps.append(f"所以 $P$ 點與圓 $C$ 上各點距離的最大值為 ${max_dist}$，最小值為 ${min_dist}$。")
    
    correct_answer = f"最大值為 {max_dist}, 最小值為 {min_dist}"
    
    full_solution = "\n".join(solution_steps)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "solution": full_solution
    }

def generate(level=1):
    problem_type = random.choice(['point_circle_relationship', 'max_min_distance'])
    
    if problem_type == 'point_circle_relationship':
        return generate_point_circle_relationship(level)
    else: # max_min_distance
        return generate_max_min_distance(level)

def check(user_answer, correct_answer):
    user_answer_cleaned = user_answer.strip().replace(" ", "").replace("$", "").lower()
    correct_answer_cleaned = correct_answer.strip().replace(" ", "").replace("$", "").lower()

    is_correct = (user_answer_cleaned == correct_answer_cleaned)

    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}