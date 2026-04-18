import random

def generate(level=1):
    """
    生成一道「三次乘法公式 (展開)」的題目。
    level 1: (a+b)³ 或 (a-b)³
    level 2: (a+b)(a²-ab+b²) 或 (a-b)(a²+ab+b²)
    """
    a = 'x'
    b = random.randint(1, 5)

    if level == 1:
        op = random.choice(['+', '-'])
        question_text = f"請展開並化簡：({a} {op} {b})³"
        if op == '+':
            correct_answer = f"x³ + {3*b}x² + {3*b*b}x + {b**3}"
        else:
            correct_answer = f"x³ - {3*b}x² + {3*b*b}x - {b**3}"
    else: # level 2
        op = random.choice(['+', '-'])
        if op == '+': # 立方和展開
            question_text = f"請展開並化簡：({a} + {b})({a}² - {b}{a} + {b**2})"
            correct_answer = f"x³ + {b**3}"
        else: # 立方差展開
            question_text = f"請展開並化簡：({a} - {b})({a}² + {b}{a} + {b**2})"
            correct_answer = f"x³ - {b**3}"

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}