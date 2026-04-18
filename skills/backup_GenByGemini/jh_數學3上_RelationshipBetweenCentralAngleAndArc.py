import random
from fractions import Fraction
import math

# --- Helper Functions ---

def format_pi_fraction(frac: Fraction):
    """Formats a Fraction object into a LaTeX string with pi."""
    if frac.numerator == 0:
        return "0"
        
    if frac.denominator == 1:
        if abs(frac.numerator) == 1:
            return f"{'' if frac.numerator > 0 else '-'}\\pi"
        else:
            return f"{frac.numerator}\\pi"
    else:
        sign = "" if frac.numerator > 0 else "-"
        num = abs(frac.numerator)
        den = frac.denominator
        return f"{sign}\\frac{{{num}}}{{{den}}}\\pi"

def format_number(val):
    """Formats a number, converting float to int if possible."""
    if isinstance(val, float) and val.is_integer():
        return int(val)
    return val

# --- Problem Generation Functions ---

def generate_arc_length_and_degree():
    """
    Asks for arc degree or arc length given a central angle and radius.
    Covers concepts from Examples 1, 2, 3.
    """
    radius = random.randint(5, 25)
    # Use angles that result in simple fractions of 360
    angle_choices = [30, 45, 60, 72, 90, 120, 135, 150, 180, 210, 240, 270, 300]
    angle = random.choice(angle_choices)
    
    task = random.choice(['degree', 'length'])
    
    if task == 'degree':
        question_text = f"在一個半徑為 ${radius}$ 公分的圓中，一個圓心角為 ${angle}^{{\\circ}}$ 的扇形，其所對應的弧度數為多少度？"
        correct_answer = str(angle)
    else: # task == 'length'
        question_text = f"在一個半徑為 ${radius}$ 公分的圓中，一個圓心角為 ${angle}^{{\\circ}}$ 的扇形，其弧長為多少公分？"
        
        # Arc length = 2 * pi * r * (angle / 360)
        # Calculate the coefficient of pi separately
        numerator = 2 * radius * angle
        denominator = 360
        
        # Fix: Ensure numerator and denominator are integers for Fraction
        arc_len_frac = Fraction(int(numerator), int(denominator))
        
        correct_answer = format_pi_fraction(arc_len_frac)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_divided_circle_problem():
    """
    A circle is divided into n equal parts. Find degree/length of a composite arc.
    Based on Example 1.
    """
    n_parts = random.choice([6, 8, 9, 10, 12, 15, 18])
    angle_per_part = 360 / n_parts
    radius = random.randint(10, 40)
    
    # Number of parts can be an integer or a half-integer
    num_parts = random.choice([2, 3, 4, 1.5, 2.5, 3.5])
    
    total_angle = angle_per_part * num_parts
    
    task = random.choice(['degree', 'length'])
    
    if task == 'degree':
        question_text = f"如圖，一圓 O 被虛線分成 ${n_parts}$ 等分。若有一段弧橫跨了 ${num_parts}$ 個等分，則此弧所對的圓心角為多少度？"
        correct_answer = str(format_number(total_angle))
    else: # task == 'length'
        question_text = f"如圖，一圓 O 的半徑為 ${radius}$ 公分，且被虛線分成 ${n_parts}$ 等分。若有一段弧的長度相當於 ${num_parts}$ 個等分，則此弧長為多少公分？"
        # Arc length = 2 * pi * r * (angle / 360)
        # angle/360 is simply num_parts / n_parts
        
        # Using Fraction allows us to handle float num_parts (like 1.5) cleanly
        # 1.5/6 -> 3/12 -> 1/4
        ratio = Fraction(num_parts / n_parts).limit_denominator()
        
        arc_len_frac = Fraction(2 * radius) * ratio
        correct_answer = format_pi_fraction(arc_len_frac)
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_polygon_central_angle():
    """
    Asks for the central angle subtended by a number of sides of an inscribed regular polygon.
    Based on Example 6.
    """
    polygon_names = {5: "五", 6: "六", 8: "八", 9: "九", 10: "十", 12: "十二"}
    n_sides = random.choice(list(polygon_names.keys()))
    
    # The number of arcs to span
    num_arcs = random.randint(2, n_sides // 2)
    
    angle_per_arc = 360 / n_sides
    total_angle = angle_per_arc * num_arcs
    
    start_vertex = 'A'
    end_vertex = chr(ord('A') + num_arcs)
    
    question_text = f"一個正{polygon_names[n_sides]}邊形 ${'A' * (num_arcs+1)}$... 的所有頂點皆在圓 O 上，請問圓心角 $\\angle {start_vertex}O{end_vertex}$ 的度數為多少？"
    
    correct_answer = str(format_number(total_angle))
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_conceptual_relations():
    """
    Asks conceptual questions about the relationship between arcs and chords.
    Based on Examples 4 and 5.
    """
    problem_type = random.choice(['arc_to_chord', 'chord_to_arc'])
    
    if problem_type == 'arc_to_chord':
        question_text = "在同一個圓中，若兩段弧的『度數』相等（等弧），則它們所對應的『弦長』是否也會相等？ (請回答 '是' 或 '否')"
        correct_answer = "是"
    else: # chord_to_arc
        question_text = "在同一個圓中，若兩條弦的『長度』相等（等弦），則它們所對應的弧『度數』是否也會相等？ (請回答 '是' 或 '否')"
        correct_answer = "是"
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

# --- Main Functions ---

def generate(level=1):
    """
    Generates a question for the skill 'Relationship Between Central Angle and Arc'.
    
    The function selects one of the following problem types:
    1.  `arc_length_and_degree`: Basic calculation of arc length or degree from radius and central angle.
    2.  `divided_circle_problem`: A circle is divided into n parts, find the length/degree of a composite arc.
    3.  `polygon_central_angle`: Find the central angle in a circle with an inscribed regular polygon.
    4.  `conceptual_relations`: Asks about the core theorems (equal arcs <=> equal chords).
    """
    
    # Distribute problem types based on commonality
    problem_type_pool = [
        'arc_length_and_degree', 
        'arc_length_and_degree', 
        'divided_circle_problem',
        'polygon_central_angle',
        'conceptual_relations'
    ]
    
    problem_type = random.choice(problem_type_pool)

    if problem_type == 'arc_length_and_degree':
        return generate_arc_length_and_degree()
    elif problem_type == 'divided_circle_problem':
        return generate_divided_circle_problem()
    elif problem_type == 'polygon_central_angle':
        return generate_polygon_central_angle()
    else: # conceptual_relations
        return generate_conceptual_relations()

def check(user_answer, correct_answer):
    """
    Checks if the user's answer is correct.
    This function is designed to be robust for math answers, handling:
    - Text answers (e.g., '是', '否').
    - Numerical answers (e.g., '144', '67.5').
    - Answers with pi (e.g., '15/2 pi', '7.5pi', '15/2 π').
    """
    # Normalize user's answer
    user_answer_norm = user_answer.strip().lower()
    user_answer_norm = user_answer_norm.replace('π', 'pi').replace(' ', '')
    
    # Normalize correct answer for comparison
    correct_answer_norm = correct_answer.strip().lower()
    # Handle conceptual answers like '是' or '否'
    if correct_answer_norm in ['是', '否']:
        is_correct = (user_answer_norm == correct_answer_norm)
    else:
        # For numerical/pi answers, prepare a comparable string
        correct_answer_comp = correct_answer_norm.replace('\\circ', '')
        correct_answer_comp = correct_answer_comp.replace('\\frac{', '').replace('}{', '/').replace('}', '')
        correct_answer_comp = correct_answer_comp.replace('\\pi', 'pi').replace(' ', '')

        # Direct string comparison first
        if user_answer_norm == correct_answer_comp:
            is_correct = True
        else:
            # If direct comparison fails, try numerical evaluation
            try:
                user_has_pi = 'pi' in user_answer_norm
                correct_has_pi = 'pi' in correct_answer_comp

                if user_has_pi != correct_has_pi:
                    is_correct = False
                else:
                    user_val_str = user_answer_norm.replace('pi', '')
                    corr_val_str = correct_answer_comp.replace('pi', '')

                    # Allow empty string for answers like "pi" (value = 1)
                    if user_val_str == '' or user_val_str == '-':
                        user_val_str += '1'
                    if corr_val_str == '' or corr_val_str == '-':
                        corr_val_str += '1'

                    # Evaluate fractions like '15/2'
                    if '/' in user_val_str:
                        num, den = map(float, user_val_str.split('/'))
                        user_val = num / den
                    else:
                        user_val = float(user_val_str)
                    
                    if '/' in corr_val_str:
                        num, den = map(float, corr_val_str.split('/'))
                        corr_val = num / den
                    else:
                        corr_val = float(corr_val_str)
                    
                    # Compare with a tolerance for floating point inaccuracies
                    is_correct = math.isclose(user_val, corr_val)

            except (ValueError, ZeroDivisionError):
                # If conversion to number fails, it's incorrect
                is_correct = False
    
    # Add degree symbol to numerical answers for display if it was in the original
    if '\\circ' in correct_answer:
        display_answer = correct_answer
    elif '°' in correct_answer:
        display_answer = correct_answer.replace('°', '^{\\circ}')
    else:
        # Check if the answer is purely numerical (and not conceptual) before adding degree sign
        try:
            float(correct_answer)
            # This is a bit ambiguous, so we'll stick to formatting only if symbol is present
            # For this skill, degrees are usually explicitly stated in the question
            display_answer = correct_answer
        except ValueError:
             display_answer = correct_answer
             
    result_text = f"完全正確！答案是 ${display_answer}$。" if is_correct else f"答案不正確。正確答案應為：${display_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}