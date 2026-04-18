# \三角函數\三角圖形 (振幅伸縮)
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「三角圖形 (振幅伸縮)」的題目。
    """
    a = random.randint(2, 10)
    func = random.choice(['sin', 'cos'])
    
    if level == 1:
        question_text = f"請問函數 y = {a}{func}(x) 的振幅是多少？"
        correct_answer = str(a)
    else: # level 2, 逆向提問或求極值
        q_type = random.choice(['max_val', 'min_val'])
        if q_type == 'max_val':
            question_text = f"請問函數 y = -{a}{func}(x) 的最大值是多少？"
            correct_answer = str(a)
        else: # min_val
            question_text = f"請問函數 y = {a}{func}(x) + 3 的最小值是多少？"
            correct_answer = str(-a + 3)
            
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    return check_answer(user_answer, correct_answer, check_type='numeric')