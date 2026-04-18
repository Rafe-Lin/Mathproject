import random
import math
from fractions import Fraction

def generate(level=1):
    """
    生成「海龍公式」相關題目。
    根據給定的三角形三邊長，計算其面積。
    """
    
    # Pre-defined combinations of (s-a, s-b, s-c) that result in integer areas.
    # These tuples represent (x, y, z) where x = s-a, y = s-b, z = s-c.
    # From these, we can derive:
    #   s = x + y + z (semi-perimeter)
    #   a = y + z
    #   b = x + z
    #   c = x + y
    # Heron's Formula: Area = sqrt(s * (s-a) * (s-b) * (s-c))
    # Area = sqrt(s * x * y * z)
    
    # Level 1 focuses on integer side lengths and integer areas.
    # List of (x, y, z) tuples that produce integer areas:
    valid_xyz_combinations = [
        (1, 2, 3),   # s=6, x=1, y=2, z=3 -> s*x*y*z = 36 -> Area=6. Sides: (3,4,5) (Right triangle)
        (1, 3, 12),  # s=16, x=1, y=3, z=12 -> s*x*y*z = 576 -> Area=24. Sides: (4,13,15)
        (1, 8, 9),   # s=18, x=1, y=8, z=9 -> s*x*y*z = 1296 -> Area=36. Sides: (9,10,17)
        (2, 3, 10),  # s=15, x=2, y=3, z=10 -> s*x*y*z = 900 -> Area=30. Sides: (5,12,13) (Right triangle)
        (2, 4, 6),   # s=12, x=2, y=4, z=6 -> s*x*y*z = 576 -> Area=24. Sides: (6,8,10) (Right triangle)
        (2, 3, 3),   # s=8, x=2, y=3, z=3 -> s*x*y*z = 144 -> Area=12. Sides: (5,5,6) (Isosceles triangle)
        (3, 5, 12),  # s=20, x=3, y=5, z=12 -> s*x*y*z = 3600 -> Area=60. Sides: (8,15,17) (Right triangle)
        (4, 6, 6),   # s=16, x=4, y=6, z=6 -> s*x*y*z = 2304 -> Area=48. Sides: (10,10,12) (Isosceles triangle)
        (5, 5, 8),   # s=18, x=5, y=5, z=8 -> s*x*y*z = 3600 -> Area=60. Sides: (13,13,10) (Isosceles triangle)
    ]

    # Select a random combination for the problem.
    # The 'level' parameter could be used to select from different lists
    # or ranges for more advanced problems, but for this skill, level 1 is sufficient.
    x, y, z = random.choice(valid_xyz_combinations)

    # Calculate semi-perimeter and side lengths from x, y, z
    s = x + y + z
    side_a = y + z
    side_b = x + z
    side_c = x + y

    # Sort side lengths for consistent problem presentation (e.g., 3, 4, 5 instead of 4, 3, 5)
    sides = sorted([side_a, side_b, side_c])
    a, b, c = sides[0], sides[1], sides[2]

    # Calculate area using Heron's formula.
    # The product s*x*y*z is guaranteed to be a perfect square by our choice of combinations.
    area_squared = s * x * y * z
    
    # Calculate the square root and convert to an integer.
    area = int(math.sqrt(area_squared))

    # Construct the question text using f-strings and LaTeX for mathematical expressions.
    # Note the use of $...$ for numbers that represent values.
    question_text = f"求三邊長分別為 ${a}$、${b}$、${c}$ 的三角形之面積。"
    correct_answer = str(area)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查使用者答案是否正確。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    
    is_correct = False
    result_text = ""

    try:
        user_num = float(user_answer)
        correct_num = float(correct_answer)
        
        # Using math.isclose for robust floating-point comparison,
        # although for integer answers, direct comparison might often suffice.
        if math.isclose(user_num, correct_num, rel_tol=1e-9, abs_tol=1e-9):
            is_correct = True
            result_text = f"完全正確！答案是 ${correct_answer}$。"
        else:
            result_text = f"答案不正確。您的答案是 ${user_answer}$，但正確答案應為：${correct_answer}$"
    except ValueError:
        # Handle cases where user_answer is not a valid number.
        result_text = f"答案格式不正確。請輸入一個數字。正確答案應為：${correct_answer}$"

    return {"correct": is_correct, "result": result_text, "next_question": True}