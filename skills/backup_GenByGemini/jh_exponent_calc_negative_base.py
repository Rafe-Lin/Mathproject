# \指數\指數 (負數底)
import random
from .utils import check_answer, to_superscript

def generate(level=1):
    """
    生成一道「指數 (負數底)」的題目，並確保次方使用上標顯示。
    """
    base = random.randint(-5, -2)

    if level == 1:
        # Level 1: 偶數次方，結果為正
        exp = random.choice([2, 4])
    else: # level 2
        # Level 2: 奇數次方，結果為負
        exp = random.choice([3, 5])

    # 使用 to_superscript 函式來格式化次方
    exp_super = to_superscript(exp)
    
    question_text = f"請問 ({base}){exp_super} 的值是多少？"
    
    correct_answer = str(base ** exp)
    
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    return check_answer(user_answer, correct_answer, check_type='numeric')