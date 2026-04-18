import random
import math
from fractions import Fraction

def generate(level=1):
    n = 0
    p_num = 0
    p_den = 0
    scenario_desc = ""

    # Adjust parameters based on level
    if level == 1:
        n = random.randint(3, 5) # Fewer trials for easier level
        # Simple probabilities: 1/2, 1/3, 1/4, 2/3
        possible_probs = [(1, 2), (1, 3), (1, 4), (2, 3)]
        p_num, p_den = random.choice(possible_probs)
    elif level == 2:
        n = random.randint(4, 7)
        # More varied probabilities, maybe with common factors
        possible_probs = [(1, 2), (1, 3), (1, 4), (2, 3), (1, 5), (2, 5), (3, 4)]
        p_num, p_den = random.choice(possible_probs)
    else: # level 3+
        n = random.randint(6, 10)
        # Wider range of probabilities
        den_candidates = [2, 3, 4, 5, 6, 7, 8, 9, 10]
        p_den = random.choice(den_candidates)
        p_num = random.randint(1, p_den - 1) # p_num must be less than p_den
        # Simplify p_num, p_den
        common = math.gcd(p_num, p_den)
        p_num //= common
        p_den //= common

    q_num = p_den - p_num
    q_den = p_den

    # Choose a scenario description to make problems more engaging
    scenario_choice = random.randint(1, 4)
    if scenario_choice == 1: # Multiple Choice
        num_options = p_den
        # If p_num is not 1, this scenario description might be awkward.
        # Ensure p_num is 1 for this specific description.
        # Regenerate p_num, p_den if not suitable
        attempts = 0
        while (p_num != 1 or num_options < 2) and attempts < 5: # Max 5 attempts to find suitable p
             if level == 1:
                 p_num, p_den = random.choice([(1,2), (1,3), (1,4)])
             else:
                 p_den = random.randint(2, 5) # At least 2 options
                 p_num = 1
             num_options = p_den
             attempts += 1
        # Fallback if a suitable p couldn't be found (e.g., if only p_num != 1 options available at higher levels)
        if p_num != 1 or num_options < 2:
            p_num, p_den = (1, 4) # Default to 4-choice question
            num_options = 4

        scenario_desc = f"有 ${n}$ 題 {num_options} 選 1 的單選題，某生每題皆隨意選擇一個選項作答。"
        p_text = r"\text{答對的機率}"
        q_text = r"\text{答錯的機率}"
    elif scenario_choice == 2: # Coin Toss
        # Ensure p_num = 1, p_den = 2
        p_num, p_den = (1, 2)
        q_num, q_den = (1, 2) # Also set q
        coin_side = random.choice(["正面", "反面"])
        scenario_desc = f"丟一枚均勻硬幣 ${n}$ 次，觀察出現{coin_side}的情形。"
        p_text = f"\\text{{出現}}{coin_side}\\text{{的機率}}"
        q_text = f"\\text{{未出現}}{coin_side}\\text{{的機率}}"
    elif scenario_choice == 3: # Ball Drawing (with replacement)
        # Ensure p_num/p_den can represent balls, and white_balls > 0
        attempts = 0
        while (p_num >= p_den or p_den - p_num <= 0) and attempts < 5: # p_num must be < p_den and white_balls > 0
             if level == 1:
                 p_num, p_den = random.choice([(1, 2), (1, 3), (1, 4), (2, 3)])
             else:
                 p_den = random.randint(3, 10)
                 p_num = random.randint(1, p_den - 1)
                 common = math.gcd(p_num, p_den)
                 p_num //= common
                 p_den //= common
             attempts += 1
        if p_num >= p_den or p_den - p_num <= 0: # Fallback
            p_num, p_den = (1, 3) # Default to 1 red, 2 white
        
        q_num = p_den - p_num # Recalculate q in case p changed
        q_den = p_den

        total_balls = p_den
        red_balls = p_num
        white_balls = total_balls - red_balls

        scenario_desc = f"袋中有大小相同的紅球 ${red_balls}$ 顆、白球 ${white_balls}$ 顆。每次從袋中取出一球，觀察顏色後再放回袋中，共取球 ${n}$ 次。"
        p_text = r"\text{取到紅球的機率}"
        q_text = r"\text{取到白球的機率}"
    else: # Generic "成功" / "失敗" trial
        p_symbol = random.choice(["成功", "甲事件發生", "目標達成"])
        q_symbol = random.choice(["失敗", "甲事件未發生", "目標未達成"])
        scenario_desc = f"進行一項伯努力試驗，已知{p_symbol}的機率為 $\\frac{{{p_num}}}{{{p_den}}}$，共重複試驗 ${n}$ 次。"
        p_text = f"\\text{{{p_symbol}}}\\text{{的機率}}"
        q_text = f"\\text{{{q_symbol}}}\\text{{的機率}}"


    # Ensure n is reasonable for calculation difficulty, especially if p_den is large
    # For higher levels, allow slightly more complex, but cap max n
    if n > 7 and p_den > 5: # Avoid overly complex fractions for large n
        n = random.randint(5, 7)
    elif n > 10: # Absolute max n
        n = random.randint(7, 10)


    # Choose problem type
    problem_type = 'exactly_k'
    if level == 2:
        problem_type = random.choice(['exactly_k', 'at_most_at_least_k'])
    elif level >= 3:
        problem_type = random.choice(['exactly_k', 'at_most_at_least_k', 'distribution_table'])


    question_text = ""
    correct_answer = ""

    if problem_type == 'exactly_k':
        k = random.randint(0, n)
        question_text = f"{scenario_desc} 求恰有 ${k}$ 次{p_text}的機率。"
        prob = Fraction(math.comb(n, k), 1) * \
               (Fraction(p_num, p_den) ** k) * \
               (Fraction(q_num, q_den) ** (n - k))
        correct_answer = str(prob)
        
    elif problem_type == 'at_most_at_least_k':
        # k should be meaningful, not 0 or n for at most/at least.
        # If n is small (e.g., 3), k can be 1 or 2.
        # If n=3, k can be 1 (at most 1) or 2 (at most 2). k can be 1 (at least 1), 2 (at least 2).
        if n < 2: # Should not happen with current n generation (n >= 3), but for safety
            k = 0
        else:
            k = random.randint(1, n-1) 
        
        condition_type = random.choice(['at_most', 'at_least'])

        prob_sum = Fraction(0, 1)
        if condition_type == 'at_most':
            question_text = f"{scenario_desc} 求至多 ${k}$ 次{p_text}的機率。"
            for i in range(k + 1):
                prob_sum += Fraction(math.comb(n, i), 1) * \
                            (Fraction(p_num, p_den) ** i) * \
                            (Fraction(q_num, q_den) ** (n - i))
        else: # 'at_least'
            question_text = f"{scenario_desc} 求至少 ${k}$ 次{p_text}的機率。"
            for i in range(k, n + 1):
                prob_sum += Fraction(math.comb(n, i), 1) * \
                            (Fraction(p_num, p_den) ** i) * \
                            (Fraction(q_num, q_den) ** (n - i))
        correct_answer = str(prob_sum)

    elif problem_type == 'distribution_table':
        # Add a note about the order of probabilities (for k=0, 1, ..., n)
        question_text = f"{scenario_desc}<br>請列出{p_text}的機率分布表 (成功次數從 $0$ 到 ${n}$)。答案請以分號分隔每個機率值，並以分數表示。例如：$1/8; 3/8; 3/8; 1/8$。"
        probabilities = []
        for k_val in range(n + 1):
            prob = Fraction(math.comb(n, k_val), 1) * \
                   (Fraction(p_num, p_den) ** k_val) * \
                   (Fraction(q_num, q_den) ** (n - k_val))
            probabilities.append(str(prob))
        correct_answer = "; ".join(probabilities) # e.g., "1/16; 4/16; 6/16; 4/16; 1/16"

    return {
        "question_text": question_text,
        "answer": correct_answer, # This is the internal answer, check uses correct_answer
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()

    is_correct = False
    feedback = ""

    # Handle multiple answers for distribution table
    if ";" in correct_answer:
        user_parts = [p.strip() for p in user_answer.split(';')]
        correct_parts = [p.strip() for p in correct_answer.split(';')]

        if len(user_parts) != len(correct_parts):
            feedback = f"答案數量不符。應有 {len(correct_parts)} 個機率值。"
            is_correct = False
        else:
            all_parts_correct = True
            for i in range(len(user_parts)):
                u_part = user_parts[i]
                c_part = correct_parts[i]
                try:
                    user_fraction = Fraction(u_part)
                    correct_fraction = Fraction(c_part)
                    if user_fraction != correct_fraction:
                        all_parts_correct = False
                        break
                except ValueError:
                    # If user's part is not a valid fraction string, try float comparison
                    try:
                        user_float = float(u_part)
                        correct_float = float(Fraction(c_part))
                        if not math.isclose(user_float, correct_float, rel_tol=1e-9, abs_tol=1e-9):
                            all_parts_correct = False
                            break
                        # If floats are close, consider it correct for this part, but give a hint
                        # No need for extra feedback per part, general feedback at end is enough.
                    except ValueError:
                        all_parts_correct = False
                        break # Part is neither a fraction string nor a float string
            
            is_correct = all_parts_correct
            if is_correct:
                feedback = "完全正確！機率分布表已正確列出。"
            else:
                feedback = f"部分答案不正確。請檢查您的機率值。正確答案應為：${correct_answer}$。"

    else: # Single fraction answer
        try:
            user_fraction = Fraction(user_answer)
            correct_fraction = Fraction(correct_answer)
            is_correct = (user_fraction == correct_fraction)
            if is_correct:
                feedback = f"完全正確！答案是 $\\frac{{{correct_fraction.numerator}}}{{{correct_fraction.denominator}}}$。"
            else:
                # If not equal as exact fractions, try float comparison for closeness
                user_float = float(user_fraction)
                correct_float = float(correct_fraction)
                if math.isclose(user_float, correct_float, rel_tol=1e-9, abs_tol=1e-9):
                    is_correct = True
                    feedback = f"您的答案是 {user_answer}，非常接近正確答案 $\\frac{{{correct_fraction.numerator}}}{{{correct_fraction.denominator}}}$。請盡量以分數形式作答，以確保精確度。"
                else:
                    feedback = f"答案不正確。正確答案應為 $\\frac{{{correct_fraction.numerator}}}{{{correct_fraction.denominator}}}$。"
        except ValueError:
            # User input was not a valid fraction string (e.g., "0.333" or "abc")
            try:
                user_float = float(user_answer)
                correct_fraction = Fraction(correct_answer) # Correct answer is always a valid fraction
                correct_float = float(correct_fraction)
                if math.isclose(user_float, correct_float, rel_tol=1e-9, abs_tol=1e-9):
                    is_correct = True
                    feedback = f"您的答案是 {user_answer}，非常接近正確答案 $\\frac{{{correct_fraction.numerator}}}{{{correct_fraction.denominator}}}$。請盡量以分數形式作答，以確保精確度。"
                else:
                    feedback = f"答案不正確。正確答案應為 $\\frac{{{correct_fraction.numerator}}}{{{correct_fraction.denominator}}}$。"
            except ValueError:
                feedback = "您的答案格式不正確。請以分數 (例如 '1/4') 或小數形式作答。"
    
    return {"correct": is_correct, "result": feedback, "next_question": True}