# skills/jh_geo_def_point_line_angle.py
import random

def generate(level=1):
    """
    生成一道「點、線、角定義」的題目。
    此為概念題。
    """
    concepts = [
        ("點、直線、線段、射線有什麼不同？請試著畫圖並說明。", "點是位置，沒有大小。直線無限延伸。線段有兩個端點。射線有一個端點，另一端無限延伸。"),
        ("什麼是「角」？請畫一個角，並標示出角的頂點和邊。", "由一個頂點和兩條射線（邊）組成的圖形。"),
        ("銳角、直角、鈍角、平角、周角有什麼區別？請各畫一個例子。", "銳角<90度，直角=90度，鈍角>90度，平角=180度，周角=360度。")
    ]
    
    question, _ = random.choice(concepts)

    question_text = (
        f"請回答以下幾何基本概念問題：\n\n"
        f"{question}\n\n"
        "請在下方的「數位計算紙」上畫圖並寫下你的解釋。\n\n"
        "完成後，請點擊「AI 檢查」按鈕。"
    )

    return {
        "question_text": question_text,
        "answer": None,
        "correct_answer": "graph",
        "context_string": "學習幾何中的基本元素：點、線、角的定義與區別。",
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