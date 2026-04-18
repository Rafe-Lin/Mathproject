# \直線方程式\二元一次不等式的圖形
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道關於「二元一次不等式圖形」的觀念題。
    """
    a = random.randint(1, 5)
    b = random.randint(1, 5)
    c = random.randint(1, 5)
    op = random.choice(['>=', '<='])
    
    line_eq = f"{a}x + {b}y + {c} = 0"
    ineq_eq = f"{a}x + {b}y + {c} {op} 0"

    # 確保選項之間有換行符 \n
    question_text = (
        f"二元一次不等式 {ineq_eq} 的圖形為直線 {line_eq} 的某一側半平面。\n"
        "要判斷是哪一側，我們通常代入哪個「不在線上」的點來測試？\n\n"
        "A) (1, 1)\n"
        "B) (-1, -1)\n"
        "C) (0, 0) 原點"
    )
    correct_answer = "C"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    return check_answer(user_answer, correct_answer, check_type='case_insensitive')