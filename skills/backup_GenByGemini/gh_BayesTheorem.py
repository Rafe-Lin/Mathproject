import random
from fractions import Fraction
import math

def generate(level=1):
    """
    生成貝氏定理相關題目。
    包含：
    1. 計算總機率 P(B) (全機率公式)
    2. 計算條件機率 P(Ai|B) (貝氏定理)
    """
    
    # Randomly choose scenario type
    scenario_type = random.choice(['medical_test', 'factory_production'])
    
    if scenario_type == 'medical_test':
        return generate_medical_test_problem(level)
    else: # 'factory_production'
        return generate_factory_problem(level)

def generate_medical_test_problem(level):
    """
    生成醫學檢測情境的貝氏定理問題。
    """
    # P(Disease) - Prevalence
    prevalence_denom_pool = [100, 200, 500, 1000]
    if level >= 2:
        prevalence_denom_pool.extend([50, 250, 750]) # Add more diversity for higher levels
    prevalence_denom = random.choice(prevalence_denom_pool)
    
    prevalence_num = random.randint(1, 10) # 1/X to 10/X
    if level >= 2:
        prevalence_num = random.randint(1, 20)
    
    p_D = Fraction(prevalence_num, prevalence_denom) # P(Disease)
    
    # Ensure p_D is not 0 or 1, and ensure p_D_prime is also valid
    while p_D >= 1 or p_D <= 0:
        prevalence_num = random.randint(1, prevalence_denom - 1)
        p_D = Fraction(prevalence_num, prevalence_denom)

    p_D_prime = Fraction(1) - p_D # P(No Disease)
    
    # P(Positive | Disease) - Sensitivity
    sensitivity_num = random.randint(90, 99) # e.g., 90% to 99%
    if level >= 2:
        sensitivity_num = random.randint(85, 999) # e.g., 85% to 99.9%
        sensitivity_denom = 100 if sensitivity_num < 100 else 1000 # Allow 99.x%
        p_P_given_D = Fraction(sensitivity_num, sensitivity_denom)
    else:
        p_P_given_D = Fraction(sensitivity_num, 100)
    
    # P(Positive | No Disease) - False Positive Rate
    false_pos_denom_pool = [1000, 2000, 5000, 10000] # Denominator for false positive
    if level >= 2:
        false_pos_denom_pool.extend([500, 750, 1500])
    false_pos_denom = random.choice(false_pos_denom_pool)
    
    false_pos_num = random.randint(1, 5) # e.g., 0.1% to 0.5%
    if level >= 2:
        false_pos_num = random.randint(1, 20) # e.g., 0.1% to 2.0%
    
    p_P_given_D_prime = Fraction(false_pos_num, false_pos_denom)
    
    # Ensure P(P|D') < P(P|D) typically
    while p_P_given_D_prime >= p_P_given_D:
        false_pos_num = random.randint(1, int(false_pos_denom * float(p_P_given_D) / 2) + 1)
        if false_pos_num == 0: false_pos_num = 1 # Avoid 0 false positives
        p_P_given_D_prime = Fraction(false_pos_num, false_pos_denom)

    # Calculate P(Positive) using total probability
    p_P = p_D * p_P_given_D + p_D_prime * p_P_given_D_prime
    
    # Define events for question text
    event_D = r"患病的事件"
    event_D_prime = r"未患病的事件"
    event_P = r"篩檢結果呈現陽性的事件"

    # Convert fractions to percentages for display in question
    p_D_percent_val = p_D * 100
    p_D_percent_display = str(p_D_percent_val.numerator) if p_D_percent_val.denominator == 1 else f"{float(p_D_percent_val):.1f}"
    
    p_P_given_D_percent_val = p_P_given_D * 100
    p_P_given_D_percent_display = str(p_P_given_D_percent_val.numerator) if p_P_given_D_percent_val.denominator == 1 else f"{float(p_P_given_D_percent_val):.1f}"
    
    p_P_given_D_prime_percent_val = p_P_given_D_prime * 100
    p_P_given_D_prime_percent_display = str(p_P_given_D_prime_percent_val.numerator) if p_P_given_D_prime_percent_val.denominator == 1 else f"{float(p_P_given_D_prime_percent_val):.1f}"
    
    question_base = (
        f"有一種檢驗某傳染病的篩檢試劑，根據統計：<br>"
        f"患此病的人經篩檢後有 ${p_P_given_D_percent_display}\\%$ 的機率呈現陽性；<br>"
        f"未患此病的人也有 ${p_P_given_D_prime_percent_display}\\%$ 的機率被誤檢而呈現陽性。<br>"
        f"假設某地區有 ${p_D_percent_display}\\%$ 的人罹患此病。<br>"
    )

    question_type = random.choice(['total_prob', 'bayes_disease', 'bayes_no_disease'])
    if level == 1: # Level 1 primarily focuses on total probability or disease given positive
        question_type = random.choice(['total_prob', 'bayes_disease'])

    if question_type == 'total_prob':
        question_text = question_base + r"(1) 從此地區任選一人接受篩檢，求此人的篩檢結果呈現陽性的機率。(請以最簡分數或小數作答)"
        correct_answer_frac = p_P
        explanation = (
            f"設 $D$ 為{event_D}，$D'$ 為{event_D_prime}，$P$ 為{event_P}。<br>"
            f"已知 $P(D) = {p_D}$，$P(D') = {p_D_prime}$，$P(P|D) = {p_P_given_D}$，$P(P|D') = {p_P_given_D_prime}$。<br>"
            f"篩檢結果呈現陽性的機率為 $P(P) = P(D)P(P|D) + P(D')P(P|D')$<br>"
            f"$= {p_D} \\times {p_P_given_D} + {p_D_prime} \\times {p_P_given_D_prime}$<br>"
            f"$= {p_D * p_P_given_D} + {p_D_prime * p_P_given_D_prime}$<br>"
            f"$= {p_P}$。"
        )
    elif question_type == 'bayes_disease':
        # P(Disease | Positive)
        correct_answer_frac = (p_D * p_P_given_D) / p_P
        question_text = question_base + r"(2) 已知某人的篩檢結果呈現陽性，求此人實際上患病的機率。(請以最簡分數或小數作答)"
        explanation = (
            f"設 $D$ 為{event_D}，$D'$ 為{event_D_prime}，$P$ 為{event_P}。<br>"
            f"已知 $P(D) = {p_D}$，$P(D') = {p_D_prime}$，$P(P|D) = {p_P_given_D}$，$P(P|D') = {p_P_given_D_prime}$。<br>"
            f"首先計算 $P(P)$ (篩檢結果呈現陽性的機率)：<br>"
            f"$P(P) = P(D)P(P|D) + P(D')P(P|D') = {p_D} \\times {p_P_given_D} + {p_D_prime} \\times {p_P_given_D_prime} = {p_P}$。<br>"
            f"已知篩檢結果呈現陽性，此人實際上患病的機率為 $P(D|P)$：<br>"
            f"$P(D|P) = \\frac{{P(D \\cap P)}}{{P(P)}} = \\frac{{P(D)P(P|D)}}{{P(P)}}$<br>"
            f"$= \\frac{{{p_D} \\times {p_P_given_D}}}{{{p_P}}} = \\frac{{{p_D * p_P_given_D}}}{{{p_P}}} = {correct_answer_frac}$。"
        )
    else: # 'bayes_no_disease'
        # P(No Disease | Positive)
        correct_answer_frac = (p_D_prime * p_P_given_D_prime) / p_P
        question_text = question_base + r"(2) 已知某人的篩檢結果呈現陽性，求此人實際上未患病的機率。(請以最簡分數或小數作答)"
        explanation = (
            f"設 $D$ 為{event_D}，$D'$ 為{event_D_prime}，$P$ 為{event_P}。<br>"
            f"已知 $P(D) = {p_D}$，$P(D') = {p_D_prime}$，$P(P|D) = {p_P_given_D}$，$P(P|D') = {p_P_given_D_prime}$。<br>"
            f"首先計算 $P(P)$ (篩檢結果呈現陽性的機率)：<br>"
            f"$P(P) = P(D)P(P|D) + P(D')P(P|D') = {p_D} \\times {p_P_given_D} + {p_D_prime} \\times {p_P_given_D_prime} = {p_P}$。<br>"
            f"已知篩檢結果呈現陽性，此人實際上未患病的機率為 $P(D'|P)$：<br>"
            f"$P(D'|P) = \\frac{{P(D' \\cap P)}}{{P(P)}} = \\frac{{P(D')P(P|D')}}{{P(P)}}$<br>"
            f"$= \\frac{{{p_D_prime} \\times {p_P_given_D_prime}}}{{{p_P}}} = \\frac{{{p_D_prime * p_P_given_D_prime}}}{{{p_P}}} = {correct_answer_frac}$。"
        )
    
    return {
        "question_text": question_text,
        "answer": str(correct_answer_frac), # Store as string
        "correct_answer": str(correct_answer_frac),
        "explanation": explanation
    }


def generate_factory_problem(level):
    """
    生成工廠生產情境的貝氏定理問題。
    """
    num_machines = 3 if level >= 2 else 2 # Use 2 or 3 machines
    
    machine_names = ['甲', '乙', '丙']
    machines = machine_names[:num_machines]
    
    # Generate production proportions (P(Ai))
    if num_machines == 2:
        denom = random.choice([3, 4, 5, 6, 8, 10, 12, 15, 20])
        p_A1_num = random.randint(1, denom - 1)
        p_A1 = Fraction(p_A1_num, denom)
        p_A2 = Fraction(1) - p_A1
        p_A_values = [p_A1, p_A2]
    else: # 3 machines
        denominators_pool = [6, 8, 10, 12, 15, 20, 24, 30]
        denom = random.choice(denominators_pool)
        
        # Pick 2 split points from 1 to denom-1 to divide the total into 3 parts
        splits = sorted(random.sample(range(1, denom), 2)) 
        
        n1 = splits[0]
        n2 = splits[1] - splits[0]
        n3 = denom - splits[1]
        
        nums_sum_to_denom = [n1, n2, n3]
        random.shuffle(nums_sum_to_denom) # Shuffle to make machine assignment random
        
        p_A_values = [Fraction(n, denom) for n in nums_sum_to_denom]

    # Generate defective rates (P(B|Ai))
    p_B_given_A_values = []
    for _ in range(num_machines):
        defect_num = random.randint(1, 10) # 1% to 10%
        if level >= 2:
            defect_num = random.randint(1, 20) # 1% to 20%
        p_B_given_A_values.append(Fraction(defect_num, 100)) # e.g., 6/100
        
    # Calculate P(B) using total probability
    p_B = Fraction(0)
    for i in range(num_machines):
        p_B += p_A_values[i] * p_B_given_A_values[i]

    # Construct the base problem description
    machine_production_parts = []
    machine_defect_rates_display = []
    for i in range(num_machines):
        p_B_given_A_percent_val = p_B_given_A_values[i] * 100
        p_B_given_A_percent_display = str(p_B_given_A_percent_val.numerator) if p_B_given_A_percent_val.denominator == 1 else f"{float(p_B_given_A_percent_val):.1f}"
        
        machine_production_parts.append(f"${machines[i]}$ 機器，其產量佔總產量的 ${p_A_values[i]}$")
        machine_defect_rates_display.append(f"${p_B_given_A_percent_display}\\%$") 
    
    question_base = (
        f"某工廠有 {num_machines} 台機器：{', '.join([f'${m}$' for m in machines])}。<br>"
        f"其產量分別佔總產量的 {', '.join([str(p_A_values[i]) for i in range(num_machines)])}，"
        f"且依過去的經驗知 {', '.join([f'${m}$' for m in machines])} 機器生產的產品中分別有 "
        f"{', '.join(machine_defect_rates_display)} 的不良品。<br>"
    )
    
    # Randomly choose question type
    question_type = random.choice(['total_prob', 'bayes_specific_machine'])
    if level == 1: # For level 1, make the specific machine the first one
        machine_for_bayes = 0 # Default to machine A
    else:
        machine_for_bayes = random.randint(0, num_machines - 1) # Random machine

    if question_type == 'total_prob':
        question_text = question_base + r"(1) 任選一產品，求該產品為不良品的機率。(請以最簡分數或小數作答)"
        correct_answer_frac = p_B
        explanation_terms = []
        for i in range(num_machines):
            explanation_terms.append(f"P(A_{{ {i+1} }})P(B|A_{{ {i+1} }}) = {p_A_values[i]} \\times {p_B_given_A_values[i]} = {p_A_values[i] * p_B_given_A_values[i]}")
        
        explanation = (
            f"設 $A_1, \\dots, A_{{ {num_machines} }}$ 分別表示選出的產品是由${machines[0]},\\dots,{machines[num_machines-1]}$ 機器所製造的事件；$B$ 表示選出者為不良品的事件。<br>"
            f"任選一產品為不良品的機率為 $P(B) = \\sum_{{i=1}}^{{{num_machines}}} P(A_i)P(B|A_i)$<br>"
            f"$ = {' + '.join([f'{p_A_values[i]} \\times {p_B_given_A_values[i]}' for i in range(num_machines)])}$<br>"
            f"$ = {' + '.join([str(p_A_values[i] * p_B_given_A_values[i]) for i in range(num_machines)])}$<br>"
            f"$ = {p_B}$。"
        )
    else: # 'bayes_specific_machine'
        target_machine_idx = machine_for_bayes
        target_machine_name = machines[target_machine_idx]
        
        p_target_A = p_A_values[target_machine_idx]
        p_B_given_target_A = p_B_given_A_values[target_machine_idx]
        
        correct_answer_frac = (p_target_A * p_B_given_target_A) / p_B
        question_text = question_base + f"(2) 已知某產品為不良品，求該產品為${target_machine_name}$機器所生產的機率。(請以最簡分數或小數作答)"
        
        explanation_terms_pB = []
        for i in range(num_machines):
            explanation_terms_pB.append(f"{p_A_values[i]} \\times {p_B_given_A_values[i]}")

        explanation = (
            f"設 $A_1, \\dots, A_{{ {num_machines} }}$ 分別表示選出的產品是由機器所製造的事件；$B$ 表示選出者為不良品的事件。<br>"
            f"首先計算 $P(B)$ (產品為不良品的機率)：<br>"
            f"$P(B) = \\sum_{{i=1}}^{{{num_machines}}} P(A_i)P(B|A_i) = {' + '.join(explanation_terms_pB)} = {p_B}$。<br>"
            f"某產品為不良品，此不良品為${target_machine_name}$機器所生產的機率為 $P(A_{{ {target_machine_idx+1} }}|B)$：<br>"
            f"$P(A_{{ {target_machine_idx+1} }}|B) = \\frac{{P(A_{{ {target_machine_idx+1} }} \\cap B)}}{{P(B)}} = \\frac{{P(A_{{ {target_machine_idx+1} }})P(B|A_{{ {target_machine_idx+1} }})}}{{P(B)}}$<br>"
            f"$= \\frac{{{p_target_A} \\times {p_B_given_target_A}}}{{{p_B}}} = \\frac{{{p_target_A * p_B_given_target_A}}}{{{p_B}}} = {correct_answer_frac}$。"
        )

    return {
        "question_text": question_text,
        "answer": str(correct_answer_frac),
        "correct_answer": str(correct_answer_frac),
        "explanation": explanation
    }


def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    
    is_correct = False
    feedback = ""

    try:
        # Try to convert to Fraction first for exact comparison
        user_frac = Fraction(user_answer)
        correct_frac = Fraction(correct_answer)
        if user_frac == correct_frac:
            is_correct = True
        else:
            # If not exact fraction match, try float comparison with tolerance
            user_float = float(user_frac)
            correct_float = float(correct_frac)
            if math.isclose(user_float, correct_float, rel_tol=1e-7, abs_tol=1e-10):
                is_correct = True
            
    except ValueError:
        try:
            # If user answer is not a valid fraction, try converting to float directly
            user_float = float(user_answer)
            correct_float = float(correct_answer)
            if math.isclose(user_float, correct_float, rel_tol=1e-7, abs_tol=1e-10):
                is_correct = True
        except ValueError:
            # User answer is neither a valid fraction nor a float
            is_correct = False

    if is_correct:
        feedback = f"完全正確！答案是 ${correct_answer}$。"
    else:
        feedback = f"答案不正確。正確答案應為：${correct_answer}$"
        
    return {"correct": is_correct, "result": feedback, "next_question": True}