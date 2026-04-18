# skills/jh_graph_horizontal_line.py
import random

def generate(level=1):
    """
    生成一道「水平線圖形」的題目。
    此為圖形題。
    """
    y_val = random.randint(-5, 5)
    
    equation_str = f"y = {y_val}"

    question_text = (
        f"請在下方的「數位計算紙」上，畫出方程式 {equation_str} 的圖形。\n\n"
        f"提示：這是一條通過 y 坐標為 {y_val} 的所有點的直線。\n\n"
        "完成後，請點擊「AI 檢查」按鈕。"
    )

    return {
        "question_text": question_text,
        "answer": None,
        "correct_answer": "graph",
        "context_string": f"學習如何在直角坐標平面上畫出水平線 {equation_str} 的圖形。",
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