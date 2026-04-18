import random
from fractions import Fraction
import numpy as np

# Helper function to convert polynomial coefficients to a string
def poly_to_str(coeffs):
    """
    Converts a list of coefficients into a LaTeX-style polynomial string.
    Example: [1, -2, -3] -> "x^{2} - 2x - 3"
    """
    terms = []
    degree = len(coeffs) - 1
    for i, c in enumerate(coeffs):
        if c == 0:
            continue

        # Sign part
        sign = ""
        is_first_term = not terms
        if not is_first_term:
            sign = " + " if c > 0 else " - "
        elif c < 0: # First term is negative
            sign = "-"
        
        c = abs(c)
        
        # Coefficient part
        power = degree - i
        if c == 1 and power != 0:
            coeff_str = ""
        else:
            coeff_str = str(c)
        
        # Variable part
        if power == 0:
            var_str = ""
        elif power == 1:
            var_str = "x"
        else:
            var_str = f"x^{{{power}}}"
            
        terms.append(f"{sign}{coeff_str}{var_str}")

    if not terms:
        return "0"
    
    return "".join(terms).strip()

def generate_division_check_problem():
    """
    Generates a problem asking if P1 is a factor/multiple of P2,
    which can be determined by polynomial division. This corresponds to the first reference example.
    """
    # Generate two linear factors (x+b) and (x+d)
    b = random.choice([i for i in range(-9, 10) if i != 0])
    d = random.choice([i for i in range(-9, 10) if i != 0 and i != b and i != -b])
    
    divisor_coeffs = [1, b]
    # P(x) = (x+b)(x+d) = x^2 + (b+d)x + bd
    dividend_base_coeffs = np.convolve([1, b], [1, d]).astype(int).tolist()
    
    is_zero_remainder = random.choice([True, False])
    
    if is_zero_remainder:
        dividend_coeffs = dividend_base_coeffs
        answer = "是"
    else:
        # Add a non-zero remainder by altering the constant term
        r = random.choice([i for i in range(-10, 11) if i != 0])
        dividend_coeffs = dividend_base_coeffs[:]
        dividend_coeffs[-1] += r
        answer = "不是"

    dividend_str = poly_to_str(dividend_coeffs)
    divisor_str = poly_to_str(divisor_coeffs)
    
    # Randomly choose the question format (factor or multiple)
    question_type = random.choice(['factor', 'multiple'])
    
    if question_type == 'factor':
        # Is divisor a factor of dividend?
        question_text = f"請問 $({divisor_str})$ 是 $({dividend_str})$ 的因式嗎？"
    else:
        # Is dividend a multiple of divisor?
        question_text = f"請問 $({dividend_str})$ 是 $({divisor_str})$ 的倍式嗎？"
        
    return {
        "question_text": question_text,
        "answer": answer,
        "correct_answer": answer
    }

def generate_definitional_check_problem():
    """
    Generates a problem based on the definition of factor/multiple given a
    factored polynomial A = F1 * F2. This corresponds to the second reference example.
    """
    # Generate two linear factors, F1 and F2
    a = random.randint(1, 2)
    b = random.choice([i for i in range(-9, 10) if i != 0])
    c = 1
    d = random.choice([i for i in range(-9, 10) if i != 0])
    
    # Ensure factors are not identical, e.g., (x+3) and (x+3)
    if a == c and b == d:
        d = random.choice([i for i in range(-9, 10) if i != 0 and i != b])

    F1_coeffs = [a, b]
    F2_coeffs = [c, d]
    
    # Calculate the product polynomial A
    A_coeffs = np.convolve(F1_coeffs, F2_coeffs).astype(int).tolist()
    
    A_str = poly_to_str(A_coeffs)
    F1_str = poly_to_str(F1_coeffs)
    F2_str = poly_to_str(F2_coeffs)
    
    # Create 4 statements to be judged
    statements_data = []
    
    # These represent the 4 core relationships to test (A vs F1, F1 vs A, etc.)
    concepts = [('A', 'F1'), ('F1', 'A'), ('A', 'F2'), ('F2', 'A')]
    random.shuffle(concepts)
    
    polys = {'A': A_str, 'F1': F1_str, 'F2': F2_str}
    
    for p1_key, p2_key in concepts:
        relation = random.choice(["因式", "倍式"])
        
        p1_str = polys[p1_key]
        p2_str = polys[p2_key]
        
        is_correct = False
        if relation == "倍式":
            if p1_key == 'A' and p2_key in ['F1', 'F2']:
                is_correct = True
        elif relation == "因式":
            if p1_key in ['F1', 'F2'] and p2_key == 'A':
                is_correct = True
        
        answer_symbol = "○" if is_correct else "×"
        
        statements_data.append({
            "text": f"({p1_str}) 是 ({p2_str}) 的{relation}",
            "answer": answer_symbol
        })

    # Build the final question and answer strings
    question_lines = [f"已知 ${A_str} = ({F1_str})({F2_str})$，判斷下列敘述正確的打「○」，錯誤的打「×」。"]
    correct_answer_list = []
    
    for i, data in enumerate(statements_data):
        question_lines.append(f"(  ) ({i+1}) ${data['text']}$。")
        correct_answer_list.append(data['answer'])
        
    question_text = "\n".join(question_lines)
    correct_answer = "".join(correct_answer_list)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    生成「多項式的因式與倍式」相關題目。
    包含：
    1. 透過除法判斷因倍式關係 (A / B 的餘式是否為 0)
    2. 透過已分解的式子判斷因倍式定義 (A = B * C)
    """
    problem_type = random.choice(['division_check', 'definitional_check'])
    
    if problem_type == 'division_check':
        return generate_division_check_problem()
    else:
        return generate_definitional_check_problem()

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip().replace(' ', '')
    correct_answer = correct_answer.strip()
    
    # Normalize full-width characters for ○ and ×
    user_answer = user_answer.replace('Ｏ', '○').replace('Ｘ', '×')
    
    is_correct = (user_answer == correct_answer)
    
    # Format the feedback text
    if correct_answer in ["是", "不是"]:
        answer_display = f"${correct_answer}$"
    else:
        answer_display = correct_answer

    if is_correct:
        result_text = f"完全正確！答案是 {answer_display}。"
    else:
        result_text = f"答案不正確。正確答案應為：{answer_display}"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}