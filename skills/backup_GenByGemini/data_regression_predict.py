import random

def generate(level=1):
    """
    生成一道「利用迴歸直線預測」的題目。
    """
    a = round(random.uniform(1.5, 3.0), 1)
    b = round(random.uniform(5, 15), 1)
    
    if level == 1:
        x_val = random.randint(10, 20)
        question_text = f"已知兩變數的迴歸直線方程式為 y = {a}x + {b}。當 x = {x_val} 時，y 的預測值是多少？"
        y_val = a * x_val + b
    else: # level 2
        y_val = random.randint(50, 80)
        question_text = f"已知兩變數的迴歸直線方程式為 y = {a}x + {b}。若 y 的觀測值為 {y_val}，x 的預測值是多少？ (四捨五入至小數點後一位)"
        x_val = (y_val - b) / a

    correct_answer = str(round(y_val if level==1 else x_val, 1))
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}