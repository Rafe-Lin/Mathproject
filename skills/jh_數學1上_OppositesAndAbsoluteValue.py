# ==============================================================================
# ID: jh_數學1上_OppositesAndAbsoluteValue
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 80.18s | RAG: 5 examples
# Created At: 2026-01-12 18:50:14
# Fix Status: [Clean Pass]
# Fixes: Regex=0, Logic=0
#==============================================================================

import random
import io
import base64
from matplotlib.figure import Figure

# ==============================================================================
# GOLD STANDARD TEMPLATE v8.9 (List Support Edition)
# Topic: Opposites and Absolute Value (相反數與絕對值)
# ==============================================================================

def generate(level=1):
    """
    Main Dispatcher
    Level 1: 基礎運算 (絕對值計算、相反數)
    Level 2: 應用題 (列舉範圍內的整數、比較大小)
    """
    if level == 1:
        return generate_basic_concept()
    else:
        return generate_advanced_application()

def get_base64_image(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    return img_str

def generate_basic_concept():
    """
    Level 1: 基礎題
    1. 寫出相反數
    2. 計算絕對值
    """
    q_type = random.choice(['opposite', 'absolute', 'absolute_val'])
    
    # 建立獨立 Figure (Thread-Safe)
    fig = Figure(figsize=(8, 1.5))
    ax = fig.subplots()
    
    target_val = random.randint(-15, 15)
    if target_val == 0: target_val = 5

    # 繪製基本數線
    limit = abs(target_val) + 3
    ax.hlines(0, -limit, limit, colors='black', linewidth=1.5)
    ax.plot(limit, 0, ">k", markersize=10, clip_on=False)
    ax.plot(-limit, 0, "<k", markersize=10, clip_on=False)
    ax.plot([0, 0], [-0.1, 0.1], 'k', linewidth=1)
    ax.text(0, -0.4, "0", ha='center', va='top', fontsize=10)
    
    # 標示目標點
    ax.plot(target_val, 0, 'bo', markersize=8)
    ax.text(target_val, 0.3, str(target_val), ha='center', va='bottom', color='blue', fontsize=12)
    ax.axis('off')

    if q_type == 'opposite':
        question_text = f"寫出 ${target_val}$ 的相反數。"
        ans_str = str(-target_val)
    elif q_type == 'absolute':
        question_text = f"計算 $|{target_val}|$ 的值。"
        ans_str = str(abs(target_val))
    else:
        # 比較兩數絕對值 (簡單版)
        v1 = random.randint(-10, -1)
        v2 = random.randint(1, 10)
        question_text = f"比較 $|{v1}|$ 與 $|{v2}|$ 的大小 (請填入 >、< 或 =)。"
        if abs(v1) > abs(v2): ans_str = ">"
        elif abs(v1) < abs(v2): ans_str = "<"
        else: ans_str = "="
        
        # 重新畫圖標示兩點
        ax.clear()
        ax.hlines(0, -12, 12, colors='black', linewidth=1.5)
        ax.plot(12, 0, ">k", markersize=10, clip_on=False)
        ax.plot(-12, 0, "<k", markersize=10, clip_on=False)
        ax.plot(0, 0, '|k', markersize=10)
        ax.text(0, -0.4, "0", ha='center', va='top')
        ax.plot(v1, 0, 'bo', label=str(v1))
        ax.plot(v2, 0, 'ro', label=str(v2))
        ax.axis('off')

    img_base64 = get_base64_image(fig)

    return {
        "question_text": question_text,
        "answer": ans_str,
        "correct_answer": ans_str,
        "image_base64": img_base64,
        "difficulty": 1
    }

def generate_advanced_application():
    """
    Level 2: 您要求的特定題型
    1. 已知 c 為負整數，且 |c| < k，求 c
    2. 寫出絕對值小於 k 的所有整數
    3. 比較兩數絕對值 (含計算)
    """
    q_type = random.choice(['find_c', 'list_int', 'compare_abs'])
    
    fig = Figure(figsize=(8, 1.5))
    ax = fig.subplots()
    ax.axis('off') # 預設關閉，有需要再畫

    if q_type == 'find_c':
        k = random.randint(3, 8)
        question_text = f"已知 $c$ 為負整數，且 $|c| < {k}$，則 $c$ 可能是多少？(請列出所有答案，用逗號隔開)"
        # 答案是 -1, -2, ..., -(k-1)
        ans_list = [str(-i) for i in range(1, k)]
        # 排序方便閱讀 (數學上集合無序，但習慣由小到大或由大到小)
        ans_list.sort(key=lambda x: int(x)) 
        ans_str = ", ".join(ans_list)

    elif q_type == 'list_int':
        k = random.randint(3, 6)
        question_text = f"寫出絕對值小於 ${k}$ 的所有整數。(請用逗號隔開)"
        # 答案是 -(k-1) ... 0 ... (k-1)
        ans_ints = range(-(k-1), k)
        ans_list = [str(x) for x in ans_ints]
        ans_str = ", ".join(ans_list)

    else:
        # 比較題：分別寫出 -A 和 -B 的絕對值，並比較大小
        a = random.randint(2, 9)
        b = random.randint(2, 9)
        while a == b: b = random.randint(2, 9)
        v1, v2 = -a, -b # 都是負數
        
        # 為了讓 check 方便，我們引導學生回答最後的比較結果即可，或者格式固定
        # 但既然是自動批改，建議簡化為：「比較 |-a| 與 |-b| 的大小」
        question_text = f"比較 $|{v1}|$ 與 $|{v2}|$ 的大小 (請填入 >、< 或 =)。"
        if abs(v1) > abs(v2): ans_str = ">"
        else: ans_str = "<"

    return {
        "question_text": question_text,
        "answer": ans_str,
        "correct_answer": ans_str,
        "difficulty": 2
    }

def check(user_answer, correct_answer):
    """
    Smart Checker: 支援「列舉清單」的批改
    """
    u = user_answer.strip().replace(" ", "").replace("，", ",") # 全形逗號轉半形
    c = correct_answer.strip().replace(" ", "").replace("，", ",")
    
    # 1. 簡單比對
    if u == c:
        return {"correct": True, "result": "正確！"}
    
    # 2. 清單比對 (處理順序不同：例如 "-1,-2" vs "-2,-1")
    if "," in c:
        try:
            # 將使用者輸入和正確答案都切割成集合 (Set)
            u_set = set(u.split(','))
            c_set = set(c.split(','))
            
            # 移除空字串 (避免尾端逗號)
            u_set.discard('')
            c_set.discard('')
            
            if u_set == c_set:
                return {"correct": True, "result": "正確！"}
        except:
            pass
            
    # 3. 符號比對
    u = u.replace("＞", ">").replace("＜", "<").replace("＝", "=")
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
