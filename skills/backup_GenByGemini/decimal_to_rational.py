import random
from fractions import Fraction

def generate(level=1):
    """
    生成一道「循環小數化為有理數」的題目。
    level 1: 純循環小數
    level 2: 混循環小數
    """
    if level == 1:
        # 純循環小數 0.(ab) = ab/99
        num = random.randint(1, 98)
        den = 9 if num < 10 else 99
        question_text = f"請將純循環小數 0.({num}) 化為最簡分數。"
        frac = Fraction(num, den)
        correct_answer = f"{frac.numerator}/{frac.denominator}"
    else: # level 2
        # 混循環小數 0.a(b) = (ab-a)/90
        non_repeating_part = random.randint(1, 9)
        repeating_part = random.randint(0, 9)
        while repeating_part == non_repeating_part:
            repeating_part = random.randint(0, 9)
        
        question_text = f"請將混循環小數 0.{non_repeating_part}({repeating_part}) 化為最簡分數。"
        num = int(f"{non_repeating_part}{repeating_part}") - non_repeating_part
        frac = Fraction(num, 90)
        correct_answer = f"{frac.numerator}/{frac.denominator}"

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}