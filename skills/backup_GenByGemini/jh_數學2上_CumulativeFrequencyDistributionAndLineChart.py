import random

def _get_display_width(s):
    """
    Approximates the display width of a string, where CJK characters count as 2.
    """
    return sum(2 if '\u4e00' <= char <= '\u9fff' else 1 for char in str(s))

def _pad(text, total_width, align='center'):
    """
    Pads a string to a certain display width, handling CJK characters.
    """
    text = str(text)
    text_width = _get_display_width(text)
    if text_width >= total_width:
        return text
    padding = total_width - text_width
    if align == 'center':
        left_pad = padding // 2
        right_pad = padding - left_pad
        return ' ' * left_pad + text + ' ' * right_pad
    elif align == 'left':
        return text + ' ' * padding
    elif align == 'right':
        return ' ' * padding + text
    return text

def _build_table_string(subject, unit, data_rows, columns_to_show, total=None):
    """
    Builds a well-formatted string for an ASCII table.
    - columns_to_show: list of keys to display, e.g., ['group', 'freq', 'cum_freq']
    - data_rows: list of dictionaries, each dict is a row
    """
    headers = {
        'group': f"{subject}({unit})",
        'freq': "次數",
        'cum_freq': "累積次數"
    }
    col_widths = {'group': 22, 'freq': 10, 'cum_freq': 12}

    header_parts = [_pad(headers[key], col_widths[key]) for key in columns_to_show]
    header_line = f"|{'|'.join(header_parts)}|"

    divider_parts = ['-' * col_widths[key] for key in columns_to_show]
    divider_line = f"|{'|'.join(divider_parts)}|"

    table_lines = [header_line, divider_line]

    for row in data_rows:
        row_parts = []
        for key in columns_to_show:
            align = 'left' if key == 'group' else 'center'
            content = str(row.get(key, ''))
            row_parts.append(_pad(content, col_widths[key], align=align))
        row_line = f"|{'|'.join(row_parts)}|"
        table_lines.append(row_line)

    if total is not None:
        table_lines.append(divider_line)
        total_parts = []
        for i, key in enumerate(columns_to_show):
            if i == 0:
                total_parts.append(_pad("合計", col_widths[key], align='center'))
            elif key == 'freq':
                total_parts.append(_pad(str(total), col_widths[key], align='center'))
            else:
                total_parts.append(' ' * col_widths[key])
        total_line = f"|{'|'.join(total_parts)}|"
        table_lines.append(total_line)

    return "\n".join(table_lines)


def _generate_data():
    """
    Generates a set of data for frequency distribution problems.
    """
    contexts = [
        {'subject': '數學測驗', 'unit': '分', 'start_range': (40, 60), 'width': 10},
        {'subject': '學生體重', 'unit': '公斤', 'start_range': (40, 55), 'width': 5},
        {'subject': '每月薪資', 'unit': '萬元', 'start_range': (2, 4), 'width': 1},
        {'subject': '閱讀課外讀物時間', 'unit': '小時', 'start_range': (0, 2), 'width': 1},
        {'subject': '電池使用時間', 'unit': '小時', 'start_range': (5, 8), 'width': 1}
    ]
    context = random.choice(contexts)

    num_groups = random.randint(4, 5)
    start_val = random.randint(context['start_range'][0], context['start_range'][1])
    if context['width'] >= 5:
        start_val = int(start_val / 5) * 5

    class_width = context['width']

    groups = []
    lower_bounds = []
    upper_bounds = []
    current_val = start_val
    for _ in range(num_groups):
        lower = current_val
        upper = current_val + class_width
        groups.append(f"{lower}~{upper}")
        lower_bounds.append(lower)
        upper_bounds.append(upper)
        current_val = upper

    frequencies = [random.randint(3, 15) for _ in range(num_groups)]

    cum_frequencies = []
    current_sum = 0
    for freq in frequencies:
        current_sum += freq
        cum_frequencies.append(current_sum)

    total = current_sum

    return {
        'subject': context['subject'],
        'unit': context['unit'],
        'groups': groups,
        'lower_bounds': lower_bounds,
        'upper_bounds': upper_bounds,
        'frequencies': frequencies,
        'cum_frequencies': cum_frequencies,
        'total': total
    }

def generate_complete_table_problem():
    """
    Generates a problem asking the user to complete the cumulative frequency column.
    """
    data = _generate_data()

    rows = []
    for i in range(len(data['groups'])):
        rows.append({
            'group': data['groups'][i],
            'freq': data['frequencies'][i],
            'cum_freq': '?'
        })

    table_str = _build_table_string(
        data['subject'], data['unit'], rows,
        columns_to_show=['group', 'freq', 'cum_freq'],
        total=data['total']
    )

    question_text = (f"下表為某次「{data['subject']}」的次數分配表，"
                     f"請根據表中的次數，完成累積次數分配表，並依序填入累積次數的數值 (由上到下，以逗號分隔)。\n\n"
                     f"```\n{table_str}\n```")

    correct_answer = ",".join(map(str, data['cum_frequencies']))

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_read_cumulative_table_problem():
    """
    Generates a problem that requires reading a complete cumulative frequency table.
    """
    data = _generate_data()

    rows = []
    for i in range(len(data['groups'])):
        rows.append({
            'group': data['groups'][i],
            'freq': data['frequencies'][i],
            'cum_freq': data['cum_frequencies'][i]
        })

    table_str = _build_table_string(
        data['subject'], data['unit'], rows,
        columns_to_show=['group', 'freq', 'cum_freq']
    )

    question_type = random.choice(['less_than', 'at_least'])

    if question_type == 'less_than':
        # Ask "how many are less than X?"
        q_idx = random.randint(0, len(data['groups']) - 2)
        limit = data['upper_bounds'][q_idx]
        correct_answer = str(data['cum_frequencies'][q_idx])
        question_text = (f"根據下方的「{data['subject']}」累積次數分配表，回答下列問題：\n"
                         f"```\n{table_str}\n```\n\n"
                         f"請問{data['subject']}未滿 {limit} {data['unit']} 的有多少？")
    else:  # 'at_least'
        # Ask "how many are Y or more?"
        q_idx = random.randint(1, len(data['groups']) - 1)
        limit = data['lower_bounds'][q_idx]

        correct_answer_val = data['total'] - data['cum_frequencies'][q_idx - 1]
        correct_answer = str(correct_answer_val)
        question_text = (f"根據下方的「{data['subject']}」累積次數分配表，回答下列問題：\n"
                         f"```\n{table_str}\n```\n\n"
                         f"請問{data['subject']}在 {limit} {data['unit']} 以上 (含) 的有多少？")

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_interpret_specific_group_problem():
    """
    Generates a problem asking for the frequency of a specific group,
    given only the cumulative frequency table.
    """
    data = _generate_data()

    rows = []
    for i in range(len(data['groups'])):
        rows.append({
            'group': data['groups'][i],
            'cum_freq': data['cum_frequencies'][i]
        })

    # Hide the frequency column to make it more challenging
    table_str = _build_table_string(
        data['subject'], data['unit'], rows,
        columns_to_show=['group', 'cum_freq']
    )

    q_idx = random.randint(0, len(data['groups']) - 1)
    target_group = data['groups'][q_idx]

    correct_answer = str(data['frequencies'][q_idx])

    question_text = (f"下表為某次「{data['subject']}」的累積次數分配表，請問在「{target_group}」{data['unit']}這一組的次數是多少？\n\n"
                     f"```\n{table_str}\n```")

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    Generates a problem related to Cumulative Frequency Distribution tables.
    """
    problem_types = [
        'complete_table',
        'read_cumulative_table',
        'interpret_specific_group'
    ]

    problem_type = random.choices(problem_types, weights=[30, 45, 25], k=1)[0]

    if problem_type == 'complete_table':
        return generate_complete_table_problem()
    elif problem_type == 'read_cumulative_table':
        return generate_read_cumulative_table_problem()
    else:  # 'interpret_specific_group'
        return generate_interpret_specific_group_problem()

def check(user_answer, correct_answer):
    """
    Checks if the user's answer is correct.
    """
    user_answer_norm = user_answer.strip().replace(' ', '').replace('，', ',')
    correct_answer_norm = correct_answer.strip()

    is_correct = (user_answer_norm.upper() == correct_answer_norm.upper())

    if not is_correct:
        try:
            if float(user_answer_norm) == float(correct_answer_norm):
                is_correct = True
        except (ValueError, TypeError):
            pass

    if is_correct:
        result_text = f"完全正確！答案是 {correct_answer}。"
    else:
        result_text = f"答案不正確。正確答案應為：{correct_answer}"

    return {"correct": is_correct, "result": result_text, "next_question": True}