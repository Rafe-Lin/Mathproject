# skills/jh_graph_system_solution.py
import random

def generate(level=1):
    """
    生成一道「二元一次聯立方程式的圖形解」的題目。
    此為圖形題。
    """
    # 構造有整數解的聯立方程式
    x = random.randint(-3, 3)
    y = random.randint(-3, 3)

    a1, b1 = random.randint(1, 2), random.randint(1, 2)
    c1 = a1 * x + b1 * y

    a2, b2 = random.randint(1, 2), random.randint(1, 2)
    while a1 * b2 == a2 * b1: # 避免重合或平行
        a2, b2 = random.randint(1, 2), random.randint(1, 2)
    c2 = a2 * x + b2 * y

    eq1_str = f"{a1}x + {b1}y = {c1}"
    eq2_str = f"{a2}x + {b2}y = {c2}"

    question_text = (
        f"請在下方的「數位計算紙」上，畫出聯立方程式\n(1) {eq1_str}\n(2) {eq2_str}\n的圖形，並標示出其交點坐標。\n\n"
        "完成後，請點擊「AI 檢查」按鈕。"
    )

    return {
        "question_text": question_text,
        "answer": None,
        "correct_answer": "graph",
        "context_string": f"學習聯立方程式的解即為其圖形在坐標平面上的交點。",
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