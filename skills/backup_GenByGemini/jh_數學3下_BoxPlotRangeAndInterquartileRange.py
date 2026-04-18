import random
import math

def _calculate_five_number_summary(data):
    """
    Calculates Min, Q1, Q2, Q3, Max, Range, and IQR for a given dataset.
    This uses the quartile calculation method commonly found in Taiwanese textbooks.
    """
    if not data:
        return {'min': None, 'q1': None, 'q2': None, 'q3': None, 'max': None, 'range': None, 'iqr': None}

    sorted_data = sorted(data)
    n = len(sorted_data)
    
    summary = {}
    summary['min'] = sorted_data[0]
    summary['max'] = sorted_data[-1]
    
    # Q1 (First Quartile)
    idx_q1 = n * 0.25
    if idx_q1 == int(idx_q1):
        # If n/4 is an integer k, Q1 is the average of the k-th and (k+1)-th values.
        # In 0-based index, this is (data[k-1] + data[k]) / 2
        summary['q1'] = (sorted_data[int(idx_q1) - 1] + sorted_data[int(idx_q1)]) / 2
    else:
        # If n/4 is not an integer, Q1 is the value at the ceiling(n/4)-th position.
        # In 0-based index, this is data[ceil(n/4)-1]
        summary['q1'] = sorted_data[math.ceil(idx_q1) - 1]

    # Q2 (Median)
    idx_q2 = n * 0.5
    if idx_q2 == int(idx_q2):
        summary['q2'] = (sorted_data[int(idx_q2) - 1] + sorted_data[int(idx_q2)]) / 2
    else:
        summary['q2'] = sorted_data[math.ceil(idx_q2) - 1]
        
    # Q3 (Third Quartile)
    idx_q3 = n * 0.75
    if idx_q3 == int(idx_q3):
        summary['q3'] = (sorted_data[int(idx_q3) - 1] + sorted_data[int(idx_q3)]) / 2
    else:
        summary['q3'] = sorted_data[math.ceil(idx_q3) - 1]
        
    summary['range'] = summary['max'] - summary['min']
    if summary['q1'] is not None and summary['q3'] is not None:
        summary['iqr'] = summary['q3'] - summary['q1']
    else:
        summary['iqr'] = None

    # Format numbers to remove .0 for integers
    for key, value in summary.items():
        if isinstance(value, float) and value.is_integer():
            summary[key] = int(value)
    
    return summary

def generate_calc_from_raw():
    """
    Generates a problem asking to calculate a statistic from a list of raw data.
    """
    n = random.randint(11, 20)
    data = [random.randint(1, 100) for _ in range(n)]
    
    summary = _calculate_five_number_summary(data)
    
    # Randomly choose which statistic to ask for
    ask_for = random.choice(['最小值', '最大值', 'Q1 (第一四分位數)', 'Q2 (中位數)', 'Q3 (第三四分位數)', '全距', '四分位距'])
    
    # Sort data for presentation to make it easier for students to verify
    data.sort()
    data_str = ", ".join(map(str, data))
    
    question_text = f"觀察下列已排序的資料：<br>${data_str}$<br>請問這組資料的{ask_for}是多少？"
    
    key_map = {
        '最小值': 'min', '最大值': 'max', 'Q1 (第一四分位數)': 'q1', 
        'Q2 (中位數)': 'q2', 'Q3 (第三四分位數)': 'q3',
        '全距': 'range', '四分位距': 'iqr'
    }
    answer_val = summary[key_map[ask_for]]
            
    return {
        "question_text": question_text,
        "answer": str(answer_val),
        "correct_answer": str(answer_val)
    }

def generate_calc_from_freq():
    """
    Generates a problem asking to calculate range or IQR from a frequency table.
    """
    num_categories = random.randint(6, 9)
    start_score = random.randint(50, 70)
    scores = [start_score]
    for _ in range(num_categories - 1):
        scores.append(scores[-1] + random.randint(2, 5))
        
    freqs = [random.randint(1, 8) for _ in range(num_categories)]
    
    # Ensure total number of students is reasonable
    while sum(freqs) < 20 or sum(freqs) > 50:
        freqs = [random.randint(1, 8) for _ in range(num_categories)]

    data = []
    for score, freq in zip(scores, freqs):
        data.extend([score] * freq)
    
    summary = _calculate_five_number_summary(data)
    
    ask_for = random.choice(['全距', '四分位距'])
    
    table_header = "分數(分): " + ", ".join(map(str, scores))
    table_body = "次數(人): " + ", ".join(map(str, freqs))
    question_text = f"下表為某次測驗成績的次數分配表：<br>{table_header}<br>{table_body}<br>請問這組分數的{ask_for}為多少？"
    
    key_map = {'全距': 'range', '四分位距': 'iqr'}
    answer_val = summary[key_map[ask_for]]
    
    return {
        "question_text": question_text,
        "answer": str(answer_val),
        "correct_answer": str(answer_val)
    }

def generate_compare_two():
    """
    Generates a problem comparing range or IQR of two datasets described by their five-number summaries.
    """
    n_a = random.randint(25, 40)
    data_a = [random.randint(30, 100) for _ in range(n_a)]
    summary_a = _calculate_five_number_summary(data_a)
    
    while True:
        n_b = random.randint(25, 40)
        data_b = [random.randint(30, 100) for _ in range(n_b)]
        summary_b = _calculate_five_number_summary(data_b)
        if summary_a['range'] != summary_b['range'] and summary_a['iqr'] != summary_b['iqr']:
            break
            
    desc = "某校九年級甲、乙兩班的英語科成績，其五數綜合摘要資訊如下：<br>"
    desc += f"甲班：最小值 ${summary_a['min']}$分, Q1 ${summary_a['q1']}$分, 中位數 ${summary_a['q2']}$分, Q3 ${summary_a['q3']}$分, 最大值 ${summary_a['max']}$分。<br>"
    desc += f"乙班：最小值 ${summary_b['min']}$分, Q1 ${summary_b['q1']}$分, 中位數 ${summary_b['q2']}$分, Q3 ${summary_b['q3']}$分, 最大值 ${summary_b['max']}$分。"

    metric = random.choice(['全距', '四分位距'])
    comparison_word = random.choice(['大', '小'])
    
    question_text = f"{desc}<br>請問哪一班的{metric}比較{comparison_word}？(請填 甲 或 乙)"
    
    if metric == '全距':
        if comparison_word == '大':
            correct_answer = '甲' if summary_a['range'] > summary_b['range'] else '乙'
        else:
            correct_answer = '甲' if summary_a['range'] < summary_b['range'] else '乙'
    else: # '四分位距'
        if comparison_word == '大':
            correct_answer = '甲' if summary_a['iqr'] > summary_b['iqr'] else '乙'
        else:
            correct_answer = '甲' if summary_a['iqr'] < summary_b['iqr'] else '乙'
            
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    生成盒狀圖、全距與四分位距相關題目。
    包含：
    1. 從原始資料計算統計量
    2. 從次數分配表計算統計量
    3. 比較兩組資料的統計量
    """
    problem_type = random.choice(['calc_from_raw', 'calc_from_freq', 'compare_two'])
    
    if problem_type == 'calc_from_raw':
        return generate_calc_from_raw()
    elif problem_type == 'calc_from_freq':
        return generate_calc_from_freq()
    else: # 'compare_two'
        return generate_compare_two()

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip()
    correct_answer_str = str(correct_answer).strip()

    is_correct = (user_answer == correct_answer_str)
    
    if not is_correct:
        try:
            if abs(float(user_answer) - float(correct_answer_str)) < 1e-9:
                is_correct = True
        except (ValueError, TypeError):
            pass

    if is_correct:
        result_text = f"完全正確！答案是 {correct_answer_str}。"
    else:
        result_text = f"答案不正確。正確答案應為：{correct_answer_str}"

    try:
        float(correct_answer_str)
        result_text = result_text.replace(correct_answer_str, f"${correct_answer_str}$")
    except (ValueError, TypeError):
        pass
        
    return {"correct": is_correct, "result": result_text, "next_question": True}