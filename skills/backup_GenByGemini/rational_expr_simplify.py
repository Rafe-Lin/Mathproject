# \多項式\分式化簡
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「分式化簡」的題目。
    """
    # 構造 (x-a)(x-b) / (x-a)(x-c)
    a = random.randint(-5, 5)
    b = random.randint(-5, 5)
    c = random.randint(-5, 5)
    while a==b or a==c or b==c:
        b = random.randint(-5, 5)
        c = random.randint(-5, 5)
        
    num_str = f"(x² + {-(a+b)}x + {a*b})"
    den_str = f"(x² + {-(a+c)}x + {a*c})"
    
    question_text = f"請化簡下列分式：{num_str} / {den_str}"
    correct_answer = f"(x-{b})/(x-{c})"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user_answer = user_answer.replace(" ", "")
    return check_answer(user_answer, correct_answer)