import random
import math

def generate(level=1):
    """
    生成一道「從幾何觀點判斷圓與直線關係」的題目。
    比較圓心到直線距離 d 與半徑 r 的大小。
    level 1: 圓心在原點，答案為整數。
    level 2: 圓心不在原點。
    """
    if level == 1:
        h, k = 0, 0
    else: # level 2
        h, k = random.randint(-3, 3), random.randint(-3, 3)

    # 構造直線 ax+by+c=0，其中 a,b 來自畢氏三元數
    pythagorean_triples = [(3, 4, 5), (5, 12, 13)]
    a, b, den = random.choice(pythagorean_triples)
    
    # 隨機決定關係
    relation = random.choice(['intersect', 'tangent', 'disjoint'])
    
    if relation == 'tangent': # d = r
        r = random.randint(2, 5)
        # |a*h + b*k + c| / den = r => |a*h + b*k + c| = r * den
        c = r * den - (a*h + b*k)
        correct_answer = "相切"
    elif relation == 'intersect': # d < r
        r = random.randint(3, 6)
        c = random.randint(-5, 5) # 隨意給 c，讓 d < r 的機率較高
        correct_answer = "相交兩點"
    else: # disjoint, d > r
        r = random.randint(1, 3)
        c = (r + random.randint(1,3)) * den - (a*h + b*k) # 讓 d > r
        correct_answer = "不相交"

    line_eq = f"{a}x + {b}y + {c} = 0".replace("+-", "-")
    question_text = f"請問圓 C: (x-{h})² + (y-{k})² = {r**2} 與直線 L: {line_eq} 的關係為何？ (相交兩點、相切、不相交)"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    is_correct = (user == correct_answer)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}