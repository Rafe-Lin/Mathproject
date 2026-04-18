# ==============================================================================
# ID: jh_數學1上_GeometryProblems
# Model: V12.1 Elite (Physical Geometry)
# Title: Geometry Problems (Trapezoid & Rectangle-Triangle)
# Version: 1.1.0
# Created: 2026-01-15
# Maintainer: Antigravity (Chief AI Engineer)
# ==============================================================================

import random
import math
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from fractions import Fraction
import base64
import io
import re
from datetime import datetime

# [V11.6 Elite Font & Style]
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
plt.rcParams['axes.unicode_minus'] = False

# --- 1. Formatting Helpers (V10.6 No-F-String LaTeX) ---
def to_latex(num):
    """
    Convert int/float/Fraction to LaTeX using .replace() to avoid f-string conflicts.
    """
    if isinstance(num, int): return str(num)
    if isinstance(num, float): 
        # Check if integer
        if num.is_integer(): return str(int(num))
        num = Fraction(str(num)).limit_denominator(100)
    
    if isinstance(num, Fraction):
        if num.denominator == 1: return str(num.numerator)
        if num == 0: return "0"
        
        sign = "-" if num < 0 else ""
        abs_num = abs(num)
        
        if abs_num.numerator > abs_num.denominator:
            whole = abs_num.numerator // abs_num.denominator
            rem_num = abs_num.numerator % abs_num.denominator
            if rem_num == 0: return r"{s}{w}".replace("{s}", sign).replace("{w}", str(whole))
            return r"{s}{w} \frac{{n}}{{d}}".replace("{s}", sign).replace("{w}", str(whole)).replace("{n}", str(rem_num)).replace("{d}", str(abs_num.denominator))
        return r"\frac{{n}}{{d}}".replace("{n}", str(num.numerator)).replace("{d}", str(num.denominator))
    return str(num)

# --- 2. Ultra Visual Renderer (V11.6) ---
def draw_geometry_composite(polygons, labels, x_limit=None, y_limit=None, auxiliary_lines=None):
    """
    [V11.6 Ultra Visual] Physical Geometry Renderer
    [Coordinate Lock Protocol]: Strict adherence to physical coordinates.
    """
    fig = Figure(figsize=(6, 5), dpi=300) # [High Resolution]
    canvas = FigureCanvasAgg(fig)
    ax = fig.add_subplot(111)
    
    # [Physical Standard] 90 degrees must be 90 degrees
    ax.set_aspect('equal', adjustable='datalim')

    # Draw Polygons
    all_x = []
    all_y = []
    
    for poly_data in polygons:
        pts = poly_data[0]
        ec = poly_data[1] if len(poly_data) > 1 else 'black'
        fc = poly_data[2] if len(poly_data) > 2 else 'none'
        alpha = poly_data[3] if len(poly_data) > 3 else 1.0
        
        polygon = patches.Polygon(pts, closed=True, edgecolor=ec, facecolor=fc, alpha=alpha, linewidth=2)
        ax.add_patch(polygon)
        
        for p in pts:
            all_x.append(p[0])
            all_y.append(p[1])

    # Draw Auxiliary Lines
    if auxiliary_lines:
        for p1, p2, style in auxiliary_lines:
            ls = '--' if style == 'dashed' else ':' if style == 'dotted' else '-'
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], ls, color='black', linewidth=1.5)

    # Draw Labels with White Halo
    for text, pos in labels.items():
        all_x.append(pos[0])
        all_y.append(pos[1])
        t = ax.text(pos[0], pos[1], text, fontsize=14, fontweight='bold', ha='center', va='center', zorder=10)
        # [White Halo]
        t.set_bbox(dict(facecolor='white', edgecolor='none', alpha=0.7, pad=2, boxstyle='round,pad=0.2'))

    # Dynamic limits
    if all_x and all_y:
        margin_x = (max(all_x) - min(all_x)) * 0.15 + 1
        margin_y = (max(all_y) - min(all_y)) * 0.15 + 1
        ax.set_xlim(min(all_x) - margin_x, max(all_x) + margin_x)
        ax.set_ylim(min(all_y) - margin_y, max(all_y) + margin_y)
    
    if x_limit: ax.set_xlim(x_limit)
    if y_limit: ax.set_ylim(y_limit)

    ax.axis('off')
    
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', transparent=True, dpi=300)
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

# --- 3. Core Generation Logic ---
def generate(level=1):
    """
    Generate Geometry Problems.
    Type 1: Trapezoid Reverse Op (Textbook P.208)
    Type 2: Rectangle-Triangle Area (Image 166d87 + 436661 Fix)
    """
    
    # Decide Type (Weighted or Random)
    problem_type = random.choice(['Type 1', 'Type 2'])
    
    if problem_type == 'Type 1':
        # --- Type 1: Trapezoid (Reverse Engineering) ---
        # Scenario: Lower base is 4 less than 3 times upper base.
        # Given Area and Height -> Find Upper Base.
        
        # 1. Randomize Answer First (Upper Base)
        upper_base = random.randint(3, 10)
        
        # 2. Derive Lower Base
        # "Lower base is 4 less than 3 times upper base" -> L = 3x - 4
        # Mirroring textbook logic exactly.
        lower_base = 3 * upper_base - 4
        
        # 3. Randomize Height
        height = random.choice([4, 6, 8, 10, 12, 14]) # Even numbers make 0.5 easier
        
        # 4. Calculate Area
        area = int(0.5 * (upper_base + lower_base) * height)
        
        # 5. Question Text
        # Security Guardrails: No f-strings with latex.
        q_template = r"已知梯形下底比上底的 3 倍少 4 公分。若此梯形的高為 {h} 公分，面積為 {a} 平方公分，則此梯形的上底為多少公分？"
        question_text = q_template.replace("{h}", str(height)).replace("{a}", str(area))
        
        # 6. Visualization
        # Isosceles Trapezoid centered at (0,0) looks good.
        diff = lower_base - upper_base
        offset = diff / 2
        
        pt_D = (0, 0)
        pt_C = (lower_base, 0)
        pt_B = (offset + upper_base, height)
        pt_A = (offset, height)
        
        polygons = [
            ([pt_D, pt_C, pt_B, pt_A], 'black', '#E0F7FA', 0.5) # Trapezoid
        ]
        
        # Add Height Indicator (dashed line)
        h_pt_top = (offset + upper_base/2, height)
        h_pt_bot = (offset + upper_base/2, 0)
        aux_lines = [
            (h_pt_top, h_pt_bot, 'dashed')
        ]
        
        labels = {
            "h": (offset + upper_base/2 + 0.2, height/2)
        }

        image_base64 = draw_geometry_composite(polygons, labels, auxiliary_lines=aux_lines)
        
        correct_answer = upper_base
        answer_display = str(upper_base)

    else:
        # --- Type 2: Rectangle ACEF with Triangle BDF (Physical Lock) ---
        # [Strict Constants]: AF=10, AB=8, CD=7, DE=3
        # Variable: BC (random integer)
        
        # 1. Constants
        given_AF = 10
        given_AB = 8
        given_CD = 7
        given_DE = 3
        
        # 2. Variable BC
        ans_BC = random.randint(2, 10)
        
        # 3. Derived W
        # W = AB + BC
        width_W = given_AB + ans_BC
        
        # 4. Coordinates [Coordinate Lock Protocol F=(0,0)]
        # F - Bottom Left
        pt_F = (0, 0)
        # E - Bottom Right
        pt_E = (width_W, 0)
        # C - Top Right (E + H)
        pt_C = (width_W, given_AF)
        # A - Top Left (F + H)
        pt_A = (0, given_AF)
        
        # B is on Top Edge AC?
        # A=(0,10), C=(W,10). Line AC is y=10.
        # "AB = 8". So B_x = A_x + 8 = 8.
        # B = (8, 10).
        pt_B = (given_AB, given_AF)
        
        # D is on Right Edge CE?
        # C=(W,10), E=(W,0). Line CE is x=W.
        # "CD = 7". D is 7 units down from C.
        # D_y = C_y - 7 = 10 - 7 = 3.
        # "DE = 3". Check: D_y - E_y = 3 - 0 = 3. Consistent.
        # D = (W, 3).
        pt_D = (width_W, given_DE)
        
        # 5. Calculate Triangle BDF Area
        # B(8, 10), D(W, 3), F(0, 0)
        # Shoelace
        x1, y1 = pt_B
        x2, y2 = pt_D
        x3, y3 = pt_F
        
        # Area = 0.5 * |x1(y2-y3) + x2(y3-y1) + x3(y1-y2)|
        #      = 0.5 * |8(3-0) + W(0-10) + 0|
        #      = 0.5 * |24 - 10W|
        #      = |12 - 5W|
        # Since W = 8 + BC >= 10, 5W >= 50. 12 - 5W is negative.
        # Area = 5W - 12.
        tri_area_val = 5 * width_W - 12
        tri_area_int = int(tri_area_val)
        
        # 6. Question Text
        # [Violence Segment Marking]: Use \overline{NAME} = Val
        q_template = r"如圖，四邊形 $ACEF$ 為長方形，已知 $\triangle BDF$ 的面積為 {area}。若 $\overline{AF} = 10, \overline{AB} = 8, \overline{CD} = 7, \overline{DE} = 3$，求 $\overline{BC}$ 的長度。"
        question_text = q_template.replace("{area}", str(tri_area_int))
        
        # 7. Visualization
        # Polygons: Rectangle [F, E, C, A], Triangle [B, D, F]
        polygons = [
            ([pt_F, pt_E, pt_C, pt_A], 'black', 'white', 1.0), # Rect ACEF
            ([pt_B, pt_D, pt_F], 'blue', '#E3F2FD', 0.6)      # Triangle BDF
        ]
        
        labels = {
            "A": (pt_A[0]-0.5, pt_A[1]+0.5),
            "C": (pt_C[0]+0.5, pt_C[1]+0.5), 
            "E": (pt_E[0]+0.5, pt_E[1]-0.5),
            "F": (pt_F[0]-0.5, pt_F[1]-0.5),
            "B": (pt_B[0], pt_B[1]+0.8),
            "D": (pt_D[0]+0.8, pt_D[1])
        }
        
        image_base64 = draw_geometry_composite(polygons, labels)
        
        correct_answer = ans_BC
        answer_display = str(ans_BC)

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": answer_display,
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(),
        "version": "1.1.0"
    }

def check(user_answer, correct_answer):
    """
    Standard Answer Checker
    """
    if user_answer is None or user_answer == "":
        return {"correct": False, "result": "未作答"}
        
    try:
        # Normalize user input
        u_str = str(user_answer).strip().replace(" ", "")
        c_str = str(correct_answer).strip().replace(" ", "")
        
        # Simple Float/Int comparison
        if u_str == c_str:
            return {"correct": True, "result": "正確"}
        
        if abs(float(u_str) - float(c_str)) < 1e-6:
             return {"correct": True, "result": "正確"}
             
    except:
        pass
        
    return {"correct": False, "result": r"正確答案是 {a}".replace("{a}", str(correct_answer))}