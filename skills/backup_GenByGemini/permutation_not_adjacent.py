import random
import math

def P(n, k):
    return math.factorial(n) // math.factorial(n - k)

def generate(level=1):
    """
    生成一道「不相鄰排列」的題目。
    level 1: 兩人不相鄰 (插空法)。
    level 2: 三人皆不相鄰 (插空法)。
    """
    if level == 1:
        question_text = "甲、乙、丙、丁 4 人排成一列，若甲、乙兩人不得相鄰，共有多少種排法？"
        # 丙丁先排: 2!，再將甲乙插入 3 個間隔: P(3,2)
        correct_answer = str(math.factorial(2) * P(3, 2))
    else: # level 2
        question_text = "甲、乙、丙、丁、戊 5 人排成一列，若甲、乙、丙三人皆不相鄰，共有多少種排法？"
        # 丁戊先排: 2!，再將甲乙丙插入 3 個間隔: P(3,3)
        correct_answer = str(math.factorial(2) * P(3, 3))
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}