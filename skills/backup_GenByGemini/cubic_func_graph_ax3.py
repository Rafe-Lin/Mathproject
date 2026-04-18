import random

def generate(level=1):
    """
    生成一道「y=ax³ 圖形」的題目。
    此為觀念題。
    """
    if level == 1:
        a = random.choice([1, -1])
    else:
        a = random.choice([2, -2, 3, -3])

    func_str = f"y = {a}x³".replace("1x", "x")
    
    question_text = (
        f"關於三次函數 {func_str} 的圖形，下列敘述何者「正確」？\n"
        f"A) 圖形對稱於 y 軸\n"
        f"B) 圖形對稱於原點\n"
        f"C) 圖形是一個拋物線"
    )
    correct_answer = "B"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().upper()
    is_correct = (user == correct_answer)
    result_text = f"完全正確！答案是 {correct_answer}。y=ax³ 的圖形都以原點為對稱中心。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}