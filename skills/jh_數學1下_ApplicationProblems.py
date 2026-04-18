# ==============================================================================
# ID: jh_數學1下_ApplicationProblems
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Logic: Dynamic Age & Application Problems (Reinforced)
# Version: V10.2.1 (Full Recovery)
# Created At: 2026-01-15 13:55:00
#==============================================================================

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

# [V11.6 Elite Font & Style]
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
plt.rcParams['axes.unicode_minus'] = False

# --- 基礎工具函式 ---
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

# --- 題型一：壽司問題 (Mirror Ex 1) ---
def _generate_type1_sushi_problem():
    cost_A = random.choice([20, 30, 40])
    cost_B = random.choice([50, 60, 70])
    x_ans = random.randint(2, 7) 
    y_ans = random.randint(2, 7) 
    total_plates = x_ans + y_ans
    total_cost = cost_A * x_ans + cost_B * y_ans
    person_name = random.choice(['小翊', '巴奈', '阿賢', '小明'])
    item_name_A = random.choice(['30 元', 'A 款', '小盤'])
    item_name_B = random.choice(['50 元', 'B 款', '大盤'])
    
    template = r"某迴轉壽司店舉辦週年大優惠，{item_A_cost} 的壽司一律 ${costA}$ 元；{item_B_cost} 的壽司一律 ${costB}$ 元。{person_name} 只記得一共吃了 ${total_P}$ 盤，且花費 ${total_C}$ 元。試問 {person_name} 各吃了幾盤 {item_A_cost} 及 {item_B_cost} 的壽司？"
    question_text = template.replace("{item_A_cost}", item_name_A).replace("{costA}", str(cost_A)).replace("{item_B_cost}", item_name_B).replace("{costB}", str(cost_B)).replace("{person_name}", person_name).replace("{total_P}", str(total_plates)).replace("{total_C}", str(total_cost))
    correct_answer = f"{item_name_A} 的壽司 {x_ans} 盤，{item_name_B} 的壽司 {y_ans} 盤。"
    return {"question_text": question_text, "correct_answer": correct_answer, "answer": f"{x_ans},{y_ans}", "image_base64": ""}

# --- 題型二：炸雞披薩問題 (Mirror Ex 2) ---
def _generate_type2_chicken_pizza_problem():
    c_ans = random.randint(200, 400)
    p_ans = random.randint(c_ans + 50, c_ans + 150)
    total_cost_initial = c_ans + p_ans
    ordered_num_A = random.randint(2, 5)
    ordered_num_B = random.randint(2, 5)
    while ordered_num_A == ordered_num_B: ordered_num_B = random.randint(2, 5)
    actual_num_A, actual_num_B = ordered_num_B, ordered_num_A
    cost_diff = (actual_num_A * c_ans + actual_num_B * p_ans) - (ordered_num_A * c_ans + ordered_num_B * p_ans)
    diff_phrase = "多花了" if cost_diff > 0 else "少花了"
    person_name = random.choice(['阿賢', '巴奈', '小明', '張先生'])
    
    template = r"{person_name} 之前在快餐店買 1 桶炸雞與 1 個披薩共要 ${initial_cost}$ 元。某天 {person_name} 在同家店點了 ${ordered_A}$ 桶炸雞與 ${ordered_B}$ 個披薩，但店員將數量聽反了，送來 ${actual_A}$ 桶炸雞與 ${actual_B}$ 個披薩，使 {person_name} {diff_phrase} ${diff_cost}$ 元。試問炸雞與披薩各是多少元？"
    question_text = template.replace("{person_name}", person_name).replace("{initial_cost}", str(total_cost_initial)).replace("{ordered_A}", str(ordered_num_A)).replace("{ordered_B}", str(ordered_num_B)).replace("{actual_A}", str(actual_num_A)).replace("{actual_B}", str(actual_num_B)).replace("{diff_phrase}", diff_phrase).replace("{diff_cost}", str(abs(cost_diff)))
    correct_answer = f"1 桶炸雞 {c_ans} 元，1 個披薩 {p_ans} 元。"
    return {"question_text": question_text, "correct_answer": correct_answer, "answer": f"{c_ans},{p_ans}", "image_base64": ""}

# --- 題型三：蘋果裝箱問題 (Mirror Ex 3) ---
def _generate_type3_apple_box_problem():
    while True:
        B_ans = random.randint(3, 15)
        n1 = random.randint(5, 10)
        r1 = random.randint(1, n1 - 1)
        A_ans = n1 * B_ans + r1
        n2 = random.randint(n1 + 1, n1 + 5)
        s2 = n2 * B_ans - A_ans
        if 0 < s2 < n2: break
    template = r"某水果行買進一批蘋果，老闆想用禮盒分裝。若每 ${n1}$ 顆裝成一盒，則會剩下 ${r1}$ 顆；若每盒裝滿 ${n2}$ 顆，則會不足 ${s2}$ 顆。試問蘋果共有多少顆？盒子共有多少個？"
    question_text = template.replace("{n1}", str(n1)).replace("{r1}", str(r1)).replace("{n2}", str(n2)).replace("{s2}", str(s2))
    correct_answer = f"蘋果共有 {A_ans} 顆，盒子共有 {B_ans} 個。"
    return {"question_text": question_text, "correct_answer": correct_answer, "answer": f"{A_ans},{B_ans}", "image_base64": ""}

# --- 題型四：年齡問題 (動態有解/無解判定) ---
def _generate_type4_age_problem():
    """
    [V10.2 修復] 逆向出題邏輯：先定解，後定題
    """
    is_solvable_target = random.choice([True, False])
    
    # 預設基礎參數 (基準人物：小翊 J, 姐姐 S)
    a2 = random.randint(2, 5)   
    J_ans = random.randint(a2 + 2, 15) 
    S_ans = J_ans + random.randint(2, 10) 
    
    if is_solvable_target:
        # --- 有解路徑 ---
        a1 = random.randint(3, 10)
        m1 = random.randint(2, 3)
        S_ans = m1 * (J_ans + a1) - a1 
        m2 = random.randint(2, 4)
        m3 = random.randint(1, m2)
        k_val = m2 * (S_ans - a2) - m3 * (J_ans - a2)
    else:
        # --- 無解路徑 (隨機生成參數，極大機率導致無解) ---
        a1, m1 = random.randint(5, 15), random.randint(2, 4)
        a2, m2, m3 = random.randint(2, 5), random.randint(2, 5), random.randint(1, 3)
        k_val = random.randint(10, 100)

    # --- 克拉瑪公式驗證 (Cramer's Rule) ---
    # 1. S - m1*J = (m1-1)*a1
    # 2. m2*S - m3*J = (m2-m3)*a2 + k_val
    det = (1 * (-m3)) - ((-m1) * m2)
    is_solvable_actually = False
    
    if det != 0:
        b1 = (m1 - 1) * a1
        b2 = (m2 - m3) * a2 + k_val
        real_J = (1 * b2 - m2 * b1) / det
        real_S = (b1 * (-m3) - (-m1) * b2) / det
        
        # 物理意義檢查：年齡需為正整數、姐姐比弟弟大、現在需大於回溯年份
        if real_J > a2 and real_S > real_J and real_J.is_integer():
            is_solvable_actually = True
            J_ans = int(real_J)

    person_A, person_B = "姐姐", "小翊"
    template = r"{person_A}跟{person_B}說：「${a1}$ 年後，我年齡是你年齡的 ${m1}$ 倍；而 ${a2}$ 年前，我年齡的 ${m2}$ 倍比你年齡的 ${m3}$ 倍多 ${k_val}$ 歲」。試問{person_B}現在幾歲？"
    
    question_text = template.replace("{person_A}", person_A).replace("{person_B}", person_B)\
                            .replace("{a1}", str(a1)).replace("{m1}", str(m1))\
                            .replace("{a2}", str(a2)).replace("{m2}", str(m2))\
                            .replace("{m3}", str(m3)).replace("{k_val}", str(k_val))

    if is_solvable_actually:
        correct_answer = r"{person_B}現在 {J} 歲。".replace("{person_B}", person_B).replace("{J}", str(J_ans))
    else:
        correct_answer = "此題無解"

    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": str(J_ans) if is_solvable_actually else "此題無解",
        "image_base64": ""
    }

# --- 頂層函式區 ---

def generate(level=1):
    problem_types = [
        _generate_type1_sushi_problem,
        _generate_type2_chicken_pizza_problem,
        _generate_type3_apple_box_problem,
        _generate_type4_age_problem,
    ]
    return random.choice(problem_types)()

def check(user_answer, correct_answer):
    """
    [V10.2 修復] 強化型閱卷引擎
    """
    if user_answer is None: return {"correct": False, "result": "未提供答案。"}
    
    def _clean(s):
        return str(s).strip().replace(" ", "").replace("，", ",").replace("$", "").lower()

    u = _clean(user_answer)
    c = _clean(correct_answer)

    # 1. 關鍵字「無解」優先判定
    if "無解" in c:
        return {"correct": "無解" in u, "result": "正確！" if "無解" in u else "答案錯誤。此題無解"}

    # 2. 數值提取比對
    u_nums = re.findall(r"\d+", u)
    c_nums = re.findall(r"\d+", c)
    if u_nums and c_nums and u_nums == c_nums:
        return {"correct": True, "result": "正確！"}
    
    # 3. 兜底字串比對
    if u == c: return {"correct": True, "result": "正確！"}
    
    return {"correct": False, "result": r"答案錯誤。正確答案為：{ans}".replace("{ans}", str(correct_answer))}

# [Auto-Injected Patch v11.0] Universal Return, Linebreak & Handwriting Fixer
def _patch_all_returns(func):
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        if func.__name__ == 'check' and isinstance(res, bool):
            return {'correct': res, 'result': '正確！' if res else '答案錯誤'}
        if isinstance(res, dict):
            if 'question_text' in res and isinstance(res['question_text'], str):
                res['question_text'] = re.sub(r'\\n', '\n', res['question_text'])
            c_ans = str(res.get('correct_answer', ''))
            triggers = ['^', '/', ',', '|', '(', '[', '{', '\\']
            has_prompt = "手寫" in res.get('question_text', '')
            should_inject = (res.get('input_mode') == 'handwriting') or any(t in c_ans for t in triggers)
            if should_inject and not has_prompt:
                res['input_mode'] = 'handwriting'
                res['question_text'] = res['question_text'].rstrip() + "\n(請在手寫區作答!)"
            if 'answer' not in res and 'correct_answer' in res: res['answer'] = res['correct_answer']
            if 'image_base64' not in res: res['image_base64'] = ""
        return res
    return wrapper

for _name, _func in list(globals().items()):
    if callable(_func) and (_name.startswith('generate') or _name == 'check'):
        globals()[_name] = _patch_all_returns(_func)