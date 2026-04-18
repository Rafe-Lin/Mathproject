# \極限\數列的夾擠定理
import random

def generate(level=1):
    """
    生成一道「數列的夾擠定理」的觀念題。
    """
    if level == 1:
        limit = random.randint(1, 5)
        question_text = f"已知對於所有 n，數列 aₙ, bₙ, cₙ 滿足 aₙ ≤ bₙ ≤ cₙ。若已知 lim(aₙ) = {limit} 且 lim(cₙ) = {limit}，請問 lim(bₙ) 是多少？"
        correct_answer = str(limit)
    else: # level 2
        question_text = "請求出數列 aₙ = sin(n)/n 的極限值。"
        correct_answer = "0"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}