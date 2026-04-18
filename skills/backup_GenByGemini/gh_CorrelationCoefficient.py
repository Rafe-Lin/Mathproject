import random
import math
from fractions import Fraction

def generate(level=1):
    """
    生成「相關係數」相關題目。
    要求學生計算給定數據的相關係數。
    """
    # 決定數據點數量
    n_points = random.randint(5, 7) if level == 1 else random.randint(6, 9)

    # 數據範圍
    x_range_min, x_range_max = -15, 15
    y_range_min, y_range_max = -15, 15

    # 生成 x 值：確保唯一且有一定分佈
    # random.sample 保證了 x_values 是唯一的，因此 sum_x_sq_dev 不會為零 (只要 n_points > 1)
    x_values = sorted(random.sample(range(x_range_min, x_range_max + 1), n_points))

    # 生成 y 值，控制相關性強度
    correlation_type = random.choice(['strong_pos', 'strong_neg', 'weak'])
    y_values_raw = []

    if correlation_type == 'strong_pos':
        m = random.choice([1, 2])
        c = random.randint(-5, 5)
        noise_magnitude = random.randint(1, 3) # 較小的雜訊
        for x_val in x_values:
            y_base = m * x_val + c
            y_values_raw.append(y_base + random.randint(-noise_magnitude, noise_magnitude))
    elif correlation_type == 'strong_neg':
        m = random.choice([-1, -2])
        c = random.randint(-5, 5)
        noise_magnitude = random.randint(1, 3) # 較小的雜訊
        for x_val in x_values:
            y_base = m * x_val + c
            y_values_raw.append(y_base + random.randint(-noise_magnitude, noise_magnitude))
    else: # 弱相關或無相關
        # 生成相對獨立的 y 值，或加入較大雜訊
        y_values_raw = [random.randint(y_range_min, y_range_max) for _ in range(n_points)]
        random.shuffle(y_values_raw) # 隨機打亂以減少意外的相關性

    # 確保 y 值至少有兩個不同，避免 sum_y_sq_dev 為零
    # 如果初次生成不滿足條件，則重新生成
    if len(set(y_values_raw)) < 2:
        y_values_raw = [random.randint(y_range_min, y_range_max) for _ in range(n_points)]
        while len(set(y_values_raw)) < 2:
            y_values_raw = [random.randint(y_range_min, y_range_max) for _ in range(n_points)]

    y_values = y_values_raw # Use the validated y_values

    # 計算平均數
    mu_x = sum(x_values) / n_points
    mu_y = sum(y_values) / n_points

    # 計算相關係數公式所需之和
    sum_xy_dev = 0  # Sum of (x_i - mu_x)(y_i - mu_y)
    sum_x_sq_dev = 0  # Sum of (x_i - mu_x)^2
    sum_y_sq_dev = 0  # Sum of (y_i - mu_y)^2

    for i in range(n_points):
        x_dev = x_values[i] - mu_x
        y_dev = y_values[i] - mu_y
        sum_xy_dev += x_dev * y_dev
        sum_x_sq_dev += x_dev * x_dev
        sum_y_sq_dev += y_dev * y_dev

    # 計算相關係數
    denominator = math.sqrt(sum_x_sq_dev) * math.sqrt(sum_y_sq_dev)

    if denominator == 0:
        # 理論上，由於 x_values 和 y_values 的生成方式，這裡不應出現 denominator == 0。
        # 如果發生，表示數據沒有變異，相關係數無意義。
        # 應重新生成題目，這裡暫時給一個預設值（或觸發錯誤讓外部重試）。
        # 為了魯棒性，可以將整個生成邏輯包裝在一個循環中，直到生成有效數據。
        # 在此處，我們假設上述數據生成策略已有效避免此情況。
        correct_r = 0.0 # Fallback
    else:
        correct_r = sum_xy_dev / denominator

    # 將結果四捨五入到小數點後第三位
    correct_r_str = f"{correct_r:.3f}"
    correct_r_float = round(correct_r, 3)

    # 格式化數據為 LaTeX 表格
    x_row_str = " & ".join(map(str, x_values))
    y_row_str = " & ".join(map(str, y_values))

    # 動態生成 LaTeX array 的列格式字符串
    # 1 個 `c` 給標籤 (x/y)，n_points 個 `c` 給數據
    column_format = r"|c|" + r"c|" * n_points
    
    table_latex = r"""
\begin{array}{""" + column_format + r"""}
\hline
\text{x} & """ + x_row_str + r""" \\
\hline
\text{y} & """ + y_row_str + r""" \\
\hline
\end{array}
"""

    question_text = f"兩變量 $x$ 與 $y$ 的數據如下表。\n\n{table_latex}\n\n求 $x$ 與 $y$ 的相關係數。(請四捨五入到小數點後第三位)"

    return {
        "question_text": question_text,
        "answer": str(correct_r_float),
        "correct_answer": str(correct_r_float)
    }

def check(user_answer, correct_answer):
    """
    檢查用戶答案是否正確。
    允許浮點數比較時有微小誤差，並要求四捨五入到小數點後第三位。
    """
    try:
        user_val = float(user_answer)
        correct_val = float(correct_answer)

        # 將用戶答案四捨五入到小數點後第三位，再進行比較
        user_val_rounded = round(user_val, 3)

        # 浮點數比較，使用一個極小的容許誤差
        is_correct = abs(user_val_rounded - correct_val) < 1e-9 

        if is_correct:
            result_text = f"完全正確！答案是 ${correct_answer}$。"
        else:
            result_text = f"答案不正確。您的答案是 ${user_answer}$，正確答案應為：${correct_answer}$。(請注意四捨五入到小數點後第三位)"
        return {"correct": is_correct, "result": result_text, "next_question": True}
    except ValueError:
        return {"correct": False, "result": "請輸入一個有效的數字。", "next_question": False}