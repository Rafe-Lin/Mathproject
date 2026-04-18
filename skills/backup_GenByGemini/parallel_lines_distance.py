import random
import math

def generate(level=1):
    """
    生成一道「兩平行線距離」的題目。
    level 1: 係數為整數，答案為整數。
    level 2: 係數為整數，答案可能為分數。
    """
    # 從畢氏三元數中選 a, b 確保分母為整數
    pythagorean_triples = [(3, 4, 5), (5, 12, 13), (8, 15, 17)]
    a, b, den = random.choice(pythagorean_triples)
    a = random.choice([a, -a])
    b = random.choice([b, -b])
    
    c1 = random.randint(-10, 10)
    
    if level == 1:
        # 讓答案為整數
        dist = random.randint(1, 5)
        # |c1 - c2| / sqrt(a^2+b^2) = dist
        # |c1 - c2| = dist * den
        c_diff = dist * den
        c2 = c1 + random.choice([c_diff, -c_diff])
    else: # level 2
        c2 = random.randint(-10, 10)
        while c1 == c2: c2 = random.randint(-10, 10)

    line1_eq = f"{a}x + {b}y + {c1} = 0".replace("+-", "-")
    line2_eq = f"{a}x + {b}y + {c2} = 0".replace("+-", "-")
    question_text = f"請求出兩平行線 L1: {line1_eq} 與 L2: {line2_eq} 的距離。"
    
    dist_num = abs(c1 - c2)
    dist_den = math.sqrt(a**2 + b**2)
    correct_answer = str(int(dist_num / dist_den))

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}