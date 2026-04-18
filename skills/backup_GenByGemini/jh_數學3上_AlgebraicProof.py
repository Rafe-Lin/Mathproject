import random
import re

def generate(level=1):
    """
    生成「代數證明」相關題目。
    包含：
    1. 奇偶數性質證明 (填空)
    2. 代數式奇偶性判斷
    3. 倍數證明 (填空)
    4. 不等式證明 (填空)
    """
    problem_type = random.choice([
        'odd_even_properties', 
        'classify_expression', 
        'multiples_proof', 
        'inequality_proof'
    ])
    
    if problem_type == 'odd_even_properties':
        return generate_odd_even_properties_problem()
    elif problem_type == 'classify_expression':
        return generate_classify_expression_problem()
    elif problem_type == 'multiples_proof':
        return generate_multiples_proof_problem()
    else: # inequality_proof
        return generate_inequality_proof_problem()

def generate_odd_even_properties_problem():
    """
    生成奇偶數運算性質的證明填空題。
    """
    ops = [
        ('奇數', '+', '奇數', '偶數'),
        ('奇數', '+', '偶數', '奇數'),
        ('偶數', '+', '偶數', '偶數'),
        ('奇數', '\\times', '奇數', '奇數'),
        ('奇數', '\\times', '偶數', '偶數'),
        ('偶數', '\\times', '偶數', '偶數')
    ]
    t1_str, op_str, t2_str, res_str = random.choice(ops)
    
    op_desc = '相加' if op_str == '+' else '相乘'
    
    a_def = "$a=2m+1$" if t1_str == '奇數' else "$a=2m$"
    b_def = "$b=2n+1$" if t2_str == '奇數' else "$b=2n$"
    
    question_text = f"請完成以下關於「一個{t1_str}和一個{t2_str}{op_desc}的結果是{res_str}」的證明：<br>"
    question_text += f"設 a 為{t1_str}，b 為{t2_str}，可表示為 {a_def}、{b_def} (其中 m, n 為整數)。<br>"
    
    if op_str == '+':
        if t1_str == '奇數' and t2_str == '奇數':
            expr = "a+b = (2m+1)+(2n+1) = 2m+2n+2 = 2(\\underline{ \\quad ? \\quad })"
            blank_ans = "m+n+1"
        elif (t1_str == '奇數' and t2_str == '偶數') or (t1_str == '偶數' and t2_str == '奇數'):
            expr = "a+b = 2m+(2n+1) = 2m+2n+1 = 2(\\underline{ \\quad ? \\quad })+1"
            blank_ans = "m+n"
        else: # even + even
            expr = "a+b = 2m+2n = 2(\\underline{ \\quad ? \\quad })"
            blank_ans = "m+n"
    else: # multiplication
        if t1_str == '奇數' and t2_str == '奇數':
            expr = f"a {op_str} b = (2m+1)(2n+1) = 4mn+2m+2n+1 = 2(\\underline{{ \\quad ? \\quad }})+1"
            blank_ans = "2mn+m+n"
        elif t1_str == '奇數' and t2_str == '偶數':
            expr = f"a {op_str} b = (2m+1)(2n) = 4mn+2n = 2(\\underline{{ \\quad ? \\quad }})"
            blank_ans = "2mn+n"
        elif t1_str == '偶數' and t2_str == '奇數':
             expr = f"a {op_str} b = (2m)(2n+1) = 4mn+2m = 2(\\underline{{ \\quad ? \\quad }})"
             blank_ans = "2mn+m"
        else: # even * even
            expr = f"a {op_str} b = (2m)(2n) = 4mn = 2(\\underline{{ \\quad ? \\quad }})"
            blank_ans = "2mn"
            
    question_text += f"則 ${expr}$<br>"
    question_text += "請問空格中應填入什麼代數式？ (變數請依 m, n 順序填寫)"
    
    return {
        "question_text": question_text,
        "answer": blank_ans,
        "correct_answer": blank_ans
    }

def generate_classify_expression_problem():
    """
    生成判斷代數式奇偶性的問題。
    """
    c1 = random.randint(2, 5)
    c2 = random.randint(2, 10)
    
    expr_str = f"{c1}a + {c2}"
    
    if c1 % 2 == 0:
        if c2 % 2 == 0:
            correct_answer = "偶數"
        else:
            correct_answer = "奇數"
    else:
        correct_answer = "都有可能"
        
    question_text = f"已知 a 是整數，判斷下列式子所代表的數是「奇數」、「偶數」或「都有可能」？<br>${expr_str}$"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_multiples_proof_problem():
    """
    生成利用乘法公式證明倍數的填空題。
    """
    c = random.randint(2, 5)
    
    # Template: prove (k+c)^2 - (k-c)^2 is a multiple of 4c
    # (k+c)^2 - (k-c)^2 = ((k+c)+(k-c)) * ((k+c)-(k-c)) = (2k)(2c) = 4ck
    k_term_1 = f"(k+{c})^2"
    k_term_2 = f"(k-{c})^2"
    multiple_val = 4 * c
    
    if random.random() < 0.5:
        expr = f"( \\underline{{ \\quad ? \\quad }} ) (2c)"
        blank_ans = "2k"
    else:
        expr = f"(2k) ( \\underline{{ \\quad ? \\quad }} )"
        blank_ans = f"2c"
        
    question_text = f"請完成證明「${k_term_1} - {k_term_2}$ 為 ${multiple_val}$ 的倍數」的關鍵步驟：<br>"
    question_text += "利用平方差公式 $a^2 - b^2 = (a+b)(a-b)$，<br>"
    question_text += f"${k_term_1} - {k_term_2} = ( (k+{c}) + (k-{c}) ) ( (k+{c}) - (k-{c}) )$<br>"
    question_text += f"$ = {expr} $<br>"
    question_text += f"$ = {multiple_val}k $<br>"
    question_text += f"因為 k 為整數，所以 ${multiple_val}k$ 為 ${multiple_val}$ 的倍數。<br>"
    question_text += "請問空格中應填入什麼？"
    
    return {
        "question_text": question_text,
        "answer": blank_ans,
        "correct_answer": blank_ans
    }
    
def generate_inequality_proof_problem():
    """
    生成利用乘法公式證明不等式的填空題。
    """
    if random.random() < 0.5:
        # Prove a>b -> a^2>b^2, given a,b > 0
        blanks = [
            {"part": "a+b", "answer": "正數", "reason": "因為 a、b 為正數"},
            {"part": "a-b", "answer": "正數", "reason": "因為已知 a > b"},
            {"part": "(a+b)(a-b)", "answer": "正數", "reason": "因為正數乘以正數的結果為正數"}
        ]
        chosen_blank = random.choice(blanks)
        
        question_text = "已知 a、b 為正數，且 a > b，請完成 $a^2 > b^2$ 的證明過程。<br>"
        question_text += "欲證明 $a^2 > b^2$，等同於證明 $a^2 - b^2 > 0$。<br>"
        question_text += "利用平方差公式：$a^2-b^2=(a+b)(a-b)$。<br>"
        question_text += f"{chosen_blank['reason']}，所以 $( {chosen_blank['part']} )$ 的結果為？ (請填 正數、負數 或 零)"
        correct_answer = chosen_blank['answer']
        
    else:
        # Prove a^2>b^2 -> a>b, given a,b > 0
        blanks = [
            {"part": "a+b", "answer": "正數", "reason": "因為 a、b 為正數"},
            {"part": "a-b", "answer": "正數", "reason": "因為 (a+b) 是正數，且兩數相乘 $(a+b)(a-b)$ 的結果為正數"}
        ]
        chosen_blank = random.choice(blanks)
        
        question_text = "已知 a、b 為正數，且 $a^2 > b^2$，請完成 $a > b$ 的證明過程。<br>"
        question_text += "因為 $a^2 > b^2$，所以 $a^2 - b^2 > 0$。<br>"
        question_text += "利用平方差公式：$a^2-b^2=(a+b)(a-b) > 0$。<br>"
        question_text += f"{chosen_blank['reason']}，所以可推得 $( {chosen_blank['part']} )$ 的結果為？ (請填 正數、負數 或 零)"
        correct_answer = chosen_blank['answer']

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    cleaned_user_answer = re.sub(r'\s+', '', user_answer).lower()
    cleaned_correct_answer = re.sub(r'\s+', '', correct_answer).lower()
    
    is_correct = (cleaned_user_answer == cleaned_correct_answer)
    
    # Allow for some flexibility in categorical answers
    categorical_answers = {
        "奇數": ["奇"],
        "偶數": ["偶"],
        "都有可能": ["都", "可能"],
        "正數": ["正"],
        "負數": ["負"],
        "零": ["零", "0"]
    }
    
    for key, synonyms in categorical_answers.items():
        if correct_answer == key:
            for syn in synonyms:
                if syn in user_answer:
                    is_correct = True
                    break
    
    if is_correct:
        result_text = f"完全正確！答案是 ${correct_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer}$"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}