import random
import re
from fractions import Fraction

def _format_linear_expr(coeff, const, var='x'):
    """Helper function to format linear expressions like '3x - 20'."""
    if coeff == 0 and const == 0:
        return "0"
    
    # Coefficient part
    if coeff == 1:
        term1 = var
    elif coeff == -1:
        term1 = f"-{var}"
    elif coeff != 0:
        term1 = f"{coeff}{var}"
    else:
        term1 = ""

    # Constant part
    if const == 0:
        return term1
    
    if term1 == "":
        return str(const)

    op = "+" if const > 0 else "-"
    return f"{term1} {op} {abs(const)}"

def generate_angle_algebra_problem():
    """
    Generates problems involving finding angles by solving linear equations.
    Covers properties: opposite angles are equal, consecutive angles are supplementary.
    """
    if random.random() < 0.5:  # Opposite angles are equal: ∠A = ∠C
        a = random.randint(2, 5)
        c = random.randint(1, a - 1)
        x = random.randint(15, 40)
        
        while True:
            b = random.randint(-50, 50)
            angle_val = a * x + b
            if 10 < angle_val < 170:
                break
        
        d = (a - c) * x + b
        
        expr_A = _format_linear_expr(a, b)
        expr_C = _format_linear_expr(c, d)

        if random.random() < 0.5:
            expr_A, expr_C = expr_C, expr_A
            
        angle_B = 180 - angle_val
        
        question_text = f"在平行四邊形 ABCD 中，若 $\\angle A = ( {expr_A} )^\\circ$、$\\angle C = ( {expr_C} )^\\circ$，則 $\\angle B$ 的度數為何？"
        correct_answer = str(angle_B)
        
    else:  # Consecutive angles are supplementary: ∠A + ∠B = 180
        a = random.randint(1, 3)
        c = random.randint(1, 3)
        x = random.randint(20, 45)
        
        while True:
            b = random.randint(-40, 40)
            d = 180 - (a + c) * x - b
            angle_A = a * x + b
            angle_B = c * x + d
            if 10 < angle_A < 170 and 10 < angle_B < 170:
                break
        
        expr_A = _format_linear_expr(a, b)
        expr_B = _format_linear_expr(c, d)
        
        target_angle_name = random.choice(['C', 'D'])
        if target_angle_name == 'C':
            correct_answer = str(angle_A)
        else: # 'D'
            correct_answer = str(angle_B)
            
        question_text = f"在平行四邊形 ABCD 中，$\\angle A$ 比 $\\angle B$ 的 {c//a} 倍多 {d-b}°。若設 $\\angle A=x^\\circ$，則 $\\angle B=({_format_linear_expr(c,d)})^\\circ$。請問這個平行四邊形的 $\\angle {target_angle_name}$ 是幾度？<br>另一種問法：在平行四邊形 ABCD 中，若 $\\angle A = ( {expr_A} )^\\circ$、$\\angle B = ( {expr_B} )^\\circ$，則 $\\angle {target_angle_name}$ 的度數為何？"
        # Let's simplify the question text to one form
        question_text = f"在平行四邊形 ABCD 中，若 $\\angle A = ( {expr_A} )^\\circ$、$\\angle B = ( {expr_B} )^\\circ$，則 $\\angle {target_angle_name}$ 的度數為何？"
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_angle_simple_problem():
    """
    Given one angle, find the other three.
    """
    angle = random.randint(20, 160)
    while angle == 90:
        angle = random.randint(20, 160)
    
    other_angle = 180 - angle
    
    given_angle_name = random.choice(['A', 'B'])
    
    question_text = f"一個平行四邊形 ABCD 中，已知 $\\angle {given_angle_name} = {angle}^\\circ$，求其他三個內角的度數。"
    if given_angle_name == 'A':
        correct_answer = f"∠C={angle}°, ∠B=∠D={other_angle}°"
    else: # 'B'
        correct_answer = f"∠D={angle}°, ∠A=∠C={other_angle}°"
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_side_algebra_problem():
    """
    Find side lengths or perimeter by solving linear equations.
    """
    if random.random() < 0.5: # AB = a*BC+c1, CD = b*AD+c2 style
        x = random.randint(10, 25)  # Let x be BC
        a1 = random.randint(2, 4)
        a2 = random.randint(1, a1 - 1)
        c1 = random.randint(-15, 15)
        c2 = (a1 - a2) * x + c1
        
        side_bc = x
        side_ab = a1 * x + c1
        
        if side_ab <= 0 or side_bc <= 0: return generate_side_algebra_problem()

        perimeter = 2 * (side_ab + side_bc)
        
        op1 = "多" if c1 >= 0 else "少"
        val1 = abs(c1)
        op2 = "多" if c2 >= 0 else "少"
        val2 = abs(c2)

        question_text = f"在平行四邊形 ABCD 中，$\\overline{{AB}}$ 比 $\\overline{{BC}}$ 的 ${a1}$ 倍{op1} ${val1}$ 公分，且 $\\overline{{CD}}$ 比 $\\overline{{AD}}$ 的 ${a2}$ 倍{op2} ${val2}$ 公分，則此平行四邊形 ABCD 的周長為多少公分？"
        correct_answer = str(perimeter)
    else: # AB = 3a+5, CD = 8a-20 style
        a_val = random.randint(3, 10)
        a_coeff = random.randint(2, 5)
        c_coeff = random.randint(a_coeff + 1, 8)

        a_const = random.randint(-30, 30)
        c_const = a_coeff * a_val + a_const - c_coeff * a_val
        
        expr_ab = _format_linear_expr(a_coeff, a_const, 'a')
        expr_cd = _format_linear_expr(c_coeff, c_const, 'a')
        
        side_ab = a_coeff * a_val + a_const

        b_coeff = random.randint(2, 5)
        b_const = random.randint(-20, 20)
        side_bc = b_coeff * a_val + b_const

        if side_ab <= 0 or side_bc <= 0: return generate_side_algebra_problem()

        perimeter = 2 * (side_ab + side_bc)
        expr_bc = _format_linear_expr(b_coeff, b_const, 'a')

        question_text = f"在平行四邊形 ABCD 中，$\\overline{{AB}} = ( {expr_ab} )$ 公分，$\\overline{{BC}} = ( {expr_bc} )$ 公分，$\\overline{{CD}} = ( {expr_cd} )$ 公分，則此平行四邊形 ABCD 的周長為多少公分？"
        correct_answer = str(perimeter)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_side_perimeter_ratio_problem():
    """
    Given perimeter and ratio of adjacent sides, find side lengths.
    """
    side1 = random.randint(5, 15)
    ratio = random.randint(2, 4)
    side2 = side1 * ratio
    
    perimeter = 2 * (side1 + side2)
    
    question_text = f"已知一個平行四邊形 ABCD 的周長為 ${perimeter}$ 公分，且其中一邊長是另一相鄰邊長的 ${ratio}$ 倍，則此平行四邊形較短的邊長為多少公分？"
    correct_answer = str(side1)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_diagonal_length_problem():
    """
    Problems about diagonals bisecting each other.
    """
    if random.random() < 0.5: # Given OA and OB, find AC + BD
        oa = random.randint(3, 10)
        ob = random.randint(oa + 1, 15)
        sum_diagonals = 2 * oa + 2 * ob
        question_text = f"在平行四邊形 ABCD 中，對角線 $\\overline{{AC}}$ 與 $\\overline{{BD}}$ 相交於 O 點。若 $\\overline{{OA}} = {oa}$ 公分，$\\overline{{OB}} = {ob}$ 公分，則兩條對角線的長度和 ($\\overline{{AC}} + \\overline{{BD}}$) 為多少公分？"
        correct_answer = str(sum_diagonals)
    else: # Given OA + OB, find AC + BD
        sum_oa_ob = random.randint(10, 25)
        sum_diagonals = 2 * sum_oa_ob
        question_text = f"在平行四邊形 ABCD 中，對角線 $\\overline{{AC}}$ 與 $\\overline{{BD}}$ 相交於 O 點。若 $\\overline{{OA}} + \\overline{{OB}} = {sum_oa_ob}$，則 $\\overline{{AC}} + \\overline{{BD}}$ 的長度為何？"
        correct_answer = str(sum_diagonals)
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_diagonal_area_problem():
    """
    Problems about diagonals dividing the area into four equal triangles.
    """
    if random.random() < 0.5: # General case: Given area of one small triangle
        area_aob = random.randint(15, 40)
        area_abcd = 4 * area_aob
        question_text = f"在平行四邊形 ABCD 中，對角線 $\\overline{{AC}}$ 與 $\\overline{{BD}}$ 相交於 O 點。若 $\\triangle AOB$ 的面積為 ${area_aob}$ 平方單位，則平行四邊形 ABCD 的面積為多少平方單位？"
        correct_answer = str(area_abcd)
    else: # Special case: Perpendicular diagonals (rhombus)
        oa = random.randint(3, 8)
        ob = random.randint(4, 12)
        area_abcd = 2 * oa * ob
        question_text = f"在一個特殊的平行四邊形 ABCD 中，已知其對角線 $\\overline{{AC}}$ 與 $\\overline{{BD}}$ 互相垂直且相交於 O 點。若 $\\overline{{OA}} = {oa}$ 公分，$\\overline{{OB}} = {ob}$ 公分，求此平行四邊形 ABCD 的面積為多少平方公分？"
        correct_answer = str(area_abcd)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }
    
def generate_diagonal_pythagorean_problem():
    """
    Problems involving diagonals and Pythagorean theorem in a rhombus.
    """
    triples = [(5, 4, 3), (13, 12, 5), (17, 15, 8), (25, 24, 7)]
    c, b, a = random.choice(triples) # c=hypotenuse, a,b=legs
    
    # In right triangle BOC, BC=c, BO=b, CO=a
    bc = c
    bd = 2 * b
    ac = 2 * a
    
    area = int(0.5 * ac * bd)
    
    if random.random() < 0.5: # Ask for AC
        question_text = f"在平行四邊形 ABCD 中，已知對角線 $\\overline{{AC}} \\perp \\overline{{BD}}$。若 $\\overline{{BC}} = {bc}$ 公分，$\\overline{{BD}} = {bd}$ 公分，求 $\\overline{{AC}}$ 的長度為多少公分？"
        correct_answer = str(ac)
    else: # Ask for Area
        question_text = f"在平行四邊形 ABCD 中，已知對角線 $\\overline{{AC}} \\perp \\overline{{BD}}$。若 $\\overline{{BC}} = {bc}$ 公分，$\\overline{{BD}} = {bd}$ 公分，求平行四邊形 ABCD 的面積為多少平方公分？"
        correct_answer = str(area)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_area_bisection_concept_problem():
    """
    Conceptual question about the line that bisects the area.
    """
    question_text = "如果要畫一條直線將平行四邊形 ABCD 的面積平分，這條直線必須通過下列哪一個特殊點？<br>(A) 頂點 A<br>(B) 邊 $\\overline{{AB}}$ 的中點<br>(C) 對角線 $\\overline{{AC}}$ 與 $\\overline{{BD}}$ 的交點<br>(D) 平行四邊形內的任意一點"
    correct_answer = "C"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    Generates a question about the meaning and properties of parallelograms.
    """
    problem_types = [
        'angle_algebra', 
        'angle_simple', 
        'side_algebra', 
        'side_perimeter_ratio', 
        'diagonal_length', 
        'diagonal_area', 
        'diagonal_pythagorean', 
        'area_bisection_concept'
    ]
    problem_type = random.choice(problem_types)
    
    if problem_type == 'angle_algebra':
        return generate_angle_algebra_problem()
    elif problem_type == 'angle_simple':
        return generate_angle_simple_problem()
    elif problem_type == 'side_algebra':
        return generate_side_algebra_problem()
    elif problem_type == 'side_perimeter_ratio':
        return generate_side_perimeter_ratio_problem()
    elif problem_type == 'diagonal_length':
        return generate_diagonal_length_problem()
    elif problem_type == 'diagonal_area':
        return generate_diagonal_area_problem()
    elif problem_type == 'diagonal_pythagorean':
        return generate_diagonal_pythagorean_problem()
    else: # area_bisection_concept
        return generate_area_bisection_concept_problem()

def check(user_answer, correct_answer):
    """
    Checks if the user's answer is correct.
    """
    user_answer = user_answer.strip().upper()
    correct_answer = str(correct_answer).strip().upper()

    is_correct = (user_answer == correct_answer)

    # If string comparison fails, try numerical comparison for non-MCQ
    if not is_correct and not (len(correct_answer) == 1 and correct_answer.isalpha()):
        try:
            # Clean user input from common units or symbols for parsing
            user_num_str = re.sub(r'[^\d.-]', '', user_answer)
            correct_num_str = re.sub(r'[^\d.-]', '', correct_answer)
            
            if user_num_str and correct_num_str:
                user_val = float(user_num_str)
                correct_val = float(correct_num_str)
                # Use a small tolerance for float comparison
                if abs(user_val - correct_val) < 1e-9:
                    is_correct = True
        except (ValueError, TypeError):
            # Cannot be converted to numbers, stick with string comparison result
            pass
            
    # For angle_simple, the answer format is complex, so we check for components
    if "∠" in correct_answer or "°" in correct_answer:
        # A simple check: if user answer contains all numbers from correct answer
        correct_nums = set(re.findall(r'\d+', correct_answer))
        user_nums = set(re.findall(r'\d+', user_answer))
        if correct_nums and correct_nums.issubset(user_nums):
            is_correct = True


    if is_correct:
        result_text = f"完全正確！答案是 ${correct_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer}$。"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}