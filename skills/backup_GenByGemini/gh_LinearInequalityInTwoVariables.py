import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import uuid
import os
from fractions import Fraction
import numpy as np

# Define a directory for generated plots. This needs to be accessible by the web server.
# For local testing, ensure 'static/generated_plots' exists.
PLOT_DIR = 'static/generated_plots'
os.makedirs(PLOT_DIR, exist_ok=True)

def generate(level=1):
    """
    生成「二元一次不等式」相關題目 (包含圖形)。
    題目類型：
    1. 圖示單一二元一次不等式，並判斷某點是否在解區域內。
    2. 圖示二元一次聯立不等式，並判斷某點是否在解區域內。
    """
    
    problem_type = random.choice(['single_inequality', 'system_of_inequalities'])
    
    if problem_type == 'single_inequality':
        return generate_single_inequality_problem(level)
    else: # system_of_inequalities
        return generate_system_inequalities_problem(level)

def _generate_coefficients(min_val=-5, max_val=5, allow_zero_c=True):
    """Generates A, B, C for Ax + By + C = 0, ensuring A and B are not both zero."""
    A = random.randint(min_val, max_val)
    B = random.randint(min_val, max_val)
    # Ensure A and B are not both zero
    while A == 0 and B == 0:
        A = random.randint(min_val, max_val)
        B = random.randint(min_val, max_val)
    
    C = random.randint(min_val, max_val)
    if not allow_zero_c and C == 0:
        C = random.randint(min_val, max_val)
        while C == 0:
            C = random.randint(min_val, max_val)

    # To avoid all coefficients being too large, simplify by GCD
    coeffs = [A, B, C]
    non_zero_coeffs = [abs(c) for c in coeffs if c != 0]
    if non_zero_coeffs:
        gcd_val = non_zero_coeffs[0]
        for val in non_zero_coeffs[1:]:
            gcd_val = np.gcd(gcd_val, val)
        if gcd_val > 1:
            A //= gcd_val
            B //= gcd_val
            C //= gcd_val
    
    return A, B, C

def _get_inequality_string(A, B, C, op):
    """Formats Ax + By + C op 0 into a readable string for LaTeX."""
    parts = []
    
    # Handle Ax term
    if A != 0:
        if A == 1:
            parts.append("x")
        elif A == -1:
            parts.append("-x")
        else:
            parts.append(f"{A}x")
    
    # Handle By term
    if B != 0:
        if B == 1:
            parts.append(" + y" if parts else "y")
        elif B == -1:
            parts.append(" - y" if parts else "-y")
        else:
            parts.append(f"{'+' if B > 0 and parts else ''}{B}y")

    # Handle C term
    if C != 0:
        parts.append(f"{'+' if C > 0 and parts else ''}{C}")

    # Fallback if somehow all coeffs are zero (should be prevented by _generate_coefficients)
    if not parts:
        return f"0 {op} 0" 

    return f"{''.join(parts)} {op} 0"

def _get_condition(Z, op):
    """Returns a boolean array based on the operator for shading."""
    if op == '>':
        return Z > 0
    elif op == '>=':
        return Z >= 0
    elif op == '<':
        return Z < 0
    elif op == '<=':
        return Z <= 0
    return np.zeros_like(Z, dtype=bool) # Should not be reached with valid op

def _plot_line_segment(ax, A, B, C, op, x_min, x_max, y_min, y_max, label=""):
    """Plots a single boundary line segment."""
    is_strict = (op == '>' or op == '<')
    line_style = '--' if is_strict else '-'

    if B == 0: # Vertical line Ax + C = 0 => x = -C/A
        x_val = -Fraction(C, A)
        ax.plot([x_val, x_val], [y_min, y_max], line_style, color='black', lw=1.5, label=label)
    elif A == 0: # Horizontal line By + C = 0 => y = -C/B
        y_val = -Fraction(C, B)
        ax.plot([x_min, x_max], [y_val, y_val], line_style, color='black', lw=1.5, label=label)
    else: # General line y = (-A/B)x - C/B
        # Calculate points for plotting the line across the defined range
        # Use a higher resolution for x to ensure line goes through the boundary
        line_x = np.array([x_min, x_max])
        # Ensure float conversion for plotting
        line_y = (np.array([-Fraction(A, B) * val - Fraction(C, B) for val in line_x])).astype(float)
        ax.plot(line_x, line_y, line_style, color='black', lw=1.5, label=label)

def _check_point_in_region(A, B, C, op, px, py):
    """Checks if a point (px, py) satisfies Ax + By + C op 0."""
    val = A * px + B * py + C
    if op == '>':
        return val > 0
    elif op == '>=':
        return val >= 0
    elif op == '<':
        return val < 0
    elif op == '<=':
        return val <= 0
    return False

def generate_single_inequality_problem(level):
    fig, ax = plt.subplots(figsize=(6, 6))
    x_min, x_max = -10, 10
    y_min, y_max = -10, 10

    A, B, C = _generate_coefficients()
    ops = ['>', '>=', '<', '<=']
    op = random.choice(ops)
    
    ineq_str = _get_inequality_string(A, B, C, op)

    # Create a grid for evaluating the inequality
    x_grid = np.linspace(x_min, x_max, 400)
    y_grid = np.linspace(y_min, y_max, 400)
    X, Y = np.meshgrid(x_grid, y_grid)
    Z = A*X + B*Y + C

    # Plot the shaded region using contourf
    condition = _get_condition(Z, op)
    ax.contourf(X, Y, condition.astype(int), levels=[-0.5, 0.5, 1.5], colors=['none', 'skyblue'], alpha=0.3, extend='neither')

    # Plot the boundary line
    _plot_line_segment(ax, A, B, C, op, x_min, x_max, y_min, y_max)

    # Generate a test point (px, py)
    px = random.randint(x_min + 1, x_max - 1)
    py = random.randint(y_min + 1, y_max - 1)

    # Mark the test point on the graph
    ax.plot(px, py, 'o', color='red', markersize=6)
    ax.text(px + 0.5, py + 0.5, r'$P$', color='red', fontsize=12)

    # Set plot limits and aspect ratio
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_aspect('equal', adjustable='box')
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.set_xlabel('$x$')
    ax.set_ylabel('$y$')
    ax.axhline(0, color='gray', lw=0.5)
    ax.axvline(0, color='gray', lw=0.5)
    ax.set_title(f"圖示 ${{ineq_str}}$ 的解區域")

    # Calculate if the test point satisfies the inequality
    is_correct = _check_point_in_region(A, B, C, op, px, py)
    
    # Save plot
    plot_filename = f"gh_LinearInequalityInTwoVariables_{uuid.uuid4().hex}.png"
    plot_filepath = os.path.join(PLOT_DIR, plot_filename)
    plt.savefig(plot_filepath, bbox_inches='tight')
    plt.close(fig) # Close the figure to free up memory

    img_tag = f"<img src=\"/{PLOT_DIR}/{plot_filename}\" alt=\"Linear Inequality Graph\" style=\"max-width:400px; height:auto;\">"

    question_text = (
        f"請觀察下列圖形，圖中表示了二元一次不等式 ${{ineq_str}}$ 的解區域。"
        f"<br>圖中的點 $P({{{px}}},{{{py}}})$ 是否位於此不等式的解區域內？ (請回答 '是' 或 '否')"
        f"<br>{img_tag}"
    )
    
    correct_answer_str = '是' if is_correct else '否'
    
    return {
        "question_text": question_text,
        "answer": correct_answer_str,
        "correct_answer": correct_answer_str
    }

def generate_system_inequalities_problem(level):
    fig, ax = plt.subplots(figsize=(6, 6))
    x_min, x_max = -10, 10
    y_min, y_max = -10, 10

    # Inequality 1
    A1, B1, C1 = _generate_coefficients()
    op1 = random.choice(['>', '>=', '<', '<='])
    ineq1_str = _get_inequality_string(A1, B1, C1, op1)

    # Inequality 2
    A2, B2, C2 = _generate_coefficients()
    op2 = random.choice(['>', '>=', '<', '<='])
    ineq2_str = _get_inequality_string(A2, B2, C2, op2)

    # Create a grid for evaluating both inequalities
    x_grid = np.linspace(x_min, x_max, 400)
    y_grid = np.linspace(y_min, y_max, 400)
    X, Y = np.meshgrid(x_grid, y_grid)
    
    Z1 = A1*X + B1*Y + C1
    Z2 = A2*X + B2*Y + C2

    # Conditions for each inequality
    cond1 = _get_condition(Z1, op1)
    cond2 = _get_condition(Z2, op2)
    
    # Combined condition for the system (intersection)
    combined_condition = cond1 & cond2
    
    # Plot the shaded region for the intersection
    ax.contourf(X, Y, combined_condition.astype(int), levels=[-0.5, 0.5, 1.5], colors=['none', 'lightgreen'], alpha=0.4, extend='neither')

    # Plot boundary lines
    _plot_line_segment(ax, A1, B1, C1, op1, x_min, x_max, y_min, y_max, label=f'$L_1: {{{ineq1_str.replace(op1, "=")}}}$')
    _plot_line_segment(ax, A2, B2, C2, op2, x_min, x_max, y_min, y_max, label=f'$L_2: {{{ineq2_str.replace(op2, "=")}}}$')

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_aspect('equal', adjustable='box')
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.set_xlabel('$x$')
    ax.set_ylabel('$y$')
    ax.axhline(0, color='gray', lw=0.5)
    ax.axvline(0, color='gray', lw=0.5)
    ax.set_title(f"圖示聯立不等式解區域")

    # Generate a test point (px, py)
    px = random.randint(x_min + 1, x_max - 1)
    py = random.randint(y_min + 1, y_max - 1)

    # Mark the test point on the graph
    ax.plot(px, py, 'o', color='red', markersize=6)
    ax.text(px + 0.5, py + 0.5, r'$P$', color='red', fontsize=12)
    ax.legend(loc='upper right') # Display legend including line labels

    # Calculate if the test point satisfies both inequalities
    is_correct1 = _check_point_in_region(A1, B1, C1, op1, px, py)
    is_correct2 = _check_point_in_region(A2, B2, C2, op2, px, py)
    is_correct = is_correct1 and is_correct2
    
    # Save plot
    plot_filename = f"gh_LinearInequalityInTwoVariables_{uuid.uuid4().hex}.png"
    plot_filepath = os.path.join(PLOT_DIR, plot_filename)
    plt.savefig(plot_filepath, bbox_inches='tight')
    plt.close(fig) # Close the figure to free up memory

    img_tag = f"<img src=\"/{PLOT_DIR}/{plot_filename}\" alt=\"System of Linear Inequalities Graph\" style=\"max-width:400px; height:auto;\">"

    question_text = (
        f"請觀察下列圖形，圖中表示了二元一次聯立不等式 "
        f"$\\begin{{cases}} {{{ineq1_str}}} \\\\ {{{ineq2_str}}} \\end{{cases}}$ 的解區域。"
        f"<br>圖中的點 $P({{{px}}},{{{py}}})$ 是否位於此聯立不等式的解區域內？ (請回答 '是' 或 '否')"
        f"<br>{img_tag}"
    )
    
    correct_answer_str = '是' if is_correct else '否'
    
    return {
        "question_text": question_text,
        "answer": correct_answer_str,
        "correct_answer": correct_answer_str
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip().lower()
    correct_answer = correct_answer.strip().lower()
    
    # Handle synonyms for '是' and '否'
    yes_answers = ['是', 'yes', 'true', '對', 'o', '〇']
    no_answers = ['否', 'no', 'false', '錯', 'x', '╳']

    is_correct = False
    if (user_answer in yes_answers and correct_answer in yes_answers):
        is_correct = True
    elif (user_answer in no_answers and correct_answer in no_answers):
        is_correct = True

    result_text = f"完全正確！答案是 '{correct_answer}'。" if is_correct else f"答案不正確。正確答案應為 '{correct_answer}'。"
    return {"correct": is_correct, "result": result_text, "next_question": True}