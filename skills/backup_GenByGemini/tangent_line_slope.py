# \微分\切線斜率
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「切線斜率」的題目。
    """
    # 隨機選擇題型
    q_type = random.choice(['forward', 'reverse']) if level > 1 else 'forward'

    if q_type == 'forward':
        a = random.randint(1, 5)
        c, d = random.randint(2, 5), random.randint(1, 10)
        if level == 1:
            question_text = f"請求出函數 f(x) = {c}x + {d} 在 x={a} 處的切線斜率。"
            correct_answer = str(c)
        else: # level 2
            b, c_const = random.randint(2, 5), random.randint(1, 5)
            question_text = f"請求出函數 f(x) = {b}x² + {c_const} 在 x={a} 處的切線斜率。"
            # f'(x) = 2bx => f'(a) = 2ba
            correct_answer = str(2 * b * a)
    else: # q_type == 'reverse' (Level 3+)
        b, c_const = random.randint(2, 5), random.randint(1, 5)
        x_sol = random.randint(1, 5)
        slope = 2 * b * x_sol
        question_text = f"已知函數 f(x) = {b}x² + {c_const} 的圖形在某點的切線斜率為 {slope}，請求出該點的 x 坐標。"
        correct_answer = str(x_sol)

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    return check_answer(user_answer, correct_answer, check_type='numeric')