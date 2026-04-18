# skills/jh_geo_3d_skew_lines_def.py
import random

def generate(level=1):
    """
    生成一道「歪斜線定義」的題目。
    此為概念/圖形題。
    """
    question_text = (
        "在空間中，兩條直線除了平行和相交之外，還有第三種關係。\n\n"
        "請說明什麼是「歪斜線」？\n\n"
        "請在下方的「數位計算紙」上，畫一個長方體，並標示出一對互為歪斜線的邊。\n\n"
        "完成後，請點擊「AI 檢查」按鈕。"
    )

    return {
        "question_text": question_text,
        "answer": None,
        "correct_answer": "graph",
        "context_string": "學習歪斜線的定義：在空間中，兩條直線既不平行也不相交。",
    }

def check(user_answer, correct_answer):
    return {
        "correct": False, 
        "result": "這是一道觀念題，請在數位計算紙上作答後，點選「AI 檢查」。",
        "next_question": False
    }