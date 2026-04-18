import random

def generate(level=1):
    """
    生成一道「圓的一般式化為標準式」的題目。
    level 1: 係數簡單，圓心半徑為整數。
    level 2: 係數較複雜。
    """
    if level == 1:
        h, k = random.randint(-5, 5), random.randint(-5, 5)
        r = random.randint(2, 6)
    else: # level 2
        h, k = random.randint(-9, 9), random.randint(-9, 9)
        r = random.randint(2, 10)

    # 從 (x-h)^2 + (y-k)^2 = r^2 展開
    # x^2 - 2hx + h^2 + y^2 - 2ky + k^2 - r^2 = 0
    # x^2 + y^2 + Dx + Ey + F = 0
    D = -2 * h
    E = -2 * k
    F = h**2 + k**2 - r**2

    D_str = f"+ {D}" if D >= 0 else f"- {abs(D)}"
    E_str = f"+ {E}" if E >= 0 else f"- {abs(E)}"
    F_str = f"+ {F}" if F >= 0 else f"- {abs(F)}"

    question_text = f"請將圓的一般式 x² + y² {D_str}x {E_str}y {F_str} = 0 化為標準式。"

    h_part = f"(x - {h})²" if h > 0 else f"(x + {abs(h)})²" if h < 0 else "x²"
    k_part = f"(y - {k})²" if k > 0 else f"(y + {abs(k)})²" if k < 0 else "y²"
    correct_answer = f"{h_part} + {k_part} = {r**2}"

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").replace("^2", "²")
    correct = str(correct_answer).strip().replace(" ", "")
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}