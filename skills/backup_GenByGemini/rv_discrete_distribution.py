import random

def generate(level=1):
    """
    生成一道「離散型隨機變數 (機率分布)」的題目。
    """
    if level == 1:
        p1, p2 = random.randint(1, 4), random.randint(1, 4)
        total = p1 + p2 + 1
        question_text = f"一個袋中有 {p1} 個紅球和 {p2} 個白球。從袋中隨機抽取一球，令隨機變數 X 表示抽中紅球的個數。請問 P(X=1) 是多少？ (請以最簡分數 a/b 表示)"
        correct_answer = f"{p1}/{p1+p2}"
    else: # level 2
        p1, p2, p3 = random.randint(1, 3), random.randint(1, 3), random.randint(1, 3)
        total = p1 + p2 + p3
        question_text = f"一個機率分布表如下：\nX | 1 | 2 | 3\n--|---|---|--\nP(X) | {p1}/{total} | {p2}/{total} | p\n請問 p 的值是多少？ (請以最簡分數 a/b 表示)"
        correct_answer = f"{p3}/{total}"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}