import random

def generate(level=1):
    """
    生成一道「空間向量的坐標表示」的題目。
    """
    p1 = [random.randint(-10, 10) for _ in range(3)]
    p2 = [random.randint(-10, 10) for _ in range(3)]
    
    if level == 1:
        question_text = f"已知點 A({p1[0]},{p1[1]},{p1[2]}) 與點 B({p2[0]},{p2[1]},{p2[2]})，請求出向量 AB。"
        vec = [p2[i] - p1[i] for i in range(3)]
    else: # level 2
        question_text = f"已知點 A({p1[0]},{p1[1]},{p1[2]}) 與點 B({p2[0]},{p2[1]},{p2[2]})，請求出向量 BA。"
        vec = [p1[i] - p2[i] for i in range(3)]
        
    correct_answer = f"({vec[0]},{vec[1]},{vec[2]})"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip().replace(" ", "")
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}