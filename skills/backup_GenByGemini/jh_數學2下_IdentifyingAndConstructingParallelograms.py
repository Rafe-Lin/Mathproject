import random
import re

def generate(level=1):
    """
    生成「判斷與建構平行四邊形」相關題目。
    包含：
    1. 依據角度判斷
    2. 依據邊長判斷
    3. 依據代數式角度判斷
    4. 依據判別性質選擇
    5. 依據尺規作圖方法判斷
    """
    problem_type = random.choice([
        'identify_by_angles', 
        'identify_by_sides', 
        'algebra_angles', 
        'property_mcq',
        'construction_method'
    ])
    
    if problem_type == 'identify_by_angles':
        return generate_identify_by_angles_problem()
    elif problem_type == 'identify_by_sides':
        return generate_identify_by_sides_problem()
    elif problem_type == 'algebra_angles':
        return generate_algebra_angles_problem()
    elif problem_type == 'property_mcq':
        return generate_property_mcq_problem()
    else: # construction_method
        return generate_construction_method_problem()

def generate_identify_by_angles_problem():
    # 題型：給定數組四邊形內角，判斷哪些是平行四邊形
    options_labels = ['甲', '乙', '丙', '丁']
    num_options = 4
    correct_count = random.randint(1, 2)
    
    is_parallelogram_flags = [True] * correct_count + [False] * (num_options - correct_count)
    random.shuffle(is_parallelogram_flags)
    
    options_text_parts = []
    correct_labels = []
    
    for i in range(num_options):
        if is_parallelogram_flags[i]:
            a = random.randint(40, 140)
            b = 180 - a
            if random.random() < 0.5:
                angles = [a, b, a, b]
            else:
                angles = [b, a, b, a]
            correct_labels.append(options_labels[i])
        else:
            # Generate a non-parallelogram
            a = random.randint(40, 140)
            b = random.randint(40, 140)
            c = random.randint(40, 140)
            if a + b + c >= 330 or a + b + c <= 100: # Ensure d is in a reasonable range
                c = 120
            d = 360 - a - b - c
            # Ensure it doesn't accidentally become a parallelogram
            if (a == c and b == d):
                a += 5
                d -= 5
            angles = [a, b, c, d]
            
        options_text_parts.append(f"{options_labels[i]}：${angles[0]}° , {angles[1]}° , {angles[2]}° , {angles[3]}°$")
        
    question_text = "小明用色紙剪了四個不同的四邊形，並將它們的四個內角依 $\\angle A$、$\\angle B$、$\\angle C$、$\\angle D$ 的順序寫在下面，則哪些四邊形必為平行四邊形？<br>"
    question_text += "<br>".join(options_text_parts)
    
    correct_answer = "".join(sorted(correct_labels))
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_identify_by_sides_problem():
    # 題型：給定數組四邊形邊長，判斷哪些是平行四邊形
    options_labels = ['甲', '乙', '丙', '丁']
    num_options = 4
    correct_count = random.randint(1, 2)

    is_parallelogram_flags = [True] * correct_count + [False] * (num_options - correct_count)
    random.shuffle(is_parallelogram_flags)
    
    options_text_parts = []
    correct_labels = []
    
    for i in range(num_options):
        if is_parallelogram_flags[i]:
            s1 = random.randint(3, 10)
            s2 = random.randint(3, 10)
            sides = [s1, s2, s1, s2] # AB, BC, CD, DA
            correct_labels.append(options_labels[i])
        else:
            # Generate a non-parallelogram (e.g., a kite or random)
            if random.random() < 0.5: # Kite
                s1 = random.randint(3, 10)
                s2 = random.randint(3, 10)
                while s1 == s2:
                    s2 = random.randint(3, 10)
                sides = [s1, s1, s2, s2]
            else: # Random, but ensure not parallelogram
                s1 = random.randint(3, 10)
                s2 = random.randint(3, 10)
                s3 = random.randint(3, 10)
                s4 = random.randint(3, 10)
                if s1 == s3 and s2 == s4: # Avoid accidental parallelogram
                    s3 += 1
                sides = [s1, s2, s3, s4]
            
        options_text_parts.append(f"{options_labels[i]}：${sides[0]} cm , {sides[1]} cm , {sides[2]} cm , {sides[3]} cm$")
        
    question_text = "小華利用木棍排了四個不同的四邊形，並將它們的邊長依 $\\overline{AB}$、$\\overline{BC}$、$\\overline{CD}$、$\\overline{DA}$ 的順序寫在下面，則哪些四邊形必為平行四邊形？<br>"
    question_text += "<br>".join(options_text_parts)
    
    correct_answer = "".join(sorted(correct_labels))
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_algebra_angles_problem():
    # 題型：四邊形內角用代數表示，判斷是否為平行四邊形
    x_sol = random.randint(10, 30)
    is_para = random.choice([True, False])
    
    # Function to create an expression for an angle
    def create_expr(target_val, x_sol, used_coeffs):
        while True:
            coeff = random.randint(2, 9)
            if coeff not in used_coeffs:
                break
        const = target_val - coeff * x_sol
        used_coeffs.append(coeff)
        if const == 0:
            return f"{coeff}x"
        elif const > 0:
            return f"{coeff}x + {const}"
        else:
            return f"{coeff}x - {-const}"

    used_coeffs = []
    if is_para:
        angle_A_val = random.randint(50, 130)
        angle_B_val = 180 - angle_A_val
        angle_C_val = angle_A_val
        angle_D_val = angle_B_val
        correct_answer = "是"
    else:
        # Create 4 angles that sum to 360 but don't form a parallelogram
        angle_A_val = random.randint(50, 130)
        angle_B_val = random.randint(50, 130)
        angle_C_val = random.randint(50, 130)
        if angle_A_val + angle_B_val + angle_C_val > 320:
            angle_C_val = 100
        angle_D_val = 360 - angle_A_val - angle_B_val - angle_C_val
        if (angle_A_val == angle_C_val and angle_B_val == angle_D_val): # Avoid accidental parallelogram
             angle_C_val -= 10
             angle_D_val += 10
        correct_answer = "否"

    expr_A = create_expr(angle_A_val, x_sol, used_coeffs)
    expr_B = create_expr(angle_B_val, x_sol, used_coeffs)
    expr_C = create_expr(angle_C_val, x_sol, used_coeffs)
    expr_D = create_expr(angle_D_val, x_sol, used_coeffs)
    
    question_text = (
        f"四邊形 ABCD 中，$\\angle A = ({expr_A})°$，$\\angle B = ({expr_B})°$，"
        f"$\\angle C = ({expr_C})°$，$\\angle D = ({expr_D})°$。<br>"
        "請問在求出 $x$ 值後，此四邊形 ABCD 是不是平行四邊形？ (請回答 是 或 否)"
    )
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }
    
def generate_property_mcq_problem():
    # 題型：選擇題，判斷哪個條件足以證明為平行四邊形
    correct_conditions = [
        ("$\\overline{AB} = \\overline{CD}$ 且 $\\overline{AD} = \\overline{BC}$", "兩雙對邊分別相等"),
        ("$\\angle A = \\angle C$ 且 $\\angle B = \\angle D$", "兩雙對角分別相等"),
        ("$\\overline{AB} // \\overline{CD}$ 且 $\\overline{AB} = \\overline{CD}$", "一雙對邊平行且相等"),
        ("對角線 $\\overline{AC}$ 與 $\\overline{BD}$ 互相平分", "兩對角線互相平分")
    ]
    
    incorrect_conditions = [
        "$\\overline{AB} // \\overline{CD}$ 且 $\\overline{AD} = \\overline{BC}$", # Isosceles trapezoid case
        "$\\overline{AC} \\perp \\overline{BD}$", # Kite/Rhombus property
        "對角線 $\\overline{AC}$ 平分 $\\angle A$ 與 $\\angle C$", # Rhombus property
        "$\\angle A + \\angle B = 180°$", # Trapezoid property
        "$\\overline{AB} = \\overline{BC}$ 且 $\\overline{CD} = \\overline{DA}$" # Kite property
    ]

    chosen_correct = random.choice(correct_conditions)[0]
    chosen_incorrect = random.sample(incorrect_conditions, 3)
    
    options = [chosen_correct] + chosen_incorrect
    random.shuffle(options)
    
    correct_label = chr(ord('A') + options.index(chosen_correct))
    
    options_text = [f"({chr(ord('A') + i)}) {opt}" for i, opt in enumerate(options)]
    
    question_text = "下列哪一個條件，足以判斷四邊形 ABCD 必為平行四邊形？<br>" + "<br>".join(options_text)
    
    return {
        "question_text": question_text,
        "answer": correct_label,
        "correct_answer": correct_label
    }

def generate_construction_method_problem():
    # 題型：描述尺規作圖過程，判斷其根據的性質
    properties = [
        "兩雙對角分別相等",
        "兩雙對邊分別相等",
        "一雙對邊平行且相等",
        "兩對角線互相平分"
    ]

    methods = [
        {
            "description": "⑴ 作 $\\overline{BA}$ 與 $\\overline{BC}$。<br>⑵ 分別以 A、C 為圓心，$\\overline{BC}$、$\\overline{AB}$ 長為半徑畫弧，設兩弧交於 D 點。<br>⑶ 連接 $\\overline{AD}$、$\\overline{CD}$，得到四邊形 ABCD。",
            "correct_property": "兩雙對邊分別相等"
        },
        {
            "description": "⑴ 作 $\\overline{BA}$ 與 $\\overline{BC}$。<br>⑵ 過 C 作直線 L 平行於 $\\overline{AB}$。<br>⑶ 在直線 L 上取一點 D，使得 $\\overline{CD} = \\overline{AB}$。<br>⑷ 連接 $\\overline{AD}$，得到四邊形 ABCD。",
            "correct_property": "一雙對邊平行且相等"
        },
        {
            "description": "⑴ 給定兩線段 $\\overline{AC}$ 與 $\\overline{BD}$。<br>⑵ 找出兩線段的中點 O。<br>⑶ 將兩線段疊合，使其中心點 O 重合。<br>⑷ 依序連接 A, B, C, D 四點，得到四邊形 ABCD。",
            "correct_property": "兩對角線互相平分"
        }
    ]

    chosen_method = random.choice(methods)
    
    # The options will be the list of properties, shuffled.
    options = list(properties)
    random.shuffle(options)
    
    correct_label = chr(ord('A') + options.index(chosen_method["correct_property"]))
    
    options_text = [f"({chr(ord('A') + i)}) {prop}" for i, prop in enumerate(options)]
    
    question_text = (
        f"已知平面上 A、B、C 三點，阿誠按照下面的作圖步驟畫了一個四邊形 ABCD。<br>"
        f"{chosen_method['description']}<br>"
        f"請問阿誠是根據哪一個判別性質，得知四邊形 ABCD 為平行四邊形？<br>" + 
        "<br>".join(options_text)
    )

    return {
        "question_text": question_text,
        "answer": correct_label,
        "correct_answer": correct_label
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer_str = str(user_answer).strip()
    correct_answer_str = str(correct_answer).strip()

    # Normalize Chinese answers for Yes/No
    if '是' in correct_answer_str or '否' in correct_answer_str:
        if user_answer_str.lower() in ['y', 'yes', '是', 'true']:
            user_answer_str = '是'
        elif user_answer_str.lower() in ['n', 'no', '否', 'false']:
            user_answer_str = '否'

    # Normalize multi-character answers (e.g., 甲乙, 乙, 甲) by sorting
    # This also handles single character answers like 'A', 'B'
    normalized_user_answer = "".join(sorted(re.sub(r'[\s,]', '', user_answer_str).upper()))
    normalized_correct_answer = "".join(sorted(re.sub(r'[\s,]', '', correct_answer_str).upper()))
    
    is_correct = (normalized_user_answer == normalized_correct_answer)

    if is_correct:
        result_text = f"完全正確！答案是 {correct_answer_str}。"
    else:
        result_text = f"答案不正確。正確答案應為：{correct_answer_str}"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}