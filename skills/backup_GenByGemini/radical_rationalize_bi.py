import random

def generate(level=1):
    """
    生成一道「根式有理化 (雙項分母)」的題目。
    level 1: a + √b
    level 2: √a + √b
    """
    num = random.randint(1, 5)
    
    if level == 1:
        a = random.randint(2, 5)
        b = random.randint(2, 5)
        while a*a == b: b = random.randint(2, 5)
        question_text = f"請將分數 {num}/({a} + √{b}) 的分母有理化。"
        correct_answer = f"({num*a} - {num}√{b})/({a*a - b})"
    else: # level 2
        a = random.randint(2, 7)
        b = random.randint(2, 7)
        while a == b: b = random.randint(2, 7)
        question_text = f"請將分數 {num}/(√{a} + √{b}) 的分母有理化。"
        correct_answer = f"({num}√{a} - {num}√{b})/({a - b})"

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}