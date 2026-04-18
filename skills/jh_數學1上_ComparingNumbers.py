import random
import matplotlib.pyplot as plt
import io
import base64
from fractions import Fraction

# ==============================================================================
# GOLD STANDARD TEMPLATE v8.7 (Universal)
# Modified for Comparing Numbers
# ==============================================================================

def generate(level=1):
    """
    Main Dispatcher
    """
    if level == 1:
        return generate_basic_concept()
    else:
        return generate_advanced_application()

def get_base64_image(fig):
    """Helper to convert Matplotlib figure to Base64 string"""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return img_str

def fmt_num_latex(val):
    """
    將數值格式化為美觀的 LaTeX 字串
    例如: 4.5 -> 4\frac{1}{2}
    """
    if isinstance(val, int):
        return str(val)
    
    # 處理小數或分數
    f = Fraction(val).limit_denominator()
    
    if f.denominator == 1:
        return str(f.numerator)
    
    # 帶分數處理
    int_part = int(f.numerator / f.denominator)
    remainder = abs(f.numerator % f.denominator)
    den = f.denominator
    
    if int_part == 0:
        # 真分數 (例如 1/2, -1/2)
        # 注意 f-string 中 LaTeX 大括號要用 {{ }}
        if f.numerator < 0:
            return f"-\\frac{{{abs(f.numerator)}}}{{{den}}}"
        else:
            return f"\\frac{{{f.numerator}}}{{{den}}}"
    else:
        # 帶分數 (例如 4 1/2)
        # 負號處理
        sign = "-" if f.numerator < 0 else ""
        abs_int = abs(int_part)
        # 修正：整數與分數間加入 \, (thin space) 避免擠在一起
        return f"{sign}{abs_int}\\frac{{{remainder}}}{{{den}}}"

def generate_basic_concept():
    """
    Level 1: 數線標示與大小比較 (基礎整數與簡單小數)
    """
    # 1. 生成數據
    integers = random.sample(range(-7, 8), 3) # 3個整數
    
    # 生成 1 個簡單小數 (如 X.5)
    decimal_base = random.randint(-6, 6)
    decimal_val = decimal_base + 0.5
    
    # 組合並排序
    numbers = sorted(integers + [decimal_val])
    
    # 2. 選擇比較對象 (最大值 vs 帶小數的值)
    target_1 = numbers[-1] # 最大值
    target_2 = decimal_val
    
    # 決定正確答案 (比大小符號)
    if target_1 > target_2:
        ans_symbol = ">"
    elif target_1 < target_2:
        ans_symbol = "<"
    else:
        ans_symbol = "="
        
    # 3. 繪圖 (數線)
    fig, ax = plt.subplots(figsize=(8, 2))
    
    # 畫軸線
    min_range = -8
    max_range = 8
    ax.hlines(0, min_range, max_range, colors='black', linewidth=1.5)
    ax.plot(max_range, 0, ">k", markersize=10, clip_on=False)
    ax.plot(min_range, 0, "<k", markersize=10, clip_on=False)
    
    # 畫刻度
    ticks = range(min_range, max_range + 1)
    for t in ticks:
        ax.plot([t, t], [-0.1, 0.1], 'k', linewidth=1)
        # 只標示偶數刻度以免太擠
        if t % 2 == 0:
            ax.text(t, -0.4, str(t), ha='center', va='top', fontsize=10)

    # 標示點 (題目要求學生標示，這裡畫出空心點或不畫，
    # 但為了美觀，我們畫出正確位置的點，標上字母讓學生對照？
    # 或者此題型是「選擇題」或「填充題」？
    # 根據描述是「請在數線上標示...並比較...」，通常這類自動生成題會簡化為「比較大小」的部分為主要作答區)
    
    # 這裡我們只畫出點的位置，不標數值，模擬題目情境
    labels = ['A', 'B', 'C', 'D']
    for i, num in enumerate(numbers):
        ax.plot(num, 0, 'bo', markersize=6)
        ax.text(num, 0.3, labels[i], ha='center', va='bottom', color='blue', fontsize=11)

    ax.axis('off')
    ax.set_xlim(min_range - 1, max_range + 1)
    ax.set_ylim(-1, 1)
    
    img_base64 = get_base64_image(fig)

    # 4. 格式化題目字串 (使用 fmt_num_latex 處理 LaTeX)
    # 顯示列表字串
    nums_str = ", ".join([f"${fmt_num_latex(n)}$" for n in numbers])
    
    t1_str = f"${fmt_num_latex(target_1)}$"
    t2_str = f"${fmt_num_latex(target_2)}$"
    
    question_text = f"請看下圖，圖中 A, B, C, D 分別代表下列各數：{nums_str}。\n請比較 {t1_str} 和 {t2_str} 的大小（請填入 >、< 或 =）。"
    
    return {
        "question_text": question_text,
        "answer": ans_symbol,
        "correct_answer": ans_symbol,
        "image_base64": img_base64,
        "difficulty": 1
    }

def generate_advanced_application():
    """
    Level 2: 絕對值與相反數的大小比較
    """
    # 生成兩個數，包含負分數
    a = random.randint(2, 8)
    b_num = random.randint(1, 5)
    b_den = random.randint(2, 4)
    b_val = -1 * (b_num / b_den) # 負分數
    
    # 隨機決定題目類型
    q_type = random.choice(['abs_comp', 'opposite_comp'])
    
    if q_type == 'abs_comp':
        # 比較絕對值
        val_1 = -a
        val_2 = b_val
        
        abs_1 = abs(val_1)
        abs_2 = abs(val_2)
        
        if abs_1 > abs_2:
            ans = ">"
        elif abs_1 < abs_2:
            ans = "<"
        else:
            ans = "="
            
        t1_str = f"$|-{a}|$"
        t2_str = f"$|{fmt_num_latex(val_2)}|$"
        
    else:
        # 比較相反數
        val_1 = a
        val_2 = b_val
        
        opp_1 = -val_1
        opp_2 = -val_2
        
        if opp_1 > opp_2:
            ans = ">"
        elif opp_1 < opp_2:
            ans = "<"
        else:
            ans = "="
            
        t1_str = f"${a}$ 的相反數"
        t2_str = f"${fmt_num_latex(val_2)}$ 的相反數"

    question_text = f"請比較 {t1_str} 與 {t2_str} 的大小（請填入 >、< 或 =）。"
    
    # 這裡不一定需要圖，回傳 None
    return {
        "question_text": question_text,
        "answer": ans,
        "correct_answer": ans,
        "difficulty": 2
    }

def check(user_answer, correct_answer):
    """
    自訂核對邏輯：專門處理 > < = 符號
    """
    # 1. 清理字串 (移除空白、全形轉半形)
    u = user_answer.strip().replace(" ", "")
    u = u.replace("＞", ">").replace("＜", "<").replace("＝", "=")
    
    c = correct_answer.strip().replace(" ", "")
    
    # 2. 直接比對符號
    if u == c:
        return {"correct": True, "result": "正確！"}
        
    return {"correct": False, "result": r"""答案錯誤。正確答案為：{ans}""".replace("{ans}", str(correct_answer))}

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
