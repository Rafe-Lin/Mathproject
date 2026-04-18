# \複數\一元二次方程式 (虛根)
import random
import cmath

def generate(level=1):
    """
    生成一道「一元二次方程式 (虛根)」的題目。
    """
    if level == 1:
        # (x-a)² = -k² => x²-2ax+a²+k²=0
        a = random.randint(1, 5)
        k = random.randint(1, 5)
        b, c = -2*a, a*a + k*k
    else: # level 2
        a = random.randint(2, 4)
        b = random.randint(1, 5)
        c = random.randint(b*b, b*b + 10) # 確保 D < 0
        
    question_text = f"請求解一元二次方程式：{a}x² + {b}x + {c} = 0。(格式: a+bi,a-bi)"
    
    d = (b**2) - 4*a*c
    sol1 = (-b - cmath.sqrt(d)) / (2*a)
    sol2 = (-b + cmath.sqrt(d)) / (2*a)
    
    correct_answer = f"{sol1:.2f},{sol2:.2f}".replace("j","i")
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user_parts = sorted(user_answer.strip().replace(" ", "").split(','))
    correct_parts = sorted(correct_answer.strip().split(','))
    is_correct = (user_parts == correct_parts)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}