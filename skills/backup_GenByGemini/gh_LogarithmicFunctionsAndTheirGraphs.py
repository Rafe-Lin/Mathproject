import random
import math
from fractions import Fraction

def generate(level=1):
    """
    生成「對數函數與其圖形」相關題目。
    包含：
    1. 對數函數的基本特性（定義域、值域、漸近線、定點、遞增遞減性）。
    2. 圖形的簡單變換（平移、對稱）。
    3. 對數函數與指數函數的關係。
    4. 複合變換的描述。
    5. 係數對圖形陡峭度及遞增遞減性的影響。
    """
    problem_types_by_level = {
        1: ['characteristics', 'simple_transformation', 'inverse_relation'],
        2: ['combined_transformation', 'coefficient_comparison']
    }
    
    # 合併當前等級及以下等級的題型
    all_available_types = []
    for l in range(1, level + 1):
        all_available_types.extend(problem_types_by_level.get(l, []))
    
    # 確保題型列表不為空，若 level 過高或未定義，則預設為 level 1 的題型
    if not all_available_types:
        all_available_types = problem_types_by_level[1]
        
    problem_type = random.choice(list(set(all_available_types))) # 使用 set 去除重複，並轉回 list 供 random.choice 使用

    if problem_type == 'characteristics':
        return generate_characteristics_problem()
    elif problem_type == 'simple_transformation':
        return generate_simple_transformation_problem()
    elif problem_type == 'inverse_relation':
        return generate_inverse_relation_problem()
    elif problem_type == 'combined_transformation':
        return generate_combined_transformation_problem()
    elif problem_type == 'coefficient_comparison':
        return generate_coefficient_comparison_problem()
    else:
        # Fallback to a basic problem type if an unexpected problem_type is generated (should not happen with current logic)
        return generate_characteristics_problem() 

# 輔助映射，用於生成對數函數基本特性問題
characteristic_map = {
    'domain': {'chinese_name': '定義域', 'answer': r"$(0, \\infty)$ 或 $x>0$"},
    'range': {'chinese_name': '值域', 'answer': r"$(-\\infty, \\infty)$ 或 $\\mathbb{{R}}$"},
    'vertical_asymptote': {'chinese_name': '鉛直漸近線', 'answer': r"$x=0$"},
    'fixed_point': {'chinese_name': '定點', 'answer': r"$(1, 0)$"},
    'increasing_decreasing': {'chinese_name': '遞增或遞減性質', 'answer': "遞增"} # 假設底數大於1
}

def get_log_func_str(base, var='x'):
    """根據底數和變數，返回對數函數的 LaTeX 字串。"""
    if base == 'e':
        return r"\\ln " + var
    elif base == 10:
        return r"\\log " + var
    else:
        return r"\\log_{" + str(base) + r"} " + var

def generate_characteristics_problem():
    """生成關於對數函數基本特性的問題。"""
    characteristic = random.choice(list(characteristic_map.keys()))
    
    base_choices = [2, 3, 5, 10, 'e'] # 目前只包含底數 > 1 的情況
    base = random.choice(base_choices) 
    
    func_str = get_log_func_str(base)
        
    question_text = f"關於函數 $y = {func_str}$ 的圖形，請填入其{characteristic_map[characteristic]['chinese_name']}。"
    
    correct_answer = characteristic_map[characteristic]['answer']
    
    return {
        "question_text": question_text,
        "answer": correct_answer, # 答案就是字串本身，用於直接檢查
        "correct_answer": correct_answer
    }

def generate_simple_transformation_problem():
    """生成關於對數函數簡單圖形變換的問題。"""
    base = random.choice([2, 10, 'e'])
    base_func_str = get_log_func_str(base)

    transformations = [
        {'type': 'reflect_x', 'desc': '對稱於x軸'},
        {'type': 'reflect_y', 'desc': '對稱於y軸'},
        {'type': 'horizontal_shift', 'desc': '水平移動', 'param': 'h'},
        {'type': 'vertical_shift', 'desc': '垂直移動', 'param': 'k'}
    ]
    
    chosen_transform = random.choice(transformations)
    
    transformed_func_str = ""
    correct_answer = ""
    
    if chosen_transform['type'] == 'reflect_x':
        transformed_func_str = r"-" + base_func_str
        correct_answer = "對稱於x軸"
    elif chosen_transform['type'] == 'reflect_y':
        # 需要重新生成函數字串，將變數替換為 (-x)
        transformed_func_str = get_log_func_str(base, var=r"(-x)")
        correct_answer = "對稱於y軸"
    elif chosen_transform['type'] == 'horizontal_shift':
        h = random.randint(1, 5) * random.choice([-1, 1])
        if h > 0:
            shift_dir = "右"
            transformed_func_str = get_log_func_str(base, var=f"(x - {h})")
        else:
            shift_dir = "左"
            transformed_func_str = get_log_func_str(base, var=f"(x + {abs(h)})") # (x - (-h)) becomes (x + h)
        correct_answer = f"向{shift_dir}平移${abs(h)}$單位"
    elif chosen_transform['type'] == 'vertical_shift':
        k = random.randint(1, 5) * random.choice([-1, 1])
        if k > 0:
            shift_dir = "上"
            transformed_func_str = f"{base_func_str} + {k}"
        else:
            shift_dir = "下"
            transformed_func_str = f"{base_func_str} - {abs(k)}"
        correct_answer = f"向{shift_dir}平移${abs(k)}$單位"
    
    question_text = f"函數 $y = {base_func_str}$ 的圖形經過何種變換會得到 $y = {transformed_func_str}$ 的圖形？"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_inverse_relation_problem():
    """生成關於對數函數反函數或其圖形關係的問題。"""
    base = random.choice([2, 3, 5, 10]) # 為簡化反函數字串，避免 'e'
    
    log_func_str = get_log_func_str(base)
    exp_func_str = r"{{" + str(base) + r"}}^{{x}}" # 指數函數的 LaTeX 形式
    
    question_type = random.choice(['find_inverse', 'relation_between_graphs'])
    
    if question_type == 'find_inverse':
        question_text = f"函數 $y = {log_func_str}$ 的反函數為何？"
        correct_answer = f"$y = {exp_func_str}$"
    else: # relation_between_graphs
        question_text = f"函數 $y = {log_func_str}$ 與其反函數的圖形有何幾何關係？"
        correct_answer = r"它們的圖形對稱於直線 $y=x$"
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_combined_transformation_problem():
    """生成關於對數函數複合圖形變換的描述問題。"""
    base = random.choice([2, 10])
    base_func_str = get_log_func_str(base)

    h_val = random.randint(1, 3) * random.choice([-1, 1])
    k_val = random.randint(1, 3) * random.choice([-1, 1])
    coeff_val = random.choice([-1, 1, 2, -2]) # c 值用於垂直伸縮/對稱
    
    transformed_func_parts = []
    answer_desc_parts = []

    # 構造變換後的函數字串
    if coeff_val == -1:
        transformed_func_parts.append(r"-")
    elif coeff_val == 2:
        transformed_func_parts.append(r"2")
    elif coeff_val == -2:
        transformed_func_parts.append(r"-2")
    
    # 處理對數參數中的水平平移
    log_arg = f"x - {h_val}"
    if h_val == 0:
        log_arg = "x"
    elif h_val < 0: # 處理 x - (-h) 變成 x + h 的情況
        log_arg = f"x + {abs(h_val)}"

    transformed_func_parts.append(get_log_func_str(base, var=f"({log_arg})")) # 例如: 2 * log_b (x-h)
    
    # 處理垂直平移
    if k_val > 0:
        transformed_func_parts.append(f" + {k_val}")
    elif k_val < 0:
        transformed_func_parts.append(f" - {abs(k_val)}")
        
    transformed_func_str = "".join(transformed_func_parts)

    # 構造正確答案的描述，遵循特定順序
    # 1. 對稱 / 垂直伸縮
    if coeff_val == -1:
        answer_desc_parts.append("對稱於x軸")
    elif coeff_val == 2:
        answer_desc_parts.append("垂直拉伸為2倍")
    elif coeff_val == -2:
        answer_desc_parts.append("對稱於x軸後垂直拉伸為2倍")

    # 2. 水平平移
    if h_val > 0:
        answer_desc_parts.append(f"向右平移${h_val}$單位")
    elif h_val < 0:
        answer_desc_parts.append(f"向左平移${abs(h_val)}$單位")
    
    # 3. 垂直平移
    if k_val > 0:
        answer_desc_parts.append(f"向上平移${k_val}$單位")
    elif k_val < 0:
        answer_desc_parts.append(f"向下平移${abs(k_val)}$單位")

    question_text = f"描述函數 $y = {transformed_func_str}$ 的圖形相較於 $y = {base_func_str}$ 的圖形，經歷了哪些變換？ (請條列說明，例如：'變換一；變換二；變換三'，各變換之間用全形分號「；」隔開，不需考慮順序)"
    
    correct_answer = "；".join(answer_desc_parts)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_coefficient_comparison_problem():
    """生成關於係數對對數函數圖形影響的問題。"""
    base = random.choice([2, 10])
    if base == 10:
        log_base_str = r"\\log x"
    else:
        log_base_str = r"\\log_{" + str(base) + r"} x"
        
    comparison_type = random.choice(['steepness_positive_c', 'increasing_decreasing_c'])

    if comparison_type == 'steepness_positive_c':
        c1 = random.randint(1, 4)
        c2 = random.randint(1, 4)
        while c1 == c2:
            c2 = random.randint(1, 4)
        
        # 確保 c1 總是代表更陡峭的圖形
        if c1 < c2:
            c1, c2 = c2, c1 
        
        func1_str = f"{c1}{log_base_str}"
        func2_str = f"{c2}{log_base_str}"
        
        question_text = (
            f"考慮函數 $y_1 = {func1_str}$ 和 $y_2 = {func2_str}$ "
            r"（假設底數大於1，且 $x>1$）。<br>"
            r"請問哪個函數的圖形在 $x>1$ 時更陡峭？(請填寫 $y_1$ 或 $y_2$)"
        )
        correct_answer = f"$y_1$" # 對於 c > 0 且 x > 1，|c| 越大圖形越陡峭
        
    elif comparison_type == 'increasing_decreasing_c':
        coeff = random.choice([-3, -2, 2, 3]) # 係數 c
        
        if coeff > 0:
            correct_behavior = "遞增"
        else: # coeff < 0
            correct_behavior = "遞減"
            
        func_str = f"{coeff}{log_base_str}"
            
        question_text = (
            f"考慮函數 $y = {func_str}$ "
            r"（假設底數大於1）。<br>"
            r"請問此函數的圖形是遞增還是遞減？"
        )
        correct_answer = correct_behavior

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def check(user_answer, correct_answer):
    """
    檢查使用者答案是否正確。
    處理常見的答案變體和正規化。
    """
    user_answer_norm = user_answer.strip().lower().replace(' ', '').replace('　', '') # 正規化使用者輸入
    correct_answer_norm = correct_answer.strip().lower().replace(' ', '').replace('　', '') # 正規化正確答案

    is_correct = False

    # 若正確答案包含「；」，表示是複合變換問題，需處理多個部分且不考慮順序
    if "；" in correct_answer_norm:
        # 將正確答案和使用者答案都按「；」分割，並對每個部分進行正規化
        correct_parts = [p.strip().lower().replace(' ', '').replace('　', '').replace('$', '') for p in correct_answer.split('；')]
        user_parts = [p.strip().lower().replace(' ', '').replace('　', '').replace('$', '') for p in user_answer.split('；')]
        
        # 對分割後的部件進行排序，以便進行順序無關的比較
        correct_parts.sort()
        user_parts.sort()
        
        if correct_parts == user_parts:
            is_correct = True
            
    else: # 對於單一答案的問題
        # 基本的直接比較（經過完整正規化後）
        if user_answer_norm == correct_answer_norm:
            is_correct = True
        else:
            # 針對常見的數學表達式或符號變體進行額外檢查
            # 定義域: (0,inf) vs x>0
            if correct_answer_norm == r"$(0,\\infty)$" and (user_answer_norm == r"$x>0$" or user_answer_norm == r"(0,inf)"):
                is_correct = True
            # 值域: (-inf,inf) vs R
            elif correct_answer_norm == r"$(-\\infty,\\infty)$" and (user_answer_norm == r"$\\mathbb{{r}}$" or user_answer_norm == r"(-inf,inf)" or user_answer_norm == r"r"):
                is_correct = True
            # 漸近線: x=0 vs y軸
            elif correct_answer_norm == r"$x=0$" and (user_answer_norm == r"x=0" or user_answer_norm == r"y軸"):
                is_correct = True
            # 定點: (1,0)
            elif correct_answer_norm == r"$(1,0)$" and user_answer_norm == r"(1,0)":
                is_correct = True
            # 反函數: y=a^x
            elif correct_answer_norm.startswith(r"$y=") and correct_answer_norm.endswith(r"$") and \
                 user_answer_norm.startswith(r"$y=") and user_answer_norm.endswith(r"$"):
                # 移除 LaTeX 和 y= 進行函數部分的比較
                clean_correct = correct_answer_norm[len(r"$y="):-len(r"$")].replace('{{', '').replace('}}', '')
                clean_user = user_answer_norm[len(r"$y="):-len(r"$")].replace('{{', '').replace('}}', '')
                if clean_correct == clean_user:
                    is_correct = True
            # 圖形關係: 對稱於 y=x
            elif correct_answer_norm == r"它們的圖形對稱於直線 $y=x$" and (user_answer_norm == r"對稱於y=x" or user_answer_norm == r"對稱於直線y=x" or user_answer_norm == r"對稱於直線$y=x$"):
                is_correct = True
            # 陡峭度比較: $y_1$ 或 $y_2$
            elif correct_answer_norm in ["$y_1$", "$y_2$"] and user_answer_norm == correct_answer_norm:
                is_correct = True
            # 遞增/遞減性質
            elif correct_answer_norm in ["遞增", "遞減"] and user_answer_norm == correct_answer_norm:
                is_correct = True

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}