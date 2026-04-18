import random
from fractions import Fraction
import math

def _calculate_median_from_raw_data(data):
    """Calculates the median from a list of raw data."""
    sorted_data = sorted(data)
    n = len(sorted_data)
    if n % 2 == 1:
        # Odd number of data points
        median = sorted_data[n // 2]
    else:
        # Even number of data points
        mid1 = sorted_data[n // 2 - 1]
        mid2 = sorted_data[n // 2]
        median = (mid1 + mid2) / 2.0
    
    if median == int(median):
        return int(median)
    else:
        return Fraction(median) # Use Fraction for X.5 cases

def _generate_median_raw_data():
    """Generates a problem for calculating the median from raw data."""
    num_elements = random.randint(5, 12) # Between 5 and 12 elements
    # Generate numbers that might include repeats
    data = [random.randint(1, 100) for _ in range(num_elements)]
    
    random.shuffle(data) # Shuffle to make it unsorted initially

    # Format the data for the question text
    data_str = ", ".join(map(str, data))

    median_val = _calculate_median_from_raw_data(data)

    question_text = f"求下列各數據的中位數：<br>${data_str}$"
    correct_answer = str(median_val)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def _calculate_percentile_from_grouped_data(values, frequencies, k):
    """
    Calculates the k-th percentile from grouped frequency data.
    values: list of distinct data values (sorted)
    frequencies: list of counts for each value
    k: the percentile (e.g., 25 for Q1, 50 for Q2, 75 for Q3)
    """
    N = sum(frequencies)
    
    cumulative_frequencies = []
    current_cumulative = 0
    for freq in frequencies:
        current_cumulative += freq
        cumulative_frequencies.append(current_cumulative)

    index_pos_float = N * k / 100.0

    if index_pos_float.is_integer():
        # Case 1: N * k / 100 is an integer (e.g., 150)
        # P_k = (x_index_pos + x_{index_pos + 1}) / 2
        
        # Find x_index_pos (the value at the exact index_pos)
        val_at_index_pos = None
        for i, cf in enumerate(cumulative_frequencies):
            if cf >= index_pos_float:
                val_at_index_pos = values[i]
                break
        
        # Find x_{index_pos + 1} (the value at the next index)
        val_at_index_pos_plus_1 = None
        for i, cf in enumerate(cumulative_frequencies):
            if cf >= index_pos_float + 1:
                val_at_index_pos_plus_1 = values[i]
                break

        # This should not happen with well-formed data and k < 100
        if val_at_index_pos is None or val_at_index_pos_plus_1 is None:
            # Fallback for unexpected data, though ideally data generation prevents this
            # In practical problems, k will not lead to index_pos = N
            # If it did, it means x_N and x_{N+1} is requested where x_{N+1} doesn't exist
            # but standard percentile definitions usually handle this with interpolation within data range.
            # For educational context, we assume sufficient data points exist.
            return 0 # Or raise an error
            
        percentile_value = (val_at_index_pos + val_at_index_pos_plus_1) / 2.0

    else:
        # Case 2: N * k / 100 is not an integer (e.g., 87.5)
        # P_k = x_{floor(N * k / 100) + 1}
        target_index = math.floor(index_pos_float) + 1
        
        percentile_value = None
        for i, cf in enumerate(cumulative_frequencies):
            if cf >= target_index:
                percentile_value = values[i]
                break
        
        if percentile_value is None:
            return 0 # Or raise an error

    # Convert to Fraction if it's a simple half, otherwise int/float
    if percentile_value == int(percentile_value):
        return int(percentile_value)
    elif abs(percentile_value - (int(percentile_value) + 0.5)) < 1e-9: # Check for X.5
        return Fraction(percentile_value)
    else:
        return percentile_value # Return float if not a simple half

def _generate_grouped_data_problem():
    """Generates a problem for calculating percentile/quartile from grouped frequency data."""
    
    scenario = random.choice(['進球數（次）', '薪資（千元）', '考試分數（分）', '銷售額（萬元）'])
    unit = scenario.split('（')[-1][:-1] if '（' in scenario else ''
    
    # Generate values (categories)
    num_categories = random.randint(5, 7)
    if scenario == '薪資（千元）':
        values = sorted(random.sample(range(20, 60, 2), num_categories)) # Even numbers for salaries
    elif scenario == '考試分數（分）':
        values = sorted(random.sample(range(50, 100, 5), num_categories))
    else: # 進球數, 銷售額 etc.
        values = list(range(0, num_categories))

    # Generate frequencies that sum up to total_N
    total_N = random.randint(80, 250)
    
    # Create num_categories-1 distinct breakpoints to divide total_N
    if num_categories > 1:
        break_points = sorted(random.sample(range(1, total_N), num_categories - 1))
    else:
        break_points = []
    
    break_points = [0] + break_points + [total_N]
    
    frequencies = []
    for i in range(1, len(break_points)):
        freq = break_points[i] - break_points[i-1]
        # Ensure minimum frequency is 1 if it somehow became 0 (shouldn't with distinct breakpoints)
        frequencies.append(max(1, freq))
    
    # Recalculate total_N based on actual frequencies if adjustments were made, otherwise it's original total_N
    actual_total_N = sum(frequencies)

    # Decide what to ask for: Percentile P_k or Quartile Q_x
    question_target_type = random.choice(['percentile', 'quartile'])
    
    k_val = None
    if question_target_type == 'percentile':
        # Pick k such that N*k/100 can be integer or non-integer
        possible_ks = [10, 20, 30, 35, 40, 60, 65, 70, 80, 90]
        k_val = random.choice(possible_ks)
        target_name = f"$P_{{{k_val}}}$"
        
    else: # 'quartile'
        quartile_type = random.choice([1, 2, 3])
        if quartile_type == 1: k_val = 25
        elif quartile_type == 2: k_val = 50
        else: k_val = 75
        target_name = f"$Q_{{{quartile_type}}}$"

    correct_answer_val = _calculate_percentile_from_grouped_data(values, frequencies, k_val)

    # Format the table for question text using <br> for new lines outside math blocks
    header = f"| {scenario} | {' | '.join(map(str, values))} |"
    separator = "| :--- |" + " :--- |" * len(values)
    freq_row = f"| 人數（人） | {' | '.join(map(str, frequencies))} |"
    
    question_text = (
        f"某校有${actual_total_N}$位學生的{scenario.split('（')[0]}數如下表。<br>"
        "求這組數據的下列百分位數或四分位數。<br>"
        f"{header}<br>"
        f"{separator}<br>"
        f"{freq_row}<br>"
        f"求 {target_name}。"
    )
    
    correct_answer_str = str(correct_answer_val)
    if unit:
        correct_answer_str += f"（{unit}）" # Add unit back to answer text only, not numerical answer.

    return {
        "question_text": question_text,
        "answer": str(correct_answer_val), # Numerical part for internal check
        "correct_answer": correct_answer_str # Full string with unit for display
    }

def generate(level=1):
    """
    生成中位數與百分位數相關題目。
    包含：
    1. 原始數據的中位數計算 (奇數/偶數個數據)
    2. 分組頻率數據的百分位數計算 (N*k/100 為整數/非整數)
    3. 分組頻率數據的四分位數計算
    """
    
    problem_type = random.choice(['median_raw', 'grouped_data_percentile_quartile'])
    
    if problem_type == 'median_raw':
        return _generate_median_raw_data()
    elif problem_type == 'grouped_data_percentile_quartile':
        return _generate_grouped_data_problem()

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = str(user_answer).strip()
    correct_answer = str(correct_answer).strip()
    
    is_correct = False
    feedback = ""

    # Try exact string match first (e.g., for answers with units)
    if user_answer == correct_answer:
        is_correct = True
    else:
        # Attempt numerical comparison
        try:
            # Extract numerical part from correct_answer if it contains units
            correct_num_str = correct_answer
            if '（' in correct_answer and '）' in correct_answer:
                correct_num_str = correct_answer.split('（')[0].strip()

            user_num = float(Fraction(user_answer)) # Handle fractions like "3.5" or "7/2"
            correct_num = float(Fraction(correct_num_str))

            if abs(user_num - correct_num) < 1e-9: # Compare floats with tolerance
                is_correct = True
        except ValueError:
            pass # Not a straightforward numerical answer

    if is_correct:
        feedback = f"完全正確！答案是 ${correct_answer}$。"
    else:
        # Ensure correct_answer is displayed with LaTeX formatting if it was originally formatted
        display_correct_answer = correct_answer
        # If it was "3.5（次）", format it nicely like "$3.5$（次）" for feedback.
        if '（' in correct_answer and '）' in correct_answer:
             num_part = correct_answer.split('（')[0].strip()
             unit_part = '（' + correct_answer.split('（')[1]
             display_correct_answer = f"${num_part}${unit_part}"
        else:
             display_correct_answer = f"${correct_answer}$"

        feedback = f"答案不正確。正確答案應為：{display_correct_answer}"
    
    return {"correct": is_correct, "result": feedback, "next_question": True}