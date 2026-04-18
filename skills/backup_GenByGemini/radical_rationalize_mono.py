import random

def generate(level=1):
    """
    生成一道「根式有理化 (單項分母)」的題目。
    """
    num = random.randint(1, 10)
    den_rad = random.randint(2, 7)
    
    # 確保分子分母不為倍數關係
    while num % den_rad == 0:
        num = random.randint(1, 10)

    question_text = f"請將分數 {num}/√{den_rad} 的分母有理化。"
    correct_answer = f"({num}√{den_rad})/{den_rad}"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}