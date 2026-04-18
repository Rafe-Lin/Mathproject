# ==============================================================================
# ID: jh_數學1下_ThreeViewDrawings
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 55.26s | RAG: 4 examples
# Created At: 2026-01-17 23:42:21
# Fix Status: [Repaired]
# Fixes: Regex=1, Logic=0
#==============================================================================


# [V12.3 Elite Standard Math Tools]
import random
import math
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from fractions import Fraction
from functools import reduce
import ast
import base64
import io
import re

# [V11.6 Elite Font & Style] - Hardcoded
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
plt.rcParams['axes.unicode_minus'] = False

def to_latex(num):
    if isinstance(num, int): return str(num)
    if isinstance(num, float): num = Fraction(str(num)).limit_denominator(100)
    if isinstance(num, Fraction):
        if num == 0: return "0"
        if num.denominator == 1: return str(num.numerator)
        sign = "-" if num < 0 else ""
        abs_num = abs(num)
        if abs_num.numerator > abs_num.denominator:
            whole = abs_num.numerator // abs_num.denominator
            rem_num = abs_num.numerator % abs_num.denominator
            if rem_num == 0: return r"{s}{w}".replace("{s}", sign).replace("{w}", str(whole))
            return r"{s}{w} \frac{{n}}{{d}}".replace("{s}", sign).replace("{w}", str(whole)).replace("{n}", str(rem_num)).replace("{d}", str(abs_num.denominator))
        return r"\frac{{n}}{{d}}".replace("{n}", str(num.numerator)).replace("{d}", str(num.denominator))
    return str(num)

def fmt_num(num, signed=False, op=False):
    latex_val = to_latex(num)
    if num == 0 and not signed and not op: return "0"
    is_neg = (num < 0)
    abs_str = to_latex(abs(num))
    if op:
        if is_neg: return r" - {v}".replace("{v}", abs_str)
        return r" + {v}".replace("{v}", abs_str)
    if signed:
        if is_neg: return r"-{v}".replace("{v}", abs_str)
        return r"+{v}".replace("{v}", abs_str)
    if is_neg: return r"({v})".replace("{v}", latex_val)
    return latex_val

# --- 2. Number Theory Helpers ---
def is_prime(n):
    if n <= 1: return False
    if n <= 3: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True

def get_positive_factors(n):
    factors = set()
    for i in range(1, int(math.isqrt(n)) + 1):
        if n % i == 0:
            factors.add(i)
            factors.add(n // i)
    return sorted(list(factors))

def get_prime_factorization(n):
    factors = {}
    d = 2
    temp = n
    while d * d <= temp:
        while temp % d == 0:
            factors[d] = factors.get(d, 0) + 1
            temp //= d
        d += 1
    if temp > 1:
        factors[temp] = factors.get(temp, 0) + 1
    return factors

def gcd(a, b): return math.gcd(int(a), int(b))
def lcm(a, b): return abs(int(a) * int(b)) // math.gcd(int(a), int(b))

# --- 3. Fraction Generator & Helpers ---
def simplify_fraction(n, d):
    common = math.gcd(n, d)
    return n // common, d // common

def _calculate_distance_1d(a, b):
    return abs(a - b)

def get_random_fraction(min_val=-10, max_val=10, denominator_limit=10, simple=True):
    for _ in range(100):
        den = random.randint(2, denominator_limit)
        num = random.randint(min_val * den, max_val * den)
        if den == 0: continue
        val = Fraction(num, den)
        if simple and val.denominator == 1: continue 
        if val == 0: continue
        return val
    return Fraction(1, 2)

# --- 7 下 強化組件 A: 數線區間渲染器 (針對不等式) ---
def draw_number_line(points_map, x_min=None, x_max=None, intervals=None, **kwargs):
    """
    intervals: list of dict, e.g., [{'start': 3, 'direction': 'right', 'include': False}]
    """
    values = [float(v) for v in points_map.values()] if points_map else [0]
    if intervals:
        for inter in intervals: values.append(float(inter['start']))
    
    if x_min is None: x_min = math.floor(min(values)) - 2
    if x_max is None: x_max = math.ceil(max(values)) + 2
    
    fig = Figure(figsize=(8, 2))
    ax = fig.add_subplot(111)
    ax.plot([x_min, x_max], [0, 0], 'k-', linewidth=1.5)
    ax.plot(x_max, 0, 'k>', markersize=8, clip_on=False)
    ax.plot(x_min, 0, 'k<', markersize=8, clip_on=False)
    
    # 數線刻度規範
    ax.set_xticks([0])
    ax.set_xticklabels(['0'], fontsize=18, fontweight='bold')
    
    # 繪製不等式區間 (7 下 關鍵)
    if intervals:
        for inter in intervals:
            s = float(inter['start'])
            direct = inter.get('direction', 'right')
            inc = inter.get('include', False)
            color = 'red'
            # 畫圓點 (空心/實心)
            ax.plot(s, 0.2, marker='o', mfc='white' if not inc else color, mec=color, ms=10, zorder=5)
            # 畫折線射線
            target_x = x_max if direct == 'right' else x_min
            ax.plot([s, s, target_x], [0.2, 0.5, 0.5], color=color, lw=2)

    for label, val in points_map.items():
        v = float(val)
        ax.plot(v, 0, 'ro', ms=7)
        ax.text(v, 0.08, label, ha='center', va='bottom', fontsize=16, fontweight='bold', color='red')

    ax.set_yticks([]); ax.axis('off')
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', transparent=True, dpi=300)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

# --- 7 下 強化組件 B: 直角坐標系渲染器 (針對方程式圖形) ---
def draw_coordinate_system(lines=None, points=None, x_range=(-5, 5), y_range=(-5, 5)):
    """
    繪製標準坐標軸與直線方程式
    """
    fig = Figure(figsize=(5, 5))
    ax = fig.add_subplot(111)
    ax.set_aspect('equal') # 鎖死比例
    
    # 繪製網格與軸線
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.axhline(0, color='black', lw=1.5)
    ax.axvline(0, color='black', lw=1.5)
    
    # 繪製直線 (y = mx + k)
    if lines:
        import numpy as np
        for line in lines:
            m, k = line.get('m', 0), line.get('k', 0)
            x = np.linspace(x_range[0], x_range[1], 100)
            y = m * x + k
            ax.plot(x, y, lw=2, label=line.get('label', ''))

    # 繪製點 (x, y)
    if points:
        for p in points:
            ax.plot(p[0], p[1], 'ro')
            ax.text(p[0]+0.2, p[1]+0.2, p.get('label', ''), fontsize=14, fontweight='bold')

    ax.set_xlim(x_range); ax.set_ylim(y_range)
    # 隱藏刻度，僅保留 0
    ax.set_xticks([0]); ax.set_yticks([0])
    
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', transparent=True, dpi=300)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

def draw_geometry_composite(polygons, labels, x_limit=(0,10), y_limit=(0,10)):
    """[V11.6 Ultra Visual] 物理級幾何渲染器 (Physical Geometry Renderer)"""
    fig = Figure(figsize=(5, 4))
    canvas = FigureCanvasAgg(fig)
    ax = fig.add_subplot(111)
    ax.set_aspect('equal', adjustable='datalim')
    all_x, all_y = [], []
    for poly_pts in polygons:
        polygon = patches.Polygon(poly_pts, closed=True, fill=False, edgecolor='black', linewidth=2)
        ax.add_patch(polygon)
        for p in poly_pts:
            all_x.append(p[0])
            all_y.append(p[1])
    for text, pos in labels.items():
        all_x.append(pos[0])
        all_y.append(pos[1])
        ax.text(pos[0], pos[1], text, fontsize=20, fontweight='bold', ha='center', va='center',
                bbox=dict(facecolor='white', edgecolor='none', alpha=0.8, pad=1))
    if all_x and all_y:
        min_x, max_x = min(all_x), max(all_x)
        min_y, max_y = min(all_y), max(all_y)
        rx = (max_x - min_x) * 0.3 if (max_x - min_x) > 0 else 1.0
        ry = (max_y - min_y) * 0.3 if (max_y - min_y) > 0 else 1.0
        ax.set_xlim(min_x - rx, max_x + rx)
        ax.set_ylim(min_y - ry, max_y + ry)
    else:
        ax.set_xlim(x_limit)
        ax.set_ylim(y_limit)
    ax.axis('off')
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', transparent=True, dpi=300)
    del fig
    return base64.b64encode(buf.getvalue()).decode('utf-8')

# --- 4. Answer Checker (V11.6 Smart Formatting Standard) ---
def check(user_answer, correct_answer):
    if user_answer is None: return {"correct": False, "result": "未提供答案。"}
    
    # 將字典或複雜格式轉為乾淨字串
    def _format_ans(a):
        if isinstance(a, dict):
            if "quotient" in a: 
                return r"{q}, {r}".replace("{q}", str(a.get("quotient",""))).replace("{r}", str(a.get("remainder","")))
            return ", ".join([r"{k}={v}".replace("{k}", str(k)).replace("{v}", str(v)) for k, v in a.items()])
        return str(a)

    def _clean(s):
        # 雙向清理：剝除 LaTeX 符號與空格
        return str(s).strip().replace(" ", "").replace("，", ",").replace("$", "").replace("\\", "").lower()
    
    u = _clean(user_answer)
    c_raw = _format_ans(correct_answer)
    c = _clean(c_raw)
    
    if u == c: return {"correct": True, "result": "正確！"}
    
    try:
        import math
        if math.isclose(float(u), float(c), abs_tol=1e-6): return {"correct": True, "result": "正確！"}
    except: pass
    
    return {"correct": False, "result": r"答案錯誤。正確答案為：{ans}".replace("{ans}", c_raw)}

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import base64
from io import BytesIO
import json
import re


def plot_blocks(blocks_coords, ax, color='skyblue', alpha=0.8):
    """
    Plots a 3D block stack on the given matplotlib 3D axes.

    Args:
        blocks_coords (list): A list of (x, y, z) tuples representing the
                              base-corner coordinates of each unit cube.
        ax (Axes3D): The matplotlib 3D axes object to draw on.
        color (str): The color of the blocks.
        alpha (float): The transparency of the blocks.
    """
    if not blocks_coords:
        return

    # Determine the minimum and maximum coordinates to define the grid for plotting
    min_x = min(c[0] for c in blocks_coords)
    max_x = max(c[0] for c in blocks_coords)
    min_y = min(c[1] for c in blocks_coords)
    max_y = max(c[1] for c in blocks_coords)
    min_z = min(c[2] for c in blocks_coords)
    max_z = max(c[2] for c in blocks_coords)

    # Create a 3D boolean array (voxel grid) to represent the filled space
    # Dimensions are based on the extent of the blocks
    grid_dim_x = max_x - min_x + 1
    grid_dim_y = max_y - min_y + 1
    grid_dim_z = max_z - min_z + 1

    filled = np.zeros((grid_dim_x, grid_dim_y, grid_dim_z), dtype=bool)

    # Populate the filled array by adjusting coordinates to be 0-indexed relative to the minimums
    for x, y, z in blocks_coords:
        filled[x - min_x, y - min_y, z - min_z] = True

    # Define the grid lines for ax.voxels. These should span from min_coord to max_coord + 1.
    x_grid = np.arange(min_x, max_x + 2)
    y_grid = np.arange(min_y, max_y + 2)
    z_grid = np.arange(min_z, max_z + 2)
    
    # Plot the voxels
    ax.voxels(x_grid[:-1], y_grid[:-1], z_grid[:-1], filled, facecolors=color, edgecolor='grey', shade=True, alpha=alpha)

    # Set axis limits to tightly fit the blocks, with a small margin
    margin = 0.5
    ax.set_xlim(min_x - margin, max_x + margin + 0.5)
    ax.set_ylim(min_y - margin, max_y + margin + 0.5)
    ax.set_zlim(min_z - margin, max_z + margin + 0.5)

    # Set mandatory axis ticks (as per coding standards)
    ax.set_xticks(np.arange(min_x, max_x + 1))
    ax.set_yticks(np.arange(min_y, max_y + 1))
    ax.set_zticks(np.arange(min_z, max_z + 1))

    # Remove axis labels and tick labels for a cleaner isometric view, focusing on the object
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.set_zlabel('')
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.set_zticklabels([])

    # Set view angle for isometric perspective (a common choice for 3D blocks)
    ax.view_init(elev=30, azim=-60)
    
    # Ensure equal aspect ratio (MANDATORY MIRRORING RULES)
    ax.set_aspect('equal')

    # Remove the bounding box for a cleaner visual representation of the object itself
    ax.set_box_on(False)


def generate(level=1, **kwargs):
    """
    Generates a Type 3 problem based on RAG Ex 3: identifying observation directions
    from described 2D views of a 3D block stack.
    """
    problem_type = "view_identification"
    
    # Define the 3D shape as a list of unit cube coordinates (bottom-front-left corner)
    # This specific shape (an L-shape, 1 unit deep) is chosen to match the views
    # described in RAG Ex 3's solution:
    # - Blocks at (0,0,0), (1,0,0), (0,0,1)
    # - Right View (from +X, looking towards Y-Z plane): projects to (0,0) and (0,1) in Y-Z plane,
    #   forming a 2x1 vertical block.
    # - Top View (from +Z, looking towards X-Y plane): projects to (0,0) and (1,0) in X-Y plane,
    #   forming a 1x2 horizontal block.
    blocks_coords = [(0,0,0), (1,0,0), (0,0,1)]

    # Create the 3D plot of the block stack
    fig = plt.figure(figsize=(6, 6), dpi=300) # ULTRA VISUAL STANDARDS: dpi=300
    ax = fig.add_subplot(111, projection='3d')

    plot_blocks(blocks_coords, ax)

    # Convert the plot to a base64 encoded PNG image
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=300)
    plt.close(fig)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')

    # Problem question text, mirroring RAG Ex 3
    question_text = (
        "右圖是一個由方塊堆疊的立體圖形，小嘉和小鈺分別從不同方向觀察這個立體圖形，並繪製視圖如下。\n"
        "請判斷他們分別是從哪個方向觀察？( 填前、後、左、右、上 )\n"
        "小嘉的視圖：一個2x1的垂直排列方塊\n"
        "小鈺的視圖：一個1x2的水平排列方塊"
    )
    
    # Correct answer, mirroring RAG Ex 3
    correct_answer = "小嘉：右面，小鈺：上面"

    # Detailed solution explanation
    solution_text = (
        "此立體圖形由三塊方塊組成，其底層方塊位於 (0,0,0) 和 (1,0,0)，頂層方塊位於 (0,0,1)。\n"
        "1. 小嘉的視圖是一個2x1的垂直排列方塊：\n"
        "   - 從右面觀察 (沿X軸正向看Y-Z平面)，會看到方塊 (0,0,0) 和 (0,0,1) 在Y-Z平面上投影為 (0,0) 和 (0,1)，\n"
        "     形成一個高2單位、寬1單位的垂直排列方塊。方塊 (1,0,0) 會被 (0,0,0) 遮擋。\n"
        "   - 因此，小嘉是從右面觀察。\n"
        "2. 小鈺的視圖是一個1x2的水平排列方塊：\n"
        "   - 從上面觀察 (沿Z軸正向看X-Y平面)，會看到方塊 (0,0,0) 和 (1,0,0) 在X-Y平面上投影為 (0,0) 和 (1,0)，\n"
        "     形成一個高1單位、寬2單位的水平排列方塊。方塊 (0,0,1) 會被 (0,0,0) 遮擋。\n"
        "   - 因此，小鈺是從上面觀察。\n"
        "綜合以上判斷，小嘉從右面觀察，小鈺從上面觀察。"
    )

    return {
        "problem_type": problem_type,
        "question": question_text,
        "image_base64": image_base64,
        "correct_answer": correct_answer,
        "solution": solution_text
    }



    """
    Compares the user's answer to the correct answer, with robust string cleaning
    and normalization for direction identification problems.

    Args:
        user_answer (str): The answer provided by the user.
        correct_answer (str): The true correct answer.

    Returns:
        dict: A dictionary indicating if the answer is correct and a result message.
    """
    import re, math

    # 1. 清洗雙方輸入 (移除 LaTeX, 變數名, 空格, 並進行特定內容的正規化)
    def clean(s):
        s = str(s).strip().replace(" ", "").lower()
        s = re.sub(r'^[a-z]+=', '', s)  # 移除 k=, x=, y= 等變數前綴
        s = s.replace("$", "").replace("\\", "")  # 移除 LaTeX 符號
        
        # 特定清洗規則，用於方向詞彙和人名
        s = s.replace("面", "")  # 移除 '面' 字，例如 "右面" 變 "右"
        
        # 正規化觀察者名稱和分隔符
        s = s.replace("小嘉:", "小嘉").replace("小鈺:", "小鈺")
        s = s.replace("，", ",").replace("、", ",").replace("和", ",")  # 正規化所有分隔符為逗號
        
        # 將答案拆分為多個部分，排序後重新組合，以處理使用者輸入順序不一致的情況
        parts = sorted([p.strip() for p in s.split(',') if p.strip()])
        return ",".join(parts)
    
    u = clean(user_answer)
    c = clean(correct_answer)
    
    # 2. 嘗試數值比對 (支援分數與小數) - 根據 CRITICAL CODING STANDARDS 模板保留，
    #    但對於此題型（方向判斷）通常不適用。
    try:
        def parse_val(val_str):
            if "/" in val_str:
                n, d = map(float, val_str.split("/"))
                return n/d
            return float(val_str)
        
        # 僅當字串看起來是純數字時才嘗試數值比對
        if re.fullmatch(r"[-+]?\d+(\.\d+)?(/[+-]?\d+(\.\d+)?)?", u) and \
           re.fullmatch(r"[-+]?\d+(\.\d+)?(/[+-]?\d+(\.\d+)?)?", c):
            if math.isclose(parse_val(u), parse_val(c), rel_tol=1e-5):
                return {"correct": True, "result": "正確！"}
    except:
        pass
        
    # 3. 降級為字串比對
    if u == c:
        return {"correct": True, "result": "正確！"}
    return {"correct": False, "result": f"答案錯誤。"}


# [Auto-Injected Patch v11.0] Universal Return, Linebreak & Handwriting Fixer
def _patch_all_returns(func):
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        
        # 1. 針對 check 函式的布林值回傳進行容錯封裝
        if func.__name__ == 'check' and isinstance(res, bool):
            return {'correct': res, 'result': '正確！' if res else '答案錯誤'}
        
        if isinstance(res, dict):
            # [V11.3 Standard Patch] - 解決換行與編碼問題
            if 'question_text' in res and isinstance(res['question_text'], str):
                # 僅針對「文字反斜線+n」進行物理換行替換，不進行全局編碼轉換
                import re
                # 解決 r-string 導致的 \n 問題
                res['question_text'] = re.sub(r'\n', '\n', res['question_text'])
            
            # --- [V11.0] 智能手寫模式偵測 (Auto Handwriting Mode) ---
            # 判定規則：若答案包含複雜運算符號，強制提示手寫作答
            # 包含: ^ / _ , | ( [ { 以及任何 LaTeX 反斜線
            c_ans = str(res.get('correct_answer', ''))
            # [V13.1 修復] 移除 '(' 與 ','，允許座標與數列使用純文字輸入
            triggers = ['^', '/', '|', '[', '{', '\\']
            
            # [V11.1 Refined] 僅在題目尚未包含提示時注入，避免重複堆疊
            has_prompt = "手寫" in res.get('question_text', '')
            should_inject = (res.get('input_mode') == 'handwriting') or any(t in c_ans for t in triggers)
            
            if should_inject and not has_prompt:
                res['input_mode'] = 'handwriting'
                # [V11.3] 確保手寫提示語在最後一行
                res['question_text'] = res['question_text'].rstrip() + "\n(請在手寫區作答!)"

            # 3. 確保反饋訊息中文
            if func.__name__ == 'check' and 'result' in res:
                if res['result'].lower() in ['correct!', 'correct', 'right']:
                    res['result'] = '正確！'
                elif res['result'].lower() in ['incorrect', 'wrong', 'error']:
                    res['result'] = '答案錯誤'
            
            # 4. 確保欄位完整性
            if 'answer' not in res and 'correct_answer' in res:
                res['answer'] = res['correct_answer']
            if 'answer' in res:
                res['answer'] = str(res['answer'])
            if 'image_base64' not in res:
                res['image_base64'] = ""
        return res
    return wrapper

import sys
for _name, _func in list(globals().items()):
    if callable(_func) and (_name.startswith('generate') or _name == 'check'):
        globals()[_name] = _patch_all_returns(_func)
