import random
from fractions import Fraction
import math

def generate_unique_solution_problem():
    """
    生成具有唯一解的向量聯立方程式題目。
    $x\vec{v_1} + y\vec{v_2} = \vec{b}$
    其中 $\vec{v_1}$ 和 $\vec{v_2}$ 線性獨立。
    """
    # 隨機生成唯一的解 (x_sol, y_sol)
    x_sol = random.randint(-3, 3)
    y_sol = random.randint(-3, 3)

    # 確保至少有一個非零解，除非目標向量是(0,0)，那樣(0,0)也是唯一解
    # 此處允許 (0,0) 作為解，這在數學上是有效的
    
    # 隨機生成向量 v1 和 v2 的分量
    while True:
        a = random.randint(-5, 5)
        c = random.randint(-5, 5)
        b = random.randint(-5, 5)
        d = random.randint(-5, 5)

        # 確保 v1 和 v2 不是零向量
        if (a == 0 and c == 0) or (b == 0 and d == 0):
            continue
        
        # 檢查是否存在唯一解 (行列式不為零)
        # 即 a*d - b*c != 0
        if (a * d - b * c) != 0:
            break
    
    # 計算目標向量 b 的分量
    e = a * x_sol + b * y_sol
    f = c * x_sol + d * y_sol

    question_text = (
        f"考慮下列向量方程式：<br>"
        f"$x\\begin{{pmatrix}} {{ {a} }} \\\\ {{ {c} }} \\end{{pmatrix}} + y\\begin{{pmatrix}} {{ {b} }} \\\\ {{ {d} }} \\end{{pmatrix}} = \\begin{{pmatrix}} {{ {e} }} \\\\ {{ {f} }} \\end{{pmatrix}}$<br>"
        f"請問是否存在一組實數 $x, y$ 滿足此方程式？若存在，請寫出 $(x, y)$ 的值，以逗號分隔；若不存在，請回答 '無解'。"
        f"（如果存在無限多組解，請回答 '無限多組解'）"
    )
    correct_answer = f"{x_sol},{y_sol}"

    return {
        "question_text": question_text,
        "answer": correct_answer, # 在這裡 'answer' 和 'correct_answer' 相同
        "correct_answer": correct_answer
    }

def generate_no_solution_problem():
    """
    生成無解的向量聯立方程式題目。
    $x\vec{v_1} + y\vec{v_2} = \vec{b}$
    其中 $\vec{v_1}$ 和 $\vec{v_2}$ 線性相關 (平行)，且 $\vec{b}$ 不與它們共線。
    """
    while True:
        # 生成 v1
        a = random.randint(-5, 5)
        c = random.randint(-5, 5)

        # 確保 v1 不是零向量
        if a == 0 and c == 0:
            continue

        # 生成一個非零、非一的倍數 k，使 v2 = k * v1
        k = random.choice([-2, -1, 2, 3]) 
        b = k * a
        d = k * c
        
        # 至此，v1 和 v2 是平行的 (線性相關)
        
        # 生成目標向量 b_vec(e, f)，使其不與 v1 (和 v2) 平行
        # 即 a*f - c*e != 0
        e = random.randint(-5, 5)
        f = random.randint(-5, 5)

        # 確保目標向量不是零向量 (否則可能變成無限多組解)
        if e == 0 and f == 0:
            continue
        
        # 檢查 b_vec 是否與 v1 平行。如果是，重新生成 b_vec。
        # 處理 a 或 c 為零的特殊情況
        if a == 0: # v1 = (0, c)，v1是垂直向量
            if c == 0: # 應被前面的 `a==0 and c==0` 捕捉
                continue
            # 若 b_vec (e, f) 要不與 v1 平行，e 必須不為零
            while e == 0:
                e = random.randint(-5, 5)
        elif c == 0: # v1 = (a, 0)，v1是水平向量
            # 若 b_vec (e, f) 要不與 v1 平行，f 必須不為零
            while f == 0:
                f = random.randint(-5, 5)
        else: # 一般情況，a != 0 且 c != 0
            # 確保 a*f - c*e != 0
            while (a * f - c * e) == 0:
                e = random.randint(-5, 5)
                f = random.randint(-5, 5)
        
        break # 成功生成有效向量
    
    question_text = (
        f"考慮下列向量方程式：<br>"
        f"$x\\begin{{pmatrix}} {{ {a} }} \\\\ {{ {c} }} \\end{{pmatrix}} + y\\begin{{pmatrix}} {{ {b} }} \\\\ {{ {d} }} \\end{{pmatrix}} = \\begin{{pmatrix}} {{ {e} }} \\\\ {{ {f} }} \\end{{pmatrix}}$<br>"
        f"請問是否存在一組實數 $x, y$ 滿足此方程式？若存在，請寫出 $(x, y)$ 的值，以逗號分隔；若不存在，請回答 '無解'。"
        f"（如果存在無限多組解，請回答 '無限多組解'）"
    )
    correct_answer = "無解"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_infinite_solution_problem():
    """
    生成無限多組解的向量聯立方程式題目。
    $x\vec{v_1} + y\vec{v_2} = \vec{b}$
    其中 $\vec{v_1}$ 和 $\vec{v_2}$ 線性相關 (平行)，且 $\vec{b}$ 也與它們共線。
    """
    while True:
        # 生成 v1
        a = random.randint(-5, 5)
        c = random.randint(-5, 5)
        
        if a == 0 and c == 0: # v1 不能是零向量
            continue
            
        # 生成一個非零、非一的倍數 k_v2，使 v2 = k_v2 * v1
        k_v2 = random.choice([-2, -1, 2, 3]) 
        b = k_v2 * a
        d = k_v2 * c
        
        # 至此，v1 和 v2 是平行的
        
        # 生成一個非零的倍數 k_b，使目標向量 b_vec = k_b * v1
        k_b = random.choice([-3, -2, -1, 2, 3]) 
        e = k_b * a
        f = k_b * c
        
        # 確保目標向量 b_vec 不是零向量，除非它來自於 v1,v2 也是零向量的組合 (k_b=0)
        # 允許 b_vec 是零向量，因為此時也有無限多組解
        # 例如：x(1,2) + y(2,4) = (0,0) -> x+2y=0，有無窮多解
        
        break # 成功生成有效向量
    
    question_text = (
        f"考慮下列向量方程式：<br>"
        f"$x\\begin{{pmatrix}} {{ {a} }} \\\\ {{ {c} }} \\end{{pmatrix}} + y\\begin{{pmatrix}} {{ {b} }} \\\\ {{ {d} }} \\end{{pmatrix}} = \\begin{{pmatrix}} {{ {e} }} \\\\ {{ {f} }} \\end{{pmatrix}}$<br>"
        f"請問是否存在一組實數 $x, y$ 滿足此方程式？若存在，請寫出 $(x, y)$ 的值，以逗號分隔；若不存在，請回答 '無解'。"
        f"（如果存在無限多組解，請回答 '無限多組解'）"
    )
    correct_answer = "無限多組解"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    生成「從向量的線性組合觀點來討論二元一次聯立方程式的解」相關題目。
    包含：
    1. 唯一解 (向量線性獨立)
    2. 無解 (向量線性相關但目標向量不共線)
    3. 無限多組解 (向量線性相關且目標向量共線)
    """
    
    problem_type_choices = ['unique_solution', 'no_solution']
    if level >= 2: # 隨著難度提升，加入無限多組解的題目
        problem_type_choices.append('infinite_solution')
    
    problem_type = random.choice(problem_type_choices)
    
    if problem_type == 'unique_solution':
        return generate_unique_solution_problem()
    elif problem_type == 'no_solution':
        return generate_no_solution_problem()
    else: # 'infinite_solution'
        return generate_infinite_solution_problem()

def check(user_answer, correct_answer):
    """
    檢查使用者答案是否正確。
    支援 (x,y) 數值解、'無解' 和 '無限多組解'。
    """
    user_answer_normalized = user_answer.strip().lower().replace(' ', '')
    correct_answer_normalized = correct_answer.strip().lower().replace(' ', '')

    is_correct = (user_answer_normalized == correct_answer_normalized)
    
    if not is_correct:
        # 對於數值型答案 (x,y) 進行浮點數比較
        if ',' in correct_answer_normalized and ',' in user_answer_normalized:
            try:
                user_x_str, user_y_str = user_answer_normalized.split(',')
                correct_x_str, correct_y_str = correct_answer_normalized.split(',')
                
                user_x = float(Fraction(user_x_str))
                user_y = float(Fraction(user_y_str))
                correct_x = float(Fraction(correct_x_str))
                correct_y = float(Fraction(correct_y_str))
                
                # 使用一個小的容忍度進行浮點數比較
                if math.isclose(user_x, correct_x) and math.isclose(user_y, correct_y):
                    is_correct = True
            except (ValueError, ZeroDivisionError):
                pass # 不是有效的 (x,y) 數值對，或分數轉換錯誤
    
    # 根據答案類型格式化回饋訊息
    if ',' in correct_answer_normalized:
        x_val, y_val = correct_answer_normalized.split(',')
        if is_correct:
            result_text = f"完全正確！答案是 $(x, y) = ({x_val}, {y_val})$。"
        else:
            result_text = f"答案不正確。正確答案應為：$(x, y) = ({x_val}, {y_val})$"
    elif correct_answer_normalized == "無解":
        if is_correct:
            result_text = f"完全正確！答案是 '無解'。"
        else:
            result_text = f"答案不正確。正確答案應為：'無解'"
    elif correct_answer_normalized == "無限多組解":
        if is_correct:
            result_text = f"完全正確！答案是 '無限多組解'。"
        else:
            result_text = f"答案不正確。正確答案應為：'無限多組解'"
    else:
        # 預設的回饋訊息
        if is_correct:
            result_text = f"完全正確！答案是 {correct_answer_normalized}。"
        else:
            result_text = f"答案不正確。正確答案應為：{correct_answer_normalized}"

    return {"correct": is_correct, "result": result_text, "next_question": True}