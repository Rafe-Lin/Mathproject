import random
from fractions import Fraction

# Define constants and options for problem generation
SCENARIOS = {
    "dice_roll": {
        "sample_space": list(range(1, 7)),
        "event_A_options": [
            ("質數", lambda x: x in {2, 3, 5}),
            ("偶數", lambda x: x % 2 == 0),
            ("奇數", lambda x: x % 2 != 0),
            ("大於3的數", lambda x: x > 3),
            ("小於4的數", lambda x: x < 4),
            ("不大於5的數", lambda x: x <= 5)
        ],
        "event_B_options": [
            ("小於5的數", lambda x: x < 5),
            ("奇數", lambda x: x % 2 != 0),
            ("偶數", lambda x: x % 2 == 0),
            ("質數", lambda x: x in {2, 3, 5}),
            ("大於2的數", lambda x: x > 2),
            ("不大於4的數", lambda x: x <= 4)
        ],
        "descriptions": {
            "title": "擲一粒公正骰子一次。",
            "A_prefix": "出現點數為",
            "B_prefix": "擲出點數",
            "question_pattern": "在{A_prefix}{A_desc}的條件下，求{B_prefix}{B_desc}的機率。"
        }
    },
    "card_draw": {
        "sample_space": [(suit, rank) for suit in ["紅心", "方塊", "梅花", "黑桃"] for rank in list(range(2, 11)) + ["J", "Q", "K", "A"]],
        "event_A_options": [
            ("花色為紅心", lambda s, r: s == "紅心"),
            ("點數為K", lambda s, r: r == "K"),
            ("花色為黑色牌", lambda s, r: s in ["梅花", "黑桃"]),
            ("點數為偶數", lambda s, r: r in [2, 4, 6, 8, 10] if isinstance(r, int) else False),
            ("點數為圖案牌", lambda s, r: r in ["J", "Q", "K"])
        ],
        "event_B_options": [
            ("點數為A", lambda s, r: r == "A"),
            ("花色為方塊", lambda s, r: s == "方塊"),
            ("點數為6", lambda s, r: r == "6" if isinstance(r, str) else r == 6),
            ("點數為奇數", lambda s, r: r in [3, 5, 7, 9] if isinstance(r, int) else False),
            ("點數為大於7的數", lambda s, r: (isinstance(r, int) and r > 7) or (r in ["J", "Q", "K", "A"]))
        ],
        "descriptions": {
            "title": "一副撲克牌共有52張，從中隨機抽取一張。",
            "A_prefix": "抽到",
            "B_prefix": "抽到",
            "question_pattern": "在{A_prefix}{A_desc}的條件下，求{B_prefix}{B_desc}的機率。"
        }
    },
    "population_counts": {
        "contexts": [
            "某班的學生",
            "某公司的員工",
            "某社區的住戶"
        ],
        "skill_options": [
            ("游自由式", "游仰式", "兩式都會", "游自由式", "游仰式"),
            ("說英文", "說法文", "兩種語言都會", "說英文", "說法文"),
            ("開車", "騎機車", "兩種交通工具都會", "開車", "騎機車"),
            ("使用電腦", "使用智慧手機", "兩者都會", "使用電腦", "使用智慧手機")
        ],
        "question_patterns": [
            "已知此{person}會{A_skill_desc}，求他也會{B_skill_desc}的機率。", # P(B|A)
            "已知此{person}會{B_skill_desc}，求他也會{A_skill_desc}的機率。" # P(A|B)
        ]
    },
    "population_percentages": {
        "contexts": [
            "醫院統計某地區成人的健康檢查資料",
            "某公司統計員工的問卷資料",
            "某網路平台統計用戶的行為資料"
        ],
        "condition_options": [
            ("體重過重者", "有脂肪肝者", "兩者都有的"),
            ("喜歡看電影", "喜歡聽音樂", "兩者都喜歡的"),
            ("通勤搭捷運", "通勤搭公車", "兩者都搭乘的")
        ],
        "negated_descriptions": {
            "體重過重者": "體重沒有過重的",
            "喜歡看電影": "不喜歡看電影",
            "通勤搭捷運": "通勤不搭捷運"
        },
        "question_patterns": [
            "已知此人{A_desc}，求他{B_desc}的機率。", # P(B|A)
            "已知此人{B_desc}，求他{A_desc}的機率。", # P(A|B)
            "已知此人{B_desc}，求他{A_complement_desc}的機率。" # P(A'|B)
        ]
    },
    "two_way_table": {
        "contexts": [
            "某影音平台分析資料庫中的{total_users}位用戶，他們對甲、乙兩部影片的喜好人數統計如下表。",
            "某市場調查公司分析{total_users}位顧客，他們對A、B兩種商品的購買意願統計如下表。",
            "某學校統計{total_users}位學生，他們選修微積分、線性代數兩門課程的人數統計如下表。"
        ],
        "event_names_options": [
            ("影片甲", "影片乙", "用戶"),
            ("商品A", "商品B", "顧客"),
            ("微積分", "線性代數", "學生")
        ],
        "table_vars": ["喜歡", "不喜歡"], # For generating question text dynamically
        "question_patterns": [
            "今任選一位{person_noun}，已知此{person_noun}{A_var}，求他也{B_var}的機率。", # P(B|A)
            "今任選一位{person_noun}，已知此{person_noun}{B_var}，求他也{A_var}的機率。", # P(A|B)
            "今任選一位{person_noun}，已知此{person_noun}{A_var}，求他{B_not_var}的機率。" # P(B'|A)
        ]
    }
}


def _calculate_prob_from_sets(sample_space, event_A_func, event_B_func):
    """Calculates n(A), n(A_intersect_B) for conditional probability."""
    set_A = {x for x in sample_space if event_A_func(x)}
    set_B = {x for x in sample_space if event_B_func(x)}
    set_A_intersect_B = set_A.intersection(set_B)

    if not set_A: # Avoid division by zero if P(A) is 0
        return None, None # Indicate impossible condition

    n_A = len(set_A)
    n_A_intersect_B = len(set_A_intersect_B)
    
    return n_A, n_A_intersect_B

def _generate_basic_counting_problem():
    scenario_type = random.choice(["dice_roll", "card_draw"])
    scenario = SCENARIOS[scenario_type]

    if scenario_type == "dice_roll":
        ss = scenario["sample_space"]
        event_A_desc, event_A_func = random.choice(scenario["event_A_options"])
        event_B_desc, event_B_func = random.choice(scenario["event_B_options"])
        
        # Ensure events are distinct and A is not empty
        attempts = 0
        while (event_A_desc == event_B_desc or not any(event_A_func(x) for x in ss)) and attempts < 10:
            event_A_desc, event_A_func = random.choice(scenario["event_A_options"])
            event_B_desc, event_B_func = random.choice(scenario["event_B_options"])
            attempts += 1
        
        if attempts == 10: # Fallback if suitable events aren't found
            return None

        n_A, n_A_intersect_B = _calculate_prob_from_sets(ss, event_A_func, event_B_func)
        
        if n_A is None or n_A == 0:
            return None # Retry if A is impossible

        question_text = f"{scenario['descriptions']['title']}<br>" + \
                        scenario["descriptions"]["question_pattern"].format(
                            A_prefix=scenario["descriptions"]["A_prefix"],
                            A_desc=event_A_desc,
                            B_prefix=scenario["descriptions"]["B_prefix"],
                            B_desc=event_B_desc
                        )

    elif scenario_type == "card_draw":
        ss = scenario["sample_space"]
        event_A_desc_raw, event_A_func = random.choice(scenario["event_A_options"])
        event_B_desc_raw, event_B_func = random.choice(scenario["event_B_options"])

        # Ensure events are distinct and A is not empty
        attempts = 0
        while (event_A_desc_raw == event_B_desc_raw or not any(event_A_func(s,r) for s,r in ss)) and attempts < 10:
            event_A_desc_raw, event_A_func = random.choice(scenario["event_A_options"])
            event_B_desc_raw, event_B_func = random.choice(scenario["event_B_options"])
            attempts += 1

        if attempts == 10: # Fallback if suitable events aren't found
            return None
        
        # Wrapper for card functions to match _calculate_prob_from_sets signature
        wrapper_A = lambda card: event_A_func(card[0], card[1])
        wrapper_B = lambda card: event_B_func(card[0], card[1])

        n_A, n_A_intersect_B = _calculate_prob_from_sets(ss, wrapper_A, wrapper_B)

        if n_A is None or n_A == 0:
             return None # Retry if A is impossible
        
        question_text = f"{scenario['descriptions']['title']}<br>" + \
                        scenario["descriptions"]["question_pattern"].format(
                            A_prefix=scenario["descriptions"]["A_prefix"],
                            A_desc=event_A_desc_raw,
                            B_prefix=scenario["descriptions"]["B_prefix"],
                            B_desc=event_B_desc_raw
                        )
    
    answer_fraction = Fraction(n_A_intersect_B, n_A)
    
    return {
        "question_text": question_text,
        "answer": str(answer_fraction),
        "correct_answer": str(answer_fraction)
    }

def _generate_population_stats_problem():
    prob_type = random.choice(["counts", "percentages"])
    
    if prob_type == "counts":
        scenario = SCENARIOS["population_counts"]
        context = random.choice(scenario["contexts"])
        skill_a, skill_b, both_skill, event_A_name, event_B_name = random.choice(scenario["skill_options"])
        
        # Generate consistent counts
        n_both = random.randint(5, 20)
        n_A_only = random.randint(5, 20)
        n_B_only = random.randint(5, 20)
        
        n_A = n_A_only + n_both
        n_B = n_B_only + n_both
        
        # Ensure n_A and n_B are not too small to be meaningful as conditions
        if n_A < 10 or n_B < 10:
            return None # Retry
        
        person_noun = "學生" if "學生" in context else "員工" if "員工" in context else "住戶"
        
        main_context_text = f"在{context}中，有${n_A}$人{skill_a}，有${n_B}$人{skill_b}，有${n_both}$人{both_skill}。今從{person_noun}中任選一位，試回答下列問題。<br><br>"
        
        q_type = random.choice([0, 1]) # P(B|A) or P(A|B)
        if q_type == 0: # P(B|A)
            question_pattern = scenario["question_patterns"][0]
            prob_value = Fraction(n_both, n_A)
            question_text_specific = question_pattern.format(person=person_noun, A_skill_desc=skill_a, B_skill_desc=skill_b)
        else: # P(A|B)
            question_pattern = scenario["question_patterns"][1]
            prob_value = Fraction(n_both, n_B)
            question_text_specific = question_pattern.format(person=person_noun, A_skill_desc=skill_a, B_skill_desc=skill_b)

        question_text = main_context_text + question_text_specific

    else: # percentages
        scenario = SCENARIOS["population_percentages"]
        context = random.choice(scenario["contexts"])
        event_A_desc_raw, event_B_desc_raw, both_desc = random.choice(scenario["condition_options"])
        
        # Generate consistent percentages
        p_both = random.randint(10, 30) # P(A intersect B)
        p_A_only = random.randint(10, 40) # P(A) - P(A intersect B)
        p_B_only = random.randint(10, 40) # P(B) - P(A intersect B)
        
        p_A = p_A_only + p_both
        p_B = p_B_only + p_both
        
        # Ensure P_A and P_B are not too small
        if p_A < 15 or p_B < 15:
            return None # Retry
        
        main_context_text = f"{context}：{event_A_desc_raw}占${p_A}$％，{event_B_desc_raw}占${p_B}$％，{both_desc}占${p_both}$％。今任選一位成年人，試回答下列問題。<br><br>"
        
        q_type = random.choice([0, 1, 2]) # P(B|A), P(A|B), P(A'|B)
        
        if q_type == 0: # P(B|A)
            question_pattern = scenario["question_patterns"][0]
            prob_value = Fraction(p_both, p_A)
            question_text_specific = question_pattern.format(A_desc=event_A_desc_raw, B_desc=event_B_desc_raw)
        elif q_type == 1: # P(A|B)
            question_pattern = scenario["question_patterns"][1]
            prob_value = Fraction(p_both, p_B)
            question_text_specific = question_pattern.format(A_desc=event_A_desc_raw, B_desc=event_B_desc_raw)
        else: # P(A'|B)
            question_pattern = scenario["question_patterns"][2]
            # Need complement of A: P(A' intersect B) = P(B) - P(A intersect B)
            p_A_complement_intersect_B = p_B - p_both
            # Ensure p_A_complement_intersect_B is non-negative and P(B) is not zero for calculation
            if p_A_complement_intersect_B < 0 or p_B == 0:
                 return None # Retry
            prob_value = Fraction(p_A_complement_intersect_B, p_B)
            
            # Formulate the complement description
            negated_A_desc = scenario["negated_descriptions"].get(event_A_desc_raw, f"沒有{event_A_desc_raw}")
            
            question_text_specific = question_pattern.format(A_complement_desc=negated_A_desc, B_desc=event_B_desc_raw)
        
        question_text = main_context_text + question_text_specific

    return {
        "question_text": question_text,
        "answer": str(prob_value),
        "correct_answer": str(prob_value)
    }

def _generate_sequential_events_problem():
    total_items = random.randint(6, 10)
    
    type1_count = random.randint(2, total_items - 2)
    type2_count = total_items - type1_count
    
    # Ensure both types have at least 2 items for interesting problems involving picking two of the same type.
    # Or at least 1 of each type if we need to pick different types.
    # Specifically, for picking two of same, need at least 2.
    # For picking different, need at least 1 of each.
    # The random.randint(2, total_items - 2) ensures type1_count is at least 2 and type2_count is at least 2 (total_items - type1_count >= 2).
    # This also means total_items must be at least 4.
    if total_items < 4 or type1_count < 2 or type2_count < 2:
        return None # Retry if counts are too low for interesting problems

    item_name = random.choice(["歌曲", "球", "籤"])
    
    type_options = {
        "歌曲": ["爵士樂", "抒情歌", "搖滾樂"],
        "球": ["藍色", "紅色", "綠色"],
        "籤": ["中獎", "銘謝惠顧"]
    }
    
    possible_type_names = type_options[item_name]
    
    if len(possible_type_names) < 2: # Should not happen with current options, but for robustness
        return None

    type1_name = random.choice(possible_type_names)
    type2_name = random.choice([t for t in possible_type_names if t != type1_name])
    
    if not type2_name: # Fallback if only one type is available
        return None

    question_context = f"某人有${total_items}$個{item_name}，其中${type1_count}$個為{type1_name}，另外${type2_count}$個為{type2_name}。今隨機抽出2個{item_name}，抽過的{item_name}不再抽回，設每個{item_name}被抽到的機率都相等，求下列各事件的機率。"

    q_choice = random.choice([0, 1]) # Sticking to 1st & 2nd specific types for level 1/2
    
    if q_choice == 0: # P(1st is Type1 and 2nd is Type1)
        # Check if enough items for this question
        if type1_count < 2:
             return None # Retry
        question_text_specific = f"(1)第一首與第二首都抽到{type1_name}。" if item_name == "歌曲" else \
                                 f"(1)第一次與第二次都抽到{type1_name}。"
        prob_value = Fraction(type1_count, total_items) * Fraction(type1_count - 1, total_items - 1)
    else: # P(1st is Type1 and 2nd is Type2)
        question_text_specific = f"(1)第一首抽到{type1_name}且第二首抽到{type2_name}。" if item_name == "歌曲" else \
                                 f"(1)第一次抽到{type1_name}且第二次抽到{type2_name}。"
        prob_value = Fraction(type1_count, total_items) * Fraction(type2_count, total_items - 1)
    
    question_text = question_context + "<br><br>" + question_text_specific
    
    return {
        "question_text": question_text,
        "answer": str(prob_value),
        "correct_answer": str(prob_value)
    }

def _generate_two_way_table_problem():
    scenario = SCENARIOS["two_way_table"]
    
    # Generate valid table counts (a,b,c,d)
    # a: A and B
    # b: A' and B
    # c: A and B'
    # d: A' and B'
    
    a = random.randint(20, 80)
    b = random.randint(5, 20)
    c = random.randint(5, 20)
    d = random.randint(5, 20)

    # Ensure all cells are positive and not too small
    if a < 5 or b < 5 or c < 5 or d < 5:
        return None # Retry if values are too small

    total_users = a + b + c + d
    
    event_A_name, event_B_name, person_noun = random.choice(scenario["event_names_options"])
    context = random.choice(scenario["contexts"]).format(total_users=total_users)

    event_A_name_full = f"{scenario['table_vars'][0]}{event_A_name}"
    event_A_not_name_full = f"{scenario['table_vars'][1]}{event_A_name}"
    event_B_name_full = f"{scenario['table_vars'][0]}{event_B_name}"
    event_B_not_name_full = f"{scenario['table_vars'][1]}{event_B_name}"
    
    # Construct the table LaTeX string
    # Using raw string and .format() for easier LaTeX syntax handling
    table_latex = r"""
\begin{{array}}{{|c|c|c|c|}}
\hline
\text{{（單位：人）}} & \text{{{col1}}} & \text{{{col2}}} & \text{{總計}} \\
\hline
\text{{{row1}}} & ${a}$ & ${b}$ & ${a_plus_b}$ \\
\hline
\text{{{row2}}} & ${c}$ & ${d}$ & ${c_plus_d}$ \\
\hline
\text{{總計}} & ${a_plus_c}$ & ${b_plus_d}$ & ${total}$ \\
\hline
\end{{array}}
""".format(
        col1=event_A_name_full, col2=event_A_not_name_full,
        row1=event_B_name_full, row2=event_B_not_name_full,
        a=a, b=b, c=c, d=d,
        a_plus_b=a+b, c_plus_d=c+d,
        a_plus_c=a+c, b_plus_d=b+d,
        total=total_users
    )
    
    question_text = f"{context}<br>{table_latex}<br><br>試回答下列問題。<br>"

    q_type = random.choice([0, 1, 2]) # P(B|A), P(A|B), P(B'|A)
    
    if q_type == 0: # P(B|A)
        # Condition is A (喜歡影片甲), want B (喜歡影片乙)
        # Count A: a+c
        # Count A and B: a
        if a + c == 0: return None # Avoid division by zero
        question_pattern = scenario["question_patterns"][0]
        prob_value = Fraction(a, a + c)
        question_text_specific = question_pattern.format(person_noun=person_noun, A_var=event_A_name_full, B_var=event_B_name_full)
    elif q_type == 1: # P(A|B)
        # Condition is B (喜歡影片乙), want A (喜歡影片甲)
        # Count B: a+b
        # Count A and B: a
        if a + b == 0: return None # Avoid division by zero
        question_pattern = scenario["question_patterns"][1]
        prob_value = Fraction(a, a + b)
        question_text_specific = question_pattern.format(person_noun=person_noun, A_var=event_A_name_full, B_var=event_B_name_full)
    else: # P(B'|A)
        # Condition is A (喜歡影片甲), want B' (不喜歡影片乙)
        # Count A: a+c
        # Count A and B': c
        if a + c == 0: return None # Avoid division by zero
        question_pattern = scenario["question_patterns"][2]
        prob_value = Fraction(c, a + c)
        question_text_specific = question_pattern.format(person_noun=person_noun, A_var=event_A_name_full, B_not_var=event_B_not_name_full)
    
    question_text += question_text_specific
    return {
        "question_text": question_text,
        "answer": str(prob_value),
        "correct_answer": str(prob_value)
    }

def generate(level=1):
    """
    生成條件機率相關題目。
    """
    problem_funcs = [
        _generate_basic_counting_problem,
        _generate_population_stats_problem
    ]

    if level >= 2:
        problem_funcs.append(_generate_sequential_events_problem)
        problem_funcs.append(_generate_two_way_table_problem)
    
    # Always try to generate a valid problem.
    max_attempts = 10
    for _ in range(max_attempts):
        try:
            problem_func = random.choice(problem_funcs)
            problem = problem_func()
            if problem and problem["question_text"] and problem["answer"]: 
                return problem
        except Exception:
            # Continue to next attempt if an error occurs or problem is invalid
            continue
    
    # Fallback if all attempts fail
    return {
        "question_text": "無法生成題目，請再試一次。",
        "answer": "",
        "correct_answer": ""
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    預期答案是分數或整數的字串形式。
    """
    is_correct = False
    feedback = ""

    try:
        user_fraction = Fraction(user_answer)
        correct_fraction = Fraction(correct_answer)
        
        if user_fraction == correct_fraction:
            is_correct = True
            feedback = f"完全正確！答案是 ${correct_fraction}$。"
        else:
            feedback = f"答案不正確。正確答案應為：${correct_fraction}$"
    except ValueError:
        feedback = f"請確保您的答案是有效的數字或分數（例如：1/2, 3, 0.5）。正確答案是：${correct_answer}$"
    except ZeroDivisionError:
        feedback = f"您的答案分母為零，請檢查。正確答案是：${correct_answer}$"
    
    return {"correct": is_correct, "result": feedback, "next_question": True}