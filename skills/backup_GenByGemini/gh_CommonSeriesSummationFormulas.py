import random
from fractions import Fraction
import math

# Helper functions for calculations
def sum_n(n):
    """Calculates the sum of the first n natural numbers: 1 + 2 + ... + n."""
    if n < 0: return 0
    return n * (n + 1) // 2

def sum_n_squared(n):
    """Calculates the sum of the first n squares: 1^2 + 2^2 + ... + n^2."""
    if n < 0: return 0
    return n * (n + 1) * (2 * n + 1) // 6

def sum_n_cubed(n):
    """Calculates the sum of the first n cubes: 1^3 + 2^3 + ... + n^3."""
    if n < 0: return 0
    return (n * (n + 1) // 2)**2

def generate(level=1):
    """
    生成「常用級數和公式」相關題目。
    根據難度等級 (level) 生成不同類型的問題。
    """
    problem_funcs = [
        generate_type_1_direct_sum,
        generate_type_2_partial_sum,
        generate_type_3_even_odd_sum_sq_cb,
        generate_type_4_word_problem_sq_cb,
        generate_type_5_formula_recall,
    ]

    # Adjust problem distribution based on level
    if level == 1:
        chosen_func = random.choice([
            generate_type_1_direct_sum,
            generate_type_1_direct_sum, # Increase frequency of direct sums
            generate_type_5_formula_recall,
        ])
    elif level == 2:
        chosen_func = random.choice([
            generate_type_1_direct_sum,
            generate_type_2_partial_sum,
            generate_type_3_even_odd_sum_sq_cb,
            generate_type_5_formula_recall,
        ])
    else: # level 3+
        chosen_func = random.choice(problem_funcs) # All types including word problems

    return chosen_func(level)

def generate_type_1_direct_sum(level):
    """
    生成計算 $\sum_{{k=1}}^{{n}} k^p$ 的題目，其中 $p \in \{1, 2, 3\}$。
    """
    power = random.choice([1, 2, 3])
    
    if power == 1:
        n = random.randint(10, 50) if level > 1 else random.randint(5, 20)
        sum_val = sum_n(n)
        formula_latex = r"\\frac{{{n}({n}+1)}}{{2}}"
        sum_terms_str = f"1+2+...+{n}"
    elif power == 2:
        n = random.randint(10, 25) if level > 1 else random.randint(5, 15)
        sum_val = sum_n_squared(n)
        formula_latex = r"\\frac{{{n}({n}+1)(2{n}+1)}}{{6}}"
        sum_terms_str = f"1^{{2}}+2^{{2}}+...+{n}^{{2}}"
    else: # power == 3
        n = random.randint(7, 15) if level > 1 else random.randint(3, 10)
        sum_val = sum_n_cubed(n)
        formula_latex = r"(\\frac{{{n}({n}+1)}}{{2}})^{{2}}"
        sum_terms_str = f"1^{{3}}+2^{{3}}+...+{n}^{{3}}"

    question_text = f"求下列級數的和：${sum_terms_str}$。"
    correct_answer = str(sum_val)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "explanation": f"使用公式：${sum_terms_str} = {formula_latex} = {sum_val}$ 計算。",
    }

def generate_type_2_partial_sum(level):
    """
    生成計算 $\sum_{{k=m}}^{{n}} k^p$ 的題目，其中 $p \in \{1, 2, 3\}$。
    """
    power = random.choice([1, 2, 3])
    
    if power == 1:
        n_max = 50 if level > 1 else 20
        m_val = random.randint(2, n_max // 2)
        n_val = random.randint(m_val + 5, n_max)
        sum_func = sum_n
    elif power == 2:
        n_max = 25 if level > 1 else 15
        m_val = random.randint(2, n_max // 2)
        n_val = random.randint(m_val + 3, n_max)
        sum_func = sum_n_squared
    else: # power == 3
        n_max = 15 if level > 1 else 10
        m_val = random.randint(2, n_max // 2)
        n_val = random.randint(m_val + 2, n_max)
        sum_func = sum_n_cubed

    sum_val = sum_func(n_val) - sum_func(m_val - 1)

    question_text = f"求下列級數的和：${m_val}^{{{power}}}+{(m_val+1)}^{{{power}}}+...+{n_val}^{{{power}}}$。"
    correct_answer = str(sum_val)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "explanation": (
            f"此為部分和，可使用 $\\sum_{{k={m_val}}}^{{{n_val}}} k^{{{power}}} = "
            f"\\sum_{{k=1}}^{{{n_val}}} k^{{{power}}} - \\sum_{{k=1}}^{{{m_val}-1}} k^{{{power}}} = "
            f"{sum_func(n_val)} - {sum_func(m_val - 1)} = {sum_val}$ 計算。"
        ),
    }


def generate_type_3_even_odd_sum_sq_cb(level):
    """
    生成計算連續正偶數或正奇數的平方和或立方和的題目。
    e.g., $2^2+4^2+...+20^2$ 或 $1^2+3^2+...+19^2$
    """
    is_even = random.choice([True, False])
    power = random.choice([2, 3]) 

    if is_even:
        n_terms = random.randint(5, 12) if level > 1 else random.randint(3, 8)
        last_term = 2 * n_terms
        
        if power == 2:
            sum_val = 4 * sum_n_squared(n_terms)
            sum_terms_str = f"2^{{2}}+4^{{2}}+...+{last_term}^{{2}}"
            nested_sum_terms = f"1^{{2}}+2^{{2}}+...+{n_terms}^{{2}}"
            nested_sum_val = sum_n_squared(n_terms)
        else: # power == 3
            sum_val = 8 * sum_n_cubed(n_terms)
            sum_terms_str = f"2^{{3}}+4^{{3}}+...+{last_term}^{{3}}"
            nested_sum_terms = f"1^{{3}}+2^{{3}}+...+{n_terms}^{{3}}"
            nested_sum_val = sum_n_cubed(n_terms)
        
        question_text = f"求下列連續正偶數的{['平方', '立方'][power-2]}和：${sum_terms_str}$。"
        explanation = f"可將級數改寫為 $2^{{{power}}}({nested_sum_terms}) = 2^{{{power}}} \\times {nested_sum_val} = {sum_val}$ 再計算。"
    else: # Odd series
        n_terms = random.randint(5, 12) if level > 1 else random.randint(3, 8)
        last_term = 2 * n_terms - 1
        
        if power == 2:
            sum_up_to_last_even_val = sum_n_squared(2 * n_terms)
            sum_of_even_val = (4 * sum_n_squared(n_terms))
            sum_val = sum_up_to_last_even_val - sum_of_even_val
            sum_terms_str = f"1^{{2}}+3^{{2}}+...+{last_term}^{{2}}"
            all_terms_str = f"1^{{2}}+2^{{2}}+...+{(2*n_terms)}^{{2}}"
            even_terms_str = f"2^{{2}}+4^{{2}}+...+{(2*n_terms)}^{{2}}"
        else: # power == 3
            sum_up_to_last_even_val = sum_n_cubed(2 * n_terms)
            sum_of_even_val = (8 * sum_n_cubed(n_terms))
            sum_val = sum_up_to_last_even_val - sum_of_even_val
            sum_terms_str = f"1^{{3}}+3^{{3}}+...+{last_term}^{{3}}"
            all_terms_str = f"1^{{3}}+2^{{3}}+...+{(2*n_terms)}^{{3}}"
            even_terms_str = f"2^{{3}}+4^{{3}}+...+{(2*n_terms)}^{{3}}"

        question_text = f"求下列連續正奇數的{['平方', '立方'][power-2]}和：${sum_terms_str}$。"
        explanation = (
            f"可使用 $(\\sum_{{k=1}}^{{{2*n_terms}}} k^{{{power}}}) - (\\sum_{{k=1}}^{{{n_terms}}} (2k)^{{{power}}})$ 計算。<br>"
            f"即 $({all_terms_str}) - ({even_terms_str}) = {sum_up_to_last_even_val} - {sum_of_even_val} = {sum_val}$。"
        )

    correct_answer = str(sum_val)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "explanation": explanation,
    }

def generate_type_4_word_problem_sq_cb(level):
    """
    生成應用級數和公式的文字題，例如香檳塔或招兵問題。
    """
    problem_scenario = random.choice(['champagne_tower', 'daily_recruitment'])
    
    if problem_scenario == 'champagne_tower':
        num_layers = random.randint(8, 15) if level > 1 else random.randint(5, 10)
        
        # Part 1: Cups in the last layer
        answer_part1 = str(num_layers**2)
        
        # Part 2: Total cups
        answer_part2 = str(sum_n_squared(num_layers))
        
        question_text = (
            f"右圖為使用高腳杯堆疊而成的香檳塔，最頂層有1個杯子，"
            f"往下的每一層都排成正方形，第2層每邊有2個杯子，"
            f"第3層每邊有3個杯子，......，以此類推。仿照上面的方式，"
            f"堆成{num_layers}層高的香檳塔，試回答下列問題。<br>"
            f"(1) 第{num_layers}層有幾個高腳杯？<br>"
            f"(2) 堆成{num_layers}層高的香檳塔需要準備多少個高腳杯？"
        )
        # Combine answers as a string to be parsed by check function
        correct_answer = f"(1) {answer_part1} (2) {answer_part2}" 
        explanation = (
            f"(1) 第{num_layers}層每邊有{num_layers}個杯子，排成正方形，所以數量為 ${num_layers}^{{2}} = {answer_part1}$。<br>"
            f"(2) 總杯子數為 $1^{{2}}+2^{{2}}+...+{num_layers}^{{2}} = \\frac{{{num_layers}({num_layers}+1)(2 \\times {num_layers}+1)}}{{6}} = {answer_part2}$。"
        )

    else: # daily_recruitment - cubes
        num_days = random.randint(8, 25) if level > 1 else random.randint(5, 15)
        total_recruits = sum_n_cubed(num_days)
        
        question_text = (
            f"官府每日招兵人數均為立方數，依序為：首日招1人，次日招8人，"
            f"第三日招27人，......，以此類推。已知總共招兵{total_recruits}人，"
            f"求官府招兵的總日數。"
        )
        correct_answer = str(num_days)
        
        sqrt_total = int(math.sqrt(total_recruits))
        half_n_n_plus_1 = sqrt_total
        n_n_plus_1 = 2 * half_n_n_plus_1
        
        explanation = (
            f"設總日數為 $n$ 日，則招兵總人數為 $1^{{3}}+2^{{3}}+...+n^{{3}} = (\\frac{{n(n+1)}}{{2}})^{{2}}$。<br>"
            f"已知總招兵人數為 ${total_recruits}$，因此 $(n(n+1)/2)^{{2}} = {total_recruits}$。<br>"
            f"$\\frac{{n(n+1)}}{{2}} = \\sqrt{{{total_recruits}}} = {sqrt_total}$。<br>"
            f"$n(n+1) = {n_n_plus_1}$。<br>"
            f"由於 $n(n+1)$ 是一個連續整數的乘積，找出其等於 ${n_n_plus_1}$ 的 $n$ 值。"
            f"在本題中，計算得出 $n = {num_days}$。"
        )

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "explanation": explanation,
    }


def generate_type_5_formula_recall(level):
    """
    生成要求回憶級數和公式的題目。
    """
    formula_type = random.choice(['sum_n', 'sum_n_squared', 'sum_n_cubed'])
    
    if formula_type == 'sum_n':
        question_text = r"下列何者為連續正整數和 $\sum_{{k=1}}^{{n}} k$ 的公式？"
        correct_latex = r"\\frac{{n(n+1)}}{{2}}"
        options_latex = [
            r"\\frac{{n(n+1)}}{{2}}",
            r"\\frac{{n(n+1)(2n+1)}}{{6}}",
            r"(\\frac{{n(n+1)}}{{2}})^{{2}}",
            r"n(n+1)",
        ]
    elif formula_type == 'sum_n_squared':
        question_text = r"下列何者為連續正整數平方和 $\sum_{{k=1}}^{{n}} k^{{2}}$ 的公式？"
        correct_latex = r"\\frac{{n(n+1)(2n+1)}}{{6}}"
        options_latex = [
            r"\\frac{{n(n+1)}}{{2}}",
            r"\\frac{{n(n+1)(2n+1)}}{{6}}",
            r"(\\frac{{n(n+1)}}{{2}})^{{2}}",
            r"n^{{2}}",
        ]
    else: # sum_n_cubed
        question_text = r"下列何者為連續正整數立方和 $\sum_{{k=1}}^{{n}} k^{{3}}$ 的公式？"
        correct_latex = r"(\\frac{{n(n+1)}}{{2}})^{{2}}"
        options_latex = [
            r"\\frac{{n(n+1)}}{{2}}",
            r"\\frac{{n(n+1)(2n+1)}}{{6}}",
            r"(\\frac{{n(n+1)}}{{2}})^{{2}}",
            r"n^{{3}}",
        ]
    
    random.shuffle(options_latex)
    option_letters = ['①', '②', '③', '④']
    option_text = ""
    answer_idx = -1
    for i, opt in enumerate(options_latex):
        option_text += f"{option_letters[i]} ${opt}$<br>"
        if opt == correct_latex:
            answer_idx = i
            
    question_text += f"<br>{option_text}請填寫選項代號。"
    
    correct_answer_for_check = option_letters[answer_idx]

    return {
        "question_text": question_text,
        "answer": correct_answer_for_check, # This is the option letter
        "correct_answer": correct_answer_for_check,
        "explanation": f"正確的公式為 ${correct_latex}$。",
    }


def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    處理單一數值答案、選項答案或多部分答案 (如word problem)。
    """
    user_answer = user_answer.strip().upper()
    correct_answer_strip = correct_answer.strip().upper() 

    is_correct = False
    result_text = ""

    # Check if the correct_answer indicates a multi-part answer (e.g., from word problems)
    is_multi_part = "(1)" in correct_answer_strip and "(2)" in correct_answer_strip

    if is_multi_part:
        correct_parts = {}
        # Parse correct_answer like "(1) X (2) Y"
        temp_correct_str = correct_answer_strip.replace("(", "").replace(")", "")
        parts_list = temp_correct_str.split()
        for part in parts_list:
            if part.startswith('1'):
                correct_parts[1] = part[1:].strip()
            elif part.startswith('2'):
                correct_parts[2] = part[1:].strip()
        
        user_parts = {}
        # Try to parse user input in multiple ways
        # "(1) X (2) Y"
        if "(1)" in user_answer and "(2)" in user_answer:
            temp_user_str = user_answer.replace("(", "").replace(")", "")
            user_parts_list = temp_user_str.split()
            for part in user_parts_list:
                if part.startswith('1'):
                    user_parts[1] = part[1:].strip()
                elif part.startswith('2'):
                    user_parts[2] = part[1:].strip()
        # "X, Y"
        elif "," in user_answer:
            temp_parts = [p.strip() for p in user_answer.split(',')]
            if len(temp_parts) == 2:
                user_parts[1] = temp_parts[0]
                user_parts[2] = temp_parts[1]
        # "X Y" (space separated)
        elif len(user_answer.split()) == 2:
            temp_parts = user_answer.split()
            user_parts[1] = temp_parts[0]
            user_parts[2] = temp_parts[1]

        if 1 in user_parts and 2 in user_parts:
            part1_correct = False
            part2_correct = False
            
            # Check numerical equality for each part
            if 1 in correct_parts:
                try:
                    if float(user_parts[1]) == float(correct_parts[1]):
                        part1_correct = True
                except ValueError:
                    if user_parts[1] == correct_parts[1]: # Fallback to string comparison
                        part1_correct = True
            
            if 2 in correct_parts:
                try:
                    if float(user_parts[2]) == float(correct_parts[2]):
                        part2_correct = True
                except ValueError:
                    if user_parts[2] == correct_parts[2]: # Fallback to string comparison
                        part2_correct = True

            is_correct = part1_correct and part2_correct
            if is_correct:
                result_text = f"完全正確！答案是 {correct_answer}。" # No $ for multi-part answer
            else:
                feedback = []
                if 1 in correct_parts and not part1_correct: feedback.append(f"第1部分答案不正確 (正確答案為 {correct_parts[1]})")
                if 2 in correct_parts and not part2_correct: feedback.append(f"第2部分答案不正確 (正確答案為 {correct_parts[2]})")
                result_text = "；".join(feedback) + f"。正確答案應為：{correct_answer}" # No $ for multi-part answer
        else:
            result_text = f"您的答案格式可能不正確或不完整。請確保您回答了所有部分。正確答案應為：{correct_answer}" # No $

    # Handle single answer (numerical or option code)
    else:
        try:
            user_num = float(user_answer)
            correct_num = float(correct_answer_strip)
            if user_num == correct_num:
                is_correct = True
                result_text = f"完全正確！答案是 ${correct_answer_strip}$。"
            else:
                result_text = f"答案不正確。正確答案應為：${correct_answer_strip}$。"
        except ValueError:
            # Not a number, check for direct string match (e.g., for options like "①")
            if user_answer == correct_answer_strip:
                is_correct = True
                result_text = f"完全正確！答案是 ${correct_answer_strip}$。"
            else:
                result_text = f"答案不正確。正確答案應為：${correct_answer_strip}$。"

    return {"correct": is_correct, "result": result_text, "next_question": True}