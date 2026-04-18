# \多項式\多項式的 GCF / LCM
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「多項式的 GCF / LCM」的題目。
    """
    # 構造公因式
    common_factor = f"(x - {random.randint(1, 5)})"
    
    # 構造兩個多項式
    p1_factor = f"(x + {random.randint(1, 5)})"
    p2_factor = f"(x - {random.randint(6, 10)})"
    # 雖然範圍不同，但為了絕對保險，加上檢查
    while p1_factor == p2_factor: # 確保兩個多項式不完全相同
        p1_factor = f"(x + {random.randint(1, 5)})"
    
    poly1_str = f"{common_factor}{p1_factor}"
    poly2_str = f"{common_factor}{p2_factor}"
    
    if level == 1:
        question_text = f"請求出多項式 A = {poly1_str} 與 B = {poly2_str} 的最高公因式 (GCF)。"
        correct_answer = common_factor
    else: # level 2
        question_text = f"請求出多項式 A = {poly1_str} 與 B = {poly2_str} 的最低公倍式 (LCM)。"
        correct_answer = f"{common_factor}{p1_factor}{p2_factor}"
        
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user_answer = user_answer.replace(" ", "")
    return check_answer(user_answer, correct_answer)