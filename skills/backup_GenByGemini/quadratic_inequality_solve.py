import random

def generate(level=1):
    """
    生成一道「二次不等式求解」的題目。
    level 1: 可分解為 (x-a)(x-b)，根為整數。
    level 2: 判別式 D<0 或 D=0 的情況。
    """
    a_coeff = random.choice([-1, 1])
    
    if level == 1: # D > 0
        r1, r2 = random.sample(range(-5, 6), 2)
        # (x-r1)(x-r2) = x² - (r1+r2)x + r1r2
        b, c = -(r1+r2), r1*r2
        b, c = b*a_coeff, c*a_coeff
        op = random.choice(['>', '<', '>=', '<='])
        
        sol_outside = (a_coeff > 0 and op in ['>','>=']) or (a_coeff < 0 and op in ['<','<='])
        if sol_outside:
            correct_answer = f"x >= {max(r1,r2)} 或 x <= {min(r1,r2)}"
        else:
            correct_answer = f"{min(r1,r2)} <= x <= {max(r1,r2)}"
        correct_answer = correct_answer.replace(">= "," > ").replace("<= "," < ") if op in ['>','<'] else correct_answer
    else: # D <= 0
        h = random.randint(-3, 3)
        k = random.randint(0, 4) if a_coeff > 0 else random.randint(-4, 0) # a*k >= 0
        b, c = -2*a_coeff*h, a_coeff*h**2 + k
        op = random.choice(['>', '<', '>=', '<='])
        
        if k == 0: # D=0
            correct_answer = "所有實數" if (a_coeff > 0 and op in ['>=']) or (a_coeff < 0 and op in ['<=']) else f"x={h}" if (a_coeff > 0 and op == '<=') or (a_coeff < 0 and op == '>=') else "無解"
        else: # D<0
            correct_answer = "所有實數" if (a_coeff > 0 and op in ['>','>=']) or (a_coeff < 0 and op in ['<','<=']) else "無解"

    a_str = "" if a_coeff == 1 else "- " if a_coeff == -1 else f"{a_coeff}"
    b_str = "" if b == 0 else f" + {b}x" if b > 0 else f" - {abs(b)}x"
    c_str = "" if c == 0 else f" + {c}" if c > 0 else f" - {abs(c)}"
    func_str = f"{a_str}x²{b_str}{c_str}"

    question_text = f"請求解二次不等式：{func_str} {op} 0"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip().replace(" ", "")
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}