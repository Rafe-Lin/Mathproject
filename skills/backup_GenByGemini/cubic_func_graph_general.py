import random

def generate(level=1):
    """
    生成一道「一般三次函數圖形」的題目。
    此為觀念/作圖題。
    """
    a = random.choice([-2, -1, 1, 2])
    b = random.randint(-3, 3)
    c = random.randint(-4, 4)
    d = random.randint(-5, 5)

    func_str = f"y = {a}x³ + {b}x² + {c}x + {d}".replace("+-", "-")

    question_text = (
        f"請在計算紙上大致描繪出三次函數 {func_str} 的圖形。\n"
        f"提示：\n"
        f"1. 判斷首項係數 a ({a})，決定圖形右方是上升或下降。\n"
        f"2. 找出與 y 軸的交點 (0, {d})。\n"
        f"3. (進階) 配方找出對稱中心。\n"
        "完成後請點擊「AI 檢查」。"
    )
    return {"question_text": question_text, "answer": None, "correct_answer": "graph"}

def check(user_answer, correct_answer):
    return {"correct": True, "result": "觀念正確！掌握首項係數和 y 截距是畫出三次函數圖形的關鍵第一步。", "next_question": True}