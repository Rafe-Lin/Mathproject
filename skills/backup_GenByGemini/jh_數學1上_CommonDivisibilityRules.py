import random

def is_divisible(n, d):
    """
    Helper function to check if a number n is divisible by d.
    Handles divisibility rules for 2, 3, 4, 5, 9, 11.
    """
    try:
        num = int(n)
    except (ValueError, TypeError):
        return False
        
    if d == 2:
        return num % 2 == 0
    if d == 5:
        return num % 5 == 0
    if d == 3:
        return sum(int(digit) for digit in str(num)) % 3 == 0
    if d == 9:
        return sum(int(digit) for digit in str(num)) % 9 == 0
    if d == 4:
        if len(str(num)) < 2:
            return num % 4 == 0
        return int(str(num)[-2:]) % 4 == 0
    if d == 11:
        s = str(num)
        odd_sum = sum(int(digit) for digit in s[::-1][0::2])
        even_sum = sum(int(digit) for digit in s[::-1][1::2])
        return abs(odd_sum - even_sum) % 11 == 0
    return False

def generate_judgment_problem():
    """
    題型：判斷一個數是否為某數的倍數。
    例如：「判斷 201798 是不是 4 的倍數？」
    """
    divisor = random.choice([2, 3, 4, 5, 9, 11])
    should_be_divisible = random.choice([True, False])

    num = 0
    if should_be_divisible:
        # Construct a number that IS a multiple
        base = random.randint(1000, 99999)
        if divisor == 11:
            num = random.randint(1000, 90000) * 11
        elif divisor == 9:
            s = sum(int(d) for d in str(base))
            last_digit = (9 - (s % 9)) % 9
            num = base * 10 + last_digit
        elif divisor == 3:
            s = sum(int(d) for d in str(base))
            last_digit = (3 - (s % 3)) % 3
            num = base * 10 + last_digit
        elif divisor == 4:
            last_two = random.randint(0, 24) * 4
            num = base * 100 + last_two
        elif divisor == 5:
            num = base * 10 + random.choice([0, 5])
        elif divisor == 2:
            num = base * 10 + random.choice([0, 2, 4, 6, 8])
    else:
        # Construct a number that IS NOT a multiple
        while True:
            num = random.randint(10000, 999999)
            if not is_divisible(num, divisor):
                break

    question_text = f"判斷 $ {num} $ 是不是 $ {divisor} $ 的倍數？ (請回答「是」或「不是」)"
    correct_answer = "是" if should_be_divisible else "不是"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_fill_blank_problem():
    """
    題型：填空使數字符合倍數規則。
    例如：「已知五位數 9176□ 是 4 的倍數,則□中可填入的數為何？」
    """
    divisor = random.choice([3, 4, 9, 11])
    num_digits = random.randint(4, 6)
    digits = [random.randint(1, 9)] + [random.randint(0, 9) for _ in range(num_digits - 1)]
    
    # For rule of 4, the blank must be in the last two digits.
    if divisor == 4:
        blank_pos = random.choice([num_digits - 2, num_digits - 1])
    else:
        blank_pos = random.randint(1, num_digits - 1)

    solutions = []

    if divisor == 3 or divisor == 9:
        known_digits_sum = sum(d for i, d in enumerate(digits) if i != blank_pos)
        for i in range(10):
            if blank_pos == 0 and i == 0:
                continue
            if (known_digits_sum + i) % divisor == 0:
                solutions.append(str(i))
    
    elif divisor == 4:
        if blank_pos == num_digits - 1: # ...X□
            tens_digit = digits[num_digits - 2]
            for i in range(10):
                if (tens_digit * 10 + i) % 4 == 0:
                    solutions.append(str(i))
        else: # ...□X
            ones_digit = digits[num_digits - 1]
            for i in range(10):
                if blank_pos == 0 and i == 0:
                    continue
                if (i * 10 + ones_digit) % 4 == 0:
                    solutions.append(str(i))

    elif divisor == 11:
        odd_sum, even_sum = 0, 0
        for i in range(num_digits):
            if i == blank_pos:
                continue
            pos_from_right = num_digits - i
            if pos_from_right % 2 == 1: odd_sum += digits[i]
            else: even_sum += digits[i]
        
        blank_pos_from_right = num_digits - blank_pos
        for i in range(10):
            if blank_pos == 0 and i == 0:
                continue
            
            diff = 0
            if blank_pos_from_right % 2 == 1: # blank in odd position
                diff = abs((odd_sum + i) - even_sum)
            else: # blank in even position
                diff = abs(odd_sum - (even_sum + i))
            
            if diff % 11 == 0:
                solutions.append(str(i))

    if not solutions:
        return generate_fill_blank_problem()

    display_digits = [str(d) for d in digits]
    display_digits[blank_pos] = "□"
    number_str = "".join(display_digits)
    
    question_text = f"已知{num_digits}位數 $ {number_str} $ 是 $ {divisor} $ 的倍數，則□中可填入的數為何？ (若有多個答案，請用逗號分隔)"
    correct_answer = ",".join(sorted(solutions))
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_combined_fill_blank_problem():
    """
    題型：填空使數字符合多個倍數規則。
    例如：「若五位數 9176□ 是 5 的倍數,也是 2 的倍數,則□中可填入的數為何？」
    """
    num_digits = random.randint(4, 6)
    base_num_str = "".join([random.choice('123456789')] + [random.choice('0123456789') for _ in range(num_digits - 2)])
    number_with_blank = base_num_str + "□"

    problem_type = random.choice(['2_and_5', '5_not_2'])

    if problem_type == '2_and_5':
        question_text = f"已知{num_digits}位數 $ {number_with_blank} $ 是 $ 2 $ 的倍數，也是 $ 5 $ 的倍數，則□中可填入的數為何？"
        correct_answer = "0"
    else: # '5_not_2'
        question_text = f"已知{num_digits}位數 $ {number_with_blank} $ 是 $ 5 $ 的倍數，但不是 $ 2 $ 的倍數，則□中可填入的數為何？"
        correct_answer = "5"
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_double_judgment_problem():
    """
    題型：同時判斷兩個數是否為某數的倍數。
    例如：「判斷 345345 和 37195 是不是 11 的倍數？」
    """
    divisor = random.choice([3, 4, 9, 11])
    
    num1, num2 = 0, 0
    is_div1, is_div2 = False, False

    while num1 == num2 or is_div1 == is_div2:
        # Generate num1
        while True:
            n1_candidate = random.randint(10000, 999999)
            if is_divisible(n1_candidate, divisor) != is_div1:
                num1 = n1_candidate
                break
        is_div1 = is_divisible(num1, divisor)
        
        # Flip the desired outcome for the second number
        is_div2_target = not is_div1
        # Generate num2
        while True:
            n2_candidate = random.randint(10000, 999999)
            if is_divisible(n2_candidate, divisor) == is_div2_target and n2_candidate != num1:
                num2 = n2_candidate
                break
        is_div2 = is_divisible(num2, divisor)
        
        # Final check to ensure they are different
        if is_div1 == is_div2:
            is_div1 = not is_div1 # Flip and try again

    ans1_text = "是" if is_div1 else "不是"
    ans2_text = "是" if is_div2 else "不是"

    question_text = f"分別判斷 $ {num1} $ 和 $ {num2} $ 是不是 $ {divisor} $ 的倍數？ (請依序回答，例如: 是,不是)"
    correct_answer = f"{ans1_text},{ans2_text}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    生成「因數與倍數 - 公倍數與公因數的判別法」相關題目。
    包含：
    1. 判斷題：判斷一個數是否為 2, 3, 4, 5, 9, 11 的倍數。
    2. 雙重判斷題：同時判斷兩個數。
    3. 填空題：數字中填入一個數，使其成為特定數的倍數。
    4. 複合條件填空題：滿足多個條件 (例如 2 和 5 的倍數)。
    """
    problem_type = random.choice([
        'judgment',
        'fill_blank',
        'combined_fill_blank',
        'double_judgment'
    ])
    
    if problem_type == 'judgment':
        return generate_judgment_problem()
    elif problem_type == 'fill_blank':
        return generate_fill_blank_problem()
    elif problem_type == 'combined_fill_blank':
        return generate_combined_fill_blank_problem()
    else:
        return generate_double_judgment_problem()

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    def normalize_answer(answer_str):
        """Helper to handle various user input formats."""
        s = answer_str.strip().replace('，', ',').replace(' ', '')
        if any(c in s for c in "是不是"):
            return s
        
        # For numeric lists, sort them for consistent comparison.
        parts = [part for part in s.split(',') if part.isdigit()]
        parts.sort()
        return ','.join(parts)

    user_answer_normalized = normalize_answer(user_answer)
    correct_answer_normalized = normalize_answer(correct_answer)
    
    is_correct = (user_answer_normalized == correct_answer_normalized)

    display_answer = correct_answer.replace(",", "、")

    result_text = f"完全正確！答案是 {display_answer}。" if is_correct else f"答案不正確。正確答案應為：{display_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}
