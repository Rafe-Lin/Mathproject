# skills/jh_circle_equal_chords_property.py
import random

def generate(level=1):
    """
    生成一道「等弦對等弦心距」的題目。
    此為概念/圖形題。
    """
    question_text = (
        "請說明圓的「等弦對等弦心距」性質是什麼？反之，「等弦心距對等弦」又如何？\n\n"
        "請在下方的「數位計算紙」上，畫出一個圓，並畫出兩條等長的弦 AB 和 CD。\n"
        "標示出它們的弦心距 OM 和 ON。\n"
        "根據性質，OM 和 ON 的長度有什麼關係？\n\n"
        "完成後，請點擊「AI 檢查」按鈕。"
    )

    return {
        "question_text": question_text,
        "answer": None,
        "correct_answer": "graph",
        "context_string": "學習圓的性質：在同圓或等圓中，等弦對等弦心距，等弦心距對等弦。",
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