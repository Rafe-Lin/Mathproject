# skills/jh_geo_parallel_lines_def.py
import random

def generate(level=1):
    """
    生成一道「平行線定義」的題目。
    此為概念題。
    """
    question_text = (
        "請說明在同一個平面上，「兩條直線互相平行」的定義是什麼？\n\n"
        "請在下方的「數位計算紙」上畫出兩條平行線 L1 和 L2，並用符號表示 L1 平行於 L2。\n\n"
        "完成後，請點擊「AI 檢查」按鈕。"
    )

    return {
        "question_text": question_text,
        "answer": None,
        "correct_answer": "graph",
        "context_string": "學習平行線的定義：同一平面上，永不相交的兩條直線。",
    }

def check(user_answer, correct_answer):
    """
    圖形題的 check 函數通常只返回提示，實際批改由前端 AI 完成。
    """
    return {
        "correct": False, 
        "result": "請在數位計算紙上畫圖並寫下你的解釋，然後點選「AI 檢查」。",
        "next_question": False
    }