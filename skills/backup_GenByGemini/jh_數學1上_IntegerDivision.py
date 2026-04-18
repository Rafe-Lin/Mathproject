import random

def _make_divisible_pair(level):
    """
    生成一個可整除的數字對 (被除數, 除數, 商)，數字大小根據 level 決定。
    """
    if level == 1:
        # 較小的數字，結果在 2~12 之間
        quotient = random.randint(2, 12)
        divisor = random.randint(2, 9)
    elif level == 2:
        # 中等數字，結果在 5~20 之間
        quotient = random.randint(5, 20)
        divisor = random.randint(2, 15)
    else:  # level 3 或更高
        # 較大的數字，結果在 10~30 之間
        quotient = random.randint(10, 30)
        divisor = random.randint(10, 25)

    dividend = quotient * divisor
    return dividend, divisor, quotient

def generate_neg_div_pos_problem(level):
    """
    生成「負數 ÷ 正數」的題目。
    範例: (-63) ÷ 7 = -9
    """
    dividend, divisor, quotient = _make_divisible_pair(level)

    signed_dividend = -dividend
    signed_divisor = divisor

    question_text = f"計算 $({signed_dividend}) \\div {signed_divisor}$ 的值。"
    correct_answer = str(-quotient)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_pos_div_neg_problem(level):
    """
    生成「正數 ÷ 負數」的題目。
    範例: 256 ÷ (-16) = -16
    """
    dividend, divisor, quotient = _make_divisible_pair(level)

    signed_dividend = dividend
    signed_divisor = -divisor

    question_text = f"計算 ${signed_dividend} \\div ({signed_divisor})$ 的值。"
    correct_answer = str(-quotient)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_neg_div_neg_problem(level):
    """
    生成「負數 ÷ 負數」的題目。
    範例: (-72) ÷ (-6) = 12
    """
    dividend, divisor, quotient = _make_divisible_pair(level)

    signed_dividend = -dividend
    signed_divisor = -divisor

    question_text = f"計算 $({signed_dividend}) \\div ({signed_divisor})$ 的值。"
    correct_answer = str(quotient)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_zero_div_problem(level):
    """
    生成「0 ÷ 非零數」的題目。
    範例: 0 ÷ (-5) = 0
    """
    if level == 1:
        divisor = random.randint(2, 20)
    else:
        divisor = random.randint(21, 99)

    if random.random() < 0.5:
        divisor = -divisor

    # 確保除數為負數時被括號包圍
    divisor_str = f"({divisor})" if divisor < 0 else str(divisor)
    
    question_text = f"計算 $0 \\div {divisor_str}$ 的值。"
    correct_answer = "0"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    生成「整數的除法」相關題目。
    技能：jh_數學1上_IntegerDivision
    題型包含：
    1. 負數 ÷ 正數 (同號數相除為負)
    2. 正數 ÷ 負數 (異號數相除為負)
    3. 負數 ÷ 負數 (同號數相除為正)
    4. 0 的除法 (0 除以任何非零數為 0)
    """
    problem_generators = [
        generate_neg_div_pos_problem,
        generate_pos_div_neg_problem,
        generate_neg_div_neg_problem,
        generate_zero_div_problem
    ]

    chosen_generator = random.choice(problem_generators)
    return chosen_generator(level)

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()

    is_correct = (user_answer == correct_answer)

    if is_correct:
        result_text = f"完全正確！答案是 ${correct_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer}$。"

    return {"correct": is_correct, "result": result_text, "next_question": True}
