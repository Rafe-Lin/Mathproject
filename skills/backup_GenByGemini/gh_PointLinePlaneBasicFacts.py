import random
# from fractions import Fraction # Not needed for this skill

def generate(level=1):
    """
    生成「點、線、面基本性質」相關題目。
    包括：
    1. 決定唯一直線的條件
    2. 決定唯一平面的條件（多選題）
    3. 點、線、面關係的判斷（是非題）
    4. 交點/交線/交面的性質
    """
    problem_type = random.choice([
        'unique_line_condition',
        'unique_plane_condition_mc',
        'true_false_spatial_relation',
        'intersection_facts_mc'
    ])
    
    if problem_type == 'unique_line_condition':
        return generate_unique_line_condition()
    elif problem_type == 'unique_plane_condition_mc':
        return generate_unique_plane_condition_mc()
    elif problem_type == 'true_false_spatial_relation':
        return generate_true_false_spatial_relation()
    elif problem_type == 'intersection_facts_mc':
        return generate_intersection_facts_mc()

def generate_unique_line_condition():
    """
    題型：決定唯一直線最少需要的相異點數。
    """
    question_text = r"空間中，決定一條唯一直線最少需要幾個相異點？"
    correct_answer = "2" # As text, not math
    
    return {
        "question_text": question_text,
        "answer": correct_answer, # Store string answer for check function
        "correct_answer": correct_answer
    }

def generate_unique_plane_condition_mc():
    """
    題型：關於決定唯一平面的條件（多選題）。
    """
    correct_conditions = [
        r"三個不共線的點",
        r"一直線與線外一點",
        r"兩相交直線",
        r"兩平行直線"
    ]
    
    incorrect_conditions = [
        r"三個共線的點",
        r"兩相異點",
        r"一直線與線上任一點",
        r"兩條歪斜線" # Skew lines do not define a unique plane
    ]

    # For Level 1, we'll always ask for a condition that *determines* a plane.
    # So we'll pick one correct condition and three incorrect ones.

    correct_choice_statement = random.choice(correct_conditions)
    
    # Ensure distinct incorrect choices and that they are not the same as the correct choice
    available_incorrect = [cond for cond in incorrect_conditions if cond != correct_choice_statement]
    random.shuffle(available_incorrect)
    
    # Pick 3 distinct incorrect choices. If fewer than 3, pad with duplicates (though unlikely for current options)
    while len(available_incorrect) < 3:
        available_incorrect.append(random.choice(incorrect_conditions))
        
    choices = [correct_choice_statement] + available_incorrect[:3]
    random.shuffle(choices) # Shuffle all four options
    
    options_map = {}
    option_labels = ['A', 'B', 'C', 'D']
    for i, choice_text in enumerate(choices):
        options_map[option_labels[i]] = choice_text
        
    question_text = r"下列哪一個條件可以決定一個唯一的平面？<br>" + \
                    r"<br>".join([f"${label}$. {text}" for label, text in options_map.items()])
    
    # Find the label for the correct statement
    correct_answer = ""
    for label, text in options_map.items():
        if text == correct_choice_statement:
            correct_answer = label
            break
            
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_true_false_spatial_relation():
    """
    題型：判斷空間中點、線、面關係的敘述是否正確（是非題）。
    """
    statements = [
        {"text": r"若直線 $L$ 在平面 $E$ 上，則 $L$ 上所有點都在 $E$ 上。", "is_true": True},
        {"text": r"空間中，不共線的三點決定唯一一個平面。", "is_true": True},
        {"text": r"兩相異直線若相交於一點，則兩直線共平面。", "is_true": True},
        {"text": r"通過空間中任意兩相異點，恰可決定一直線。", "is_true": True},
        {"text": r"空間中任意三點都可以決定唯一平面。", "is_true": False}, # if collinear
        {"text": r"過平面外一點，恰可作一直線與此平面平行。", "is_true": False}, # infinitely many parallel lines
        {"text": r"兩條相異直線若沒有交點，則它們必定平行。", "is_true": False}, # skew lines
        {"text": r"一直線與線外一點，若該點位於此直線上，則可決定唯一平面。", "is_true": False} # point on line does not determine unique plane
    ]
    
    chosen_statement = random.choice(statements)
    
    question_text = f"判斷以下敘述是否正確？(請填寫『是』或『否』)<br>{chosen_statement['text']}"
    correct_answer = "是" if chosen_statement["is_true"] else "否"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_intersection_facts_mc():
    """
    題型：關於交點、交線的性質（多選題）。
    """
    problem_choice = random.randint(1, 3)
    
    if problem_choice == 1:
        question_text = r"兩相異平面相交，其交集為何？"
        options = {
            'A_orig': r"一個點",
            'B_orig': r"一條直線",
            'C_orig': r"一個平面",
            'D_orig': r"沒有交集"
        }
        correct_option_content = r"一條直線"
        
    elif problem_choice == 2:
        question_text = r"一直線與一平面相交，若直線不在平面上，則最多有幾個交點？"
        options = {
            'A_orig': r"0 個",
            'B_orig': r"1 個",
            'C_orig': r"2 個",
            'D_orig': r"無限多個"
        }
        correct_option_content = r"1 個"
        
    else: # problem_choice == 3
        question_text = r"空間中兩相異直線相交於一點，則它們共幾個平面？"
        options = {
            'A_orig': r"0 個",
            'B_orig': r"1 個",
            'C_orig': r"2 個",
            'D_orig': r"無限多個"
        }
        correct_option_content = r"1 個"

    # Shuffle options and re-label to A, B, C, D
    option_contents = list(options.values())
    random.shuffle(option_contents)
    
    shuffled_options_map = {}
    new_correct_label = ""
    for i, content in enumerate(option_contents):
        label = chr(ord('A') + i)
        shuffled_options_map[label] = content
        if content == correct_option_content:
            new_correct_label = label
    
    question_text += r"<br>" + \
                     r"<br>".join([f"${label}$. {text}" for label, text in shuffled_options_map.items()])
    
    return {
        "question_text": question_text,
        "answer": new_correct_label,
        "correct_answer": new_correct_label
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer_cleaned = user_answer.strip().upper()
    correct_answer_cleaned = correct_answer.strip().upper()
    
    is_correct = (user_answer_cleaned == correct_answer_cleaned)
    
    if not is_correct:
        # For numerical answers (like '2' for unique_line_condition), try converting to float for robustness.
        # This will also cover cases where user might enter '1.0' instead of '1'.
        try:
            if float(user_answer_cleaned) == float(correct_answer_cleaned):
                is_correct = True
        except ValueError:
            pass
        
        # Special handling for '是'/'否' type questions
        if user_answer_cleaned in ['是', '否'] and correct_answer_cleaned in ['是', '否']:
            is_correct = (user_answer_cleaned == correct_answer_cleaned)

    result_text = f"完全正確！答案是 ${correct_answer_cleaned}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer_cleaned}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}