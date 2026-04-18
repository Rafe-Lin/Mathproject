# \函數\函數四則運算
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「函數四則運算」的題目。
    """
    a, b = random.randint(1, 5), random.randint(1, 5)
    c, d = random.randint(1, 5), random.randint(1, 5)
    x_val = random.randint(1, 5)
    
    f_str = f"{a}x + {b}"
    g_str = f"{c}x - {d}"
    
    if level == 1:
        op_symbol = random.choice(['+', '-'])
        question_text = f"已知 f(x) = {f_str}，g(x) = {g_str}，請求出 (f {op_symbol} g)({x_val}) 的值。"
        f_val = a * x_val + b
        g_val = c * x_val - d
        correct_answer = str(f_val + g_val if op_symbol == '+' else f_val - g_val)
    else: # level 2
        op_symbol = random.choice(['·', '/'])
        question_text = f"已知 f(x) = {f_str}，g(x) = {g_str}，請求出 (f {op_symbol} g)({x_val}) 的值。"
        f_val = a * x_val + b
        g_val = c * x_val - d
        correct_answer = str(f_val * g_val if op_symbol == '·' else round(f_val / g_val, 2))
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    return check_answer(user_answer, correct_answer, check_type='numeric')