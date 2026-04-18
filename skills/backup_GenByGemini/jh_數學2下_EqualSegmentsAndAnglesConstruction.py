import random
import uuid

def generate(level=1):
    """
    生成「等線段與等角作圖」相關題目。
    包含：
    1. 尺規作圖的觀念性運算 (線段和/差、角和/差)
    2. 等角作圖的步驟選擇題
    """
    # 隨機選擇題型
    problem_type = random.choice(['arithmetic_construction', 'angle_construction_mcq'])
    
    if problem_type == 'arithmetic_construction':
        return generate_arithmetic_construction_problem()
    else: # 'angle_construction_mcq'
        return generate_angle_construction_mcq_problem()

def generate_arithmetic_construction_problem():
    """
    生成關於線段或角作圖後的長度/角度計算問題。
    這類題目測試學生是否理解作圖與算術運算的關聯。
    """
    if random.choice(['segment', 'angle']) == 'segment':
        # 線段和/差
        a = random.randint(5, 20)
        b = random.randint(2, a - 1)
        operation = random.choice(['+', '-'])
        
        if operation == '+':
            question_text = f"已知兩線段長分別為 $a={a}$、$b={b}$。若利用尺規作圖作出一線段長為 $a+b$，請問其長度為何？"
            correct_answer = str(a + b)
        else: # operation == '-'
            question_text = f"已知兩線段長分別為 $a={a}$、$b={b}$。若利用尺規作圖作出一線段長為 $a-b$，請問其長度為何？"
            correct_answer = str(a - b)
    else:
        # 角和/差
        angle1 = random.randint(50, 130)
        angle2 = random.randint(20, angle1 - 20)
        operation = random.choice(['+', '-'])

        # 避免角度和超過180度，簡化問題
        if operation == '+' and angle1 + angle2 > 180:
            operation = '-'

        if operation == '+':
            question_text = f"已知 $\\angle 1 = {angle1}^\\circ$、$\\angle 2 = {angle2}^\\circ$。若利用尺規作圖作出一角等於 $\\angle 1 + \\angle 2$，請問其角度為何？(只需回答數字)"
            correct_answer = str(angle1 + angle2)
        else: # operation == '-'
            question_text = f"已知 $\\angle 1 = {angle1}^\\circ$、$\\angle 2 = {angle2}^\\circ$。若利用尺規作圖作出一角等於 $\\angle 1 - \\angle 2$，請問其角度為何？(只需回答數字)"
            correct_answer = str(angle1 - angle2)
            
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_angle_construction_mcq_problem():
    """
    生成等角作圖的步驟選擇題。
    這類題目測試學生對作圖原理（SSS 全等）的理解。
    """
    # 隨機選擇點的標籤，避免每次題目都一樣
    points_pool1 = ['A', 'B', 'C', 'D', 'E']
    points_pool2 = ['O', 'P', 'Q', 'R', 'S', 'T']
    
    # 從點池中隨機抽取不重複的點
    vA, pB, pC = random.sample(points_pool1, 3)
    vO, pP, pQ = random.sample(points_pool2, 3)

    # 建立題目描述
    question_stem = (
        f"有一 $\\angle {pB}{vA}{pC}$ 及一直線 L，L 上有一點 ${vO}$。小華想以 ${vO}$ 為頂點、L 為角的一邊，作一角與 $\\angle {pB}{vA}{pC}$ 相等。"
        "<br>已經進行的步驟如下：<br>"
        f"⑴ 以 ${vA}$ 為圓心，適當長為半徑畫弧，分別交 $\\angle {pB}{vA}{pC}$ 的兩邊於 ${pB}$、${pC}$ 兩點。<br>"
        f"⑵ 以 ${vO}$ 為圓心，$\\overline{{{vA}{pB}}}$ 為半徑畫弧，交 L 於 ${pP}$ 點。<br>"
        f"請問小華繼續下列哪一個步驟後，連接 $\\overline{{{vO}{pQ}}}$，$\\angle {pQ}{vO}{pP}$ 即為所求？"
    )
    
    # 建立選項
    # 正確答案：以新線段的端點P為圓心，取原角兩邊交點的弦長BC為半徑畫弧
    correct_option = f"以 ${pP}$ 為圓心，$\\overline{{{pB}{pC}}}$ 為半徑畫弧，與前弧相交於 ${pQ}$ 點"
    
    # 干擾選項
    # 1. 圓心錯誤
    distractor1 = f"以 ${vO}$ 為圓心，$\\overline{{{pB}{pC}}}$ 為半徑畫弧，與前弧相交於 ${pQ}$ 點"
    # 2. 半徑錯誤 (使用與步驟⑵相同的半徑)
    distractor2 = f"以 ${pP}$ 為圓心，$\\overline{{{vA}{pC}}}$ 為半徑畫弧，與前弧相交於 ${pQ}$ 點"
    # 3. 圓心與半徑混亂
    distractor3 = f"以 ${pB}$ 為圓心，$\\overline{{{vO}{pP}}}$ 為半徑畫弧，與前弧相交於 ${pQ}$ 點"

    options = [correct_option, distractor1, distractor2, distractor3]
    random.shuffle(options)
    
    correct_answer_char = chr(ord('A') + options.index(correct_option))
    
    options_text = ""
    for i, option in enumerate(options):
        options_text += f"({chr(ord('A') + i)}) {option}<br>"
        
    question_text = question_stem + "<br>" + options_text
    
    return {
        "question_text": question_text,
        "answer": correct_answer_char,
        "correct_answer": correct_answer_char
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    # 統一將使用者答案和正確答案轉為大寫並去除前後空白，以進行比較
    user_answer = user_answer.strip().upper()
    correct_answer = correct_answer.strip().upper()
    
    is_correct = (user_answer == correct_answer)
    
    # 對於數值題，嘗試比較浮點數值
    if not is_correct:
        try:
            if float(user_answer) == float(correct_answer):
                is_correct = True
        except (ValueError, TypeError):
            pass

    if is_correct:
        result_text = f"完全正確！答案是 {correct_answer}。"
    else:
        result_text = f"答案不正確。正確答案應為：{correct_answer}。"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}