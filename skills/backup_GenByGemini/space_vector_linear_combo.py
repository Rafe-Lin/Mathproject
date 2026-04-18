import random

def generate(level=1):
    """
    生成一道「線性組合」的題目。
    """
    # 構造線性獨立的向量
    v1 = [random.randint(1, 3), random.randint(1, 3), 0]
    v2 = [random.randint(1, 3), 0, random.randint(1, 3)]
    
    x = random.randint(-3, 3)
    y = random.randint(-3, 3)
    
    w = [x*v1[i] + y*v2[i] for i in range(3)]
    
    if level == 1:
        question_text = f"已知向量 a={tuple(v1)}, b={tuple(v2)}，請求出向量 w = {x}a + {y}b。"
        correct_answer = str(tuple(w))
    else: # level 2
        question_text = f"已知向量 w={tuple(w)} 可表示為向量 a={tuple(v1)} 與 b={tuple(v2)} 的線性組合，即 w = xa + yb，請求出數對 (x, y)。"
        correct_answer = f"({x},{y})"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip().replace(" ", "")
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}