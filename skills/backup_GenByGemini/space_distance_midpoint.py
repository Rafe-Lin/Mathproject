import random
import math

def generate(level=1):
    """
    生成一道「空間中兩點距離與中點」的題目。
    """
    p1 = [random.randint(-10, 10) for _ in range(3)]
    p2 = [random.randint(-10, 10) for _ in range(3)]
    
    if level == 1:
        # 確保中點為整數
        p2 = [p2[i] if (p1[i]+p2[i])%2==0 else p2[i]+1 for i in range(3)]
        question_text = f"空間中兩點 A({p1[0]},{p1[1]},{p1[2]}) 與 B({p2[0]},{p2[1]},{p2[2]}) 的中點坐標為何？"
        midpoint = [ (p1[i]+p2[i])//2 for i in range(3) ]
        correct_answer = f"({midpoint[0]},{midpoint[1]},{midpoint[2]})"
    else: # level 2
        question_text = f"空間中兩點 A({p1[0]},{p1[1]},{p1[2]}) 與 B({p2[0]},{p2[1]},{p2[2]}) 的距離為何？"
        dist_sq = (p1[0]-p2[0])**2 + (p1[1]-p2[1])**2 + (p1[2]-p2[2])**2
        # 為了讓答案漂亮，這裡不開根號
        correct_answer = f"√{dist_sq}"

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").replace("sqrt", "√")
    correct = str(correct_answer).strip().replace(" ", "")
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}