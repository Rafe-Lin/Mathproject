# skills/jh_geo_angle_bisector_property.py
import random

def generate(level=1):
    """
    生成一道「角平分線性質」的題目。
    此為概念/圖形題。
    """
    question_text = (
        "請說明「角平分線的性質」是什麼？\n\n"
        "請在下方的「數位計算紙」上，畫出一個角 ∠ABC，並畫出其角平分線 BP。\n"
        "在 BP 上任取一點 Q，並從 Q 點向兩邊 BA、BC 作垂直線段 QD、QE。\n"
        "根據角平分線性質，線段 QD 和 QE 的長度有什麼關係？\n\n"
        "完成後，請點擊「AI 檢查」按鈕。"
    )

    return {
        "question_text": question_text,
        "answer": None,
        "correct_answer": "graph",
        "context_string": "學習角平分線的性質：角平分線上的任意一點，到角兩邊的距離相等。",
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