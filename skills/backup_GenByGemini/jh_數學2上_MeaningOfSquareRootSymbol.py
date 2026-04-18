import random
from fractions import Fraction
import math

def generate(level=1):
    """
    生成「根號意義」相關題目。
    - Topic: MeaningOfSquareRootSymbol
    - Description: 此觀念透過正方形的面積與邊長關係來介紹根號「√」的由來。說明一個面積為 a 的正方形，其邊長可以表示為 √a，因此 (√a)² = a。同時，也介紹了根號數值大小的比較原則：若 a＞b＞0，則 √a＞√b。
    """
    problem_type = random.choice(['evaluate_square', 'compare_roots'])
    
    if problem_type == 'evaluate_square':
        return generate_evaluate_square_problem()
    else:  # 'compare_roots'
        return generate_compare_roots_problem()

def generate_evaluate_square_problem():
    """
    題型一：根據根號定義求值。
    $(\sqrt{a})^2 = a$
    其中 a 可以是整數、小數或分數。
    """
    value_type = random.choice(['integer', 'decimal', 'fraction'])
    
    if value_type == 'integer':
        a = random.randint(2, 150)
        a_str_latex = str(a)
        answer_str = str(a)
    elif value_type == 'decimal':
        a = round(random.uniform(1.1, 99.9), 1)
        # Avoid .0 decimals
        if a == int(a):
            a = int(a) + 0.1
        a_str_latex = str(a)
        answer_str = str(a)
    else:  # fraction
        num = random.randint(1, 10)
        den = random.randint(2, 11)
        # 確保非整數
        while num % den == 0:
            den = random.randint(2, 11)
        
        # 約分
        common_divisor = math.gcd(num, den)
        num //= common_divisor
        den //= common_divisor
        
        a_str_latex = f"\\frac{{{num}}}{{{den}}}"
        answer_str = f"{num}/{den}"

    question_text = f"在下列空格中填入正確的值。<br>$ (\\sqrt{{{a_str_latex}}})^2 = $ ______。"
    
    return {
        "question_text": question_text,
        "answer": answer_str,
        "correct_answer": answer_str
    }

def generate_compare_roots_problem():
    """
    題型二：比較根號數值大小。
    1. 直接比較 (√a [ ] √b)
    2. 排序三個根號 (√a, √b, √c)
    """
    sub_type = random.choice(['direct_comparison', 'ordering'])
    
    def _get_random_number():
        """Helper to generate a number (int or Fraction) and its LaTeX string."""
        if random.random() < 0.7:  # 70% chance of being an integer
            val = random.randint(2, 150)
            latex_str = str(val)
            return val, latex_str
        else:  # 30% chance of being a fraction
            num = random.randint(1, 13)
            den = random.randint(2, 13)
            # 避免整數
            while num % den == 0:
                den = random.randint(2, 13)
            
            f = Fraction(num, den)
            # 使用約分後的分數作為 LaTeX 字串
            latex_str = f"\\frac{{{f.numerator}}}{{{f.denominator}}}"
            return f, latex_str

    if sub_type == 'direct_comparison':
        val1, s1 = _get_random_number()
        val2, s2 = _get_random_number()
        while val1 == val2:
            val2, s2 = _get_random_number()
        
        # 隨機交換順序
        if random.choice([True, False]):
            val1, val2 = val2, val1
            s1, s2 = s2, s1
            
        question_text = f"在 [ ] 中填入＞、＜或=。<br>$\\sqrt{{{s1}}}$ [ ] $\\sqrt{{{s2}}}$"
        
        if val1 > val2:
            correct_answer = ">"
        elif val1 < val2:
            correct_answer = "<"
        else:
            correct_answer = "="
            
        return {
            "question_text": question_text,
            "answer": correct_answer,
            "correct_answer": correct_answer
        }
        
    else:  # ordering
        # 生成 3 個不重複的數字
        numbers = []
        while len(numbers) < 3:
            val, latex_str = _get_random_number()
            # 確保數值不重複
            if val not in [item[0] for item in numbers]:
                numbers.append((val, latex_str))
        
        shuffled_numbers = numbers[:]
        random.shuffle(shuffled_numbers)
        
        # --- 修正重點開始 ---
        # 從打亂的數字生成題目，這裡每個項目都要加上 $ 符號，前端才會渲染成數學式
        shuffled_terms_display = [f"$\\sqrt{{{item[1]}}}$" for item in shuffled_numbers]
        
        # 將它們用頓號連接
        question_text = f"試比較下列各數的大小關係 (由小到大，用 < 連接)。<br>{ '、'.join(shuffled_terms_display) }"
        # --- 修正重點結束 ---
        
        # 從排序好的數字生成答案 (答案字串本身不需要加 $，因為 check 函式顯示時會自動加上)
        sorted_numbers = sorted(numbers, key=lambda x: x[0])
        sorted_terms = [f"\\sqrt{{{item[1]}}}" for item in sorted_numbers]
        correct_answer = ' < '.join(sorted_terms)
        
        return {
            "question_text": question_text,
            "answer": correct_answer,
            "correct_answer": correct_answer
        }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    # 標準化答案：去除空白、轉換全形符號
    user_answer_norm = user_answer.strip().replace(' ', '').replace('＞', '>').replace('＜', '<')
    correct_answer_norm = correct_answer.strip().replace(' ', '')
    
    is_correct = False

    # 情況 1: 答案是比較符號
    if correct_answer_norm in ['>', '<', '=']:
        is_correct = (user_answer_norm == correct_answer_norm)
    else:
        # 情況 2: 答案是數值
        try:
            # 嘗試比較分數
            if '/' in user_answer_norm and '/' in correct_answer_norm:
                if Fraction(user_answer_norm) == Fraction(correct_answer_norm):
                    is_correct = True
            # 嘗試比較浮點數/整數
            elif math.isclose(float(user_answer_norm), float(correct_answer_norm)):
                is_correct = True
        except (ValueError, ZeroDivisionError):
            # 若數值轉換失敗，則可能是排序題，繼續往下比較字串
            pass

    # 情況 3: 若非以上情況，直接比較標準化後的字串（主要用於排序題）
    if not is_correct:
        is_correct = (user_answer_norm == correct_answer_norm)

    # 顯示時使用未處理過的 correct_answer 以維持 LaTeX 格式
    if is_correct:
        result_text = f"完全正確！答案是 ${correct_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer}$"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}