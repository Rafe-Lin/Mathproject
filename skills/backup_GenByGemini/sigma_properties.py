import random

def generate(level=1):
    """
    生成一道「Sigma (Σ) 性質」的觀念題。
    """
    if level == 1:
        question_text = (
            "關於 Σ 的性質，下列何者「正確」？\n\n"
            "A) Σ(aₖ + bₖ) = Σaₖ + Σbₖ\n"
            "B) Σ(aₖ * bₖ) = (Σaₖ) * (Σbₖ)\n"
            "C) Σ(c * aₖ) = c + Σaₖ (其中 c 為常數)"
        )
        correct_answer = "A"
    else: # level 2
        question_text = (
            "關於 Σ 的性質，下列何者「錯誤」？\n\n"
            "A) Σ(c) = n*c (其中 c 為常數，從 k=1 到 n)\n"
            "B) Σ(aₖ - bₖ) = Σaₖ - Σbₖ\n"
            "C) Σ(aₖ / bₖ) = (Σaₖ) / (Σbₖ)"
        )
        correct_answer = "C"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().upper()
    is_correct = (user == correct_answer)
    result_text = f"完全正確！答案是 {correct_answer}。Σ 對加減法和常數倍可拆開，但對乘除法不可拆開。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}