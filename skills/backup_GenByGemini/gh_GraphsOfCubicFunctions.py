import random
import math
from fractions import Fraction
import matplotlib.pyplot as plt
import numpy as np
import os
import uuid
import re

# Helper function to plot a cubic function and its symmetry center
def _plot_cubic_function(a, h, p, k, equation_label="", center_label="", filename=None, x_range_start=-5, x_range_end=5):
    plt.clf() # Clear the current figure
    plt.figure(figsize=(7, 7))
    ax = plt.gca()

    x_values = np.linspace(h + x_range_start, h + x_range_end, 400) # Range around h
    y_values = a * (x_values - h)**3 + p * (x_values - h) + k

    ax.plot(x_values, y_values, label=equation_label, color='blue', linewidth=2)
    
    # Plot symmetry center
    ax.scatter([h], [k], color='red', s=100, zorder=5, label=center_label)
    ax.text(h + 0.2, k + 0.2, f'$({h},{k})$', color='red', fontsize=12)

    ax.axhline(0, color='gray', linewidth=0.5)
    ax.axvline(0, color='gray', linewidth=0.5)
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.set_xlabel('$x$')
    ax.set_ylabel('$y$')
    ax.set_title(f"Graph of $y={equation_label.replace('y=', '')}$") # Title for the plot
    ax.legend()

    # Adjust limits to make the plot look good
    y_min, y_max = np.min(y_values), np.max(y_values)
    y_plot_range = y_max - y_min
    
    # Ensure the y-axis range isn't too extreme for steep graphs, centered around k
    if y_plot_range > 50 or abs(y_max) > 50 or abs(y_min) > 50: 
        ax.set_ylim(k - 25, k + 25)
    else:
        ax.set_ylim(y_min - 0.1 * y_plot_range, y_max + 0.1 * y_plot_range)

    ax.set_xlim(h + x_range_start - 0.5, h + x_range_end + 0.5)
    ax.set_aspect('equal', adjustable='box')

    if filename:
        plot_dir = 'static/generated_plots'
        os.makedirs(plot_dir, exist_ok=True)
        filepath = os.path.join(plot_dir, filename)
        plt.savefig(filepath, bbox_inches='tight')
        plt.close()
        return filepath
    plt.close()
    return None

# Problem Type 1: Find Symmetry Center (from y = a(x-h)^3 + p(x-h) + k)
def _generate_symmetry_center_translated():
    a = random.choice([-2, -1, 1, 2])
    h = random.randint(-4, 4)
    k = random.randint(-4, 4)
    p = random.choice([-3, -2, -1, 1, 2, 3]) # p != 0 to make it not just y=ax^3 translated unless specifically desired

    # Construct the function string for LaTeX
    func_parts = []
    if a == 1:
        func_parts.append(r"(x-" + str(h) + r")^{{3}}") if h != 0 else r"x^{{3}}"
    elif a == -1:
        func_parts.append(r"-(x-" + str(h) + r")^{{3}}") if h != 0 else r"-x^{{3}}"
    else:
        if h != 0:
            func_parts.append(f"{a}(x-{h})^{{3}}")
        else:
            func_parts.append(f"{a}x^{{3}}")

    if p != 0:
        if p == 1:
            func_parts.append(f" +(x-{h})") if h != 0 else f" +x"
        elif p == -1:
            func_parts.append(f" -(x-{h})") if h != 0 else f" -x"
        elif p > 0:
            func_parts.append(f" +{p}(x-{h})") if h != 0 else f" +{p}x"
        else: # p < 0
            func_parts.append(f" {p}(x-{h})") if h != 0 else f" {p}x"

    if k > 0:
        func_parts.append(f" +{k}")
    elif k < 0:
        func_parts.append(f" {k}")

    func_str = "".join(func_parts)
    func_str = func_str.replace("+-", "-").replace("--", "+") # Clean up signs like +(-2) to -2, -(-2) to +2
    if func_str.startswith("+"): func_str = func_str[1:] # remove leading + if exists

    # Generate plot
    unique_id = uuid.uuid4()
    filename = f"gh_GraphsOfCubicFunctions_{unique_id}.png"
    filepath = _plot_cubic_function(a, h, p, k, equation_label=f"y={func_str}", center_label="對稱中心", filename=filename)

    question_text = f"已知三次函數 $y={func_str}$ 的圖形如圖所示，請找出其對稱中心。<br><img src='/static/generated_plots/{filename}' alt='Cubic function graph'>"
    correct_answer = f"({h},{k})"
    
    return {
        "question_text": question_text,
        "answer": correct_answer, # Answer format is (h,k)
        "correct_answer": correct_answer
    }

# Problem Type 2: Convert General Form to Standard Form and Find Symmetry Center
def _generate_symmetry_center_general():
    a = random.choice([-2, -1, 1, 2])
    h = random.randint(-3, 3)
    k = random.randint(-3, 3)
    p = random.choice([-3, -2, -1, 0, 1, 2, 3]) # p can be 0 here

    # Expand y = a(x-h)^3 + p(x-h) + k to ax^3 + bx^2 + cx + d
    A_coeff = a
    B_coeff = -3 * a * h
    C_coeff = 3 * a * h**2 + p
    D_coeff = -a * h**3 - p * h + k

    # Construct the function string in general form for LaTeX
    general_func_parts = []
    if A_coeff == 1:
        general_func_parts.append(r"x^{{3}}")
    elif A_coeff == -1:
        general_func_parts.append(r"-x^{{3}}")
    else:
        general_func_parts.append(f"{A_coeff}x^{{3}}")

    if B_coeff != 0:
        if B_coeff == 1:
            general_func_parts.append(r" +x^{{2}}")
        elif B_coeff == -1:
            general_func_parts.append(r" -x^{{2}}")
        elif B_coeff > 0:
            general_func_parts.append(f" +{B_coeff}x^{{2}}")
        else:
            general_func_parts.append(f" {B_coeff}x^{{2}}")

    if C_coeff != 0:
        if C_coeff == 1:
            general_func_parts.append(r" +x")
        elif C_coeff == -1:
            general_func_parts.append(r" -x")
        elif C_coeff > 0:
            general_func_parts.append(f" +{C_coeff}x")
        else:
            general_func_parts.append(f" {C_coeff}x")

    if D_coeff != 0:
        if D_coeff > 0:
            general_func_parts.append(f" +{D_coeff}")
        else:
            general_func_parts.append(f" {D_coeff}")

    general_func_str = "".join(general_func_parts).replace("+-", "-").replace("--", "+")
    if general_func_str.startswith("+"): general_func_str = general_func_str[1:] # remove leading + if exists

    # Generate plot for the general form
    unique_id = uuid.uuid4()
    filename = f"gh_GraphsOfCubicFunctions_{unique_id}.png"
    filepath = _plot_cubic_function(A_coeff, h, p, k, equation_label=f"y={general_func_str}", center_label="對稱中心", filename=filename)

    question_text = f"將三次函數 $y={general_func_str}$ 表示成 $y=A(x-H)^{{3}}+P(x-H)+K$ 的形式，並找出其對稱中心。<br><img src='/static/generated_plots/{filename}' alt='Cubic function graph'>"
    correct_answer = f"({h},{k})" # Answer format is (h,k)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

# Helper function to format coefficients nicely for LaTeX
def _format_coeff_for_label(coeff):
    if coeff == 1:
        return ""
    if coeff == -1:
        return "-"
    fraction = Fraction(coeff).limit_denominator(4)
    if fraction.denominator == 1:
        return str(fraction.numerator)
    return f"\\frac{{{fraction.numerator}}}{{{fraction.denominator}}}"

# Problem Type 3: Graph Identification (Matching function to a curve by color)
def _generate_graph_identification_problem():
    plt.clf()
    plt.figure(figsize=(8, 8))
    ax = plt.gca()

    x_values = np.linspace(-3, 3, 400)
    
    # Pool of distinct cubic functions (right-hand side of y=f(x))
    func_pool = [
        {'a': 1, 'h': 0, 'p': 0, 'k': 0, 'label_text': r"x^{{3}}"},
        {'a': -1, 'h': 0, 'p': 0, 'k': 0, 'label_text': r"-x^{{3}}"},
        {'a': 2, 'h': 0, 'p': 0, 'k': 0, 'label_text': r"2x^{{3}}"},
        {'a': 0.5, 'h': 0, 'p': 0, 'k': 0, 'label_text': r"\\frac{{1}}{{2}}x^{{3}}"},
        {'a': 1, 'h': 0, 'p': -1, 'k': 0, 'label_text': r"x^{{3}}-x"},
        {'a': 1, 'h': 0, 'p': 2, 'k': 0, 'label_text': r"x^{{3}}+2x"},
        {'a': -1, 'h': 0, 'p': 1, 'k': 0, 'label_text': r"-x^{{3}}+x"},
    ]
    
    chosen_funcs = random.sample(func_pool, 3) # Select 3 unique functions
    
    # Shuffle colors and labels for presentation
    plot_colors = ['red', 'blue', 'green']
    func_letters = ['A', 'B', 'C']
    random.shuffle(plot_colors)
    random.shuffle(func_letters)

    min_y, max_y = float('inf'), float('-inf')

    # Plot each chosen function
    for i, func_info in enumerate(chosen_funcs):
        a, h, p, k = func_info['a'], func_info['h'], func_info['p'], func_info['k']
        y_values = a * (x_values - h)**3 + p * (x_values - h) + k
        ax.plot(x_values, y_values, color=plot_colors[i], label=f"Curve {plot_colors[i]}", linewidth=2)
        
        min_y = min(min_y, np.min(y_values))
        max_y = max(max_y, np.max(y_values))

    ax.axhline(0, color='gray', linewidth=0.5)
    ax.axvline(0, color='gray', linewidth=0.5)
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.set_xlabel('$x$')
    ax.set_ylabel('$y$')
    ax.set_title("三次函數圖形匹配")
    # Legend is used internally for matplotlib, but actual matching is by color text
    
    # Adjust y-limits
    y_range = max_y - min_y
    # Ensure a reasonable fixed range around origin if functions are all centered at (0,0)
    # or ensure all curves are visible but not too stretched
    if y_range < 1: # Avoid division by zero if all y values are same or very close
        y_range = 1
    ax.set_ylim(min_y - 0.1 * y_range - 1, max_y + 0.1 * y_range + 1)
    ax.set_xlim(-3.5, 3.5)
    ax.set_aspect('equal', adjustable='box') # Keep aspect ratio for visual clarity

    unique_id = uuid.uuid4()
    filename = f"gh_GraphsOfCubicFunctions_{unique_id}.png"
    filepath = os.path.join('static/generated_plots', filename)
    os.makedirs('static/generated_plots', exist_ok=True)
    plt.savefig(filepath, bbox_inches='tight')
    plt.close()

    # Construct the question text for matching, as in the example
    question_text = "請將下列函數連到所對應的函數圖形之顏色上：<br>"
    
    answer_pairs_for_check = []
    
    # Present functions with A, B, C labels
    for i in range(len(chosen_funcs)):
        func_info = chosen_funcs[i]
        assigned_letter = func_letters[i] # The letter for this function
        assigned_color = plot_colors[i] # The color this function was plotted with
        
        question_text += f"\\quad ({assigned_letter}) $y={func_info['label_text']}$<br>"
        answer_pairs_for_check.append(f"{assigned_letter}:{assigned_color}")
            
    question_text += f"<img src='/static/generated_plots/{filename}' alt='Cubic function graph'>"
    
    # The correct answer should be a string like "A:red,B:blue,C:green"
    answer_pairs_for_check.sort() # Ensure consistent order for checking
    correct_answer = ",".join(answer_pairs_for_check)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def generate(level=1):
    """
    生成「三次函數圖形」相關題目。
    包含：
    1. 找出平移後三次函數的對稱中心 (y=a(x-h)^3+p(x-h)+k)
    2. 找出一般式三次函數的對稱中心 (y=ax^3+bx^2+cx+d)
    3. 函數圖形與函數式的匹配
    """
    
    problem_types = [
        'symmetry_center_translated',
        'symmetry_center_general',
        'graph_identification'
    ]
    
    # Adjust problem difficulty based on level (if applicable)
    # For now, all types can be chosen randomly.
    problem_type = random.choice(problem_types)

    if problem_type == 'symmetry_center_translated':
        return _generate_symmetry_center_translated()
    elif problem_type == 'symmetry_center_general':
        return _generate_symmetry_center_general()
    else: # 'graph_identification'
        return _generate_graph_identification_problem()


def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()

    is_correct = False
    feedback = ""

    # Attempt to parse as (h,k) coordinates
    coord_pattern = r"\((-?\d+),(-?\d+)\)"
    user_match = re.match(coord_pattern, user_answer)
    correct_match = re.match(coord_pattern, correct_answer)

    if user_match and correct_match:
        try:
            user_h, user_k = int(user_match.group(1)), int(user_match.group(2))
            correct_h, correct_k = int(correct_match.group(1)), int(correct_match.group(2))
            if user_h == correct_h and user_k == correct_k:
                is_correct = True
                feedback = f"完全正確！對稱中心是 $({correct_h},{correct_k})$。"
            else:
                feedback = f"答案不正確。正確的對稱中心應為 $({correct_h},{correct_k})$。"
        except ValueError:
            feedback = f"答案格式不正確。請以 (h,k) 格式輸入。"
    
    # Attempt to parse as comma-separated color matches (e.g., A:red,B:blue,C:green)
    elif ':' in user_answer and ',' in user_answer:
        def parse_matches(s):
            matches = {}
            for part in s.split(','):
                if ':' in part:
                    key, value = part.split(':', 1)
                    matches[key.strip().upper()] = value.strip().lower()
            return matches

        user_matches = parse_matches(user_answer)
        correct_matches = parse_matches(correct_answer)

        if user_matches == correct_matches:
            is_correct = True
            feedback = f"完全正確！"
        else:
            incorrect_parts = []
            for key, value in correct_matches.items():
                if key not in user_matches:
                    incorrect_parts.append(f"函數 ${key}$ 的匹配遺失。")
                elif user_matches[key] != value:
                    incorrect_parts.append(f"函數 ${key}$ 應匹配為 {value} 曲線。")
            if incorrect_parts:
                feedback = f"答案不正確。{' '.join(incorrect_parts)}"
            else: # Fallback if specific feedback fails unexpectedly
                 feedback = f"答案不正確。請檢查您的匹配。"

    else:
        # Fallback for simple string comparison if no specific format matches
        # (Though current problem types should mostly fall into the above categories)
        if user_answer.lower() == correct_answer.lower():
            is_correct = True
            feedback = f"完全正確！答案是 ${correct_answer}$。"
        else:
            feedback = f"答案不正確。正確答案應為：${correct_answer}$"


    return {"correct": is_correct, "result": feedback, "next_question": True}