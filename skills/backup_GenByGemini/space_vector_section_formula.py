import random

def generate(level=1):
    """
    生成一道「空間向量分點公式」的題目。
    """
    A = [random.randint(-5, 5) for _ in range(3)]
    B = [random.randint(-5, 5) for _ in range(3)]
    
    m = random.randint(1, 4)
    n = random.randint(1, 4)
    
    if level == 1: # 內分點
        question_text = f"已知空間中兩點 A{tuple(A)}, B{tuple(B)}，若點 P 在線段 AB 上且 AP:PB = {m}:{n}，利用分點公式求 P 點坐標。"
        P = [(n*A[i] + m*B[i]) / (m+n) for i in range(3)]
    else: # level 2, 外分點
        while m == n: n = random.randint(1, 4)
        question_text = f"已知空間中兩點 A{tuple(A)}, B{tuple(B)}，若點 P 在直線 AB 上且 AP:PB = {m}:{n} (P為外分點)，求 P 點坐標。"
        P = [(-n*A[i] + m*B[i]) / (m-n) for i in range(3)]
        
    P_rounded = [round(c, 1) for c in P]
    correct_answer = str(tuple(P_rounded))
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip().replace(" ", "")
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}