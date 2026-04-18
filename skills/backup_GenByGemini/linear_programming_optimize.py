# \線性規劃\線性規劃 (最佳解)
import random

# 建議：使用常數來增加可讀性
MIN_COEFF, MAX_COEFF = 1, 3
MIN_TARGET_COEFF, MAX_TARGET_COEFF = 1, 10

def generate(level=1):
    """
    生成一道「線性規劃 (最佳解)」的題目。
    """
    # 生成不等式組，定義可行解區域
    # 為了簡化，使用一個三角形區域: x ≥ 0, y ≥ 0, ax + by ≤ c
    a = random.randint(MIN_COEFF, MAX_COEFF)
    b = random.randint(MIN_COEFF, MAX_COEFF)
    # 確保 c 是 a 和 b 的公倍數，讓頂點是整數
    c_val = a * b * random.randint(3, 6)

    inequalities_str = f"x ≥ 0, y ≥ 0, {a}x + {b}y ≤ {c_val}"
    
    # 可行解區域的頂點
    vertices = [
        (0, 0),
        (c_val // a, 0),
        (0, c_val // b)
    ]
    
    # 生成目標函數 f(x, y) = px + qy
    p = random.randint(MIN_TARGET_COEFF, MAX_TARGET_COEFF)
    q = random.randint(MIN_TARGET_COEFF, MAX_TARGET_COEFF)
    objective_func_str = f"f(x, y) = {p}x + {q}y"
    
    # 計算各頂點的目標函數值
    values = [p*x + q*y for x, y in vertices]
    
    if level == 1:
        question_text = f"在可行解區域 {inequalities_str} 中，求目標函數 {objective_func_str} 的「最大值」。"
        correct_answer = str(max(values))
    else: # level 2
        question_text = f"在可行解區域 {inequalities_str} 中，求目標函數 {objective_func_str} 的「最小值」。"
        correct_answer = str(min(values))
        
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}