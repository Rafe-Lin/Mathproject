import random

def generate(level=1):
    """
    生成一道「二集合取捨原理」的應用題。
    |A ∪ B| = |A| + |B| - |A ∩ B|
    """
    total = random.randint(30, 50)
    a_only = random.randint(5, 15)
    b_only = random.randint(5, 15)
    both = random.randint(3, 8)
    
    A = a_only + both
    B = b_only + both
    
    if level == 1:
        question_text = f"班上 {total} 位同學中，有 {A} 人喜歡籃球，{B} 人喜歡棒球，其中 {both} 人兩者都喜歡。請問只喜歡籃球或只喜歡棒球的同學共有幾人？"
        correct_answer = str(a_only + b_only)
    else: # level 2
        question_text = f"班上 {total} 位同學中，有 {A} 人喜歡籃球，{B} 人喜歡棒球，其中 {both} 人兩者都喜歡。請問兩種球類都不喜歡的同學有幾人？"
        # total - |A ∪ B| = total - (|A| + |B| - |A ∩ B|)
        correct_answer = str(total - (A + B - both))

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}