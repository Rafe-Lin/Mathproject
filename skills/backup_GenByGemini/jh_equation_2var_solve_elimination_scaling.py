# skills/jh_equation_2var_solve_elimination_scaling.py
import random

def generate(level=1):
    """
    生成一道「加減消去法 (需變形)」的題目。
    """
    x = random.randint(-5, 5)
    y = random.randint(-5, 5)

    # 構造係數，確保不可以直接相加減
    a1 = random.randint(2, 4)
    b1 = random.randint(2, 4)
    a2 = random.randint(2, 4)
    b2 = random.randint(2, 4)
    
    # 確保係數不成比例，避免無限多解或無解
    while a1 * b2 == a2 * b1:
        a2 = random.randint(2, 4)
        b2 = random.randint(2, 4)

    c1 = a1 * x + b1 * y
    c2 = a2 * x + b2 * y

    question_text = f"請用加減消去法解下列二元一次聯立方程式：\n(1) {a1}x + {b1}y = {c1}\n(2) {a2}x + {b2}y = {c2}\n請回答 x,y 的值 (例如: 3,-4)"
    correct_answer = f"{x},{y}"

    context_string = "使用加減消去法解聯立方程式，需要先將其中一個未知數的係數變為相同或相反數。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = correct_answer.strip().replace(" ", "")

    try:
        user_x, user_y = map(int, user.split(','))
        correct_x, correct_y = map(int, correct.split(','))
        if user_x == correct_x and user_y == correct_y:
            is_correct = True
            result_text = f"完全正確！解為 x={correct_x}, y={correct_y}。"
        else:
            is_correct = False
            result_text = f"答案不正確。正確答案是：x={correct_x}, y={correct_y}"
    except ValueError:
        is_correct = False
        result_text = f"請用 'x,y' 的格式作答，例如 3,-4。正確答案是：x={correct.split(',')[0]}, y={correct.split(',')[1]}"

    return {"correct": is_correct, "result": result_text, "next_question": is_correct}