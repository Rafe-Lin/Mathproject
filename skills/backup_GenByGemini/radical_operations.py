import random

def generate(level=1):
    """
    生成一道「根式運算」的題目。
    level 1: 簡單加減
    level 2: 乘法或除法
    """
    radicand = random.choice([2, 3, 5, 6])
    a = random.randint(2, 7)
    b = random.randint(2, 7)
    
    if level == 1:
        # 簡單加減: a√c + b√c
        op = random.choice(['+', '-'])
        question_text = f"請計算：{a}√{radicand} {op} {b}√{radicand}"
        result = a + b if op == '+' else a - b
        correct_answer = f"{result}√{radicand}"
    else: # level 2
        # 乘法: (a√c) * (b√d)
        radicand2 = random.choice([2, 3, 5, 7])
        question_text = f"請計算：({a}√{radicand}) × ({b}√{radicand2})"
        correct_answer = f"{a*b}√{radicand*radicand2}" # 未化簡，可再擴充

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}