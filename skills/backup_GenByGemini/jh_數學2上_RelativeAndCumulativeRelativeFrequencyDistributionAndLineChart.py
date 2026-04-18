import random
import uuid
import os

# --- Helper Functions ---

def _create_distribution(num_groups_range=(5, 7), total_count_options=(20, 25, 40, 50, 80, 100), start_val_range=(30, 50), group_width_options=(5, 10)):
    """
    Generates a complete frequency distribution table.
    """
    num_groups = random.randint(*num_groups_range)
    total_count = random.choice(total_count_options)
    start_val = random.randint(*start_val_range)
    group_width = random.choice(group_width_options)

    # Generate frequencies with a slight bell curve tendency
    weights = [1, 2, 4, 5, 4, 2, 1]
    weights = weights[:num_groups]
    proportions = [w * random.uniform(0.8, 1.2) for w in weights]
    total_prop = sum(proportions)
    
    freqs_float = [(p / total_prop) * total_count for p in proportions]
    freqs = [int(f) for f in freqs_float]
    remainders = [f - i for f, i in zip(freqs_float, freqs)]
    
    diff = total_count - sum(freqs)
    
    # Distribute the difference based on largest remainders to ensure sum is correct
    for _ in range(diff):
        max_rem_idx = remainders.index(max(remainders))
        freqs[max_rem_idx] += 1
        remainders[max_rem_idx] = -1 # Prevent re-selection

    # Build the table data
    table = []
    cum_freq = 0
    
    for i in range(num_groups):
        lower = start_val + i * group_width
        upper = lower + group_width
        freq = freqs[i]
        rel_freq = (freq / total_count) * 100
        cum_freq += freq
        cum_rel_freq = (cum_freq / total_count) * 100
        
        row = {
            "group": f"{lower}∼{upper}", "lower": lower, "upper": upper, "freq": freq,
            "rel_freq": rel_freq, "cum_freq": cum_freq, "cum_rel_freq": cum_rel_freq
        }
        # Create clean string representations for display
        row['rel_freq_str'] = f"{rel_freq:.1f}".rstrip('0').rstrip('.')
        row['cum_rel_freq_str'] = f"{cum_rel_freq:.1f}".rstrip('0').rstrip('.')
        table.append(row)

    # Correct final cumulative percentage for potential rounding errors
    table[-1]['cum_rel_freq'] = 100.0
    table[-1]['cum_rel_freq_str'] = '100'

    return table, total_count

def _format_table(header, rows):
    """
    Formats data into a monospaced text table.
    """
    if not rows:
        return ""
    col_widths = [max(len(str(item)) for item in col) for col in zip(header, *rows)]
    
    header_line = " | ".join(f"{h:<{w}}" for h, w in zip(header, col_widths))
    separator = "-+-".join("-" * w for w in col_widths)
    row_lines = [" | ".join(f"{str(item):<{w}}" for item, w in zip(row, col_widths)) for row in rows]
    
    return f"```\n{header_line}\n{separator}\n" + "\n".join(row_lines) + "\n```"

def _get_scenario():
    """Returns a random context for the problem."""
    scenarios = [
        {"item": "數學測驗", "unit": "分"},
        {"item": "立定跳遠", "unit": "公分"},
        {"item": "週末讀書時間", "unit": "小時"},
        {"item": "每月購書量", "unit": "本"},
        {"item": "英語聽力測驗", "unit": "分"}
    ]
    return random.choice(scenarios)

# --- Problem Type Generators ---

def generate_read_relative_freq_table():
    """
    Problem Type: Read and interpret a given relative frequency table.
    """
    scenario = _get_scenario()
    data, _ = _create_distribution()
    
    header = [f"{scenario['item']}({scenario['unit']})", "相對次數(%)"]
    rows = [[row['group'], row['rel_freq_str']] for row in data]
    table_str = _format_table(header, rows)
    
    q_type = random.choice(['max_freq', 'sum_freq'])
    
    if q_type == 'max_freq':
        max_row = max(data, key=lambda x: x['rel_freq'])
        question_text = f"根據下表八年級某班的{scenario['item']}相對次數分配表，哪一組的相對次數最大？\n{table_str}"
        correct_answer = max_row['group']
    else: # sum_freq
        # Select 2 or 3 consecutive groups from the start
        num_groups_to_sum = random.randint(2, 3)
        groups_to_sum = data[:num_groups_to_sum]
        threshold = groups_to_sum[-1]['upper']
        total_rel_freq = sum(row['rel_freq'] for row in groups_to_sum)
        
        question_text = f"根據下表八年級某班的{scenario['item']}相對次數分配表，未滿 {threshold} {scenario['unit']}的學生，占全班人數的百分比(%)為多少？\n{table_str}"
        correct_answer = f"{total_rel_freq:.1f}".rstrip('0').rstrip('.')

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_table_completion():
    """
    Problem Type: Complete a table by calculating relative or cumulative relative frequencies.
    """
    scenario = _get_scenario()
    data, total_count = _create_distribution()
    
    task = random.choice(['rel_freq', 'cum_rel_freq'])
    
    if task == 'rel_freq':
        header = [f"{scenario['item']}({scenario['unit']})", "次數(人)", "相對次數(%)"]
        rows = [[row['group'], row['freq'], "(?)"] for row in data]
        table_str = _format_table(header, rows)
        question_text = f"下表為某班 {total_count} 位學生的{scenario['item']}次數分配表，請完成表格中的相對次數(%)部分。\n{table_str}\n(請由上到下依序作答，答案以逗號分隔)"
        correct_answer = ",".join([row['rel_freq_str'] for row in data])
    else: # cum_rel_freq
        header = [f"{scenario['item']}({scenario['unit']})", "相對次數(%)", "累積相對次數(%)"]
        rows = [[row['group'], row['rel_freq_str'], "(?)"] for row in data]
        table_str = _format_table(header, rows)
        question_text = f"下表為某班學生的{scenario['item']}相對次數分配表，請完成表格中的累積相對次數(%)部分。\n{table_str}\n(請由上到下依序作答，答案以逗號分隔)"
        correct_answer = ",".join([row['cum_rel_freq_str'] for row in data])
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_compare_two_groups():
    """
    Problem Type: Compare relative frequency vs. absolute numbers for two different groups.
    """
    scenario = _get_scenario()
    
    # Generate data for two classes with different total counts
    data_a, total_a = _create_distribution()
    total_b = random.choice([t for t in (20, 25, 40, 50) if t != total_a])
    data_b, _ = _create_distribution(
        num_groups_range=(len(data_a), len(data_a)),
        total_count_options=[total_b],
        start_val_range=(data_a[0]['lower'], data_a[0]['lower']),
        group_width_options=[data_a[0]['upper'] - data_a[0]['lower']]
    )
    
    # Create table strings for both
    header = [f"{scenario['item']}({scenario['unit']})", "相對次數(%)"]
    rows_a = [[row['group'], row['rel_freq_str']] for row in data_a]
    rows_b = [[row['group'], row['rel_freq_str']] for row in data_b]
    table_a_str = f"甲班 (共 {total_a} 人)\n" + _format_table(header, rows_a)
    table_b_str = f"乙班 (共 {total_b} 人)\n" + _format_table(header, rows_b)
    
    # Choose a threshold (e.g., failing grade)
    threshold_idx = random.randint(1, 3)
    threshold = data_a[threshold_idx]['upper']
    
    # Calculate values for comparison
    rel_freq_a = data_a[threshold_idx]['cum_rel_freq']
    rel_freq_b = data_b[threshold_idx]['cum_rel_freq']
    
    count_a = data_a[threshold_idx]['cum_freq']
    count_b = data_b[threshold_idx]['cum_freq']
    
    # Determine answers
    ans1 = "甲班" if rel_freq_a > rel_freq_b else "乙班"
    if abs(rel_freq_a - rel_freq_b) < 0.01: ans1 = "一樣"
    
    ans2 = "甲班" if count_a > count_b else "乙班"
    if count_a == count_b: ans2 = "一樣"

    question_text = (
        f"右表為甲、乙兩班某次{scenario['item']}的相對次數分配表。\n{table_a_str}\n{table_b_str}\n"
        f"回答下列問題："
        f"⑴ 哪一班在未滿 {threshold} {scenario['unit']}的「相對次數」較大？\n"
        f"⑵ 哪一班在未滿 {threshold} {scenario['unit']}的「人數」較多？\n"
        f"(請依序回答 ⑴ 和 ⑵，答案以逗號分隔，例如：甲班,乙班)"
    )
    correct_answer = f"{ans1},{ans2}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_read_cumulative_chart():
    """
    Problem Type: Interpret data from a cumulative relative frequency chart (presented as a table).
    """
    scenario = _get_scenario()
    data, total_count = _create_distribution()
    
    header = [f"未滿({scenario['unit']})", "累積相對次數(%)"]
    rows = [[row['upper'], row['cum_rel_freq_str']] for row in data]
    table_str = _format_table(header, rows)
    
    q_type = random.choice(['below', 'above', 'between', 'count'])
    
    if q_type == 'below':
        chosen_row = random.choice(data)
        threshold = chosen_row['upper']
        question_text = f"根據下方{scenario['item']}的累積相對次數分配表，未滿 {threshold} {scenario['unit']}的學生占全體的百分比(%)為多少？\n{table_str}"
        correct_answer = chosen_row['cum_rel_freq_str']
    elif q_type == 'above':
        chosen_row = random.choice(data[:-1]) # Don't pick the last one (always 0%)
        threshold = chosen_row['upper']
        percent_above = 100 - chosen_row['cum_rel_freq']
        question_text = f"根據下方{scenario['item']}的累積相對次數分配表，{threshold} {scenario['unit']}以上(含)的學生占全體的百分比(%)為多少？\n{table_str}"
        correct_answer = f"{percent_above:.1f}".rstrip('0').rstrip('.')
    elif q_type == 'count':
        chosen_row = random.choice(data[:-1])
        threshold = chosen_row['upper']
        percent_above = 100 - chosen_row['cum_rel_freq']
        num_above = round(total_count * percent_above / 100)
        question_text = f"已知全班共 {total_count} 人，根據下方{scenario['item']}的累積相對次數分配表，成績在 {threshold} {scenario['unit']}以上(含)的學生有多少人？\n{table_str}"
        correct_answer = str(num_above)
    else: # between
        idx1 = random.randint(0, len(data) - 2)
        idx2 = random.randint(idx1 + 1, len(data) - 1)
        row1 = data[idx1]
        row2 = data[idx2]
        lower_bound = row1['upper']
        upper_bound = row2['upper']
        
        # Relative frequency of the interval is the difference in cumulative frequencies
        percent_between = data[idx2]['cum_rel_freq'] - data[idx1]['cum_rel_freq']
        
        question_text = f"根據下方{scenario['item']}的累積相對次數分配表，成績介於 {lower_bound}∼{upper_bound} {scenario['unit']}的學生占全體的百分比(%)為多少？\n{table_str}"
        correct_answer = f"{percent_between:.1f}".rstrip('0').rstrip('.')

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_compare_two_charts():
    """
    Problem Type: Compare two cumulative relative frequency distributions.
    """
    scenario = _get_scenario()
    
    # Generate data for two classes
    data_a, _ = _create_distribution()
    data_b, _ = _create_distribution(
        num_groups_range=(len(data_a), len(data_a)),
        start_val_range=(data_a[0]['lower'], data_a[0]['lower']),
        group_width_options=[data_a[0]['upper'] - data_a[0]['lower']]
    )
    
    header = [f"未滿({scenario['unit']})", "甲班 累積相對(%)", "乙班 累積相對(%)"]
    rows = []
    for r_a, r_b in zip(data_a, data_b):
        rows.append([r_a['upper'], r_a['cum_rel_freq_str'], r_b['cum_rel_freq_str']])
    table_str = _format_table(header, rows)
    
    q_type = random.choice(['compare_interval', 'compare_threshold'])
    
    if q_type == 'compare_interval':
        idx1 = random.randint(0, len(data_a) - 2)
        idx2 = idx1 + 1
        
        lower_bound = data_a[idx1]['upper'] if idx1 >= 0 else data_a[0]['lower']
        upper_bound = data_a[idx2]['upper']
        
        cum_rel_a1 = data_a[idx1]['cum_rel_freq'] if idx1 >= 0 else 0
        cum_rel_b1 = data_b[idx1]['cum_rel_freq'] if idx1 >= 0 else 0
        
        rel_freq_a = data_a[idx2]['cum_rel_freq'] - cum_rel_a1
        rel_freq_b = data_b[idx2]['cum_rel_freq'] - cum_rel_b1

        answer = "甲班" if rel_freq_a > rel_freq_b else "乙班"
        if abs(rel_freq_a - rel_freq_b) < 0.01: answer = "一樣多"

        question_text = f"下圖是甲、乙兩班{scenario['item']}的累積相對次數分配表。\n{table_str}\n在 {lower_bound}∼{upper_bound} {scenario['unit']} 這一組，哪一班的相對次數較高？"
        correct_answer = answer
    else: # compare_threshold
        idx = random.randint(1, len(data_a) - 2)
        threshold = data_a[idx]['upper']
        
        pass_rate_a = 100 - data_a[idx]['cum_rel_freq']
        pass_rate_b = 100 - data_b[idx]['cum_rel_freq']

        answer = "甲班" if pass_rate_a > pass_rate_b else "乙班"
        if abs(pass_rate_a - pass_rate_b) < 0.01: answer = "一樣高"
        
        question_text = f"下圖是甲、乙兩班{scenario['item']}的累積相對次數分配表。\n{table_str}\n若以 {threshold} {scenario['unit']} 為及格標準，哪一班的及格比例（{threshold} {scenario['unit']}以上）較高？"
        correct_answer = answer
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    Generates a question for the skill: Relative and Cumulative Relative Frequency Distribution.
    """
    problem_type = random.choice([
        'read_relative_freq_table',
        'table_completion',
        'compare_two_groups',
        'read_cumulative_chart',
        'compare_two_charts'
    ])
    
    if problem_type == 'read_relative_freq_table':
        return generate_read_relative_freq_table()
    elif problem_type == 'table_completion':
        return generate_table_completion()
    elif problem_type == 'compare_two_groups':
        return generate_compare_two_groups()
    elif problem_type == 'read_cumulative_chart':
        return generate_read_cumulative_chart()
    else: # 'compare_two_charts'
        return generate_compare_two_charts()


def check(user_answer, correct_answer):
    """
    Checks if the user's answer is correct.
    """
    user_ans_str = str(user_answer).strip().replace('%', '').replace(' ', '')
    correct_ans_str = str(correct_answer).strip().replace('%', '').replace(' ', '')

    is_correct = False
    
    # Handle comma-separated answers
    if ',' in correct_ans_str:
        user_parts = [p.strip() for p in user_ans_str.split(',')]
        correct_parts = [p.strip() for p in correct_ans_str.split(',')]
        
        if len(user_parts) == len(correct_parts):
            match = True
            for u_part, c_part in zip(user_parts, correct_parts):
                try:
                    # Try numeric comparison first
                    if abs(float(u_part) - float(c_part)) > 0.01:
                        match = False
                        break
                except ValueError:
                    # Fallback to string comparison
                    if u_part.lower() != c_part.lower():
                        match = False
                        break
            if match:
                is_correct = True
    else:
        # Handle single answers
        if user_ans_str.lower() == correct_ans_str.lower():
            is_correct = True
        else:
            try:
                # Try numeric comparison for robustness
                if abs(float(user_ans_str) - float(correct_ans_str)) < 0.01:
                    is_correct = True
            except (ValueError, TypeError):
                pass

    if is_correct:
        result_text = f"完全正確！答案是 {correct_answer}。"
    else:
        result_text = f"答案不正確。正確答案應為：{correct_answer}"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}