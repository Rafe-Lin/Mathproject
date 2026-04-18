import random

def generate(level=1):
    """
    生成一道「期望值」的計算題。
    E(X) = Σ [x * P(x)]
    level 1: 擲骰子。
    level 2: 抽獎券。
    """
    if level == 1:
        question_text = "擲一顆公正的骰子一次，所得點數的期望值是多少？"
        # (1+2+3+4+5+6)/6 = 21/6 = 3.5
        correct_answer = "3.5"
    else: # level 2
        prize1, p1 = 1000, 1
        prize2, p2 = 100, 5
        total_tickets = 100
        question_text = f"一個抽獎活動共有 {total_tickets} 張獎券，其中 {p1} 張可得獎金 {prize1} 元，{p2} 張可得獎金 {prize2} 元，其餘無獎。請問抽一張獎券的獎金期望值是多少元？"
        ev = (prize1 * p1 + prize2 * p2) / total_tickets
        correct_answer = str(ev)
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}