import random
from fractions import Fraction

def generate(level=1):
    """
    生成「中垂線與角平分線」相關題目 (標準 LaTeX 範本)。
    包含：
    1. 中垂線性質 (周長計算)
    2. 角平分線性質 (距離相等)
    """
    problem_type = random.choice(['perpendicular_bisector_perimeter', 'angle_bisector_distance'])
    
    if problem_type == 'perpendicular_bisector_perimeter':
        return generate_perpendicular_bisector_perimeter_problem()
    elif problem_type == 'angle_bisector_distance':
        return generate_angle_bisector_distance_problem()

def generate_perpendicular_bisector_perimeter_problem():
    """
    生成中垂線性質的題目，類似範例，涉及周長計算。
    題目: 直線 L 為 BC 的中垂線，且交 AB 於 E 點。若△AEC 的周長為 P，AC＝s，則 AB 的長度為多少？
    答案: AB = AE + BE = AE + CE = P - AC
    """
    # 隨機生成數值
    ac_length = random.randint(5, 15) # AC 的長度
    
    # 根據中垂線性質，E點在BC的中垂線上，所以 BE = CE。
    # △AEC 的周長 = AE + CE + AC
    # AB 的長度 = AE + BE
    # 因此，△AEC 的周長 = AE + BE + AC = AB + AC
    # 所以，AB = (△AEC 的周長) - AC
    
    # 為了使題目合理，確保 AB 的長度大於 AC (至少稍大一些)
    ab_length = random.randint(ac_length + 3, ac_length + 15) # AB 的長度
    perimeter_aec = ab_length + ac_length # 計算△AEC 的周長

    # 題目文本
    # 注意 LaTeX 符號和 f-string 的雙大括號 `{{...}}` 和雙反斜線 `\\`
    question_text = (
        f"如右圖，直線 $L$ 為 $\\overline{{BC}}$ 的中垂線，且交 $\\overline{{AB}}$ 於 $E$ 點。<br>"
        f"若 $\\triangle AEC$ 的周長為 ${perimeter_aec}$，$\\overline{{AC}}={ac_length}$，<br>"
        f"則 $\\overline{{AB}}$ 的長度為多少？"
    )
    
    correct_answer = str(ab_length)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_angle_bisector_distance_problem():
    """
    生成角平分線性質的題目，涉及距離相等。
    題目: 在△ABC 中，AD 為∠BAC 的角平分線。若 P 為 AD 上一點，且 P 到 AB 的距離為 d_ab，
    則 P 到 AC 的距離為多少？
    答案: P 到 AC 的距離 = P 到 AB 的距離
    """
    distance = random.randint(3, 12) # 距離
    
    # 隨機選擇四個不重複的字母來命名三角形頂點和角平分線上的點
    all_letters = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    random.shuffle(all_letters)
    
    # 確保使用的字母是唯一的
    angle_vertex = all_letters.pop()
    side1_vertex = all_letters.pop()
    side2_vertex = all_letters.pop()
    bisector_point = all_letters.pop() # 通常用於命名角平分線上的輔助點，如 AD

    # 題目文本
    question_text = (
        f"如右圖，在 $\\triangle {side1_vertex}{angle_vertex}{side2_vertex}$ 中，"
        f"$\\overline{{{angle_vertex}{bisector_point}}}$ 為 $\\angle {side1_vertex}{angle_vertex}{side2_vertex}$ 的角平分線。<br>"
        f"若 $P$ 為 $\\overline{{{angle_vertex}{bisector_point}}}$ 上一點，"
        f"且 $P$ 到 $\\overline{{{angle_vertex}{side1_vertex}}}$ 的距離為 ${distance}$，<br>"
        f"則 $P$ 到 $\\overline{{{angle_vertex}{side2_vertex}}}$ 的距離為多少？"
    )
    
    correct_answer = str(distance)
    
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
    
    if not is_correct:
        try:
            # 嘗試將答案轉換為浮點數進行比較，以處理 '5.0' 和 '5' 的情況
            if float(user_answer) == float(correct_answer):
                is_correct = True
        except ValueError:
            pass # 如果轉換失敗，則非數值比較

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}