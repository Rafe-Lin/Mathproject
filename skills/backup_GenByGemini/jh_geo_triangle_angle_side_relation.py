# skills/jh_geo_triangle_angle_side_relation.py
import random

def generate(level=1):
    """
    生成一道「三角形邊角關係」的題目。
    此為概念題。
    """
    question_text = (
        "請說明三角形的「大角對大邊，小角對小邊」關係是什麼？\n\n"
        "請在下方的「數位計算紙」上，畫出一個不等邊三角形 ABC，標示出三個角和三個邊。\n"
        "假設 ∠A > ∠B > ∠C，請根據邊角關係，寫出其對應邊 a, b, c 的大小關係。\n\n"
        "完成後，請點擊「AI 檢查」按鈕。"
    )

    return {
        "question_text": question_text,
        "answer": None,
        "correct_answer": "graph",
        "context_string": "學習三角形的邊角關係：在同一個三角形中，較大的角對應較長的邊，較小的角對應較短的邊。",
    }

def check(user_answer, correct_answer):
    """
    圖形題的 check 函數通常只返回提示，實際批改由前端 AI 完成。
    """
    return {
        "correct": False, 
        "result": "請在數位計算紙上畫圖並寫下你的結論，然後點選「AI 檢查」。",
        "next_question": False
    }