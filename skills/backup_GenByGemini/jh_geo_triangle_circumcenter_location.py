# skills/jh_geo_triangle_circumcenter_location.py
import random

def generate(level=1):
    """
    生成一道「三角形外心的位置」的題目。
    此為概念/圖形題。
    """
    question_text = (
        "三角形的外心位置會因為三角形的種類而不同。\n\n"
        "請在下方的「數位計算紙」上，分別畫出「銳角三角形」、「直角三角形」、「鈍角三角形」以及它們各自的外心位置。\n"
        "並說明外心分別在三角形的內部、邊上、還是外部？\n\n"
        "完成後，請點擊「AI 檢查」按鈕。"
    )

    return {
        "question_text": question_text,
        "answer": None,
        "correct_answer": "graph",
        "context_string": "學習外心位置的判斷：銳角三角形外心在內部；直角三角形外心在斜邊中點；鈍角三角形外心在外部。",
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