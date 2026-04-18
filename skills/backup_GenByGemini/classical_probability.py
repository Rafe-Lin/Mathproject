import random

def generate_classical_probability_question():
    """動態生成一道「古典機率」的題目"""
    total_outcomes = 6
    event_type = random.choice(['even', 'odd', 'greater_than'])
    if event_type == 'even':
        fav_outcomes = 3 # 2, 4, 6
        question_text = "擲一顆公正的骰子，出現偶數點的機率是多少？（請以 a/b 的形式表示）"
        answer = "3/6"
    elif event_type == 'odd':
        fav_outcomes = 3 # 1, 3, 5
        question_text = "擲一顆公正的骰子，出現奇數點的機率是多少？（請以 a/b 的形式表示）"
        answer = "3/6"
    else: # greater_than
        num = random.randint(1, 4)
        fav_outcomes = 6 - num
        question_text = f"擲一顆公正的骰子，出現比 {num} 大的點數的機率是多少？（請以 a/b 的形式表示）"
        answer = f"{fav_outcomes}/6"
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }
