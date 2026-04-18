# \三角函數\三角函數的合成(疊合)
import random

def generate(level=1):
    """
    生成一道「三角函數的合成(疊合)」的題目。
    """
    if level == 1:
        a, b = 1, 1
        question_text = "請將函數 f(x) = sin(x) + cos(x) 合成 r*sin(x+α) 的形式，並求出 r 的值。"
        # r = sqrt(a²+b²)
        correct_answer = "√2"
    else: # level 2
        a = random.choice([1, 3, 4])
        b = random.choice([1, 3, 4])
        while a==b: b = random.choice([1, 3, 4])
        question_text = f"請將函數 f(x) = {a}sin(x) + {b}cos(x) 合成 r*sin(x+α) 的形式，並求出 r 的值。"
        r_sq = a*a + b*b
        correct_answer = f"√{r_sq}"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").replace("sqrt", "√")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}