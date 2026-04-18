import random
import math

def generate(level=1):
    """
    生成一道「不盡相異物排列」的題目。
    level 1: 兩種相同物。
    level 2: 三種相同物。
    """
    if level == 1:
        question_text = "將 3 個紅球、2 個白球排成一列，共有多少種排法？"
        # 5! / (3! * 2!)
        correct_answer = str(math.factorial(5) // (math.factorial(3) * math.factorial(2)))
    else: # level 2
        question_text = "將 a,a,b,b,c,c,c 共 7 個字母排成一列，共有多少種排法？"
        # 7! / (2! * 2! * 3!)
        correct_answer = str(math.factorial(7) // (math.factorial(2) * math.factorial(2) * math.factorial(3)))
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}