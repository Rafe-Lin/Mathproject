import random

def generate(level=1):
    """
    生成一道「計數乘法原理」的應用題。
    """
    if level == 1:
        a = random.randint(3, 5)
        b = random.randint(2, 4)
        question_text = f"小華有 {a} 件不同的上衣和 {b} 件不同的褲子，請問他有多少種搭配方式？"
    else: # level 2
        a = random.randint(3, 5)
        b = random.randint(2, 4)
        c = random.randint(2, 3)
        question_text = f"從台北到台中，有 {a} 種客運可選；從台中到台南，有 {b} 種客運可選；從台南到高雄，有 {c} 種客運可選。請問從台北經台中、台南到高雄，共有多少種交通方式？"

    total = a * b if level == 1 else a * b * c
    correct_answer = str(total)

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}