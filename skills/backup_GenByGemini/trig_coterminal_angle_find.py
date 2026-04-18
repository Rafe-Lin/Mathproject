# \三角函數\同界角
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「同界角」的題目。
    """
    if level == 1:
        # 給一個大於 360 的角，求最小正同界角
        angle = random.randint(400, 800)
        question_text = f"請問 {angle}° 的最小正同界角是多少度？"
        correct_answer = str(angle % 360)
    else: # level 2, 負角或求最大負同界角
        q_type = random.choice(['negative_to_positive', 'find_negative'])
        if q_type == 'negative_to_positive':
            angle = random.randint(-700, -100)
            question_text = f"請問 {angle}° 的最小正同界角是多少度？"
            correct_answer = str(angle % 360)
        else: # find_negative
            angle = random.randint(100, 700)
            question_text = f"請問 {angle}° 的最大負同界角是多少度？"
            correct_answer = str((angle % 360) - 360)
            
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    return check_answer(user_answer, correct_answer, check_type='numeric')