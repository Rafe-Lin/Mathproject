import random
from fractions import Fraction

def format_scale_factor_for_question(num):
    """Formats a number (int, float, Fraction) into a LaTeX-compatible string for questions."""
    if isinstance(num, Fraction):
        if num.denominator == 1:
            return str(num.numerator)
        else:
            # Using \\frac for better rendering in LaTeX
            return f"\\frac{{{num.numerator}}}{{{num.denominator}}}"
    if isinstance(num, float) and num.is_integer():
        return str(int(num))
    return str(num)

def format_answer(num):
    """Formats a number into a clean string for the answer key (e.g., no trailing .0)."""
    # This handles Fraction, float, int
    val = float(num)
    if val.is_integer():
        return str(int(val))
    else:
        # Round to avoid potential floating point representation issues, though unlikely with these numbers
        return f'{val:.10f}'.rstrip('0').rstrip('.')

def generate_regular_polygon_scaling_problem():
    """
    Generates a problem about scaling a regular polygon.
    Asks for the new side length and the new interior angle.
    """
    polygons = {
        '正三角形': 3, '正方形': 4, '正五邊形': 5,
        '正六邊形': 6, '正八邊形': 8, '正十二邊形': 12
    }
    poly_name, n_sides = random.choice(list(polygons.items()))
    original_length = random.randint(2, 10)
    
    scale_factor_options = [2, 3, 4, 1.5, 2.5, 0.5]
    if original_length % 4 == 0:
        scale_factor_options.append(0.25)
    if original_length % 3 == 0:
        scale_factor_options.extend([Fraction(1, 3), Fraction(2, 3)])

    scale_factor = random.choice(scale_factor_options)
    
    new_length = original_length * scale_factor
    angle = 180 * (n_sides - 2) / n_sides
    
    scale_str = format_scale_factor_for_question(scale_factor)
    
    question_text = f"一個邊長為 ${original_length}$ 公分的{poly_name}，將它縮放 ${scale_str}$ 倍後，其縮放圖形的邊長與一內角度數分別為多少？<br>(請依序回答邊長和角度，並以逗號分隔，例如: 2.5,108)"
    
    new_length_str = format_answer(new_length)
    angle_str = format_answer(angle)
    
    correct_answer = f"{new_length_str},{angle_str}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_line_segment_scaling_problem():
    """
    Generates a problem about scaling a line segment.
    Asks for the new length.
    """
    original_length = random.randint(5, 20)
    
    scale_factor_options = [2, 3, 4, 5, 1.5, 2.5, 0.5]
    if original_length % 4 == 0:
        scale_factor_options.extend([Fraction(1, 4), 0.25])
    if original_length % 3 == 0:
        scale_factor_options.append(Fraction(1, 3))
    
    scale_factor = random.choice(scale_factor_options)
    new_length = original_length * scale_factor
    
    scale_str = format_scale_factor_for_question(scale_factor)

    question_text = f"一線段 $\\overline{{AB}}$ 的長度為 ${original_length}$ 公分，若以某點為中心將其縮放 ${scale_str}$ 倍，則縮放後的新線段 $\\overline{{A'B'}}$ 長度為多少公分？"
    
    correct_answer = format_answer(new_length)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_conceptual_choice_problem():
    """
    Generates a multiple-choice question about the properties of scaling.
    """
    concept = random.choice(['angle', 'side', 'similarity'])
    shape = random.choice(['三角形', '四邊形', '五邊形', '多邊形'])
    
    if concept == 'angle':
        scale_factor = random.choice([2, 3, 0.5, Fraction(1, 3)])
        scale_str = format_scale_factor_for_question(scale_factor)
        question_text = f"將一個{shape}以某個中心點縮放 ${scale_str}$ 倍後，其縮放圖形中的『對應角』角度會如何變化？"
        options = [f'變為原來的 ${scale_str}$ 倍', '保持不變', '變為 0 度', '變為 180 度']
        correct_option = '保持不變'
    elif concept == 'side':
        k = random.choice(['2', '3', 'k'])
        question_text = f"將一個多邊形縮放 ${k}$ 倍（${k}>0$）後，其縮放圖形的『對應邊長』會變為原來的幾倍？"
        options = [f'${k}$ 倍', f'$\\frac{{1}}{{{k}}}$ 倍', f'${k}^2$ 倍', '不受影響']
        correct_option = f'${k}$ 倍'
    else: # similarity
        question_text = "將一個圖形進行縮放後，得到的縮放圖形與原圖形必定存在下列何種關係？"
        options = ['全等', '相似', '面積相等', '以上皆非']
        correct_option = '相似'
    
    random.shuffle(options)
    correct_letter = chr(ord('A') + options.index(correct_option))
    
    options_str = "<br>".join([f"({chr(ord('A') + i)}) {opt}" for i, opt in enumerate(options)])
    
    full_question = f"{question_text}<br>{options_str}"
    
    return {
        "question_text": full_question,
        "answer": correct_letter,
        "correct_answer": correct_letter
    }

def generate(level=1):
    """
    Generates a question for the skill 'Scaling Figures'.

    This function randomly selects one of three problem types:
    1. regular_polygon_scaling: Calculate new side length and angle of a scaled regular polygon.
    2. line_segment_scaling: Calculate the new length of a scaled line segment.
    3. conceptual_choice: A multiple-choice question about the properties of scaling (angles, sides, similarity).
    """
    problem_type = random.choice(['regular_polygon_scaling', 'line_segment_scaling', 'conceptual_choice'])
    
    if problem_type == 'regular_polygon_scaling':
        return generate_regular_polygon_scaling_problem()
    elif problem_type == 'line_segment_scaling':
        return generate_line_segment_scaling_problem()
    else: # conceptual_choice
        return generate_conceptual_choice_problem()

def check(user_answer, correct_answer):
    """
    Checks the user's answer against the correct answer.
    Handles multiple-choice, single numeric, and comma-separated numeric answers.
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    
    # Handle multiple-choice answers (A, B, C, D)
    if correct_answer.isalpha() and len(correct_answer) == 1:
        is_correct = (user_answer.upper() == correct_answer.upper())
        result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
        return {"correct": is_correct, "result": result_text, "next_question": True}
        
    # Handle comma-separated answers like "2.5,108"
    if ',' in correct_answer:
        user_parts = [p.strip() for p in user_answer.split(',')]
        correct_parts = [p.strip() for p in correct_answer.split(',')]
        
        is_correct = False
        if len(user_parts) == len(correct_parts):
            try:
                # Compare parts as floating point numbers
                is_correct = all(abs(float(u) - float(c)) < 1e-9 for u, c in zip(user_parts, correct_parts))
            except (ValueError, TypeError):
                # Fallback to string comparison if conversion fails
                is_correct = (user_answer.replace(" ", "") == correct_answer.replace(" ", ""))

        correct_answer_latex = correct_answer.replace(",", ",\\ ")
        result_text = f"完全正確！答案是 ${correct_answer_latex}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer_latex}$"
        return {"correct": is_correct, "result": result_text, "next_question": True}
        
    # Handle single numeric answers
    is_correct = False
    try:
        is_correct = abs(float(user_answer) - float(correct_answer)) < 1e-9
    except (ValueError, TypeError):
        # Fallback for non-numeric single answers, though not expected in this skill
        is_correct = (user_answer.lower() == correct_answer.lower())
        
    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}