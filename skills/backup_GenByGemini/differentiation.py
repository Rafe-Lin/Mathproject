import random

def generate_differentiation_question():
    """動態生成一道「微分」的題目 (求多項式函數的導數)"""
    # f(x) = ax^2 + bx + c
    # f'(x) = 2ax + b
    
    a = random.randint(-3, 3)
    b = random.randint(-5, 5)
    c = random.randint(-9, 9)
    
    # 確保不是常數函數
    while a == 0 and b == 0:
        a = random.randint(-3, 3)
        b = random.randint(-5, 5)
        
    question_text = f"請問函數 f(x) = {a}x^2 + {b}x + {c} 的導數 f'(x) 是多少？ (請以 ax+b 的形式回答)"
    
    # 格式化答案
    terms = []
    if 2*a != 0:
        terms.append(f"{2*a}x")
    if b != 0:
        if b > 0 and terms:
            terms.append(f" + {b}")
        elif b < 0 and terms:
            terms.append(f" - {abs(b)}")
        else:
            terms.append(str(b))
            
    if not terms:
        answer = "0"
    else:
        answer = "".join(terms)
        
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }
