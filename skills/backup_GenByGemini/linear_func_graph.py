import random

def generate(level=1):
    """
    生成一道「一次函數圖形」的題目。
    此為觀念/作圖題。
    level 1: y = ax+b
    level 2: ax+by+c=0
    """
    if level == 1:
        a = random.randint(-3, 3)
        while a == 0: a = random.randint(-3, 3)
        b = random.randint(-5, 5)
        func_str = f"y = {a}x + {b}".replace("+-", "-")
    else: # level 2
        a = random.randint(-3, 3)
        b = random.randint(-3, 3)
        while a == 0 or b == 0: a,b = random.randint(-3, 3), random.randint(-3, 3)
        c = random.randint(-5, 5)
        func_str = f"{a}x + {b}y + {c} = 0".replace("+-", "-")

    question_text = (
        f"請在計算紙上畫出一次函數 {func_str} 的圖形。\n"
        "提示：可以找出圖形與兩軸的交點，再將兩點連成直線。\n"
        "完成後請點擊「AI 檢查」。"
    )
    return {"question_text": question_text, "answer": None, "correct_answer": "graph"}

def check(user_answer, correct_answer):
    return {"correct": True, "result": "觀念正確！畫直線的關鍵是找到兩個點，例如與 X, Y 軸的交點。", "next_question": True}