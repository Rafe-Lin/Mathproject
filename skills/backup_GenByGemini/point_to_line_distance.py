import random
import math

def generate(level=1):
    """
    生成一道「點到直線距離」的題目。
    level 1: 係數為整數，答案為整數。
    level 2: 係數為整數，答案可能為分數。
    """
    # 從畢氏三元數中選 a, b 確保分母為整數
    pythagorean_triples = [(3, 4, 5), (5, 12, 13), (8, 15, 17)]
    a, b, den = random.choice(pythagorean_triples)
    a = random.choice([a, -a])
    b = random.choice([b, -b])
    
    px, py = random.randint(-5, 5), random.randint(-5, 5)
    
    if level == 1:
        # 讓答案為整數
        dist = random.randint(1, 5)
        # |a*px + b*py + c| / sqrt(a^2+b^2) = dist
        # |a*px + b*py + c| = dist * den
        target_num = dist * den
        current_num = a*px + b*py
        c = random.choice([target_num, -target_num]) - current_num
    else: # level 2
        c = random.randint(-10, 10)

    line_eq = f"{a}x + {b}y + {c} = 0".replace("+-", "-")
    question_text = f"請求出點 P({px}, {py}) 到直線 L: {line_eq} 的距離。"
    
    dist_num = abs(a*px + b*py + c)
    dist_den = math.sqrt(a**2 + b**2)
    correct_answer = str(int(dist_num / dist_den))

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}