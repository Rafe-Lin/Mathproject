# \三角函數\cos函數圖形
import random

def generate(level=1):
    """
    生成一道「cos函數圖形」的觀念題。
    """
    question_text = (
        "請在計算紙上畫出 y = cos(x) 在 [0, 2π] 區間的圖形。\n"
        "提示：圖形通過 (0,1), (π/2, 0), (π, -1), (3π/2, 0), (2π, 1)。\n"
        "完成後請點擊「AI 檢查」。"
    )
    return {"question_text": question_text, "answer": None, "correct_answer": "graph"}

def check(user_answer, correct_answer):
    return {"correct": True, "result": "觀念正確！cos函數圖形與sin函數圖形相似，但有相位差。", "next_question": True}