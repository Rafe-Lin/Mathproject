# skills/jh_pythagorean_theorem_calc.py
import random
import math

def generate(level=1):
    """
    生成一道「畢氏定理計算」的題目。
    """
    # 使用畢氏三元數 (3,4,5), (5,12,13), (8,15,17), (7,24,25)
    triples = [(3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25)]
    a, b, c = random.choice(triples)
    
    # 隨機放大倍數
    multiplier = random.randint(1, 3)
    a, b, c = a * multiplier, b * multiplier, c * multiplier

    # 隨機決定要求哪一邊
    find = random.choice(['leg_a', 'leg_b', 'hypotenuse'])

    if find == 'hypotenuse':
        question_text = f"一個直角三角形的兩股長分別為 {a} 和 {b}，請問斜邊長是多少？"
        correct_answer = str(c)
    elif find == 'leg_a':
        question_text = f"一個直角三角形的斜邊長為 {c}，其中一股長為 {b}，請問另一股長是多少？"
        correct_answer = str(a)
    else: # leg_b
        question_text = f"一個直角三角形的斜邊長為 {c}，其中一股長為 {a}，請問另一股長是多少？"
        correct_answer = str(b)

    context_string = "利用畢氏定理 a² + b² = c² 來計算直角三角形的邊長。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    user = user_answer.strip()
    correct = correct_answer.strip()
    try:
        is_correct = int(user) == int(correct)
        result_text = f"完全正確！答案是 {correct}。" if is_correct else f"答案不正確。正確答案是：{correct}"
    except ValueError:
        is_correct = False
        result_text = f"請輸入數字答案。正確答案是：{correct}"
    return {"correct": is_correct, "result": result_text, "next_question": is_correct}