# skills/jh_geo_construct_perpendicular_point_on_line.py
import random

def generate(level=1):
    """
    生成一道「過線上一點作垂線」的題目。
    此為圖形題。
    """
    question_text = (
        "請利用尺規作圖，畫一條直線 L，並在 L 上取一點 P。\n"
        "通過 P 點作一條直線 M，使得 M 與 L 垂直。\n\n"
        "請在下方的「數位計算紙」上展示你的作圖過程，並保留作圖痕跡。\n\n"
        "完成後，請點擊「AI 檢查」按鈕。"
    )

    return {
        "question_text": question_text,
        "answer": None,
        "correct_answer": "graph",
        "context_string": "學習使用尺規作圖，過線上一點作已知直線的垂線。",
    }

def check(user_answer, correct_answer):
    return {
        "correct": False, 
        "result": "請在數位計算紙上畫出您的解題過程，然後點選「AI 檢查」。",
        "next_question": False
    }