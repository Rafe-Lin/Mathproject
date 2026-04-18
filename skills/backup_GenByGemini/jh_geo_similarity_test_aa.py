# skills/jh_geo_similarity_test_aa.py
import random

def generate(level=1):
    """
    生成一道「AA 相似性質」的題目。
    此為概念/圖形題。
    """
    question_text = (
        "請說明什麼是三角形的「AA 相似性質」？\n\n"
        "請在下方的「數位計算紙」上，畫出兩個利用 AA 性質可以證明為相似的三角形 △ABC 和 △DEF。\n"
        "請標示出兩組對應相等的角。\n\n"
        "完成後，請點擊「AI 檢查」按鈕。"
    )

    return {
        "question_text": question_text,
        "answer": None,
        "correct_answer": "graph",
        "context_string": "學習 AA (Angle-Angle) 相似性質：若一個三角形的兩個角與另一個三角形的兩個角對應相等，則這兩個三角形相似。",
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