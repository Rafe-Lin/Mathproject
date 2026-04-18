import random

def generate(level=1):
    """
    生成「平行線的意義與性質」相關題目。
    Topic Description: 本觀念定義了平行線：在同一平面上，若兩條直線能找到一條共同的垂直線，則此兩直線互相平行。由此定義延伸出平行線的三個重要性質：1. 若一直線垂直於兩平行線中的一條，則必垂直於另一條。2. 兩平行線之間的距離處處相等，永不相交。3. 平行關係具有遞移性，即若 L1 // L2 且 L2 // L3，則 L1 // L3。
    """
    problem_type = random.choice([
        'relationship', 
        'area_comparison', 
        'area_calculation', 
        'application'
    ])
    
    if problem_type == 'relationship':
        return generate_relationship_problem()
    elif problem_type == 'area_comparison':
        return generate_area_comparison_problem()
    elif problem_type == 'area_calculation':
        return generate_area_calculation_problem()
    else: # 'application'
        return generate_application_problem()

def generate_relationship_problem():
    """
    題型：根據垂直與平行關係，判斷兩直線的關係。
    Covers:
    1. Definition: L1 ⊥ M, L2 ⊥ M => L1 // L2
    2. Perpendicular Property: L1 // L2, M ⊥ L1 => M ⊥ L2
    3. Transitive Property: L1 // L2, L2 // L3 => L1 // L3
    """
    problem_subtype = random.choice(['definition', 'perpendicular_property', 'transitivity'])
    
    line_names = random.choice([("L_1", "L_2", "L_3"), ("L", "M", "N")])
    l1, l2, l3 = line_names[0], line_names[1], line_names[2]

    if problem_subtype == 'definition':
        question_text = f"在同一平面上，若直線 ${l1}$ 與直線 ${l2}$ 皆垂直於直線 ${l3}$，則 ${l1}$ 與 ${l2}$ 的關係為何？（請回答 '平行'、'垂直' 或 '相交'）"
        correct_answer = "平行"
    elif problem_subtype == 'perpendicular_property':
        question_text = f"在同一平面上，若直線 ${l1}$ 與直線 ${l2}$ 互相平行，且直線 ${l3}$ 垂直於 ${l1}$，則 ${l3}$ 與 ${l2}$ 的關係為何？（請回答 '平行'、'垂直' 或 '相交'）"
        correct_answer = "垂直"
    else: # transitivity
        question_text = f"在同一平面上，若直線 ${l1}$ 平行於直線 ${l2}$，且直線 ${l2}$ 也平行於直線 ${l3}$，則 ${l1}$ 與 ${l3}$ 的關係為何？（請回答 '平行'、'垂直' 或 '相交'）"
        correct_answer = "平行"
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_area_comparison_problem():
    """
    題型：利用平行線間距離處處相等，比較三角形面積。
    """
    line_names = random.choice([("L", "M"), ("L_1", "L_2")])
    l1, l2 = line_names[0], line_names[1]
    
    points_on_l1 = random.sample(['A', 'B', 'C', 'P', 'Q'], 3)
    points_on_l2 = random.sample(['D', 'E', 'F', 'R', 'S'], 2)
    
    base = "".join(sorted(points_on_l2))
    v1, v2, v3 = points_on_l1[0], points_on_l1[1], points_on_l1[2]
    
    question_text = f"已知平面上兩直線 ${l1} // {l2}$。點 ${v1}$、${v2}$、${v3}$ 在直線 ${l1}$ 上，點 ${points_on_l2[0]}$、${points_on_l2[1]}$ 在直線 ${l2}$ 上。<br>請問 $\\triangle {v1}{base}$、$\\triangle {v2}{base}$、$\\triangle {v3}{base}$ 中，哪一個三角形的面積最大？"
    correct_answer = "一樣大"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_area_calculation_problem():
    """
    題型：利用平行線間距離相等，計算三角形面積。
    """
    h = random.choice([4, 6, 8, 10, 12])
    
    bases = random.sample(range(3, 16), 2)
    base_bd = bases[0]
    base_ae = bases[1]
    
    area_abd = int(0.5 * base_bd * h)
    area_ace = int(0.5 * base_ae * h)
    
    question_text = f"在平面上，已知 $\\overline{{AE}} // \\overline{{BD}}$，且點 $C$ 在直線 $BD$ 上。若 $\\overline{{AE}} = {base_ae}$，$\\overline{{BD}} = {base_bd}$，且 $\\triangle ABD$ 的面積為 ${area_abd}$，則 $\\triangle ACE$ 的面積為多少？"
    correct_answer = str(area_ace)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }
    
def generate_application_problem():
    """
    題型：平行線定義在生活實例中的應用。
    """
    subtype = random.choice(['rectangle', 'ladder'])
    
    if subtype == 'rectangle':
        question_text = "一個長方形的四個內角都是直角 ($90^\\circ$)，請問這個長方形的對邊 (例如上邊和下邊) 會互相平行嗎？ (請回答 '會' 或 '不會')"
        correct_answer = "會"
    else: # ladder
        question_text = "一個梯子的每個橫桿都垂直於其中一邊的立柱，請問這些橫桿彼此之間是否互相平行？ (請回答 '是' 或 '否')"
        correct_answer = "是"
        
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
    canonical_answer = correct_answer.strip()
    
    synonyms = {
        "會": ["是"],
        "是": ["會"],
        "一樣大": ["相等"],
        "相等": ["一樣大"]
    }
    
    is_correct = (user_answer == canonical_answer)
    
    if not is_correct and canonical_answer in synonyms:
        if user_answer in synonyms[canonical_answer]:
            is_correct = True
            
    if not is_correct:
        try:
            if float(user_answer) == float(canonical_answer):
                is_correct = True
        except (ValueError, TypeError):
            pass

    if is_correct:
        result_text = f"完全正確！答案是 ${canonical_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${canonical_answer}$"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}