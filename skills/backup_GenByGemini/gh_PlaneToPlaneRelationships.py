import random
import math
from fractions import Fraction

def generate(level=1):
    """
    生成「空間中兩平面關係」相關題目。
    包含：
    1. 計算二面角大小 (利用餘弦定理)
    2. 判斷長方體中兩平面的關係 (平行或垂直)
    3. 識別二面角所代表的平面角 (線性角)
    """
    problem_type = random.choice([
        'calculate_dihedral_angle',
        'plane_relationship_cuboid',
        'dihedral_angle_vertex_identification'
    ])

    if problem_type == 'calculate_dihedral_angle':
        return generate_calculate_dihedral_angle(level)
    elif problem_type == 'plane_relationship_cuboid':
        return generate_plane_relationship_cuboid(level)
    else: # 'dihedral_angle_vertex_identification'
        return generate_dihedral_angle_vertex_identification(level)

def generate_calculate_dihedral_angle(level):
    """
    生成計算二面角大小的題目。
    情境：兩平面相交於一直線，提供形成二面角的線性角的三角形三邊長。
    使用餘弦定理計算角度。
    """
    # Try to generate side lengths that result in a valid triangle and a reasonable angle.
    side_x = random.randint(10, 30) # Corresponds to PQ
    
    if level == 1:
        # For Level 1, often make it an isosceles triangle (PQ = PR) to simplify.
        side_y = side_x 
        
        # Target cos_theta between -0.7 and 0.7 (angles approx 45 to 135 degrees)
        target_cos = random.uniform(-0.7, 0.7)
        side_z_squared = 2 * side_x**2 * (1 - target_cos)
        side_z = int(round(math.sqrt(side_z_squared)))
        
        # Ensure side_z forms a valid triangle
        min_z = abs(side_x - side_y) + 1
        max_z = side_x + side_y - 1
        side_z = max(min_z, min(side_z, max_z))
        if side_z < 1: side_z = 1 # Avoid zero or negative lengths after rounding
        
    else: # level > 1, more varied triangles
        side_y = random.randint(15, 40) # Corresponds to PR
        
        # Target cos_theta between -0.95 and 0.95 (angles approx 18 to 162 degrees)
        target_cos = random.uniform(-0.95, 0.95)
        side_z_squared = side_x**2 + side_y**2 - 2 * side_x * side_y * target_cos
        side_z = int(round(math.sqrt(side_z_squared)))
        
        # Ensure side_z forms a valid triangle
        min_z = abs(side_x - side_y) + 1
        max_z = side_x + side_y - 1
        side_z = max(min_z, min(side_z, max_z))
        if side_z < 1: side_z = 1 # Avoid zero or negative lengths after rounding

    # Calculate cos_theta using the actual chosen side lengths
    # Clamp cos_theta to [-1, 1] to prevent floating point errors leading to domain errors in acos
    numerator = side_x**2 + side_y**2 - side_z**2
    denominator = 2 * side_x * side_y
    if denominator == 0: # Avoid division by zero in case of degenerate triangle parameters
        return generate_calculate_dihedral_angle(level) # Regenerate if parameters are problematic

    cos_theta = max(-1.0, min(1.0, numerator / denominator))
    
    theta_rad = math.acos(cos_theta)
    theta_deg = round(math.degrees(theta_rad))

    # Regenerate if angle is too close to 0 or 180 (degenerate triangle)
    if theta_deg <= 1 or theta_deg >= 179:
        return generate_calculate_dihedral_angle(level)

    question_text = (
        r"空間中兩平面相交於一直線 $L$。"
        r"在其中一個平面上有一點 $Q$，使 $Q$ 到直線 $L$ 的垂足為 $P$，"
        r"且線段 $PQ$ 長度為 ${{{side_x}}}$ 單位。"
        r"在另一個平面上有一點 $R$，使 $R$ 到直線 $L$ 的垂足亦為 $P$，"
        r"且線段 $PR$ 長度為 ${{{side_y}}}$ 單位。"
        r"已知線段 $QR$ 長度為 ${{{side_z}}}$ 單位，"
        r"試求此兩平面所形成的二面角的大小。（請將答案四捨五入到最接近的整數度數）"
    )
    correct_answer = str(theta_deg)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_plane_relationship_cuboid(level):
    """
    生成判斷長方體中兩平面關係的題目 (平行或垂直)。
    問題將描述一個標準命名的長方體，並詢問特定兩平面的關係。
    """
    # Standard cuboid naming: A-D counter-clockwise on bottom, E-H corresponding on top
    # A B C D (bottom face)
    # E F G H (top face, E above A, F above B, etc.)
    
    # Define faces by their vertices for clarity (though not strictly used for logic, good for mental model)
    # This also helps identify shared edges for perpendicularity
    faces_map = {
        'ABCD': {'A', 'B', 'C', 'D'}, # Bottom
        'EFGH': {'E', 'F', 'G', 'H'}, # Top
        'ABFE': {'A', 'B', 'F', 'E'}, # Front
        'DCGH': {'D', 'C', 'G', 'H'}, # Back
        'ADHE': {'A', 'D', 'H', 'E'}, # Left
        'BCGF': {'B', 'C', 'G', 'F'}, # Right
    }
    
    problem_choice = random.choice(['parallel', 'perpendicular'])
    
    if problem_choice == 'parallel':
        # Choose two parallel faces
        parallel_pairs = [
            ('ABCD', 'EFGH'),
            ('ABFE', 'DCGH'),
            ('ADHE', 'BCGF'),
        ]
        plane1_name, plane2_name = random.choice(parallel_pairs)
        relationship_text = r"平行"
    else: # perpendicular
        # Choose two faces that share an edge (and are thus perpendicular in a cuboid)
        perpendicular_pairs = [
            ('ABCD', 'ABFE'), ('ABCD', 'BCGF'), ('ABCD', 'DCGH'), ('ABCD', 'ADHE'), # Bottom with side faces
            ('EFGH', 'ABFE'), ('EFGH', 'BCGF'), ('EFGH', 'DCGH'), ('EFGH', 'ADHE'), # Top with side faces
            ('ABFE', 'ADHE'), ('ABFE', 'BCGF'), # Front with Left/Right
            ('DCGH', 'ADHE'), ('DCGH', 'BCGF'), # Back with Left/Right
        ]
        plane1_name, plane2_name = random.choice(perpendicular_pairs)
        relationship_text = r"垂直"
    
    question_text = (
        r"有一個長方體，其八個頂點依序為 $A, B, C, D, E, F, G, H$，其中 $ABCD$ 為底面，"
        r"且 $E, F, G, H$ 分別在 $A, B, C, D$ 的正上方。"
        r"請問平面 ${{{plane1_name}}}$ "
        r"和平面 ${{{plane2_name}}}$ 的關係為何？(請回答：平行 或 垂直)"
    )
    correct_answer = relationship_text

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_dihedral_angle_vertex_identification(level):
    """
    生成識別二面角所代表的平面角 (線性角) 的題目。
    問題將描述構成線性角的幾何條件，要求學生指出該角。
    """
    # Randomize the labels for points slightly
    points_pool = ['P', 'Q', 'R', 'A', 'B', 'C', 'X', 'Y', 'Z', 'M', 'N']
    p1, p2, p_on_line = random.sample(points_pool, 3)

    question_text = (
        f"空間中，平面 $E_1$ 與平面 $E_2$ 相交於一直線 $L$。"
        f"點 ${{{p_on_line}}}$ 是直線 $L$ 上的一點。"
        f"在平面 $E_1$ 上有一點 ${{{p1}}}$，使得直線 ${{{p1}}}{{{p_on_line}}}$ 垂直於直線 $L$。"
        f"在平面 $E_2$ 上有一點 ${{{p2}}}$，使得直線 ${{{p2}}}{{{p_on_line}}}$ 垂直於直線 $L$。"
        f"請問此兩平面所形成的二面角的大小，可以用哪一個角的度數來表示？"
        r"(請填寫角的三個頂點字母，例如：$ABC$)"
    )
    correct_answer = f"{p1}{p_on_line}{p2}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    處理數值、文字 (平行/垂直)、以及角度名稱的答案類型。
    """
    user_answer_strip = user_answer.strip()
    correct_answer_strip = correct_answer.strip()
    
    is_correct = False
    result_text = ""

    # 1. 數值比較 (用於二面角計算的答案)
    try:
        ua_float = float(user_answer_strip)
        ca_float = float(correct_answer_strip)
        # 允許四捨五入到最近整數度的誤差 (小於0.5度)
        if abs(ua_float - ca_float) < 0.5:
            is_correct = True
    except ValueError:
        pass # 不是數值答案，繼續進行字串比較

    # 2. 字串比較 (用於關係判斷或角度名稱)
    if not is_correct:
        ua_upper = user_answer_strip.upper()
        ca_upper = correct_answer_strip.upper()

        # 針對 "平行" / "垂直" 的答案
        if ca_upper == "平行":
            if ua_upper in ["平行", "PARALLEL", "P"]:
                is_correct = True
        elif ca_upper == "垂直":
            if ua_upper in ["垂直", "PERPENDICULAR", "VERTICAL", "V"]:
                is_correct = True
        # 針對角度名稱的答案 (例如：AMB, BMA)
        elif len(ca_upper) == 3: # 假設正確答案是三個字母組成的角名
            # 清理使用者輸入中可能包含的角符號
            ua_clean = ua_upper.replace(r'\ANGLE', '').replace('∠', '')
            if ua_clean == ca_upper or ua_clean == ca_upper[::-1]: # 允許正向或反向的頂點順序
                is_correct = True
        else: # 一般的字串比對
            if ua_upper == ca_upper:
                is_correct = True

    if is_correct:
        result_text = f"完全正確！答案是 ${correct_answer_strip}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer_strip}$"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}