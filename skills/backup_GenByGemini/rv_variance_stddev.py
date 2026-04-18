# \機率統計\隨機變數變異數與標準差
import random
import math
from .utils import check_answer

def generate(level=1):
    """
    生成一道「隨機變數變異數與標準差」的題目。
    """
    x_vals = [1, 2, 3]
    p_vals = [0.3, 0.4, 0.3]
    
    ev = sum(x * p for x, p in zip(x_vals, p_vals))
    var = sum(((x - ev)**2) * p for x, p in zip(x_vals, p_vals))
    
    if level == 1:
        question_text = f"已知隨機變數 X 的機率分布如下：\nX | 1 | 2 | 3\nP(X) | 0.3 | 0.4 | 0.3\n請問 X 的變異數 Var(X) 是多少？"
        correct_answer = str(round(var, 2))
    else: # level 2
        question_text = f"已知隨機變數 X 的機率分布如下：\nX | 1 | 2 | 3\nP(X) | 0.3 | 0.4 | 0.3\n請問 X 的標準差 σ(X) 是多少？ (四捨五入至小數點後兩位)"
        correct_answer = str(round(math.sqrt(var), 2))
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    # 使用通用的數字檢查，它內部處理了浮點數比較
    return check_answer(user_answer, correct_answer, check_type='numeric')