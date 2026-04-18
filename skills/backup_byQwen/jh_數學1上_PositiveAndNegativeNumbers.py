import random
from fractions import Fraction
import math

def to_latex(num):
    """
    Core Utility: Converts numbers to LaTeX format.
    Handles: Floats (fixes precision), Fractions (proper/improper/mixed), Integers.
    """
    if isinstance(num, int): return str(num)
    if isinstance(num, float):
        num = Fraction(str(num)).limit_denominator(100) # Fix IEEE 754
    if isinstance(num, Fraction):
        if num.denominator > 1000: num = num.limit_denominator(100)
        if num.denominator == 1: return str(num.numerator)
        # Mixed Fraction Logic
        if abs(num.numerator) > num.denominator:
            sign = "-" if num.numerator < 0 else ""
            abs_num = abs(num)
            i = abs_num.numerator // abs_num.denominator
            rem = abs_num - i
            return f"{sign}{i} \\frac{{{rem.numerator}}}{{{rem.denominator}}}"
        return f"\\frac{{{num.numerator}}}{{{num.denominator}}}"
    return str(num)

def sub_problem_type_A():
    # Word problem involving positive and negative numbers in real-life context
    base_location = random.choice(["學校", "商店", "車站", "公園"])
    direction_positive = random.choice(["東邊", "北邊", "前進"])
    direction_negative = random.choice(["西邊", "南邊", "後退"])
    pos_distance = random.randint(1, 20)
    neg_distance = random.randint(1, 20)
    
    question_text = f"以{base_location}的位置為基準，{base_location}的{direction_positive}當作正向，{base_location}的{direction_negative}為負向。若甲地位在{base_location}的{direction_positive} {pos_distance} 公里處，記為「＋{pos_distance}」公里，則乙地位在{base_location}的{direction_negative} {neg_distance} 公里處，應該怎麼記錄？"
    
    answer = f"-{neg_distance} 公里"
    correct_answer = f"-{neg_distance} 公里"
    
    return {'question_text': question_text, 'answer': answer, 'correct_answer': correct_answer}

def sub_problem_type_B():
    # Word problem involving gains/losses in financial context
    item = random.choice(["花", "書", "玩具", "零食"])
    profit_loss = random.choice(["賺", "賠"])
    amount = random.randint(10, 100)
    
    question_text = f"商店老闆每賣出一{item}，就會記錄這筆交易的賺賠情形，他以「＋」表示{profit_loss}錢，以「-」表示{profit_loss}錢。例如：{profit_loss}了 {amount} 元，就記為「＋{amount}」元。試回答下列問題：\n⑴ 若{profit_loss}了 {amount} 元，應該怎麼記錄？"
    
    answer = f"-{amount} 元"
    correct_answer = f"-{amount} 元"
    
    return {'question_text': question_text, 'answer': answer, 'correct_answer': correct_answer}

def sub_problem_type_C():
    # Identify negative numbers, integers, and same-sign numbers
    numbers = []
    for _ in range(5):
        if random.choice([True, False]):
            numbers.append(random.randint(-20, -1))
        else:
            numbers.append(random.randint(1, 20))
    
    # Add some fractions
    frac1 = Fraction(random.randint(1, 5), random.randint(2, 5))
    frac2 = Fraction(random.randint(1, 5), random.randint(2, 5))
    if random.choice([True, False]):
        frac1 = -frac1
    if random.choice([True, False]):
        frac2 = -frac2
    numbers.extend([frac1, frac2])
    
    # Pick one number to be the reference (negative)
    ref_num = random.choice([n for n in numbers if isinstance(n, Fraction) and n < 0] + [n for n in numbers if isinstance(n, int) and n < 0])
    
    # Convert all to LaTeX strings
    latex_nums = [to_latex(n) for n in numbers]
    
    question_text = f"下列各數中，哪些是負數？哪些是整數？哪些與${to_latex(ref_num)}$ 是同號數？\n{' '.join([f'${to_latex(n)}$' for n in numbers])}"
    
    # Identify negative numbers
    negatives = [to_latex(n) for n in numbers if n < 0]
    
    # Identify integers
    integers = [to_latex(n) for n in numbers if isinstance(n, int) or (isinstance(n, Fraction) and n.denominator == 1)]
    
    # Same sign numbers
    same_sign = [to_latex(n) for n in numbers if (n < 0) == (ref_num < 0)]
    
    answer = f"負數：{'、'.join(negatives)}；整數：{'、'.join(integers)}；{to_latex(ref_num)} 的同號數：{'、'.join(same_sign)}"
    correct_answer = answer
    
    return {'question_text': question_text, 'answer': answer, 'correct_answer': correct_answer}

def generate(level=1):
    # Randomly select ONE problem type
    problem_type = random.choice(['Type A', 'Type B', 'Type C'])
    if problem_type == 'Type A': return sub_problem_type_A()
    elif problem_type == 'Type B': return sub_problem_type_B()
    else: return sub_problem_type_C()