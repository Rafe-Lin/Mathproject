# \三角函數\tan函數圖形
import random

def generate(level=1):
    """
    生成一道「tan函數圖形」的觀念題。
    """
    question_text = (
        "請在計算紙上畫出 y = tan(x) 在 (-π/2, π/2) 區間的圖形。\n"
        "提示：圖形通過 (0,0)，且在 x=±π/2 有垂直漸近線。\n"
        "完成後請點擊「AI 檢查」。"
    )
    return {"question_text": question_text, "answer": None, "correct_answer": "graph"}

def check(user_answer, correct_answer):
    return {"correct": True, "result": "觀念正確！tan函數圖形是週期性的，且有垂直漸近線。", "next_question": True}