# skills/jh_geo_def_polygon.py
import random

def generate(level=1):
    """
    生成一道「多邊形定義」的題目。
    此為概念題。
    """
    polygons = ["三角形", "四邊形", "五邊形", "六邊形"]
    polygon = random.choice(polygons)

    question_text = (
        f"請回答以下問題：\n\n"
        f"1. 什麼是多邊形？\n"
        f"2. 請畫出一個「{polygon}」。\n"
        f"3. 什麼是「正{polygon}」？它和一般的{polygon}有什麼不同？\n\n"
        "請在下方的「數位計算紙」上畫圖並寫下你的解釋。\n\n"
        "完成後，請點擊「AI 檢查」按鈕。"
    )

    return {
        "question_text": question_text,
        "answer": None,
        "correct_answer": "graph",
        "context_string": "學習多邊形、正多邊形的定義與特性。",
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