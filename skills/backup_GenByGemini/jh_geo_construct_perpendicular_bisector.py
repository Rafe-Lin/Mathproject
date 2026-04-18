# skills/jh_geo_construct_perpendicular_bisector.py
import random

def generate(level=1):
    """
    生成一道「中垂線作圖」的題目。
    此為圖形題。
    """
    question_text = (
        "請利用尺規作圖，畫出線段 AB 的垂直平分線（中垂線）。\n\n"
        "1. 請先在「數位計算紙」上畫一條線段 AB。\n"
        "2. 分別以 A、B 為圓心，大於 AB 線段一半長為半徑畫弧，兩弧交於兩點。\n"
        "3. 連接此兩點即為 AB 的中垂線。\n\n"
        "完成後，請點擊「AI 檢查」按鈕。"
    )

    return {
        "question_text": question_text,
        "answer": None,
        "correct_answer": "graph",
        "context_string": "學習使用尺規作圖，畫出一條線段的垂直平分線。",
    }

def check(user_answer, correct_answer):
    return {
        "correct": False, 
        "result": "請在數位計算紙上畫出您的解題過程，然後點選「AI 檢查」。",
        "next_question": False
    }