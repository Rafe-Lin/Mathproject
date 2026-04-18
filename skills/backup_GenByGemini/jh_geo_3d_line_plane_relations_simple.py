# skills/jh_geo_3d_line_plane_relations_simple.py
import random

def generate(level=1):
    """
    生成一道「空間中直線與平面的關係」的題目。
    此為概念題。
    """
    question_text = (
        "在空間中，一條直線 L 和一個平面 E 有哪三種可能的相交關係？\n\n"
        "請在下方的「數位計算紙」上，分別畫出這三種關係的示意圖，並寫下它們的名稱（例如：交於一點、...）。\n\n"
        "完成後，請點擊「AI 檢查」按鈕。"
    )

    return {
        "question_text": question_text,
        "answer": None,
        "correct_answer": "graph",
        "context_string": "學習空間中直線與平面的三種關係：直線在平面上、直線與平面平行、直線與平面交於一點。",
    }

def check(user_answer, correct_answer):
    """
    圖形題的 check 函數通常只返回提示，實際批改由前端 AI 完成。
    """
    return {
        "correct": False, 
        "result": "這是一道觀念題，請在數位計算紙上作答後，點選「AI 檢查」。",
        "next_question": False
    }