import random

def generate(level=1):
    """
    生成一道「極坐標」的題目。
    level 1: 極坐標轉直角坐標。
    level 2: 直角坐標轉極坐標。
    """
    if level == 1:
        r = random.randint(2, 10)
        angle = random.choice([30, 45, 60, 120, 150, 210, 240, 300, 330])
        question_text = f"一個點的極坐標為 [{r}, {angle}°]，請問其直角坐標為何？\n(這是一道觀念/計算題，請在紙上作答)"
        correct_answer = "作圖題"
    else: # level 2
        # 從畢氏三元數構造
        a, b, c = random.choice([(3,4,5), (5,12,13)])
        x, y = random.choice([a, -a]), random.choice([b, -b])
        question_text = f"一個點的直角坐標為 ({x}, {y})，請問其極坐標的 r 值是多少？"
        correct_answer = str(c)

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    if correct_answer == "作圖題":
        return {"correct": True, "result": "觀念正確！x=rcos(θ), y=rsin(θ)。", "next_question": True}
    user = user_answer.strip().replace(" ", "")
    is_correct = (user == correct_answer)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}