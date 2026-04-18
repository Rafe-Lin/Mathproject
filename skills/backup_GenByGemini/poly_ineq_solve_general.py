import random
import numpy as np
from .utils import poly_to_string

def generate(level=1):
    """
    生成一道「一般高次不等式求解」的題目。
    此為觀念/作圖題，重點在於因式分解。
    """
    r1, r2, r3 = random.sample(range(-3, 4), 3)
    f = np.poly1d([1, -r1]) * np.poly1d([1, -r2]) * np.poly1d([1, -r3])
    op = random.choice(['>', '<', '>=', '<='])
    question_text = f"請求解高次不等式：{poly_to_string(f)} {op} 0\n(此為作圖題，請在計算紙上畫出數線解，並點擊 AI 檢查)"
    return {"question_text": question_text, "answer": None, "correct_answer": "graph"}

def check(user_answer, correct_answer):
    return {"correct": True, "result": "觀念正確！解高次不等式的關鍵是先因式分解找實根，再利用數線判斷正負區間。", "next_question": True}