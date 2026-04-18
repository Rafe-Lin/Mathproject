# skills/jh_geo_3d_plane_def.py
import random

def generate(level=1):
    """
    生成一道「空間中的平面」的題目。
    此為概念題。
    """
    question_text = (
        "在幾何學中，我們如何決定一個「唯一」的平面？\n\n"
        "請至少寫出或畫出兩種可以決定一個唯一平面的條件。\n"
        "（例如：不共線的三點...）\n\n"
        "請在下方的「數位計算紙」上寫下或畫出你的答案。\n\n"
        "完成後，請點擊「AI 檢查」按鈕。"
    )

    return {
        "question_text": question_text,
        "answer": None,
        "correct_answer": "graph",
        "context_string": "學習決定一個唯一平面的條件，例如：不共線的三點、一直線及線外一點、兩相交直線、兩平行直線。",
    }

def check(user_answer, correct_answer):
    return {
        "correct": False, 
        "result": "這是一道觀念題，請在數位計算紙上作答後，點選「AI 檢查」。",
        "next_question": False
    }