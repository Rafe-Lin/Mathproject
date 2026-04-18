# ==============================================================================
# ID: jh_數學1上_DistanceBetweenTwoPointsOnNumberLine
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 26.10s | RAG: 5 examples
# Created At: 2026-01-14 09:33:32
# Fix Status: [Repaired]
# Fixes: Regex=6, Logic=0
#==============================================================================


import random
import math
import matplotlib
# [Fix] Font injection for Traditional Chinese support
matplotlib.rcParams["font.sans-serif"] = ["Microsoft JhengHei"] 
matplotlib.rcParams['axes.unicode_minus'] = False
from fractions import Fraction
from functools import reduce

# --- 1. Formatting Helpers ---
def to_latex(num):
    """
    Convert int/float/Fraction to LaTeX.
    Handles mixed numbers automatically for Fractions.
    """
    if isinstance(num, int): return str(num)
    if isinstance(num, float): num = Fraction(str(num)).limit_denominator(100)
    if isinstance(num, Fraction):
        if num.denominator == 1: return str(num.numerator)
        # Logic for negative fractions
        sign = "-" if num < 0 else ""
        abs_num = abs(num)
        
        if abs_num.numerator > abs_num.denominator:
            whole = abs_num.numerator // abs_num.denominator
            rem_num = abs_num.numerator % abs_num.denominator
            if rem_num == 0: return f"{sign}{whole}"
            return f"{sign}{whole} \\frac{{rem_num}}{{abs_num.denominator}}"
        return f"\\frac{{{num.numerator}}}{{{num.denominator}}}"
    return str(num)

def fmt_num(num, signed=False, op=False):
    """
    Format number for LaTeX.
    
    Args:
        num: The number to format.
        signed (bool): If True, always show sign (e.g., "+3", "-5").
        op (bool): If True, format as operation with spaces (e.g., " + 3", " - 5").
    """
    latex_val = to_latex(num)
    if num == 0 and not signed and not op: return "0"
    
    is_neg = (num < 0)
    abs_val = to_latex(abs(num))
    
    if op:
        # e.g., " + 3", " - 3"
        return f" - {abs_val}" if is_neg else f" + {abs_val}"
    
    if signed:
        # e.g., "+3", "-3"
        return f"-{abs_val}" if is_neg else f"+{abs_val}"
        
    # Default behavior (parentheses for negative)
    if is_neg: return f"({latex_val})"
    return latex_val

# Alias for AI habits
fmt_fraction_latex = to_latex 

# --- 2. Number Theory Helpers ---
def get_positive_factors(n):
    """Return a sorted list of positive factors of n."""
    factors = set()
    for i in range(1, int(math.isqrt(n)) + 1):
        if n % i == 0:
            factors.add(i)
            factors.add(n // i)
    return sorted(list(factors))

def is_prime(n):
    """Check primality."""
    if n <= 1: return {"correct": False, "result": r"""答案錯誤。正確答案為：{ans}""".replace("{ans}", str(correct_answer))}
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return {"correct": False, "result": r"""答案錯誤。正確答案為：{ans}""".replace("{ans}", str(correct_answer))}
    final_label_str = ""
    for labels in label_slots:
        final_label_str += f"{labels[0]:<{unit_width}}" if labels else " " * unit_width
    result = (
        f"<div style='font-family: Consolas, monospace; white-space: pre; overflow-x: auto; background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; line-height: 1.2;'>"
        f"{final_label_str}\n{line_str}+\n{tick_str}</div>"
    )

# --- 4. High-Level Math Objects (Vector/Matrix/Calculus) ---
class Vector3:
    """Simple 3D Vector Class for Geometry."""
    def __init__(self, x, y, z=0): self.x, self.y, self.z = x, y, z
    def __add__(self, o): return Vector3(self.x+o.x, self.y+o.y, self.z+o.z)
    def __sub__(self, o): return Vector3(self.x-o.x, self.y-o.y, self.z-o.z)
    def dot(self, o): return self.x*o.x + self.y*o.y + self.z*o.z
    def cross(self, o): return Vector3(self.y*o.z-self.z*o.y, self.z*o.x-self.x*o.z, self.x*o.y-self.y*o.x)
    def mag(self): return math.sqrt(self.x**2 + self.y**2 + self.z**2)
    def __repr__(self): return f"({self.x}, {self.y}, {self.z})"

class Matrix:
    """Simple Matrix (2x2 or 3x3) for transformations."""
    def __init__(self, rows): self.rows = rows
    def det(self):
        if len(self.rows) == 2: return self.rows[0][0]*self.rows[1][1] - self.rows[0][1]*self.rows[1][0]
        return 0 # Placeholder for 3x3
    def mv(self, v): # Matrix-Vector multiplication
        return Vector3(
            self.rows[0][0]*v.x + self.rows[0][1]*v.y,
            self.rows[1][0]*v.x + self.rows[1][1]*v.y, 0
        )

def draw_integral_area(func_lambda, x_range, color='blue', alpha=0.3):
    """
    [Visual] Helper to plot area under curve. 
    Usage: In generate(), ax.fill_between(x, y, ...).
    Actually, this is just a placeholder to remind AI to use fill_between.
    """
    pass

# --- 5. Standard Answer Checker (Auto-Injected) ---
def check(user_answer, correct_answer):
    """
    Standard Answer Checker [V9.8.1 Enhanced]
    1. Handles float tolerance.
    2. Normalizes strings (removes spaces, supports Chinese commas).
    3. Returns user-friendly Chinese error messages.
    """
    if user_answer is None: return {"correct": False, "result": r"""答案錯誤。正確答案為：{ans}""".replace("{ans}", str(correct_answer))}



import base64
from datetime import datetime
from io import BytesIO
from matplotlib.figure import Figure # 遵循 Infrastructure Rule 1: NO matplotlib.pyplot
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import numpy as np

# --- 視覺化與輔助函式通用規範 (Generic Helper Rules) ---
# 這些輔助函式是 TECHNICAL SPECIFICATION 的一部分，而非我額外定義，因此保留。

def _draw_number_line(points_data, min_limit, max_limit, title_text="", highlight_segments=None):
    """
    [V10.2 精簡版] 只顯示刻度 0，字體放大，去除所有文字提示。
    """
    fig = Figure(figsize=(8, 1.5)) # 高度縮小一點更精悍
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(111)

    # 1. 繪製數線主體
    ax.plot([min_limit, max_limit], [0, 0], 'k-', linewidth=1.5) 
    ax.plot(max_limit, 0, 'k>', markersize=8) # 右箭頭
    ax.plot(min_limit, 0, 'k<', markersize=8) # 左箭頭

    # 2. 設定刻度：只顯示 0，並且字體加大
    ax.set_xticks([0])
    ax.set_xticklabels(['0'], fontsize=18, fontweight='bold') 
    
    # 3. 移除所有標籤與標題 (滿足「不顯示任何提示」需求)
    ax.set_title("")
    ax.set_xlabel("")
    ax.set_yticks([]) 

    # 4. 繪製題目指定的點 (紅點與標籤 A, B)
    for label, coord in points_data.items():
        if isinstance(coord, (int, float)):
            ax.plot(coord, 0, 'ro', markersize=7) 
            # 點的標籤 (A, B) 稍微放大
            ax.text(coord, 0.08, label, ha='center', va='bottom', fontsize=14, fontweight='bold')

    # 5. 美化版面
    ax.set_ylim(-0.15, 0.25)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False) # 隱藏底線，讓數線本體看起來更乾淨
    
    fig.tight_layout()

    # 輸出 Base64
    buf = BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', transparent=True)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

def _generate_distinct_coordinates(min_val=-10, max_val=10, count=2):
    """
    生成指定範圍內 `count` 個不重複的隨機整數坐標。
    """
    if count > (max_val - min_val + 1):
        raise ValueError("無法在給定範圍內生成足夠的不重複坐標。")
    coords = random.sample(range(min_val, max_val + 1), count)
    return coords

# --- 程式結構 (Structure Hardening) ---
# 遵循 Infrastructure Rule 2: Top-level functions ONLY
def generate(level=1):
    """
    生成 K12 數學「數線上兩點的距離」題目。
    嚴禁使用 class 封裝，代碼不依賴全域狀態。
    """
    # 題型隨機分流 (Problem Variety)
    problem_type = random.choice(["direct_calculation", "inverse_problem", "contextual_application"])
    
    question_text = ""
    correct_answer = None
    numerical_answer = None
    image_base64 = ""
    points_for_plot = {} # 僅用於繪圖的已知點
    plot_min = -15
    plot_max = 15

    if problem_type == "direct_calculation":
        # 題型1: 直接計算 (Direct Calculation)
        # 給定兩點坐標，求距離。
        coord1, coord2 = _generate_distinct_coordinates(min_val=-10, max_val=10, count=2)
        coord1_label = random.choice(['A', 'P', 'X'])
        coord2_label = random.choice(['B', 'Q', 'Y'])
        while coord2_label == coord1_label: # 確保標籤不重複
            coord2_label = random.choice(['B', 'Q', 'Y'])

        points_for_plot = {coord1_label: coord1, coord2_label: coord2}
        numerical_answer = abs(coord1 - coord2)
        
        # 排版與 LaTeX 安全 (Elite Guardrails)
        # 凡字串包含 LaTeX 指令 (如 \frac, \sqrt, \pm)，嚴禁使用 f-string 或 % 格式化。
        # 這裡的字串雖然沒有 LaTeX 指令，但仍遵循嚴格的 .replace() 模板以確保未來擴展性。
        # 遵循 Infrastructure Rule 5: LaTeX Integrity (使用 r"template".replace())
        question_template = r"數線上有兩點 {label1} 和 {label2}，其坐標分別為 {val1} 和 {val2}。請問 {label1} 和 {label2} 兩點之間的距離為何？"
        
        question_text = question_template.replace("{label1}", coord1_label)\
                                         .replace("{label2}", coord2_label)\
                                         .replace("{val1}", str(coord1))\
                                         .replace("{val2}", str(coord2))
        
        correct_answer = str(numerical_answer) # 答案必須是字串
        
        # 調整繪圖範圍以包含所有點
        plot_min = min(coord1, coord2) - random.randint(3, 7)
        plot_max = max(coord1, coord2) + random.randint(3, 7)
        image_base64 = _draw_number_line(points_for_plot, plot_min, plot_max, title_text=r"數線上兩點的距離")

    elif problem_type == "inverse_problem":
        # 題型2: 逆向求解 (已知距離求座標)
        # 給定一點、距離和方向，求另一個點的坐標。
        start_coord = random.randint(-8, 8)
        distance = random.randint(3, 12)
        direction = random.choice(["right", "left"]) # 決定向左或向右

        start_label = random.choice(['A', 'P', 'X'])
        end_label = random.choice(['B', 'Q', 'Y'])
        while end_label == start_label:
            end_label = random.choice(['B', 'Q', 'Y'])

        if direction == "right":
            numerical_answer = start_coord + distance
            question_template = r"數線上 {label1} 點的坐標為 {val1}。若 {label2} 點在 {label1} 點的右方，且兩點之間的距離為 {dist}，請問 {label2} 點的坐標為何？"
            question_text = question_template.replace("{label1}", start_label)\
                                             .replace("{label2}", end_label)\
                                             .replace("{val1}", str(start_coord))\
                                             .replace("{dist}", str(distance))
        else: # direction == "left"
            numerical_answer = start_coord - distance
            question_template = r"數線上 {label1} 點的坐標為 {val1}。若 {label2} 點在 {label1} 點的左方，且兩點之間的距離為 {dist}，請問 {label2} 點的坐標為何？"
            question_text = question_template.replace("{label1}", start_label)\
                                             .replace("{label2}", end_label)\
                                             .replace("{val1}", str(start_coord))\
                                             .replace("{dist}", str(distance))
        
        correct_answer = str(numerical_answer)
        
        # 視覺化函式僅能接收「題目已知數據」。此處僅繪製已知點。
        points_for_plot = {start_label: start_coord}
        plot_min = min(start_coord, numerical_answer) - random.randint(3, 7)
        plot_max = max(start_coord, numerical_answer) + random.randint(3, 7)
        image_base64 = _draw_number_line(points_for_plot, plot_min, plot_max, title_text=r"尋找數線上的點")

    elif problem_type == "contextual_application":
        # 題型3: 情境應用 (如移動點)
        # 點在數線上經過多次移動，求最終位置。
        start_coord = random.randint(-10, 10)
        move1_dist = random.randint(2, 7)
        move2_dist = random.randint(2, 7)
        
        move1_dir = random.choice(["right", "left"])
        move2_dir = random.choice(["right", "left"])

        current_coord = start_coord # 追蹤點的當前位置
        description_parts = []
        
        point_label = random.choice(['P', 'Q', 'M'])
        
        description_parts.append(r"點 {label} 原本在坐標 {start_val} 的位置。".replace("{label}", point_label).replace("{start_val}", str(start_coord)))
        
        if move1_dir == "right":
            current_coord += move1_dist
            description_parts.append(r"它先向右移動了 {dist1} 個單位。".replace("{dist1}", str(move1_dist)))
        else:
            current_coord -= move1_dist
            description_parts.append(r"它先向左移動了 {dist1} 個單位。".replace("{dist1}", str(move1_dist)))
            
        if move2_dir == "right":
            current_coord += move2_dist
            description_parts.append(r"接著再向右移動了 {dist2} 個單位。".replace("{dist2}", str(move2_dist)))
        else:
            current_coord -= move2_dist
            description_parts.append(r"接著再向左移動了 {dist2} 個單位。".replace("{dist2}", str(move2_dist)))

        numerical_answer = current_coord
        
        question_text = "".join(description_parts) + r"請問點 {label} 最後的坐標為何？".replace("{label}", point_label)
        correct_answer = str(numerical_answer)
        
        # 視覺化函式僅能接收「題目已知數據」。此處僅繪製起點。
        points_for_plot = {point_label: start_coord}
        plot_min = min(start_coord, numerical_answer) - random.randint(3, 7)
        plot_max = max(start_coord, numerical_answer) + random.randint(3, 7)
        image_base64 = _draw_number_line(points_for_plot, plot_min, plot_max, title_text=r"點的移動")

    # 數據與欄位 (Standard Fields)
    # 遵循 Infrastructure Rule 3: Return Format (CRITICAL)
    return {
        "question_text": question_text,
        "correct_answer": correct_answer, # 必須是字串
        "answer": numerical_answer,       # 數值型答案 (int 或 float)
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(), # ISO 8601 格式時間戳記
        "version": 1 # 初始版本號，外部系統負責遞增
    }

# 遵循 Infrastructure Rule 2: Top-level functions ONLY
# 遵循 Infrastructure Rule 3: Return Format (CRITICAL)
def check(user_answer, correct_answer):
    """
    檢查使用者答案是否正確。
    
    Args:
        user_answer (str): 使用者輸入的答案字串。
        correct_answer (str): 由 generate 函式提供的正確答案字串。
        
    Returns:
        dict: 包含 'correct' (bool) 和 'result' (str) 的字典。
    """
    try:
        user_ans_num = float(user_answer)
        correct_ans_num = float(correct_answer)
        # 使用一個小的容忍度進行浮點數比較，以防潛在的精度問題
        is_correct = math.isclose(user_ans_num, correct_ans_num, rel_tol=1e-9, abs_tol=1e-9)
        
        if is_correct:
            return {"correct": True, "result": "正確！"}
    except:
        pass
            
    return {"correct": False, "result": r"""答案錯誤。正確答案為：{ans}""".replace("{ans}", str(correct_answer))}

# --- 範例使用 (用於測試，非最終模組的一部分) ---
if __name__ == "__main__":
    print("--- 生成 5 個題目範例 ---")
    for i in range(5):
        problem = generate()
        print(f"\n--- 題目 {i+1} ---")
        print(f"問題: {problem['question_text']}")
        print(f"正確答案 (字串): {problem['correct_answer']}")
        print(f"答案 (數值): {problem['answer']}")
        print(f"圖片 Base64 (前50字元): {problem['image_base64'][:50]}...")
        print(f"生成時間: {problem['created_at']}")
        print(f"版本: {problem['version']}")

        # 測試 check 函式
        test_user_answer_correct = problem['correct_answer']
        # 確保錯誤答案與正確答案不同，且能轉換為數字
        test_user_answer_wrong = str(float(problem['correct_answer']) + random.choice([-1, 1]) * random.random() * 5)
        
        print(f"檢查使用者答案 '{test_user_answer_correct}': {check(test_user_answer_correct, problem['correct_answer'])}")
        print(f"檢查使用者答案 '{test_user_answer_wrong}': {check(test_user_answer_wrong, problem['correct_answer'])}")
        print(f"檢查使用者答案 'abc': {check('abc', problem['correct_answer'])}")

        # 將 Base64 圖片儲存為檔案以供查看 (可選)
        # with open(f"number_line_problem_{i+1}.png", "wb") as f:
        #     f.write(base64.b64decode(problem['image_base64']))
        # print(f"圖片已儲存為 number_line_problem_{i+1}.png")

    print("\n--- LaTeX 安全性測試 (確保未使用 f-string 處理可能含 LaTeX 的字串) ---")
    ans_val_test = 10
    # 遵循規範，即使是簡單替換也使用 .replace()
    expr_safe_template = r"答案為 {a}。"
    expr_safe = expr_safe_template.replace("{a}", str(ans_val_test))
    print(f"安全字串生成範例: {expr_safe}")
    # 嚴禁使用 f"答案為 {ans_val_test}" 這樣的寫法

# [Auto-Injected Patch v10.4] Universal Return, Linebreak & Chinese Fixer
def _patch_all_returns(func):
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        if func.__name__ == "check" and isinstance(res, bool):
            return {"correct": res, "result": "正確！" if res else "答案錯誤"}
        if isinstance(res, dict):
            if "question_text" in res and isinstance(res["question_text"], str):
                res["question_text"] = res["question_text"].replace("\\n", "\n")
            if func.__name__ == "check" and "result" in res:
                msg = str(res["result"]).lower()
                if any(w in msg for w in ["correct", "right", "success"]): res["result"] = "正確！"
                elif any(w in msg for w in ["incorrect", "wrong", "error"]):
                    if "正確答案" not in res["result"]: res["result"] = "答案錯誤"
            if "answer" not in res and "correct_answer" in res: res["answer"] = res["correct_answer"]
            if "answer" in res: res["answer"] = str(res["answer"])
            if "image_base64" not in res: res["image_base64"] = ""
        return res
    return wrapper
import sys
for _name, _func in list(globals().items()):
    if callable(_func) and (_name.startswith("generate") or _name == "check"):
        globals()[_name] = _patch_all_returns(_func)
