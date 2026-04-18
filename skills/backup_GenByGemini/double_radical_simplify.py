import random

def generate(level=1):
    """
    生成一道「雙重根式化簡」的題目。
    √(A ± 2√B) = √x ± √y, 其中 x+y=A, xy=B
    """
    x = random.randint(2, 8)
    y = random.randint(1, x - 1)
    
    A = x + y
    B = x * y
    op_char = random.choice(['+', '-'])
    
    question_text = f"請化簡雙重根式：√({A} {op_char} 2√{B})"
    correct_answer = f"√{x} {op_char} √{y}"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}