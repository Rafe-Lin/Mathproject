import random

def generate(level=1):
    """
    生成一道「向量相等」的題目。
    """
    v1 = [random.randint(-10, 10) for _ in range(2)]
    x = random.randint(-10, 10)
    
    if level == 1:
        question_text = f"已知向量 a = ({v1[0]}, {v1[1]}) 與向量 b = (x, {v1[1]}) 相等，請問 x 的值是多少？"
        correct_answer = str(v1[0])
    else: # level 2
        question_text = f"已知向量 a = ({v1[0]}, y+1) 與向量 b = ({v1[0]}, {v1[1]+1}) 相等，請問 y 的值是多少？"
        correct_answer = str(v1[1])
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}