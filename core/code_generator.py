# -*- coding: utf-8 -*-
"""
=============================================================================
模組名稱 (Module Name): core/code_generator.py
功能說明 (Description): 數學題目生成腳本的核心引擎，負責生成、驗證、修復 Python 程式碼，並包含標準數學工具庫 (Perfect Utils) 的注入與程式碼安全防護。
執行語法 (Usage): 由系統調用
版本資訊 (Version): V2.0
更新日期 (Date): 2026-01-13
維護團隊 (Maintainer): Math AI Project Team
=============================================================================
"""
# ==============================================================================

import os
import re
import sys
import io
import time
import ast
import random
import importlib
from datetime import datetime  # [核心修復] 補齊遺失的 datetime
import psutil                 # [數據強化] CPU/RAM 監控
try:
    import GPUtil             # [數據強化] GPU 監控
except ImportError:
    GPUtil = None

def get_system_snapshot():
    """獲取當前環境的真實硬體數據"""
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    gpu, gpuram = 0.0, 0.0
    if GPUtil:
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0].load * 100
                gpuram = gpus[0].memoryUtil * 100
        except:
            pass
    return cpu, ram, gpu, gpuram

def categorize_error(error_msg):
    """根據錯誤訊息進行自動分類 [V9.9.9 Precision]"""
    if not error_msg or error_msg == "None": return None
    err_low = error_msg.lower()
    if "syntax" in err_low: return "SyntaxError"
    if "list" in err_low: return "FormatError"
    return "RuntimeError"
from pyflakes.api import check as pyflakes_check
from pyflakes.reporter import Reporter
from flask import current_app
from core.ai_wrapper import get_ai_client
from models import db, SkillInfo, TextbookExample, ExperimentLog, SkillGenCodePrompt
from config import Config



# ==============================================================================
# --- Perfect Utils (Standard Math Tools v3.1) ---
# Description: The "Standard Library" injected into every generated skill.
# ==============================================================================
PERFECT_UTILS = r'''
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
'''

def inject_perfect_utils(code_str):
    # [V16.0 強力清掃] 擴大刪除範圍，確保不留下任何「孤兒縮進」
    # 只要偵測到 AI 試圖寫 patch 或 checker，就把該區塊連根拔起
    patterns = [
        r'def\s+_patch_all_returns\(.*?\):.*?(?=\n\S|$)',
        r'def\s+check\(user_answer, correct_answer\):.*?(?=\n\S|$)',
        r'for _name, _func in list\(globals\(\)\.items\(\)\):.*'
    ]
    for pat in patterns:
        code_str = re.sub(pat, '', code_str, flags=re.DOTALL | re.MULTILINE)
    
    # 移除重複的 import
    code_str = code_str.replace("import random", "").replace("import math", "")
    
    return PERFECT_UTILS + "\n" + code_str


# ==============================================================================
# UNIVERSAL SYSTEM PROMPT (v9.2 Optimized - Lean & Powerful)
# 結合了「規則防護」與「範例引導」，用最少的 Token 達到最強的約束力
# ==============================================================================

UNIVERSAL_GEN_CODE_PROMPT = r"""
You are a Senior Python Developer (V14.0 Professional Guard).

### ⛔ 系統底層鐵律 (不可違背):
## [CRITICAL CODING STANDARDS: Verification & Stability]

1. **閱卷決定論 (Deterministic Grading)**：
   - `check(user_answer, correct_answer)` 函式 **嚴禁** 呼叫任何 `random` 模組或重新執行 `generate` 邏輯。
   - `check` 函式必須完全依賴傳入的 `correct_answer` 參數作為唯一的真理來源 (Source of Truth)。

2. **通用 Check 函式模板 (Universal Check Template)**：
   - 除非有特殊幾何需求，否則所有數值/代數題型必須實作包含以下邏輯的 `check` 函式：
     ```python
     def check(user_answer, correct_answer):
         import re, math
         def clean(s):
             s = str(s).strip().replace(" ", "").lower()
             return re.sub(r'[\$\s\(\)\{\}\[\]\\a-zA-Z=,;:\u4e00-\u9fff]', '', s) # 保留數字與小數點

         # [V18.13 Update] 支援中英文是非題互通
         u_str = str(user_answer).strip()
         c_str = str(correct_answer).strip()
         
         yes_group = ["是", "Yes", "TRUE", "True", "1", "O", "right"]
         no_group = ["否", "No", "FALSE", "False", "0", "X", "wrong"]
         
         if c_str in yes_group:
             return {"correct": u_str in yes_group, "result": "正確！" if u_str in yes_group else "答案錯誤"}
         if c_str in no_group:
             return {"correct": u_str in no_group, "result": "正確！" if u_str in no_group else "答案錯誤"}

         # 3. 數值與字串比對
         try:
             # 解析分數與浮點數
             def parse(v):
                if "/" in v: return float(v.split("/")[0]) / float(v.split("/")[1])
                return float(v)
             
             u_val = parse(clean(u_str))
             c_val = parse(clean(c_str))
             if math.isclose(u_val, c_val, rel_tol=1e-5):
                 return {"correct": True, "result": "正確！"}
         except:
             pass
             
         if u_str == c_str: return {"correct": True, "result": "正確！"}
         return {"correct": False, "result": f"答案錯誤。"}
     ```

3. **數據傳遞完整性**：
   - 在 `generate()` 函式中，如果答案是一個複雜物件（如座標點），`correct_answer` 必須序列化為易於解析的格式（如 JSON string 或 CSV），而不是自然語言描述。

1. **方程式生成鎖死 (Equation Robustness)**:
   - 嚴禁使用 f-string 組合 `ax + by = c`。
   - 【強制流程】：必須分別判定 a, b 的正負與是否為 1，手動組合字串片段後合併。
   - 範例：`parts = []; if a==1: parts.append("x"); ... eq_str = "".join(parts) + " = " + str(c)`。

2. **視覺絕對淨化 (Zero-Graph Protocol)**:
   - 針對「判斷點是否在直線上」題型，`image_base64` 【嚴禁包含任何線段或點】。
   - 僅提供 1x1 的淺灰色網格、座標軸與原點 '0'。

3. **LaTeX 單層大括號**:
   - 所有的 \frac 必須使用 `r"\frac{n}{d}"` 結構，嚴禁出現 `{{ }}`。
   - 所有的變數代換必須使用 `.replace("{n}", str(val))`。

4. **閱卷與反饋**:
   - check(u, c) 僅限回傳 True/False。
   - 系統 Patch 會自動移除 $ 與 \ 符號。

5. **座標精度**: 座標值僅限整數或 0.5。

6. **強制顯示刻度 (Mandatory Axis Ticks)**：
   - 在使用 `matplotlib` 繪製數線 (Number Line) 或直角座標系 (Coordinate System) 時，**嚴禁**使用預設刻度。
   - **必須** 顯式呼叫 `set_xticks` 和 `set_yticks` 來強制顯示整數數字。
   - **程式碼範例**：
     ```python
     # 正確寫法：強制標示範圍內的所有整數
     import numpy as np
     x_range = range(min_val, max_val + 1)
     ax.set_xticks(x_range)
     ax.set_yticks(x_range)
     # 避免數字重疊，可視情況設定 fontsize
     ax.tick_params(axis='both', which='major', labelsize=12)
     ```

7. **座標軸優化 (Axis Visibility)**：
   - 確保 X 軸與 Y 軸的 `spines` 位置正確（通常在 `center` 或 `zero`）。
   - 務必檢查 `ax.spines['left'].set_position('zero')` 和 `ax.spines['bottom'].set_position('zero')` 後，刻度數字不會被遮擋。

8. **網格線輔助 (Grid Lines)**：
   - 對於讀圖題，必須開啟 `ax.grid(True, linestyle=':', alpha=0.6)` 以輔助學生對齊數值。

9. **主題一致性防護 (Topic Integrity)**：
   - 在生成邏輯之前，檢查 `skill_id` 是否包含特定數學領域（如 `Distributive`、`Polynomial`、`Factorization`）。
   - **複雜度門檻**：若 ID 屬於國二以上 (2上, 2下, 3上...)，**嚴禁**生成僅涉及小學或國一程度的單步驟算術題。
   - **強制特徵**：
     - 乘法公式單元：必須包含平方、變數 $(x, y)$ 或特定數字結構 (如 $99^2$)。
     - 幾何單元：必須包含圖形繪製或角度/面積計算。

10. **函式完整性 (Function Definition Integrity)**:
    - CRITICAL: When implementing the `check` function, YOU MUST explicitly write the line `def check(user_answer, correct_answer):`. Do not just start writing the inner logic or comments.

12. **Boolean/Yes-No Standardization**:
   - For any "Yes/No" or "True/False" question, the `correct_answer` MUST be the Chinese character **"是"** or **"否"**.
   - DO NOT use "1", "0", "True", "False".
"""


def infer_model_tag(model_name):
    """
    根據模型名稱自動判斷 V9 架構師的分級 (Model Tag)。
    支援 Qwen, DeepSeek, Phi, Llama 等常見模型。
    """
    name = model_name.lower()
    
    # 1. Cloud Models
    if any(x in name for x in ['gemini', 'gpt', 'claude']): return 'cloud_pro'
    
    # 2. Local Large/Medium (>= 10B)
    # DeepSeek 默認視為強邏輯模型，歸類在 local_14b (除非顯式標註 7b/8b)
    if '70b' in name or '32b' in name or '14b' in name: return 'local_14b'
    if 'deepseek' in name and not any(x in name for x in ['1.5b', '7b', '8b']): return 'local_14b'
    if 'qwen' in name and not any(x in name for x in ['0.5b', '1.5b', '3b', '7b']): return 'local_14b'
    
    # 3. Local Small/Edge (< 10B)
    if 'phi' in name or '7b' in name or '8b' in name: return 'edge_7b'
    
    # Default Fallback
    return 'local_14b'


# ==============================================================================
# --- Dispatcher Injection (v8.7 Level-Aware) ---
# ==============================================================================
def inject_robust_dispatcher(code_str):
    if re.search(r'^def generate\s*\(', code_str, re.MULTILINE):
        return code_str 
    
    # 搜尋所有 generate_ 開頭的函式
    candidates = re.findall(r'^def\s+(generate_[a-zA-Z0-9_]+)\s*\(', code_str, re.MULTILINE)
    valid_funcs = [f for f in candidates if f not in ['generate', 'check', 'solve', 'to_latex', 'fmt_num']]
    
    if not valid_funcs: return code_str
    
    # Heuristic Split: First half -> Level 1, Second half -> Level 2
    mid_point = (len(valid_funcs) + 1) // 2
    level_1_funcs = valid_funcs[:mid_point]
    level_2_funcs = valid_funcs[mid_point:] if len(valid_funcs) > 1 else valid_funcs

    dispatcher_code = "\n\n# [Auto-Injected Smart Dispatcher v8.7]\n"
    dispatcher_code += "def generate(level=1):\n"
    dispatcher_code += f"    if level == 1:\n"
    dispatcher_code += f"        types = {str(level_1_funcs)}\n"
    dispatcher_code += f"        selected = random.choice(types)\n"
    dispatcher_code += f"    else:\n"
    
    if level_2_funcs:
        dispatcher_code += f"        types = {str(level_2_funcs)}\n"
        dispatcher_code += f"        selected = random.choice(types)\n"
    else:
        dispatcher_code += f"        types = {str(level_1_funcs)}\n"
        dispatcher_code += f"        selected = random.choice(types)\n"

    for func in valid_funcs:
        dispatcher_code += f"    if selected == '{func}': return {func}()\n"
    
    dispatcher_code += f"    return {valid_funcs[0]}()\n"
    return code_str + dispatcher_code


def fix_return_format(code_str):
    pattern = r'(^\s*)return\s+(f["\'].*?["\'])\s*,\s*(\[.*?\])\s*$'
    def repl(m):
        return f"{m.group(1)}return {{'question_text': {m.group(2)}, 'answer': str({m.group(3)}[0]), 'correct_answer': str({m.group(3)}[0])}}"
    return re.sub(pattern, repl, code_str, flags=re.MULTILINE)


def universal_function_patcher(code_content):
    total_fixes = 0
    # 1. 找出所有以 draw_ 開頭的函式定義區塊
    # 正則表達式：尋找 def draw_...(): 到下一個 def 或 檔案結尾
    func_blocks = re.finditer(r'def (draw_[a-zA-Z0-9_]+)\(.*?\):(.*?)(\n(?=def)|$)', code_content, re.DOTALL)
    
    for match in func_blocks:
        func_name = match.group(1)
        func_body = match.group(2)
        
        # 2. 如果函式內有賦值給常見的「結果變數」，但沒有 return
        target_vars = ['result', 'html', 'fig_str', 'output', 'svg_data']
        needs_fix = any(f"{v} =" in func_body for v in target_vars) and "return" not in func_body
        
        if needs_fix:
            # 找到最後一個賦值的變數名稱
            found_var = next(v for v in target_vars if f"{v} =" in func_body)
            # 自動在函式末尾補上 return
            lines = func_body.splitlines()
            last_indent = "    "
            if lines:
                # Find last non-empty line to determine indentation or just blindly ensure 4 spaces
                # Better strategy: use the indentation of the last line of the body if available
                # But here we will follow the user provided logic which seemed to copy indentation
                for line in reversed(lines):
                     if line.strip():
                         last_indent = line[:len(line) - len(line.lstrip())]
                         break
            
            patched_body = func_body.rstrip() + f"\n{last_indent}return {found_var}\n"
            code_content = code_content.replace(func_body, patched_body)
            total_fixes += 1
            print(f"   🔧 [Universal-Fix] Patched missing return in {func_name}.")
            
    return code_content, total_fixes


def clean_global_scope_execution(code_str):
    lines = code_str.split('\n')
    cleaned = []
    for line in lines:
        s = line.strip()
        if (s.startswith("print(") or s.startswith("generate(")) and "def " not in code_str: 
            continue
        cleaned.append(line)
    return '\n'.join(cleaned)


def load_gold_standard_example():
    try:
        path = os.path.join(current_app.root_path, 'skills', 'Example_Program.py')
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f: return f.read()
    except Exception as e:
        print(f"⚠️ Warning: Could not load Example_Program.py: {e}")
    return "def generate_type_1_problem(): return {}"


def fix_missing_answer_key(code_str):
    """[V10.3.1] 增加換行修復、回傳格式強化與全面中文化反饋"""
    patch_code = r"""
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
                # 解決 r-string 導致的 \\n 問題
                res['question_text'] = re.sub(r'\\n', '\n', res['question_text'])
            
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
                res['question_text'] = res['question_text'].rstrip() + "\\n(請在手寫區作答!)"

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
"""
    return code_str + patch_code

# ==============================================================================
# --- THE REGEX ARMOR (v8.7.3 - Full Math Protection) ---
# ==============================================================================
def fix_code_syntax(code_str, error_msg=""):
    fixed_code = code_str
    total_fixes = 0
    
    # 1. 基礎反斜線修復 (Regex Armor)
    fixed_code = re.sub(r'(?<!\\)\\ ', r'\\\\ ', fixed_code)
    fixed_code = re.sub(r'(?<!\\)\\u(?![0-9a-fA-F]{4})', r'\\\\u', fixed_code)

    # 2. [智慧冪等修復] 僅在缺失 \begin 時補全 cases
    lines = fixed_code.split('\n')
    cleaned_lines = []
    for line in lines:
        # IME 全形自癒：抹除行末非法標點
        line = re.sub(r'[。，；：]\s*$', '', line)
        if not re.search(r'["\']', line):
            line = line.replace('，', ',').replace('；', ';').replace('：', ':')
        
        # LaTeX cases 安全網：防止 \begin{\\begin{cases}}
        if "{cases}" in line and "\\begin{cases}" not in line:
            line = line.replace("{cases}", "\\\\begin{cases}")
            total_fixes += 1
        
        # 指數保護
        line = re.sub(r'\^\{(?!\{)(.*?)\}(?!\})', r'^{{{\1}}}', line)
        cleaned_lines.append(line)
        
    return '\n'.join(cleaned_lines), total_fixes


def validate_and_fix_code(code_content):
    """
    [V10.2 Pure] 採用「隔離注入」與「字典封裝」策略。
    解決引號不對稱 (SyntaxError) 與 500 錯誤。
    """
    total_fixes = 0
    
    # =========================================================
    # 防線 A: [V18.9] 雙錢號清洗 (Double Dollar Cleanup)
    # 解決截圖中出現 "$$0.64" 導致的排版錯誤
    # 強制將所有 "$$" 替換為單個 "$"
    # =========================================================
    if "$$" in code_content:
        code_content = code_content.replace("$$", "$")
        total_fixes += 1
        print("   🔧 [Format-Fix] Removed double dollar signs ($$ -> $).")

    # =========================================================
    # 防線 B: [V18.9] Check 函式環境隔離修復 (Scope Injection)
    # 解決 "cannot access local variable 'math'" 錯誤
    # 強制在 def check(...): 的下一行注入 import math, random, re
    # =========================================================
    if "def check(" in code_content:
        # 使用 Regex 尋找 def check(...) 及其換行
        pattern = r"(def\s+check\s*\(.*?\):\s*\n)"
        match = re.search(pattern, code_content)
        if match:
            # 檢查下一行是否已經有 import
            next_lines = code_content[match.end():match.end()+50]
            if "import math" not in next_lines:
                # 假設標準縮排為 4 空格
                injection = "    import math, random, re\n"
                code_content = code_content[:match.end()] + injection + code_content[match.end():]
                total_fixes += 1
                print("   🔧 [Scope-Fix] Injected local imports into check().")

    # =========================================================
    # 防線 C: [V18.9] LaTeX 跳脫字元修復 (Escape Char Fix)
    # 解決 f"$\angle" 被轉義為響鈴字元的問題
    # =========================================================
    latex_keywords = ['angle', 'triangle', 'frac', 'sqrt', 'times', 'div', 'pm', 'approx', 'circ']
    for kw in latex_keywords:
        # 尋找單反斜線 + 關鍵字 (排除已經是雙反斜線的情況)
        # Regex: f" ... \keyword ... "
        pattern = r'(f["\'].*?)(?<!\\)\\' + kw + r'(.*?["\'])'
        while re.search(pattern, code_content):
            code_content = re.sub(pattern, r'\1\\\\' + kw + r'\2', code_content)
            total_fixes += 1
    
    if total_fixes > 0:
        print(f"   🛡️ [Auto-Heal] Applied {total_fixes} critical fixes.")

    # --- [V10.2] 隔離注入：使用 r-string 三引號保護補丁 ---
    if ("matplotlib" in code_content or "Figure" in code_content) and "font.sans-serif" not in code_content:
        font_style_patch = r'''
# [V10.2 Elite Font & Style]
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
plt.rcParams['axes.unicode_minus'] = False

def _apply_v10_visual_style(ax):
    ax.set_xticks([0])
    for tick in ax.get_xticklabels():
        tick.set_fontsize(18); tick.set_fontweight('bold')
    ax.set_title(""); ax.set_xlabel("")
'''
        # 放在最頂部，避開後續 Regex 掃描
        code_content = font_style_patch + "\n" + code_content
        total_fixes += 1

    # [V10.6.2 Elite] 針對字體設定行的「全方位引號對齊」手術
    # 增加對 matplotlib.rcParams, plt.rcParams 與 rcParams 的全面支援
    font_conf_pattern = r"(?:matplotlib\.|plt\.)?rcParams\[['\"]font\.sans-serif['\"]\]\s*=\s*\[['\"]Microsoft JhengHei['\"]\]"
    replacement = "plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']"
    
    # 執行置換並精確統計修復次數
    code_content, f_count = re.subn(font_conf_pattern, replacement, code_content)
    total_fixes += f_count
    
    if f_count > 0:
        print(f"   🔧 [Font-Fix] Aligned quotes in matplotlib config ({f_count} lines).")

    # --- [V10.2] 答案驗證格式自癒 ---
    # 如果 AI 寫了裸露的 return True/False，自動包裝並加入正確答案顯示



    # LaTeX 精確修復 (避開 \n)
    def smart_fix(match):
        nonlocal total_fixes
        c = match.group(1)
        if re.search(r'\\[a-zA-Z]+', c) and not re.search(r'^\\n', c) and "{" in c and "{{" not in c:
            if not re.search(r'\{[a-zA-Z_][a-zA-Z0-9_]*\}', c):
                total_fixes += 1
                return f'f"{c.replace("{", "{{").replace("}", "}}")}"'
        return f'f"{c}"'
    
    code_content = re.sub(r'f"(.*?)"', smart_fix, code_content)
    code_content = re.sub(r"f'(.*?)'", smart_fix, code_content)
    
    # [新增] 偵測過度轉義的 Python 變數 (例如 {{ans}})
    # 這通常是 AI 被 LaTeX 規則搞混的結果
    over_escaped_pattern = r'f".*?\{\{[a-zA-Z_][a-zA-Z0-9_]*\}\}.*?"'
    matches = re.findall(over_escaped_pattern, code_content)
    if matches:
        # 將 {{var}} 修正為 {var}
        for m in matches:
            fixed = m.replace("{{", "{").replace("}}", "}")
            code_content = code_content.replace(m, fixed)
            total_fixes += 1 # 這下子實驗數據就不會是 0 了！
    
    # =========================================================
    # 防線 3：變數名稱防呆 (防止 Target_val 錯誤)
    # =========================================================
    if "return {" in code_content and "target_val" in code_content:
         if "target_val =" not in code_content and "ans =" in code_content:
             code_content = code_content.replace("str(target_val)", "str(ans)")
             total_fixes += 1

    # =========================================================
    # 防線 4：[V18.4] 函式定義遺失自癒 (Missing Def Auto-Recovery)
    # 針對 AI 輸出 def check 內容但遺漏 def check(...) 這一行的情況
    # =========================================================
    # 偵測特徵：縮排的 u = clean(...) 或 def clean(s): 但上方沒有 def check
    # 這裡我們尋找一個常見的 check 內部特徵
    check_internal_signatures = [
        r'^\s{4}def clean\(s\):',
        r'^\s{4}u = clean\(user_answer\)',
        r'^\s{4}c = clean\(correct_answer\)',
        r'^\s{4}def _clean\(s\):',
    ]
    
    has_check_def = re.search(r'^def check\(user_answer, correct_answer\):', code_content, re.MULTILINE)
    has_internal_logic = any(re.search(sig, code_content, re.MULTILINE) for sig in check_internal_signatures)
    
    if has_internal_logic and not has_check_def:
        # 找到第一個類似 check 內部的邏輯行，並在其上方插入 def check
        # 為了安全起見，我們直接在程式碼最後面尋找孤兒縮排區塊的頂部有點困難，
        # 但通常這種錯誤發生時，程式碼會從縮排開始。
        # 策略：如果發現有縮排的 clean 函式且沒有 check，嘗試包裹。
        # 但更簡單的方式是：如果確定沒有 check 但有 check 的特徵，直接把 def check 補在最前面？不，這可能會亂。
        # 我們假設 AI 是接著 generate 之後寫的。
        
        # 掃描每一行，如果發現一行是縮排的 def clean(s):，且往上找非空行不是 def check，則插入
        lines = code_content.split('\n')
        new_lines = []
        inserted = False
        for i, line in enumerate(lines):
            # 檢查是否為 check 內部的關鍵特徵行
            is_feature = any(re.match(sig, line) for sig in check_internal_signatures)
            
            if is_feature and not inserted:
                # 往回找最近的非空行
                prev_idx = len(new_lines) - 1
                while prev_idx >= 0 and not new_lines[prev_idx].strip():
                    prev_idx -= 1
                
                # 如果前一行不是以 def check 開頭
                if prev_idx < 0 or not new_lines[prev_idx].strip().startswith("def check"):
                     # 插入 def check
                     new_lines.append("def check(user_answer, correct_answer):")
                     total_fixes += 1
                     print(f"   [Critical-Fix] Auto-injected missing 'def check' definition.")
                     inserted = True # 避免重複插入
            
            new_lines.append(line)
        
        if inserted:
            code_content = "\n".join(new_lines)


    return code_content, total_fixes


# ==============================================================================
# --- Generator Pipeline ---
# ==============================================================================
def validate_python_code(code_str):
    try: ast.parse(code_str); return True, None
    except SyntaxError as e: return False, f"{e.msg} (Line {e.lineno})"
    except Exception as e: return False, str(e)


def validate_logic_with_pyflakes(code_str):
    log_stream = io.StringIO(); reporter = Reporter(log_stream, log_stream)
    pyflakes_check(code_str, "generated_code", reporter)
    error_log = log_stream.getvalue()
    return "undefined name" not in error_log.lower(), error_log


def fix_logic_errors(code_str, error_log):
    """
    [V9.8 Upgrade] Returns (fixed_code, fix_count)
    """
    fixed_code = code_str
    undefined_vars = set(re.findall(r"undefined name ['\"](\w+)['\"]", error_log))
    
    imports = []
    fix_count = 0
    
    for var in undefined_vars:
        if var in ['random', 'math']: 
            imports.append(f"import {var}")
            fix_count += 1
        if var == 'Fraction': 
            imports.append("from fractions import Fraction")
            fix_count += 1
            
    if imports: 
        fixed_code = "\n".join(imports) + "\n" + fixed_code
        
    return fixed_code, fix_count


def log_experiment(skill_id, start_time, input_len, output_len, success, error_msg, repaired, 
                   actual_model_name="Unknown", actual_provider="google",
                   regex_fixes=0, logic_fixes=0, prompt_tokens=0, completion_tokens=0, 
                   prompt_version=1, strategy="Standard", raw_output_len=0, utils_len=0):
    """
    [V9.9.9 最終修正版] 解決重複參數問題，確保數據精確入庫。
    """
    try:
        duration = time.time() - start_time
        cpu, ram, gpu, gpuram = get_system_snapshot() # 真實硬體監控
        
        # 錯誤分類邏輯
        err_cat = None
        if error_msg and error_msg != "None":
            err_low = error_msg.lower()
            if "syntax" in err_low: err_cat = "SyntaxError"
            elif "list" in err_low: err_cat = "FormatError"
            elif "attribute" in err_low: err_cat = "StructureError"
            else: err_cat = "RuntimeError"

        log = ExperimentLog(
            timestamp=datetime.now(), # 確保頂部有 from datetime import datetime
            skill_id=skill_id,
            ai_provider=actual_provider,
            model_name=actual_model_name,
            duration_seconds=round(duration, 2),
            input_length=input_len,
            raw_output_length=raw_output_len,   # AI 產出的真實純度
            perfect_utils_length=utils_len,     # 系統注入的工具庫長度
            output_length=output_len,           # 最終存檔總長度
            is_success=success,
            syntax_error_initial=str(error_msg)[:500] if error_msg else None,
            error_category=err_cat,
            ast_repair_triggered=repaired,
            experiment_batch=getattr(Config, 'EXPERIMENT_BATCH', 'Run_V2.5_Elite'),
            prompt_strategy=strategy,
            prompt_version=prompt_version,
            regex_fix_count=regex_fixes,
            logic_fix_count=logic_fixes,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            code_complexity=raw_output_len // 40, # [Refined] Reflects AI logic only
            cpu_usage=cpu,
            ram_usage=ram,
            gpu_usage=gpu,
            gpuram_usage=gpuram
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"🚨 Experiment Log 寫入失敗: {e}")


def auto_generate_skill_code(skill_id, queue=None):
    start_time = time.time()
    
    # 1. Determine Target Tag based on Config
    role_config = Config.MODEL_ROLES.get('coder', Config.MODEL_ROLES.get('default'))
    current_model = role_config.get('model', 'Unknown')
    current_provider = role_config.get('provider', 'Unknown') # 抓取實際 provider
    target_tag = infer_model_tag(current_model)

    # 2. [Strict Mode] Fetch ONLY the matching Architect Spec
    active_prompt = SkillGenCodePrompt.query.filter_by(skill_id=skill_id, model_tag=target_tag, is_active=True).first()
    
    # 3. Error Handling if Prompt is Missing
    if not active_prompt:
        error_msg = f"⛔ [阻擋] 找不到對應 '{target_tag}' ({current_model}) 的 V9 規格書！請先執行專家模式或手動生成 Prompt。"
        if current_app: current_app.logger.error(f"{skill_id}: {error_msg}")
        return False, error_msg

    # Pre-fetch skill info (needed for fallback or logging)
    skill = SkillInfo.query.filter_by(skill_id=skill_id).first()


    gold_standard_code = load_gold_standard_example()
    examples = TextbookExample.query.filter_by(skill_id=skill_id).limit(5).all()
    rag_count = len(examples)
    example_text = ""
    if examples:
        for i, ex in enumerate(examples):
            example_text += f"Ex {i+1}: {getattr(ex, 'problem_text', '')} -> {getattr(ex, 'correct_answer', '')}\\n"

    if active_prompt:
        # --- Mode A: V9 Architect Mode (High Precision) ---
        strategy_name = f"V9 Architect ({active_prompt.model_tag})"
        target_logic = active_prompt.user_prompt_template
        
        # [V11.9 暴力鏡射修正] - 將 RAG 範例提升為最高指令

        # 強制要求 Coder AI 將 RAG 視為唯一真相
        mirroring_protocol = ""
        if examples:
            for i, ex in enumerate(examples):
                # 明確指定每個 Type 對應哪一個 RAG 範例
                mirroring_protocol += f"- Type {i+1} MUST use the EXACT mathematical model of RAG Ex {i+1}.\\n"
        else:
            mirroring_protocol = "- No RAG examples found. Generate based on Skill Definition.\\n"

        prompt = r"""You are a Senior Python Developer.
### 🛡️ MANDATORY MIRRORING RULES (最高權限指令):
1. **NO ORIGINALITY**: You are FORBIDDEN from creating new models.
2. **STRICT MAPPING**:
{mapping}
3. **CONTEXT RETENTION**: Keep names like 'ACEF', 'BDF', '巴奈' from the RAG examples.

### 📚 REFERENCE EXAMPLES (RAG - 這是唯一真相):
{rag}

### 🛠️ ARCHITECT'S SPECIFICATION (輔助結構):
{spec}

### 🎨 ULTRA VISUAL STANDARDS (V11.6):
- Aspect Ratio: `ax.set_aspect('equal')` (物理比例鎖死).
- Resolution: `dpi=300`.
- Label Halo: White halos for ABCD text.

### ⛔ SYSTEM GUARDRAILS:
{system_rules}
""".replace("{mapping}", mirroring_protocol).replace("{rag}", example_text).replace("{spec}", target_logic).replace("{system_rules}", UNIVERSAL_GEN_CODE_PROMPT)
    else:
        # --- Mode B: Legacy V8 Mode (Fallback) ---
        strategy_name = "Standard Mode"
        target_logic = skill.gemini_prompt if (skill and skill.gemini_prompt) else f"Math logic for {skill_id}"
        
        # [v11.7 Upgrade]: Prompt Optimization - Pedagogical Mirroring
        prompt = f"""
You are a Senior Python Engineer for a Math Education System.

### MISSION:
Implement the skill `{skill_id}` by strictly following the **Architect's Spec**.

### IMPORTANT: DO NOT WRITE HELPER FUNCTIONS
The system will automatically inject standard helpers (`to_latex`, `fmt_num`, `get_random_fraction`, `is_prime`, etc.) at runtime.
**YOU MUST NOT DEFINE THEM.** Just use them directly.

### REFERENCE STRUCTURE (GOLD STANDARD v3.0):
```python
import random
import math
from fractions import Fraction

# (Helpers are auto-injected here, do not write them)

def generate_type_1_problem():
    val = get_random_fraction()
    # Question needs LaTeX wrapping:
    q = f"What is ${{to_latex(val)}}?"
    # Answer MUST be clean (NO $ signs):
    a = to_latex(val) 
    return {{'question_text': q, 'answer': a, 'correct_answer': a}}

def generate(level=1):
    # Dispatcher logic
    ...
ARCHITECT'S SPECIFICATION: {target_logic}

### REFERENCE EXAMPLES (RAG):
{example_text}

### 💡 INSTRUCTION:
Your task is to dynamize (Dynamize) the following examples into Python code, strictly adhering to their mathematical models.

### 🛡️ PEDAGOGICAL PRIORITY PROTOCOL (V11.7):
1. **Type 1 - Textbook Mirroring (Mirror Mode)**:
   - You MUST generate `generate_type_1` by strictly mirroring the first RAG example.
   - **NO ORIGINALITY**: Use the EXACT same mathematical model. ONLY Randomize the numbers.
   - **Context**: Keep keywords like "Aquarium", "Ticket". Do not change context.

2. **Data Linkage (Integer Guarantee)**:
   - For Reverse Calculation problems, generate the integer ANSWER first, then derive the question parameters.

CODING RULES:

1. **NO HELPERS**: Do NOT define `to_latex`, `fmt_num`, `check`, etc. They are auto-injected. Use them directly.

2. **Smart Dispatcher**: Implement `def generate(level=1):` to handle difficulty levels.
   - **[重要：函式命名規範]** 不論題目類型為何，主生成函式必須統一命名為 `generate()`。
   - 禁止使用 `generate_number_line()` 或 `generate_logic()` 等自定義名稱。
   - 如果有繪圖輔助函式（如 `draw_graph`），請在 `generate()` 函式內部呼叫它。
   - 必須確保檔案中存在 `def generate():` 和 `def check(user_answer, correct_answer):`。

3. **LaTeX Formatting (CRITICAL)**: 
   - All mathematical expressions (integers, fractions, equations) in `question_text` MUST be wrapped in single dollar signs `$`.
   - Example: `f"計算 ${fmt_num(a)} + {fmt_num(b)}$ 的值"` -> "計算 $3 + 5$ 的值".
   - **NO BACKTICKS**: Never use backticks (`) to wrap numbers or lists. BAD: `[1, 2]`. GOOD: $1, 2$.

4. **Answer Format Hint (CRITICAL)**:
   - You **MUST** append a clear format hint at the very end of `question_text`.
   - Format: `\\n(答案格式：...)`.
   - Example 1 (Values): `... \\n(答案格式：請填寫整數)` or `... \\n(答案格式：最簡分數)`.
   - Example 2 (Variables): `... \\n(答案格式：x=_, y=_)` (This ensures specific ordering).
   - Example 3 (Coordinates): `... \\n(答案格式：(x,y))`.

5. **Return Keys**: Return dict with keys: `'question_text'`, `'answer'`, `'correct_answer'`.
   - `correct_answer`: Must be a clean string for checking (e.g., "-5", "3/4", "x=2, y=3"). 
   - Do NOT use LaTeX (`$`) in `correct_answer` or `answer` keys, as this makes user input matching difficult. Keep it raw text.

6. **Language**: Traditional Chinese (Taiwan) ONLY (繁體中文). Use local terminology (e.g., 座標, 聯立方程式).

7. **Level Completeness**: Implement both Level 1 (Basic) and Level 2 (Advanced/Applied).

OUTPUT: Return ONLY the Python code. Start with `import random`.

[防呆輸出要求] 在 Python 檔案的最末尾，請務必包含以下代碼，確保進入點相容性：
```python
# 確保主進入點存在 (別名掛載)
if 'generate' not in globals() and any(k.startswith('generate_') for k in globals()):
    generate = next(v for k, v in globals().items() if k.startswith('generate_'))
``` """

    # 初始化計數器
    regex_fixes = 0
    logic_fixes = 0
    prompt_tokens = 0
    completion_tokens = 0

    try:
        if current_app: current_app.logger.info(f"Generating {skill_id} with {current_model}")
        
        client = get_ai_client(role='coder') 
        response = client.generate_content(prompt)
        code = response.text
        
        # [V9.8] 嘗試獲取 Token 用量 (視 API 而定)
        try:
            # 適用於 Google Gemini / Vertex AI
            if hasattr(response, 'usage_metadata'):
                prompt_tokens = response.usage_metadata.prompt_token_count
                completion_tokens = response.usage_metadata.candidates_token_count
            # 如果是其他 API，可能需要調整這裡
        except:
            pass # 取不到就算了，保持 0
        
        match = re.search(r'```(?:python)?\s*(.*?)```', code, re.DOTALL | re.IGNORECASE)
        if match: code = match.group(1)
        elif "import random" in code: code = code[code.find("import random"):]
        
        # [V9.5 Check] Integrity Validation
        if "def generate" not in code:
            # If critical function is missing, it implies truncation.
            # We attempt a naive fix by appending a default dispatcher if at least generate_problem exists.
            if "def generate_problem" in code:
                code += "\n\n# [Auto-Recovered Dispatcher]\ndef generate(level=1):\n    return generate_problem()"
            else:
                return False, "Critical Error: Generated code is incomplete (missing 'generate' function)."
        
        # [V9.9.9 Code Metrics] Intercept raw length before injection
        raw_len = len(code)
        
        code = inject_perfect_utils(code)
        
        # Calculate injected utils length
        utils_len = len(PERFECT_UTILS)
        total_len = len(code)
        
        # [V9.8.2 Defense] Hard Validation for 7B Models
        code, pre_fixes = validate_and_fix_code(code)
        
        # [V9.9.5 Data Flow] Accumulate preventive fixes
        regex_fixes = pre_fixes

        # [V9.9.9] Universal Helper Patcher
        # Patches all draw_* functions to ensure they return values
        code, patch_fixes = universal_function_patcher(code)
        regex_fixes += patch_fixes
        
        code = fix_return_format(code)
        code = clean_global_scope_execution(code)
        code = inject_robust_dispatcher(code) 
        code = fix_missing_answer_key(code)
        
        # [V9.8] 驗證與修復 (使用新版函式)
        is_valid, syntax_err = validate_python_code(code)
        repaired = (pre_fixes > 0) # 如果預防性修復動過，狀態改為已修復
        
        if not is_valid:
            # 呼叫新版 fix_code_syntax，接收次數
            code, r_count = fix_code_syntax(code, syntax_err)
            regex_fixes += r_count # 累加
            
            is_valid, syntax_err = validate_python_code(code)
            repaired = True
            
        is_valid_log, logic_err = validate_logic_with_pyflakes(code)
        if not is_valid_log:
            # 呼叫新版 fix_logic_errors，接收次數
            code, l_count = fix_logic_errors(code, logic_err)
            logic_fixes += l_count # 累加
            repaired = True

        # =========================================================
        # [V11.4] "Final Intercept" (The Last Line of Defense)
        # =========================================================

        # 1. String Deduplication (防止提示語堆疊)
        # 合併 question_text 中連續重複的括號引導語
        if code.count("請輸入") > 1 or code.count("例如：") > 1 or code.count("答案格式") > 1:
            code = re.sub(r'(\(請輸入.*?\))(\s*\\n\1)+', r'\1', code)
            code = re.sub(r'(\(例如：.*?\))(\s*\\n\1)+', r'\1', code)
            code = re.sub(r'(\(答案格式：.*?\))(\s*\\n\1)+', r'\1', code)

        # 2. Answer Purge (答案欄位淨化) - 強制清除引導語
        # 若 answer 欄位包含「例如：」或「請輸入」，強制還原為 str(correct_answer)
        if "例如：" in code or "請輸入" in code:
             code = re.sub(r"'answer':\s*['\"](.*?(?:例如|請輸入).*?)['\"]", r"'answer': str(correct_answer)", code)

        # 3. Quote Hardening (引號鎖死) [Final Intercept]
        # 強制修正為標準格式 ['Microsoft JhengHei']，無論 AI 產出為何
        font_pattern = r"(?:matplotlib\.|plt\.)?rcParams\[['\"]font\.sans-serif['\"]\]\s*=\s*(?:\[[^\]]*\]|['\"].*?['\"])"
        code = re.sub(font_pattern, "plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']", code)

        # 4. Physical Newline Hardening (物理換行硬化)
        # 將程式碼中所有文字態的 \\n 替換為物理換行符號 \n (解決單引號/f-string 內的換行顯示問題)
        code = code.replace('\\\\n', '\\n')

        # 4. Truncation Detection (斷頭偵測) [NEW]
        # Scan for calls to _generate_type_... inside generate()
        # And ensure they are defined in the code.
        generate_match = re.search(r'def generate\(.*?\):(.*?)(?=\ndef|\Z)', code, re.DOTALL)
        if generate_match:
            generate_body = generate_match.group(1)
            calls = re.findall(r'(_generate_type_\w+)\(', generate_body)
            definitions = re.findall(r'def\s+(_generate_type_\w+)\s*\(', code)
            missing_funcs = [c for c in calls if c not in definitions]
            if missing_funcs:
                error_msg = f"Critical Error: Called functions not defined: {missing_funcs}. Code truncated?"
                log_experiment(
                    skill_id, start_time, len(prompt), len(code), False, 
                    error_msg, repaired,
                    current_model,
                    actual_provider=current_provider,
                    regex_fixes=regex_fixes, 
                    raw_output_len=raw_len,
                    utils_len=utils_len
                )
                return False, error_msg

        # 4. Logic Self-Healing (邏輯自癒)
        # 若發現 is_prime 或 _check_divisibility 函式內部包含 return {'correct': False...} 這種錯誤格式
        # 強制將其替換為標準的 return False 或 return True
        # 注意：這裡使用較為保守的替換，避免誤傷主 check 函式
        
        def fix_bool_return(match):
            func_body = match.group(0)
            if "def check" in func_body: return func_body # Skip main check function
            # Replace dict returns with bools
            fixed = re.sub(r"return\s+\{['\"]correct['\"]\s*:\s*False.*?\}", "return False", func_body)
            fixed = re.sub(r"return\s+\{['\"]correct['\"]\s*:\s*True.*?\}", "return True", fixed)
            return fixed

        # 掃描 helper functions (此處假設 helper 函式較短，且由 def 開頭)
        # 為了安全，我們針對特定函式名稱進行掃描
        for func_name in ['is_prime', '_check_divisibility', 'check_divisibility']:
            pattern = rf"(def {func_name}\(.*?\):.*?)(?=\ndef|\Z)"
            code = re.sub(pattern, fix_bool_return, code, flags=re.DOTALL)


        # 2. Handwriting Prompt Injection (Logic Enhancement) - [Cleaned up in V11.1]
        # 由於 fix_missing_answer_key 已包含增強邏輯，此處僅做備援檢查或是移除舊的 runtime patch
        if "_patch_all_returns" in code:
             # 如果 AI 沒有寫 input_mode，我們不需要強制 runtime patch 去 check 變數
             # 因為 fix_missing_answer_key 的 patch 已經很強大了
             pass
        # =========================================================

        duration = time.time() - start_time
        created_at = time.strftime('%Y-%m-%d %H:%M:%S')
        
        header = f'''# ==============================================================================
# ID: {skill_id}
# Model: {current_model} | Strategy: {strategy_name}
# Duration: {duration:.2f}s | RAG: {rag_count} examples
# Created At: {created_at}
# Fix Status: {'[Repaired]' if repaired else '[Clean Pass]'}
# Fixes: Regex={regex_fixes}, Logic={logic_fixes}
#==============================================================================\n\n'''
        path = os.path.join(current_app.root_path, 'skills', f'{skill_id}.py')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(header + code)
            
        # [V9.8] 呼叫 Log，傳入完整數據
        log_experiment(
            skill_id, start_time, len(prompt), len(code), True, 
            syntax_err if not is_valid else "None", repaired,
            current_model,
            actual_provider=current_provider, # 傳入實際供應商
            regex_fixes=regex_fixes,      # New
            logic_fixes=logic_fixes,      # New
            prompt_tokens=prompt_tokens,  # New
            completion_tokens=completion_tokens, # New
            prompt_version=active_prompt.version if active_prompt else 1,
            strategy=active_prompt.model_tag if active_prompt else "Legacy",
            raw_output_len=raw_len,   # [新增]
            utils_len=utils_len       # [新增]
        )
        return True, "Success"

    except Exception as e:
        # [核心修復] 即使程式崩潰，也要將錯誤存入資料庫
        log_experiment(
            skill_id, start_time, len(prompt) if 'prompt' in locals() else 0, 0, False, 
            str(e), False, 
            current_model if 'current_model' in locals() else "Unknown",
            current_provider if 'current_provider' in locals() else "google",
            regex_fixes=regex_fixes, 
            prompt_version=active_prompt.version if 'active_prompt' in locals() and active_prompt else 1,
            raw_output_len=raw_len if 'raw_len' in locals() else 0, # [新增] 防止變數未定義
            utils_len=utils_len if 'utils_len' in locals() else 0   # [新增]
        )
        return False, str(e)
