# \三角函數\三角圖形 (週期伸縮)
import random
from fractions import Fraction
from .utils import check_answer

def generate(level=1):
    """
    生成一道「三角圖形 (週期伸縮)」的題目。
    """
    b = random.randint(2, 6)
    func = random.choice(['sin', 'cos'])
    
    if level == 1:
        question_text = f"請問函數 y = {func}({b}x) 的週期是多少？ (以 π 表示)"
        period = Fraction(2, b)
        correct_answer = f"{period.numerator}π/{period.denominator}" if period.denominator != 1 else (f"{period.numerator}π" if period.numerator != 1 else "π")
    else: # level 2, 逆向提問
        period_str = random.choice(["π", "π/2", "4π"])
        if period_str == "π": correct_b = 2
        elif period_str == "π/2": correct_b = 4
        else: correct_b = "1/2"
        question_text = f"已知函數 y = {func}(bx) 的週期為 {period_str}，若 b > 0，請問 b 的值是多少？"
        correct_answer = str(correct_b)
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user_answer = user_answer.replace(" ", "").replace("pi", "π")
    return check_answer(user_answer, correct_answer)