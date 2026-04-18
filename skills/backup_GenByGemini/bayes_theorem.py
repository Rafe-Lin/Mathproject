import random

def generate_bayes_theorem_question():
    """動態生成一道「貝氏定理」的題目 (簡化版)"""
    # 假設情境：某疾病的盛行率和檢測的準確性
    # P(D) = 疾病盛行率
    # P(pos|D) = 檢測結果為陽性，且確實有病 (真陽性率)
    # P(pos|not D) = 檢測結果為陽性，但沒有病 (偽陽性率)
    # 求 P(D|pos) = P(pos|D) * P(D) / P(pos)
    # P(pos) = P(pos|D) * P(D) + P(pos|not D) * P(not D)
    
    # 為了簡化，我們使用容易計算的數字
    p_d = 0.01 # 疾病盛行率 1%
    p_pos_given_d = 0.95 # 真陽性率 95%
    p_pos_given_not_d = 0.10 # 偽陽性率 10%
    
    p_not_d = 1 - p_d
    p_pos = (p_pos_given_d * p_d) + (p_pos_given_not_d * p_not_d)
    p_d_given_pos = (p_pos_given_d * p_d) / p_pos
    
    question_text = (
        f"某種疾病的盛行率為 {p_d*100:.0f}%。"
        f"一種檢測方法對有病的人有 {p_pos_given_d*100:.0f}% 的機率呈現陽性，"
        f"對沒病的人有 {p_pos_given_not_d*100:.0f}% 的機率呈現陽性。"
        f"如果一個人的檢測結果為陽性，請問他確實有病的機率是多少？ (請四捨五入到小數點後兩位)"
    )
    answer = f"{p_d_given_pos:.2f}"
    
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }
