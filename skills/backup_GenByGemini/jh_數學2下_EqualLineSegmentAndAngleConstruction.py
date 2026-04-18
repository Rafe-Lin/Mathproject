import random
from fractions import Fraction

# 使用 raw string 定義 LaTeX 指令
ANGLE_CMD = r"\angle"
OVERLINE_CMD = r"\overline"

def generate(level=1):
    """
    生成「等線段與等角作圖」相關題目。
    包含：
    1. 比較線段長短 (疊合與圓規)
    2. 比較角度大小 (圓規測量)
    3. 等線段作圖的目的
    4. 等角作圖的目的
    5. 尺規作圖的定義及規則
    """
    problem_type = random.choice([
        'compare_line_segments_overlap',
        'compare_line_segments_compass',
        'compare_angles_conceptual',
        'construct_equal_segment_purpose',
        'construct_equal_angle_purpose',
        'ruler_compass_definition'
    ])
    
    if problem_type == 'compare_line_segments_overlap':
        return generate_compare_line_segments_overlap()
    elif problem_type == 'compare_line_segments_compass':
        return generate_compare_line_segments_compass()
    elif problem_type == 'compare_angles_conceptual':
        return generate_compare_angles_conceptual()
    elif problem_type == 'construct_equal_segment_purpose':
        return generate_construct_equal_segment_purpose()
    elif problem_type == 'construct_equal_angle_purpose':
        return generate_construct_equal_angle_purpose()
    elif problem_type == 'ruler_compass_definition':
        return generate_ruler_compass_definition()

def generate_compare_line_segments_overlap():
    """
    生成比較線段長短的題目，情境為疊合。
    """
    scenarios = [
        {"desc": "若 $D$ 點落在 $A$、$B$ 兩點之間", "answer_raw": "AB", "answer_latex": r"$\overline{AB}$"},
        {"desc": "若 $B$ 點落在 $C$、$D$ 兩點之間", "answer_raw": "CD", "answer_latex": r"$\overline{CD}$"},
        {"desc": "若 $B$ 點與 $D$ 點重合", "answer_raw": "AB 與 CD 相等", "answer_latex": r"$\overline{AB}$ 與 $\overline{CD}$ 相等"}
    ]
    
    chosen_scenario = random.choice(scenarios)
    
    # 使用 {{ }} 轉義 f-string 中的大括號
    question_text = (
        f"已知 ${OVERLINE_CMD}{{AB}}$、${OVERLINE_CMD}{{CD}}$，比較兩線段長短時，將 ${OVERLINE_CMD}{{AB}}$ 移到 ${OVERLINE_CMD}{{CD}}$ 上，"
        f"使 $A$ 點與 $C$ 點重合。{chosen_scenario['desc']}，則哪一個線段較長？(若相等請回答：AB 與 CD 相等)"
    )
    
    return {
        "question_text": question_text,
        "answer": chosen_scenario['answer_raw'], 
        "correct_answer": chosen_scenario['answer_raw']
    }

def generate_compare_line_segments_compass():
    """
    生成比較線段長短的題目，情境為圓規測量。
    """
    scenarios = [
        {"compare_op": "大於", "answer_raw": "AB", "answer_latex": r"$\overline{AB}$"},
        {"compare_op": "小於", "answer_raw": "CD", "answer_latex": r"$\overline{CD}$"},
        {"compare_op": "等於", "answer_raw": "AB 與 CD 相等", "answer_latex": r"$\overline{AB}$ 與 $\overline{CD}$ 相等"}
    ]
    
    chosen_scenario = random.choice(scenarios)
    
    question_text = (
        f"比較兩線段 ${OVERLINE_CMD}{{AB}}$ 與 ${OVERLINE_CMD}{{CD}}$ 的長短，"
        f"若以 $A$ 點為圓心，${OVERLINE_CMD}{{AB}}$ 長為半徑畫弧，再以 $C$ 點為圓心，${OVERLINE_CMD}{{CD}}$ 長為半徑畫弧，"
        f"發現 ${OVERLINE_CMD}{{AB}}$ 的長度{chosen_scenario['compare_op']}${OVERLINE_CMD}{{CD}}$ 的長度，"
        f"則哪一個線段較長？(若相等請回答：AB 與 CD 相等)"
    )
        
    return {
        "question_text": question_text,
        "answer": chosen_scenario['answer_raw'],
        "correct_answer": chosen_scenario['answer_raw']
    }

def generate_compare_angles_conceptual():
    """
    生成比較角度大小的題目，情境為圓規測量兩邊交點距離。
    """
    angles = ['A', 'B']
    random.shuffle(angles)
    angle1_label, angle2_label = angles[0], angles[1]

    comparison_results = [
        {"relationship": "大於", "answer_raw": f"L{angle1_label}", "answer_latex": f"$\\angle {angle1_label}$"},
        {"relationship": "小於", "answer_raw": f"L{angle2_label}", "answer_latex": f"$\\angle {angle2_label}$"},
        {"relationship": "等於", "answer_raw": f"L{angle1_label} 與 L{angle2_label} 相等", "answer_latex": f"$\\angle {angle1_label}$ 與 $\\angle {angle2_label}$ 相等"}
    ]
    
    chosen_result = random.choice(comparison_results)
    
    question_text = (
        f"比較 ${ANGLE_CMD} {angle1_label}$ 與 ${ANGLE_CMD} {angle2_label}$ 的大小，"
        f"若以兩角的頂點為圓心，相同長度為半徑畫弧，"
        f"且發現 ${ANGLE_CMD} {angle1_label}$ 兩邊與弧的交點距離{chosen_result['relationship']}${ANGLE_CMD} {angle2_label}$ 兩邊與弧的交點距離，"
        f"則哪一個角度較大？(若相等請回答：L{angle1_label} 與 L{angle2_label} 相等)"
    )
    
    return {
        "question_text": question_text,
        "answer": chosen_result['answer_raw'],
        "correct_answer": chosen_result['answer_raw']
    }

def generate_construct_equal_segment_purpose():
    """
    生成關於等線段作圖目的的題目。
    """
    correct_answers_pool = [
        "畫出與已知線段等長的線段",
        "複製已知線段的長度",
        "將已知線段的長度轉移到其他位置"
    ]
    
    correct_answer = random.choice(correct_answers_pool)
    
    question_template = [
        f"在尺規作圖中，已知線段 ${OVERLINE_CMD}{{AB}}$，我們如何畫出線段 ${OVERLINE_CMD}{{CD}}$ 使得 ${OVERLINE_CMD}{{CD}} = {OVERLINE_CMD}{{AB}}$？此作圖的目的是什麼？",
        f"當我們使用尺規作圖複製線段 ${OVERLINE_CMD}{{AB}}$ 到一條直線上，使之成為 ${OVERLINE_CMD}{{CD}}$，這項作圖的目的是什麼？",
        f"尺規作圖中，複製線段長度的基本操作，目的是什麼？"
    ]
    
    question_text = random.choice(question_template)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_construct_equal_angle_purpose():
    """
    生成關於等角作圖目的的題目。
    """
    correct_answers_pool = [
        "畫出與已知角等大的角",
        "複製一個角的角度大小",
        "將一個角的角度轉移到其他位置"
    ]
    
    correct_answer = random.choice(correct_answers_pool)

    question_template = [
        f"尺規作圖中，複製 ${ANGLE_CMD} A$ 的目的為何？",
        f"若要畫出一個與已知 ${ANGLE_CMD} A$ 等大的角，這項作圖的目的是什麼？",
        f"尺規作圖複製角度時，最終目標是什麼？"
    ]

    question_text = random.choice(question_template)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_ruler_compass_definition():
    """
    生成關於尺規作圖定義及規則的題目。
    """
    question_data = [
        {"q_type": "definition", "question": "尺規作圖的定義是什麼？", "ans": "只使用沒有刻度的直尺和圓規進行的幾何作圖"},
        {"q_type": "allowed_tools", "question": "尺規作圖允許使用哪些工具？", "ans": "沒有刻度的直尺和圓規"},
        {"q_type": "forbidden_actions_ruler", "question": "在尺規作圖中，直尺有哪些限制？(請列出一項)", "ans": "直尺不能用來測量長度"},
        {"q_type": "forbidden_actions_compass", "question": "在尺規作圖中，圓規有哪些限制？(請列出一項)", "ans": "圓規不能直接用來畫直線或移動刻度"}
    ]
    
    chosen_data = random.choice(question_data)
    
    return {
        "question_text": chosen_data['question'],
        "answer": chosen_data['ans'],
        "correct_answer": chosen_data['ans']
    }

def normalize_text_for_comparison(text):
    """
    正規化文本用於比較：去除首尾空白、轉為小寫、移除所有非字母數字及非中文字符。
    """
    text = text.strip().lower()
    normalized_chars = []
    for char in text:
        if char.isalnum() or ('\u4e00' <= char <= '\u9fff'):
            normalized_chars.append(char)
    return "".join(normalized_chars)

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_norm = normalize_text_for_comparison(str(user_answer))
    correct_norm = normalize_text_for_comparison(str(correct_answer))
    
    is_correct = False

    if user_norm == correct_norm:
        is_correct = True
    else:
        # 關鍵字寬鬆匹配
        keywords = ["ab", "cd", "la", "lb", "相等", "直尺", "圓規", "刻度", "測量", "複製"]
        matched = 0
        required = 0
        for kw in keywords:
            if kw in correct_norm:
                required += 1
                if kw in user_norm:
                    matched += 1
        
        if required > 0 and matched >= required:
            is_correct = True
                
    result_text = f"完全正確！答案是：{correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}。"
    return {"correct": is_correct, "result": result_text, "next_question": True}