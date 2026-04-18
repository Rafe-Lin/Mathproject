# skills/jh_circle_inscribed_angle_diameter.py
import random

def generate(level=1):
    """
    生成一道「圓內接三角形(直徑對圓周角)」的題目。
    此為概念題。
    """
    question_text = (
        "請說明「直徑所對的圓周角」有什麼特性？\n\n"
        "請在下方的「數位計算紙」上，畫出一個圓和它的一條直徑 AB。\n"
        "在圓周上任取一點 C (不是 A 或 B)，並連接 AC 和 BC。\n"
        "請問 ∠ACB 是多少度？為什麼？\n\n"
        "完成後，請點擊「AI 檢查」按鈕。"
    )

    return {
        "question_text": question_text,
        "answer": None,
        "correct_answer": "graph",
        "context_string": "學習圓的性質：直徑所對的圓周角是直角 (90°)。",
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