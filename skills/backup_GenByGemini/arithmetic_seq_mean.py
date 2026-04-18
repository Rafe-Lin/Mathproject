import random

def generate(level=1):
    """
    生成一道「等差中項」的題目。
    """
    a1 = random.randint(-10, 10)
    d = random.randint(-5, 5)
    while d == 0: d = random.randint(-5, 5)
    x = a1 + d
    c = a1 + 2*d
    question_text = f"若 {a1}, x, {c} 三數成等差數列，請問 x 的值是多少？"
    correct_answer = str(x)

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}