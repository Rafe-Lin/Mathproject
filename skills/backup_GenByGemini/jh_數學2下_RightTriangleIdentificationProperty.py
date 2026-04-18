import random
import math

def _assign_and_find(s1, s2, s3):
    """
    Helper function to randomly assign sides to labels AB, BC, CA,
    and identify the angle opposite the longest side.
    Handles both integer and (value, string) tuple inputs for sides.
    """
    sides = [s1, s2, s3]
    labels = ['AB', 'BC', 'CA']
    random.shuffle(sides)
    
    assigned_sides = dict(zip(labels, sides))
    
    side_values = {}
    side_displays = {}
    for label, side in assigned_sides.items():
        if isinstance(side, tuple):
            side_values[label] = side[0]
            side_displays[label] = side[1]
        else:
            side_values[label] = side
            side_displays[label] = str(side)
            
    longest_side_label = max(side_values, key=side_values.get)
    
    angle_map = {'BC': 'A', 'CA': 'B', 'AB': 'C'}
    opposite_angle = angle_map[longest_side_label]
    
    return side_displays, opposite_angle

def generate_right_triangle_problem():
    """Generates a problem where the sides form a right triangle."""
    triples = [(3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25)]
    a, b, c = random.choice(triples)
    
    # Scale the triple to add variety
    k = random.randint(1, 3)
    s1, s2, s3 = k * a, k * b, k * c

    side_displays, opposite_angle = _assign_and_find(s1, s2, s3)
    
    question_text = f"下列各組數是否可以構成直角△ABC？如果可以，寫出直角三角形中哪個角是直角。<br>$\\overline{{AB}}={side_displays['AB']}$，$\\overline{{BC}}={side_displays['BC']}$，$\\overline{{CA}}={side_displays['CA']}$"
    
    correct_answer = f"是，∠{opposite_angle}是直角"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_non_right_triangle_problem():
    """Generates a problem where the sides do not form a right triangle."""
    # Choose between two methods for generating non-right triangles
    if random.random() < 0.6:
        # Method 1: Perturb an integer Pythagorean triple
        triples = [(3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25)]
        a, b, c = random.choice(triples)
        
        k = random.randint(1, 2)
        ka, kb, kc = k * a, k * b, k * c

        # Perturb the longest side by a small amount to break the property
        perturbed_c = kc + random.choice([-1, 1])

        s1, s2, s3 = ka, kb, perturbed_c
        side_displays, _ = _assign_and_find(s1, s2, s3)

    else:
        # Method 2: Use a square root, similar to the reference example
        a = random.randint(2, 7)
        b = random.randint(2, 7)
        while a == b:
            b = random.randint(2, 7)
        
        sum_sq = a**2 + b**2
        
        # Perturb the sum of squares, then take the sqrt
        perturbation = random.choice([-3, -2, -1, 1, 2, 3])
        c_sq = sum_sq + perturbation
        if c_sq <= 0: # Ensure the value under the root is positive
            c_sq = sum_sq + 1

        s1 = a
        s2 = b
        # Store as a tuple: (numerical value for comparison, display string)
        s3 = (math.sqrt(c_sq), f"\\sqrt{{{c_sq}}}")

        side_displays, _ = _assign_and_find(s1, s2, s3)
        
    question_text = f"下列各組數是否可以構成直角△ABC？如果可以，寫出直角三角形中哪個角是直角。<br>$\\overline{{AB}}={side_displays['AB']}$，$\\overline{{BC}}={side_displays['BC']}$，$\\overline{{CA}}={side_displays['CA']}$"
    
    correct_answer = "不是"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    生成關於「畢氏定理的逆敘述」的題目。
    要求學生判斷給定的三邊長是否能構成直角三角形，如果可以，並指出哪個角是直角。
    """
    # 65% chance to generate a right triangle problem, 35% for non-right
    if random.random() < 0.65:
        return generate_right_triangle_problem()
    else:
        return generate_non_right_triangle_problem()

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    # Normalize user answer for common variations
    normalized_user_answer = user_answer.strip().replace(" ", "").replace("，", ",").replace("角", "∠")
    normalized_correct_answer = correct_answer.strip().replace(" ", "").replace("，", ",")
    
    is_correct = (normalized_user_answer == normalized_correct_answer)
    
    # Generate feedback with nicely formatted LaTeX
    if '是' in correct_answer:
        angle = correct_answer.split('∠')[1][0]
        result_answer_latex = f"是，$\\angle {angle}$是直角"
    else:
        result_answer_latex = correct_answer

    if is_correct:
        result_text = f"完全正確！答案是 {result_answer_latex}。"
    else:
        result_text = f"答案不正確。正確答案應為：{result_answer_latex}"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}