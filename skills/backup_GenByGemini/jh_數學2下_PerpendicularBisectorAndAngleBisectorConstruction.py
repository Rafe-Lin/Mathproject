import random
from fractions import Fraction

def generate(level=1):
    """
    生成「尺規作圖：中垂線與角平分線」相關題目。
    包含：
    1. 觀念題：基於角平分線性質的角度計算。
    2. 原理題：作圖所基於的幾何圖形性質。
    3. 應用題：判斷特定作圖任務所需的方法。
    4. 條件題：作圖步驟中的關鍵條件判斷。
    """
    problem_type = random.choice(['conceptual_angle', 'property_recognition', 'application_id', 'step_condition'])

    if problem_type == 'conceptual_angle':
        return generate_conceptual_angle_problem()
    elif problem_type == 'property_recognition':
        return generate_property_recognition_problem()
    elif problem_type == 'application_id':
        return generate_application_identification_problem()
    else: # step_condition
        return generate_step_condition_problem()

def generate_conceptual_angle_problem():
    """
    基於角平分線性質的角度計算題。
    """
    total_angle = random.choice([180, random.randint(8, 16) * 10])
    answer = total_angle / 2
    if answer.is_integer():
        answer = int(answer)

    if total_angle == 180:
        question_text = f"若 $A$、$O$、$B$ 三點在同一直線上，且射線 $OD$ 是 $\\angle AOC$ 的角平分線，射線 $OE$ 是 $\\angle BOC$ 的角平分線，則 $\\angle DOE$ 的度數為何？（請填寫數字答案，不含單位）"
    else:
        question_text = f"已知 $\\angle AOB = {total_angle}^\\circ$，且 $OC$ 為 $\\angle AOB$ 內部的一條射線。若射線 $OD$ 是 $\\angle AOC$ 的角平分線，射線 $OE$ 是 $\\angle BOC$ 的角平分線，則 $\\angle DOE$ 的度數為何？（請填寫數字答案，不含單位）"

    correct_answer = str(answer)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_property_recognition_problem():
    """
    作圖原理題：辨認作圖所基於的幾何圖形。
    """
    construction_type = random.choice(['perpendicular_bisector', 'angle_bisector'])
    options = ['菱形', '箏形', '長方形', '梯形']
    random.shuffle(options)

    if construction_type == 'perpendicular_bisector':
        question_text = "中垂線作圖是利用哪一種四邊形的對角線會互相垂直平分的性質？"
        correct_answer_text = '菱形'
    else: # angle_bisector
        question_text = "角平分線作圖是利用哪一種四邊形的其中一條對角線（對稱軸）會平分頂角的性質？"
        correct_answer_text = '箏形'

    correct_answer_label = chr(ord('A') + options.index(correct_answer_text))
    
    options_str = ""
    for i, opt in enumerate(options):
        options_str += f"({chr(ord('A') + i)}) {opt} "
    
    question_text += f"<br>{options_str.strip()}"

    return {
        "question_text": question_text,
        "answer": correct_answer_label,
        "correct_answer": correct_answer_label
    }

def generate_application_identification_problem():
    """
    作圖應用題：判斷特定任務所需的方法。
    """
    scenarios = {
        "在 $\\triangle ABC$ 中，要作圖找出 $\\overline{AC}$ 邊上的高": "過線外一點作垂線",
        "若要在線段 $\\overline{CD}$ 上找一點 $M$，使得 $\\overline{CM} = \\overline{MD}$": "中垂線作圖",
        "已知直線 $L$ 及線上一點 $P$，要作一條通過 $P$ 點且與 $L$ 垂直的直線": "過線上一點作垂線",
        "若要將 $\\angle ABC$ 平分成兩個相等的角": "角平分線作圖",
    }

    chosen_task = random.choice(list(scenarios.keys()))
    correct_method = scenarios[chosen_task]
    
    options = ['中垂線作圖', '角平分線作圖', '過線上一點作垂線', '過線外一點作垂線']
    random.shuffle(options)

    correct_answer_label = chr(ord('A') + options.index(correct_method))
    
    options_str = ""
    for i, opt in enumerate(options):
        options_str += f"({chr(ord('A') + i)}) {opt} "

    question_text = f"請問若要完成以下任務：「{chosen_task}」，應使用下列何種尺規作圖方法？<br>{options_str.strip()}"

    return {
        "question_text": question_text,
        "answer": correct_answer_label,
        "correct_answer": correct_answer_label
    }
    
def generate_step_condition_problem():
    """
    作圖條件題：判斷作圖步驟中的關鍵條件。
    """
    construction_type = random.choice(['perpendicular_bisector', 'angle_bisector'])
    
    if construction_type == 'perpendicular_bisector':
        question_text = "在使用尺規作圖作線段 $\\overline{AB}$ 的中垂線時，會分別以 $A$、$B$ 為圓心畫弧。設此兩弧的半徑為 $r$，則 $r$ 必須滿足下列何種條件才能使兩弧相交於兩點？"
        options = [f"$r > \\overline{{AB}}$", f"$r = \\frac{{1}}{{2}} \\overline{{AB}}$", f"$r > \\frac{{1}}{{2}} \\overline{{AB}}$", f"$r < \\frac{{1}}{{2}} \\overline{{AB}}$"]
        correct_answer_text = f"$r > \\frac{{1}}{{2}} \\overline{{AB}}$"
    else: # angle_bisector
        question_text = "在使用尺規作圖作 $\\angle P$ 的角平分線時，第一步會以 $P$ 為圓心畫弧，交角的兩邊於 $A$、$B$ 兩點。第二步再分別以 $A$、$B$ 為圓心，以相同長度 $r$ 為半徑畫弧，則 $r$ 必須滿足下列何種條件才能確保兩弧一定有交點？"
        options = [f"$r > \\overline{{AB}}$", f"$r = \\frac{{1}}{{2}} \\overline{{AB}}$", f"$r > \\frac{{1}}{{2}} \\overline{{AB}}$", f"$r < \\overline{{AB}}$"]
        correct_answer_text = f"$r > \\frac{{1}}{{2}} \\overline{{AB}}$"

    random.shuffle(options)
    correct_answer_label = chr(ord('A') + options.index(correct_answer_text))
    
    options_str = ""
    for i, opt in enumerate(options):
        options_str += f"({chr(ord('A') + i)}) {opt} "

    question_text += f"<br>{options_str.strip()}"

    return {
        "question_text": question_text,
        "answer": correct_answer_label,
        "correct_answer": correct_answer_label
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip().upper()
    correct_answer = correct_answer.strip().upper()
    
    is_correct = (user_answer == correct_answer)
    
    if not is_correct:
        try:
            # Check for numerical equivalence if conversion is possible
            if float(user_answer) == float(correct_answer):
                is_correct = True
        except ValueError:
            pass

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}