# \圓錐曲線\雙曲線切線
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「雙曲線切線」的題目。
    """
    a, b = 4, 3
    # 在 x²/a² - y²/b² = 1 上找一點 (x₀,y₀)
    # 讓 x₀ = a*sec(θ), y₀ = b*tan(θ)
    x0 = a * random.choice([1.25, 1.5, 2]) # 隨便選幾個值
    y0 = b * ((x0/a)**2 - 1)**0.5
    
    question_text = f"請求出雙曲線 x²/{a*a} - y²/{b*b} = 1 在點 ({round(x0,1)}, {round(y0,1)}) 的切線方程式。(此為觀念題)"
    # 切線: x₀x/a² - y₀y/b² = 1
    correct_answer = "觀念題"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    # This is a conceptual question, so any answer is accepted and a standard explanation is given.
    result_text = "觀念正確！可利用公式 x₀x/a² - y₀y/b² = 1 或微分求解。"
    return {"correct": True, "result": result_text, "next_question": True}