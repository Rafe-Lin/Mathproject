import random

# Global constant for number to Chinese character mapping
_N_MAP = {
    3: '三', 4: '四', 5: '五', 6: '六', 7: '七', 8: '八', 
    9: '九', 10: '十', 11: '十一', 12: '十二', 13: '十三', 
    14: '十四', 15: '十五'
}

def generate(level=1):
    """
    生成「多邊形」相關題目 (標準 LaTeX 範本)。
    包含：
    1. 正多邊形定義
    2. 多邊形命名
    3. 對角線數量
    4. 內角和
    5. 正多邊形單一內角
    """
    problem_type = random.choice(['definition', 'naming', 'diagonal', 'angle_sum', 'regular_angle'])
    
    if problem_type == 'definition':
        return generate_definition_problem()
    elif problem_type == 'naming':
        return generate_naming_problem()
    elif problem_type == 'diagonal':
        return generate_diagonal_problem()
    elif problem_type == 'angle_sum':
        return generate_angle_sum_problem()
    else: # regular_angle
        return generate_regular_polygon_angle_problem()

def generate_definition_problem():
    # 題型：根據邊長與內角條件，判斷是否為正多邊形
    n_sides = random.choice([4, 5, 6, 7, 8])
    n_sides_str = _N_MAP[n_sides]
    
    # 30% of the time, ask the direct definition which is true
    if random.random() < 0.3:
        question_text = "一個多邊形的『所有邊長都相等』且『所有內角都相等』，請問這個多邊形『一定』是正多邊形嗎？(請回答『是』或『不是』)"
        correct_answer = "是"
    else:
        condition_type = random.choice(['sides_only', 'angles_only'])
        if condition_type == 'sides_only':
            question_text = f"小明用 {n_sides} 根長度皆相同的吸管圍成一個{n_sides_str}邊形，請問這個多邊形『一定』是正{n_sides_str}邊形嗎？(請回答『是』或『不是』)"
            # 解釋：例如四根等長吸管可以圍成菱形，但不一定是正方形(內角不相等)
        else: # angles_only
            question_text = f"有一個{n_sides_str}邊形，經測量後發現其所有內角都相等，請問這個多邊形『一定』是正{n_sides_str}邊形嗎？(請回答『是』或『不是』)"
            # 解釋：例如一個長方形所有內角都是90度，但不一定是正方形(邊長不相等)
        correct_answer = "不是"
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_naming_problem():
    # 題型：判斷多邊形的正確命名方式
    n_sides = random.choice([5, 6])
    n_sides_str = _N_MAP[n_sides]
    
    all_vertices = ['A', 'B', 'C', 'D', 'E', 'F']
    
    # Create a correct sequence by shuffling
    base_vertices = all_vertices[:n_sides]
    random.shuffle(base_vertices)
    
    # Generate two correct naming options
    correct_options = []
    start_idx1 = random.randint(0, n_sides - 1)
    seq1 = "".join([base_vertices[(start_idx1 + i) % n_sides] for i in range(n_sides)])
    correct_options.append(seq1)
    
    start_idx2 = random.randint(0, n_sides - 1)
    seq2 = "".join([base_vertices[(start_idx2 - i + n_sides) % n_sides] for i in range(n_sides)])
    if seq2 in correct_options: # Avoid duplicates
        start_idx2 = (start_idx2 + 1) % n_sides
        seq2 = "".join([base_vertices[(start_idx2 - i + n_sides) % n_sides] for i in range(n_sides)])
    correct_options.append(seq2)

    # Generate one guaranteed incorrect option by swapping non-adjacent vertices
    incorrect_list = list(base_vertices)
    idx1, idx2 = 0, random.randint(2, n_sides - 2)
    incorrect_list[idx1], incorrect_list[idx2] = incorrect_list[idx2], incorrect_list[idx1]
    incorrect_option = "".join(incorrect_list)

    # Combine and shuffle
    options = correct_options + [incorrect_option]
    random.shuffle(options)
    
    correct_answer_letter = chr(ord('A') + options.index(incorrect_option))
    polygon_name = f"{n_sides_str}邊形"
    
    question_text = (f"一個{n_sides_str}邊形的頂點依序為 ${' 	o '.join(base_vertices)}$。<br>"
                     f"下列哪一個標示『不可以』表示此多邊形？<br>"
                     f"$(A)$ {polygon_name} ${options[0]}$<br>"
                     f"$(B)$ {polygon_name} ${options[1]}$<br>"
                     f"$(C)$ {polygon_name} ${options[2]}$")
                     
    return {
        "question_text": question_text,
        "answer": correct_answer_letter,
        "correct_answer": correct_answer_letter
    }
    
def generate_diagonal_problem():
    # 題型：計算對角線數量
    n_sides = random.randint(5, 12)
    n_sides_str = _N_MAP[n_sides]

    prob_type = random.choice(['from_vertex', 'total'])
    
    if prob_type == 'from_vertex':
        answer = n_sides - 3
        question_text = f"從一個{n_sides_str}邊形的其中一個頂點，最多可以畫出幾條對角線？"
    else: # total
        answer = n_sides * (n_sides - 3) // 2
        question_text = f"一個{n_sides_str}邊形總共有幾條對角線？"
        
    return {
        "question_text": question_text,
        "answer": str(answer),
        "correct_answer": str(answer)
    }

def generate_angle_sum_problem():
    # 題型：計算內角和
    n_sides = random.randint(4, 12)
    n_sides_str = _N_MAP[n_sides]
    
    answer = (n_sides - 2) * 180
    
    question_text = f"一個{n_sides_str}邊形的內角和是幾度？"
    
    return {
        "question_text": question_text,
        "answer": str(answer),
        "correct_answer": str(answer)
    }

def generate_regular_polygon_angle_problem():
    # 題型：計算正多邊形的單一內角
    # We choose n-gons where the interior angle is an integer
    possible_n_sides = [3, 4, 5, 6, 8, 9, 10, 12, 15]
    n_sides = random.choice(possible_n_sides)
    n_sides_str = _N_MAP[n_sides]
    
    answer = (n_sides - 2) * 180 // n_sides
    
    question_text = f"一個『正』{n_sides_str}邊形的一個內角是幾度？"
    
    return {
        "question_text": question_text,
        "answer": str(answer),
        "correct_answer": str(answer)
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip().upper()
    correct_answer_str = str(correct_answer).strip().upper()
    
    is_correct = (user_answer == correct_answer_str)
    
    # Allow for flexible 'Yes/No' answers in Chinese
    if not is_correct:
        if correct_answer_str == "是" and user_answer in ["對", "TRUE", "YES", "T", "Y"]:
            is_correct = True
        elif correct_answer_str == "不是" and user_answer in ["否", "不對", "FALSE", "NO", "F", "N"]:
            is_correct = True

    # Allow for numeric answers to be compared as floats
    if not is_correct:
        try:
            if float(user_answer) == float(correct_answer_str):
                is_correct = True
        except (ValueError, TypeError):
            pass

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}
