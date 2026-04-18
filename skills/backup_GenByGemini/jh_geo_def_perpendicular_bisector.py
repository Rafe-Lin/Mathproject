# skills/jh_geo_def_perpendicular_bisector.py
import random

def generate(level=1):
    """
    生成一道「中垂線定義」的題目。
    此為概念題/圖形題。
    """
    question_text = (
        "請說明什麼是線段的中垂線（或稱垂直平分線）？\n\n"
        "請在下方的「數位計算紙」上，畫出一條線段 AB，並利用尺規作圖畫出它的中垂線 L。\n\n"
        "完成後，請點擊「AI 檢查」按鈕。"
    )

    return {
        "question_text": question_text,
        "answer": None,
        "correct_answer": "graph",
        "context_string": "學習中垂線的定義與尺規作圖方法。",
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