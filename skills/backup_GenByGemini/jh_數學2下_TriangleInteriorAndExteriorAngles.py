import random
import math
from fractions import Fraction

def _format_expr(c, k, var='x'):
    """
    Formats a coefficient and a constant into a string like '2x - 10', 'x', or '3x + 10'.
    """
    if c == 0:
        return f"{k}"
    
    # Coefficient part
    if c == 1:
        c_str = var
    elif c == -1:
        c_str = f"-{var}"
    else:
        c_str = f"{c}{var}"

    # Constant part
    if k == 0:
        return c_str
    elif k > 0:
        return f"{c_str} + {k}"
    else: # k < 0
        return f"{c_str} - {-k}"

def generate_interior_sum_algebra():
    """
    Generates a problem based on the Triangle Interior Angle Sum Theorem.
    e.g., 若△ABC 三內角分別為 ( 2x-10 )°、 x°、( 3x＋10 )°，則 x=？
    """
    while True:
        try:
            x_sol = random.randint(10, 40)
            total_coeff = random.choice([4, 5, 6, 8, 9, 10])
            total_const = 180 - total_coeff * x_sol

            # Split total_coeff into c1, c2, c3
            # Ensure safe range for c1: must leave at least 1 for c2 and 1 for c3
            if total_coeff - 2 < 1: continue
            c1 = random.randint(1, total_coeff - 2)
            
            # Ensure safe range for c2: must leave at least 1 for c3
            remaining_for_c2 = total_coeff - c1 - 1
            if remaining_for_c2 < 1: continue
            c2 = random.randint(1, remaining_for_c2)
            
            c3 = total_coeff - c1 - c2
            if c3 <= 0: continue

            coeffs = [c1, c2, c3]
            random.shuffle(coeffs)
            c1, c2, c3 = coeffs
            
            # Split total_const into k1, k2, k3
            k1 = random.randint(-40, 40)
            k2 = random.randint(-40, 40)
            k3 = total_const - k1 - k2
            
            # Check if all angles are positive at the solution
            angle1 = c1 * x_sol + k1
            angle2 = c2 * x_sol + k2
            angle3 = c3 * x_sol + k3
            
            if angle1 > 10 and angle2 > 10 and angle3 > 10:
                expr1 = _format_expr(c1, k1)
                expr2 = _format_expr(c2, k2)
                expr3 = _format_expr(c3, k3)
                
                question_text = f"若 $\\triangle ABC$ 三內角分別為 $({expr1})^\\circ$、$({expr2})^\\circ$、$({expr3})^\\circ$，則 $x=?$"
                correct_answer = str(x_sol)
                
                return {
                    "question_text": question_text,
                    "answer": correct_answer,
                    "correct_answer": correct_answer
                }
        except ValueError:
            continue

def generate_exterior_sum_algebra():
    """
    Generates a problem based on the Triangle Exterior Angle Sum Theorem.
    e.g., 一組外角度數為 2x°、3x°、4x°，則此三角形的最大內角為多少度？
    """
    while True:
        try:
            total_coeff = random.choice([9, 10, 12, 15, 18])
            x_sol = 360 // total_coeff

            # [Fix] Logic to ensure c1 < c2 < c3
            # Constraints:
            # 1. c1 >= 2
            # 2. c1 + c2 + c3 = total
            # 3. c1 < c2 < c3 implies min sum is c1 + (c1+1) + (c1+2) = 3*c1 + 3 <= total
            #    So c1 <= (total - 3) // 3
            
            max_c1 = (total_coeff - 3) // 3
            if max_c1 < 2: continue # Should not happen for 9+
            
            c1 = random.randint(2, max_c1)
            
            # Max c2: c1 + c2 + (c2+1) <= total => 2*c2 <= total - c1 - 1
            max_c2 = (total_coeff - c1 - 1) // 2
            min_c2 = c1 + 1
            
            if min_c2 > max_c2: continue # Should not happen if max_c1 logic is correct
            
            c2 = random.randint(min_c2, max_c2)
            c3 = total_coeff - c1 - c2

            # Final check just in case
            if c3 > c2:
                # Check for valid exterior angles (corresponding interior angle must be > 0)
                # Exterior angle < 180 => c3 * x_sol < 180 => c3 < 180 / x_sol => c3 < total_coeff / 2
                if c3 < total_coeff / 2.0:
                    break
        except ValueError:
            continue

    coeffs = [c1, c2, c3]
    random.shuffle(coeffs)
    
    ext_angles = [c * x_sol for c in coeffs]
    int_angles = [180 - ext for ext in ext_angles]

    target = random.choice(['最大', '最小'])
    if target == '最大':
        result_angle = max(int_angles)
    else:
        result_angle = min(int_angles)

    question_text = f"有一個三角形，它的一組外角度數為 ${coeffs[0]}x^\\circ$、${coeffs[1]}x^\\circ$、${coeffs[2]}x^\\circ$，則此三角形的{target}內角為多少度？"
    correct_answer = str(int(result_angle))

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_exterior_theorem_algebra():
    """
    Generates a problem based on the Triangle Exterior Angle Theorem.
    e.g., 若∠B 的外角為 120°，且∠C=2∠A，則∠A 為多少度？
    """
    while True:
        c2 = random.randint(2, 5) # Multiplier for the angle
        multiplier = 1 + c2
        x_sol = random.randint(10, 35)
        ext_angle = multiplier * x_sol

        # Ensure the exterior angle is reasonable
        if 70 < ext_angle < 170:
            break

    vertices = random.sample(['A', 'B', 'C'], 3)
    v_ext, v_int1, v_int2 = vertices[0], vertices[1], vertices[2]

    question_text = f"$\\triangle {v_ext}{v_int1}{v_int2}$ 中，若 $\\angle {v_ext}$ 的外角為 ${ext_angle}^\\circ$，且 $\\angle {v_int2}={c2}\\angle {v_int1}$，則 $\\angle {v_int1}$ 為多少度？"
    correct_answer = str(x_sol)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }
    
def generate_bowtie_theorem():
    """
    Generates a problem based on the "bowtie" or "butterfly" theorem (∠A+∠B = ∠C+∠D).
    e.g., 若∠A=x°、∠B=45°、∠C=(2x-5)°、∠D=30°，則x=？
    """
    while True:
        try:
            x_sol = random.randint(15, 35)
            b = random.randint(30, 80)
            d = random.randint(30, 80)
            c_coeff = random.randint(2, 4)

            # A + B = C + D  => x + b = (c_coeff*x + c_const) + d
            # c_const = x + b - d - c_coeff*x
            c_const = (1 - c_coeff) * x_sol + b - d
            
            angle_a = x_sol
            angle_c = c_coeff * x_sol + c_const
            
            if angle_a > 10 and b > 10 and d > 10 and angle_c > 10:
                break
        except ValueError:
            continue
            
    expr_c = _format_expr(c_coeff, c_const)

    question_text = f"如圖，AD 與 BC 交於 O 點。若 $\\angle A=x^\\circ$、$\\angle B={b}^\\circ$、$\\angle C=({expr_c})^\\circ$、$\\angle D={d}^\\circ$，則 $x=?$<br>(註：此題型為對頂的兩個三角形，俗稱蝴蝶形或領結形)"
    correct_answer = str(x_sol)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_boomerang_theorem():
    """
    Generates a problem based on the concave quadrilateral theorem (∠BCD = ∠A+∠B+∠D).
    """
    while True:
        try:
            x_sol = random.randint(20, 50)
            a = random.randint(20, 60)
            b = random.randint(20, 60)
            d = random.randint(20, 60)
            
            sum_angles = a + b + d
            if sum_angles >= 360: continue

            bcd_coeff = random.randint(2, 5)
            # bcd = bcd_coeff*x + bcd_const = a + b + d
            bcd_const = sum_angles - bcd_coeff * x_sol
            
            angle_bcd = bcd_coeff * x_sol + bcd_const
            if angle_bcd > 20 and angle_bcd < 360:
                break
        except ValueError:
            continue

    expr_bcd = _format_expr(bcd_coeff, bcd_const)
    
    question_text = f"在一個凹四邊形 $ABCD$ 中，其中 $\\angle C$ 為凹角。若 $\\angle A={a}^\\circ$、$\\angle B={b}^\\circ$、$\\angle D={d}^\\circ$，且 $\\angle BCD=({expr_bcd})^\\circ$，則 $x=?$"
    correct_answer = str(x_sol)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_angle_relation_type():
    """
    Generates a problem asking for the triangle type based on angle relations.
    e.g., ∠C=∠A+∠B or ∠A:∠B:∠C = 1:2:3
    """
    sub_type = random.choice(['sum', 'ratio'])
    
    if sub_type == 'sum':
        v = random.sample(['A', 'B', 'C'], 3)
        question_text = f"在 $\\triangle {v[0]}{v[1]}{v[2]}$ 中，若已知 $\\angle {v[2]} = \\angle {v[0]} + \\angle {v[1]}$，則 $\\triangle {v[0]}{v[1]}{v[2]}$ 為何種三角形？"
        correct_answer = "直角三角形"
    else: # ratio
        ratio_map = {
            (1, 1, 1): "正三角形",
            (1, 2, 3): "直角三角形",
            (2, 3, 4): "銳角三角形",
            (1, 4, 5): "直角三角形",
            (3, 4, 5): "銳角三角形"
        }
        ratios = random.choice(list(ratio_map.keys()))
        correct_answer = ratio_map[ratios]
        
        shuffled_ratios = list(ratios)
        random.shuffle(shuffled_ratios)
        r1, r2, r3 = shuffled_ratios
        
        v = ['A', 'B', 'C']
        question_text = f"在 $\\triangle {v[0]}{v[1]}{v[2]}$ 中，若三內角 $\\angle {v[0]} : \\angle {v[1]} : \\angle {v[2]} = {r1} : {r2} : {r3}$，則 $\\triangle {v[0]}{v[1]}{v[2]}$ 為何種三角形？"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    生成「三角形內角與外角」相關題目。
    """
    problem_types = [
        'interior_sum_algebra', 
        'exterior_sum_algebra', 
        'exterior_theorem_algebra', 
        'bowtie_theorem', 
        'boomerang_theorem',
        'angle_relation_type'
    ]
    problem_type = random.choice(problem_types)
    
    if problem_type == 'interior_sum_algebra':
        return generate_interior_sum_algebra()
    elif problem_type == 'exterior_sum_algebra':
        return generate_exterior_sum_algebra()
    elif problem_type == 'exterior_theorem_algebra':
        return generate_exterior_theorem_algebra()
    elif problem_type == 'bowtie_theorem':
        return generate_bowtie_theorem()
    elif problem_type == 'boomerang_theorem':
        return generate_boomerang_theorem()
    else: # angle_relation_type
        return generate_angle_relation_type()

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip()
    correct_answer_str = str(correct_answer).strip()
    
    is_correct = False
    
    # Direct string comparison for text answers
    if user_answer == correct_answer_str:
        is_correct = True
    # Handle synonyms
    elif correct_answer_str == "正三角形" and user_answer == "等邊三角形":
        is_correct = True
    elif correct_answer_str == "等邊三角形" and user_answer == "正三角形":
        is_correct = True
        
    # Numerical comparison
    if not is_correct:
        try:
            user_val = float(user_answer)
            correct_val = float(correct_answer_str)
            if abs(user_val - correct_val) < 1e-9:
                is_correct = True
        except (ValueError, TypeError):
            pass

    # Format feedback
    is_numerical_answer = False
    try:
        float(correct_answer_str)
        is_numerical_answer = True
    except (ValueError, TypeError):
        pass

    if is_numerical_answer:
        display_answer = f"${correct_answer_str}$"
    else:
        display_answer = correct_answer_str

    if is_correct:
        result_text = f"完全正確！答案是 {display_answer}。"
    else:
        result_text = f"答案不正確。正確答案應為：{display_answer}"
    
    return {"correct": is_correct, "result": result_text, "next_question": True}