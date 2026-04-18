# \積分應用\旋轉體體積 (圓盤法)
import random

def generate(level=1):
    """
    生成一道「旋轉體體積 (圓盤法)」的題目。
    """
    r = random.randint(2, 5)
    a, b = 0, random.randint(3, 6)
    if level == 1:
        question_text = f"將區域 y={r}, x={a}, x={b} 與 x 軸所圍成的矩形，對 x 軸旋轉所得的圓柱體體積為何？"
        # V = π * r² * h
        correct_answer = f"{r*r*(b-a)}π"
    else: # level 2
        question_text = f"將函數 y=x 在區間 [{a}, {b}] 的圖形與 x 軸所圍成的區域，對 x 軸旋轉所得的圓錐體體積為何？"
        # V = π ∫[a,b] x² dx = π [x³/3] from a to b
        vol = (b**3 - a**3) / 3
        correct_answer = f"{vol}π"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").replace("pi", "π")
    correct = str(correct_answer).strip().replace(" ", "")
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}