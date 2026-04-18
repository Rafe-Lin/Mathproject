import random

def generate(level=1):
    """
    生成一道「集合運算」的題目。
    level 1: 交集 A ∩ B
    level 2: 聯集 A ∪ B
    """
    # 生成兩個集合
    A = set(random.sample(range(1, 20), random.randint(5, 8)))
    B = set(random.sample(range(1, 20), random.randint(5, 8)))
    
    A_str = str(sorted(list(A)))
    B_str = str(sorted(list(B)))

    if level == 1:
        question_text = f"給定兩集合 A = {A_str} 與 B = {B_str}，請求出它們的交集 A ∩ B。\n(請由小到大排列，用逗號分隔)"
        intersection = sorted(list(A.intersection(B)))
        correct_answer = ",".join(map(str, intersection))
    else: # level 2
        question_text = f"給定兩集合 A = {A_str} 與 B = {B_str}，請求出它們的聯集 A ∪ B。\n(請由小到大排列，用逗號分隔)"
        union = sorted(list(A.union(B)))
        correct_answer = ",".join(map(str, union))

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {{{correct_answer}}}。" if is_correct else f"答案不正確。正確答案應為：{{{correct_answer}}}"
    return {"correct": is_correct, "result": result_text, "next_question": True}