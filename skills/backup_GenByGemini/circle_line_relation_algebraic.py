import random

def generate(level=1):
    """
    生成一道「從代數觀點判斷圓與直線關係」的題目。
    解聯立，看判別式 D 的正負。
    level 1: 圓心在原點，直線為 y=c 或 x=c。
    level 2: 圓心在原點，直線為 y=mx+c。
    """
    r = random.randint(3, 8)
    circle_eq = f"x² + y² = {r**2}"

    if level == 1:
        line_type = random.choice(['x', 'y'])
        c = random.randint(r-2, r+2)
        if line_type == 'x':
            line_eq = f"x = {c}"
            # c^2 + y^2 = r^2 => y^2 = r^2 - c^2
            D = r**2 - c**2
        else:
            line_eq = f"y = {c}"
            # x^2 + c^2 = r^2 => x^2 = r^2 - c^2
            D = r**2 - c**2
    else: # level 2
        m = random.choice([-2, -1, 1, 2])
        c = random.randint(-5, 5)
        line_eq = f"y = {m}x + {c}"
        # x^2 + (mx+c)^2 = r^2
        # x^2 + m^2x^2 + 2mcx + c^2 - r^2 = 0
        # (1+m^2)x^2 + (2mc)x + (c^2-r^2) = 0
        # D = (2mc)^2 - 4(1+m^2)(c^2-r^2)
        D = (2*m*c)**2 - 4*(1+m**2)*(c**2 - r**2)

    if D > 0: correct_answer = "相交兩點"
    elif D == 0: correct_answer = "相切"
    else: correct_answer = "不相交"

    question_text = f"利用判別式，判斷圓 C: {circle_eq} 與直線 L: {line_eq} 的關係為何？ (相交兩點、相切、不相交)"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    is_correct = (user == correct_answer)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}