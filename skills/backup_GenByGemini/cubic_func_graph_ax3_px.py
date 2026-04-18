import random

def generate(level=1):
    """
    生成一道「y=ax³+px 圖形」的題目。
    此為觀念題。
    """
    if level == 1:
        a = random.choice([1, -1])
        p = random.choice([1, -1, 2, -2])
    else:
        a = random.choice([2, -2, 3, -3])
        p = random.choice([-5, -4, 4, 5])

    func_str = f"y = {a}x³ + {p}x".replace("1x", "x").replace("+-", "-")
    
    question_text = (
        f"關於三次函數 {func_str} 的圖形，下列敘述何者「正確」？\n"
        f"A) 圖形對稱於 y 軸\n"
        f"B) 圖形對稱於原點\n"
        f"C) 圖形必有局部極大值與極小值"
    )
    correct_answer = "B"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().upper()
    is_correct = (user == correct_answer)
    result_text = f"完全正確！答案是 {correct_answer}。y=ax³+px 的圖形都以原點為對稱中心，但不一定有極值 (當 a, p 同號時)。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}