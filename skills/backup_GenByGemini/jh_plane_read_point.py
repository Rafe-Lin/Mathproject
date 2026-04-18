# skills/jh_plane_read_point.py
import random

def generate(level=1):
    """
    生成一道「讀取坐標平面上的點」的題目。
    此為圖形題，需要AI輔助。
    """
    x = random.randint(-5, 5)
    y = random.randint(-5, 5)

    question_text = (
        f"這是一個需要老師出題的互動題：\n\n"
        f"1. 請老師在下方的「數位計算紙」上畫出一個直角坐標平面。\n"
        f"2. 請老師在平面上標示一個點 P。\n"
        f"3. 請學生寫出 P 點的坐標。\n\n"
        f"學生寫完答案後，請點擊「AI 檢查」按鈕，AI會判斷您畫的點和學生的答案是否一致。"
    )

    # 這種互動題沒有固定答案
    correct_answer = None
    
    context_string = f"學習觀察直角坐標平面上的點，並正確讀出其 (x, y) 坐標。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "graph", # 答案類型為圖形，由AI批改
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    return {
        "correct": False, 
        "result": "這是一道互動題，請在數位計算紙上完成作答後，點選「AI 檢查」。",
        "next_question": False
    }