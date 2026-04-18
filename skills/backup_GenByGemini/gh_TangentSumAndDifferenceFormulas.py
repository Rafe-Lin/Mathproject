# skills/gh_TangentSumAndDifferenceFormulas.py
import random
from sympy import symbols, sin, cos, tan, latex, N

def generate(level=1):
    """
    Generates a question for Tangent Sum and Difference Formulas.
    TODO: Implement the actual logic for different levels.
    """
    # Placeholder implementation
    alpha_deg = random.choice([30, 45, 60, 120])
    beta_deg = random.choice([30, 45, 60])
    
    op = random.choice(['+', '-'])

    # For now, let's ask for tan(alpha + beta) or tan(alpha - beta)
    question_text = f"試求 tan({alpha_deg}° {op} {beta_deg}°) 的值。（若答案為分數，請寫成小數並四捨五入到小數點後三位）"
    
    # Calculate correct answer using sympy for precision
    alpha_rad = alpha_deg * 3.1415926535 / 180
    beta_rad = beta_deg * 3.1415926535 / 180
    
    tan_alpha = tan(alpha_rad)
    tan_beta = tan(beta_rad)
    
    if op == '+':
        correct_expr = (tan_alpha + tan_beta) / (1 - tan_alpha * tan_beta)
    else: # op == '-'
        correct_expr = (tan_alpha - tan_beta) / (1 + tan_alpha * tan_beta)

    # Evaluate the expression to a float and round it
    correct_answer = f"{N(correct_expr):.3f}"
    
    return {
        "question_text": question_text,
        "answer": str(correct_answer),
        "correct_answer": "text",
        "context_string": f"求 tan({alpha_deg}° {op} {beta_deg}°)"
    }

def check(user_answer, correct_answer_str):
    """
    Checks the user's answer.
    """
    try:
        user_val = float(user_answer)
        correct_val = float(correct_answer_str)
        
        # Check if the user's answer is close enough to the correct answer
        is_correct = abs(user_val - correct_val) < 0.001
        
        if is_correct:
            return {
                "correct": True,
                "result": f"正確！答案約為 {correct_answer_str}",
                "next_question": True
            }
        else:
            return {
                "correct": False,
                "result": f"錯誤，正確答案應約為 {correct_answer_str}",
                "next_question": False
            }
    except (ValueError, TypeError):
        return {
            "correct": False,
            "result": f"請輸入有效的數值。正確答案應約為 {correct_answer_str}",
            "next_question": False
        }
