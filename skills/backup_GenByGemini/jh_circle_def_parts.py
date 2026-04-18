# skills/jh_circle_def_parts.py
import random

def generate(level=1):
    """
    生成一道「圓的各部分名稱」的題目。
    此為概念/圖形題。
    """
    question_text = (
        "請在下方的「數位計算紙」上，畫出一個圓，並在圓上標示出以下各部分：\n\n"
        "1. 圓心 (O)\n"
        "2. 半徑 (r)\n"
        "3. 直徑 (d)\n"
        "4. 弦\n"
        "5. 弧\n\n"
        "完成後，請點擊「AI 檢查」按鈕。"
    )

    return {
        "question_text": question_text,
        "answer": None,
        "correct_answer": "graph",
        "context_string": "學習辨識圓的各個基本組成部分。",
    }

def check(user_answer, correct_answer):
    return {
        "correct": False, 
        "result": "請在數位計算紙上畫圖並標示，然後點選「AI 檢查」。",
        "next_question": False
    }