import random
import math

# Helper function to calculate mean, variance, and standard deviation
def _calculate_stats(data):
    n = len(data)
    if n == 0:
        return 0.0, 0.0, 0.0 # Return floats for consistency when data is empty

    mu = sum(data) / n

    # Using population variance formula (divide by N), as per reference examples
    # Sum of squared differences from the mean
    sum_sq_diff = sum([(x - mu)**2 for x in data])
    sigma_sq = sum_sq_diff / n

    sigma = math.sqrt(sigma_sq)

    return mu, sigma_sq, sigma

# Helper function to format numbers to string, handling integers cleanly
def _format_number(num, precision=2):
    # Check if number is effectively an integer within a small epsilon tolerance
    if abs(num - round(num)) < 1e-9:
        return str(int(round(num)))
    return f"{num:.{precision}f}"

def _generate_calculation_problem(level):
    num_count = random.randint(4, 6) # Default for level 1
    num_range_low = -10
    num_range_high = 10

    if level >= 2:
        num_count = random.randint(5, 8) # More numbers for higher levels
        num_range_low = -20
        num_range_high = 20 # Wider range for higher levels

    data = []
    # Generate unique random integers
    while len(data) < num_count:
        num = random.randint(num_range_low, num_range_high)
        if num not in data:
            data.append(num)
    data.sort() # Present data in sorted order as in examples

    mu, sigma_sq, sigma = _calculate_stats(data)

    formatted_data = ', '.join(map(str, data))

    # Define possible statistics to ask for
    possible_questions = [
        {'label': r"算術平均數$\mu$", 'value': mu},
        {'label': r"變異數$\sigma^2$", 'value': sigma_sq},
        {'label': r"標準差$\sigma$", 'value': sigma}
    ]

    # Randomly select one statistic to ask for
    target_q = random.choice(possible_questions)
    
    question_text = f"求以下{num_count}個數據的{target_q['label']}。<br>${formatted_data}$"
    correct_answer_str = _format_number(target_q['value'])

    return {
        "question_text": question_text,
        "answer": correct_answer_str, # Expected user input type (e.g., a number)
        "correct_answer": correct_answer_str
    }

def _generate_conceptual_problem():
    # List of true/false statements related to variance and standard deviation concepts
    problems = [
        {"question_stem": r"若所有數據的值都相等，則其標準差為$0$。", "answer": "O"},
        {"question_stem": r"標準差越大代表數據越集中。", "answer": "X"}, # Incorrect: greater std dev means more dispersed
        {"question_stem": r"離均差平方和越大，表示數據越分散。", "answer": "O"},
        {"question_stem": r"母體變異數是離均差平方和的平均值。", "answer": "O"},
        {"question_stem": r"數據的集中程度與其標準差大小呈正相關。", "answer": "X"}, # Incorrect: inversely related
        {"question_stem": r"將所有數據皆加上一個常數，其標準差會改變。", "answer": "X"}, # Standard deviation is invariant to shifts
    ]
    
    problem = random.choice(problems)
    
    question_text = f"下列敘述對的打「O」，錯的打「X」。<br>□{problem['question_stem']}"
    
    return {
        "question_text": question_text,
        "answer": problem['answer'], # Expected user input is 'O' or 'X'
        "correct_answer": problem['answer']
    }

def generate(level=1):
    """
    生成「變異數與標準差」相關題目。
    包含：
    1. 計算題：給定數據，計算平均數、變異數或標準差。
    2. 觀念題：判斷變異數與標準差相關敘述的對錯。
    """
    problem_type = random.choice(['calculation', 'conceptual']) 

    if problem_type == 'calculation':
        return _generate_calculation_problem(level)
    elif problem_type == 'conceptual':
        return _generate_conceptual_problem()

def check(user_answer, correct_answer):
    """
    檢查使用者答案是否正確。
    """
    user_answer_processed = user_answer.strip().upper()
    correct_answer_processed = correct_answer.strip().upper()

    is_correct = False
    result_text = ""

    # Check for conceptual problems (O/X answers)
    if correct_answer_processed in ["O", "X"]:
        if user_answer_processed == correct_answer_processed:
            is_correct = True
            result_text = f"完全正確！答案是 {correct_answer_processed}。"
        else:
            result_text = f"答案不正確。正確答案應為：{correct_answer_processed}"
    else: # Check for calculation problems (numeric answers)
        try:
            user_val = float(user_answer_processed)
            correct_val = float(correct_answer_processed)
            
            # Use a small tolerance for floating point comparison (e.g., for answers rounded to 2 decimal places)
            tolerance = 1e-2 # Allows for slight rounding differences, e.g., 2.50 vs 2.51
            if abs(user_val - correct_val) < tolerance:
                is_correct = True
                result_text = f"完全正確！答案是 ${correct_answer_processed}$。"
            else:
                result_text = f"答案不正確。正確答案應為：${correct_answer_processed}$"
        except ValueError:
            # Handle cases where user input is not a valid number
            result_text = f"您的輸入 '{user_answer}' 無法辨識為數字。正確答案應為：${correct_answer_processed}$"
            
    return {"correct": is_correct, "result": result_text, "next_question": True}