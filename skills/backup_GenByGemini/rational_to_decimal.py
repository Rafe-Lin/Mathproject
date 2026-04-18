import random
from fractions import Fraction

def generate(level=1):
    """
    生成一道「有理數化為小數」的題目。
    level 1: 有限小數
    level 2: 循環小數
    """
    if level == 1:
        # 有限小數：分母是 2 和 5 的次方組合
        den = random.choice([2, 4, 5, 8, 10, 20, 25, 40, 50])
        num = random.randint(1, den - 1)
        question_text = f"請將分數 {num}/{den} 化為小數。"
        correct_answer = str(num / den)
    else: # level 2
        # 循環小數：分母包含 2, 5 以外的質因數
        den = random.choice([3, 6, 7, 9, 11, 12, 15])
        num = random.randint(1, den - 1)
        question_text = f"請將分數 {num}/{den} 化為循環小數。（例如：0.333... 請表示為 0.(3)）"
        
        # 手動計算循環小數以符合格式
        if den == 3: correct_answer = f"0.({num*3})"
        elif den == 6: correct_answer = "0.1(6)" if num == 1 else "0.8(3)" if num == 5 else f"0.({num*3})"
        elif den == 9: correct_answer = f"0.({num})"
        else: correct_answer = "請手動計算" # 簡化版，複雜情況可擴充

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

# 這裡可以加入 check 函式來比對答案