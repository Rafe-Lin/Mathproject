# skills/jh_graph_vertical_line.py
import random

def generate(level=1):
    """
    生成一道「鉛垂線圖形」的題目。
    此為圖形題。
    """
    x_val = random.randint(-5, 5)
    
    equation_str = f"x = {x_val}"

    question_text = (
        f"請在下方的「數位計算紙」上，畫出方程式 {equation_str} 的圖形。\n\n"
        f"提示：這是一條通過 x 坐標為 {x_val} 的所有點的直線。\n\n"
        "完成後，請點擊「AI 檢查」按鈕。"
    )

    return {
        "question_text": question_text,
        "answer": None,
        "correct_answer": "graph",
        "context_string": f"學習如何在直角坐標平面上畫出鉛垂線 {equation_str} 的圖形。",
    }

def check(user_answer, correct_answer):
    """
    圖形題的 check 函數通常只返回提示，實際批改由前端 AI 完成。
    """
    return {
        "correct": False, 
        "result": "請在數位計算紙上畫出您的解題過程，然後點選「AI 檢查」。",
        "next_question": False
    }