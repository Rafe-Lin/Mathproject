# \三角函數\三角圖形 (水平平移)
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「三角圖形 (水平平移)」的題目。
    """
    h_val = random.choice(["π/4", "π/3", "π/2", "π"])
    h_deg = {"π/4": 45, "π/3": 60, "π/2": 90, "π": 180}[h_val]
    direction = random.choice(['向左', '向右'])
    
    if level == 1:
        sign = "-" if direction == '向右' else "+"
        question_text = f"函數 y = sin(x {sign} {h_val}) 的圖形，是由 y = sin(x) 的圖形如何平移得到？\n\n" \
                        f"A) {direction}平移 {h_val} 單位\n" \
                        f"B) 向上平移 {h_val} 單位\n" \
                        f"C) 週期變為 {h_val}"
        correct_answer = "A"
    else: # level 2, 逆向提問
        question_text = f"若要將 y = cos(x) 的圖形{direction}平移 {h_val} 單位，其新的函數方程式為何？"
        sign = "-" if direction == '向右' else "+"
        correct_answer = f"y=cos(x{sign}{h_val})"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user_answer = user_answer.replace(" ", "").replace("pi", "π").lower()
    return check_answer(user_answer, correct_answer, check_type='case_insensitive')