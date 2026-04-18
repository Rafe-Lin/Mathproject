import random

def generate(level=1):
    """
    生成一道「三次函數配方」的題目。
    此為觀念/作圖題。
    """
    if level == 1:
        a = 1
    else:
        a = random.choice([-2, -1, 2])

    h = random.randint(-3, 3)
    p = random.randint(-5, 5)
    k = random.randint(-5, 5)
    
    # f(x) = a(x-h)³ + p(x-h) + k
    func_str = f"y = {a}(x-{h})³ + {p}(x-{h}) + {k}".replace("+-", "-")

    question_text = (
        f"三次函數 {func_str} 是由哪個基本函數平移而來？其對稱中心為何？\n"
        "這是一道觀念題，請在計算紙上寫下你的答案，然後點擊「AI 檢查」。"
    )
    return {"question_text": question_text, "answer": None, "correct_answer": "graph"}

def check(user_answer, correct_answer):
    return {"correct": True, "result": "觀念正確！此圖形是由 y=ax³+px 平移而來，對稱中心為 (h, k)。", "next_question": True}