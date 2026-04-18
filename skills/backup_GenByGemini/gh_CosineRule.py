import random
import math

# --- Helper Functions ---
def is_perfect_square(n):
    """
    Checks if a number is a perfect square, accounting for floating-point inaccuracies.
    """
    if n < 0:
        return False
    # Use a small tolerance for floating point comparisons to handle potential inaccuracies
    sqrt_n_approx = math.sqrt(n)
    sqrt_n_round = round(sqrt_n_approx)
    return abs(sqrt_n_approx - sqrt_n_round) < 1e-9 and sqrt_n_round * sqrt_n_round == n

def is_valid_triangle(a, b, c):
    """
    Checks if three given side lengths can form a valid triangle.
    """
    # Sum of any two sides must be greater than the third side
    # All sides must be positive
    return a + b > c and a + c > b and b + c > a and a > 0 and b > 0 and c > 0

def format_number(num, decimal_places=1):
    """
    Formats a number to a string, displaying integers as integers and floats with specified decimal places.
    Handles very small numbers by returning "0".
    """
    if abs(num) < 1e-9: # Treat very small numbers (effectively zero) as "0"
        return "0"
    if num == int(num):
        return str(int(num))
    return f"{num:.{decimal_places}f}"

def generate_find_side_problem(level):
    """
    Generates a problem to find the third side given two sides and the included angle (SAS).
    """
    side_b = random.randint(5, 15)
    side_c = random.randint(5, 15)
    
    # Cosine values for common angles (pre-calculated or approximate)
    cos_map = {
        60: 0.5,
        90: 0,
        120: -0.5,
        30: math.sqrt(3)/2, # approx 0.866
        45: math.sqrt(2)/2, # approx 0.707
        135: -math.sqrt(2)/2, # approx -0.707
        150: -math.sqrt(3)/2, # approx -0.866
    }

    angle_A_deg_choices = []
    if level == 1:
        # Prioritize angles that give exact or simple cosine values for Level 1
        angle_A_deg_choices = [60, 90, 120] 
    else: # Level 2+ for more varied angles
        # Include a wider range of angles, some of which will force rounding
        angle_A_deg_choices = [30, 45, 60, 70, 80, 90, 100, 110, 120, 135, 150]
        # Filter out 0 and 180 degrees and remove duplicates
        angle_A_deg_choices = sorted(list(set(choice for choice in angle_A_deg_choices if 0 < choice < 180)))
    
    angle_A_deg = random.choice(angle_A_deg_choices)
    
    # Get cosine value from map or calculate
    cos_A = cos_map.get(angle_A_deg)
    if cos_A is None: # For angles not in map (e.g., 70, 80, 100, 110 etc.)
        cos_A = math.cos(math.radians(angle_A_deg))

    a_squared = side_b**2 + side_c**2 - 2 * side_b * side_c * cos_A
    
    # Ensure a_squared is positive, clamping due to float precision
    a_squared = max(0.0, a_squared)

    side_a_val = math.sqrt(a_squared)
    
    # For Level 1, if side_a_val is an integer and the angle is "nice", provide exact integer answer.
    # Otherwise, provide rounding instructions.
    if level == 1 and is_perfect_square(a_squared) and angle_A_deg in [60, 90, 120]:
        correct_answer = str(int(side_a_val))
        question_text = (
            f"在 $\\triangle ABC$ 中，已知 $b={side_b}$，$c={side_c}$，$\\angle A={angle_A_deg}{{^\\circ}}$，"
            f"求 $a$ 的長度。"
        )
    else:
        # Default to rounding for all other cases or higher levels
        decimal_places = 1 if level == 1 else 2 # Level 1 rounds to 1 decimal, Level 2+ to 2 decimals
        correct_answer = format_number(side_a_val, decimal_places)
        question_text = (
            f"在 $\\triangle ABC$ 中，已知 $b={side_b}$，$c={side_c}$，$\\angle A={angle_A_deg}{{^\\circ}}$，"
            f"求 $a$ 的長度。(請四捨五入至小數點以下第{decimal_places}位)"
        )
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_find_angle_problem(level):
    """
    Generates a problem to find an angle given three side lengths (SSS).
    """
    while True:
        a, b, c = 0, 0, 0 # Initialize to ensure they are defined
        angle_label = random.choice(['A', 'B', 'C'])

        if level == 1:
            # Construct sides for exact angles (60, 90, 120) for Level 1
            target_angle_deg = random.choice([60, 90, 120])
            side1_gen = random.randint(5, 12)
            side2_gen = random.randint(5, 12)
            
            cos_target_angle = math.cos(math.radians(target_angle_deg))
            opposite_side_squared = side1_gen**2 + side2_gen**2 - 2 * side1_gen * side2_gen * cos_target_angle
            
            # Ensure opposite_side_squared is positive and a perfect square to get integer side
            if opposite_side_squared <= 0 or not is_perfect_square(opposite_side_squared):
                continue # Regenerate if conditions not met
            
            opposite_side_gen = int(math.sqrt(opposite_side_squared))
            
            # Assign generated sides based on the angle label chosen (e.g., if asking for A, then a=opposite)
            if angle_label == 'A':
                a, b, c = opposite_side_gen, side1_gen, side2_gen
            elif angle_label == 'B':
                a, b, c = side1_gen, opposite_side_gen, side2_gen
            else: # C
                a, b, c = side1_gen, side2_gen, opposite_side_gen
            
            if is_valid_triangle(a, b, c):
                correct_answer = str(target_angle_deg)
                question_text = (
                    f"在 $\\triangle ABC$ 中，已知 $a={a}$，$b={b}$，$c={c}$，"
                    f"求 $\\angle {angle_label}$ 的度數。"
                )
                return { # Return, successful generation for level 1
                    "question_text": question_text,
                    "answer": correct_answer,
                    "correct_answer": correct_answer
                }
            # If not a valid triangle, continue the while loop to try again

        else: # Level 2+ for arbitrary angles and rounding
            a = random.randint(5, 15)
            b = random.randint(5, 15)
            c = random.randint(5, 15)

            if not is_valid_triangle(a, b, c):
                continue # Regenerate if not a valid triangle

            # Determine which sides correspond to the angle we are asking for
            if angle_label == 'A':
                side1, side2, opposite_side = b, c, a
            elif angle_label == 'B':
                side1, side2, opposite_side = a, c, b
            else: # C
                side1, side2, opposite_side = a, b, c
            
            num = side1**2 + side2**2 - opposite_side**2
            den = 2 * side1 * side2
            
            if den == 0: # This should not happen with positive random.randint values
                continue
            
            cos_val = num / den

            # Clamp cos_val to [-1, 1] to prevent domain errors for math.acos
            # due to potential floating point inaccuracies (e.g., cos_val slightly > 1 or < -1)
            cos_val = max(-1.0, min(1.0, cos_val))
            
            angle_deg = math.degrees(math.acos(cos_val))

            decimal_places = 1 if level == 1 else 2
            correct_answer = format_number(angle_deg, decimal_places)
            question_text = (
                f"在 $\\triangle ABC$ 中，已知 $a={a}$，$b={b}$，$c={c}$，"
                f"求 $\\angle {angle_label}$ 的度數。(請四捨五入至小數點以下第{decimal_places}位)"
            )
            return { # Return, successful generation for level 2+
                "question_text": question_text,
                "answer": correct_answer,
                "correct_answer": correct_answer
            }
    
    # This part should ideally not be reached if generation is successful within the loop.
    # Added for robustness, though a `while True` loop with sufficient random options usually finds a solution.


def generate(level=1):
    """
    Generates "Cosine Rule" related math problems based on the specified level.
    Includes a retry mechanism and a fallback default problem.
    """
    problem_type = random.choice(['find_side', 'find_angle'])
    
    # Try a few times to generate a problem to increase chances of finding valid/clean numbers
    for _ in range(10): 
        try:
            if problem_type == 'find_side':
                problem = generate_find_side_problem(level)
            else: # find_angle
                problem = generate_find_angle_problem(level)
            
            # If problem generation was successful (returned a dict), break and return it
            if problem:
                return problem
        except Exception:
            # Catch potential errors during generation and retry
            continue
    
    # Fallback: if all attempts fail, generate a default simple problem
    # This ensures the function always returns a valid problem structure.
    return {
        "question_text": r"在 $\\triangle ABC$ 中，已知 $b=3$，$c=8$，$\\angle A=60{{^\\circ}}$，求 $a$ 的長度。",
        "answer": "7",
        "correct_answer": "7"
    }


def check(user_answer, correct_answer):
    """
    Checks if the user's answer is correct, allowing for floating point comparisons with appropriate tolerance.
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    
    is_correct = False
    feedback = ""

    try:
        user_num = float(user_answer)
        correct_num = float(correct_answer)
        
        # Determine tolerance based on whether correct_answer is an integer or float.
        # This allows for strict checking for exact integer answers and lenient checking for rounded answers.
        if correct_num == int(correct_num): # Correct answer is an integer (e.g., 7, 60)
             tolerance = 1e-9 # Very small tolerance for exact matches
        else: # Correct answer is a float (e.g., "11.1", "82.8")
             tolerance = 1e-2 # Standard tolerance for 1-2 decimal places (0.01 margin)

        if abs(user_num - correct_num) < tolerance:
            is_correct = True
            feedback = f"完全正確！答案是 ${correct_answer}$。"
        else:
            feedback = f"答案不正確。您的答案為 ${user_num}$，但正確答案應約為 ${correct_answer}$。"
    except ValueError:
        # If conversion to float fails, user might have entered non-numeric input.
        # For this skill, we generally expect numeric answers.
        if user_answer == correct_answer: # Basic string comparison for non-numeric exact matches
            is_correct = True
            feedback = f"完全正確！答案是 ${correct_answer}$。"
        else:
            feedback = f"答案不正確。請檢查您的輸入格式或計算。正確答案應為：${correct_answer}$。"

    return {"correct": is_correct, "result": feedback, "next_question": True}