# skills/jh_circle_tangent_property.py
import random

def generate(level=1):
    """
    生成一道「切線性質」的題目。
    此為概念/圖形題。
    """
    question_text = (
        "請說明圓的「切線性質」是什麼？\n\n"
        "請在下方的「數位計算紙」上，畫出一個圓，圓心為 O，並畫一條切線 L，切點為 P。\n"
        "連接圓心 O 和切點 P，得到半徑 OP。\n"
        "根據切線性質，半徑 OP 和切線 L 有什麼關係？\n\n"
        "完成後，請點擊「AI 檢查」按鈕。"
    )

    return {
        "question_text": question_text,
        "answer": None,
        "correct_answer": "graph",
        "context_string": "學習切線的性質：過切點的半徑必垂直於此切線。",
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