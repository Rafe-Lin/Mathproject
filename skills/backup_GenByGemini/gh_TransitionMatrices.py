import random
from fractions import Fraction

# Define state labels for different scenarios
STATE_LABELS = {
    "city_suburb": ("市區", "郊區"),
    "on_time_late": ("準時還款", "延遲還款"),
    "hq_branch": ("總公司", "分公司"),
    "hole_ab": ("甲洞", "乙洞"),
}

def matrix_vector_multiply(matrix, vector):
    """
    Performs matrix-vector multiplication for a 2x2 matrix and a 2x1 vector.
    matrix = [[a, b], [c, d]]
    vector = [x, y]
    result = [a*x + b*y, c*x + d*y]
    """
    res_x = matrix[0][0] * vector[0] + matrix[0][1] * vector[1]
    res_y = matrix[1][0] * vector[0] + matrix[1][1] * vector[1]
    return [res_x, res_y]

def _format_fraction_as_decimal_or_fraction(val):
    """
    Helper to format Fraction values: as decimal if terminating nicely, else as fraction.
    """
    if isinstance(val, Fraction):
        # Check if denominator allows for a short terminating decimal (e.g., 2, 4, 5, 8, 10, 20, 25, 50, 100)
        # Or if it's a whole number (denominator is 1)
        temp_val = float(val)
        if val.denominator in [1, 2, 4, 5, 8, 10, 20, 25, 50, 100] or val.denominator == 1:
            return f"{temp_val:.2f}".rstrip('0').rstrip('.') or "0"
        return f"{val.numerator}/{val.denominator}"
    return str(val)

def format_matrix_latex(matrix):
    """
    Formats a 2x2 matrix into a LaTeX pmatrix string.
    Example: [[a, b], [c, d]] -> \begin{pmatrix} a & b \\ c & d \end{pmatrix}
    """
    return (
        r"\begin{{pmatrix}}"
        f"{_format_fraction_as_decimal_or_fraction(matrix[0][0])} & {_format_fraction_as_decimal_or_fraction(matrix[0][1])} \\\\"
        f"{_format_fraction_as_decimal_or_fraction(matrix[1][0])} & {_format_fraction_as_decimal_or_fraction(matrix[1][1])}"
        r"\end{{pmatrix}}"
    )

def format_vector_latex(vector):
    """
    Formats a 2x1 vector into a LaTeX pmatrix string.
    Example: [x, y] -> \begin{pmatrix} x \\ y \end{pmatrix}
    """
    return (
        r"\begin{{pmatrix}}"
        f"{_format_fraction_as_decimal_or_fraction(vector[0])} \\\\"
        f"{_format_fraction_as_decimal_or_fraction(vector[1])}"
        r"\end{{pmatrix}}"
    )

def generate(level=1):
    """
    生成「轉移矩陣」相關題目。
    包含：
    1. 根據文字描述建立轉移矩陣。
    2. 計算 N 步後的狀態向量。
    """
    scenario = random.choice(list(STATE_LABELS.keys()))
    state1_label, state2_label = STATE_LABELS[scenario]

    question_parts = []
    solution_parts = []
    
    # Generate probabilities for transitions, ensuring simple fractions
    denom = random.choice([10, 20, 25, 4, 5])
    
    # Probabilities from State 1 (first column of A)
    p_s1_s1_num = random.randint(1, denom - 1) # Ensure P(S1->S1) is not 0 or 1
    p_s1_s1 = Fraction(p_s1_s1_num, denom)
    p_s1_s2 = 1 - p_s1_s1

    # Probabilities from State 2 (second column of A)
    p_s2_s1_num = random.randint(1, denom - 1) # Ensure P(S2->S1) is not 0 or 1
    p_s2_s1 = Fraction(p_s2_s1_num, denom)
    p_s2_s2 = 1 - p_s2_s1
    
    # Transition matrix A: [[P(S1->S1), P(S2->S1)], [P(S1->S2), P(S2->S2)]]
    A = [[p_s1_s1, p_s2_s1], [p_s1_s2, p_s2_s2]]
    A_latex_str = format_matrix_latex(A)

    # Initial state proportions
    x0_denom = random.choice([4, 5, 10, 20])
    x0_s1_num = random.randint(1, x0_denom - 1) # Ensure initial state is not 0 or 1
    x0_s1 = Fraction(x0_s1_num, x0_denom)
    x0_s2 = 1 - x0_s1
    X0 = [x0_s1, x0_s2]
    X0_latex_str = format_vector_latex(X0)

    # Generate problem description based on scenario
    if scenario == "city_suburb":
        question_parts.append(f"某城市統計人口遷移狀況如下：")
        question_parts.append(f"{state1_label}的居民隔年有 ${_format_fraction_as_decimal_or_fraction(p_s1_s1)}$ 比例仍留在{state1_label}，另有 ${_format_fraction_as_decimal_or_fraction(p_s1_s2)}$ 比例遷往{state2_label}。")
        question_parts.append(f"{state2_label}的居民隔年有 ${_format_fraction_as_decimal_or_fraction(p_s2_s1)}$ 比例遷往{state1_label}，另有 ${_format_fraction_as_decimal_or_fraction(p_s2_s2)}$ 比例仍留在{state2_label}。")
        initial_desc = f"已知目前{state1_label}與{state2_label}人口的比例分別為 ${float(x0_s1)*100:.1f}\\%$ 與 ${float(x0_s2)*100:.1f}\\%$。"
        answer_unit = "比例"
        time_unit = "年"
    elif scenario == "on_time_late":
        question_parts.append(f"某銀行統計其信用卡客戶每月的還款情形發現：")
        question_parts.append(f"{state1_label}的人隔月有 ${_format_fraction_as_decimal_or_fraction(p_s1_s1)}$ 仍{state1_label}，另 ${_format_fraction_as_decimal_or_fraction(p_s1_s2)}$ 會{state2_label}。")
        question_parts.append(f"{state2_label}的人隔月有 ${_format_fraction_as_decimal_or_fraction(p_s2_s1)}$ 會{state1_label}，另 ${_format_fraction_as_decimal_or_fraction(p_s2_s2)}$ 仍{state2_label}。")
        initial_desc = f"已知本月的客戶中有 ${float(x0_s1)*100:.1f}\\%$ {state1_label}，其餘{state2_label}。"
        answer_unit = "比例"
        time_unit = "月"
    elif scenario == "hq_branch":
        question_parts.append(f"某公司針對新進員工的輪調規則如下：")
        question_parts.append(f"{state1_label}的員工隔年有 ${_format_fraction_as_decimal_or_fraction(p_s1_s1)}$ 仍留在{state1_label}，另有 ${_format_fraction_as_decimal_or_fraction(p_s1_s2)}$ 調到{state2_label}。")
        question_parts.append(f"{state2_label}的員工隔年有 ${_format_fraction_as_decimal_or_fraction(p_s2_s1)}$ 調到{state1_label}，另有 ${_format_fraction_as_decimal_or_fraction(p_s2_s2)}$ 仍留在{state2_label}。")
        initial_desc = f"已知今年新進員工中有 ${float(x0_s1)*100:.1f}\\%$ 在{state1_label}，其餘在{state2_label}。"
        answer_unit = "比例"
        time_unit = "年"
    elif scenario == "hole_ab":
        question_parts.append(f"一款打地鼠手機遊戲，初始關卡只有{state1_label}、{state2_label}兩個洞，地鼠每次只從一個洞冒出。")
        question_parts.append(f"從{state1_label}冒出後，下次仍從{state1_label}冒出的機率為 ${_format_fraction_as_decimal_or_fraction(p_s1_s1)}$，從{state2_label}冒出的機率為 ${_format_fraction_as_decimal_or_fraction(p_s1_s2)}$。")
        question_parts.append(f"從{state2_label}冒出後，下次從{state1_label}冒出的機率為 ${_format_fraction_as_decimal_or_fraction(p_s2_s1)}$，仍從{state2_label}冒出的機率為 ${_format_fraction_as_decimal_or_fraction(p_s2_s2)}$。")
        initial_desc = f"已知地鼠第一次從{state1_label}冒出的機率為 ${float(x0_s1)*100:.1f}\\%$，從{state2_label}冒出的機率為 ${float(x0_s2)*100:.1f}\\%$。"
        answer_unit = "機率"
        time_unit = "次"

    # Choose number of steps
    num_steps = random.choice([1, 2])
    
    question_text = "\n".join(question_parts)
    question_text += f"\n(1) 寫出描述上述現象的轉移矩陣 $A$。"
    question_text += f"\n(2) {initial_desc} 求 {num_steps} {time_unit}後 {state1_label} 的{answer_unit}。 (答案請四捨五入到小數點後三位)"

    # Calculate X1, X2
    X1 = matrix_vector_multiply(A, X0)
    X_final = X1
    if num_steps == 2:
        X2 = matrix_vector_multiply(A, X1)
        X_final = X2
    
    # Format answers
    correct_X_final_s1_float = float(X_final[0])
    correct_X_final_s1_str = f"{correct_X_final_s1_float:.3f}" # Rounded to 3 decimal places
    
    # Store solutions for reference/feedback
    solution_parts.append(f"(1) 轉移矩陣 $A = {A_latex_str}$。")
    solution_parts.append(f"初始狀態 $X_0 = {X0_latex_str}$。")
    
    solution_parts.append(f"(2) {1} {time_unit}後： $X_1 = AX_0 = {A_latex_str} {X0_latex_str} = {format_vector_latex(X1)}$。")
    if num_steps == 2:
        solution_parts.append(f"再經過 {1} {time_unit}後： $X_2 = AX_1 = {A_latex_str} {format_vector_latex(X1)} = {format_vector_latex(X2)}$。")
    
    final_state_percentage_str = f"{correct_X_final_s1_float*100:.1f}\\%" # Display as percentage in solution
    solution_parts.append(f"所以 {num_steps} {time_unit}後 {state1_label} 的{answer_unit}約為 ${correct_X_final_s1_str}$ (即 ${final_state_percentage_str}$)。")

    # The user only needs to input the final probability for question (2)
    question_text = f"{question_text}\n請填寫問題 (2) 的答案。"
    correct_answer = correct_X_final_s1_str
    
    full_solution = "\n".join(solution_parts)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "solution": full_solution
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    
    is_correct = False
    feedback = ""

    try:
        user_val = float(user_answer)
        correct_val = float(correct_answer)
        
        # Allow a small tolerance for floating point comparisons due to rounding
        tolerance = 1e-4 # For rounding to 3 decimal places, 1e-4 should be sufficient
        if abs(user_val - correct_val) < tolerance:
            is_correct = True
            feedback = f"完全正確！答案是 ${correct_answer}$。"
        else:
            feedback = f"答案不正確。你的答案是 ${user_answer}$，但正確答案應為：${correct_answer}$。"
            
    except ValueError:
        feedback = f"輸入格式錯誤。請確保輸入的是一個數字 (小數點後三位)。"

    return {"correct": is_correct, "result": feedback, "next_question": True}