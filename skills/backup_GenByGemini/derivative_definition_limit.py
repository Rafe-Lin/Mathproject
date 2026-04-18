import random

def generate(level=1):
    """
    生成一道「導數定義 (極限法)」的題目。
    """
    a = random.randint(1, 5)
    if level == 1:
        c = random.randint(2, 5)
        question_text = f"請利用導數的定義，求函數 f(x) = {c}x 在 x={a} 處的導數 f'({a})。"
        correct_answer = str(c)
    else: # level 2
        question_text = f"請利用導數的定義，求函數 f(x) = x² 在 x={a} 處的導數 f'({a})。"
        # lim (h->0) [(a+h)²-a²]/h = lim (2ah+h²)/h = 2a
        correct_answer = str(2 * a)
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}