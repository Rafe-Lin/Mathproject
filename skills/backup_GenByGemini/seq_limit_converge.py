import random

def generate(level=1):
    """
    生成一道「數列的收斂與發散」的觀念題。
    """
    if level == 1:
        seq = random.choice(["1/n", "(-1)ⁿ", "n²"])
        question_text = f"請問無窮數列 aₙ = {seq} 是收斂還是發散？ (收斂/發散)"
        if seq == "1/n":
            correct_answer = "收斂"
        else:
            correct_answer = "發散"
    else: # level 2
        question_text = (
            "下列哪個無窮數列是「收斂」的？\n\n"
            "A) aₙ = sin(n)\n"
            "B) aₙ = (n+1)/n\n"
            "C) aₙ = n"
        )
        correct_answer = "B"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip()
    is_correct = (user == correct_answer)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}