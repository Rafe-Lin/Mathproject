# \三角函數\三角圖形 (鉛直平移)
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「三角圖形 (鉛直平移)」的題目。
    """
    k = random.randint(1, 5)
    direction = random.choice(['向上', '向下'])
    
    if level == 1:
        sign = "+" if direction == '向上' else "-"
        question_text = f"函數 y = sin(x) {sign} {k} 的圖形，是由 y = sin(x) 的圖形如何平移得到？\n\n" \
                        f"A) {direction}平移 {k} 單位\n" \
                        f"B) 向右平移 {k} 單位\n" \
                        f"C) 振幅變為 {k}"
        correct_answer = "A"
    else: # level 2, 逆向提問
        question_text = f"若要將 y = cos(x) 的圖形{direction}平移 {k} 單位，其新的函數方程式為何？"
        sign = "+" if direction == '向上' else "-"
        correct_answer = f"y=cos(x){sign}{k}"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user_answer = user_answer.replace(" ", "").lower()
    return check_answer(user_answer, correct_answer, check_type='case_insensitive')