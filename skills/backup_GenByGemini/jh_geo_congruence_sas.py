# skills/jh_geo_congruence_sas.py
import random

def generate(level=1):
    """
    生成一道「SAS 全等性質」的題目。
    此為概念/圖形題。
    """
    question_text = (
        "請說明什麼是三角形的「SAS 全等性質」？\n\n"
        "請在下方的「數位計算紙」上，畫出兩個利用 SAS 性質可以證明為全等的三角形 △ABC 和 △DEF。\n"
        "請標示出對應相等的「邊、夾角、邊」。\n\n"
        "完成後，請點擊「AI 檢查」按鈕。"
    )

    return {
        "question_text": question_text,
        "answer": None,
        "correct_answer": "graph",
        "context_string": "學習 SAS (Side-Angle-Side) 全等性質：若兩三角形的兩邊及其夾角對應相等，則兩三角形全等。",
    }

def check(user_answer, correct_answer):
    """
    圖形題的 check 函數通常只返回提示，實際批改由前端 AI 完成。
    """
    return {
        "correct": False, 
        "result": "請在數位計算紙上畫圖並標示，然後點選「AI 檢查」。",
        "next_question": False
    }