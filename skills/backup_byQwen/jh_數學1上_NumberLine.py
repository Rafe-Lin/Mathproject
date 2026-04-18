import random
from fractions import Fraction

# ==============================================================================
# 工具函式：這部分負責畫出漂亮的 ASCII 圖
# ==============================================================================
def draw_number_line(points_map):
    """
    產生包含 HTML <pre> 標籤的對齊數線。
    points_map: 例如 {'A': -2, 'B': 3}
    """
    # 1. 找出範圍
    values = [int(v) if isinstance(v, (int, float)) else int(v.numerator/v.denominator) for v in points_map.values()]
    if not values: values = [0]
    
    r_min = min(min(values) - 1, -5)
    r_max = max(max(values) + 1, 5)

    # 限制長度
    if r_max - r_min > 10:
        center = int(sum(values) / len(values))
        r_min, r_max = center - 5, center + 5
    
    # 2. 繪製圖層 (每單位寬度 5 格)
    u_w = 5
    l_nums = ""   # 數字層
    l_axis = ""   # 軸線層
    l_labels = "" # 標籤層
    
    for i in range(r_min, r_max + 1):
        # 數字置中
        l_nums += f"{str(i):^{u_w}}"
        # 刻度
        if i == r_max:
            l_axis += "+" + " " * (u_w - 1)
        else:
            l_axis += "+" + "-" * (u_w - 1)
        # 標籤
        curr_labels = [k for k, v in points_map.items() if (v == i if isinstance(v, int) else int(v) == i)]
        lbl_str = curr_labels[0] if curr_labels else ""
        l_labels += f"{lbl_str:^{u_w}}"

    # 3. 組合 (使用 <pre> 強制對齊)
    # 注意：這裡使用 <br> 換行，避免 \n 在某些前端被吃掉
    content = f"{l_nums}\n{l_axis}\n{l_labels}"
    return f"<pre style='font-family: monospace; line-height: 1.2; white-space: pre;'>{content}</pre>"

# ==============================================================================
# 核心邏輯：依照 Example_Program.py 架構
# ==============================================================================
def generate(level=1):
    # 隨機選擇一種題型
    problem_type = random.choice(['read_graph', 'draw_graph'])
    
    if problem_type == 'read_graph':
        return generate_read_problem()
    else:
        return generate_draw_problem()

def generate_read_problem():
    # 題型：讀圖 (圖在題目 Question 中)
    val = random.randint(-5, 5)
    ascii_art = draw_number_line({'P': val})
    
    question_text = f"觀察下列數線，請問 $P$ 點的座標為何？\n{ascii_art}"
    correct_answer = str(val)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_draw_problem():
    # 題型：作圖 (圖在詳解 Answer 中)
    val = random.randint(-5, 5)
    ascii_art = draw_number_line({'Q': val})
    
    question_text = f"請畫出一條數線，並在數線上標出 $Q({val})$ 的位置。"
    answer_text = f"參考解法：\n{ascii_art}"
    correct_answer = str(val)
    
    return {
        "question_text": question_text,
        "answer": answer_text,
        "correct_answer": correct_answer
    }

def check(user_ans, correct_ans):
    return {
        "correct": user_ans.strip() == correct_ans.strip(),
        "result": f"答案是 ${correct_ans}$",
        "next_question": True
    }