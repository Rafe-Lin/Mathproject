# \圓錐曲線\雙曲線平移
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「雙曲線平移」的題目。
    """
    a, b = 4, 3
    h = random.randint(-5, 5)
    k = random.randint(-5, 5)
    
    if level == 1:
        question_text = f"雙曲線 ((x-{h})²)/{a*a} - ((y-{k})²)/{b*b} = 1 的中心坐標為何？"
        correct_answer = f"({h},{k})"
    else: # level 2
        c = 5 # c²=a²+b² => 25=16+9
        question_text = f"一個中心在 ({h},{k})、焦點在 ({h+c},{k}) 和 ({h-c},{k})、貫軸長為 {2*a} 的雙曲線，其方程式為何？"
        correct_answer = f"((x-{h})²)/{a*a}-((y-{k})²)/{b*b}=1"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user_answer = user_answer.replace(" ", "").replace("^2", "²")
    return check_answer(user_answer, correct_answer)