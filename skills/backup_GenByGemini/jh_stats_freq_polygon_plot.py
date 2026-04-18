# skills/jh_stats_freq_polygon_plot.py
import random

def generate(level=1):
    """
    生成一道「繪製次數分配折線圖」的題目。
    此為圖形題。
    """
    question_text = (
        "假設某班級學生的體重次數分配表如下：\n"
        "40~45公斤: 3人\n"
        "45~50公斤: 8人\n"
        "50~55公斤: 12人\n"
        "55~60公斤: 5人\n"
        "60~65公斤: 2人\n\n"
        "請在下方的「數位計算紙」上，畫出對應的次數分配折線圖。\n\n"
        "完成後，請點擊「AI 檢查」按鈕。"
    )

    return {
        "question_text": question_text,
        "answer": None,
        "correct_answer": "graph",
        "context_string": "學習根據次數分配表，以組中點為 x 坐標，次數為 y 坐標，描點並連接成折線圖。",
    }

def check(user_answer, correct_answer):
    return {
        "correct": False, 
        "result": "請在數位計算紙上畫出您的解題過程，然後點選「AI 檢查」。",
        "next_question": False
    }