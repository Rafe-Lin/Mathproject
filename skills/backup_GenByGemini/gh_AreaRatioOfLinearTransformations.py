import random
from fractions import Fraction

def generate(level=1):
    """
    生成「線性變換的面積比」相關題目。
    探討經過二階方陣線性變換後，圖形面積與原圖形面積的關係，
    其比值等於該方陣行列式的絕對值。
    """
    # For level 1, we will focus on triangle area transformation.
    # Future levels could include parallelogram transformation,
    # more complex polygons, or fractional coordinates.
    
    return generate_triangle_area_transformation_problem()

def generate_triangle_area_transformation_problem():
    """
    生成一個關於二階方陣將三角形變換後面積的題目。
    """
    
    # 1. 隨機生成一個2x2方陣 A
    # 確保行列式不為零，以避免圖形退化成一條線或一點（面積為0）
    while True:
        a = random.randint(-5, 5)
        b = random.randint(-5, 5)
        c = random.randint(-5, 5)
        d = random.randint(-5, 5)
        det_A = a * d - b * c
        if det_A != 0:
            break
            
    # 2. 隨機生成三角形 PQR 的三個頂點坐標
    # 確保三角形不是退化的（即三點不共線，面積不為零）
    while True:
        px, py = random.randint(-4, 4), random.randint(-4, 4)
        qx, qy = random.randint(px - 4, px + 4), random.randint(py - 4, py + 4)
        rx, ry = random.randint(px - 4, px + 4), random.randint(py - 4, py + 4)

        # 計算向量 PQ 和 PR
        vec_PQ_x = qx - px
        vec_PQ_y = qy - py
        vec_PR_x = rx - px
        vec_PR_y = ry - py

        # 計算原三角形 PQR 的面積
        # 面積 = 1/2 * |det(PQ, PR)|
        # det(PQ, PR) = (vec_PQ_x * vec_PR_y) - (vec_PQ_y * vec_PR_x)
        original_area_num = abs(vec_PQ_x * vec_PR_y - vec_PQ_y * vec_PR_x)
        
        if original_area_num != 0: # 確保三角形面積不為零
            original_area = Fraction(original_area_num, 2)
            break

    # 3. 計算變換後三角形 P'Q'R' 的面積
    # 變換後面積 = |det(A)| * 原面積
    abs_det_A = abs(det_A)
    transformed_area = original_area * abs_det_A
    
    # 準備 LaTeX 格式的方陣字串
    # 注意：在 f-string 中嵌入 LaTeX 的大括號需要雙重 `{{` 和 `}}`
    # 這裡 `matrix_str` 已經是一個原始字串 (r"...")，其中包含 LaTeX 格式
    matrix_str = r"\begin{{pmatrix}} {a} & {b} \\ {c} & {d} \end{{pmatrix}}".format(a=a, b=b, c=c, d=d)

    question_text = (
        f"已知二階方陣 $A = {matrix_str}$ 將 $\\triangle PQR$ 變換成 $\\triangle P'Q'R'$，"
        f"且 $\\triangle PQR$ 三頂點坐標為 $P({px}, {py})$, $Q({qx}, {qy})$, $R({rx}, {ry})$，"
        f"求 $\\triangle P'Q'R'$ 的面積。"
    )
    
    # 將答案轉換為字串， Fractions 會自動處理分數格式
    correct_answer_str = str(transformed_area)

    return {
        "question_text": question_text,
        "answer": correct_answer_str,
        "correct_answer": correct_answer_str
    }

def check(user_answer, correct_answer):
    """
    檢查使用者答案是否正確。
    接受使用者輸入的字串和正確答案字串，進行分數比較。
    """
    try:
        # 嘗試將使用者答案和正確答案轉換為 Fraction 對象進行精確比較
        user_fraction = Fraction(user_answer.strip())
        correct_fraction = Fraction(correct_answer.strip())
        is_correct = (user_fraction == correct_fraction)
    except ValueError:
        # 如果使用者輸入不是有效數字或分數，則認為不正確
        is_correct = False

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}