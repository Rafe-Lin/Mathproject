# skills/jh_graph_2var_plot_line.py
import random

def generate(level=1):
    """
    生成一道「二元一次方程式圖形繪製」的題目。
    此為圖形題。
    """
    a = random.randint(1, 3)
    b = random.randint(1, 3)
    c = random.randint(-5, 5)
    
    equation_str = f"{a}x + {b}y = {c}"

    question_text = (
        f"請在下方的「數位計算紙」上，畫出二元一次方程式 {equation_str} 的圖形。\n\n"
        f"提示：可以先找出圖形通過的兩個點，再將兩點連成直線。\n\n"
        "完成後，請點擊「AI 檢查」按鈕。"
    )

    return {
        "question_text": question_text,
        "answer": None,
        "correct_answer": "graph",
        "context_string": f"學習如何在直角坐標平面上畫出二元一次方程式 {equation_str} 的圖形。",
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