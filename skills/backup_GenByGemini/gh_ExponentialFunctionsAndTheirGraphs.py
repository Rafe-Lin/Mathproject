import matplotlib.pyplot as plt
import numpy as np
import random
import uuid
import os
from fractions import Fraction

# Create directory for plots if it doesn't exist
PLOT_DIR = "static/generated_plots"
os.makedirs(PLOT_DIR, exist_ok=True)

def generate(level=1):
    """
    生成「指數函數及其圖形」相關題目。
    包含：
    1. 繪製多個指數函數圖形。
    2. 根據圖形特徵提出關於底數大小、函數增減性的問題。
    """
    fig, ax = plt.subplots(figsize=(8, 6))
    
    x = np.linspace(-3, 3, 400) # x軸範圍

    bases = []
    
    # 確保生成的底數具有多樣性：至少一個底數 > 1，至少一個底數 < 1
    # 決定底數 > 1 和 底數 < 1 的數量
    if random.random() < 0.5: # 情境一: 兩個底數 > 1, 一個底數 < 1
        num_gt_1 = 2
        num_lt_1 = 1
    else: # 情境二: 一個底數 > 1, 兩個底數 < 1
        num_gt_1 = 1
        num_lt_1 = 2

    # 從候選列表中選擇唯一底數 > 1
    possible_bases_gt_1 = [2, 3, 4, 5]
    chosen_gt_1 = random.sample(possible_bases_gt_1, num_gt_1)
    bases.extend(chosen_gt_1)

    # 從候選列表中選擇唯一底數 < 1
    possible_bases_lt_1 = [Fraction(1, 2), Fraction(1, 3), Fraction(1, 4)]
    chosen_lt_1 = random.sample(possible_bases_lt_1, num_lt_1)
    bases.extend(chosen_lt_1)

    random.shuffle(bases) # 將底數順序打亂，隨機分配給 A, B, C

    function_labels = ['A', 'B', 'C']
    functions_info = []

    # 繪製函數圖形
    for i, base in enumerate(bases):
        y = base**x
        ax.plot(x, y, label=f'函數 {function_labels[i]}')
        functions_info.append({
            'label': function_labels[i],
            'base': base,
            'is_decreasing': base < 1,
            'is_increasing': base > 1
        })
    
    ax.set_title(r"指數函數 $y=a^x$ 的圖形", fontsize=16)
    ax.set_xlabel('$x$', fontsize=12)
    ax.set_ylabel('$y$', fontsize=12)
    ax.axhline(0, color='gray', linewidth=0.8, linestyle='--') # 繪製水平漸近線 y=0
    ax.axvline(0, color='gray', linewidth=0.8, linestyle='--') # 繪製 Y 軸
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend(loc='upper left', fontsize=10)
    
    # 設置合理的Y軸範圍，以便清楚比較函數行為
    ax.set_ylim(0, 15) 
    ax.set_xlim(-3, 3)

    # 保存圖形
    plot_filename = f"gh_ExponentialFunctionsAndTheirGraphs_{uuid.uuid4()}.png"
    plot_path = os.path.join(PLOT_DIR, plot_filename)
    plt.tight_layout() # 調整佈局以防止標籤重疊
    plt.savefig(plot_path)
    plt.close(fig) # 關閉圖形以釋放記憶體

    img_src = f"/static/generated_plots/{plot_filename}"

    # 根據圖形生成問題
    question_type = random.choice([
        'largest_base', 
        'smallest_base', 
        'decreasing_function', 
        'base_lt_1'
    ])
    
    question_text = f"請觀察下方圖形，其中顯示了三個指數函數 $y=a^x, y=b^x, y=c^x$ (標記為 A, B, C) 的圖形。<br><img src='{img_src}' alt='Exponential Functions Graph'><br><br>"
    correct_answer = ""

    if question_type == 'largest_base':
        # 找出底數最大的函數
        sorted_functions = sorted(functions_info, key=lambda x: x['base'], reverse=True)
        correct_answer = sorted_functions[0]['label']
        question_text += "請問哪個函數的底數 (base) 最大？(請填入函數代號 A, B 或 C)"
    elif question_type == 'smallest_base':
        # 找出底數最小的函數
        sorted_functions = sorted(functions_info, key=lambda x: x['base'])
        correct_answer = sorted_functions[0]['label']
        question_text += "請問哪個函數的底數 (base) 最小？(請填入函數代號 A, B 或 C)"
    elif question_type == 'decreasing_function':
        # 找出遞減函數 (底數 < 1)
        decreasing_funcs = [f for f in functions_info if f['is_decreasing']]
        if not decreasing_funcs: # 如果沒有遞減函數 (所有底數都 > 1)，則改問底數最大的
            sorted_functions = sorted(functions_info, key=lambda x: x['base'], reverse=True)
            correct_answer = sorted_functions[0]['label']
            question_text += "請問哪個函數的底數 (base) 最大？(請填入函數代號 A, B 或 C)"
        else:
            correct_answer = random.choice(decreasing_funcs)['label']
            question_text += "請問哪個函數是嚴格遞減函數？(請填入函數代號 A, B 或 C)"
    elif question_type == 'base_lt_1':
        # 找出底數介於 0 和 1 之間的函數
        base_lt_1_funcs = [f for f in functions_info if f['base'] < 1]
        if not base_lt_1_funcs: # 如果沒有底數介於 0 和 1 之間的函數，則改問底數最大的
            sorted_functions = sorted(functions_info, key=lambda x: x['base'], reverse=True)
            correct_answer = sorted_functions[0]['label']
            question_text += "請問哪個函數的底數 (base) 最大？(請填入函數代號 A, B 或 C)"
        else:
            correct_answer = random.choice(base_lt_1_funcs)['label']
            question_text += r"請問哪個函數的底數 (base) 介於 $0$ 和 $1$ 之間？(請填入函數代號 A, B 或 C)"
            
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查使用者答案是否正確。
    """
    user_answer = user_answer.strip().upper()
    correct_answer = correct_answer.strip().upper()
    
    is_correct = (user_answer == correct_answer)
    
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}