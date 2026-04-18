# skills/jh_geo_triangle_centroid_def_property.py
import random

def generate(level=1):
    """
    生成一道「三角形的重心定義與性質」的題目。
    此為概念/圖形題。
    """
    question_text = (
        "請說明什麼是三角形的「重心」？\n\n"
        "請在下方的「數位計算紙」上，畫出一個三角形 ABC，並畫出它的三條中線（頂點到對邊中點的連線），標示出重心 G。\n"
        "根據重心的性質，重心到頂點的距離，與重心到對邊中點的距離，兩者之間的比值是多少？\n\n"
        "完成後，請點擊「AI 檢查」按鈕。"
    )

    return {
        "question_text": question_text,
        "answer": None,
        "correct_answer": "graph",
        "context_string": "學習三角形的重心：三條中線的交點。重心到頂點的距離是該中線長的 2/3，重心到對邊中點的距離是該中線長的 1/3 (即 2:1)。",
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