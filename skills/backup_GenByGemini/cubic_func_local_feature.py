import random

def generate(level=1):
    """
    生成一道「三次函數局部特徵」的題目。
    此為觀念題。
    """
    # 構造一個有極值的函數 y = a(x-h)³ + p(x-h) + k, 其中 ap < 0
    a = random.choice([-2, -1, 1, 2])
    p = random.randint(1, 5) * (-1 if a > 0 else 1)
    h = random.randint(-3, 3)
    k = random.randint(-4, 4)

    # 展開
    # ax³ -3ahx² + (3ah²+p)x + (-ah³-ph+k)
    b = -3 * a * h
    c = 3 * a * h**2 + p
    d = -a * h**3 - p * h + k
    
    func_str = f"y = {a}x³ + {b}x² + {c}x + {d}".replace("+-", "-")

    question_text = (
        f"關於三次函數 {func_str} 的局部特徵，下列敘述何者「可能」正確？\n\n"
        f"A) 圖形沒有任何彎曲，是一條直線\n"
        f"B) 圖形可能會有一個局部極大值和一個局部極小值\n"
        f"C) 圖形一定沒有對稱中心"
    )
    correct_answer = "B"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().upper()
    is_correct = (user == correct_answer)
    result_text = f"完全正確！答案是 {correct_answer}。三次函數圖形在經歷一次微分後，若判別式大於零，則會有兩個極值。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}