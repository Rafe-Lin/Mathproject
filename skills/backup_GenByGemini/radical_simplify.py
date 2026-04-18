import random
import math

def generate(level=1):
    """
    生成一道「根式化簡」的題目。
    level 1: 根號內數字較小
    level 2: 根號內數字較大
    """
    if level == 1:
        # 數字較小，例如 sqrt(12) = 2*sqrt(3)
        inner = random.randint(2, 5)**2 * random.choice([2, 3, 5])
        a = int(math.sqrt(inner))
        b = inner // (a*a) if a != 0 else inner
    else: # level 2
        # 數字較大，例如 sqrt(72) = 6*sqrt(2)
        inner = random.randint(2, 10)**2 * random.choice([2, 3, 5, 6, 7])
    
    question_text = f"請化簡 √{inner} 為最簡根式。"
    
    # 計算正確答案
    perfect_square = max([i*i for i in range(1, int(math.sqrt(inner)) + 1) if inner % (i*i) == 0])
    coeff = int(math.sqrt(perfect_square))
    radicand = inner // perfect_square
    correct_answer = f"{coeff}√{radicand}" if radicand > 1 else str(coeff)

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}