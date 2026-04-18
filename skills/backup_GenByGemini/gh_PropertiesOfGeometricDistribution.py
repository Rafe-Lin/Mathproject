import random
import math
from fractions import Fraction

# Helper function for combinations, as math.comb is Python 3.8+
def combinations(n, k):
    if k < 0 or k > n:
        return 0
    if k == 0 or k == n:
        return 1
    if k > n // 2:
        k = n - k

    res = 1
    for i in range(k):
        res = res * (n - i) // (i + 1)
    return res

def _calculate_geometric_props(p):
    """Calculates E(X) and Std Dev for a given probability p."""
    # E(X) = 1/p
    e_x = Fraction(1, p)

    # Var(X) = (1-p)/p^2
    var_x = Fraction(1 - p, p**2)

    # Std Dev(X) = sqrt(Var(X))
    std_dev = math.sqrt(float(var_x))

    return e_x, std_dev

def generate_urn_problem(level):
    """Generates an urn problem to find p, then E(X) and Std Dev."""
    while True:
        # More balls for higher levels, ensuring enough for meaningful draws
        total_balls = random.randint(4 + min(level, 3), 10 + min(level, 3))
        red_balls = random.randint(1, total_balls - 2) # At least 1 white, 1 red initially
        white_balls = total_balls - red_balls

        # Ensure there are enough white balls to draw
        min_draw = 2 # Minimum balls to draw for a combination problem
        max_draw = min(white_balls, total_balls - 1) # Max balls to draw is white_balls, and also less than total_balls to avoid p=1
        
        if max_draw < min_draw: # Not enough white balls or total balls to make a meaningful draw
            continue
        
        balls_drawn = random.randint(min_draw, max_draw)
        
        # Calculate success probability p (drawing all white balls)
        num_success_comb = combinations(white_balls, balls_drawn)
        num_total_comb = combinations(total_balls, balls_drawn)

        if num_total_comb == 0: # Should not happen if total_balls >= balls_drawn
            continue

        p = Fraction(num_success_comb, num_total_comb)

        # Ensure 0 < p < 1
        if p <= 0 or p >= 1:
            continue
        break
    
    e_x, std_dev = _calculate_geometric_props(p)

    question_text = (
        f"袋中有大小相同的紅球 ${red_balls}$ 顆、白球 ${white_balls}$ 顆。"
        f"每次從袋中同時取出 ${balls_drawn}$ 球，觀察顏色後再放回袋中，直到取到 ${balls_drawn}$ 球皆為白球為止。"
        f"已知每一次取球都為獨立事件，且每球被取到的機會均等，"
        f"並令隨機變數 $X$ 為第一次取到 ${balls_drawn}$ 球皆為白球所需的次數，"
        f"求 $X$ 的期望值與標準差。（標準差請四捨五入至小數點後三位）"
    )
    return question_text, p, e_x, std_dev

def generate_simple_event_problem(level):
    """Generates a problem based on simple events like dice or coin rolls."""
    event_type = random.choice(['dice', 'coin', 'spinner'])
    
    if event_type == 'dice':
        sides = 6
        target_face = random.randint(1, sides)
        p = Fraction(1, sides)
        question_text = (
            f"重複擲一粒公正骰子，觀察所出現的點數，直到出現 ${target_face}$ 點為止。"
            f"令隨機變數 $X$ 為擲骰子總次數，求 $X$ 的期望值與標準差。"
            f"（標準差請四捨五入至小數點後三位）"
        )
    elif event_type == 'coin':
        sides = 2
        target_face = random.choice(['正面', '反面'])
        p = Fraction(1, sides)
        question_text = (
            f"重複擲一枚公正硬幣，觀察所出現的結果，直到出現「{target_face}」為止。"
            f"令隨機變數 $X$ 為擲硬幣總次數，求 $X$ 的期望值與標準差。"
            f"（標準差請四捨五入至小數點後三位）"
        )
    else: # spinner
        sides = random.randint(3 + min(level, 2), 8 + min(level, 2)) # More sectors for higher levels
        target_sector = random.randint(1, sides)
        p = Fraction(1, sides)
        question_text = (
            f"有一個公正的轉盤，被分成 ${sides}$ 個大小相同的扇形區域，分別標示 ${1}$ 到 ${sides}$。"
            f"重複轉動轉盤，觀察所指到的區域，直到指到區域 ${target_sector}$ 為止。"
            f"令隨機變數 $X$ 為轉動轉盤的總次數，求 $X$ 的期望值與標準差。"
            f"（標準差請四捨五入至小數點後三位）"
        )
    
    e_x, std_dev = _calculate_geometric_props(p)
    return question_text, p, e_x, std_dev

def generate_sequence_problem(level):
    """Generates a problem based on pressing buttons in a sequence."""
    num_options = random.randint(2, 3) # e.g., A/B or A/B/C
    seq_length = random.randint(3 + level // 2, 6 + level // 2) # Longer sequences for higher levels

    # Generate a random sequence
    options = [chr(ord('A') + i) for i in range(num_options)]
    target_sequence = "".join(random.choice(options) for _ in range(seq_length))
    
    p = Fraction(1, num_options**seq_length)

    e_x, std_dev = _calculate_geometric_props(p)

    question_text = (
        f"有一台機器面板上有 {', '.join(f'${opt}$' for opt in options)} 共 ${num_options}$ 個按鍵。"
        f"每一回合需按下按鍵 ${seq_length}$ 次，若這 ${seq_length}$ 次是依照「{target_sequence}」的順序按下，則會獲得獎勵。"
        f"有一隻猴子每次隨機地按下其中一個按鍵，"
        f"令隨機變數 $X$ 表示第一次獲得獎勵所需要的回合數，"
        f"求 $X$ 的期望值與標準差。（標準差請四捨五入至小數點後三位）"
    )
    return question_text, p, e_x, std_dev

def generate(level=1):
    """
    生成「幾何分布的統計性質」相關題目。
    包含：
    1. 期望值 E(X) = 1/p
    2. 變異數 Var(X) = (1-p)/p^2
    3. 標準差 σ(X) = sqrt((1-p)/p^2)
    """
    
    problem_type_choices = ['urn', 'simple_event', 'sequence']
    
    # Adjust problem type likelihood based on level
    # Level 1: simpler p (urn, simple_event)
    # Level 2: introduces sequence problems
    # Level 3+: any problem type
    if level == 1:
        problem_type = random.choice(['simple_event', 'urn'])
    elif level == 2:
        problem_type = random.choice(['simple_event', 'urn', 'sequence'])
    else: # level 3+
        problem_type = random.choice(problem_type_choices)

    if problem_type == 'urn':
        question_text, p_val, e_x_val, std_dev_val = generate_urn_problem(level)
    elif problem_type == 'simple_event':
        question_text, p_val, e_x_val, std_dev_val = generate_simple_event_problem(level)
    else: # sequence
        question_text, p_val, e_x_val, std_dev_val = generate_sequence_problem(level)

    # Format answers
    e_x_str = str(e_x_val)
    std_dev_str = f"{std_dev_val:.3f}" # Round to 3 decimal places

    # The problem statement requires both E(X) and StdDev
    # The 'answer' and 'correct_answer' should contain both.
    # Format: "E(X) value, StdDev value"
    correct_answer = f"{e_x_str}, {std_dev_str}"

    return {
        "question_text": question_text,
        "answer": correct_answer, # Store the combined string
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    user_answer 和 correct_answer 預期格式為 "E(X)_value, StdDev_value"。
    """
    user_answer_parts = [part.strip() for part in user_answer.split(',')]
    correct_answer_parts = [part.strip() for part in correct_answer.split(',')]

    if len(user_answer_parts) != 2 or len(correct_answer_parts) != 2:
        return {"correct": False, "result": "答案格式不正確。請以「期望值, 標準差」的格式回答。", "next_question": False}

    is_correct = True
    feedback = []

    # Check E(X)
    try:
        user_e_x = Fraction(user_answer_parts[0])
        correct_e_x = Fraction(correct_answer_parts[0])
        if user_e_x == correct_e_x:
            feedback.append(f"期望值 $E(X) = {correct_e_x}$ 正確。")
        else:
            is_correct = False
            feedback.append(f"期望值 $E(X)$ 不正確。你的答案是 ${user_e_x}$，正確答案是 ${correct_e_x}$。")
    except ValueError:
        is_correct = False
        feedback.append(f"期望值格式錯誤：${user_answer_parts[0]}$。")
    except ZeroDivisionError: # Happens if user_answer_parts[0] is "0" trying to create Fraction(1,0)
        is_correct = False
        feedback.append(f"期望值格式錯誤：${user_answer_parts[0]}$。")


    # Check Std Dev
    try:
        user_std_dev = float(user_answer_parts[1])
        correct_std_dev = float(correct_answer_parts[1])
        # Use a small tolerance for float comparison, matching 3 decimal places
        tolerance = 1e-3 
        if abs(user_std_dev - correct_std_dev) < tolerance:
            feedback.append(f"標準差 $\\sigma(X) \\approx {correct_std_dev:.3f}$ 正確。")
        else:
            is_correct = False
            feedback.append(f"標準差 $\\sigma(X)$ 不正確。你的答案是 ${user_std_dev:.3f}$，正確答案是 ${correct_std_dev:.3f}$。")
    except ValueError:
        is_correct = False
        feedback.append(f"標準差格式錯誤：${user_answer_parts[1]}$。")

    result_text = "<br>".join(feedback)
    if is_correct:
        result_text = f"完全正確！<br>{result_text}"
    else:
        result_text = f"答案不完全正確。<br>{result_text}"

    return {"correct": is_correct, "result": result_text, "next_question": True}