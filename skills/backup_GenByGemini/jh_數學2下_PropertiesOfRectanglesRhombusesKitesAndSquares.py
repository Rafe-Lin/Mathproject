import random
import math
import re

def format_sqrt(n):
    """
    Simplifies and formats a number n into a string, either as an integer or a simplified square root in LaTeX format.
    e.g., format_sqrt(12) -> "2\\\\sqrt{3}", format_sqrt(16) -> "4"
    """
    if n < 0:
        return "" # Should not happen for this skill
    if n == 0:
        return "0"
    
    i = math.isqrt(n)
    if i * i == n:
        return str(i)
    
    limit = math.isqrt(n)
    for j in range(limit, 1, -1):
        if n % (j * j) == 0:
            coeff = j
            radicand = n // (j * j)
            return f"{coeff}\\\\sqrt{{{radicand}}}"
            
    return f"\\\\sqrt{{{n}}}"

def generate_rectangle_problem():
    """
    Generates a problem about calculating rectangle diagonal lengths.
    """
    triples = [(3, 4, 5), (6, 8, 10), (5, 12, 13), (8, 15, 17), (7, 24, 25)]
    a, b, c = random.choice(triples)
    scale = random.randint(1, 3)
    ab, bc, ac = a * scale, b * scale, c * scale
    
    if random.random() < 0.5:
        question_text = f"一個長方形的長為 ${bc}$，寬為 ${ab}$，求其對角線長度。"
        correct_answer = str(ac)
    else:
        bo = ac / 2
        bo_str = str(int(bo)) if bo.is_integer() else str(bo)
        question_text = f"長方形 ABCD 中，已知 $AB={ab}$，$BC={bc}$，且兩對角線交於 O 點，求線段 BO 的長度。"
        correct_answer = bo_str
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_rhombus_problem():
    """
    Generates a problem about calculating rhombus area or side length from diagonals.
    """
    d1 = random.randint(2, 10) * 2
    d2 = random.randint(2, 10) * 2
    while d1 == d2:
        d2 = random.randint(2, 10) * 2

    if random.random() < 0.6: # Ask for area
        area = (d1 * d2) // 2
        question_text = f"一個菱形的兩條對角線長分別為 ${d1}$ 與 ${d2}$，求此菱形的面積。"
        correct_answer = str(area)
    else: # Ask for side length
        p = d1 // 2
        q = d2 // 2
        side_sq = p**2 + q**2
        side_str = format_sqrt(side_sq)
        question_text = f"一個菱形的兩條對角線長分別為 ${d1}$ 與 ${d2}$，求此菱形的邊長。"
        correct_answer = side_str

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_kite_problem():
    """
    Generates a problem about calculating kite area or a diagonal length.
    """
    if random.random() < 0.5: # Simple area problem
        d1 = random.randint(5, 20)
        d2 = random.randint(5, 20)
        area = (d1 * d2) / 2
        area_str = str(int(area)) if area.is_integer() else str(area)
        question_text = f"一個箏形的兩條對角線長度分別為 ${d1}$ 與 ${d2}$，求此箏形的面積。"
        correct_answer = area_str
    else: # Diagonal calculation problem
        triples = [(3, 4, 5), (6, 8, 10), (5, 12, 13), (8, 15, 17), (7, 24, 25)]
        t1 = random.choice(triples)
        r = min(t1[0], t1[1])
        t2_options = [t for t in triples if r in t[:2] and t != t1]
        if not t2_options: t2_options = [t for t in triples if r in t[:2]]
        t2 = random.choice(t2_options)
        
        p = t1[0] if t1[1] == r else t1[1]
        side1 = t1[2]
        
        q = t2[0] if t2[1] == r else t2[1]
        side2 = t2[2]
        
        question_text = f"箏形 ABCD 中，已知兩雙鄰邊長分別為 AB=AD=${side1}$ 與 BC=CD=${side2}$，且對角線 BD 長為 ${2*r}$。求另一條對角線 AC 的長度。"
        correct_answer = str(p + q)
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_square_problem():
    """
    Generates a problem about calculating square properties or coordinates.
    """
    if random.random() < 0.33: # Coordinate problem
        h = random.randint(-5, 5)
        k = random.randint(-5, 5)
        L = random.randint(1, 5)

        if random.random() < 0.5: # Axis-aligned diagonals
            ax, ay, cx, cy = h - L, k, h + L, k
            bx, by, dx, dy = h, k + L, h, k - L
        else: # 45-degree rotated diagonals
            ax, ay, cx, cy = h - L, k - L, h + L, k + L
            bx, by, dx, dy = h - L, k + L, h + L, k - L
            
        if random.random() < 0.5:
            p1_x, p1_y, p2_x, p2_y = ax, ay, cx, cy
            ans1_x, ans1_y, ans2_x, ans2_y = bx, by, dx, dy
        else:
            p1_x, p1_y, p2_x, p2_y = bx, by, dx, dy
            ans1_x, ans1_y, ans2_x, ans2_y = ax, ay, cx, cy

        question_text = f"若 ABCD 為一正方形，其中兩個對角的頂點座標為 $A({p1_x}, {p1_y})$ 與 $C({p2_x}, {p2_y})$，則另外兩個頂點 B、D 的座標為何？<br>(答案格式：(x1, y1), (x2, y2)，順序可對調)"
        ans_str1 = f"({ans1_x}, {ans1_y}), ({ans2_x}, {ans2_y})"
        ans_str2 = f"({ans2_x}, {ans2_y}), ({ans1_x}, {ans1_y})"
        correct_answer = f"{ans_str1}|{ans_str2}"
        
        return {
            "question_text": question_text,
            "answer": ans_str1,
            "correct_answer": correct_answer
        }

    elif random.random() < 0.5: # Given side
        side = random.randint(2, 12)
        if random.random() < 0.5:
            area = side**2
            question_text = f"一個邊長為 ${side}$ 的正方形，其面積為多少？"
            correct_answer = str(area)
        else:
            diag_str = f"{side}\\\\sqrt{{2}}"
            question_text = f"一個邊長為 ${side}$ 的正方形，其對角線長度為何？"
            correct_answer = diag_str
    else: # Given diagonal
        d = random.randint(2, 10) * 2
        area = (d**2) // 2
        if random.random() < 0.5:
            question_text = f"一個對角線長為 ${d}$ 的正方形，其面積為多少？"
            correct_answer = str(area)
        else:
            side_val = d // 2
            side_str = f"{side_val}\\\\sqrt{{2}}"
            question_text = f"一個對角線長為 ${d}$ 的正方形，其邊長為何？"
            correct_answer = side_str
            
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_identification_problem():
    """
    Generates a conceptual problem about identifying shapes from properties.
    """
    prop_to_shape = {
        "兩對角線相等且互相平分": "長方形",
        "兩對角線互相垂直平分": "菱形",
        "一條對角線垂直平分另一條": "箏形",
        "兩對角線相等且互相垂直平分": "正方形"
    }
    
    prop, shape = random.choice(list(prop_to_shape.items()))

    if random.random() < 0.5: # Fill in the blank
        question_text = f"一個四邊形的兩對角線具有「{prop}」的性質，則這個四邊形必定是什麼形狀？"
        correct_answer = shape
    else: # Yes/No question
        question_text = f"若一個四邊形的對角線滿足「{prop}」，那麼這個四邊形必定是{shape}嗎？（請回答「是」或「否」）"
        correct_answer = "是"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    Generates a question about the properties of special quadrilaterals.
    """
    problem_type = random.choice([
        'rectangle', 
        'rhombus', 
        'kite',
        'square',
        'identification'
    ])
    
    if problem_type == 'rectangle':
        return generate_rectangle_problem()
    elif problem_type == 'rhombus':
        return generate_rhombus_problem()
    elif problem_type == 'kite':
        return generate_kite_problem()
    elif problem_type == 'square':
        return generate_square_problem()
    else: # identification
        return generate_identification_problem()

def check(user_answer, correct_answer):
    """
    Checks if the user's answer is correct for quadrilateral problems.
    """
    user_answer = user_answer.strip()
    correct_answer_str = str(correct_answer)

    if '|' in correct_answer_str:
        options = [opt.strip() for opt in correct_answer_str.split('|')]
        try:
            user_nums = [float(n) for n in re.findall(r'-?\d+\.?\d*', user_answer)]
            if len(user_nums) == 4:
                user_coords = sorted([(user_nums[0], user_nums[1]), (user_nums[2], user_nums[3])])
                
                correct_nums = [float(n) for n in re.findall(r'-?\d+\.?\d*', options[0])]
                correct_coords = sorted([(correct_nums[0], correct_nums[1]), (correct_nums[2], correct_nums[3])])

                if user_coords == correct_coords:
                    is_correct = True
                    result_text = f"完全正確！答案是 ${options[0]}$。"
                    return {"correct": is_correct, "result": result_text, "next_question": True}
        except Exception:
            pass 

        is_correct = False
        result_text = f"答案不正確。正確答案應為：${options[0]}$"
        return {"correct": is_correct, "result": result_text, "next_question": True}

    user_answer_norm = user_answer.replace(" ", "").replace("*", "").lower()
    correct_answer_norm = correct_answer_str.replace(" ", "").replace("*", "").lower()
    user_answer_norm = user_answer_norm.replace("\\sqrt", "\\\\sqrt")
    
    is_correct = (user_answer_norm == correct_answer_norm)

    if not is_correct:
        try:
            if abs(float(user_answer) - float(correct_answer_str)) < 1e-9:
                is_correct = True
        except (ValueError, TypeError):
            pass

    if is_correct:
        result_text = f"完全正確！答案是 ${correct_answer_str}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer_str}$"

    return {"correct": is_correct, "result": result_text, "next_question": True}