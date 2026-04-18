import random
import io
import base64
from matplotlib.figure import Figure # [修正 1] 改用物件導向繪圖

# ==============================================================================
# GOLD STANDARD TEMPLATE v8.9 (Fixed for NumberLine)
# ==============================================================================

def generate(level=1):
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
    Level 1: 識別數線上的點
    """
    center = random.randint(-5, 5)
    range_val = 6
    min_val = center - range_val // 2
    max_val = center + range_val // 2
    
    target_val = random.randint(min_val + 1, max_val - 1)
    
    # [修正 2] 獨立 Figure
    fig = Figure(figsize=(8, 2))
    ax = fig.subplots()
    
    ax.hlines(0, min_val - 1, max_val + 1, colors='black', linewidth=1.5)
    ax.plot(max_val + 1, 0, ">k", markersize=10, clip_on=False)
    ax.plot(min_val - 1, 0, "<k", markersize=10, clip_on=False)

    ticks = range(min_val, max_val + 1)
    for t in ticks:
        ax.plot([t, t], [-0.1, 0.1], 'k', linewidth=1)
        ax.text(t, -0.4, str(t), ha='center', va='top', fontsize=10)

    ax.plot(target_val, 0, 'ro', markersize=8)
    ax.text(target_val, 0.3, "P", ha='center', va='bottom', color='red', fontsize=12, fontweight='bold')

    ax.axis('off')
    ax.set_xlim(min_val - 1.5, max_val + 1.5)
    ax.set_ylim(-1, 1)

    img_base64 = get_base64_image(fig)

    question_text = f"請寫出數線上 P 點的座標。"
    ans_str = str(target_val)

    return {
        "question_text": question_text,
        "answer": ans_str,
        "correct_answer": ans_str,
        "image_base64": img_base64,
        "difficulty": 1
    }

def generate_advanced_application():
    """
    Level 2: 數線上的距離與運算
    """
    a = random.randint(-10, 5)
    distance = random.randint(3, 8)
    direction = random.choice(['right', 'left'])
    
    # 計算正確答案
    if direction == 'right':
        ans = a + distance
        dir_text = "右"
    else:
        ans = a - distance
        dir_text = "左"

    # [修正 2] 獨立 Figure
    fig = Figure(figsize=(8, 2))
    ax = fig.subplots()
    
    vals = [a, ans]
    min_val = min(vals) - 2
    max_val = max(vals) + 2
    
    ax.hlines(0, min_val, max_val, colors='black', linewidth=1.5)
    ax.plot(max_val, 0, ">k", markersize=10, clip_on=False)
    ax.plot(min_val, 0, "<k", markersize=10, clip_on=False)
    
    ticks = range(int(min_val), int(max_val) + 1)
    for t in ticks:
        if t == a:
            ax.plot([t, t], [-0.1, 0.1], 'k', linewidth=1)
            ax.text(t, -0.4, str(t), ha='center', va='top', fontsize=10)
        else:
            ax.plot([t, t], [-0.05, 0.05], 'k', linewidth=0.5)

    ax.plot(a, 0, 'bo', markersize=8)
    ax.text(a, 0.3, "A", ha='center', va='bottom', color='blue', fontsize=12)

    mid = (a + ans) / 2
    # annotate 用法與 plt 相同
    ax.annotate('', xy=(ans, 0.1), xytext=(a, 0.1),
                arrowprops=dict(arrowstyle="->", connectionstyle=f"arc3,rad={-0.3 if direction=='right' else 0.3}", color='green', lw=2))
    
    ax.text(mid, 0.6, f"{distance}", ha='center', va='bottom', color='green')

    ax.axis('off')
    ax.set_ylim(-1, 2)

    img_base64 = get_base64_image(fig)

    # 題目使用 LaTeX 語法
    question_text = f"數線上有一點 $A$ 座標為 ${a}$，向{dir_text}移動 ${distance}$ 個單位長到達點 $B$，求點 $B$ 的座標。"

    # [修正 3] 這裡原本是 target_val (致命錯誤)，現在改為 ans
    ans_str = str(ans)

    return {
        "question_text": question_text,
        "answer": ans_str,         # ✅ 修正
        "correct_answer": ans_str, # ✅ 修正
        "image_base64": img_base64,
        "difficulty": 2
    }

def check(user_answer, correct_answer):
    u = user_answer.strip().replace(" ", "")
    c = correct_answer.strip().replace(" ", "")
    if u == c: return {"correct": True, "result": "正確！"}
    try:
        if abs(float(u) - float(c)) < 1e-6:
            return {"correct": True, "result": "正確！"}
    except:
        pass
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
