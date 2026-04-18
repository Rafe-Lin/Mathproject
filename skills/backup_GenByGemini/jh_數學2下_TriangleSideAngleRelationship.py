import random
import re

def generate(level=1):
    """
    生成「三角形邊角關係」相關題目。
    包含：
    1. 大邊對大角、大角對大邊
    2. 等腰三角形邊角關係
    3. 複合圖形中的邊角關係推論
    """
    problem_types = [
        'two_sides_compare_angles',
        'two_angles_compare_sides',
        'isosceles_angle_compare_sides',
        'side_relations_compare_angles',
        'multi_triangle_compare_sides'
    ]
    problem_type = random.choice(problem_types)

    if problem_type == 'two_sides_compare_angles':
        return generate_two_sides_compare_angles()
    elif problem_type == 'two_angles_compare_sides':
        return generate_two_angles_compare_sides()
    elif problem_type == 'isosceles_angle_compare_sides':
        return generate_isosceles_angle_compare_sides()
    elif problem_type == 'side_relations_compare_angles':
        return generate_side_relations_compare_angles()
    else:  # multi_triangle_compare_sides
        return generate_multi_triangle_compare_sides()

def generate_two_sides_compare_angles():
    """
    題型：已知兩邊長，比較對角大小。
    """
    side_ab = random.randint(5, 25)
    side_ac = side_ab
    while side_ac == side_ab:
        side_ac = random.randint(5, 25)

    # 角C對應邊AB，角B對應邊AC
    # 大邊對大角
    if side_ac > side_ab:
        relation = '>'  # ∠B > ∠C
    else:
        relation = '<'  # ∠B < ∠C

    question_text = f"在 $\\triangle ABC$ 中，已知 $\\overline{{AB}} = {side_ab}$，$\\overline{{AC}} = {side_ac}$，則 $\\angle B$ 與 $\\angle C$ 的大小關係為何？ (請填入 $>$、= 或 $<$) "
    correct_answer = relation

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_two_angles_compare_sides():
    """
    題型：已知兩角，比較三邊長大小。
    """
    angle_a = random.randint(30, 100)
    angle_b = random.randint(30, 149 - angle_a)
    angle_c = 180 - angle_a - angle_b
    
    # 確保角度不相等，避免邊長相等的情況
    while len({angle_a, angle_b, angle_c}) < 3:
        angle_a = random.randint(30, 100)
        angle_b = random.randint(30, 149 - angle_a)
        angle_c = 180 - angle_a - angle_b

    angles = {'A': angle_a, 'B': angle_b, 'C': angle_c}
    sides_map = {'A': 'BC', 'B': 'AC', 'C': 'AB'}

    # 依角度大小降序排列
    sorted_angles = sorted(angles.items(), key=lambda item: item[1], reverse=True)
    
    # 找出對應的邊
    sorted_sides = [sides_map[angle[0]] for angle in sorted_angles]
    
    # 格式化答案字串
    correct_answer = f"{sorted_sides[0]}>{sorted_sides[1]}>{sorted_sides[2]}"

    question_text = f"在 $\\triangle ABC$ 中，已知 $\\angle A = {angle_a}^\\circ$，$\\angle B = {angle_b}^\\circ$，則三邊長 $\\overline{{AB}}$、$\\overline{{BC}}$、$\\overline{{AC}}$ 的大小關係為何？ (請由大到小以 > 連接，例如 AC>BC>AB)"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_isosceles_angle_compare_sides():
    """
    題型：已知等腰三角形一角，比較邊長。
    """
    # 避免產生正三角形
    avoid_angles = {60}

    # Case 1: 給定頂角 A
    if random.random() < 0.5:
        # 確保頂角為偶數，使底角為整數
        angle_a = random.choice([i for i in range(10, 178, 2) if i not in avoid_angles])
        angle_c = (180 - angle_a) / 2
        question_text = f"在等腰 $\\triangle ABC$ 中，$\\overline{{AB}} = \\overline{{AC}}$ 且 $\\angle A = {angle_a}^\\circ$。試比較 $\\overline{{BC}}$ 與 $\\overline{{AB}}$ 的大小關係。 (請填入 $>$、= 或 $<$) "

    # Case 2: 給定底角 B
    else:
        angle_b = random.choice([i for i in range(1, 90) if i not in avoid_angles])
        angle_c = angle_b
        angle_a = 180 - 2 * angle_b
        question_text = f"在等腰 $\\triangle ABC$ 中，$\\overline{{AB}} = \\overline{{AC}}$ 且 $\\angle B = {angle_b}^\\circ$。試比較 $\\overline{{BC}}$ 與 $\\overline{{AB}}$ 的大小關係。 (請填入 $>$、= 或 $<$) "

    # 比較 BC 與 AB，即比較其對角 ∠A 與 ∠C
    if angle_a > angle_c:
        relation = '>'
    elif angle_a < angle_c:
        relation = '<'
    else:
        relation = '='
        
    return {
        "question_text": question_text,
        "answer": relation,
        "correct_answer": relation
    }

def generate_side_relations_compare_angles():
    """
    題型：已知邊的相對關係，比較角的大小。
    """
    vertices = ['A', 'B', 'C']
    random.shuffle(vertices)
    v1, v2, v3 = vertices[0], vertices[1], vertices[2]

    # 等長的兩邊為 v1v3 和 v2v3，其對角 ∠v2 和 ∠v1 相等。
    # 第三邊為 v1v2，其對角為 ∠v3。
    
    relation_word = random.choice(['最短', '最長'])
    
    # 比較一個底角和頂角的大小
    q_angles = random.sample([v1, v3], 2)
    q_angle1, q_angle2 = q_angles[0], q_angles[1]
    
    question_text = f"在 $\\triangle {v1}{v2}{v3}$ 中，已知 $\\overline{{{v1}{v3}}}=\\overline{{{v2}{v3}}}$，且 $\\overline{{{v1}{v2}}}$ 為{relation_word}邊，判斷 $\\angle {q_angle1}$ 與 $\\angle {q_angle2}$ 的大小關係。 (請填入 $>$、= 或 $<$) "

    # 推理：
    # 比較邊 v1v2 和 v1v3 的大小關係，即可推得其對角 ∠v3 和 ∠v2 的大小關係。
    if relation_word == '最短':  # v1v2 < v1v3 => ∠v3 < ∠v2
        relation_v3_v2 = '<'
    else:  # v1v2 > v1v3 => ∠v3 > ∠v2
        relation_v3_v2 = '>'

    # 由於 ∠v1 = ∠v2，因此 ∠v3 與 ∠v1 的關係和 ∠v3 與 ∠v2 的關係相同。
    if q_angle1 == v3:  # 比較 ∠v3 和 ∠v1 (或 ∠v2)
        correct_answer = relation_v3_v2
    else:  # 比較 ∠v1 (或 ∠v2) 和 ∠v3
        correct_answer = '>' if relation_v3_v2 == '<' else '<'
            
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_multi_triangle_compare_sides():
    """
    題型：在相鄰的兩個三角形中，利用共用邊比較三個線段的大小。
    """
    # 為了產生清晰的鏈式關係 (如 A>B>C)，中間項必須是共用邊 DB。
    possible_orders = [
        ('DC', 'DB', 'DA'), 
        ('DA', 'DB', 'DC')
    ]
    s_max, s_mid, s_min = random.choice(possible_orders)
    # 隨機決定是從大到小還是從小到大
    if random.random() < 0.5:
        s_max, s_mid, s_min = s_min, s_mid, s_max

    # 根據大小關係，生成對應的角度
    # 在 △DAB 中，比較 DA (對角∠DBA) 和 DB (對角∠DAB)
    base_angle1 = random.randint(45, 65)
    diff1 = random.randint(5, 15)
    if (s_max, s_mid) == ('DA', 'DB') or (s_mid, s_min) == ('DA', 'DB'): # DA > DB
        angle_DAB = base_angle1
        angle_DBA = base_angle1 + diff1
    else: # DA < DB
        angle_DAB = base_angle1 + diff1
        angle_DBA = base_angle1
    
    # 在 △DBC 中，比較 DB (對角∠DCB) 和 DC (對角∠DBC)
    base_angle2 = random.randint(45, 65)
    diff2 = random.randint(5, 15)
    if (s_max, s_mid) == ('DC', 'DB') or (s_mid, s_min) == ('DC', 'DB'): # DC > DB
        angle_DBC = base_angle2 + diff2
        angle_DCB = base_angle2
    else: # DC < DB
        angle_DBC = base_angle2
        angle_DCB = base_angle2 + diff2

    question_text = (f"在一個凸四邊形 $ABCD$ 中，連接對角線 $\\overline{{DB}}$。"
                     f"已知在 $\\triangle DAB$ 中，$\\angle DAB = {angle_DAB}^\\circ$ 且 $\\angle DBA = {angle_DBA}^\\circ$。"
                     f"在 $\\triangle DBC$ 中，$\\angle DBC = {angle_DBC}^\\circ$ 且 $\\angle DCB = {angle_DCB}^\\circ$。"
                     f"請比較 $\\overline{{DA}}$、$\\overline{{DB}}$、$\\overline{{DC}}$ 三個線段的長度關係。 (請由大到小以 > 連接，例如 DC>DB>DA)")
    
    correct_answer = f"{s_max}>{s_mid}>{s_min}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    # 標準化使用者答案：移除空白並轉為大寫
    user_ans = user_answer.strip().replace(" ", "").upper()
    # 標準化正確答案
    corr_ans = correct_answer.strip().replace(" ", "").upper()

    is_correct = (user_ans == corr_ans)

    # 將答案格式化為 LaTeX 以便顯示
    def format_for_latex(answer_string):
        if answer_string in ['>', '<', '=']:
            return answer_string
        # 使用正規表示式將所有邊的代號（如 AC）轉換為 LaTeX 格式（如 \\overline{AC}）
        return re.sub(r'[A-Z]+', lambda m: f"\\overline{{{m.group(0)}}}", answer_string)

    latex_answer = format_for_latex(corr_ans)

    if is_correct:
        result_text = f"完全正確！答案是 ${latex_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${latex_answer}$"

    return {"correct": is_correct, "result": result_text, "next_question": True}