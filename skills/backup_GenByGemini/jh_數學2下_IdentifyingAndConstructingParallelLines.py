import random

# Angle relationship definitions based on a standard diagram:
#    1 | 2
# -----|----- L1
#    4 | 3
# ----------- M
#    5 | 6
# -----|----- L2
#    8 | 7
ANGLE_PAIRS = {
    "同位角": [(1, 5), (2, 6), (4, 8), (3, 7)],
    "內錯角": [(4, 6), (3, 5)],
    "同側內角": [(4, 5), (3, 6)]
}

def generate_direct_check_problem():
    """
    Generates a question that directly tests one of the three parallel line conditions.
    """
    prop_name, _ = random.choice(list(ANGLE_PAIRS.items()))
    is_parallel = random.choice([True, False])

    angle1 = random.randint(30, 150)

    if prop_name == "同側內角":
        correct_angle2 = 180 - angle1
        if is_parallel:
            angle2 = correct_angle2
        else:
            offset = random.choice([-1, 1]) * random.randint(1, 10)
            angle2 = correct_angle2 + offset
        question_text = f"$L_1$ 與 $L_2$ 被一截線所截，一組{prop_name}分別為 ${angle1}^\\circ$ 和 ${angle2}^\\circ$。請問 $L_1$ 與 $L_2$ 是否平行？（請回答「平行」或「不平行」）"
    else: # 同位角 or 內錯角
        if is_parallel:
            angle2 = angle1
            question_text = f"$L_1$ 與 $L_2$ 被一截線所截，一組{prop_name}皆為 ${angle1}^\\circ$。請問 $L_1$ 與 $L_2$ 是否平行？（請回答「平行」或「不平行」）"
        else:
            offset = random.choice([-1, 1]) * random.randint(1, 10)
            angle2 = angle1 + offset
            question_text = f"$L_1$ 與 $L_2$ 被一截線所截，一組{prop_name}分別為 ${angle1}^\\circ$ 和 ${angle2}^\\circ$。請問 $L_1$ 與 $L_2$ 是否平行？（請回答「平行」或「不平行」）"
            
    correct_answer = "平行" if is_parallel else "不平行"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def _generate_angle_pair_condition(is_correct):
    """Helper to generate one condition for the calculation check problem."""
    prop_name, pairs = random.choice(list(ANGLE_PAIRS.items()))
    angle_idx1, angle_idx2 = random.choice(pairs)
    
    if random.random() < 0.5:
        angle_idx1, angle_idx2 = angle_idx2, angle_idx1

    val1 = random.randint(30, 150)
    
    if prop_name == "同側內角":
        correct_val2 = 180 - val1
        if is_correct:
            val2 = correct_val2
        else:
            offset = random.choice([-1, 1]) * random.randint(1, 10)
            val2 = correct_val2 + offset
    else: # 同位角 or 內錯角
        correct_val2 = val1
        if is_correct:
            val2 = correct_val2
        else:
            offset = random.choice([-1, 1]) * random.randint(1, 10)
            val2 = correct_val2 + offset
            if val2 <= 0 or val2 >= 180:
                 val2 = correct_val2 - offset
                 
    return f"$\\angle {angle_idx1} = {val1}^\\circ$，$\\angle {angle_idx2} = {val2}^\\circ$"

def generate_calculation_check_problem():
    """
    Generates a multiple-choice question asking which condition guarantees parallel lines.
    """
    question_desc = "假設兩直線 $L_1$、$L_2$ 被一直線 $M$ 所截，其截角位置如下圖編號所示。<br>"
    question_desc += "<pre>"
    question_desc += "   1 | 2 \n"
    question_desc += "-----|----- $L_1$"
    question_desc += "   4 | 3 \n"
    question_desc += "----------- $M$"
    question_desc += "   5 | 6 \n"
    question_desc += "-----|----- $L_2$"
    question_desc += "   8 | 7 \n"
    question_desc += "</pre>"
    question_desc += "下列哪一個條件能判斷 $L_1$ 與 $L_2$ 互相平行？"

    correct_condition = _generate_angle_pair_condition(is_correct=True)
    incorrect_condition1 = _generate_angle_pair_condition(is_correct=False)
    incorrect_condition2 = _generate_angle_pair_condition(is_correct=False)
    while incorrect_condition2 == incorrect_condition1:
        incorrect_condition2 = _generate_angle_pair_condition(is_correct=False)

    options = [correct_condition, incorrect_condition1, incorrect_condition2]
    random.shuffle(options)
    
    correct_answer_label = chr(ord('A') + options.index(correct_condition))

    question_text = f"{question_desc}<br>"
    question_text += f"(A) {options[0]}<br>"
    question_text += f"(B) {options[1]}<br>"
    question_text += f"(C) {options[2]}"

    return {
        "question_text": question_text,
        "answer": correct_answer_label,
        "correct_answer": correct_answer_label
    }

def _format_expr(a, b):
    """Helper to format ax+b into a string, handling signs and 1s."""
    if a == 0:
        return str(b)
    
    if a == 1:
        ax_part = "x"
    elif a == -1:
        ax_part = "-x"
    else:
        ax_part = f"{a}x"
        
    if b == 0:
        return ax_part
    elif b > 0:
        return f"{ax_part} + {b}"
    else: # b < 0
        return f"{ax_part} - {-b}"


def generate_algebra_problem():
    """
    Generates a problem where the student must find the value of x
    that makes two lines parallel.
    """
    prop_name, pairs = random.choice(list(ANGLE_PAIRS.items()))
    angle_idx1, angle_idx2 = random.choice(pairs)
    
    x = random.randint(5, 25)

    if prop_name == "同側內角":
        a1 = random.randint(1, 5)
        a2 = random.randint(1, 5)
        if random.random() < 0.3:
            a2 = -random.randint(1,3)
            if a1 + a2 == 0: a2 +=1
        b_sum = 180 - (a1 + a2) * x
        b1 = random.randint(-40, 40)
        b2 = b_sum - b1
        val1 = a1 * x + b1
        val2 = a2 * x + b2
        if not (20 < val1 < 160 and 20 < val2 < 160):
             return generate_algebra_problem()
    else: # 同位角 or 內錯角
        a1 = random.randint(2, 6)
        a2 = random.randint(1, 5)
        if a1 == a2: a2 -= 1
        b_diff = (a1 - a2) * x
        b2 = random.randint(-50, 50)
        b1 = b2 - b_diff
        val1 = a1 * x + b1
        if not (20 < val1 < 160):
            return generate_algebra_problem()

    expr1_str = _format_expr(a1, b1)
    expr2_str = _format_expr(a2, b2)

    question_text = f"已知兩直線 $L_1$、$L_2$ 互為平行，並被一直線所截。<br>若一對{prop_name}的角度分別為 $\\angle {angle_idx1} = ({expr1_str})^\\circ$ 與 $\\angle {angle_idx2} = ({expr2_str})^\\circ$，則 $x$ 的值為何？"

    return {
        "question_text": question_text,
        "answer": str(x),
        "correct_answer": str(x)
    }

def generate_construction_concept_problem():
    """
    Generates a conceptual question about parallel line construction.
    """
    q_pool = [
        {
            "q": "我們可以使用尺規作圖，過線外一點 $P$ 作一條與已知直線 $L$ 平行的直線。這個作圖方法是基於複製哪一個角度，來確保兩線平行？",
            "opts": ["直角", "平角", "與截線形成的一個夾角", "任意角度"],
            "ans": "C",
        },
        {
            "q": "使用一把直尺和一塊三角板畫平行線，其中一種方法是先畫一條通過目標點的垂線，再畫一條垂直於該垂線的直線。這個操作是利用了什麼原理？",
            "opts": ["同位角相等", "內錯角相等", "同時垂直於同一條直線的兩直線互相平行", "三角形內角和為180度"],
            "ans": "C",
        }
    ]
        
    chosen_q = random.choice(q_pool)
    options = chosen_q['opts']
    
    shuffled_options = options[:]
    random.shuffle(shuffled_options)
    
    correct_option_text = options[ord(chosen_q['ans']) - ord('A')] if len(chosen_q['ans'])==1 else None
    if chosen_q['ans'] == "C": # Specific to the defined questions
        correct_option_text = "與截線形成的一個夾角" if "尺規作圖" in chosen_q['q'] else "同時垂直於同一條直線的兩直線互相平行"
        
    correct_answer_label = chr(ord('A') + shuffled_options.index(correct_option_text))
    
    choices = [f"(A) {shuffled_options[0]}", f"(B) {shuffled_options[1]}", f"(C) {shuffled_options[2]}", f"(D) {shuffled_options[3]}"]
    
    question_text = chosen_q['q'] + "<br>" + "<br>".join(choices)

    return {
        "question_text": question_text,
        "answer": correct_answer_label,
        "correct_answer": correct_answer_label
    }

def generate(level=1):
    """
    生成「判別與畫出平行線」相關題目。
    包含：
    1. 根據截角性質直接判斷
    2. 從多個條件中選出可判斷平行的條件
    3. 利用平行性質反推未知數
    4. 平行線作圖的原理
    """
    problem_type = random.choice(['direct_check', 'calculation_check', 'algebra', 'construction_concept'])
    
    if problem_type == 'direct_check':
        return generate_direct_check_problem()
    elif problem_type == 'calculation_check':
        return generate_calculation_check_problem()
    elif problem_type == 'algebra':
        return generate_algebra_problem()
    else: # construction_concept
        return generate_construction_concept_problem()

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()

    is_correct = False
    if correct_answer in ["平行", "不平行"]:
        is_correct = (user_answer == correct_answer)
    elif correct_answer.isalpha() and len(correct_answer) == 1:
        is_correct = (user_answer.upper() == correct_answer.upper())
    else:
        try:
            if abs(float(user_answer) - float(correct_answer)) < 1e-9:
                is_correct = True
        except (ValueError, TypeError):
            pass
            
    if is_correct:
        result_text = f"完全正確！答案是 {correct_answer}。"
    else:
        result_text = f"答案不正確。正確答案應為：{correct_answer}"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}