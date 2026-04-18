# \三角函數\sin函數圖形
import random

def generate(level=1):
    """
    生成一道「sin函數圖形」的觀念題。
    """
    question_text = (
        "請在計算紙上畫出 y = sin(x) 在 [0, 2π] 區間的圖形。\n"
        "提示：圖形通過 (0,0), (π/2, 1), (π, 0), (3π/2, -1), (2π, 0)。\n"
        "完成後請點擊「AI 檢查」。"
    )
    return {"question_text": question_text, "answer": None, "correct_answer": "graph"}

def check(user_answer, correct_answer):
    return {"correct": True, "result": "觀念正確！sin函數圖形是一個週期性的波浪狀曲線。", "next_question": True}