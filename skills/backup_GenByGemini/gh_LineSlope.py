import random
from fractions import Fraction
import math

# Helper function to generate a random point (x, y)
def generate_point(min_coord, max_coord):
    return (random.randint(min_coord, max_coord), random.randint(min_coord, max_coord))

# Helper function to calculate slope
def calculate_slope(p1, p2):
    x1, y1 = p1
    x2, y2 = p2

    dx = x2 - x1
    dy = y2 - y1

    if dx == 0:
        return "undefined" # Vertical line
    elif dy == 0:
        return Fraction(0, 1) # Horizontal line, slope is 0
    else:
        return Fraction(dy, dx) # General case

def generate(level=1):
    problem_type = random.choice([
        'slope_from_two_points',
        'slope_comparison',
        'special_cases'
    ])

    if level == 1:
        # Simpler points, often leading to integer slopes or simple fractions.
        min_coord = -5
        max_coord = 5
    elif level == 2:
        # Wider range, more likely to get fractions.
        min_coord = -10
        max_coord = 10
    else: # level 3
        # Even wider range, potentially larger numbers.
        min_coord = -15
        max_coord = 15

    if problem_type == 'slope_from_two_points':
        return generate_slope_from_two_points_problem(min_coord, max_coord)
    elif problem_type == 'slope_comparison':
        return generate_slope_comparison_problem(min_coord, max_coord)
    else: # special_cases
        return generate_special_cases_problem(min_coord, max_coord)

def generate_slope_from_two_points_problem(min_coord, max_coord):
    p1 = generate_point(min_coord, max_coord)
    p2 = generate_point(min_coord, max_coord)

    # Ensure points are distinct for slope calculation
    while p1 == p2:
        p2 = generate_point(min_coord, max_coord)

    # Calculate the correct slope
    correct_slope = calculate_slope(p1, p2)

    question_text = f"已知坐標平面上兩點 $A({p1[0]}, {p1[1]})$ 和 $B({p2[0]}, {p2[1]})$，請求出直線 $AB$ 的斜率。"
    
    # Format the correct answer for display and internal comparison
    if correct_slope == "undefined":
        formatted_answer = "undefined"
    elif correct_slope.denominator == 1:
        formatted_answer = str(correct_slope.numerator)
    else:
        formatted_answer = f"{correct_slope.numerator}/{correct_slope.denominator}"

    return {
        "question_text": question_text,
        "answer": formatted_answer, # For display purposes primarily
        "correct_answer": formatted_answer # Actual value for check function
    }

def generate_slope_comparison_problem(min_coord, max_coord):
    num_lines = random.randint(3, 5) # Generate 3 to 5 lines
    lines_data = []
    slopes_values = set() # Use a set to track unique slopes
    labels = [f'L_{{i}}' for i in range(1, 6)] # Labels for lines, e.g., L_1, L_2
    
    # Randomly decide if all lines pass through a common anchor point (like example) or are independent
    use_anchor_point = random.choice([True, False]) 
    
    anchor_point = None
    if use_anchor_point:
        anchor_point = generate_point(min_coord, max_coord)

    attempts = 0
    while len(lines_data) < num_lines and attempts < 100:
        p1_line, p2_line = (0,0), (0,0) # Initialize to ensure distinct points are chosen
        if use_anchor_point:
            p1_line = anchor_point
            p2_line = generate_point(min_coord, max_coord)
            while p2_line == anchor_point: # Ensure p2 is distinct from anchor
                p2_line = generate_point(min_coord, max_coord)
        else:
            p1_line = generate_point(min_coord, max_coord)
            p2_line = generate_point(min_coord, max_coord)
            while p1_line == p2_line: # Ensure two points for a line are distinct
                p2_line = generate_point(min_coord, max_coord)
        
        current_slope = calculate_slope(p1_line, p2_line)
        
        # Add to lines_data only if slope is unique. Allow only one "undefined" slope for clarity.
        if current_slope == "undefined":
            if "undefined" not in slopes_values:
                slopes_values.add(current_slope)
                lines_data.append({
                    "label": labels[len(lines_data)],
                    "p1": p1_line,
                    "p2": p2_line,
                    "slope": current_slope
                })
        elif current_slope not in slopes_values:
            slopes_values.add(current_slope)
            lines_data.append({
                "label": labels[len(lines_data)],
                "p1": p1_line,
                "p2": p2_line,
                "slope": current_slope
            })
        
        attempts += 1
    
    # If not enough distinct slopes/lines were generated, fallback to a simpler problem.
    if len(lines_data) < 2: # Need at least two lines for comparison
        return generate_slope_from_two_points_problem(min_coord, max_coord) 
    
    # Custom sort key for mixed types (Fraction and "undefined")
    def sort_key(slope_val):
        if slope_val == "undefined":
            return float('inf') # undefined is conceptually the "largest" for comparison order
        return float(slope_val) # Convert Fraction to float for comparison

    # Sort lines by their slope values
    lines_data.sort(key=lambda x: sort_key(x['slope']))

    # Prepare question text
    line_statements = []
    for line in lines_data:
        p1_display = line['p1']
        p2_display = line['p2']
        line_statements.append(f"直線 ${line['label']}$ 通過點 $({p1_display[0]}, {p1_display[1]})$ 和 $({p2_display[0]}, {p2_display[1]})$")
    
    question_text = f"已知坐標平面上有 {len(lines_data)} 條直線：<br>" + "<br>".join(line_statements)
    
    # Correct answer is the sequence of labels
    correct_answer_labels = [line['label'] for line in lines_data]
    
    # Randomly choose ascending or descending order for the question
    if random.random() < 0.5: # Ascending order
        operator = "<"
        correct_answer = operator.join(correct_answer_labels)
        question_text += r"<br>請將這些直線的斜率由小到大排列。（請以 'L_A < L_B < L_C' 的格式作答，例如：$L_{{1}} < L_{{2}}$）"
    else: # Descending order
        operator = ">"
        correct_answer = operator.join(reversed(correct_answer_labels))
        question_text += r"<br>請將這些直線的斜率由大到小排列。（請以 'L_A > L_B > L_C' 的格式作答，例如：$L_{{1}} > L_{{2}}$）"

    return {
        "question_text": question_text,
        "answer": correct_answer, 
        "correct_answer": correct_answer
    }

def generate_special_cases_problem(min_coord, max_coord):
    sub_type = random.choice(['horizontal_slope', 'vertical_slope', 'positive_trend', 'negative_trend', 'zero_trend', 'undefined_trend'])

    if sub_type == 'horizontal_slope':
        y_coord = random.randint(min_coord, max_coord)
        x1 = random.randint(min_coord, max_coord - 1)
        x2 = random.randint(x1 + 1, max_coord) # Ensure x1 != x2
        p1 = (x1, y_coord)
        p2 = (x2, y_coord)
        question_text = f"已知直線通過點 $A({p1[0]}, {p1[1]})$ 和 $B({p2[0]}, {p2[1]})$，請問這條直線的斜率為何？"
        correct_answer = "0"
    elif sub_type == 'vertical_slope':
        x_coord = random.randint(min_coord, max_coord)
        y1 = random.randint(min_coord, max_coord - 1)
        y2 = random.randint(y1 + 1, max_coord) # Ensure y1 != y2
        p1 = (x_coord, y1)
        p2 = (x_coord, y2)
        question_text = f"已知直線通過點 $A({p1[0]}, {p1[1]})$ 和 $B({p2[0]}, {p2[1]})$，請問這條直線的斜率為何？"
        correct_answer = "undefined"
    elif sub_type == 'positive_trend':
        question_text = r"請問斜率為正數的直線，在坐標平面上的趨勢是什麼？<br>(A) 從左下到右上 (B) 從左上到右下 (C) 水平線 (D) 垂直線"
        correct_answer = "A"
    elif sub_type == 'negative_trend':
        question_text = r"請問斜率為負數的直線，在坐標平面上的趨勢是什麼？<br>(A) 從左下到右上 (B) 從左上到右下 (C) 水平線 (D) 垂直線"
        correct_answer = "B"
    elif sub_type == 'zero_trend':
        question_text = r"請問斜率為零的直線，在坐標平面上的趨勢是什麼？<br>(A) 從左下到右上 (B) 從左上到右下 (C) 水平線 (D) 垂直線"
        correct_answer = "C"
    else: # undefined_trend
        question_text = r"請問斜率未定義的直線，在坐標平面上的趨勢是什麼？<br>(A) 從左下到右上 (B) 從左上到右下 (C) 水平線 (D) 垂直線"
        correct_answer = "D"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    # Normalize both user and correct answers for robust comparison
    # Remove spaces, '$', '\', '{', '}' to handle LaTeX formatting in labels
    user_answer_processed = user_answer.strip().lower().replace(" ", "").replace("$", "").replace("\\", "").replace("{", "").replace("}", "")
    correct_answer_processed = correct_answer.strip().lower().replace(" ", "").replace("$", "").replace("\\", "").replace("{", "").replace("}", "")
    
    is_correct = False
    feedback = ""

    if correct_answer_processed == "undefined":
        # Allow common Chinese equivalent or misspellings for "undefined"
        if user_answer_processed in ["undefined", "無意義", "wu意義", "undifined"]: 
            is_correct = True
        else:
            feedback = f"答案不正確。這是一條垂直線，斜率應為「未定義」或「無意義」。"
    elif 'l_' in correct_answer_processed: # Comparison problem (e.g., L_1<L_2 or L_1>L_2)
        user_operator = None
        if '<' in user_answer_processed:
            user_operator = '<'
        elif '>' in user_answer_processed:
            user_operator = '>'
        
        correct_operator = None
        if '<' in correct_answer_processed:
            correct_operator = '<'
        elif '>' in correct_answer_processed:
            correct_operator = '>'

        # Check if user used an operator and if it matches the correct answer's operator
        if user_operator is None or correct_operator is None or user_operator != correct_operator:
            feedback = f"比較符號不正確或格式錯誤。請使用 '<' 或 '>'。正確答案是：${correct_answer}$。"
        else:
            # Split both answers by the detected operator
            user_parts = [p.strip() for p in user_answer_processed.split(user_operator) if p.strip()]
            correct_parts = [p.strip() for p in correct_answer_processed.split(correct_operator) if p.strip()]
            
            # Compare the ordered parts
            if len(user_parts) == len(correct_parts) and all(u == c for u, c in zip(user_parts, correct_parts)):
                is_correct = True
            else:
                feedback = f"順序不正確。正確答案是：${correct_answer}$。"

    elif correct_answer_processed in ['a', 'b', 'c', 'd']: # Multiple choice for special cases
        if user_answer_processed.upper() == correct_answer_processed.upper():
            is_correct = True
        else:
            feedback = f"選項不正確。正確答案是 ${correct_answer}$。"
    else: # Numerical slope (Fraction or integer)
        try:
            # Convert user answer to Fraction
            user_fraction = None
            if '/' in user_answer_processed:
                num_str, den_str = user_answer_processed.split('/')
                num = int(num_str)
                den = int(den_str)
                if den == 0: raise ZeroDivisionError # Prevent Fraction(x,0)
                user_fraction = Fraction(num, den)
            else:
                user_fraction = Fraction(float(user_answer_processed)).limit_denominator(1000)
            
            # Convert correct answer to Fraction
            correct_fraction = None
            if '/' in correct_answer_processed:
                num_str, den_str = correct_answer_processed.split('/')
                num = int(num_str)
                den = int(den_str)
                if den == 0: raise ZeroDivisionError
                correct_fraction = Fraction(num, den)
            else:
                correct_fraction = Fraction(float(correct_answer_processed)).limit_denominator(1000)

            if user_fraction == correct_fraction:
                is_correct = True
            else:
                feedback = f"答案計算不正確。正確答案是 ${correct_answer}$。"
        except (ValueError, ZeroDivisionError):
            feedback = f"答案格式不正確或計算錯誤。正確答案是 ${correct_answer}$。"

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else (feedback if feedback else f"答案不正確。正確答案應為：${correct_answer}$")
    return {"correct": is_correct, "result": result_text, "next_question": True}