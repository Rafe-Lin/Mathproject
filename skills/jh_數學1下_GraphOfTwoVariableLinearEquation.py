# ==============================================================================
# ID: jh_數學1下_GraphOfTwoVariableLinearEquation
# Model: gemini-2.5-flash | Strategy: V14.0 Equation Robustness & Zero-Leak
# Fix Status: [Full Recovery - Equation Visibility & Fraction Fix]
# ==============================================================================

import random, math, matplotlib, base64, io, re
import numpy as np
from matplotlib.figure import Figure

# 設定字體與風格
matplotlib.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
matplotlib.rcParams['axes.unicode_minus'] = False

def _fix_val(v):
    """移除 .0"""
    return int(v) if v.is_integer() else v

def _format_frac_latex(val):
    """修復雙大括號問題與分數格式"""
    if val.is_integer(): return str(int(val))
    abs_v = abs(val)
    int_p = int(abs_v)
    sign = "-" if val < 0 else ""
    # 鎖定 0.5 (1/2) 精度
    if int_p == 0:
        return r"{s}\frac{n}{d}".replace("{s}", sign).replace("{n}", "1").replace("{d}", "2")
    return r"{s}{i}\frac{n}{d}".replace("{s}", sign).replace("{i}", str(int_p)).replace("{n}", "1").replace("{d}", "2")

def _draw_blank_plane():
    """產出高品質空白座標系，絕不洩漏答案"""
    fig = Figure(figsize=(6, 6), dpi=120)
    ax = fig.add_subplot(111)
    ax.set_aspect('equal')
    # 強化格線可讀性
    ax.grid(True, linestyle='-', color='#E0E0E0', lw=0.8)
    ax.axhline(0, color='black', lw=1.5)
    ax.axvline(0, color='black', lw=1.5)
    ax.text(0, -0.7, '0', fontsize=18, fontweight='bold', ha='center', va='top')
    
    # 座標範圍鎖定
    ax.set_xlim(-9.5, 9.5); ax.set_ylim(-9.5, 9.5)
    ax.set_xticks(range(-9, 10)); ax.set_yticks(range(-9, 10))
    ax.set_xticklabels([]); ax.set_yticklabels([])
    
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    return base64.b64encode(buf.getvalue()).decode('utf-8')

def generate(level=1):
    """[V14.0] 方程式強化生成邏輯"""
    # 1. 產生係數 ax + by = c
    a = random.randint(1, 4) * random.choice([1, -1])
    b = random.randint(1, 4) * random.choice([1, -1])
    c = random.randint(-8, 8)
    
    # 2. 鋼鐵化組合方程式字串
    parts = []
    # 處理 x 項
    if a == 1: parts.append("x")
    elif a == -1: parts.append("-x")
    else: parts.append(str(a) + "x")
    
    # 處理 y 項
    if b > 0:
        if b == 1: parts.append("+y")
        else: parts.append("+" + str(b) + "y")
    else: # b < 0
        if b == -1: parts.append("-y")
        else: parts.append(str(b) + "y")
        
    eq_str = "".join(parts) + " = " + str(c)
    
    # 3. 題型判定：點是否在直線上
    px = random.randint(-6, 6) + random.choice([0, 0.5])
    on_line = random.choice([True, False])
    
    if on_line:
        # y = (c - ax) / b
        py = (c - a * px) / b
        # 物理驗證：確保 py 為整數或 0.5
        if not (py * 2).is_integer(): return generate(level)
    else:
        py = random.randint(-6, 6) + 0.5

    p_str = r"({x}, {y})".replace("{x}", _format_frac_latex(px)).replace("{y}", _format_frac_latex(py))
    
    # 4. 封裝題目
    question = r"請問點 {p} 是否在直線方程式 ${eq}$ 的圖形上？ (請回答「是」或「否」)"
    question_text = question.replace("{p}", p_str).replace("{eq}", eq_str)
    
    return {
        "question_text": question_text,
        "correct_answer": "是" if on_line else "否",
        "answer": "是" if on_line else "否",
        "image_base64": _draw_blank_plane(), # 絕對空白
        "input_mode": "text"
    }

def check(user_answer, correct_answer):
    """是/否題型專用閱卷"""
    return str(user_answer).strip() == str(correct_answer).strip()
