# \圓錐曲線\橢圓平移
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「橢圓平移」的題目。
    """
    a, b = 5, 4
    h = random.randint(-5, 5)
    k = random.randint(-5, 5)
    
    if level == 1:
        question_text = f"橢圓 ((x-{h})²)/{a*a} + ((y-{k})²)/{b*b} = 1 的中心坐標為何？"
        correct_answer = f"({h},{k})"
    else: # level 2
        c = 3 # a²=b²+c² => 25=16+9
        question_text = f"一個中心在 ({h},{k})、焦點在 ({h+c},{k}) 和 ({h-c},{k})、長軸長為 {2*a} 的橢圓，其方程式為何？"
        correct_answer = f"((x-{h})²)/{a*a}+((y-{k})²)/{b*b}=1"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user_answer = user_answer.replace(" ", "").replace("^2", "²")
    return check_answer(user_answer, correct_answer)