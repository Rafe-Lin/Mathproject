import random

def generate(level=1):
    """
    生成一道「二次函數圖形」的題目。
    此為觀念/作圖題。
    """
    if level == 1:
        a = 1
    else:
        a = random.choice([-2, -1, 2])

    h = random.randint(-3, 3)
    k = random.randint(-4, 4)
    
    h_part = f"(x - {h})²" if h > 0 else f"(x + {abs(h)})²" if h < 0 else "x²"
    k_part = f" + {k}" if k > 0 else f" - {abs(k)}" if k < 0 else ""
    a_part = str(a) if a != 1 else ""
    func_str = f"y = {a_part}{h_part}{k_part}"

    question_text = (
        f"請在計算紙上畫出二次函數 {func_str} 的圖形。\n"
        f"提示：先找出頂點 ({h}, {k})，再判斷開口方向 ({'上' if a > 0 else '下'})，並描繪出大致的拋物線形狀。\n"
        "完成後請點擊「AI 檢查」。"
    )
    return {"question_text": question_text, "answer": None, "correct_answer": "graph"}

def check(user_answer, correct_answer):
    return {"correct": True, "result": "觀念正確！畫拋物線的關鍵是找頂點、判斷開口方向。", "next_question": True}