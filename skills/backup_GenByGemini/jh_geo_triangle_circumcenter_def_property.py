# skills/jh_geo_triangle_circumcenter_def_property.py
import random

def generate(level=1):
    """
    生成一道「三角形的外心定義與性質」的題目。
    此為概念/圖形題。
    """
    question_text = (
        "請說明什麼是三角形的「外心」？\n\n"
        "請在下方的「數位計算紙」上，畫出一個三角形 ABC，並畫出它的外心 O。\n"
        "根據外心的性質，外心到三個頂點的距離有什麼關係？為什麼？\n\n"
        "完成後，請點擊「AI 檢查」按鈕。"
    )

    return {
        "question_text": question_text,
        "answer": None,
        "correct_answer": "graph",
        "context_string": "學習三角形的外心：三邊的垂直平分線（中垂線）的交點。外心是三角形外接圓的圓心，所以到三頂點等距離。",
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