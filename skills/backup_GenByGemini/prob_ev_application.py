import random

def generate(level=1):
    """
    生成一道「期望值應用」的題目，如公平賭局。
    """
    if level == 1:
        prize = random.randint(5, 10) * 10
        cost = prize / 6
        question_text = f"擲一顆公正骰子，若擲出1點可得 {prize} 元，擲出其他點數則無獎金。若要使這個遊戲為「公平賭局」，請問玩一次應付多少錢？"
        correct_answer = str(round(cost, 2))
    else: # level 2
        prize = 120
        cost = 30
        # E = 1/6 * (x - 30) * 5 + 1/6 * (120 - 30) = 0
        # 5x - 150 + 90 = 0 => 5x = 60 => x = 12
        loss = 12
        question_text = f"擲一顆公正骰子，擲出1點可得 {prize} 元，擲出其他點數則需賠錢。若此賭局為公平賭局，且玩一次需付 {cost} 元，請問擲出其他點數時應賠多少錢？"
        correct_answer = str(loss)
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}