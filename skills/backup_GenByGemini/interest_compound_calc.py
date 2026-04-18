# \數列與級數\複利計算
import random
import math
from .utils import check_answer

def generate(level=1):
    """
    生成一道「複利計算」的題目。
    """
    pv = random.randint(100, 500) * 100  # 本金
    r_percent = random.randint(1, 10)  # 年利率 %
    r = r_percent / 100
    n = random.randint(2, 5)  # 期數

    if level == 1:
        # 正向計算：給定本金、利率、期數，求本利和
        question_text = f"小明將 {pv} 元存入銀行，年利率為 {r_percent}%，以年複利計算。請問 {n} 年後，他的帳戶本利和會是多少元？ (四捨五入至整數位)"
        fv = pv * ((1 + r) ** n)
        correct_answer = str(round(fv))
    else: # level 2, 逆向提問
        # 變化題型：給定本金、目標金額，求所需年數
        fv = round(pv * ((1 + r) ** n))
        question_text = f"小明將 {pv} 元存入銀行，年利率為 {r_percent}%，年複利計算。請問至少需要多少年，帳戶本利和才會超過 {fv} 元？ (取整數年)"
        # fv = pv * (1+r)^n  =>  n = log(fv/pv) / log(1+r)
        # 這裡我們直接使用預設的 n 值作為答案，因為題目是「至少需要多少年」
        correct_answer = str(n)

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    return check_answer(user_answer, correct_answer, check_type='numeric')