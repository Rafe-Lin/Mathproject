# skills/jh_geo_construct_line_segment.py
import random

def generate(level=1):
    """
    生成一道「作一線段等於已知線段」的題目。
    此為圖形題。
    """
    question_text = (
        "請利用尺規作圖，作出一條線段，使其長度等於一條已知的線段 AB。\n\n"
        "1. 請先在「數位計算紙」上畫一條線段 AB。\n"
        "2. 再畫一條射線，並在射線上作出等於 AB 長的線段 CD。\n\n"
        "完成後，請點擊「AI 檢查」按鈕。"
    )

    return {
        "question_text": question_text,
        "answer": None,
        "correct_answer": "graph",
        "context_string": "學習使用尺規作圖，複製一條已知長度的線段。",
    }

def check(user_answer, correct_answer):
    return {
        "correct": False, 
        "result": "請在數位計算紙上畫出您的解題過程，然後點選「AI 檢查」。",
        "next_question": False
    }