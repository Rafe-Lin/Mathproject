# \向量\兩直線夾角 (向量法)
import random
import math
from .utils import check_answer

def generate(level=1):
    """
    生成一道「兩直線夾角 (向量法)」的題目。
    """
    if level == 1:
        # 構造特殊角度的法向量，如 90 度
        n1 = [1, 1]
        n2 = [1, -1]
        line1_eq = f"{n1[0]}x + {n1[1]}y + {random.randint(-5,5)} = 0"
        line2_eq = f"{n2[0]}x + {n2[1]}y + {random.randint(-5,5)} = 0"
        question_text = f"請求出兩直線 L₁: {line1_eq} 與 L₂: {line2_eq} 的夾角（0-90度）。"
        correct_answer = "90"
    else: # level 2, 一般角度
        n1 = [random.randint(1, 5), random.randint(1, 5)]
        # 確保法向量不是零向量
        while n1[0] == 0 and n1[1] == 0:
            n1 = [random.randint(1, 5), random.randint(1, 5)]
        n2 = [random.randint(1, 5), random.randint(1, 5)]
        # 確保法向量不是零向量
        while n2[0] == 0 and n2[1] == 0:
            n2 = [random.randint(1, 5), random.randint(1, 5)]
        line1_eq = f"{n1[0]}x + {n1[1]}y + {random.randint(-5,5)} = 0"
        line2_eq = f"{n2[0]}x + {n2[1]}y + {random.randint(-5,5)} = 0"
        question_text = f"請求出兩直線 L₁: {line1_eq} 與 L₂: {line2_eq} 夾角的 cos 值。(取正值)"
        
        dot_product = abs(n1[0]*n2[0] + n1[1]*n2[1])
        mag1 = math.sqrt(n1[0]**2 + n1[1]**2)
        mag2 = math.sqrt(n2[0]**2 + n2[1]**2)
        cos_theta = dot_product / (mag1 * mag2)
        correct_answer = str(round(cos_theta, 2))
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    return check_answer(user_answer, correct_answer, check_type='numeric')