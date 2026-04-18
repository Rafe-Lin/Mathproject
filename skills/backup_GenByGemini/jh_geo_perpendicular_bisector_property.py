# skills/jh_geo_perpendicular_bisector_property.py
import random

def generate(level=1):
    """
    生成一道「中垂線性質」的題目。
    此為概念/圖形題。
    """
    question_text = (
        "請說明「中垂線（垂直平分線）的性質」是什麼？\n\n"
        "請在下方的「數位計算紙」上，畫出一條線段 AB 及其垂直平分線 L。\n"
        "在 L 上任取一點 P，並連接 PA 和 PB。\n"
        "根據中垂線性質，線段 PA 和 PB 的長度有什麼關係？\n\n"
        "完成後，請點擊「AI 檢查」按鈕。"
    )

    return {
        "question_text": question_text,
        "answer": None,
        "correct_answer": "graph",
        "context_string": "學習中垂線的性質：中垂線上的任意一點，到線段兩端點的距離相等。",
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