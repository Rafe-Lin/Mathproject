import random
import math
from fractions import Fraction

def _format_number(num):
    """Helper function to format a number, returning an int if it's a whole number."""
    if isinstance(num, float) and num.is_integer():
        return int(num)
    return num

def _calculate_quartile_value(sorted_data, k):
    """
    Calculates the value of the k-th quartile (k=1, 2, 3) based on the standard definition for this curriculum.
    The definition is: a = N * k/4. If a is integer, Qk is avg of a-th and (a+1)-th value.
    If a is not integer, b = floor(a) + 1, Qk is the b-th value.

    Args:
        sorted_data (list): A list of numbers sorted in ascending order.
        k (int): The quartile to calculate (1 for Q1, 2 for Q2, 3 for Q3).

    Returns:
        int or float: The calculated quartile value.
    """
    n = len(sorted_data)
    pos = n * k / 4.0
    
    if pos.is_integer():
        # If 'a' is an integer, Qk is the average of the a-th and (a+1)-th data points.
        # Python lists are 0-indexed, so we use a-1 and a for the a-th and (a+1)-th elements.
        index1 = int(pos) - 1
        index2 = int(pos)
        value = (sorted_data[index1] + sorted_data[index2]) / 2.0
    else:
        # If 'a' is not an integer, take its integer part plus 1 to get 'b'. Qk is the b-th data point.
        # b = floor(a) + 1. In 0-indexing, this corresponds to index floor(a).
        index = math.floor(pos)
        value = sorted_data[index]
        
    return _format_number(value)

def generate_calculate_from_list():
    """
    Generates a question asking to find Q1, Q2, or Q3 from a raw list of numbers.
    Corresponds to example: "已知一群遊客的年齡如下..."
    """
    n = random.randint(10, 20)
    data_pool = range(10, 100)
    data = sorted([random.choice(data_pool) for _ in range(n)])
    
    question_data = data[:]
    random.shuffle(question_data)
    
    k = random.randint(1, 3)
    quartile_name = f"Q_{k}"
    
    question_text = f"已知一群資料如下：{', '.join(map(str, question_data))}。<br>請求出這群資料的 ${quartile_name}$ 為多少？"
    
    correct_answer = _calculate_quartile_value(data, k)
    
    return {
        "question_text": question_text,
        "answer": str(correct_answer),
        "correct_answer": str(correct_answer)
    }

def generate_calculate_from_freq_table():
    """
    Generates a question asking to find Q1, Q2, or Q3 from a frequency distribution table.
    Corresponds to example: "好康連鎖超市共聘有 50 位員工..."
    """
    num_groups = random.randint(5, 8)
    start_value = random.randint(25000, 40000) // 1000 * 1000
    step = random.randint(1, 5) * 1000
    values = sorted([start_value + i * step + random.randint(-500, 500) // 500 * 500 for i in range(num_groups)])
    freqs = [random.randint(2, 15) for _ in range(num_groups)]
    
    full_data = []
    n = 0
    for i in range(num_groups):
        full_data.extend([values[i]] * freqs[i])
        n += freqs[i]
        
    while n < 25:
        new_val = max(values) + step
        new_freq = random.randint(2, 8)
        values.append(new_val)
        freqs.append(new_freq)
        full_data.extend([new_val] * new_freq)
        n += new_freq
        
    k = random.randint(1, 3)
    quartile_name = f"Q_{k}"
    unit = random.choice(["元", "分"])
    
    value_line = f"數值({unit}): {', '.join(map(str, values))}"
    freq_line = f"次數(人): {', '.join(map(str, freqs))}"
    
    question_text = f"下表為一群資料的次數分配表，則此資料的 ${quartile_name}$ 為多少 {unit}？<br>{value_line}<br>{freq_line}"
    
    correct_answer = _calculate_quartile_value(full_data, k)
    
    return {
        "question_text": question_text,
        "answer": str(correct_answer),
        "correct_answer": str(correct_answer)
    }

def generate_find_quartile_group():
    """
    Generates a question asking to find which group a quartile falls into.
    Corresponds to example: "...學生身高的次數分配直方圖..."
    """
    num_groups = random.randint(5, 8)
    start_val = random.randint(130, 160)
    step = random.choice([5, 10])
    
    groups = [f"{start_val + i*step}∼{start_val + (i+1)*step}" for i in range(num_groups)]
    freqs = [random.randint(1, 12) for _ in range(num_groups)]
    n = sum(freqs)

    k = random.randint(1, 3)
    quartile_name = f"Q_{k}"
    unit = random.choice(["分", "公分", "公斤"])

    group_line = f"組別({unit}): {', '.join(groups)}"
    freq_line = f"次數(人): {', '.join(map(str, freqs))}"
    question_text = f"下表為一群資料的次數分配表，則此資料的 ${quartile_name}$ 落在下列哪一組？<br>{group_line}<br>{freq_line}"

    # For "find the group" questions, the reference examples consistently find the rank by rounding up.
    # e.g., position = 25.5 -> 26th rank. This is equivalent to ceil(position).
    pos = n * k / 4.0
    target_rank = math.ceil(pos)

    cumulative_freq = 0
    correct_answer = ""
    for i in range(num_groups):
        cumulative_freq += freqs[i]
        if target_rank <= cumulative_freq:
            correct_answer = groups[i]
            break
            
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_interpret_median():
    """
    Generates a question about interpreting the median (Q2) and proportions.
    Corresponds to example: "康強國中舉辦音樂比賽..."
    """
    n = random.randint(7, 12)
    data = sorted([random.randint(20, 50) for _ in range(n)])
    median = _calculate_quartile_value(data, 2)
    
    direction = random.choice(["以下", "以上"])
    
    if direction == "以下":
        count = sum(1 for x in data if x <= median)
        question_text = f"一群資料由小到大排序為 {', '.join(map(str, data))}，則中位數{direction} (含) 的資料占全部資料的比例為多少？"
    else: # "以上"
        count = sum(1 for x in data if x >= median)
        question_text = f"一群資料由小到大排序為 {', '.join(map(str, data))}，則中位數{direction} (含) 的資料占全部資料的比例為多少？"

    answer_fraction = Fraction(count, n)
    correct_answer = f"{answer_fraction.numerator}/{answer_fraction.denominator}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    Generates a question about quartiles, covering various calculation and interpretation scenarios.
    """
    problem_types = [
        generate_calculate_from_list,
        generate_calculate_from_freq_table,
        generate_find_quartile_group,
        generate_interpret_median
    ]
    
    generator_func = random.choice(problem_types)
    return generator_func()

def check(user_answer, correct_answer):
    """
    Checks if the user's answer is correct for quartile problems.
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    
    is_correct = (user_answer == correct_answer)

    # Allow for floating point comparison for numerical answers
    if not is_correct:
        try:
            if float(user_answer) == float(correct_answer):
                is_correct = True
        except (ValueError, TypeError):
            # Handles cases where answers are not numbers (e.g., "1/2", "155∼160")
            pass

    if is_correct:
        result_text = f"完全正確！答案是 ${correct_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer}$。"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}