# skills/jh_geo_construct_angle.py
import random

def generate(level=1):
    """
    生成一道「作一個角等於已知角」的題目。
    此為圖形題。
    """
    angle = random.choice([30, 45, 60, 120])
    question_text = (
        f"請利用尺規作圖，作出一個等於 {angle}° 的角。\n\n"
        "提示：你可以先畫一個基準角，再利用複製角的方式作圖。\n\n"
        "請在下方的「數位計算紙」上展示你的作圖過程。\n\n"
        "完成後，請點擊「AI 檢查」按鈕。"
    )

    return {
        "question_text": question_text,
        "answer": None,
        "correct_answer": "graph",
        "context_string": "學習使用尺規作圖，複製一個已知角。",
    }

def check(user_answer, correct_answer):
    return {
        "correct": False, 
        "result": "請在數位計算紙上畫出您的解題過程，然後點選「AI 檢查」。",
        "next_question": False
    }