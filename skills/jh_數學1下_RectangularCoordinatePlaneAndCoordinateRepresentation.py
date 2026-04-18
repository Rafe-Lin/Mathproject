# ==============================================================================
# ID: jh_數學1下_RectangularCoordinatePlaneAndCoordinateRepresentation
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 48.56s | RAG: 5 examples
# Created At: 2026-01-15 16:51:32
# Fix Status: [Repaired]
# Fixes: Regex=1, Logic=0
# ==============================================================================

import random
import math
import io
import base64
import re
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.ticker import MultipleLocator
import matplotlib.patches as patches

# [V11.6 Elite Font & Style]
# Note: In the OO approach, we set these via rcParams or directly on text objects if needed, 
# but setting global rcParams is still effective for the process.
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
plt.rcParams['axes.unicode_minus'] = False

# 確保版本號遞增
__version__ = "1.1.0"

# 點標籤白名單
POINT_LABELS = ['A', 'B', 'C', 'D', 'P', 'Q', 'R', 'S', '小明', '小美', '小翊']

def _generate_coordinate_value():
    """
    生成坐標數值。
    限制：整數或 .5 (分母為 2)。
    範圍：-8 到 8 (由 range(-16, 17) * 0.5 決定)
    """
    choices = [x * 0.5 for x in range(-16, 17)]
    val = random.choice(choices)
    return val

def _fmt(val):
    """
    格式化數值。
    - 如果是整數 (如 5.0, 5)，回傳 '5'。
    - 如果是小數 (如 5.5)，回傳 '5.5'。
    """
    if val == int(val):
        return str(int(val))
    return str(val)

def _draw_coordinate_plane(points_with_labels, title="直角坐標平面"):
    """
    使用 OO 方式繪製直角坐標平面。
    points_with_labels: list of (x, y, label)
    """
    fig = Figure(figsize=(6, 6), dpi=120)
    canvas = FigureCanvasAgg(fig)
    ax = fig.add_subplot(111)
    
    # 設定比例固定
    ax.set_aspect('equal')
    
    # 範圍與格線
    limit = 10
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    
    # 格線 MultipleLocator(1)
    ax.xaxis.set_major_locator(MultipleLocator(1))
    ax.yaxis.set_major_locator(MultipleLocator(1))
    ax.grid(True, linestyle='--', alpha=0.6)
    
    # 隱藏預設邊框，改用中心軸線
    # Matplotlib 的 spines 預設是四周的框
    for spine in ax.spines.values():
        spine.set_visible(False)
        
    # 繪製 X 軸與 Y 軸 (黑色實線)
    ax.axhline(0, color='black', linewidth=1.2)
    ax.axvline(0, color='black', linewidth=1.2)
    
    # 軸向箭頭 (使用 plot 繪製三角形)
    # X 軸箭頭
    ax.plot(limit, 0, ">k", markersize=6, clip_on=False, zorder=10)
    # Y 軸箭頭
    ax.plot(0, limit, "^k", markersize=6, clip_on=False, zorder=10)
    
    # 軸標籤 (x, y)
    ax.text(limit + 0.5, 0, 'x', ha='left', va='center', fontsize=14, fontstyle='italic')
    ax.text(0, limit + 0.5, 'y', ha='center', va='bottom', fontsize=14, fontstyle='italic')
    
    # 原點標記 '0' (位於左下側)
    ax.text(-0.5, -0.5, '0', ha='right', va='top', fontsize=12, fontweight='bold')
    
    # 隱藏刻度數字 (題目通常不標示所有刻度，以免過於混亂，僅依賴格線數格子)
    # 若需標示可打開，但根據要求"圖上只標示點標籤"，盡量保持乾淨
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.tick_params(axis='both', length=0) # 隱藏刻度線
    
    # 繪製點與標籤 (防洩漏：只標 label，不標座標值)
    for x, y, label in points_with_labels:
        ax.plot(x, y, 'o', color='blue', markersize=6, zorder=5)
        # 標籤加白底避免被格線干擾
        ax.text(x + 0.4, y + 0.4, label, fontsize=14, color='black', 
                bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=1), zorder=6)

    # 標題
    # ax.set_title(title, fontsize=14) 
    
    # 輸出
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

# 閱卷邏輯
def check(user_answer, correct_answer):
    if user_answer is None: return {"correct": False, "result": "未提供答案。"}
    
    # 標準化函數
    def _clean_and_parse(s):
        # 移除空格, LaTeX 符號
        s = str(s).strip().replace(" ", "").replace("$", "").replace("\\", "")
        # 尋找所有數值 (整數或小數)
        nums = re.findall(r"[-+]?\d+\.?\d*", s)
        return [float(x) for x in nums]
    
    u_nums = _clean_and_parse(user_answer)
    c_nums = _clean_and_parse(correct_answer)
    
    if not u_nums: return {"correct": False, "result": "無法識別數值。"}
    
    # 比對
    if len(u_nums) != len(c_nums):
        return {"correct": False, "result": f"答案錯誤。正確答案為：{correct_answer}"}
        
    # 逐一比對數值，容許微小誤差
    is_correct = True
    for u, c in zip(u_nums, c_nums):
        if not math.isclose(u, c, rel_tol=1e-9, abs_tol=1e-9):
            is_correct = False
            break
            
    if is_correct:
        return {"correct": True, "result": "正確！"}
    else:
        return {"correct": False, "result": f"答案錯誤。正確答案為：{correct_answer}"}


def generate(level=1):
    problem_type = random.choice([1, 2, 3, 4, 5])
    
    question_text = ""
    correct_answer = ""
    answer_data = None
    image_base64 = ""
    
    # 輔助：取不重複標籤
    def _get_labels(n):
        return random.sample(POINT_LABELS, k=n)

    if problem_type == 1: 
        # Type 1: 讀取坐標 (Reading Coordinates)
        # 圖上有點，學生回答坐標
        p_label = _get_labels(1)[0]
        x = _generate_coordinate_value()
        y = _generate_coordinate_value()
        
        # 繪圖：顯示點與標籤
        image_base64 = _draw_coordinate_plane([(x, y, p_label)])
        
        question_text = f"請寫出坐標平面上點 {p_label} 的坐標。"
        # 答案格式：A(5, 3) 或 A(-1.5, 2)
        correct_answer = f"{p_label}({_fmt(x)}, {_fmt(y)})"
        answer_data = (x, y)

    elif problem_type == 2: 
        # Type 2: 標出坐標 (Plotting Points)
        # 給坐標，學生畫圖 (實際上是系統給空白圖，學生想像或手寫)
        p_label = _get_labels(1)[0]
        x = _generate_coordinate_value()
        y = _generate_coordinate_value()
        
        # 繪圖：空白坐標系，不給答案點
        image_base64 = _draw_coordinate_plane([])
        
        question_text = f"請在直角坐標平面上標出點 {p_label}({_fmt(x)}, {_fmt(y)}) 的位置。"
        correct_answer = f"{p_label}({_fmt(x)}, {_fmt(y)})"
        answer_data = (x, y)

    elif problem_type == 3: 
        # Type 3: 判斷象限
        p_label = _get_labels(1)[0]
        # 避免 (0,0)
        while True:
            x = _generate_coordinate_value()
            y = _generate_coordinate_value()
            if not (x == 0 and y == 0): break
            
        image_base64 = _draw_coordinate_plane([]) # 不需畫點，甚至不需圖，但提供空白圖作參考可
        
        q_str = ""
        if x > 0 and y > 0: q_str = "第一象限"
        elif x < 0 and y > 0: q_str = "第二象限"
        elif x < 0 and y < 0: q_str = "第三象限"
        elif x > 0 and y < 0: q_str = "第四象限"
        elif x == 0: q_str = "Y軸上" # y != 0 因為排除 (0,0)
        elif y == 0: q_str = "X軸上"
        
        question_text = f"已知點 {p_label} 的坐標為 ({_fmt(x)}, {_fmt(y)})，請問點 {p_label} 位於哪一個象限或坐標軸上？"
        correct_answer = q_str
        answer_data = q_str

    elif problem_type == 4: 
        # Type 4: 對稱點
        orig_label, new_label = _get_labels(2)
        x = _generate_coordinate_value()
        y = _generate_coordinate_value()
        
        mode = random.choice(["X軸", "Y軸", "原點"])
        
        if mode == "X軸":
            nx, ny = x, -y
        elif mode == "Y軸":
            nx, ny = -x, y
        else: # 原點
            nx, ny = -x, -y
            
        image_base64 = _draw_coordinate_plane([])
        
        question_text = f"已知點 {orig_label}({_fmt(x)}, {_fmt(y)})，若點 {new_label} 是點 {orig_label} 對{mode}的對稱點，則 {new_label} 點的坐標為何？"
        correct_answer = f"{new_label}({_fmt(nx)}, {_fmt(ny)})"
        answer_data = (nx, ny)

    elif problem_type == 5: 
        # Type 5: 距離與軸上的點
        p_label = _get_labels(1)[0]
        dist = random.randint(1, 8) # 距離用整數比較簡單，或也可以用 float
        # 題目設計簡單點，用整數距離
        
        axis = random.choice(["X軸", "Y軸"])
        
        possible = []
        if axis == "X軸":
            # 在 X 軸上，與 Y 軸距離為 dist => x = dist or -dist, y=0
            # 題目：在 X 軸上 => (x, 0). 與 Y 軸距離 => |x| = dist.
            possible = [(dist, 0), (-dist, 0)]
            topic_str = f"已知點 {p_label} 在 X 軸上，且與 Y 軸的距離為 {dist} 單位長"
        else:
            # 在 Y 軸上 => (0, y). 與 X 軸距離 => |y| = dist.
            possible = [(0, dist), (0, -dist)]
            topic_str = f"已知點 {p_label} 在 Y 軸上，且與 X 軸的距離為 {dist} 單位長"
            
        question_text = f"{topic_str}，則點 {p_label} 的坐標可能為何？(全對才給分)"
        
        # 格式化答案
        # 排序方便比對 (雖然後端 check 已用數值比對，但文字顯示要有一致性)
        possible.sort(key=lambda p: (p[0], p[1]))
        
        ans_strs = [f"{p_label}({_fmt(px)}, {_fmt(py)})" for px, py in possible]
        correct_answer = ", ".join(ans_strs)
        answer_data = possible
        
        image_base64 = _draw_coordinate_plane([])

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": answer_data,
        "image_base64": image_base64,
        "created_at": "", # 每次生成如果是即時的，這裡通常用 datetime.now()，但此處簡易處理
        "version": __version__
    }

# [Auto-Injected Patch v11.0] Universal Return & Handwriting Fixer
def _patch_all_returns(func):
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        if func.__name__ == 'check' and isinstance(res, bool):
            return {'correct': res, 'result': '正確！' if res else '答案錯誤'}
        if isinstance(res, dict):
            if 'question_text' in res:
                res['question_text'] = res['question_text'].replace(r'\n', '\n')
            
            # 手寫模式觸發
            c_ans = str(res.get('correct_answer', ''))
            triggers = ['^', '/', '|', '[', '{', '\\'] # 減少觸發，座標題通常不需要特殊符號輸入，但可選手寫
            should_inject = (res.get('input_mode') == 'handwriting')
            if should_inject and "手寫" not in res['question_text']:
                 res['question_text'] += "\n(請在手寫區作答!)"
                 
            if 'image_base64' not in res: res['image_base64'] = ""
            
        return res
    return wrapper

for _name, _func in list(globals().items()):
    if callable(_func) and (_name.startswith('generate') or _name == 'check'):
        globals()[_name] = _patch_all_returns(_func)
