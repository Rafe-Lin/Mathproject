import random
from fractions import Fraction
import math
import uuid

def generate(level=1):
    problem_type_options = []
    if level == 1:
        problem_type_options = ['dist_comparison', 'basic_definition_calc']
    elif level == 2:
        problem_type_options = ['dist_comparison', 'basic_definition_calc', 'elements_relationship']
    else: # level 3 or higher
        problem_type_options = ['dist_comparison', 'basic_definition_calc', 'elements_relationship', 'combined_calculation']
    
    problem_type = random.choice(problem_type_options)
    
    if problem_type == 'dist_comparison':
        return generate_dist_comparison_problem()
    elif problem_type == 'basic_definition_calc':
        return generate_basic_definition_calc_problem()
    elif problem_type == 'elements_relationship':
        return generate_elements_relationship_problem()
    else: # combined_calculation
        return generate_combined_calculation_problem()

def generate_dist_comparison_problem():
    # Problem Type A: Distance Comparison (Like Example 1)
    # Concept: Points on parabola P: PF = PL. Farther from directrix => farther from focus.
    
    axis_type = random.choice(['horizontal', 'vertical'])
    points_labels = ['A', 'B', 'C']
    
    if axis_type == 'vertical': # Directrix is y=k, parabola opens up/down
        directrix_desc = r"水平準線 $L$"
        # For simplicity, assume points have increasing/decreasing y-coordinates relative to the directrix.
        # Assume parabola opens upwards, so focus F is above L. Points with larger y are farther from L.
        relative_pos_desc_options = [
            r"已知 $A$ 點的 $y$ 座標最大，$B$ 點次之，$C$ 點最小。",
            r"已知 $C$ 點的 $y$ 座標最大，$B$ 點次之，$A$ 點最小。"
        ]
        relative_pos_desc = random.choice(relative_pos_desc_options)
        
        if r"$A$ 點的 $y$ 座標最大" in relative_pos_desc:
            # A is farthest from directrix (assuming it's below points, opening upwards), so AF is largest.
            correct_order = "A>B>C"
            question_text = (
                f"在一個開口向上的拋物線上，其具有{directrix_desc}。點 ${points_labels[0]}, {points_labels[1]}, {points_labels[2]}$ "
                f"皆在拋物線上。{relative_pos_desc}<br>"
                f"請由大到小排序這三點到焦點 $F$ 的距離。(例如：A>B>C)"
            )
        else: # C is farthest
            correct_order = "C>B>A"
            question_text = (
                f"在一個開口向上的拋物線上，其具有{directrix_desc}。點 ${points_labels[0]}, {points_labels[1]}, {points_labels[2]}$ "
                f"皆在拋物線上。{relative_pos_desc}<br>"
                f"請由大到小排序這三點到焦點 $F$ 的距離。(例如：A>B>C)"
            )
            
    else: # horizontal axis, Directrix is x=k, parabola opens left/right
        directrix_desc = r"鉛垂準線 $L$"
        relative_pos_desc_options = [
            r"已知 $A$ 點的 $x$ 座標最大，$B$ 點次之，$C$ 點最小。",
            r"已知 $C$ 點的 $x$ 座標最大，$B$ 點次之，$A$ 點最小。"
        ]
        relative_pos_desc = random.choice(relative_pos_desc_options)
        
        # Assume parabola opens rightwards, so focus F is to the right of L. Points with larger x are farther from L.
        if r"$A$ 點的 $x$ 座標最大" in relative_pos_desc:
            correct_order = "A>B>C"
            question_text = (
                f"在一個開口向右的拋物線上，其具有{directrix_desc}。點 ${points_labels[0]}, {points_labels[1]}, {points_labels[2]}$ "
                f"皆在拋物線上。{relative_pos_desc}<br>"
                f"請由大到小排序這三點到焦點 $F$ 的距離。(例如：A>B>C)"
            )
        else: # C is farthest
            correct_order = "C>B>A"
            question_text = (
                f"在一個開口向右的拋物線上，其具有{directrix_desc}。點 ${points_labels[0]}, {points_labels[1]}, {points_labels[2]}$ "
                f"皆在拋物線上。{relative_pos_desc}<br>"
                f"請由大到小排序這三點到焦點 $F$ 的距離。(例如：A>B>C)"
            )
            
    return {
        "question_text": question_text,
        "answer": correct_order,
        "correct_answer": correct_order
    }

def generate_basic_definition_calc_problem():
    # Problem Type B: Directrix/Focus Distance Application (Simple Calculation)
    # Concept: PF = PL.
    
    distance = random.randint(3, 20)
    
    question_choice = random.choice(['focus_to_directrix', 'directrix_to_focus'])
    
    if question_choice == 'focus_to_directrix':
        question_text = (
            f"若點 $P$ 在拋物線上，且 $P$ 到焦點 $F$ 的距離為 ${distance}$ 單位，"
            f"則 $P$ 到準線 $L$ 的距離為何？"
        )
    else:
        question_text = (
            f"若點 $P$ 在拋物線上，且 $P$ 到準線 $L$ 的距離為 ${distance}$ 單位，"
            f"則 $P$ 到焦點 $F$ 的距離為何？"
        )
        
    correct_answer = str(distance)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_elements_relationship_problem():
    # Problem Type C: Elements Relationship (Vertex, Focus, Directrix)
    # Concept: Vertex is midpoint of focus and directrix (along the axis of symmetry).
    # Distance from vertex to focus = distance from vertex to directrix = focal length (p).
    
    h = random.randint(-5, 5)
    k = random.randint(-5, 5)
    p = random.randint(1, 5) # Focal length
    
    # For simplicity, always asking for directrix given F and V
    
    axis_orientation = random.choice(['vertical_up', 'vertical_down', 'horizontal_right', 'horizontal_left'])
    
    focus_coord_str = ""
    vertex_coord_str = ""
    directrix_eq = ""
    
    if axis_orientation == 'vertical_up': # Parabola opens up
        focus_coord_str = f"F({h}, {k + p})"
        vertex_coord_str = f"V({h}, {k})"
        directrix_eq = f"y={k - p}"
        question_text = (
            f"一個開口向上的拋物線，其焦點為 ${focus_coord_str}$，頂點為 ${vertex_coord_str}$。<br>"
            f"請問此拋物線的準線方程式為何？"
        )
    elif axis_orientation == 'vertical_down': # Parabola opens down
        focus_coord_str = f"F({h}, {k - p})"
        vertex_coord_str = f"V({h}, {k})"
        directrix_eq = f"y={k + p}"
        question_text = (
            f"一個開口向下的拋物線，其焦點為 ${focus_coord_str}$，頂點為 ${vertex_coord_str}$。<br>"
            f"請問此拋物線的準線方程式為何？"
        )
    elif axis_orientation == 'horizontal_right': # Parabola opens right
        focus_coord_str = f"F({h + p}, {k})"
        vertex_coord_str = f"V({h}, {k})"
        directrix_eq = f"x={h - p}"
        question_text = (
            f"一個開口向右的拋物線，其焦點為 ${focus_coord_str}$，頂點為 ${vertex_coord_str}$。<br>"
            f"請問此拋物線的準線方程式為何？"
        )
    else: # horizontal_left, Parabola opens left
        focus_coord_str = f"F({h - p}, {k})"
        vertex_coord_str = f"V({h}, {k})"
        directrix_eq = f"x={h + p}"
        question_text = (
            f"一個開口向左的拋物線，其焦點為 ${focus_coord_str}$，頂點為 ${vertex_coord_str}$。<br>"
            f"請問此拋物線的準線方程式為何？"
        )
            
    correct_answer = directrix_eq
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_combined_calculation_problem():
    # Problem Type D: Combined Calculation (Similar to Example 3, but simplified)
    # Concept: PF=PL, and if F is on PQ, then PQ = PF + QF.
    
    pp_prime = random.randint(3, 15)
    qq_prime = random.randint(3, 15)
    
    # Ensure PP' != QQ' for more interesting numbers, but not strictly necessary.
    while pp_prime == qq_prime:
        qq_prime = random.randint(3, 15)
        
    pq_length = pp_prime + qq_prime
    
    question_text = (
        r"直線 $L$ 與點 $F$ 分別為拋物線的準線與焦點。$P, Q$ 是拋物線上的兩點，"
        r"且 $F$ 點在線段 $PQ$ 上。已知 $P$ 點到準線 $L$ 的距離 $PP' = {pp_prime}$，"
        r" $Q$ 點到準線 $L$ 的距離 $QQ' = {qq_prime}$。"
        r"<br>請問線段 $PQ$ 的長度為何？"
    )
    correct_answer = str(pq_length)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    # Standard normalization as per template
    user_answer_normalized = user_answer.strip().upper()
    correct_answer_normalized = correct_answer.strip().upper()
    
    is_correct = (user_answer_normalized == correct_answer_normalized)
    
    # Additional checks for common variations if the first one fails
    if not is_correct:
        # 1. Numeric answers: check float equivalence
        try:
            if float(user_answer_normalized) == float(correct_answer_normalized):
                is_correct = True
        except ValueError:
            pass
            
    if not is_correct:
        # 2. Comparison strings (e.g., A>B>C, A > B > C): remove non-alphanumeric and compare
        # This handles cases like 'A>B>C' vs 'A > B > C'
        normalized_user_comp = "".join(filter(str.isalnum, user_answer_normalized))
        normalized_correct_comp = "".join(filter(str.isalnum, correct_answer_normalized))
        if normalized_user_comp == normalized_correct_comp:
            is_correct = True
            
    if not is_correct:
        # 3. Equation strings (e.g., y=3, y = 3, 3=y): remove spaces, and allow swapped sides
        # This handles 'y = 3' vs 'y=3' and 'y=3' vs '3=y'
        user_no_space = user_answer_normalized.replace(' ', '')
        correct_no_space = correct_answer_normalized.replace(' ', '')

        if '=' in user_no_space and '=' in correct_no_space:
            ua_parts = user_no_space.split('=', 1)
            ca_parts = correct_no_space.split('=', 1)

            if len(ua_parts) == 2 and len(ca_parts) == 2:
                # Compare (left == left AND right == right) OR (left == right AND right == left)
                if (ua_parts[0] == ca_parts[0] and ua_parts[1] == ca_parts[1]) or \
                   (ua_parts[0] == ca_parts[1] and ua_parts[1] == ca_parts[0]):
                    is_correct = True
                else:
                    # Try numeric comparison for the RHS if LHS is a variable
                    # e.g. y=5 vs Y=5 (already handled by .upper())
                    # Or y=5.0 vs y=5 (handled by float conversion if not caught by direct comparison)
                    # This path checks for cases like 'y=5' vs 'z=5' (variable mismatch) or 'y=5' vs 'y=6' (value mismatch)
                    try:
                        if ua_parts[0].isalpha() and ca_parts[0].isalpha() and \
                           ua_parts[0] == ca_parts[0] and \
                           float(ua_parts[1]) == float(ca_parts[1]):
                            is_correct = True
                        elif ua_parts[1].isalpha() and ca_parts[1].isalpha() and \
                             ua_parts[1] == ca_parts[1] and \
                             float(ua_parts[0]) == float(ca_parts[0]):
                            is_correct = True
                    except ValueError:
                        pass
        
    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}