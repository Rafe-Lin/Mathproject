# skills/jh_geo_congruence_def.py
import random

def generate(level=1):
    """
    生成一道「全等圖形定義」的題目。
    此為概念/圖形題。
    """
    question_text = (
        "請說明什麼是「全等圖形」？\n\n"
        "請在下方的「數位計算紙」上，畫出兩個形狀與大小完全相同的圖形（例如兩個全等的三角形或五邊形）。\n"
        "並標示出它們的對應頂點、對應邊、對應角。\n\n"
        "完成後，請點擊「AI 檢查」按鈕。"
    )

    return {
        "question_text": question_text,
        "answer": None,
        "correct_answer": "graph",
        "context_string": "學習全等圖形的定義：經過平移、旋轉、翻轉後，能夠完全疊合的兩個圖形。",
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