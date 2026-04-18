import random
from fractions import Fraction

def generate(level=1):
    """
    生成一道「廣義角三角函數定義」的題目。
    """
    # 隨機選一個象限的點
    quadrant = random.randint(1, 4)
    if quadrant == 1: x, y = random.randint(1, 10), random.randint(1, 10)
    elif quadrant == 2: x, y = random.randint(-10, -1), random.randint(1, 10)
    elif quadrant == 3: x, y = random.randint(-10, -1), random.randint(-10, -1)
    else: x, y = random.randint(1, 10), random.randint(-10, -1)
    
    # 為了讓 r 是整數，使用畢氏三元數
    a, b, c = random.choice([(3,4,5), (5,12,13)])
    x, y = a, b
    if quadrant == 2: x = -a
    elif quadrant == 3: x, y = -a, -b
    elif quadrant == 4: y = -b
    r = c

    func = random.choice(['sin', 'cos', 'tan'])
    question_text = f"設 θ 為一個標準位置角，其終邊通過點 P({x}, {y})，請問 {func}(θ) 的值是多少？ (請以最簡分數 a/b 表示)"
    
    if func == 'sin': frac = Fraction(y, r)
    elif func == 'cos': frac = Fraction(x, r)
    else: frac = Fraction(y, x)
    correct_answer = f"{frac.numerator}/{frac.denominator}"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}