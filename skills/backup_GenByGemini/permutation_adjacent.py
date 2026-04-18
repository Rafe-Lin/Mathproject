import random
import math

def generate(level=1):
    """
    生成一道「相鄰排列」的題目。
    level 1: 2 人相鄰。
    level 2: 3 人相鄰。
    """
    total_people = random.randint(5, 7)
    if level == 1:
        adjacent_count = 2
        question_text = f"甲、乙、丙、丁、戊共 {total_people} 人排成一列，若甲、乙兩人必須相鄰，共有多少種排法？"
    else: # level 2
        adjacent_count = 3
        question_text = f"甲、乙、丙、丁、戊、己共 {total_people} 人排成一列，若甲、乙、丙三人必須完全相鄰，共有多少種排法？"
    
    # (n-k+1)! * k!
    correct_answer = str(math.factorial(total_people - adjacent_count + 1) * math.factorial(adjacent_count))
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}