import random

def generate(level=1):
    """
    生成一道「線性遞迴關係式」的題目。
    an = r*an-1 + d
    此為觀念題，要求學生寫出前幾項。
    """
    a1 = random.randint(1, 5)
    if level == 1:
        r = random.randint(2, 4)
        d = random.randint(1, 5)
    else: # level 2
        r = random.randint(2, 3)
        d = random.randint(-5, -1)
    d_str = f"+ {d}" if d >= 0 else f"- {abs(d)}"

    relation = f"a₁ = {a1} 且 aₙ = {r} * aₙ₋₁ {d_str} (當 n ≥ 2)"
    a2 = r*a1 + d
    a3 = r*a2 + d
    
    question_text = f"已知數列 <aₙ> 的遞迴定義為：{relation}，請依序寫出 a₂, a₃ 的值。\n(格式: a2值,a3值)"
    correct_answer = f"{a2},{a3}"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}