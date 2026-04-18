import random
from fractions import Fraction

PROBLEM_TYPES = [
    'distance',
    'midpoint_chain',
    'symmetry_properties',
    'perpendicular_bisector_mcq',
    'shape_symmetry',
    'paper_folding'
]

def generate(level=1):
    """
    生成「中垂線與線對稱圖形」相關題目。
    包含：
    1. 點到直線的距離
    2. 線段中點的連鎖問題
    3. 線對稱圖形的性質
    4. 對稱軸與中垂線的關係
    5. 常見圖形的對稱軸數量
    6. 紙張摺疊與剪裁
    """
    problem_type = random.choice(PROBLEM_TYPES)
    
    if problem_type == 'distance':
        return generate_distance_problem()
    elif problem_type == 'midpoint_chain':
        return generate_midpoint_chain_problem()
    elif problem_type == 'symmetry_properties':
        return generate_symmetry_properties_problem()
    elif problem_type == 'perpendicular_bisector_mcq':
        return generate_perpendicular_bisector_mcq_problem()
    elif problem_type == 'shape_symmetry':
        return generate_shape_symmetry_problem()
    else: # paper_folding
        return generate_paper_folding_problem()

def generate_distance_problem():
    """
    題型：判斷點到直線的距離（垂直線段）。
    """
    points_on_line = random.sample(['A', 'B', 'C', 'D', 'E'], 3)
    point_off_line = random.choice([p for p in ['P', 'Q', 'R'] if p not in points_on_line])
    perpendicular_point = points_on_line[1]
    
    points_str = ', '.join(points_on_line)
    segment_name = f"{point_off_line}{perpendicular_point}"
    
    # 使用 \overline 來表示線段
    question_text = f"如圖所示，點 ${points_str}$ 在直線 L 上，且線段 $\overline{{{segment_name}}}$ 垂直於直線 L。請問 ${point_off_line}$ 點到直線 L 的距離是哪一個線段？（請填入線段名稱）"
    correct_answer = segment_name
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_midpoint_chain_problem():
    """
    題型：給定 AB 長度，M 為 AB 中點，N 為 AM 中點，求某段長度。
    """
    ab_len = random.randint(5, 20) * 4  # 確保可以整除 4
    am_len = ab_len / 2
    an_len = am_len / 2
    bn_len = ab_len - an_len
    
    # 決定題目要求 AN 還是 BN
    target_segment = random.choice(['AN', 'BN'])
    
    if target_segment == 'AN':
        correct_val = an_len
    else:
        correct_val = bn_len

    # 處理答案格式，如果是整數就不顯示 .0
    if correct_val.is_integer():
        correct_answer = str(int(correct_val))
    else:
        correct_answer = str(correct_val)
        
    question_text = f"已知線段 $\overline{{AB}}$ 的長度為 ${ab_len}$，M 為 $\overline{{AB}}$ 的中點，N 為 $\overline{{AM}}$ 的中點，請問 $\overline{{{target_segment}}}$ 的長度為多少？"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_symmetry_properties_problem():
    """
    題型：根據線對稱性質，求對應邊長或對應角度。
    """
    q_type = random.choice(['length', 'angle'])
    base_question = "右圖是以直線 L 為對稱軸的線對稱圖形，其中 A、B 的對稱點分別為 A'、B'。"
    
    if q_type == 'length':
        val = random.randint(3, 25)
        question_text = f"{base_question}<br>若 $\\overline{{AB}} = {val}$ 公分，則其對稱線段 $\\overline{{A'B'}}$ 的長度為多少公分？"
        correct_answer = str(val)
    else: # angle
        val = random.randint(20, 160)
        # 使用 \\circ 表示度
        question_text = f"{base_question}<br>若 $\\angle B = {val}^\\circ$，則其對稱角 $\\angle B'$ 的度數為多少度？（僅需填數字）"
        correct_answer = str(val)
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_perpendicular_bisector_mcq_problem():
    """
    題型：判斷對稱軸是否為某線段的中垂線（選擇題）。
    """
    points = random.sample(['A', 'B', 'C', 'D'], 3)
    p0, p1, p2 = points[0], points[1], points[2]
    
    # 安全地建立 LaTeX 字串
    p0_prime, p1_prime, p2_prime = f"{p0}'", f"{p1}'", f"{p2}'"
    seg1 = f"\overline{{{p0}{p0_prime}}}"
    seg2 = f"\overline{{{p1}{p1_prime}}}"
    seg3 = f"\overline{{{p2}{p2_prime}}}"
    wrong_seg = f"\overline{{{p0}{p1_prime}}}" # 混合非對稱點
    
    options = [seg1, seg2, seg3, wrong_seg]
    random.shuffle(options)
    
    answer_index = options.index(wrong_seg)
    correct_answer = chr(ord('A') + answer_index)
    
    question_text = (
        f"右圖是以直線 L 為對稱軸的線對稱圖形，其中 ${p0}$、${p1}$、${p2}$ 的對稱點分別為 ${p0_prime}$、${p1_prime}$、${p2_prime}$。"
        f"則直線 L <strong>不是</strong> 下列哪一個線段的中垂線？<br>"
        f"(A) ${options[0]}$<br>"
        f"(B) ${options[1]}$<br>"
        f"(C) ${options[2]}$<br>"
        f"(D) ${options[3]}$"
    )
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_shape_symmetry_problem():
    """
    題型：常見圖形的對稱軸數量。
    """
    shapes = {
        '長方形': '2',
        '等腰梯形': '1',
        '正五邊形': '5',
        '正三角形': '3',
        '菱形': '2',
        '正方形': '4',
        '箏形': '1' # 有一對對角相等
    }
    shape_name = random.choice(list(shapes.keys()))
    correct_answer = shapes[shape_name]
    
    question_text = f"請問一個「{shape_name}」有幾條對稱軸？"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_paper_folding_problem():
    """
    題型：紙張摺疊與剪裁的結果預測（概念題）。
    """
    question_text = (
        "將一張正方形紙張對摺兩次（例如，先上下對摺，再左右對摺），形成一個小正方形。"
        "接著，從兩條摺線交會的頂點處剪下一個圖形，再將紙張展開。"
        "請問展開後的圖形，中間的孔洞最可能為下列何種形狀？<br>"
        "(A) 正方形<br>"
        "(B) 菱形<br>"
        "(C) 十字形<br>"
        "(D) 圓形"
    )
    correct_answer = "B"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip().upper()
    correct_answer = correct_answer.strip().upper()
    
    is_correct = (user_answer == correct_answer)
    
    # 如果字串不匹配，嘗試以浮點數進行比較
    if not is_correct:
        try:
            if float(user_answer) == float(correct_answer):
                is_correct = True
        except ValueError:
            pass
    
    # 對於包含逗號的答案，例如 '2.5, 7.5'，進行分割比較
    if not is_correct and ',' in correct_answer:
        user_parts = [part.strip() for part in user_answer.split(',')]
        correct_parts = [part.strip() for part in correct_answer.split(',')]
        if len(user_parts) == len(correct_parts):
            try:
                if all(float(u) == float(c) for u, c in zip(user_parts, correct_parts)):
                    is_correct = True
            except ValueError:
                pass

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}
