import random

def generate(level=1):
    """
    生成一道「三次函數廣域特徵」的題目。
    此為觀念題。
    """
    a = random.randint(1, 3)
    b = random.randint(-3, 3)
    c = random.randint(-4, 4)
    d = random.randint(-5, 5)

    func_str = f"y = {a}x³ + {b}x² + {c}x + {d}".replace("+-", "-")

    question_text = (
        f"觀察三次函數 {func_str}。\n"
        f"當 x 非常非常大（趨近於無限大）的時候，函數圖形會往哪個方向走？\n\n"
        f"A) 右上方 (y 趨近無限大)\n"
        f"B) 右下方 (y 趨近負無限大)"
    )
    # a > 0, x->inf, y->inf
    correct_answer = "A"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().upper()
    is_correct = (user == correct_answer)
    result_text = f"完全正確！答案是 {correct_answer}。三次函數的廣域特徵（右側趨勢）由最高次項係數的正負決定。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}