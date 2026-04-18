# skills/jh_circle_chord_property.py
import random

def generate(level=1):
    """
    生成一道「弦心距性質」的題目。
    此為概念/圖形題。
    """
    question_text = (
        "請說明圓的「弦心距性質」是什麼？\n\n"
        "請在下方的「數位計算紙」上，畫出一個圓，圓心為 O，並畫一條弦 AB。\n"
        "從圓心 O 作一條垂直於弦 AB 的線段 OM，其中 M 為垂足。\n"
        "根據弦心距性質，線段 AM 和 BM 有什麼關係？\n\n"
        "完成後，請點擊「AI 檢查」按鈕。"
    )

    return {
        "question_text": question_text,
        "answer": None,
        "correct_answer": "graph",
        "context_string": "學習弦心距的性質：弦心距垂直平分其所對應的弦。",
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