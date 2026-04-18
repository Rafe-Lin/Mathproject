import random

# --- 資料設定 ---
# --- 資料設定 ---
CONTEXTS = {
    "score": {"unit": "分", "name": "數學小考分數", "data_range": (40, 100)},
    "height": {"unit": "公分", "name": "身高", "data_range": (140, 180)},
    "weight": {"unit": "公斤", "name": "體重", "data_range": (40, 70)},
    "salary": {"unit": "元", "name": "時薪", "data_range": (180, 250)},
    "time": {"unit": "小時", "name": "每週上網時間", "data_range": (0, 25)}
}

# --- 輔助函式 ---
def _generate_freq_table(is_dual=False):
    """生成一個隨機的次數分配表基礎數據。"""
    context_key = random.choice(["score", "height", "weight", "salary", "time"])
    context = CONTEXTS[context_key]

    if context_key == 'score':
        group_interval = random.choice([10, 20])
        start = random.choice([40, 50, 60])
    elif context_key == 'height':
        group_interval = random.choice([5, 10])
        start = random.choice([140, 145, 150])
    elif context_key == 'weight':
        group_interval = 5
        start = random.choice([40, 45, 50])
    elif context_key == 'salary':
        group_interval = 10
        start = 180
    else:  # time
        group_interval = 5
        start = 0
    
    num_groups = random.randint(4, 6)
    frequencies = [random.randint(2, 15) for _ in range(num_groups)]
    groups = [f"{start + i*group_interval}～{start + (i+1)*group_interval}" for i in range(num_groups)]
    
    table_data = {
        "groups": groups,
        "frequencies": frequencies,
        "context_name": context['name'],
        "unit": context['unit'],
        "start": start,
        "interval": group_interval
    }

    if is_dual:
        # 生成第二組數據，使其與第一組有差異但相關
        freqs_B = [max(1, f + random.randint(-5, 5)) for f in frequencies]
        table_data["frequencies2"] = freqs_B
        labels = random.choice([("甲班", "乙班"), ("A城市", "B城市"), ("去年", "今年")])
        table_data["labels"] = labels

    return table_data


# --- 題型生成函式 ---
def generate(level=1):
    """
    生成「分組的次數分配表與繪圖」相關題目。
    包含：
    1. 從原始資料製作次數分配表
    2. 解讀次數分配直方圖/折線圖
    3. 比較雙次的數分配折線圖
    """
    problem_type = random.choice([
        'table_from_data', 
        'single_graph_interpretation', 
        'dual_graph_comparison'
    ])
    
    if problem_type == 'table_from_data':
        return generate_table_from_data_problem()
    elif problem_type == 'single_graph_interpretation':
        return generate_single_graph_interpretation_problem()
    else: # 'dual_graph_comparison'
        return generate_dual_graph_comparison_problem()

def generate_table_from_data_problem():
    """題型1: 根據原始數據，回答次數分配表的問題。"""
    context_key = random.choice(['score', 'height', 'weight'])
    context = CONTEXTS[context_key]
    context_name = context['name']
    min_val, max_val = context['data_range']
    
    num_data_points = random.randint(20, 30)
    data_points = [random.randint(min_val, max_val) for _ in range(num_data_points)]
    
    if context_key == 'score':
        group_interval = random.choice([10, 20])
    else: # height, weight
        group_interval = 5

    start_val = (min(data_points) // group_interval) * group_interval
    data_str = ', '.join(map(str, sorted(data_points)))
    
    question_text_base = f"根據下列 {num_data_points} 位學生的{context_name}資料，以 ${group_interval}$ 為組距，從 ${start_val}$ 開始分組，回答下列問題：<br>資料: ${data_str}<br>"
    
    # 計算次數以生成正確答案
    max_data = max(data_points)
    num_groups = (max_data - start_val) // group_interval + 1
    freq_table = [0] * num_groups
    groups = [f"{start_val + i * group_interval}～{start_val + (i + 1) * group_interval}" for i in range(num_groups)]

    for dp in data_points:
        if dp < start_val: continue
        if dp == start_val + num_groups * group_interval: # 剛好是最大值的特殊情況
            freq_table[-1] += 1
            continue
        idx = (dp - start_val) // group_interval
        if 0 <= idx < num_groups:
            freq_table[idx] += 1

    q_type = random.choice(['fill_count', 'categorize'])
    
    if q_type == 'fill_count':
        target_idx = random.randint(0, num_groups - 1)
        target_group = groups[target_idx]
        correct_count = freq_table[target_idx]
        question_text = question_text_base + f"請問 ${target_group}$ 這一組應有多少人？"
        correct_answer = str(correct_count)
    else: # 'categorize'
        boundary_idx = random.randint(1, num_groups - 1)
        boundary_val = start_val + boundary_idx * group_interval
        question_text = question_text_base + f"請問{context_name}為 ${boundary_val}$ 的學生，應屬於哪一組？(請回答組別，例如 {groups[0]})"
        correct_group = groups[boundary_idx]
        correct_answer = correct_group
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_single_graph_interpretation_problem():
    """題型2: 根據給定的直方圖/折線圖數據，回答問題。"""
    data = _generate_freq_table()
    groups, frequencies = data['groups'], data['frequencies']
    context_name, unit, start, interval = data['context_name'], data['unit'], data['start'], data['interval']
    num_groups = len(groups)

    graph_type = random.choice(["直方圖", "折線圖"])
    table_str_parts = []
    for g, f in zip(groups, frequencies):
        table_str_parts.append(f"{g} {unit}: ${f} 人")
    table_str = "<br>".join(table_str_parts)

    question_text_base = f"右圖是某班級的{context_name}次數分配{graph_type}，依圖回答下列問題：<br>{table_str}<br>"
    
    q_type = random.choice(['max_freq', 'sum_range', 'total', 'count_below'])

    if q_type == 'max_freq':
        max_f = max(frequencies)
        max_indices = [i for i, f in enumerate(frequencies) if f == max_f]
        correct_group = groups[max_indices[0]]
        question_text = question_text_base + f"哪一組的人數最多？(請回答組別，例如 {groups[0]})"
        correct_answer = correct_group
    elif q_type == 'total':
        total_count = sum(frequencies)
        question_text = question_text_base + f"總共統計了多少人？"
        correct_answer = str(total_count)
    elif q_type == 'sum_range' and num_groups > 2:
        start_idx = random.randint(0, num_groups - 3)
        end_idx = random.randint(start_idx + 2, num_groups)
        lower_bound = start + start_idx * interval
        upper_bound = start + end_idx * interval
        count = sum(frequencies[start_idx:end_idx])
        question_text = question_text_base + f"{context_name}在 ${lower_bound}$ {unit}以上 (含)，未滿 ${upper_bound}$ {unit}的有多少人？"
        correct_answer = str(count)
    else: # 'count_below'
        k = random.randint(1, num_groups - 1)
        boundary_val = start + k * interval
        count = sum(frequencies[:k])
        question_text = question_text_base + f"{context_name}未滿 ${boundary_val}$ {unit}的有多少人？"
        correct_answer = str(count)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_dual_graph_comparison_problem():
    """題型3: 比較兩個次數分配折線圖。"""
    data = _generate_freq_table(is_dual=True)
    groups, freqs_A, freqs_B = data['groups'], data['frequencies'], data['frequencies2']
    context_name, unit, start, interval = data['context_name'], data['unit'], data['start'], data['interval']
    label_A, label_B = data['labels']
    num_groups = len(groups)

    table_str_parts = []
    for i in range(num_groups):
        table_str_parts.append(f"{groups[i]} {unit}: ${label_A} {freqs_A[i]}人, {label_B} {freqs_B[i]}人")
    table_str = "<br>".join(table_str_parts)

    question_text_base = f"下圖是{label_A}、{label_B}的{context_name}次數分配折線圖，依圖回答下列問題：<br>{table_str}<br>"
    
    q_type = random.choice(['max_diff', 'compare_above_below', 'range_diff_value'])

    if q_type == 'max_diff':
        diffs = [abs(a - b) for a, b in zip(freqs_A, freqs_B)]
        max_d = max(diffs)
        max_indices = [i for i, d in enumerate(diffs) if d == max_d]
        correct_group = groups[max_indices[0]]
        question_text = question_text_base + f"兩者的{context_name}分組中，哪一組的人數差距最大？(請回答組別)"
        correct_answer = correct_group
    elif q_type == 'range_diff_value' and num_groups > 1:
        start_idx = random.randint(0, num_groups - 2)
        end_idx = min(start_idx + random.randint(1, 2), num_groups)
        sum_A = sum(freqs_A[start_idx:end_idx])
        sum_B = sum(freqs_B[start_idx:end_idx])
        diff = abs(sum_A - sum_B)
        if end_idx - start_idx == 1:
            question_text = question_text_base + f"{context_name}在 ${groups[start_idx]}$ {unit}的人數相差多少人？"
        else:
            lower_bound = start + start_idx * interval
            upper_bound = start + end_idx * interval
            question_text = question_text_base + f"{context_name}在 ${lower_bound}$ {unit}以上 (含)，未滿 ${upper_bound}$ {unit}的人數相差多少人？"
        correct_answer = str(diff)
    else: # 'compare_above_below'
        direction = random.choice(['低於', '以上'])
        k = random.randint(1, num_groups - 1)
        boundary_val = start + k * interval
        if direction == '低於':
            sum_A, sum_B = sum(freqs_A[:k]), sum(freqs_B[:k])
            question_text = question_text_base + f"{context_name}{direction} ${boundary_val}$ {unit}的人數，何者較多？(請回答 {label_A} 或 {label_B} 或 一樣多)"
        else: # '以上'
            sum_A, sum_B = sum(freqs_A[k:]), sum(freqs_B[k:])
            question_text = question_text_base + f"{context_name}在 ${boundary_val}$ {unit}{direction} (含) 的人數，何者較多？(請回答 {label_A} 或 {label_B} 或 一樣多)"
        
        if sum_A > sum_B:
            correct_answer = label_A
        elif sum_B > sum_A:
            correct_answer = label_B
        else:
            correct_answer = "一樣多"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

# --- 答案檢查函式 ---
def check(user_answer, correct_answer):
    """檢查答案是否正確，處理數字、文字、組別等不同格式。"""
    user_answer = user_answer.strip().replace('~', '～').replace('-', '～')
    correct_answer = correct_answer.strip()
    
    is_correct = (user_answer.upper() == correct_answer.upper())
    
    if not is_correct:
        try:
            if float(user_answer) == float(correct_answer):
                is_correct = True
        except (ValueError, TypeError):
            pass

    if is_correct:
        result_text = f"完全正確！答案是 ${correct_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer}$"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}
