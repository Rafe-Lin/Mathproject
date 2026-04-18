import random

def generate_angle_problem():
    # Generate three valid angles for a triangle
    while True:
        # Generate angleA between 30 and 90 degrees
        angleA = random.randint(30, 90)
        # Generate angleB such that angleC (180 - angleA - angleB) is also at least 30 degrees
        # This ensures angleB is in the range [30, 180 - angleA - 30]
        angleB = random.randint(30, 180 - angleA - 30)
        angleC = 180 - angleA - angleB
        # Further ensure all angles are reasonably large (e.g., > 20 degrees)
        if angleC > 20 and angleA > 20 and angleB > 20: 
            break

    # Corresponding angles for DEF are the same as ABC due to congruence
    angles_map = {
        'A': angleA, 'B': angleB, 'C': angleC,
        'D': angleA, 'E': angleB, 'F': angleC
    }

    # Labels for all angles in both triangles
    all_angle_labels = ['A', 'B', 'C', 'D', 'E', 'F']

    # Decide which two angles to give as known values in the problem.
    # These can be from the same or different triangles.
    given_labels = random.sample(all_angle_labels, 2)
    given_val1 = angles_map[given_labels[0]]
    given_val2 = angles_map[given_labels[1]]

    # Decide which single angle to ask for. It must not be one of the given ones.
    ask_label = random.choice([label for label in all_angle_labels if label not in given_labels])
    correct_val = angles_map[ask_label]

    # Construct the question text using LaTeX for mathematical symbols
    question_text = (
        f"已知 $\\triangle ABC \\cong \\triangle DEF$，其中 $A$ 和 $D$、$B$ 和 $E$、$C$ 和 $F$ 為對應點。"
        f"若 $\\angle {given_labels[0]} = {given_val1}\\\circ$，$\\angle {given_labels[1]} = {given_val2}\\\circ$，"
        f"則 $\\angle {ask_label}$ 為多少度？"
    )
    correct_answer = str(correct_val)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_side_problem():
    # Generate three valid side lengths for a triangle
    while True:
        s1 = random.randint(5, 15)
        s2 = random.randint(5, 15)
        s3 = random.randint(5, 15)
        # Check triangle inequality: sum of any two sides must be greater than the third side
        if (s1 + s2 > s3) and (s1 + s3 > s2) and (s2 + s3 > s1):
            break
    
    # Map side lengths to corresponding segments based on congruence
    # Correspondence: AB<->DE, BC<->EF, CA<->FD
    sides_map = {
        'AB': s1, 'BC': s2, 'CA': s3,
        'DE': s1, 'EF': s2, 'FD': s3
    }
    
    # Labels for all sides in both triangles
    all_side_labels = ['AB', 'BC', 'CA', 'DE', 'EF', 'FD']

    # Decide which two side lengths to give as known values
    given_labels = random.sample(all_side_labels, 2)
    given_val1 = sides_map[given_labels[0]]
    given_val2 = sides_map[given_labels[1]]

    # Decide which single side length to ask for
    ask_label = random.choice([label for label in all_side_labels if label not in given_labels])
    correct_val = sides_map[ask_label]

    # Construct the question text using LaTeX for mathematical symbols
    question_text = (
        f"已知 $\\triangle ABC \\cong \\triangle DEF$，其中 $A$ 和 $D$、$B$ 和 $E$、$C$ 和 $F$ 為對應點。"
        f"若 $\\overline{{{given_labels[0]}}} = {given_val1}$，$\\overline{{{given_labels[1]}}} = {given_val2}$，"
        f"則 $\\overline{{{ask_label}}}$ 的長度為多少？"
    )
    correct_answer = str(correct_val)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    生成「三角形全等的意義」相關題目。
    題目類型包含：
    1. 透過全等關係判斷對應角
    2. 透過全等關係判斷對應邊
    """
    # Randomly choose between generating an angle problem or a side problem
    problem_type = random.choice(['angle', 'side'])
    
    if problem_type == 'angle':
        return generate_angle_problem()
    else: # 'side'
        return generate_side_problem()

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    # Normalize user answer and correct answer by stripping whitespace
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    
    is_correct = (user_answer == correct_answer)
    
    # If not strictly equal, try numerical comparison for floats/integers
    if not is_correct:
        try:
            if float(user_answer) == float(correct_answer):
                is_correct = True
        except ValueError:
            # If conversion to float fails, it's not a numerical match
            pass

    # Provide feedback to the user, including the correct answer in LaTeX format
    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}