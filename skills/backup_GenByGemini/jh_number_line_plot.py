# skills/jh_number_line_plot.py
import random

def generate(level=1):
    """
    生成一道「在數線上標示點」的題目。
    此為圖形題。
    """
    # 隨機生成一個整數或包含 .5 的小數
    if random.choice([True, False]):
        num = random.randint(-10, 10)
    else:
        num = random.randint(-9, 9) + 0.5

    question_text = (
        f"請在下方的「數位計算紙」上，畫出數線並標示出點 {num} 的位置。\n\n"
        f"完成後，請點擊「AI 檢查」按鈕。"
    )

    # 圖形題的答案設為 None，由 AI 進行批改
    correct_answer = None
    
    context_string = f"在數線上標示出點 {num} 的位置。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "graph", # 答案類型為圖形
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    """
    圖形題的 check 函數通常只返回提示，實際批改由前端 AI 完成。
    """
    return {
        "correct": False, 
        "result": "請在數位計算紙上畫出您的解題過程，然後點選「AI 檢查」。",
        "next_question": False
    }