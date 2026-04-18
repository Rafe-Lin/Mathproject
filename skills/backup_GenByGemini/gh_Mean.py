import random
import math
from fractions import Fraction # Allowed standard library module

# --- Helper functions for specific problem types ---

def generate_arithmetic_mean_problem():
    """
    Generates a problem for calculating the arithmetic mean.
    e.g., 平均身高、年齡
    """
    num_items = random.randint(4, 7) # Number of data points
    
    # Generate numbers that are somewhat close to each other, but with some variation
    base_val = random.randint(150, 200) # e.g., for heights
    data_points = [base_val + random.randint(-15, 15) for _ in range(num_items - 1)]
    # Add one potential outlier or just another number
    data_points.append(base_val + random.randint(-20, 30))
    
    # Ensure all data points are positive if representing things like height/age
    data_points = [max(1, p) for p in data_points]
    
    # Sort for cleaner presentation
    data_points.sort()

    # Determine context
    context = random.choice([
        ("身高", "公分", "籃球校隊"),
        ("年齡", "歲", "國家代表隊"),
        ("體重", "公斤", "某班學生"),
        ("月收入", "萬元", "某公司員工")
    ])
    item_name, unit, group_desc_prefix = context
    
    # Dynamically form group description
    group_desc_suffix = random.choice(["位先發球員", "位球員", "位同學", "位員工"])
    if group_desc_prefix == "某班學生":
        group_desc = f"{group_desc_prefix}{num_items}位同學"
    elif group_desc_prefix == "某公司員工":
        group_desc = f"{group_desc_prefix}{num_items}位員工"
    else: # For sports teams
        group_desc = f"{group_desc_prefix}{num_items}{group_desc_suffix}"

    data_str = ", ".join(map(str, data_points))
    
    question_text = (
        f"已知{group_desc}的{item_name}（{unit}）分別為 ${data_str}$，"
        f"求其算術平均數。"
    )

    total_sum = sum(data_points)
    arithmetic_mean = total_sum / num_items

    # Round to 2 decimal places if it's not an integer, otherwise convert to int
    if arithmetic_mean == int(arithmetic_mean):
        correct_answer = str(int(arithmetic_mean))
    else:
        correct_answer = f"{arithmetic_mean:.2f}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_weighted_mean_problem():
    """
    Generates a problem for calculating the weighted mean or finding a missing value.
    e.g., 學期成績
    """
    problem_type = random.choice(['calculate_mean', 'find_missing'])
    
    num_grades = random.randint(3, 5)
    
    # Generate scores and weights
    scores_initial = [random.randint(60, 95) for _ in range(num_grades)]
    
    # Ensure weights are "nice" percentages that sum to 100
    possible_weights = [10, 15, 20, 25, 30, 35, 40]
    weights_raw = []
    
    # Generate weights that sum to 100%
    while True:
        temp_weights = [random.choice(possible_weights) for _ in range(num_grades)]
        if sum(temp_weights) == 100:
            weights_raw = temp_weights
            break
        # If sum is not 100, try to adjust the last one
        elif num_grades > 1:
            current_sum = sum(temp_weights[:-1])
            remaining = 100 - current_sum
            if remaining > 0 and remaining in possible_weights:
                weights_raw = temp_weights[:-1] + [remaining]
                break
        # If no simple adjustment, regenerate all weights
    
    weights_ratio = [w / 100.0 for w in weights_raw]

    # Context items for the table
    grade_items = random.sample([
        "平常成績", "作業分數", "第一次期中考", "第二次期中考", "期末考", "專題報告", "小考平均"
    ], num_grades)
    
    # Build the table text (initially without 'x')
    header_row = "| | " + " | ".join(grade_items) + " |"
    divider_row = "| :--- | " + " | ".join([":---"] * num_grades) + " |"
    score_row_values = list(map(str, scores_initial)) # use a mutable list copy
    weight_row_values = [f"{w}\%" for w in weights_raw] # Use \% for LaTeX to display '%' in math context if part of $...$

    if problem_type == 'calculate_mean':
        # Calculate the weighted mean
        weighted_sum = sum(s * w for s, w in zip(scores_initial, weights_ratio))
        total_weight = sum(weights_ratio) # Should be 1.0 if weights sum to 100%
        
        weighted_mean = weighted_sum / total_weight
        
        # Round to one decimal place, common for grades
        correct_answer = f"{weighted_mean:.1f}"
        
        score_row = "| 分數 | " + " | ".join(score_row_values) + " |"
        weight_row = "| 比重 | " + " | ".join(weight_row_values) + " |"
        table_text = f"{header_row}<br>{divider_row}<br>{score_row}<br>{weight_row}"

        question_text = (
            f"某生本學期數學科的分數與其所占的比重如下表。<br>"
            f"{table_text}<br>"
            f"試以比重為權數，計算該生的數學科學期成績。"
        )

    else: # find_missing
        missing_idx = random.randint(0, num_grades - 1)
        score_row_values[missing_idx] = "x" # Replace a score with 'x'
        
        # Calculate the target mean and the value of x
        known_weighted_sum = 0
        for i, s_val in enumerate(scores_initial):
            if i != missing_idx:
                known_weighted_sum += s_val * weights_ratio[i]
        
        missing_weight = weights_ratio[missing_idx]
        
        # Generate a target mean that will result in a reasonable 'x'
        # The sum of all weights is 1.0
        # target_mean = (known_weighted_sum + x * missing_weight) / 1.0
        # x = (target_mean - known_weighted_sum) / missing_weight
        
        target_mean_val = round(random.uniform(65, 85), 1) 
        
        calculated_x = (target_mean_val - known_weighted_sum) / missing_weight
        calculated_x = round(calculated_x) 

        # Ensure the calculated x is within reasonable bounds (e.g., 0-100)
        # If not, generate a new problem (recursive call is a simple way)
        if not (0 <= calculated_x <= 100):
            return generate_weighted_mean_problem() 

        correct_answer = str(int(calculated_x))
        
        score_row = "| 分數 | " + " | ".join(score_row_values) + " |"
        weight_row = "| 比重 | " + " | ".join(weight_row_values) + " |"
        table_text = f"{header_row}<br>{divider_row}<br>{score_row}<br>{weight_row}"

        question_text = (
            f"某生本學期數學科的分數與其所占的比重如下表。<br>"
            f"{table_text}<br>"
            f"已知該生的數學科學期成績為 ${target_mean_val}$ 分，求 $x$ 的值。"
        )

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_geometric_mean_problem():
    """
    Generates a problem for calculating the geometric mean, often for growth rates.
    """
    num_years = random.randint(3, 5)
    
    rates_percent = []
    # Generate growth rates as percentages. Ensure (1+r) is positive.
    for _ in range(num_years):
        rate = random.randint(-80, 50) # Range from -80% to +50%
        # Ensure it's not too close to -100% to avoid (1+r) being too small or zero/negative
        if rate <= -95: # Very low negative rates can cause issues if they stack
            rate = random.randint(-90, -10) # Adjust to be safer
        rates_percent.append(rate)
        
    rates_decimal = [r / 100.0 for r in rates_percent]
    
    # Format rates for display, using \% for LaTeX math mode
    rates_display = [f"{r}\%" for r in rates_percent]
    rates_str = ", ".join(rates_display)

    # Calculate the product of (1 + r) terms
    product_term = 1.0
    for r in rates_decimal:
        product_term *= (1 + r)
    
    # If for some reason product_term became non-positive (shouldn't with current rate range)
    if product_term <= 0:
        return generate_geometric_mean_problem() # Retry

    # Geometric mean formula: (product)^(1/n) - 1
    geometric_mean = (product_term ** (1/num_years)) - 1
    
    # Convert to percentage and round to one decimal place
    geometric_mean_percent = geometric_mean * 100
    
    # Correct answer includes percentage symbol in LaTeX math mode
    correct_answer = f"{geometric_mean_percent:.1f}\%"
    
    question_text = (
        f"已知某地區人口近{num_years}年每年的成長率分別為${rates_str}$，"
        f"求此地區人口這{num_years}年的平均成長率。"
    )

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

# --- Main generation function ---
def generate(level=1):
    """
    Generates a problem related to arithmetic, weighted, or geometric mean.
    """
    problem_type = random.choice(['arithmetic_mean', 'weighted_mean', 'geometric_mean'])
    
    if problem_type == 'arithmetic_mean':
        return generate_arithmetic_mean_problem()
    elif problem_type == 'weighted_mean':
        return generate_weighted_mean_problem()
    else: # geometric_mean
        return generate_geometric_mean_problem()

# --- Check function ---
def check(user_answer, correct_answer):
    """
    Checks if the user's answer is correct, allowing for floating point comparisons
    and handling percentage symbols.
    """
    user_ans_str = user_answer.strip()
    correct_ans_str = correct_answer.strip()

    is_correct = False
    feedback = ""

    try:
        # Remove '%' for numeric comparison, but store if present
        user_has_percent = '%' in user_ans_str
        correct_has_percent = '%' in correct_ans_str

        user_val_str = user_ans_str.replace('%', '')
        correct_val_str = correct_ans_str.replace('%', '')

        user_val = float(user_val_str)
        correct_val = float(correct_val_str)
        
        # Check if percentage presence matches (e.g., if correct is X%, user should input X%)
        if user_has_percent != correct_has_percent:
            feedback = f"答案不正確。請注意答案是否需要百分比符號。正確答案應為：${correct_answer}$。"
            return {"correct": is_correct, "result": feedback, "next_question": True}

        # Allow for a small epsilon for floating point comparisons, considering 1 decimal place accuracy
        # 0.05 allows for answers like 1.4 or 1.3 to be close enough to 1.37
        if abs(user_val - correct_val) < 0.05: 
            is_correct = True
            feedback = f"完全正確！答案是 ${correct_answer}$。"
        else:
            feedback = f"答案不正確。您的答案為 ${user_answer}$，正確答案應為：${correct_answer}$。"

    except ValueError:
        # If conversion to float fails, it's definitely incorrect or malformed
        feedback = f"答案格式不正確或數值有誤。請確認您的答案為數字形式。正確答案應為：${correct_answer}$。"
    
    return {"correct": is_correct, "result": feedback, "next_question": True}