# \代數\化簡 (分數型)
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「化簡 (分數型)」的題目，並確保格式正確。
    """
    if level == 1:
        # Level 1: 簡單的整除化簡
        # 構造分子 (ax + b) 和分母 c，確保 a 和 b 都是 c 的倍數
        denominator = random.randint(2, 5)
        
        # 確保係數和常數項都是分母的倍數
        coeff_x = denominator * random.randint(-5, 5)
        while coeff_x == 0: coeff_x = denominator * random.randint(-5, 5)
        
        const_term = denominator * random.randint(-5, 5)

        # 處理分子字串，避免 "+ -" 的情況
        if const_term > 0:
            numerator_str = f"{coeff_x}x + {const_term}"
        elif const_term < 0:
            numerator_str = f"{coeff_x}x - {abs(const_term)}"
        else: # const_term == 0
            numerator_str = f"{coeff_x}x"

        question_text = f"請化簡下列式子：({numerator_str}) / {denominator}"
        
        # 計算正確答案
        ans_coeff_x = coeff_x // denominator
        ans_const = const_term // denominator
        
        if ans_const > 0:
            correct_answer = f"{ans_coeff_x}x+{ans_const}"
        elif ans_const < 0:
            correct_answer = f"{ans_coeff_x}x-{abs(ans_const)}"
        else:
            correct_answer = f"{ans_coeff_x}x"
            
    else: # level 2, 暫時與 level 1 相同，未來可擴充為因式分解等
        # 為了變化性，這裡可以設計需要因式分解的題目
        a = random.randint(1, 5)
        b = random.randint(1, 5)
        c = random.randint(1, 5)
        while a == c: c = random.randint(1, 5)
        
        question_text = f"請化簡下列式子：({a}(x+{b})) / ({c}(x+{b}))"
        correct_answer = f"{a}/{c}"

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user_answer = user_answer.replace(" ", "").lower()
    return check_answer(user_answer, correct_answer)