# \圓錐曲線\拋物線切線
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「拋物線切線」的題目。
    """
    c = random.randint(1, 3)
    # y²=4cx, 在 (x₀,y₀) 的切線為 y₀y = 2c(x+x₀)
    x0 = c * random.randint(1, 3)**2 # 讓 y₀ 是整數
    y0 = (4*c*x0)**0.5
    
    question_text = f"請求出拋物線 y² = {4*c}x 在點 ({int(x0)}, {int(y0)}) 的切線方程式。(一般式 ax+by+c=0)"
    # y₀y = 2cx + 2cx₀ => 2cx - y₀y + 2cx₀ = 0
    correct_answer = f"{2*c}x - {int(y0)}y + {int(2*c*x0)} = 0".replace("+-","-")
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user_answer = user_answer.replace(" ", "").lower()
    return check_answer(user_answer, correct_answer)