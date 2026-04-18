import random
from fractions import Fraction
import math
import re

def get_smallest_multiplier_for_perfect_square(num):
    """
    計算給定數字需要乘以的最小整數，使其結果成為一個完全平方數。
    例如：get_smallest_multiplier_for_perfect_square(12) -> 3 (因為 12 * 3 = 36 = 6^2)
    """
    if num == 0:
        return 0
    if num == 1:
        return 1
    
    factors = {}
    d = 2
    temp = num
    while d * d <= temp:
        while temp % d == 0:
            factors[d] = factors.get(d, 0) + 1
            temp //= d
        d += 1
    if temp > 1: # 處理剩下的質因數
        factors[temp] = factors.get(temp, 0) + 1

    multiplier = 1
    for factor, count in factors.items():
        if count % 2 == 1: # 如果質因數的指數是奇數，則需要多乘一次這個質因數
            multiplier *= factor
    return multiplier

def generate(level=1):
    """
    生成二項分布期望值與標準差的題目。
    題目會設計成期望值和標準差均為整數，以簡化答案輸入。
    """
    scenarios = [
        ("丟一枚均勻硬幣", "正面", Fraction(1, 2)),
        ("擲一粒公正骰子", "6點", Fraction(1, 6)),
        ("同時丟兩枚均勻硬幣", "兩枚硬幣都正面", Fraction(1, 4)),
        ("擲一粒公正骰子", "點數是3的倍數", Fraction(1, 3)), # 3, 6
        ("擲一粒公正骰子", "點數是偶數", Fraction(1, 2)), # 2, 4, 6
        ("從裝有3紅2藍的袋中隨機取一球", "藍球", Fraction(2, 5)),
        ("從裝有3紅2藍的袋中隨機取一球", "紅球", Fraction(3, 5)),
        ("從裝有4綠1黃的袋中隨機取一球", "綠球", Fraction(4, 5)),
        ("從裝有10張撲克牌（4張A, 6張K）的牌堆中隨機抽一張", "抽到A", Fraction(4, 10)), # 約分後為 2/5
        ("射擊目標，每次擊中機率為0.7", "擊中目標", Fraction(7, 10)),
        ("射擊目標，每次擊中機率為0.3", "未擊中目標", Fraction(7, 10)), # P(未擊中) = 1 - 0.3 = 0.7
    ]

    event_desc, success_desc, p_val = random.choice(scenarios)
    q_val = Fraction(1, 1) - p_val

    # 計算 n 的基底倍數，以確保期望值 E(X) 為整數，且變異數 Var(X) 為完全平方數。
    # Var(X) = n * p * q = n * (p_num/p_den) * (q_num/q_den)
    # 我們需要 n 乘以 (p_num * q_num) / (p_den * q_den) 是一個完全平方數。
    
    # 讓分母的部分 (p_den * q_den) 變為完美平方， n 至少是 p_den * q_den 的倍數。
    # 由於 p 和 q 的分母相同，所以 p_den * q_den = p_den ** 2。
    # n 應為 p_den ** 2 的倍數，以使 Var(X) 的分母簡化為 1。
    
    # 讓分子的部分 (p_num * q_num) 變為完美平方， n 需要乘以 get_smallest_multiplier_for_perfect_square(p_num * q_num)。
    
    # n 的最小基底倍數為 (p_den * q_den) 乘以 確保 p_num * q_num 成為完全平方數所需的乘數。
    n_min_base = (p_val.denominator * q_val.denominator) * get_smallest_multiplier_for_perfect_square(p_val.numerator * q_val.numerator)
    
    # 選擇一個倍數 (本身是完全平方數) 乘上 n_min_base，以產生不同的 n 值，同時保持 E(X) 和 σ(X) 為整數。
    square_multipliers = [1, 4, 9, 16, 25]
    n_multiplier = random.choice(square_multipliers)

    n = n_min_base * n_multiplier

    # 確保 n 在一個合理的範圍內，避免過小或過大。
    if n > 1500 and n_multiplier > 1: # 如果 n 過大，降低倍數
        n = n_min_base * random.choice([1, 4])
    if n < 20: # 如果 n 過小，增加倍數
        n = n_min_base * random.choice([4, 9, 16])
        if n < 20: # 確保至少為 20
            n = 20 + random.randint(0, 5) * 5 # 避免 n_min_base 為 0 或極小的情況

    # 計算期望值 E(X) 和標準差 Sigma(X)
    e_x = n * p_val
    var_x = n * p_val * q_val
    sigma_x = math.sqrt(var_x) # 根據設計，這應該是一個整數

    # 將結果轉換為字串，並確保是整數表示
    e_x_str = str(int(e_x))
    sigma_x_str = str(int(sigma_x)) # 因為我們已確保它是整數

    # 組合成正確答案的字串，包含 LaTeX 格式
    correct_answer_str = f"E(X) = ${e_x_str}$, $\\sigma(X) = ${sigma_x_str}$"

    # 生成問題文本，注意 f-string 中 LaTeX 符號的正確寫法
    question_text = (
        f"重複「{event_desc}」${n}$ 次，觀察{success_desc}的情形，<br>"
        f"求{success_desc}次數的期望值與標準差。"
    )

    return {
        "question_text": question_text,
        "answer": correct_answer_str, # 供 check 函數內部比較使用
        "correct_answer": correct_answer_str # 供錯誤時顯示給使用者
    }

def parse_answer_string(answer_str):
    """
    解析答案字串，嘗試提取期望值和標準差。
    支援 'E=18, S=3', '18, 3', '18 3' 等格式。
    """
    e_val, sigma_val = None, None

    # 清理字串，移除所有空格和 LaTeX 的 $ 符號
    cleaned_str = answer_str.replace(' ', '').replace('$', '')

    # 使用正則表達式尋找所有數字（包括整數、浮點數和分數）
    # (?:/\d+)? 允許匹配分數形式，例如 '15/2'
    nums = re.findall(r"[-+]?\d*\.?\d+(?:/\d+)?", cleaned_str)
    
    if len(nums) >= 2:
        try:
            # 使用 Fraction 處理可能的輸入分數，再轉換為浮點數進行比較
            e_val = float(Fraction(nums[0]))
            sigma_val = float(Fraction(nums[1]))
        except ValueError:
            pass # 如果解析失敗，則保持 None
            
    return e_val, sigma_val

def check(user_answer, correct_answer):
    """
    檢查使用者答案是否正確。
    比對期望值 E(X) 和標準差 σ(X)。
    """
    user_e, user_sigma = parse_answer_string(user_answer)
    correct_e, correct_sigma = parse_answer_string(correct_answer)

    # 浮點數比較時使用一個小容忍度
    tolerance = 1e-6

    is_e_correct = False
    if user_e is not None and correct_e is not None:
        is_e_correct = abs(user_e - correct_e) < tolerance
    
    is_sigma_correct = False
    if user_sigma is not None and correct_sigma is not None:
        is_sigma_correct = abs(user_sigma - correct_sigma) < tolerance

    is_correct = is_e_correct and is_sigma_correct

    result_text = ""
    if is_correct:
        # 正確答案字串格式為 "E(X) = $18$, $\\sigma(X) = $3$"
        # 使用 split(',')[0] 和 [1] 來獲取 E(X) 和 σ(X) 的部分
        result_text = f"完全正確！期望值 {correct_answer.split(',')[0]}，標準差 {correct_answer.split(',')[1]}。"
    else:
        feedback_parts = []
        if not is_e_correct:
            feedback_parts.append(f"期望值不正確。正確應為 {correct_answer.split(',')[0].strip()}。")
        if not is_sigma_correct:
            feedback_parts.append(f"標準差不正確。正確應為 {correct_answer.split(',')[1].strip()}。")
        
        if not feedback_parts: # 如果使用者答案完全無法解析
            result_text = "您的答案格式不正確，請以 '期望值,標準差' 的形式輸入，例如 '18, 3' 或 'E=18, S=3'。"
        else:
            result_text = " ".join(feedback_parts)
            result_text += f"<br>正確答案應為：{correct_answer}"

    return {"correct": is_correct, "result": result_text, "next_question": True}