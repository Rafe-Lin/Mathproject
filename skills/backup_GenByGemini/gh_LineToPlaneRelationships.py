import random
import math
from fractions import Fraction

def generate(level=1):
    """
    生成「直線與平面的關係」相關題目。
    包含：
    1. 長方體中直線與平面的垂直關係判斷。
    2. 長方體中對角線長度計算（底面或空間）。
    3. 正四面體中投影點的性質判斷。
    4. 正四面體高的計算。
    """
    problem_type = random.choice([
        'rect_prism_perp_check', 
        'rect_prism_length_face_diag', 
        'rect_prism_length_space_diag',
        'tetra_proj_point_prop',
        'tetra_height_calc'
    ])
    
    if problem_type == 'rect_prism_perp_check':
        return generate_rect_prism_perp_check_problem()
    elif problem_type == 'rect_prism_length_face_diag':
        return generate_rect_prism_length_problem(subtype='face_diag')
    elif problem_type == 'rect_prism_length_space_diag':
        return generate_rect_prism_length_problem(subtype='space_diag')
    elif problem_type == 'tetra_proj_point_prop':
        return generate_tetrahedron_problem(subtype='projection_prop')
    elif problem_type == 'tetra_height_calc':
        return generate_tetrahedron_problem(subtype='height')

def generate_rect_prism_perp_check_problem():
    """
    生成長方體中直線與平面垂直關係的判斷題。
    """
    l = random.randint(3, 10)
    w = random.randint(3, 10)
    h = random.randint(3, 10)

    question_templates = [
        f"一個長方體的長、寬、高分別為 ${l}$, ${w}$, ${h}$。請問邊長為 ${h}$ 的邊是否垂直於底面？(請回答「是」或「否」)",
        f"一個長方體具有邊 $AB$, $BC$, $BF$ (其中 $AB$ 垂直 $BC$, $BF$ 垂直 $AB$ 和 $BC$)。請問直線 $BF$ 是否垂直於平面 $ABC$？(請回答「是」或「否」)",
        "在長方體中，如果一條邊垂直於底面的兩條相鄰邊，它是否垂直於整個底面？(請回答「是」或「否」)",
        "已知直線 $L$ 垂直於平面 $P$ 上的兩條相交直線。請問直線 $L$ 是否垂直於平面 $P$？(請回答「是」或「否」)"
    ]

    question_text = random.choice(question_templates)
    
    correct_answer = "是" 

    return {
        "question_text": question_text,
        "answer": correct_answer, 
        "correct_answer": correct_answer
    }

def generate_rect_prism_length_problem(subtype):
    """
    生成長方體中底面或空間對角線長度計算題。
    """
    l = random.randint(3, 10)
    w = random.randint(3, 10)
    h = random.randint(3, 10)

    if subtype == 'face_diag':
        # 計算底面對角線長度
        diag_sq = l**2 + w**2
        diag = math.sqrt(diag_sq)
        question_text = (
            f"一個長方體的長、寬、高分別為 ${l}$, ${w}$, ${h}$。"
            f"請問其底面的對角線長度為何？(請四捨五入至小數點後兩位，若為整數請直接填寫整數)"
        )
        correct_answer_val = diag
    else: # space_diag
        # 計算空間對角線長度
        diag_sq = l**2 + w**2 + h**2
        diag = math.sqrt(diag_sq)
        question_text = (
            f"一個長方體的長、寬、高分別為 ${l}$, ${w}$, ${h}$。"
            f"請問其空間對角線長度為何？(請四捨五入至小數點後兩位，若為整數請直接填寫整數)"
        )
        correct_answer_val = diag
    
    # 將正確答案四捨五入至小數點後兩位，並轉為字串
    correct_answer_str = str(round(correct_answer_val, 2))

    return {
        "question_text": question_text,
        "answer": correct_answer_str, 
        "correct_answer": correct_answer_str
    }

def generate_tetrahedron_problem(subtype):
    """
    生成正四面體中投影點性質判斷或高的計算題。
    """
    s = random.randint(4, 10) # 正四面體的邊長

    if subtype == 'projection_prop':
        # 關於投影點性質的題目
        question_text = (
            f"一個邊長為 ${s}$ 的正四面體，頂點 $A$ 在底面 $BCD$ 上的投影點為 $H$。"
            f"請問 $H$ 是 $\\triangle BCD$ 的外心、內心、重心，還是以上皆是？(請填寫最精確的描述，例如「外心」或「重心」)"
        )
        correct_answer = "重心" 

    else: # height
        # 計算正四面體的高 AH
        # 1. 底面正三角形的高 BM = s * sqrt(3) / 2
        # 2. 頂點到重心距離 BH = (2/3) * BM = s * sqrt(3) / 3
        # 3. 四面體的高 AH = sqrt(s^2 - BH^2) = s * sqrt(6) / 3
        
        height_val = s * math.sqrt(6) / 3
        
        question_text = (
            f"一個邊長為 ${s}$ 的正四面體，求其高 $AH$ 的長度。"
            f"(請四捨五入至小數點後兩位，若為整數請直接填寫整數)"
        )
        
        # 將正確答案四捨五入至小數點後兩位，並轉為字串
        correct_answer = str(round(height_val, 2))

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    支援數值比較（含浮點數容錯）和字串比較。
    """
    user_answer_processed = user_answer.strip().lower()
    correct_answer_processed = correct_answer.strip().lower()
    
    is_correct = False
    result_feedback = ""

    # 嘗試將答案轉換為浮點數進行數值比較
    try:
        user_num = float(user_answer)
        correct_num = float(correct_answer)
        # 使用一個小容錯值比較浮點數
        if math.isclose(user_num, correct_num, rel_tol=1e-3, abs_tol=1e-3):
            is_correct = True
            result_feedback = f"完全正確！答案是 ${correct_answer}$。"
        else:
            result_feedback = f"答案不正確。正確答案應為：${correct_answer}$"
    except ValueError:
        # 如果不是數值答案（例如：「是」、「重心」）則進行字串比較
        if user_answer_processed == correct_answer_processed:
            is_correct = True
            result_feedback = f"完全正確！答案是 {correct_answer}。"
        else:
            result_feedback = f"答案不正確。正確答案應為：{correct_answer}"
    
    return {"correct": is_correct, "result": result_feedback, "next_question": True}