# \複數\複數極式
import random
import cmath
from .utils import check_answer

def generate(level=1):
    """
    生成一道「複數極式」的轉換題目。
    """
    if level == 1:
        # 從極式構造，確保角度漂亮
        r = random.randint(2, 10)
        angle_deg = random.choice([30, 45, 60, 120, 150, 210, 240, 300, 330])
        z = cmath.rect(r, cmath.pi * angle_deg / 180)
        z_str = f"{round(z.real,2)} + {round(z.imag,2)}i".replace("+-","-")
        question_text = f"請將複數 z = {z_str} 轉換為極式 r(cosθ + i sinθ)，並求出 r 值。"
        correct_answer = str(r)
    else: # level 2
        z = complex(random.randint(-5, 5), random.randint(-5, 5))
        question_text = f"請將複數 z = {z} 轉換為極式 r(cosθ + i sinθ)，並求出主輻角 θ (0≤θ<360)。(四捨五入至整數位)"
        angle_deg = (cmath.phase(z) * 180 / cmath.pi + 360) % 360
        correct_answer = str(round(angle_deg))
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    return check_answer(user_answer, correct_answer, check_type='numeric')