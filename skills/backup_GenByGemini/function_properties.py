import random

def generate_function_properties_question():
    """動態生成一道「函數性質的判定」的題目 (判斷奇偶函數)"""
    # 偶函數: f(x) = f(-x) (只有偶次項)
    # 奇函數: f(x) = -f(-x) (只有奇次項)
    # 兩者皆非: 混合奇偶次項
    
    func_type = random.choice(['even', 'odd', 'neither'])
    coeffs = [0, 0, 0, 0] # x^3, x^2, x^1, x^0
    
    if func_type == 'even':
        coeffs[1] = random.randint(1, 5) # x^2
        coeffs[3] = random.randint(1, 5) # constant
        question_text = f"請問函數 f(x) = {coeffs[1]}x^2 + {coeffs[3]} 是奇函數、偶函數還是兩者皆非？"
        answer = "偶函數"
    elif func_type == 'odd':
        coeffs[0] = random.randint(1, 5) # x^3
        coeffs[2] = random.randint(1, 5) # x^1
        question_text = f"請問函數 f(x) = {coeffs[0]}x^3 + {coeffs[2]}x 是奇函數、偶函數還是兩者皆非？"
        answer = "奇函數"
    else: # neither
        coeffs[0] = random.randint(1, 5) # x^3
        coeffs[1] = random.randint(1, 5) # x^2
        coeffs[3] = random.randint(1, 5) # constant
        question_text = f"請問函數 f(x) = {coeffs[0]}x^3 + {coeffs[1]}x^2 + {coeffs[3]} 是奇函數、偶函數還是兩者皆非？"
        answer = "兩者皆非"
        
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }
