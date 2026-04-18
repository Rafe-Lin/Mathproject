# ==============================================================================
# ID: jh_數學1下_MeanMedianAndMode
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 88.82s | RAG: 5 examples
# Created At: 2026-01-17 22:52:42
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



from datetime import datetime
import base64
import re

def generate(level=1):
    # --- Helper Functions (Implemented internally as per spec) ---
    def _generate_data_list(count, min_val, max_val, allow_duplicates=True):
        """
        Generates a list of random integers.
        :param count: Number of elements in the list.
        :param min_val: Minimum possible value for an element.
        :param max_val: Maximum possible value for an element.
        :param allow_duplicates: If False, ensures all elements are unique.
        :return: A list of integers.
        """
        if allow_duplicates:
            data = [random.randint(min_val, max_val) for _ in range(count)]
        else:
            # Ensure enough unique values are available
            if count > (max_val - min_val + 1):
                # Fallback to allowing duplicates if unique range is too small
                return [random.randint(min_val, max_val) for _ in range(count)]
            data = random.sample(range(min_val, max_val + 1), count)
        return data

    def _calculate_mean(data_list):
        """
        Calculates the arithmetic mean of a list of numbers.
        :param data_list: List of numbers (int or float).
        :return: The mean as a float.
        """
        if not data_list:
            return 0.0
        return sum(data_list) / len(data_list)

    def _calculate_median(data_list):
        """
        Calculates the median of a list of numbers.
        :param data_list: List of numbers (int or float).
        :return: The median as a float or int.
        """
        if not data_list:
            return 0
        sorted_data = sorted(data_list)
        n = len(sorted_data)
        if n % 2 == 1:
            return sorted_data[n // 2]
        else:
            mid1 = sorted_data[n // 2 - 1]
            mid2 = sorted_data[n // 2]
            return (mid1 + mid2) / 2.0

    def _calculate_mode(data_list):
        """
        Calculates the mode(s) of a list of numbers.
        :param data_list: List of numbers (int or float).
        :return: A sorted list of mode(s), or an empty list if no mode (all unique or all same frequency for >1 unique items).
        """
        if not data_list:
            return []
        
        counts = {}
        for item in data_list:
            counts[item] = counts.get(item, 0) + 1
        
        if not counts:
            return []

        max_count = 0
        for count in counts.values():
            if count > max_count:
                max_count = count
        
        modes = [item for item, count in counts.items() if count == max_count]
        
        # If all items appear with the same frequency (e.g., [1,2,3] or [1,1,2,2]),
        # and there's more than one unique item, often considered "no mode".
        # If max_count is 1 and there's more than one element, all are unique, so no mode.
        # If max_count > 1 and all unique items have this max_count, then all are modes (e.g., [1,1,2,2] -> modes 1,2).
        if max_count == 1 and len(data_list) > 1:
            return []
        else:
            return sorted(modes) # Ensure consistent order for multiple modes

    # --- Problem Generation Logic ---
    problem_type = random.choice([1, 2, 3, 4, 5]) # Maps directly to RAG Ex 1-5

    question_text = ""
    correct_answer = ""
    image_base64 = "" # As per spec, image_base64 will be an empty string for this skill.

    # Context names from RAG examples and general K12 math context
    person_names = ['小妍', '憶昀', '巴奈', '翔利', '冠豐', '小明', '小華', '大雄', '靜香', '胖虎']
    class_names = ['ACEF', 'BDF', '甲', '乙', '丙', '丁']
    subjects = ['國文', '英語', '數學', '社會', '自然', '理化', '生物', '歷史', '地理', '公民']
    item_units = ['張', '枝', '個', '顆', '份', '本', '次']
    currency_units = ['元', '塊']
    time_units = ['小時', '分鐘']

    if problem_type == 1:
        # Type 1 (Strictly mirrors RAG Ex 1): Simple list of numbers, calculate mean/median/mode.
        # RAG Ex 1: 小妍去書局買了 5 張生日卡片，價格依序為 18、25、31、17、24 元，則這 5 張卡片的平均價格為多少元？ -> 23 元
        
        num_elements = random.randint(5, 11) # Number of data points
        min_val = random.randint(10, 30)
        max_val = random.randint(min_val + 5, min_val + 20)
        
        # Generate data, ensuring some variety for mode calculation
        data = _generate_data_list(num_elements, min_val, max_val, allow_duplicates=True)
        random.shuffle(data) # Shuffle for question display
        
        data_str = ", ".join(map(str, data))

        mean_val = round(_calculate_mean(data), 2)
        median_val = _calculate_median(data)
        mode_list = _calculate_mode(data)

        # Choose what to ask (mean, median, mode, or all)
        choice = random.choice(['mean', 'median', 'mode', 'all'])
        person_name = random.choice(person_names)
        item_name = random.choice(['生日卡片', '鉛筆', '貼紙', '糖果', '彈珠', '蘋果', '練習本'])
        unit_name = random.choice(item_units)
        price_unit = random.choice(currency_units)

        if choice == 'mean':
            question_text = r"${person_name}$ 去書局買了 ${num_elements}$ ${unit_name}${item_name}，價格依序為 ${data_str}$ ${price_unit}，則這 ${num_elements}$ ${unit_name}${item_name}的平均價格為多少${price_unit}$？".replace("{person_name}", person_name).replace("{num_elements}", str(num_elements)).replace("{unit_name}", unit_name).replace("{item_name}", item_name).replace("{data_str}", data_str).replace("{price_unit}", price_unit)
            correct_answer = str(mean_val)
        elif choice == 'median':
            question_text = r"${person_name}$ 去書局買了 ${num_elements}$ ${unit_name}${item_name}，價格依序為 ${data_str}$ ${price_unit}，則這 ${num_elements}$ ${unit_name}${item_name}的中位數價格為多少${price_unit}$？".replace("{person_name}", person_name).replace("{num_elements}", str(num_elements)).replace("{unit_name}", unit_name).replace("{item_name}", item_name).replace("{data_str}", data_str).replace("{price_unit}", price_unit)
            correct_answer = str(median_val)
        elif choice == 'mode':
            question_text = r"${person_name}$ 去書局買了 ${num_elements}$ ${unit_name}${item_name}，價格依序為 ${data_str}$ ${price_unit}，則這 ${num_elements}$ ${unit_name}${item_name}的眾數價格為多少${price_unit}$？若有多個眾數，請由小到大以逗號分隔；若無眾數，請填寫 '無'。".replace("{person_name}", person_name).replace("{num_elements}", str(num_elements)).replace("{unit_name}", unit_name).replace("{item_name}", item_name).replace("{data_str}", data_str).replace("{price_unit}", price_unit)
            if not mode_list:
                correct_answer = "無"
            else:
                correct_answer = ", ".join(map(str, mode_list))
        else: # 'all'
            question_text = r"${person_name}$ 去書局買了 ${num_elements}$ ${unit_name}${item_name}，價格依序為 ${data_str}$ ${price_unit}。請依序計算這 ${num_elements}$ ${unit_name}${item_name}的平均價格、中位數價格和眾數價格。眾數有多個時請以逗號分隔，若無眾數則填寫 '無'。".replace("{person_name}", person_name).replace("{num_elements}", str(num_elements)).replace("{unit_name}", unit_name).replace("{item_name}", item_name).replace("{data_str}", data_str).replace("{price_unit}", price_unit)
            mode_ans_str = "無" if not mode_list else ", ".join(map(str, mode_list))
            correct_answer = f"{mean_val}, {median_val}, {mode_ans_str}"
            
    elif problem_type == 2:
        # Type 2 (Strictly mirrors RAG Ex 2): Given target mean and differences, calculate actual mean.
        # RAG Ex 2: 憶昀期待自己在段考時能有亮眼的表現，因此他給自己設定目標為 5 科平均 90 分。最後他得到的分數與目標分數的差距如下表，則憶昀此次段考的 5 科平均分數為多少分？科 目: 國文, 英語, 數學, 社會, 自然與目標分數的差距: +3, +5, -2, +4, -7 -> 90.6 分
        
        person_name = random.choice(['憶昀', '巴奈', '小明'])
        num_subjects = random.randint(4, 6)
        target_mean = random.randint(75, 95)
        
        # Generate differences, ensuring actual scores are reasonable (e.g., not negative)
        differences = []
        for _ in range(num_subjects):
            diff = random.randint(-10, 10)
            differences.append(diff)
        
        # Calculate actual scores based on target mean and differences
        actual_scores = [target_mean + diff for diff in differences]
        
        # Calculate the actual mean
        actual_mean_val = round(_calculate_mean(actual_scores), 1) # RAG example output is to 1 decimal place

        # Select subjects (ensure unique subjects)
        selected_subjects = random.sample(subjects, num_subjects)
        
        subject_list_str = ", ".join(selected_subjects)
        diff_list_str = ", ".join([f"{'+' if d > 0 else ''}{d}" for d in differences])

        question_text = r"${person_name}$ 期待自己在段考時能有亮眼的表現，因此他給自己設定目標為 ${num_subjects}$ 科平均 ${target_mean}$ 分。最後他得到的分數與目標分數的差距如下表，則 ${person_name}$ 此次段考的 ${num_subjects}$ 科平均分數為多少分？科 目: ${subject_list}$ 與目標分數的差距: ${diff_list}$".replace("{person_name}", person_name).replace("{num_subjects}", str(num_subjects)).replace("{target_mean}", str(target_mean)).replace("{subject_list}", subject_list_str).replace("{diff_list}", diff_list_str)
        correct_answer = str(actual_mean_val)

    elif problem_type == 3:
        # Type 3 (Strictly mirrors RAG Ex 3): Discrete frequency distribution table, calculate mean/median/mode.
        # RAG Ex 3: 七年 1 班導師為了鼓勵班上學生閱讀，規定每人每月至少閱讀 3 本課外讀物，一個月後統計結果如下表，則全班在這個月當中，每人平均閱讀幾本書？課外讀物(本): 3, 4, 5, 6, 7次數(人): 9, 8, 3, 4, 1 -> 4.2 本
        
        num_categories = random.randint(4, 7)
        # Categories (e.g., books read, scores, items collected)
        min_cat_val = random.randint(1, 5)
        categories = sorted(random.sample(range(min_cat_val, min_cat_val + num_categories + 3), num_categories)) # Ensure distinct categories
        frequencies = _generate_data_list(num_categories, 1, 15) # Number of people/occurrences

        all_data_expanded = []
        for c, f in zip(categories, frequencies):
            all_data_expanded.extend([c] * f)
        
        mean_val = round(_calculate_mean(all_data_expanded), 2)
        median_val = _calculate_median(all_data_expanded)
        mode_list = _calculate_mode(all_data_expanded)

        # [V16.23 Fix] Use list join for robust table generation
        table_lines = [
            f"| {item_name_header} | 次數({person_unit}) |",
            "|:---:|:---:|",
        ]
        for c, f in zip(categories, frequencies):
            table_lines.append(f"| {str(c)} | {str(f)} |")
        
        table_lines.append(f"| **總計** | **{total_count}** |")
        table_md = "\n".join(table_lines)
        
        question_text += "\n\n" + table_md

    elif problem_type == 4:
        # Type 4 (Strictly mirrors RAG Ex 4): Grouped frequency distribution table, calculate mean.
        # RAG Ex 4: 下表為七年甲班數學隨堂測驗分數次數分配表，則七年甲班全班學生的平均分數為多少分？分數(分): 50∼60, 60∼70, 70∼80, 80∼90, 90∼100次數(人): 2, 5, 5, 10, 3 -> 77.8 分
        
        num_groups = random.randint(4, 6)
        group_width = 10
        
        start_score = random.choice([50, 60, 70])
        
        score_ranges = []
        midpoints = []
        for i in range(num_groups):
            lower = start_score + i * group_width
            upper = lower + group_width
            score_ranges.append(f"{lower} ~ {upper}")
            midpoints.append((lower + upper) / 2.0)
            
        frequencies = _generate_data_list(num_groups, 1, 15)
        
        # Calculate grouped mean (using midpoints)
        sum_of_products = sum(m * f for m, f in zip(midpoints, frequencies))
        total_frequency = sum(frequencies)
        
        grouped_mean = round(sum_of_products / total_frequency, 1) # RAG example output is to 1 decimal place

        # [V16.23 Fix] Use list join for robust table generation
        table_lines = [
            "| 分數(分) | 次數(人) |",
            "|:---:|:---:|",
        ]
        for r, f in zip(score_ranges, frequencies):
            table_lines.append(f"| {r} | {str(f)} |")
            
        table_lines.append(f"| **總計** | **{total_frequency}** |")
        table_md = "\n".join(table_lines)

        class_name = random.choice(class_names)
        
        q_text_base = f"下表為七年 {class_name} 班數學隨堂測驗分數次數分配表，則七年 {class_name} 班全班學生的平均分數為多少分？"
        question_text = q_text_base + "\n\n" + table_md
        correct_answer = str(grouped_mean)

    elif problem_type == 5:
        # Type 5 (Strictly mirrors RAG Ex 5): Two separate lists of numbers, calculate median/mean/mode for each.
        # RAG Ex 5: 已知翔利與冠豐兩人在某月進行騎單車的自主訓練，每次訓練的騎乘時間如下:翔利：9, 3, 7, 6, 3, 10, 8, 2, 10, 2, 3 (小時)冠豐：7, 5, 2, 10, 9, 4, 9, 8, 3, 10, 5, 2 (小時)請問兩人騎乘時間的中位數分別為何？ -> 翔利的中位數為 6 小時，冠豐的中位數為 6 小時。
        
        name1 = random.choice(['翔利', '小明', 'ACEF'])
        name2 = random.choice(['冠豐', '小華', 'BDF'])
        while name1 == name2: # Ensure names are different
            name2 = random.choice(['冠豐', '小華', 'BDF'])

        num_elements1 = random.randint(8, 12)
        num_elements2 = random.randint(8, 12)
        
        min_val = random.randint(1, 5)
        max_val = random.randint(min_val + 5, min_val + 15)
        
        data1 = _generate_data_list(num_elements1, min_val, max_val)
        data2 = _generate_data_list(num_elements2, min_val, max_val)
        
        data1_str = ", ".join(map(str, data1))
        data2_str = ", ".join(map(str, data2))

        # Calculate for both lists
        mean1 = round(_calculate_mean(data1), 2)
        median1 = _calculate_median(data1)
        mode1 = _calculate_mode(data1)

        mean2 = round(_calculate_mean(data2), 2)
        median2 = _calculate_median(data2)
        mode2 = _calculate_mode(data2)

        # Choose what to ask
        choice = random.choice(['median', 'mean', 'mode']) # RAG example asks for median
        
        item_activity = random.choice(['騎單車的自主訓練', '跑步訓練', '讀書時間', '遊戲時間'])
        activity_unit = item_activity.split('的')[0] if '的' in item_activity else item_activity # e.g., '騎單車'
        time_unit = random.choice(time_units)
        
        if choice == 'median':
            question_text = r"已知${name1}$與${name2}$兩人在某月進行${item_activity}$，每次訓練的${activity_unit}$如下:\n${name1}$：${data1_str}$ (${time_unit}$)\n${name2}$：${data2_str}$ (${time_unit}$)\n請問兩人${activity_unit}$的中位數分別為何？".replace("{name1}", name1).replace("{name2}", name2).replace("{item_activity}", item_activity).replace("{activity_unit}", activity_unit).replace("{data1_str}", data1_str).replace("{data2_str}", data2_str).replace("{time_unit}", time_unit)
            correct_answer = f"{median1}, {median2}"
        elif choice == 'mean':
            question_text = r"已知${name1}$與${name2}$兩人在某月進行${item_activity}$，每次訓練的${activity_unit}$如下:\n${name1}$：${data1_str}$ (${time_unit}$)\n${name2}$：${data2_str}$ (${time_unit}$)\n請問兩人${activity_unit}$的平均數分別為何？".replace("{name1}", name1).replace("{name2}", name2).replace("{item_activity}", item_activity).replace("{activity_unit}", activity_unit).replace("{data1_str}", data1_str).replace("{data2_str}", data2_str).replace("{time_unit}", time_unit)
            correct_answer = f"{mean1}, {mean2}"
        else: # mode
            question_text = r"已知${name1}$與${name2}$兩人在某月進行${item_activity}$，每次訓練的${activity_unit}$如下:\n${name1}$：${data1_str}$ (${time_unit}$)\n${name2}$：${data2_str}$ (${time_unit}$)\n請問兩人${activity_unit}$的眾數分別為何？若有多個眾數，請由小到大以逗號分隔；若無眾數，請填寫 '無'。".replace("{name1}", name1).replace("{name2}", name2).replace("{item_activity}", item_activity).replace("{activity_unit}", activity_unit).replace("{data1_str}", data1_str).replace("{data2_str}", data2_str).replace("{time_unit}", time_unit)
            
            mode1_str = "無" if not mode1 else ", ".join(map(str, mode1))
            mode2_str = "無" if not mode2 else ", ".join(map(str, mode2))
            correct_answer = f"{mode1_str}, {mode2_str}"

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": "", # Empty for student's input
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(),
        "version": "1.0"
    }


    """
    Checks if the user's answer is correct against the generated correct answer.
    Handles numerical values, comma-separated lists, fractions, and the "無" keyword.
    """
    # 1. 清洗雙方輸入 (移除 LaTeX, 變數名, 空格, 單位)
    def clean_str(s):
        s = str(s).strip().replace(" ", "").lower()
        s = re.sub(r'^[a-z]+=', '', s) # Remove k=, x=, y=, ans=
        s = s.replace("$", "").replace("\\", "")
        # Remove common units or descriptive text that might be part of explanation but not value
        s = s.replace("小時", "").replace("分", "").replace("元", "").replace("塊", "").replace("本", "").replace("個", "").replace("張", "").replace("枝", "").replace("顆", "").replace("份", "").replace("約", "")
        return s
    
    u_cleaned = clean_str(user_answer)
    c_cleaned = clean_str(correct_answer)

    # If the entire correct_answer is "無" (e.g., for a single mode question with no mode)
    if c_cleaned == "無":
        return u_cleaned == "無"

    # Attempt to parse answers as comma-separated lists of numbers or "無"
    try:
        user_parts = [s.strip() for s in u_cleaned.split(',') if s.strip()]
        correct_parts = [s.strip() for s in c_cleaned.split(',') if s.strip()]

        if len(user_parts) != len(correct_parts):
            return False

        for u_part, c_part in zip(user_parts, correct_parts):
            if c_part == "無":
                if u_part != "無":
                    return False
            else:
                # Parse and compare numerical parts, supporting fractions
                u_val = None
                c_val = None
                
                def parse_num_from_str(num_str):
                    if "/" in num_str:
                        n, d = map(float, num_str.split('/'))
                        return n / d
                    return float(num_str)
                
                try:
                    u_val = parse_num_from_str(u_part)
                    c_val = parse_num_from_str(c_part)
                except ValueError:
                    # If a part expected to be a number cannot be parsed, it's incorrect
                    return False
                
                if not math.isclose(u_val, c_val, rel_tol=1e-5, abs_tol=1e-5):
                    return False
        
        return True # All parts match within tolerance
    except ValueError:
        # Catch any parsing errors (e.g., unexpected characters in number string)
        return False
    except Exception:
        # Catch any other unexpected errors during comparison
        return False


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
