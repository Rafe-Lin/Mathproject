import random
import math
from fractions import Fraction

# Helper function to generate coefficients, ensuring not all are zero for normal vectors
def get_coeffs(num, min_val=-5, max_val=5, allow_zero=False):
    """
    Generates a list of 'num' coefficients.
    If 'allow_zero' is False, at least one coefficient in the final list (or set of three)
    should be non-zero to prevent degenerate planes. For a single coefficient, it won't be zero.
    """
    coeffs = []
    for _ in range(num):
        while True:
            c = random.randint(min_val, max_val)
            if allow_zero or c != 0: # For individual coeffs, if not allow_zero, must be non-zero
                coeffs.append(c)
                break
    return coeffs

def generate(level=1):
    """
    生成空間中一點到一平面的距離公式或兩平行平面間的距離公式相關題目。
    """
    problem_type = random.choice([
        'point_to_plane_direct',        # 點到平面的距離計算
        'parallel_planes_direct',       # 兩平行平面間的距離計算
        'point_to_plane_find_param',    # 已知距離求平面參數
        'true_false_formula',           # 判斷距離公式是否正確 (通常是少了絕對值)
    ])
    
    if problem_type == 'point_to_plane_direct':
        return generate_point_to_plane_direct()
    elif problem_type == 'parallel_planes_direct':
        return generate_parallel_planes_direct()
    elif problem_type == 'point_to_plane_find_param':
        return generate_point_to_plane_find_param()
    elif problem_type == 'true_false_formula':
        return generate_true_false_formula()

def generate_point_to_plane_direct():
    """
    生成求點 P(x0, y0, z0) 到平面 Ax + By + Cz = D 的距離的題目。
    """
    
    # 生成平面係數 (A, B, C) 和常數 (D_rhs for Ax+By+Cz=D)
    # 確保 A, B, C 不全為零，以定義一個有效平面
    while True:
        A, B, C = get_coeffs(3, min_val=-5, max_val=5, allow_zero=True)
        if A != 0 or B != 0 or C != 0:
            break
    D_rhs = random.randint(-15, 15) # D 在等號右側
    
    # 生成點座標 (x0, y0, z0)
    x0, y0, z0 = get_coeffs(3, min_val=-5, max_val=5, allow_zero=True)

    # 題目文字：點 P(x0, y0, z0) 到平面 Ax + By + Cz = D_rhs 的距離
    question_text = (
        f"求點 $P({x0}, {y0}, {z0})$ 到平面 ${{ {A}x + {B}y + {C}z = {D_rhs} }}$ 的距離。"
    )

    # 計算分子部分：|Ax0 + By0 + Cz0 - D_rhs| (因為平面方程式是 Ax+By+Cz - D_rhs = 0)
    numerator_val = abs(A * x0 + B * y0 + C * z0 - D_rhs)
    
    # 計算分母部分：sqrt(A^2 + B^2 + C^2)
    denominator_sq = A**2 + B**2 + C**2
    denominator_val = math.sqrt(denominator_sq)

    # 計算最終答案
    if denominator_val == 0: # Should not happen if A,B,C not all zero, but for safety
        correct_answer = Fraction(0)
    elif numerator_val == 0:
        correct_answer = Fraction(0)
    elif denominator_val.is_integer():
        correct_answer = Fraction(numerator_val, int(denominator_val))
    else:
        # 如果分母不是整數，則答案為浮點數，保留4位小數
        correct_answer = numerator_val / denominator_val
    
    correct_answer_str = str(correct_answer)
    if isinstance(correct_answer, Fraction) and correct_answer.denominator == 1:
        correct_answer_str = str(correct_answer.numerator)
    elif isinstance(correct_answer, float):
        correct_answer_str = f"{{ {correct_answer:.4f} }}" # 使用大括號來確保f-string轉義LaTeX

    explanation = (
        f"利用點到平面的距離公式，得所求距離為"
        f"$\\frac{{|{A} \\times {x0} + {B} \\times {y0} + {C} \\times {z0} - ({D_rhs})|}}{{\\sqrt{{ {A}^2 + {B}^2 + {C}^2 }}}} = "
        f"\\frac{{|{A*x0 + B*y0 + C*z0 - D_rhs}|}}{{\\sqrt{{ {A**2 + B**2 + C**2} }}}} = {correct_answer_str}$。"
    )
    
    return {
        "question_text": question_text,
        "answer": correct_answer_str,
        "correct_answer": correct_answer_str,
        "explanation": explanation
    }

def generate_parallel_planes_direct():
    """
    生成求兩平行平面 Ax + By + Cz = D1 和 k(Ax + By + Cz) = D2 的距離的題目。
    """
    
    # 生成基本法向量 (A, B, C)
    while True:
        A, B, C = get_coeffs(3, min_val=-4, max_val=4, allow_zero=True)
        if A != 0 or B != 0 or C != 0:
            break
            
    # 生成兩個平面的常數項
    D1 = random.randint(-10, 10)
    D2_orig = random.randint(-10, 10) # 原始的D2，稍後會被縮放
    
    # 確保兩個平面不重合
    while D1 == D2_orig:
        D2_orig = random.randint(-10, 10)

    # 隨機選擇一個縮放因子，讓其中一個平面方程式看起來不同
    scale_factor = random.choice([1, 2, -1, 3]) 
    if scale_factor == 1 and A==0 and B==0 and C==0: # Ensure not all zero
        scale_factor = 2 

    # 平面 E1: E1_A x + E1_B y + E1_C z = E1_D
    E1_A, E1_B, E1_C = A, B, C
    E1_D = D1

    # 平面 E2: (scale_factor * A)x + (scale_factor * B)y + (scale_factor * C)z = (scale_factor * D2_orig)
    E2_A = scale_factor * A
    E2_B = scale_factor * B
    E2_C = scale_factor * C
    E2_D = scale_factor * D2_orig # 這裡 E2_D 是已經縮放過的 D 值

    question_text = (
        f"求兩平行平面 $E_1 : {{ {E1_A}x + {E1_B}y + {E1_C}z = {E1_D} }}$ 和 $E_2 : {{ {E2_A}x + {E2_B}y + {E2_C}z = {E2_D} }}$ 的距離。"
    )

    # 計算距離前，需將 E2 正規化到與 E1 相同的法向量
    # E2 的 D 值，若其法向量與 E1 相同，應為 E2_D / scale_factor
    normalized_D2_frac = Fraction(E2_D, scale_factor)

    numerator_val = abs(E1_D - normalized_D2_frac)
    
    denominator_sq = E1_A**2 + E1_B**2 + E1_C**2
    denominator_val = math.sqrt(denominator_sq)

    # 計算最終答案
    if denominator_val == 0:
        correct_answer = Fraction(0)
    elif numerator_val == 0:
        correct_answer = Fraction(0)
    elif denominator_val.is_integer():
        correct_answer = Fraction(numerator_val, int(denominator_val))
    else:
        correct_answer = numerator_val / denominator_val
        
    correct_answer_str = str(correct_answer)
    if isinstance(correct_answer, Fraction) and correct_answer.denominator == 1:
        correct_answer_str = str(correct_answer.numerator)
    elif isinstance(correct_answer, float):
        correct_answer_str = f"{{ {correct_answer:.4f} }}"

    explanation = (
        f"先將平面 $E_2$ 的方程式改寫為與 $E_1$ 具有相同法向量的形式。"
        f"將 $E_2 : {{ {E2_A}x + {E2_B}y + {E2_C}z = {E2_D} }}$ 除以 ${{ {scale_factor} }}$，得 ${{ {E1_A}x + {E1_B}y + {E1_C}z = {normalized_D2_frac} }}$。"
        f"再利用兩平行平面的距離公式 $\\frac{{|D_1 - D_2|}}{{\\sqrt{{A^2 + B^2 + C^2}}}}$，得 $E_1$ 與 $E_2$ 的距離為 "
        f"$\\frac{{|({E1_D}) - ({normalized_D2_frac})|}}{{\\sqrt{{ {E1_A}^2 + {E1_B}^2 + {E1_C}^2 }}}} = \\frac{{|{float(numerator_val)}|}}{{\\sqrt{{ {denominator_sq} }}}} = {correct_answer_str}$。"
    )

    return {
        "question_text": question_text,
        "answer": correct_answer_str,
        "correct_answer": correct_answer_str,
        "explanation": explanation
    }


def generate_point_to_plane_find_param():
    """
    生成已知點 P(x0, y0, z0) 到平面 Ax + By + Cz = d 的距離為 dist，求 d 的值的題目。
    此類題目通常有兩解。
    """

    # 生成法向量 (A, B, C)，使其 A^2+B^2+C^2 為完全平方數，以便分母為整數
    # 常見的選項可以包括 (2,3,-6) -> 49, (1,2,2) -> 9, (4,-4,2) -> 36, (1,0,0) -> 1 等
    normal_options = [
        (2, 3, -6), (-1, 2, 2), (4, -4, 2), (1, 0, 0), (0, 1, 0), (0, 0, 1),
        (3, 0, 4), (0, -3, 4)
    ]
    A, B, C = random.choice(normal_options)
    
    # 隨機正負號變化，增加題目多樣性
    if random.random() < 0.5: A = -A
    if random.random() < 0.5: B = -B
    if random.random() < 0.5: C = -C
    
    # 計算分母值，此時應為整數
    denominator_val = math.sqrt(A**2 + B**2 + C**2) 
    
    # 生成點座標 (x0, y0, z0)
    x0, y0, z0 = get_coeffs(3, min_val=-5, max_val=5, allow_zero=True)

    # 生成一個距離值，使得 d 的解為整數
    dist = random.randint(1, 5) 
    
    # 平面方程式為 Ax + By + Cz = d
    # 距離公式: dist = |A*x0 + B*y0 + C*z0 - d| / denominator_val
    # => dist * denominator_val = |A*x0 + B*y0 + C*z0 - d|
    
    val_xyz_term = A * x0 + B * y0 + C * z0
    
    # K = dist * denominator_val
    K = dist * int(denominator_val) # K 為整數
    
    # 因此，K = |val_xyz_term - d|，有兩種情況
    # 情況 1: K = val_xyz_term - d  => d = val_xyz_term - K
    d1 = val_xyz_term - K
    # 情況 2: -K = val_xyz_term - d => d = val_xyz_term + K
    d2 = val_xyz_term + K

    # 將答案排序，以便檢查時一致
    correct_answers = sorted([d1, d2])
    
    # 題目文字
    question_text = (
        f"已知點 $P({x0}, {y0}, {z0})$ 到平面 ${{ {A}x + {B}y + {C}z = d }}$ 的距離為 ${dist}$，"
        f"求 $d$ 的值。(答案有兩解，請以半形逗號分隔，由小到大排列)"
    )
    
    correct_answer_str = f"{correct_answers[0]}, {correct_answers[1]}"

    explanation = (
        f"利用點到平面的距離公式 $\\frac{{|Ax_0 + By_0 + Cz_0 - d|}}{{\\sqrt{{A^2 + B^2 + C^2}}}} = {dist}$。"
        f"將點 $P({x0}, {y0}, {z0})$ 和平面 ${{ {A}x + {B}y + {C}z - d = 0 }}$ 的係數代入，得 "
        f"$\\frac{{|{A} \\times {x0} + {B} \\times {y0} + {C} \\times {z0} - d|}}{{\\sqrt{{ {A}^2 + {B}^2 + {C}^2 }}}} = {dist}$"
        f"<br>"
        f"$\\frac{{|{val_xyz_term} - d|}}{{{int(denominator_val)}}} = {dist}$"
        f"<br>"
        f"$|{val_xyz_term} - d| = {dist} \\times {int(denominator_val)} = {K}$"
        f"<br>"
        f"因此，${val_xyz_term} - d = {K}$ 或 ${val_xyz_term} - d = -{K}$。"
        f"<br>"
        f"解得 $d = {d1}$ 或 $d = {d2}$。"
        f"所以 $d$ 的值為 ${correct_answers[0]}, {correct_answers[1]}$。"
    )
    
    return {
        "question_text": question_text,
        "answer": correct_answer_str,
        "correct_answer": correct_answer_str,
        "explanation": explanation
    }

def generate_true_false_formula():
    """
    生成判斷點到平面距離公式寫法是否正確的題目 (通常是少了絕對值)。
    """
    
    # 生成平面係數 (A, B, C) 和常數 (D_rhs)
    while True:
        A, B, C = get_coeffs(3, min_val=-4, max_val=4, allow_zero=True)
        if A != 0 or B != 0 or C != 0:
            break
    D_rhs = random.randint(-10, 10)

    # 生成點座標 (x0, y0, z0)
    x0, y0, z0 = get_coeffs(3, min_val=-3, max_val=3, allow_zero=True)

    # 計算分子部分 (不帶絕對值)
    numerator_val_no_abs = A * x0 + B * y0 + C * z0 - D_rhs
    
    # 計算分母的平方
    denominator_sq = A**2 + B**2 + C**2
    
    # 構造錯誤或不完整的公式顯示 (分子部分缺少絕對值符號)
    formula_display = (
        r"\\frac{{ {A} \\times {x0} + {B} \\times {y0} + {C} \\times {z0} - ({D_rhs}) }}{{\\sqrt{{ {A}^2 + ({B})^2 + ({C})^2 }}}}"
    )

    question_text = (
        f"下列敘述對的打「○」，錯的打「×」。"
        f"<br>"
        f"□ 點 $({x0}, {y0}, {z0})$ 到平面 ${{ {A}x + {B}y + {C}z = {D_rhs} }}$ 的距離為 ${formula_display}$。"
    )
    
    # 該敘述是「×」因為公式缺少絕對值符號，即使計算結果恰巧為正。
    correct_answer = "×" 

    explanation = (
        f"點到平面的距離公式的分子部分必須取絕對值。"
        f"正確的公式應為 $\\frac{{|{A} \\times {x0} + {B} \\times {y0} + {C} \\times {z0} - ({D_rhs})|}}{{\\sqrt{{ {A}^2 + ({B})^2 + ({C})^2 }}}}$。"
        f"原敘述分子部分缺少絕對值符號，故為「×」。"
    )

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "explanation": explanation
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip().replace(" ", "") # 移除空格
    correct_answer = correct_answer.strip().replace(" ", "")
    
    is_correct = False
    result_text = ""

    # 處理是非題
    if correct_answer in ["○", "×"]:
        is_correct = (user_answer == correct_answer)
        result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    else:
        # 處理數值型答案，包括分數和多個答案的情況 (參數d的兩解)
        try:
            # 如果正確答案包含逗號，表示有多個解 (例如 d 的兩解)
            if "," in correct_answer:
                # 解析並排序用戶答案和正確答案
                user_answers = sorted([float(Fraction(x.strip())) for x in user_answer.split(',')])
                correct_answers = sorted([float(Fraction(x.strip())) for x in correct_answer.split(',')])
                
                # 檢查長度是否相同且所有對應元素是否近似相等
                if len(user_answers) == len(correct_answers):
                    is_correct = all(math.isclose(u, c, rel_tol=1e-5, abs_tol=1e-5) for u, c in zip(user_answers, correct_answers))
            else:
                # 單一數值答案 (分數或浮點數)
                # 使用 Fraction 處理分數，然後轉換為 float 進行浮點數比較
                user_num = float(Fraction(user_answer))
                correct_num = float(Fraction(correct_answer))
                is_correct = math.isclose(user_num, correct_num, rel_tol=1e-5, abs_tol=1e-5)
        except (ValueError, ZeroDivisionError):
            is_correct = False # 用戶輸入無效數值或分母為零

        if is_correct:
            result_text = f"完全正確！答案是 ${correct_answer}$。"
        else:
            result_text = f"答案不正確。正確答案應為：${correct_answer}$"

    return {"correct": is_correct, "result": result_text, "next_question": True}