import random

def generate(level=1):
    """
    生成國中一年級上學期，基於幾何圖形的一元一次方程式應用問題。
    題型包含：
    1. 梯形面積問題
    2. 長方形周長問題
    3. 三角形內角和問題
    4. 組合圖形面積問題 (長方形挖去三角形)
    """
    problem_generators = [
        generate_trapezoid_area_problem,
        generate_rectangle_perimeter_problem,
        generate_triangle_angles_problem,
        generate_cutout_area_problem
    ]
    generator_func = random.choice(problem_generators)
    return generator_func()

def generate_trapezoid_area_problem():
    """
    題型：已知梯形上底、下底與上底的關係、高、面積，求上底。
    """
    # 預設解答 x (上底)
    x = random.randint(4, 10)
    
    # 下底 = a*x - b
    a = random.choice([2, 3])
    b = random.randint(1, 5)
    lower_base_val = a * x - b
    
    # 確保下底為正數
    while lower_base_val <= 0:
        x = random.randint(b // a + 2, 10)
        lower_base_val = a * x - b

    # 高設定為偶數，方便計算，避免答案出現分數
    h = random.choice([4, 6, 8, 10])

    area = int(((x + lower_base_val) / 2) * h)

    question_text = f"已知一個梯形，其上底為 $x$ 公分，下底比上底的 ${a}$ 倍少 ${b}$ 公分。若此梯形的高為 ${h}$ 公分，面積為 ${area}$ 平方公分，請問上底的長度是多少公分？"
    correct_answer = str(x)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_rectangle_perimeter_problem():
    """
    題型：已知長方形的長、寬皆為 x 的表達式，並給定周長，求 x。
    """
    x = random.randint(2, 10)
    a = random.randint(1, 5)
    b = random.randint(1, 5)
    
    # 確保長寬表達式不同
    while a == b:
        b = random.randint(1, 5)

    length_val = x + a
    width_val = x + b
    perimeter = 2 * (length_val + width_val)

    question_text = f"一個長方形的長為 $(x + {a})$ 公分，寬為 $(x + {b})$ 公分。若其周長為 ${perimeter}$ 公分，請問 $x$ 的值為何？"
    correct_answer = str(x)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_triangle_angles_problem():
    """
    題型：已知三角形三內角皆為 x 的表達式，利用內角和為 180 度求 x。
    """
    # 預設解答 x
    x = random.randint(25, 45)
    a = random.randint(-15, 15)
    b = random.randint(-15, 15)

    # 確保表達式有意義且各角度為正
    while a == b or a == 0 or b == 0 or (x + a) <= 0 or (x + b) <= 0 or (180 - (x + a) - (x + b)) <= 0:
        x = random.randint(25, 45)
        a = random.randint(-15, 15)
        b = random.randint(-15, 15)

    # 第三個角的表達式: 180 - (x+a) - (x+b) = 180 - a - b - 2x
    c_expr_const = 180 - a - b

    # 格式化各角度的數學表達式
    angle_a_expr = f"x {'+' if a > 0 else '-'} {abs(a)}"
    angle_b_expr = f"x {'+' if b > 0 else '-'} {abs(b)}"
    angle_c_expr = f"{c_expr_const} - 2x"

    # 隨機排列三個角的順序
    angles = [angle_a_expr, angle_b_expr, angle_c_expr]
    random.shuffle(angles)

    question_text = f"已知一個三角形的三個內角分別為 $({angles[0]})^{{\circ}}$、$({angles[1]})^{{\circ}}$ 及 $({angles[2]})^{{\circ}}$，求 $x$ 的值。"
    correct_answer = str(x)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_cutout_area_problem():
    """
    題型：長方形面積減去一個三角形面積，給定剩餘面積，求 x。
    """
    x = random.randint(3, 8)
    c = random.randint(2, 5)  # 長方形的長 = x + c
    h = random.choice([6, 8, 10, 12]) # 長方形的寬
    d = random.choice([2, 4, 6]) # 減去的三角形的高
    
    # 確保三角形的高小於長方形的寬
    while d >= h:
        d = random.choice([2, 4, 6])

    rect_area = (x + c) * h
    tri_area = (1/2) * x * d
    remaining_area = int(rect_area - tri_area)

    question_text = f"一個長方形的長為 $(x + {c})$ 公分，寬為 ${h}$ 公分。若從此長方形中切掉一個底為 $x$ 公分，高為 ${d}$ 公分的三角形，剩下的面積為 ${remaining_area}$ 平方公分，求 $x$ 的值。"
    correct_answer = str(x)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    
    is_correct = (user_answer == correct_answer)
    
    # 數值容錯 (例如 2 vs 2.0)
    if not is_correct:
        try:
            if float(user_answer) == float(correct_answer):
                is_correct = True
        except (ValueError, TypeError):
            pass

    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}
