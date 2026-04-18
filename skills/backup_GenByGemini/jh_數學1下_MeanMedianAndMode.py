import random

def _format_number(n):
    """
    將數字格式化為整數或浮點數字串，避免出現 '.0'。
    """
    if isinstance(n, str):
        return n
    if n == int(n):
        return str(int(n))
    else:
        # 最多顯示到小數點後兩位，並移除末尾的 0 和 . 
        return f"{n:.2f}".rstrip('0').rstrip('.')

def generate(level=1):
    """
    生成「平均數、中位數與眾數」相關題目 (標準 LaTeX 範本)。
    """
    problem_type = random.choice(['mean', 'median', 'mode'])
    
    if problem_type == 'mean':
        return generate_mean_problem()
    elif problem_type == 'median':
        return generate_median_problem()
    else: # mode
        return generate_mode_problem()

def generate_mean_problem():
    """生成不同類型的平均數問題。"""
    mean_type = random.choice(['simple', 'base_value', 'weighted', 'grouped'])
    
    if mean_type == 'simple':
        return generate_simple_mean()
    elif mean_type == 'base_value':
        return generate_base_value_mean()
    elif mean_type == 'weighted':
        return generate_weighted_mean()
    else: # grouped
        return generate_grouped_mean()

def generate_median_problem():
    """生成不同類型的中位數問題。"""
    median_type = random.choice(['simple', 'frequency_table', 'grouped'])
    
    if median_type == 'simple':
        return generate_simple_median()
    elif median_type == 'frequency_table':
        return generate_frequency_table_median()
    else: # grouped
        return generate_grouped_median()

def generate_mode_problem():
    """生成不同類型的眾數問題。"""
    mode_type = random.choice(['categorical', 'numerical'])
    
    if mode_type == 'categorical':
        return generate_categorical_mode()
    else: # numerical
        return generate_numerical_mode()

# --- 平均數生成器 ---

def generate_simple_mean():
    num_items = random.randint(4, 6)
    data = random.sample(range(10, 51), num_items)
    total = sum(data)
    avg = total / num_items

    data_str = '、'.join(map(str, data))
    item_name = random.choice(['張生日卡片', '本書', '件衣服', '顆蘋果'])
    unit = '元'
    
    question_text = f"小華去商店買了 ${num_items}$ {item_name}，價格依序為 ${data_str}$ {unit}，則這 ${num_items}$ {item_name}的平均價格為多少{unit}？"
    correct_answer = _format_number(avg)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_base_value_mean():
    base_score = random.choice([80, 85, 90])
    num_subjects = 5
    subjects = random.sample(['國文', '英語', '數學', '社會', '自然'], k=num_subjects)
    diffs = [random.randint(-8, 8) for _ in range(num_subjects)]
    
    while sum(diffs) == 0:
        diffs = [random.randint(-8, 8) for _ in range(num_subjects)]
        
    sum_diffs = sum(diffs)
    avg_diff = sum_diffs / num_subjects
    final_avg = base_score + avg_diff
    
    table_header = f"科 目: ${', '.join(subjects)}"
    diff_strs = [f"+{d}" if d >= 0 else str(d) for d in diffs]
    table_values = f"與目標分數的差距: ${', '.join(diff_strs)}"
    
    question_text = (
        f"小明給自己設定目標為 ${num_subjects}$ 科平均 ${base_score}$ 分。<br>"
        f"最後他得到的分數與目標分數的差距如下表，則小明此次段考的 ${num_subjects}$ 科平均分數為多少分？<br>"
        f"{table_header}<br>{table_values}"
    )
    correct_answer = _format_number(final_avg)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_weighted_mean():
    num_groups = random.randint(4, 5)
    header_options = [("課外讀物", "本"), ("進球數", "球"), ("答對題數", "題")]
    item_name, unit = random.choice(header_options)
    values_header = f"{item_name}({unit})"
    freq_header = "次數(人)"
    
    values = sorted(random.sample(range(1, 11), num_groups))
    freqs = [random.randint(2, 12) for _ in range(num_groups)]
    
    total_items = sum(freqs)
    weighted_sum = sum(v * f for v, f in zip(values, freqs))
    avg = weighted_sum / total_items
    
    table_values_header = f"{values_header}: ${', '.join(map(str, values))}"
    table_freqs_header = f"{freq_header}: ${', '.join(map(str, freqs))}"
    
    question_text = (
        f"某班級的統計結果如下表，則該班級每人平均{item_name}為多少{unit}？<br>"
        f"{table_values_header}<br>{table_freqs_header}"
    )
    correct_answer = _format_number(avg)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_grouped_mean():
    num_groups = 5
    start = random.choice([40, 50, 60])
    step = 10
    groups = [f"{s}∼{s+step}" for s in range(start, start + num_groups*step, step)]
    midpoints = [s + step/2 for s in range(start, start + num_groups*step, step)]
    freqs = [random.randint(2, 10) for _ in range(num_groups)]
    
    total_items = sum(freqs)
    weighted_sum = sum(m * f for m, f in zip(midpoints, freqs))
    avg = weighted_sum / total_items
    
    header = "分數(分)"
    freq_header = "次數(人)"
    
    table_header = f"{header}: ${', '.join(groups)}"
    table_freqs = f"{freq_header}: ${', '.join(map(str, freqs))}"
    
    question_text = (
        f"下表為某班數學測驗分數次數分配表，則該班學生的平均分數為多少分？<br>"
        f"{table_header}<br>{table_freqs}"
    )
    correct_answer = _format_number(avg)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

# --- 中位數生成器 ---

def generate_simple_median():
    is_odd = random.choice([True, False])
    num_items = random.randint(4, 6) * 2 - (1 if is_odd else 0)
    data = [random.randint(1, 50) for _ in range(num_items)]
    sorted_data = sorted(data)
    
    if is_odd:
        median = sorted_data[num_items // 2]
    else:
        mid1 = sorted_data[num_items // 2 - 1]
        mid2 = sorted_data[num_items // 2]
        median = (mid1 + mid2) / 2
        
    data_str = '、'.join(map(str, data))
    item, unit = random.choice([("騎單車時間", "小時"), ("練習時數", "小時"), ("每日花費", "元")])
    
    question_text = f"已知一組資料為 ${num_items}$ 筆{item}紀錄：${data_str}$。<br>請問這組資料的中位數為多少{unit}？"
    correct_answer = _format_number(median)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_frequency_table_median():
    num_groups = random.randint(5, 7)
    item, unit = random.choice([("跑走時間", "分鐘"), ("閱讀書本數", "本"), ("失誤次數", "次")])
    item_header = f"{item}({unit})"
    
    values = sorted(random.sample(range(5, 21), num_groups))
    freqs = [random.randint(2, 10) for _ in range(num_groups)]
    total_count = sum(freqs)
            
    if total_count % 2 == 0: # 偶數
        pos1, pos2 = total_count // 2, total_count // 2 + 1
        median_val1, median_val2 = -1, -1
        cumulative_freq = 0
        for val, freq in zip(values, freqs):
            cumulative_freq += freq
            if median_val1 == -1 and cumulative_freq >= pos1:
                median_val1 = val
            if median_val2 == -1 and cumulative_freq >= pos2:
                median_val2 = val
                break
        median = (median_val1 + median_val2) / 2
    else: # 奇數
        pos = (total_count + 1) // 2
        median_val = -1
        cumulative_freq = 0
        for val, freq in zip(values, freqs):
            cumulative_freq += freq
            if cumulative_freq >= pos:
                median_val = val
                break
        median = median_val
    
    table_values_header = f"{item_header}: ${', '.join(map(str, values))}"
    table_freqs_header = f"次數(人): ${', '.join(map(str, freqs))}"
    
    question_text = (
        f"下表為某班級 ${total_count}$ 位學生的{item}統計，則這些學生{item}的中位數為多少{unit}？<br>"
        f"{table_values_header}<br>{table_freqs_header}"
    )
    correct_answer = _format_number(median)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_grouped_median():
    num_groups = 5
    start = random.choice([10, 20, 30])
    step = 10
    item, unit = random.choice([("坐姿體前彎", "公分"), ("身高", "公分"), ("體重", "公斤")])
    item_header = f"{item}({unit})"
    
    groups = [f"{s}∼{s+step}" for s in range(start, start + num_groups*step, step)]
    freqs = [random.randint(3, 12) for _ in range(num_groups)]
    total_count = sum(freqs)
    
    median_pos = (total_count + 1) / 2
    
    median_group = ""
    cumulative_freq = 0
    for grp, freq in zip(groups, freqs):
        cumulative_freq += freq
        if cumulative_freq >= median_pos:
            median_group = grp
            break
            
    table_groups_header = f"{item_header}: ${', '.join(groups)}"
    table_freqs_header = f"次數(人): ${', '.join(map(str, freqs))}"
    
    question_text = (
        f"下表為某班 ${total_count}$ 位學生的{item}測驗結果，則該班學生{item}的中位數在哪一組？<br>"
        f"{table_groups_header}<br>{table_freqs_header}"
    )
    correct_answer = median_group
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

# --- 眾數生成器 ---

def generate_categorical_mode():
    categories = random.sample(['白色', '綠色', '藍色', '黑色', '紅色', '黃色'], k=4)
    item = random.choice(['襯衫', '帽子', '手機殼', '鞋子'])
    
    sales = list(set(random.sample(range(50, 100), k=3)))
    mode_sale = random.randint(max(sales) + 20, max(sales) + 80)
    
    mode_idx = random.randint(0, 3)
    temp_cats = list(categories)
    mode_category = temp_cats.pop(mode_idx)
    
    sales_dict = {cat: sale for cat, sale in zip(temp_cats, sales)}
    sales_dict[mode_category] = mode_sale

    display_cats = []
    display_sales = []
    for c in categories:
        display_cats.append(c)
        display_sales.append(str(sales_dict[c]))

    table_cat_header = f"顏色: ${', '.join(display_cats)}"
    table_sales_header = f"銷售量(件): ${', '.join(display_sales)}"
    
    question_text = (
        f"某服裝公司上週{item}的銷售量如下表，則{item}銷售顏色的眾數是哪一種顏色？<br>"
        f"{table_cat_header}<br>{table_sales_header}"
    )
    correct_answer = mode_category
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_numerical_mode():
    num_groups = random.randint(5, 7)
    item, unit = random.choice([("仰臥起坐", "次"), ("投籃命中數", "球"), ("單字測驗得分", "分")])
    item_header = f"{item}({unit})"
    
    values = sorted(random.sample(range(10, 41), num_groups))
    freqs = list(set(random.sample(range(5, 15), k=num_groups - 1)))
    mode_freq = random.randint(max(freqs) + 3, max(freqs) + 10)
    
    mode_idx = random.randint(0, num_groups - 1)
    freqs.insert(mode_idx, mode_freq)
    
    mode_value = values[mode_idx]
    
    table_values_header = f"{item_header}: ${', '.join(map(str, values))}"
    table_freqs_header = f"次數(人): ${', '.join(map(str, freqs))}"
    
    question_text = (
        f"下表為某班級的{item}測驗結果，則{item}的眾數為多少{unit}？<br>"
        f"{table_values_header}<br>{table_freqs_header}"
    )
    correct_answer = str(mode_value)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    
    is_correct = False
    
    # Case 1: Direct string comparison (for '藍色', '30∼40')
    if user_answer.upper() == correct_answer.upper():
        is_correct = True
        
    # Case 2: Numerical comparison
    if not is_correct:
        try:
            if float(user_answer) == float(correct_answer):
                is_correct = True
        except (ValueError, TypeError):
            pass

    try:
        float(correct_answer)
        correct_answer_latex = f"${correct_answer}$"
    except (ValueError, TypeError):
        correct_answer_latex = correct_answer

    result_text = f"完全正確！答案是 {correct_answer_latex}。" if is_correct else f"答案不正確。正確答案應為：${correct_answer_latex}"
    
    return {"correct": is_correct, "result": result_text, "next_question": True}
