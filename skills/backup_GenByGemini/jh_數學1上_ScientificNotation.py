import random
import decimal

# Helper to format numbers without trailing zeros (e.g., 2.50 -> 2.5)
def format_number(n):
    d = decimal.Decimal(str(n))
    return d.normalize().to_eng_string()

def generate(level=1):
    """
    生成「科學記號」相關題目。
    包含：
    1. 將數字轉換為科學記號 (大數、小數、分數)
    2. 科學記號的性質判斷 (位數、小數點後第幾位)
    3. 科學記號的大小比較
    """
    problem_type = random.choice(['conversion', 'properties', 'comparison'])
    
    if problem_type == 'conversion':
        return generate_conversion_problem()
    elif problem_type == 'properties':
        return generate_properties_problem()
    else: # comparison
        return generate_comparison_problem()

def generate_conversion_problem():
    """
    題型：將給定的數轉換為科學記號。
    子題型：大整數、小數、分數形式。
    """
    sub_type = random.choice(['large_int', 'small_decimal', 'fraction'])
    
    if sub_type == 'large_int':
        # 產生一個大整數
        exponent = random.randint(4, 12)
        coeff = round(random.uniform(1, 9.999), random.randint(1, 3))
        number = int(coeff * (10**exponent))
        
        question_text = f"請以科學記號表示下列各數：\n$ {number:,} $\n(答案請以 a*10^n 的格式作答，例如 3.14*10^5)"
        
        # 重新計算精確的科學記號表示，以處理 coeff > 10 的情況
        exponent_ans = 0
        temp_num = float(number)
        while temp_num >= 10:
            temp_num /= 10
            exponent_ans += 1
        coeff_ans = format_number(temp_num)

        correct_answer = f"{coeff_ans}*10^{exponent_ans}"
        answer_display = f"${coeff_ans}\\times10^{{{exponent_ans}}}$"
        
    elif sub_type == 'small_decimal':
        # 產生一個純小數
        exponent = random.randint(4, 12)
        coeff = round(random.uniform(1, 9.999), random.randint(1, 3))

        # 使用 Decimal 以精確表示小數
        ctx = decimal.Context(prec=30)
        number_val = ctx.multiply(decimal.Decimal(str(coeff)), ctx.power(decimal.Decimal('10'), decimal.Decimal(f'-{exponent}')))
        # 格式化輸出，確保顯示足夠的小數位數
        number_str = f'{number_val:f}'

        question_text = f"請以科學記號表示下列各數：\n$ {number_str} $\n(答案請以 a*10^n 的格式作答，例如 2.7*10^-8)"
        correct_answer = f"{format_number(coeff)}*10^{-exponent}"
        answer_display = f"${format_number(coeff)}\\times10^{{{-exponent}}}$"
        
    else: # fraction
        # 產生一個分母為 10 的次方的分數
        numerator = random.randint(1, 9)
        exponent = random.randint(3, 9)
        denominator = 10**exponent
        
        question_text = f"請以科學記號表示下列各數：\n$ \\frac{{{numerator}}}{{{denominator:,}}} $\n(答案請以 a*10^n 的格式作答，例如 8*10^-5)"
        correct_answer = f"{numerator}*10^{-exponent}"
        answer_display = f"${numerator}\\times10^{{{-exponent}}}$"

    return {
        "question_text": question_text,
        "answer": answer_display,
        "correct_answer": correct_answer,
        "input_type": "text"
    }

def generate_properties_problem():
    """
    題型：判斷科學記號展開後的性質。
    子題型：正指數問位數，負指數問小數點後第幾位不為0。
    """
    sub_type = random.choice(['positive_exp', 'negative_exp'])
    coeff = round(random.uniform(1, 9.99), random.randint(1, 2))
    
    if sub_type == 'positive_exp':
        exponent = random.randint(2, 10)
        question_text = f"若將 $ {format_number(coeff)}\\times10^{{{exponent}}} $ 乘開，則這個數是幾位數？"
        # 係數 a (1 <= a < 10) 的整數位有 1 位，總位數為 n+1
        num_digits = exponent + 1
        correct_answer = str(num_digits)
        
    else: # negative_exp
        exponent = random.randint(2, 10)
        question_text = f"若將 $ {format_number(coeff)}\\times10^{{{-exponent}}} $ 乘開，則這個數的小數點後第幾位開始出現不為 0 的數字？"
        # 小數點後不為 0 的位置由指數的絕對值決定
        position = exponent
        correct_answer = str(position)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "input_type": "text"
    }

def generate_comparison_problem():
    """
    題型：比較兩個以科學記號表示的數的大小。
    """
    # 產生第一個數
    coeff1 = round(random.uniform(1, 9.9), 2)
    exp1 = random.randint(-8, 8)
    
    # 決定比較類型：比較係數(指數相同)或比較指數(指數不同)
    comp_type = random.choice(['same_exp', 'diff_exp'])
    
    if comp_type == 'same_exp':
        exp2 = exp1
        # 確保係數不同
        coeff2 = round(random.uniform(1, 9.9), 2)
        while coeff2 == coeff1:
            coeff2 = round(random.uniform(1, 9.9), 2)
    else: # diff_exp
        coeff2 = round(random.uniform(1, 9.9), 2)
        # 確保指數不同
        exp2 = random.randint(-8, 8)
        while exp2 == exp1:
            exp2 = random.randint(-8, 8)

    # 隨機交換兩數，避免第一題永遠比較大或小
    if random.random() < 0.5:
        coeff1, coeff2 = coeff2, coeff1
        exp1, exp2 = exp2, exp1

    num1_str = f"{format_number(coeff1)}\\times10^{{{exp1}}}"
    num2_str = f"{format_number(coeff2)}\\times10^{{{exp2}}}"

    question_text = f"比較兩數的大小，在 __ 中填入 $>$、 $<$ 或 $=$：\n$ {num1_str} $ __ $ {num2_str} $"
    
    # 使用 Decimal 進行精確比較
    val1 = decimal.Decimal(str(coeff1)) * (decimal.Decimal('10') ** exp1)
    val2 = decimal.Decimal(str(coeff2)) * (decimal.Decimal('10') ** exp2)
    
    if val1 > val2:
        correct_answer = ">"
    elif val1 < val2:
        correct_answer = "<"
    else:
        correct_answer = "="
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "input_type": "text"
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    
    # 處理比較符號
    if correct_answer in ['>', '<', '=']:
        user_answer = user_answer.replace('＞', '>').replace('＜', '<')
        is_correct = (user_answer == correct_answer)
        result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
        return {"correct": is_correct, "result": result_text, "next_question": True}

    # 處理科學記號
    if "*10^" in correct_answer:
        # 標準化使用者輸入，以進行比較
        norm_user_answer = user_answer.lower().replace(' ', '').replace('x', '*').replace('\\times', '*')
        is_correct = (norm_user_answer == correct_answer)
        
        # 如果字串比較失敗，嘗試比較其數值，以容忍不同但等值的表示法 (如 1.2*10^4 vs 12*10^3)
        if not is_correct:
            try:
                # 解析正確答案
                corr_coeff_str, corr_exp_str = correct_answer.split('*10^')
                corr_val = decimal.Decimal(corr_coeff_str) * (decimal.Decimal('10') ** int(corr_exp_str))

                # 解析使用者答案
                if '*10^' in norm_user_answer:
                    user_coeff_str, user_exp_str = norm_user_answer.split('*10^')
                    user_val = decimal.Decimal(user_coeff_str) * (decimal.Decimal('10') ** int(user_exp_str))
                    if corr_val.compare(user_val) == 0:
                        is_correct = True
            except (ValueError, IndexError, decimal.InvalidOperation):
                pass # 解析失敗，維持原來的 is_correct=False

        answer_display = correct_answer.replace('*10^', '\\times10^{') + '}'
        result_text = f"完全正確！答案是 ${answer_display}$。" if is_correct else f"答案不正確。正確答案應為：${answer_display}$"
        return {"correct": is_correct, "result": result_text, "next_question": True}

    # 處理一般數字答案
    try:
        is_correct = (float(user_answer) == float(correct_answer))
    except ValueError:
        is_correct = (user_answer.upper() == correct_answer.upper())

    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}
