import random

def generate(level=1):
    """
    生成一道「求過圓上一點的切線方程式」的題目。
    level 1: 圓心在原點。切線為 x0*x + y0*y = r^2
    level 2: 圓心不在原點。
    """
    if level == 1:
        # 為了讓點是整數，從畢氏三元數構造
        sides = random.choice([(3,4,5), (5,12,13), (8,15,17)])
        x0 = random.choice([sides[0], -sides[0]])
        y0 = random.choice([sides[1], -sides[1]])
        r = sides[2]
        h, k = 0, 0
        circle_eq = f"x² + y² = {r**2}"
        correct_answer = f"{x0}x + {y0}y = {r**2}".replace("+-", "-")
    else: # level 2
        h, k = random.randint(-3, 3), random.randint(-3, 3)
        r = random.randint(3, 5)
        # 隨機選圓上一點
        x0, y0 = h+r, k
        circle_eq = f"(x-{h})² + (y-{k})² = {r**2}"
        # (x0-h)(x-h) + (y0-k)(y-k) = r^2
        # r(x-h) + 0 = r^2 => x-h = r => x = h+r
        correct_answer = f"x = {x0}"

    question_text = f"請求出圓 C: {circle_eq} 上一點 P({x0}, {y0}) 的切線方程式。"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").lower()
    correct = str(correct_answer).strip().replace(" ", "").lower()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}