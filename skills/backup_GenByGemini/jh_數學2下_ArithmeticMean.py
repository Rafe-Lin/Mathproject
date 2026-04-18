import random
from fractions import Fraction

def generate(level=1):
    """
    生成「等差中項」相關題目。
    當三個數 a, b, c 形成一個等差數列時，中間的數 b 稱為 a 與 c 的「等差中項」。
    公式為: b = (a+c)/2
    """
    return generate_arithmetic_mean_problem()

def generate_arithmetic_mean_problem():
    """
    生成一個等差中項的計算問題。
    題型：已知 a, b, c 成等差數列，求等差中項 b。
    """
    # 1. 生成前後兩項 a 和 c
    # 隨機生成兩個不同的整數
    a = random.randint(-20, 20)
    c = random.randint(-20, 20)
    while a == c:
        c = random.randint(-20, 20)
        
    # 隨機選擇中間項的變數名稱
    variable = random.choice(['p', 'x', 'k', 'm', 'y'])

    # 2. 計算等差中項 b = (a+c)/2
    # 使用 Fraction 以精確處理可能出現的分數
    mean = Fraction(a + c, 2)

    # 3. 格式化答案
    # 如果分母是 1，則答案為整數
    if mean.denominator == 1:
        correct_answer_str = str(mean.numerator)
    # 否則，答案為分數形式，例如 "-7/2"
    else:
        correct_answer_str = str(mean)

    # 4. 組合問題文字
    # 為了讓題目順序自然，可以隨機交換 a 和 c 的顯示位置
    if random.choice([True, False]):
        first_term, third_term = a, c
    else:
        first_term, third_term = c, a
        
    # 使用 f-string 和 LaTeX 格式化問題
    # CRITICAL: 整個數學表達式用一對 $ 包起來，避免語法錯誤
    question_text = f"已知 ${first_term}$ , ${variable}$ , ${third_term}$ 成等差數列，求 ${first_term}$ 與 ${third_term}$ 的等差中項 ${variable}=？$"

    return {
        "question_text": question_text,
        "answer": correct_answer_str,
        "correct_answer": correct_answer_str
    }

def check(user_answer, correct_answer):
    """
    檢查使用者答案是否正確。
    能夠處理整數、小數與分數形式的答案。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    
    is_correct = False
    try:
        # 使用 Fraction 物件進行比較，可以正確處理 "5.0" == "5", "10/2" == "5", "-3.5" == "-7/2" 等情況
        user_val = Fraction(user_answer)
        correct_val = Fraction(correct_answer)
        if user_val == correct_val:
            is_correct = True
    except (ValueError, ZeroDivisionError):
        # 如果無法轉換為 Fraction，表示答案格式不正確或包含非數字字元。
        # 在這種情況下，is_correct 保持為 False
        pass

    # 將正確答案格式化為 LaTeX 以便顯示
    final_frac = Fraction(correct_answer)
    if final_frac.denominator == 1:
        latex_answer = str(final_frac.numerator)
    else:
        # CRITICAL LATEX ESCAPING: Python 字串中的 \ 必須寫成 \\
        latex_answer = f"\\frac{{{final_frac.numerator}}}{{{final_frac.denominator}}}"

    if is_correct:
        result_text = f"完全正確！答案是 ${latex_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${latex_answer}$"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}