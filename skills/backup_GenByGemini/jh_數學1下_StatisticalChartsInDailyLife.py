import random
import math

def generate(level=1):
    """
    生成「生活中的統計圖表」相關題目。
    包含：
    1. 長條圖讀值
    2. 折線圖比較
    3. 折線圖趨勢
    4. 圓形圖百分比計算
    5. 圓形圖圓心角計算
    6. 列聯表比率比較
    """
    problem_types = [
        'barchart_top_one', 'linechart_compare', 'linechart_trend',
        'piechart_percent', 'piechart_angle', 'contingency_rate'
    ]
    problem_type = random.choice(problem_types)

    if problem_type == 'barchart_top_one':
        return generate_barchart_problem()
    elif problem_type == 'linechart_compare':
        return generate_linechart_compare_problem()
    elif problem_type == 'linechart_trend':
        return generate_linechart_trend_problem()
    elif problem_type == 'piechart_percent':
        return generate_piechart_percent_problem()
    elif problem_type == 'piechart_angle':
        return generate_piechart_angle_problem()
    else:  # contingency_rate
        return generate_contingency_table_problem()

def generate_barchart_problem():
    """題型：長條圖讀值，找出最大值項目"""
    scenarios = [
        {'subject': '班級', 'item_type': '最喜歡的運動', 'items': ['籃球', '足球', '羽球', '桌球'], 'unit': '人'},
        {'subject': '飲料店', 'item_type': '飲品銷售量', 'items': ['珍珠奶茶', '純茶', '水果茶', '奶蓋'], 'unit': '杯'},
        {'subject': '農場', 'item_type': '水果產量', 'items': ['香蕉', '蘋果', '橘子', '草莓'], 'unit': '公斤'}
    ]
    scenario = random.choice(scenarios)

    data = {}
    values = random.sample(range(50, 500), len(scenario['items']))
    for i, item in enumerate(scenario['items']):
        data[item] = values[i]

    chart_desc = '、'.join([f"{name} ({value}{scenario['unit']})" for name, value in data.items()])

    question_text = f"一份針對某{scenario['subject']}的{scenario['item_type']}調查，其數據以長條圖呈現如下：<br>{chart_desc}。<br>請問哪一項的數值最高？"
    correct_answer = max(data, key=data.get)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_linechart_compare_problem():
    """題型：折線圖比較，找出持續最高/最低的系列"""
    scenarios = [
        {'entities': ('台北', '台中', '高雄'), 'metric': '月均溫', 'unit': '°C'},
        {'entities': ('A公司', 'B公司', 'C公司'), 'metric': '月營收', 'unit': '萬元'},
        {'entities': ('小明', '小華', '小英'), 'metric': '每月運動時數', 'unit': '小時'}
    ]
    scenario = random.choice(scenarios)
    entity_names = list(scenario['entities'])
    random.shuffle(entity_names)

    time_points = ['一月', '二月', '三月', '四月']

    base_low = [random.randint(10, 20) + i * random.uniform(-1, 2.5) for i in range(len(time_points))]
    base_high = [val + random.randint(20, 30) for val in base_low]
    base_mid = [(low + high) / 2 + random.uniform(-3, 3) for low, high in zip(base_low, base_high)]

    data_series = [base_low, base_mid, base_high]
    random.shuffle(data_series)

    data = dict(zip(entity_names, data_series))

    # 建立文字表格來呈現數據
    table_rows = []
    header = f"{'':<5}" + "".join([f"{name:<8}" for name in entity_names])
    # The line below is a placeholder for text alignment. Actual alignment in HTML/LaTeX is different.
    # For simplicity, we just join with spaces.
    header_display = f"時間 | {' | '.join(entity_names)}"
    table_rows.append(header_display)
    table_rows.append("---|---" * len(entity_names))
    for i, tp in enumerate(time_points):
        row_data = [f"{data[name][i]:.1f}{scenario['unit']}" for name in entity_names]
        table_rows.append(f"{tp} | {' | '.join(row_data)}")
    table_str = "<br>".join(table_rows)

    question_type = random.choice(['highest', 'lowest'])

    if question_type == 'highest':
        question_verb = '最高'
        correct_answer = entity_names[data_series.index(base_high)]
    else:
        question_verb = '最低'
        correct_answer = entity_names[data_series.index(base_low)]

    question_text = f"下表為 {', '.join(entity_names)} 在一至四月的{scenario['metric']}折線圖資料：<br><pre>{table_str}</pre><br>請問何者的{scenario['metric']}在這段期間一直維持{question_verb}？"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_linechart_trend_problem():
    """題型：折線圖趨勢，找出與前期相比下降的時期"""
    years = [f"{y} 學年度" for y in range(101, 107)]
    decreased_years = []
    data = []

    while not decreased_years:
        data = [random.randint(70, 85)]
        decreased_years = []
        for i in range(1, len(years)):
            # Ensure change doesn't make value negative or too small
            change = random.randint(-5, 8)
            new_val = max(10, data[-1] + change)
            if new_val < data[-1]:
                decreased_years.append(years[i])
            data.append(new_val)

    data_desc = '、'.join([f"{years[i]} ({data[i]}%)" for i in range(len(years))])

    correct_year = random.choice(decreased_years)
    other_years = [y for y in years if y not in decreased_years and y != years[0]]
    options_list = random.sample(other_years, 3) + [correct_year]
    random.shuffle(options_list)

    options_str = "<br>".join([f"{chr(65+i)}) {opt}" for i, opt in enumerate(options_list)])
    correct_label = chr(65 + options_list.index(correct_year))

    question_text = f"右圖是某校九年級學生視力不良人數百分率折線圖，其數據如下：<br>{data_desc}。<br>請問和上一個學年度相比，下列哪一個學年度的視力不良人數百分率呈現下降的趨勢？<br>{options_str}"

    return {
        "question_text": question_text,
        "answer": correct_label,
        "correct_answer": correct_label
    }

def generate_piechart_percent_problem():
    """題型：圓形圖，給定數值計算百分比"""
    items = random.sample(['吸管', '寶特瓶', '塑膠瓶蓋', '廢棄漁網', '玻璃瓶'], 3)
    total = random.choice([200, 400, 500, 800, 1000])

    p1 = random.randint(20, 50)
    p2 = random.randint(20, 100 - p1 - 10)
    p3 = 100 - p1 - p2
    percentages = [p1, p2, p3]
    random.shuffle(percentages)

    vals = [total * p // 100 for p in percentages]
    # Adjust for rounding errors to ensure sum is correct
    vals[-1] = total - sum(vals[:-1])

    data = dict(zip(items, vals))
    target_item, target_value = random.choice(list(data.items()))

    data_desc = '、'.join([f"{name} {value} 件" for name, value in data.items()])
    percentage = round((target_value / total) * 100, 2)
    percentage_str = f"{int(percentage) if percentage == int(percentage) else percentage}"

    question_text = f"某團體淨灘活動結束後，統計所移除的海洋廢棄物如下：<br>{data_desc}。<br>若將此資料繪製成圓形圖，請問「{target_item}」占總數的百分率為何？(答案請填寫數字)"
    correct_answer = percentage_str

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_piechart_angle_problem():
    """題型：圓形圖，給定數值計算圓心角"""
    total = random.choice([180, 240, 300, 360, 600, 720])
    num_items = random.randint(3, 4)
    items = random.sample(['籃球社', '游泳社', '排球社', '桌球社', '羽球社'], num_items)

    dividers = sorted(random.sample(range(1, total), num_items - 1))
    vals = [dividers[0]] + [dividers[i] - dividers[i-1] for i in range(1, len(dividers))] + [total - dividers[-1]]
    random.shuffle(vals)
    data = dict(zip(items, vals))

    # Ensure the resulting angle is an integer
    while any((v * 360) % total != 0 for v in data.values()):
        dividers = sorted(random.sample(range(1, total), num_items - 1))
        vals = [dividers[0]] + [dividers[i] - dividers[i-1] for i in range(1, len(dividers))] + [total - dividers[-1]]
        random.shuffle(vals)
        data = dict(zip(items, vals))

    target_item, target_value = random.choice(list(data.items()))
    data_desc = '、'.join([f"{name} {value} 人" for name, value in data.items()])

    angle = (target_value * 360) // total

    question_text = f"某校五個社團中，部分社團人數統計如下：<br>{data_desc}。<br>若將此資料繪製成圓形圖，請問「{target_item}」所占的圓心角是幾度？(答案請填寫數字)"
    correct_answer = str(angle)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_contingency_table_problem():
    """題型：列聯表，根據文字描述比較比率"""
    groups = [('甲班', '乙班'), ('男生', '女生')]
    outcomes = [('及格', '不及格', '及格率'), ('贊成', '不贊成', '贊成率')]
    idx = random.randint(0, 1)
    group_a_name, group_b_name = groups[idx]
    outcome_pos, outcome_neg, rate_name = outcomes[idx]

    # Generate data ensuring rates are not too close
    while True:
        total_a = random.randint(20, 50)
        total_b = random.randint(20, 50)
        pos_a = random.randint(int(0.2 * total_a), int(0.8 * total_a))
        pos_b = random.randint(int(0.2 * total_b), int(0.8 * total_b))
        neg_b = total_b - pos_b
        rate_a = pos_a / total_a
        rate_b = pos_b / total_b
        if abs(rate_a - rate_b) > 0.05:
            break

    question_text = f"某次調查中，{group_a_name}共 {total_a} 人，其中有 {pos_a} 人{outcome_pos}；<br>{group_b_name}共 {total_b} 人，其中有 {neg_b} 人{outcome_neg}。<br>請問就「{rate_name}」而言，哪一個群體的表現比較好？"

    correct_answer = group_a_name if rate_a > rate_b else group_b_name

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_ans_clean = user_answer.strip().upper().replace('%', '').replace('度', '')
    correct_ans_clean = correct_answer.strip().upper().replace('%', '').replace('度', '')

    is_correct = (user_ans_clean == correct_ans_clean)

    if not is_correct:
        try:
            if abs(float(user_ans_clean) - float(correct_ans_clean)) < 1e-6:
                is_correct = True
        except ValueError:
            pass

    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}。"
    return {"correct": is_correct, "result": result_text, "next_question": True}
