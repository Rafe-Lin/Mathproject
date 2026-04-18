import random
from fractions import Fraction

def generate(level=1):
    """
    生成「等差級數求和」相關題目。
    包含：
    1. 已知級數首末兩項，求級數項數。
    2. 已知級數首末兩項，求級數和 (須先求出項數)。
    3. 已知級數首兩項與項數，求級數和。
    4. 已知首項、項數與級數和，求公差。
    """
    problem_type = random.choice([
        'find_n_from_series_start_end',
        'find_sum_from_series_start_end',
        'find_sum_from_series_start_n',
        'find_d_given_a1_n_sn'
    ])
    
    if problem_type == 'find_n_from_series_start_end':
        return generate_find_n_from_series_start_end()
    elif problem_type == 'find_sum_from_series_start_end':
        return generate_find_sum_from_series_start_end()
    elif problem_type == 'find_sum_from_series_start_n':
        return generate_find_sum_from_series_start_n()
    else: # find_d_given_a1_n_sn
        return generate_find_d_given_a1_n_sn()

def generate_find_n_from_series_start_end():
    """
    題型：已知級數首末兩項，求級數項數。
    例如：已知等差級數 8＋15＋22＋……＋92，此級數共有幾項？
    使用者需要先根據 a1, a2 算出公差 d，再用 an = a1 + (n-1)d 反解出 n。
    """
    a1 = random.randint(-30, 30)
    d = random.choice([i for i in range(-10, 11) if i != 0])
    n = random.randint(7, 25)
    
    a2 = a1 + d
    an = a1 + (n - 1) * d
    
    # 格式化顯示，負數加括號
    terms_to_display = [a1, a2, an]
    term_strs = []
    for t in terms_to_display:
        term_strs.append(f"({t})" if t < 0 else str(t))
        
    series_display = f"{term_strs[0]} + {term_strs[1]} + \\dots + {term_strs[2]}"
    
    question_text = f"請問等差級數 ${series_display}$ 共有幾項？"
    correct_answer = str(n)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_find_sum_from_series_start_end():
    """
    題型：已知級數首末兩項，求級數和。
    例如：求等差級數 8＋15＋22＋……＋92 的和。
    使用者需要先根據 a1, a2, an 算出公差 d 和項數 n，再求和 Sn。
    """
    a1 = random.randint(-30, 30)
    d = random.choice([i for i in range(-10, 11) if i != 0])
    n = random.randint(7, 25)
    
    a2 = a1 + d
    an = a1 + (n - 1) * d
    
    # 公式 Sn = n * (a1 + an) / 2
    sn = n * (a1 + an) // 2
    
    # 格式化顯示，負數加括號
    terms_to_display = [a1, a2, an]
    term_strs = []
    for t in terms_to_display:
        term_strs.append(f"({t})" if t < 0 else str(t))
        
    series_display = f"{term_strs[0]} + {term_strs[1]} + \\dots + {term_strs[2]}"
    
    question_text = f"求等差級數 ${series_display}$ 的和。"
    correct_answer = str(sn)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_find_sum_from_series_start_n():
    """
    題型：已知級數首兩項與項數，求級數和。
    例如：已知等差級數 -4＋2＋8＋⋯⋯，求此等差級數前 8 項的和。
    使用者需要先根據 a1, a2 算出公差 d，再用公式 Sn = n[2a1+(n-1)d]/2 求和。
    """
    a1 = random.randint(-20, 20)
    d = random.choice([i for i in range(-8, 9) if i != 0])
    n = random.randint(6, 20)
    
    a2 = a1 + d
    
    # 公式 Sn = n * (2*a1 + (n-1)*d) / 2
    sn = n * (2 * a1 + (n - 1) * d) // 2
    
    # 格式化顯示，負數加括號
    terms_to_display = [a1, a2]
    term_strs = []
    for t in terms_to_display:
        term_strs.append(f"({t})" if t < 0 else str(t))
        
    series_display = f"{term_strs[0]} + {term_strs[1]} + \\dots"
    
    question_text = f"已知一等差級數為 ${series_display}$，求此級數前 ${n}$ 項的和。"
    correct_answer = str(sn)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_find_d_given_a1_n_sn():
    """
    題型：已知首項、項數與級數和，求公差。
    例如：若等差級數的首項為 5，前 10 項的和為 365，則公差為多少？
    使用者需要根據 a1, n, Sn 反解出公差 d。
    """
    # 為了確保 d 為整數，我們先生成 a1, d, n，再算出 Sn
    a1 = random.randint(-15, 15)
    d = random.choice([i for i in range(-9, 10) if i != 0])
    n = random.randint(5, 20)
    
    # 計算對應的和
    sn = n * (2 * a1 + (n - 1) * d) // 2
    
    # 格式化顯示，負數加括號
    a1_disp = f"({a1})" if a1 < 0 else str(a1)
    sn_disp = f"({sn})" if sn < 0 else str(sn)
    
    question_text = f"若一等差級數的首項為 ${a1_disp}$，前 ${n}$ 項的和為 ${sn_disp}$，則公差為多少？"
    correct_answer = str(d)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip().upper()
    correct_answer = correct_answer.strip().upper()
    
    is_correct = (user_answer == correct_answer)
    
    if not is_correct:
        try:
            if float(user_answer) == float(correct_answer):
                is_correct = True
        except ValueError:
            pass

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}