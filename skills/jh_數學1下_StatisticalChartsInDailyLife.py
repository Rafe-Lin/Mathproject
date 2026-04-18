# ==============================================================================
# ID: jh_數學1下_StatisticalChartsInDailyLife
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 81.81s | RAG: 5 examples
# Created At: 2026-01-17 22:28:36
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
plt.rcParams['font.family'] = ['Microsoft JhengHei', 'sans-serif'] # Force fallback


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
import io
import base64

from datetime import datetime
import re
 # For check function

# Helper function to generate percentages that sum to 100, with a minimum value
def _generate_percentages(num_categories):
    if num_categories <= 1:
        return [100]

    min_percentage = 5
    if num_categories * min_percentage > 100:
        # This case should ideally be prevented by design (e.g., max num_categories = 20 for min_percentage = 5)
        # For typical 3-5 categories, this won't be an issue.
        raise ValueError(f"Cannot generate percentages for {num_categories} categories with minimum {min_percentage}% each.")

    percentages = [min_percentage] * num_categories
    remaining_to_distribute = 100 - (num_categories * min_percentage)

    # Distribute the remaining percentage randomly, one unit at a time
    for _ in range(remaining_to_distribute):
        idx = random.randint(0, num_categories - 1)
        percentages[idx] += 1
            
    random.shuffle(percentages) # Shuffle to randomize order
    return percentages

# Helper function to draw various chart types and return their base64 encoded image
def _draw_chart(chart_type, data, title, xlabel, ylabel, key_value=None, icon_type=None):
    plt.style.use('seaborn-v0_8-whitegrid') # Use a consistent style
    # Force font settings again inside function to be safe
    plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
    plt.rcParams['axes.unicode_minus'] = False
    
    # [V16.19 Ultra-High Resolution] Maximize figsize and DPI
    fig, ax = plt.subplots(figsize=(12, 8), dpi=400) 
    
    if chart_type == 'bar':
        categories, values = data
        bars = ax.bar(categories, values, color='skyblue')
        # Ultra Big Fonts
        ax.set_title(title, fontsize=22, fontweight='bold', pad=25)
        ax.set_xlabel(xlabel, fontsize=18, labelpad=15)
        ax.set_ylabel(ylabel, fontsize=18, labelpad=15)
        # Ensure x-tick labels have the correct font
        ax.set_xticklabels(categories, fontsize=16, fontproperties='Microsoft JhengHei')
        ax.tick_params(axis='x', rotation=45, labelsize=16)
        ax.tick_params(axis='y', labelsize=16)
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        # Add value labels on top of bars
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, yval + 0.5, str(yval), ha='center', va='bottom', fontsize=15, fontweight='bold')

    elif chart_type == 'pie':
        categories, percentages = data
        # Ensure percentages are floats for pie chart
        percentages_float = [float(p) for p in percentages]
        
        wedges, texts, autotexts = ax.pie(percentages_float, labels=categories, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors, textprops={'fontsize': 16})
        ax.set_title(title, fontsize=22, fontweight='bold', pad=25)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.setp(autotexts, size=16, weight="bold", color="white") # Make percentage labels white and bold
        plt.setp(texts, size=16, fontproperties='Microsoft JhengHei') # Adjust category label size and font

    elif chart_type == 'line':
        x_labels, y_values = data
        ax.plot(x_labels, y_values, marker='o', linestyle='-', color='coral', linewidth=3, markersize=10)
        ax.set_title(title, fontsize=22, fontweight='bold', pad=25)
        ax.set_xlabel(xlabel, fontsize=18, labelpad=15)
        ax.set_ylabel(ylabel, fontsize=18, labelpad=15)
        # Ensure x-tick labels have the correct font
        ax.set_xticks(range(len(x_labels)))
        ax.set_xticklabels(x_labels, rotation=45, fontsize=16, fontproperties='Microsoft JhengHei')
        ax.tick_params(axis='y', labelsize=16)
        ax.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        # Add value labels next to points
        for i, (x, y) in enumerate(zip(range(len(x_labels)), y_values)):
             ax.text(i, y + 1, str(y), ha='center', va='bottom', fontsize=15, fontweight='bold')

    elif chart_type == 'pictogram':
        categories, icon_counts = data
        ax.set_title(title, fontsize=22, fontweight='bold', pad=25)
        ax.set_xlim(-0.5, len(categories) - 0.5)
        # Add even more padding for icons in Pictogram
        ax.set_ylim(0, max(icon_counts) + 3) 
        ax.set_xticks(range(len(categories)))
        ax.set_xticklabels(categories, rotation=45, ha='right', fontsize=16, fontproperties='Microsoft JhengHei')
        ax.set_yticks([]) # No y-axis ticks for pictograms
        ax.set_ylabel(ylabel, fontsize=18, labelpad=15) # Still provide a y-axis label for context, even if no ticks
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(True)
        
        icon_map = {
            'car': '🚗', 'apple': '🍎', 'star': '⭐', 'book': '📚', 'person': '👤', 'tree': '🌳', 'heart': '❤️', 'flower': '🌸'
        }
        display_icon = icon_map.get(icon_type, '❓') # Default to a question mark if icon_type is unknown

        for i, count in enumerate(icon_counts):
            for j in range(count):
                # Larger icons and more spacing
                ax.text(i, j + 0.5, display_icon, ha='center', va='center', fontsize=26)
            ax.text(i, count + 1.0, f"({count * key_value} 個)", ha='center', va='bottom', fontsize=14, fontweight='bold') # Show total count for category
        
        # Add legend for the key - Big Fonts
        ax.text(0.02, 0.95, f"圖例: {display_icon} 代表 {key_value} 個", 
                transform=ax.transAxes, fontsize=16, verticalalignment='top', fontproperties='Microsoft JhengHei',
                bbox=dict(boxstyle='round,pad=0.5', fc='white', ec='gray', lw=1, alpha=0.8))
        
        plt.tight_layout()

    # Convert plot to base64
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', transparent=True, dpi=400) # Save with Ultra High DPI
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig) # Close the figure to free memory
    return img_base64

def generate(level=1):
    # Randomly select a problem type
    problem_type = random.choice([1, 2, 3, 4, 5])
    
    question_text = ""
    correct_answer = ""
    image_base64 = ""
    
    if problem_type == 1: # Type 1 (Maps to RAG Example 1): 長條圖數據讀取
        categories_pool = ['蘋果', '香蕉', '橘子', '葡萄', '草莓', '芒果', '梨子', '西瓜', '鳳梨', '芭樂']
        titles_pool = ['班級學生喜歡的水果', '某商店商品銷售量', '不同動物園的參觀人數', '某社團成員最愛運動']
        ylabels_pool = ['學生人數', '銷售量(個)', '參觀人數(人)', '人數']
        
        num_categories = random.randint(3, 5)
        categories = random.sample(categories_pool, num_categories)
        values = [random.randint(5, 30) for _ in range(num_categories)]
        
        question_category_idx = random.randint(0, num_categories - 1)
        question_category = categories[question_category_idx]
        
        title = random.choice(titles_pool)
        ylabel = random.choice(ylabels_pool)
        
        question_text = r"根據下方的長條圖，請找出喜歡" + question_category + r"的數量。"
        correct_answer = str(values[question_category_idx])
        
        image_base64 = _draw_chart('bar', (categories, values), title, '類別', ylabel)

    elif problem_type == 2: # Type 2 (Maps to RAG Example 2): 長條圖數據比較與總和
        categories_pool = ['鉛筆', '橡皮擦', '尺', '筆記本', '原子筆', '立可白', '剪刀', '膠水']
        titles_pool = ['文具店商品銷售數量', '某班級學生文具持有數量', '不同種類書籍的借閱次數']
        ylabels_pool = ['銷售數量(個)', '持有數量(個)', '借閱次數']
        
        num_categories = random.randint(3, 5)
        categories = random.sample(categories_pool, num_categories)
        values = [random.randint(10, 50) for _ in range(num_categories)]
        
        question_type = random.choice(['difference', 'total'])
        
        title = random.choice(titles_pool)
        ylabel = random.choice(ylabels_pool)
        
        if question_type == 'difference':
            idx1, idx2 = random.sample(range(num_categories), 2)
            category1 = categories[idx1]
            category2 = categories[idx2]
            question_text = r"根據下方的長條圖，請找出" + category1 + r"與" + category2 + r"的數量相差多少？"
            correct_answer = str(abs(values[idx1] - values[idx2]))
        else: # 'total'
            question_text = r"根據下方的長條圖，請找出所有類別的總數量。"
            correct_answer = str(sum(values))
            
        image_base64 = _draw_chart('bar', (categories, values), title, '類別', ylabel)

    elif problem_type == 3: # Type 3 (Maps to RAG Example 3): 圓形圖百分比計算
        categories_pool = ['房租', '伙食', '交通', '娛樂', '教育', '儲蓄', '醫療', '服飾']
        titles_pool = ['家庭每月開銷比例', '某公司員工部門分佈', '學生課餘活動時間分配', '某城市人口職業分佈']
        
        num_categories = random.randint(3, 5)
        categories = random.sample(categories_pool, num_categories)
        percentages = _generate_percentages(num_categories)
        
        total_value = random.randint(10, 50) * 100 # Ensure total is a multiple of 100 for easier calculation, and larger values
        
        question_category_idx = random.randint(0, num_categories - 1)
        question_category = categories[question_category_idx]
        
        title = random.choice(titles_pool)
        
        question_text = r"下圖顯示了某群體的圓形圖。如果總數為 $" + str(total_value) + r"$，請問屬於" + question_category + r"的數量是多少？"
        correct_answer = str(round(total_value * percentages[question_category_idx] / 100))
        
        image_base64 = _draw_chart('pie', (categories, percentages), title, '', '')

    elif problem_type == 4: # Type 4 (Maps to RAG Example 4): 折線圖趨勢判斷與數值讀取
        x_labels_pool_days = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
        x_labels_pool_months = ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月']
        titles_pool = ['某城市一週氣溫變化', '某產品每月銷售趨勢', '學生期中考試成績變化', '某股票每日收盤價']
        ylabels_pool = ['氣溫(°C)', '銷售量(單位)', '分數', '價格(元)']
        
        num_points = random.randint(5, 7)
        if random.choice([True, False]): # Randomly choose between days or months for x_labels
            x_labels = random.sample(x_labels_pool_days, num_points)
            x_labels.sort(key=x_labels_pool_days.index) # Keep order for days
            xlabel = '日期'
        else:
            x_labels = random.sample(x_labels_pool_months, num_points)
            x_labels.sort(key=x_labels_pool_months.index) # Keep order for months
            xlabel = '月份'

        y_values = [random.randint(10, 50) for _ in range(num_points)]
        
        question_type = random.choice(['read_value', 'find_max_min'])
        
        title = random.choice(titles_pool)
        ylabel = random.choice(ylabels_pool)
        
        if question_type == 'read_value':
            question_point_idx = random.randint(0, num_points - 1)
            question_label = x_labels[question_point_idx]
            question_text = r"根據下方的折線圖，請找出" + question_label + r"的數值。"
            correct_answer = str(y_values[question_point_idx])
        else: # 'find_max_min'
            choice = random.choice(['max', 'min'])
            if choice == 'max':
                max_value = max(y_values)
                # The question only asks for the value, not the label, to be consistent with `correct_answer`
                question_text = r"根據下方的折線圖，請找出數值最高的點的數值是多少？"
                correct_answer = str(max_value)
            else: # 'min'
                min_value = min(y_values)
                # The question only asks for the value, not the label
                question_text = r"根據下方的折線圖，請找出數值最低的點的數值是多少？"
                correct_answer = str(min_value)
                
        image_base64 = _draw_chart('line', (x_labels, y_values), title, xlabel, ylabel)

    elif problem_type == 5: # Type 5 (Maps to RAG Example 5): 象形圖數據解讀
        categories_pool = ['汽車', '機車', '腳踏車', '公車', '火車', '飛機']
        titles_pool = ['某工廠生產車輛數', '某超市水果銷售量', '學生最喜歡的動物', '班級投票結果']
        icon_types_pool = ['car', 'apple', 'star', 'book', 'person', 'tree', 'heart', 'flower']
        
        num_categories = random.randint(3, 4)
        categories = random.sample(categories_pool, num_categories)
        icon_counts = [random.randint(2, 8) for _ in range(num_categories)]
        key_value = random.choice([2, 5, 10])
        
        question_type = random.choice(['total', 'difference'])
        
        title = random.choice(titles_pool)
        icon_type = random.choice(icon_types_pool)
        
        if question_type == 'difference':
            idx1, idx2 = random.sample(range(num_categories), 2)
            category1 = categories[idx1]
            category2 = categories[idx2]
            question_text = r"根據下方的象形圖，請找出" + category1 + r"與" + category2 + r"的數量相差多少？"
            correct_answer = str(abs(icon_counts[idx1] - icon_counts[idx2]) * key_value)
        else: # 'total'
            question_text = r"根據下方的象形圖，請找出所有類別的總數量。"
            correct_answer = str(sum(icon_counts) * key_value)
            
        image_base64 = _draw_chart('pictogram', (categories, icon_counts), title, '類別', '數量', key_value, icon_type)

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": "",
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(),
        "version": "1.0.0"
    }






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
