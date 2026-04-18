import random
import math
import cmath # Used for complex number arithmetic
import matplotlib.pyplot as plt
import uuid
import os
import re # Used for regular expressions in parsing answers

# --- Helper Functions for Formatting and Generation ---

def format_complex(z):
    """
    Formats a complex number into a standard string representation (e.g., "3+2i", "-3i", "4").
    """
    real = z.real
    imag = z.imag

    if imag == 0:
        # If imaginary part is zero, return as an integer or float string
        return f"{int(real)}" if real == int(real) else f"{real}"
    elif real == 0:
        # If real part is zero, return as "bi" or "i"
        if imag == 1:
            return "i"
        elif imag == -1:
            return "-i"
        else:
            return f"{int(imag)}i" if imag == int(imag) else f"{imag}i"
    else:
        # Both real and imaginary parts are non-zero
        real_str = f"{int(real)}" if real == int(real) else f"{real}"
        if imag == 1:
            return f"{real_str}+i"
        elif imag == -1:
            return f"{real_str}-i"
        else:
            imag_val = abs(imag)
            imag_str = f"{int(imag_val)}" if imag_val == int(imag_val) else f"{imag_val}"
            return f"{real_str}{'+' if imag > 0 else '-'}{imag_str}i"

def format_sqrt_latex(n):
    """
    Formats a number into a simplified square root string for LaTeX output (e.g., r"\\sqrt{13}", "3", r"2\\sqrt{3}").
    """
    if n < 0:
        return str(n) # Should not happen for absolute values/distances
    if n == 0:
        return "0"
    
    int_n = int(n)
    if int_n != n: # If n is not an integer, return its float string representation
        return str(n)
    
    # Try to simplify sqrt(n) = a*sqrt(b)
    for i in range(math.isqrt(int_n), 1, -1): # Iterate from largest possible integer factor downwards
        if int_n % (i*i) == 0: # If i*i is a factor of int_n
            if i*i == int_n: # Perfect square
                return str(i)
            else:
                return r"{}\\sqrt{{{}}}".format(i, int_n // (i*i))
    return r"\\sqrt{{{}}}".format(int_n) # Cannot simplify further

def generate_complex_number(min_val=-5, max_val=5, allow_zero_real=True, allow_zero_imag=True, ensure_nonzero=True):
    """
    Generates a random complex number with integer real and imaginary parts within a specified range.
    Options to control zero components and overall non-zero value.
    """
    real = random.randint(min_val, max_val)
    imag = random.randint(min_val, max_val)
    
    if not allow_zero_real:
        while real == 0:
            real = random.randint(min_val, max_val)
    if not allow_zero_imag:
        while imag == 0:
            imag = random.randint(min_val, max_val)

    # Ensure the complex number itself is not zero if specified
    if ensure_nonzero:
        while real == 0 and imag == 0:
            real = random.randint(min_val, max_val)
            imag = random.randint(min_val, max_val)
    
    return complex(real, imag)

# Directory for storing generated plots
PLOT_DIR = "static/generated_plots"
os.makedirs(PLOT_DIR, exist_ok=True) # Ensure the directory exists

# --- Problem Generation Functions ---

def generate_read_complex_from_graph_problem():
    """
    Generates a problem where the user identifies a complex number from a plot.
    """
    num_points = random.randint(3, 5) # Number of points to plot
    points_data = []
    labels = ['A', 'B', 'C', 'D', 'E'] # Labels for points
    
    min_coord_range = -7 # Min bound for plot axes
    max_coord_range = 7 # Max bound for plot axes

    x_coords = []
    y_coords = []

    generated_zs = set() # To ensure unique complex numbers are plotted
    for i in range(num_points):
        z = generate_complex_number(min_val=-6, max_val=6, ensure_nonzero=True)
        while z in generated_zs: # Regenerate if duplicate complex number
            z = generate_complex_number(min_val=-6, max_val=6, ensure_nonzero=True)
        generated_zs.add(z)
        
        points_data.append({'label': labels[i], 'complex': z})
        x_coords.append(z.real)
        y_coords.append(z.imag)
    
    target_point = random.choice(points_data) # Select one point for the question
    correct_complex_str = format_complex(target_point['complex'])

    # --- Matplotlib Plotting ---
    fig, ax = plt.subplots(figsize=(6, 6))

    ax.plot(x_coords, y_coords, 'o', color='blue', markersize=6) # Plot the points

    # Add labels to points with slight offset
    for p_data in points_data:
        x, y = p_data['complex'].real, p_data['complex'].imag
        ax.text(x + 0.3 * (1 if x >= 0 else -1), y + 0.3 * (1 if y >= 0 else -1), 
                p_data['label'], fontsize=12, ha='center', va='center')

    # Draw coordinate axes
    ax.axhline(0, color='black', linewidth=0.8)
    ax.axvline(0, color='black', linewidth=0.8)

    # Determine plot limits with padding
    x_min_data, x_max_data = min(x_coords), max(x_coords)
    y_min_data, y_max_data = min(y_coords), max(y_coords)
    
    x_min_lim = min(min_coord_range, x_min_data - 1)
    x_max_lim = max(max_coord_range, x_max_data + 1)
    y_min_lim = min(min_coord_range, y_min_data - 1)
    y_max_lim = max(max_coord_range, y_max_data + 1)

    ax.set_xlim(x_min_lim, x_max_lim)
    ax.set_ylim(y_min_lim, y_max_lim)

    # Set integer ticks and grid
    ax.set_xticks(range(int(x_min_lim), int(x_max_lim) + 1))
    ax.set_yticks(range(int(y_min_lim), int(y_max_lim) + 1))
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.set_aspect('equal', adjustable='box') # Ensure proper aspect ratio

    # Add axis labels
    ax.text(ax.get_xlim()[1] + 0.5, 0, r'實軸', ha='left', va='center', fontsize=12)
    ax.text(0, ax.get_ylim()[1] + 0.5, r'虛軸', ha='center', va='bottom', fontsize=12)

    # Remove ticks at origin to avoid overlap with axis labels and plot origin point
    new_xticks = [t for t in ax.get_xticks() if t != 0]
    new_yticks = [t for t in ax.get_yticks() if t != 0]
    ax.set_xticks(new_xticks)
    ax.set_yticks(new_yticks)
    ax.plot(0, 0, 'o', color='black', markersize=3) # Origin point

    # Save plot to a unique filename
    plot_uuid = uuid.uuid4()
    plot_filename = f"gh_ComplexPlane_{plot_uuid}.png"
    filepath = os.path.join(PLOT_DIR, plot_filename)
    plt.savefig(filepath, bbox_inches='tight', dpi=150)
    plt.close(fig) # Close the figure to free memory

    # Construct question text with image tag
    image_tag = f"<img src='/{filepath}' alt='Complex Plane Plot'>"
    question_text = f"如右圖，請寫出複數平面上 ${target_point['label']}$ 所代表的複數。<br>{image_tag}"
    
    return {
        "question_text": question_text,
        "answer": correct_complex_str,
        "correct_answer": correct_complex_str
    }

def generate_absolute_value_distance_problem():
    """
    Generates a problem asking for the absolute value of a complex number or the distance between two complex numbers.
    """
    z1 = generate_complex_number(min_val=-5, max_val=5, ensure_nonzero=True)
    
    problem_subtype = random.choice(['abs_z1', 'abs_z2', 'abs_diff', 'distance'])
    
    if problem_subtype == 'abs_z1':
        question_text = f"求複數 ${format_complex(z1)}$ 的絕對值。"
        result = abs(z1)
        correct_answer_str = format_sqrt_latex(result**2)
    
    elif problem_subtype == 'abs_z2':
        z2 = generate_complex_number(min_val=-5, max_val=5, ensure_nonzero=True)
        question_text = f"求複數 ${format_complex(z2)}$ 的絕對值。"
        result = abs(z2)
        correct_answer_str = format_sqrt_latex(result**2)
    
    else: # abs_diff or distance
        z2 = generate_complex_number(min_val=-5, max_val=5, ensure_nonzero=True)
        
        while z1 == z2: # Ensure z1 and z2 are distinct
            z2 = generate_complex_number(min_val=-5, max_val=5, ensure_nonzero=True)

        diff = z1 - z2
        result = abs(diff)
        correct_answer_str = format_sqrt_latex(result**2)
        
        if problem_subtype == 'abs_diff':
            question_text = f"設 $z_1 = {format_complex(z1)}$，$z_2 = {format_complex(z2)}$。求 $|z_1 - z_2|$ 的值。"
        else: # distance
            question_text = f"在複數平面上，設 $z_1 = {format_complex(z1)}$，$z_2 = {format_complex(z2)}$。求 $z_1$ 與 $z_2$ 兩點的距離。"
            
    return {
        "question_text": question_text,
        "answer": correct_answer_str,
        "correct_answer": correct_answer_str
    }

def generate_geometric_locus_problem():
    """
    Generates a problem asking for the geometric locus represented by a complex equation.
    """
    locus_type = random.choice(['perpendicular_bisector', 'circle'])

    if locus_type == 'perpendicular_bisector':
        z1 = generate_complex_number(min_val=-4, max_val=4, ensure_nonzero=True)
        z2 = generate_complex_number(min_val=-4, max_val=4, ensure_nonzero=True)
        while z1 == z2: # Ensure z1 and z2 are distinct
            z2 = generate_complex_number(min_val=-4, max_val=4, ensure_nonzero=True)

        question_text = (
            f"在複數平面上，所有滿足方程式 $|z - ({format_complex(z1)})| = |z - ({format_complex(z2)})|$ "
            f"的複數 $z$ 形成什麼圖形？"
        )
        correct_answer = "直線" # A line (perpendicular bisector)
    
    elif locus_type == 'circle':
        z0 = generate_complex_number(min_val=-4, max_val=4, allow_zero_real=True, allow_zero_imag=True, ensure_nonzero=True)
        radius = random.randint(1, 5)

        question_text = (
            f"在複數平面上，所有滿足方程式 $|z - ({format_complex(z0)})| = {radius}$ 的複數 $z$ 形成什麼圖形？"
        )
        correct_answer = "圓" # A circle

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

# --- Main Generator Function ---

def generate(level=1):
    """
    Generates a complex plane problem based on the specified level.
    """
    problem_type_choices = ['read_complex_from_graph', 'absolute_value_distance']
    if level >= 2:
        problem_type_choices.append('geometric_locus')
    
    problem_type = random.choice(problem_type_choices)

    if problem_type == 'read_complex_from_graph':
        return generate_read_complex_from_graph_problem()
    elif problem_type == 'absolute_value_distance':
        return generate_absolute_value_distance_problem()
    elif problem_type == 'geometric_locus':
        return generate_geometric_locus_problem()
    
    # Fallback, though ideally one of the above will always be chosen
    return generate_absolute_value_distance_problem()

# --- Answer Checking Functions ---

def parse_math_expression(s):
    """
    Parses a string into its canonical form (geometric type, float, or complex number)
    for robust comparison.
    """
    s = s.strip().lower().replace(' ', '')

    # 1. Geometric locus keywords
    if s == "直線": return "直線"
    if s == "圓": return "圓"

    # 2. Square root expressions (e.g., 'sqrt(13)', '2sqrt(3)', '3')
    sqrt_match = re.match(r"(\d*)sqrt\((\d+)\)", s)
    if sqrt_match:
        coeff_str = sqrt_match.group(1)
        coeff = float(coeff_str) if coeff_str else 1.0
        val = float(sqrt_match.group(2))
        return coeff * math.sqrt(val)
    
    # 3. Complex numbers and pure real numbers
    try:
        # Handle 'i' and '-i' explicitly as cmath.complex might not parse them directly
        if s == 'i': return complex(0, 1)
        if s == '-i': return complex(0, -1)
        
        # Replace 'i' with 'j' for cmath.complex parsing
        if 'i' in s:
            s_for_cmath = s.replace('i', 'j')
            # Handle pure imaginary like '3j' that cmath.complex might struggle with without explicit '0+'
            pure_imag_match = re.match(r"^([-+]?\d*\.?\d*)j$", s_for_cmath)
            if pure_imag_match:
                coeff_str = pure_imag_match.group(1)
                coeff = float(coeff_str) if coeff_str not in ('', '+', '-') else (1.0 if coeff_str == '+' or coeff_str == '' else -1.0)
                return complex(0, coeff)
            
            # For general complex numbers (e.g., "3+2j", "-1-j")
            return cmath.complex(s_for_cmath)
        
        # If no 'i' (or 'j'), try parsing as a float
        return float(s)

    except ValueError:
        pass # Not a valid complex or float format
    
    return None # Parsing failed

def check(user_answer, correct_answer):
    """
    Checks if the user's answer is correct against the generated correct answer.
    Handles different numerical and string formats using a robust parsing helper.
    """
    user_parsed = parse_math_expression(user_answer)
    correct_parsed = parse_math_expression(correct_answer)

    is_correct = False
    
    if user_parsed is None or correct_parsed is None:
        # If parsing failed for either, perform a direct string comparison as a fallback.
        # This catches cases where specific formatting might matter or parsing is too strict.
        is_correct = (user_answer.strip().lower().replace(' ', '') == correct_answer.strip().lower().replace(' ', ''))
    elif isinstance(user_parsed, str) and isinstance(correct_parsed, str): # Geometric locus (e.g., "直線", "圓")
        is_correct = (user_parsed == correct_parsed)
    elif isinstance(user_parsed, (float, int)) and isinstance(correct_parsed, (float, int)): # Real numbers (e.g., absolute values)
        # Use math.isclose for float comparison to account for precision issues
        is_correct = math.isclose(float(user_parsed), float(correct_parsed), rel_tol=1e-6, abs_tol=1e-9)
    elif isinstance(user_parsed, complex) and isinstance(correct_parsed, complex): # Complex numbers
        # Compare real and imaginary parts separately with tolerance
        is_correct = (math.isclose(user_parsed.real, correct_parsed.real, rel_tol=1e-6, abs_tol=1e-9) and
                      math.isclose(user_parsed.imag, correct_parsed.imag, rel_tol=1e-6, abs_tol=1e-9))
    else:
        # If types don't match after parsing (e.g., user entered a float for a complex answer)
        is_correct = False

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}