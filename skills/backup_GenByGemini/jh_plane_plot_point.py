# skills/jh_plane_plot_point.py
import random

def generate(level=1):
    """
    生成一道「直角坐標平面上描點」的題目。
    此為圖形題。
    """
    x = random.randint(-5, 5)
    y = random.randint(-5, 5)

    question_text = (
        f"請在下方的「數位計算紙」上，畫出直角坐標平面，並標示出點 P({x}, {y}) 的位置。\n\n"
        "完成後，請點擊「AI 檢查」按鈕。"
    )

    # 圖形題的答案設為 None，由 AI 進行批改
    correct_answer = None
    
    context_string = f"學習在直角坐標平面上，根據坐標 (x, y) 找到對應的點。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "graph",
        "context_string": context_string,
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