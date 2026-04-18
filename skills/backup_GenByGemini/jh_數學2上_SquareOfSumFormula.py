import random

def generate(level=1):
    """
    生成「和的平方公式」相關題目。
    包含：
    1. 正向應用：利用 (a+b)^2 = a^2+2ab+b^2 計算 n^2
    2. 反向應用：利用 a^2+2ab+b^2 = (a+b)^2 計算特定運算式
    """
    problem_type = random.choice(['forward', 'reverse'])
    
    if problem_type == 'forward':
        return generate_forward_problem()
    else: # reverse
        return generate_reverse_problem()

def generate_forward_problem():
    """
    生成正向應用題目：利用 (a+b)^2 = a^2+2ab+b^2 計算 n^2
    例題: 計算 504^2
    """
    # 選擇一個接近整十或整百的數字
    # a 是整數部分, b 是尾數部分
    base_magnitude = random.choice([10, 100])
    a = random.randint(1, 9) * base_magnitude
    b = random.randint(1, 9)

    number_to_square = a + b
    answer = number_to_square ** 2

    question_text = f"利用和的平方公式 $(a+b)^2 = a^2+2ab+b^2$，計算 ${number_to_square}^2$ 的值。"
    correct_answer = str(answer)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_reverse_problem():
    """
    生成反向應用題目：利用 a^2+2ab+b^2 = (a+b)^2 計算
    例題: 計算 45^2 + 2*45*5 + 5^2
    """
    # 選擇 a 和 b，使其和為一個漂亮的數字 (整十)
    total_sum = random.randint(3, 15) * 10  # 30, 40, ..., 150
    
    # 選擇 a，讓 b 自然產生，並避免 a 或 b 過於簡單
    # 設定一個較寬的初始範圍
    min_a_candidate = 11
    max_a_candidate = total_sum - 11

    # 如果 total_sum 太小，導致範圍無效，則使用備用範圍
    if min_a_candidate >= max_a_candidate:
        min_a_candidate = total_sum // 4
        max_a_candidate = total_sum * 3 // 4
        # 確保範圍至少有1個數字
        if min_a_candidate > max_a_candidate:
            min_a_candidate = max_a_candidate

    a = random.randint(min_a_candidate, max_a_candidate)
    
    # 避免 a=b
    if a == total_sum / 2:
        a += random.choice([-2, -1, 1, 2])
        # 確保 a 仍在合理範圍內
        a = max(1, min(total_sum - 1, a))

    b = total_sum - a

    # 隨機交換 a 和 b，增加題目變化
    if random.random() < 0.5:
        a, b = b, a

    answer = total_sum ** 2

    # LaTeX 中乘號要用 \\times
    question_text = f"利用和的平方公式 $a^2+2ab+b^2 = (a+b)^2$，計算 ${a}^2+2 \\times {a} \\times {b}+{b}^2$ 的值。"
    correct_answer = str(answer)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    
    is_correct = (user_answer == correct_answer)
    
    # 為了處理可能的浮點數或格式差異，再次檢查數值是否相等
    if not is_correct:
        try:
            if float(user_answer) == float(correct_answer):
                is_correct = True
        except (ValueError, TypeError):
            # 如果無法轉換為數字，則保持 is_correct 的原值
            pass

    if is_correct:
        result_text = f"完全正確！答案是 ${correct_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer}$"
    
    return {"correct": is_correct, "result": result_text, "next_question": True}