import random
from fractions import Fraction
import math

def generate(level=1):
    problem_type = random.choice([
        'params_from_features',         # Example 1
        'find_symmetry_center',         # Example 7
        'properties_standard_form'      # Example 2, 9
    ])
    
    if problem_type == 'params_from_features':
        return generate_params_from_features_problem()
    elif problem_type == 'find_symmetry_center':
        return generate_find_symmetry_center_problem()
    else: # 'properties_standard_form'
        return generate_properties_standard_form_problem()

def format_polynomial(coeffs, x_var='x', h_val=None, use_shifted_form=False):
    """
    Formats polynomial coefficients into a LaTeX-ready string.
    
    Args:
        coeffs (list): Coefficients.
                       If use_shifted_form=False: [a, b, c, d] for ax^3+bx^2+cx+d
                       If use_shifted_form=True: [A, P, K] for A(x-h)^3 + P(x-h) + K (B term is zero)
        x_var (str): The variable name (e.g., 'x').
        h_val (int): The shift value 'h' for shifted form (x-h).
        use_shifted_form (bool): True if using A(x-h)^3 + P(x-h) + K form.
    """
    terms = []
    
    if use_shifted_form:
        A, P, K = coeffs
        if A != 0:
            if h_val == 0:
                terms.append(f"{A}{x_var}^3")
            else:
                terms.append(f"{A}({x_var}-{{h_val}})^3")
        if P != 0:
            if h_val == 0:
                terms.append(f"{'+' if P > 0 and terms else ''}{P}{x_var}")
            else:
                terms.append(f"{'+' if P > 0 and terms else ''}{P}({x_var}-{{h_val}})")
        if K != 0:
            terms.append(f"{'+' if K > 0 and terms else ''}{K}")
    else: # ax^3 + bx^2 + cx + d form
        a, b, c, d = coeffs
        if a != 0:
            terms.append(f"{a}{x_var}^3")
        if b != 0:
            terms.append(f"{'+' if b > 0 and terms else ''}{b}{x_var}^2")
        if c != 0:
            terms.append(f"{'+' if c > 0 and terms else ''}{c}{x_var}")
        if d != 0:
            terms.append(f"{'+' if d > 0 and terms else ''}{d}")
            
    if not terms:
        return "0"
    
    # Remove leading '+' if any, and clean up double signs
    formatted_str = "".join(terms)
    if formatted_str.startswith("+"):
        formatted_str = formatted_str[1:]
    
    return formatted_str.replace("+-", "-")


def generate_params_from_features_problem():
    # Similar to Example 1: f(x) = a(x+1)^3+b(x+1)^2+c(x+1)+d
    # Given global y=Mx^3, local at x=h0 is y=Px+Q. Find a, c, d.
    
    h0 = random.randint(-2, 2) 
    if h0 == 0: h0 = random.choice([-1, 1]) # Avoid x-0 which is just x
    
    a_ans = random.randint(-3, 3)
    while a_ans == 0:
        a_ans = random.randint(-3, 3)
    
    c_ans = random.randint(-5, 5)
    d_ans = random.randint(-5, 5)

    # Convert y = c_ans(x-h0) + d_ans into y = Px + Q form for the question
    P_val = c_ans
    Q_val = d_ans - c_ans * h0

    question_text = (
        f"設三次函數 $f(x) = a(x-{{h0}})^3+b(x-{{h0}})^2+c(x-{{h0}})+d$。"
        f"已知廣域看 $y=f(x)$ 的圖形會很接近 $y={a_ans}x^3$ 的圖形，"
        f"而局部看 $y=f(x)$ 在 $x={{h0}}$ 附近的圖形卻近似於直線 $y={P_val}x+{Q_val}$，"
        f"求實數 $a, c, d$ 的值。(請依序填寫，以逗號分隔)"
    )
    correct_answer = f"{a_ans},{c_ans},{d_ans}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_find_symmetry_center_problem():
    # Similar to Example 7: Find symmetry center for ax^3+bx^2+cx+d
    
    a_coeff = random.randint(-3, 3)
    while a_coeff == 0:
        a_coeff = random.randint(-3, 3)
        
    h_ans = random.randint(-3, 3)
    
    # Ensure b_coeff makes h_ans an integer (or a simple fraction for more advanced levels)
    # h = -b / (3a) => b = -3 * a * h
    b_coeff = -3 * a_coeff * h_ans
    
    c_coeff = random.randint(-5, 5)
    d_coeff = random.randint(-5, 5)
    
    # Construct the polynomial string
    coeffs = [a_coeff, b_coeff, c_coeff, d_coeff]
    f_str = format_polynomial(coeffs, use_shifted_form=False)

    # Calculate k_ans = f(h_ans)
    k_ans = a_coeff * (h_ans**3) + b_coeff * (h_ans**2) + c_coeff * h_ans + d_coeff

    question_text = (
        f"求三次函數 $y={f_str}$ 圖形的對稱中心。 "
        f"(請以 $(h,k)$ 的形式填寫，例如 $(1,2)$)"
    )
    correct_answer = f"({h_ans},{k_ans})"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_properties_standard_form_problem():
    # Similar to Example 2: True/False questions about properties of A(x-h)^3 + P(x-h) + K
    
    A_val = random.randint(-3, 3)
    while A_val == 0:
        A_val = random.randint(-3, 3)
        
    h_val = random.randint(-3, 3)
    P_val = random.randint(-5, 5)
    K_val = random.randint(-5, 5)
    
    # Construct f(x) string in standard form: A(x-h)^3 + P(x-h) + K
    f_str = format_polynomial([A_val, P_val, K_val], h_val=h_val, use_shifted_form=True)

    stmt_type = random.choice(['symmetry_center', 'local_approx', 'global_approx'])
    is_true_statement = random.choice([True, False])

    statement = ""
    if stmt_type == 'symmetry_center':
        h_display = h_val
        K_display = K_val
        if not is_true_statement:
            if random.random() < 0.5: 
                h_display_temp = h_val + random.choice([-1, 1])
                if h_display_temp == h_val: h_display_temp = h_val + 2 # ensure change
                h_display = h_display_temp
            else: 
                K_display_temp = K_val + random.choice([-1, 1])
                if K_display_temp == K_val: K_display_temp = K_val + 2 # ensure change
                K_display = K_display_temp
        statement = f"點 $({{h_display}},{{K_display}})$ 是圖形的對稱中心。"
        
    elif stmt_type == 'local_approx':
        P_display = P_val
        K_display = K_val
        if not is_true_statement:
            if random.random() < 0.5: 
                P_display_temp = P_val + random.choice([-1, 1])
                if P_display_temp == P_val: P_display_temp = P_val + 2 # ensure change
                P_display = P_display_temp
            else: 
                K_display_temp = K_val + random.choice([-1, 1])
                if K_display_temp == K_val: K_display_temp = K_val + 2 # ensure change
                K_display = K_display_temp
        statement = f"局部看 $y=f(x)$ 在 $x={{h_val}}$ 附近的圖形會近似於直線 $y={P_display}(x-{{h_val}})+{{K_display}}$。"
        
    else: # 'global_approx'
        A_display = A_val
        if not is_true_statement:
            A_display_temp = A_val + random.choice([-1, 1])
            if A_display_temp == 0: A_display_temp = A_val + 2 # Avoid A=0 for cubic global approx
            if A_display_temp == A_val: A_display_temp = A_val + 2 # ensure change
            A_display = A_display_temp
        statement = f"廣域看 $y=f(x)$ 的圖形會很接近 $y={A_display}x^3$ 的圖形。"
        
    question_text = (
        f"關於三次函數 $f(x) = {f_str}$。以下敘述對的打「○」，錯的打「×」。<br>"
        f"{statement}"
    )
    correct_answer = "O" if is_true_statement else "X"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer_processed = user_answer.strip().upper().replace(" ", "").replace("\n", "")
    correct_answer_processed = correct_answer.strip().upper().replace(" ", "").replace("\n", "")
    
    is_correct = (user_answer_processed == correct_answer_processed)
    
    # For numeric answers that might have slight variations in formatting (e.g., "1.0" vs "1")
    if not is_correct:
        try:
            # Handle comma-separated lists like "1,2,3"
            user_parts = user_answer_processed.split(',')
            correct_parts = correct_answer_processed.split(',')
            
            if len(user_parts) == len(correct_parts):
                all_parts_match = True
                for u_part, c_part in zip(user_parts, correct_parts):
                    try:
                        # Compare floats with a tolerance
                        if abs(float(u_part) - float(c_part)) > 1e-9: 
                            all_parts_match = False
                            break
                    except ValueError: # Not a float, compare as strings
                        if u_part != c_part:
                            all_parts_match = False
                            break
                if all_parts_match:
                    is_correct = True
            
            # Handle single numeric answers (e.g., for "O" or "X", this block won't activate)
            elif len(user_parts) == 1 and len(correct_parts) == 1:
                try: # Attempt float comparison for single parts
                    if abs(float(user_parts[0]) - float(correct_parts[0])) < 1e-9:
                        is_correct = True
                except ValueError:
                    pass # Fallback to string comparison if not numeric
        except ValueError:
            pass # If initial split or conversion to float fails, stick to string comparison
    
    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}