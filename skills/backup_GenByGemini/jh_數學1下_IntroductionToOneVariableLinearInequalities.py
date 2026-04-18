import random

def generate(level=1):
    """
    生成「一元一次不等式」相關題目 (標準 LaTeX 範本)。
    包含：
    1. 文字敘述轉換為不等式
    2. 應用情境列式
    3. 範圍表示
    """
    problem_type = random.choice(['phrase_translation', 'word_problem', 'range_problem'])
    
    if problem_type == 'phrase_translation':
        return generate_phrase_translation_problem()
    elif problem_type == 'word_problem':
        return generate_word_problem()
    else: # 'range_problem'
        return generate_range_problem()

def generate_phrase_translation_problem():
    """題型：將文字敘述改寫成不等式。"""
    phrases = [
        ("不超過", "\\le"), ("不大於", "\\le"),
        ("超過", ">"),
        ("不低於", "\\ge"), ("不少於", "\\ge"),
        ("未滿", "<")
    ]
    phrase, symbol = random.choice(phrases)

    # 生成表達式 ax + b
    a = random.randint(2, 9)
    var = random.choice(['x', 'y', 'm', 'p'])
    b = random.randint(-20, 20)
    c = random.randint(10, 50)

    # 組合表達式字串
    if b == 0:
        expr_str = f"{a}{var}"
    elif b > 0:
        expr_str = f"{a}{var} + {b}"
    else:  # b < 0
        expr_str = f"{a}{var} - {abs(b)}"

    # 確保題目有點挑戰性，避免 c 是 a 的倍數
    while c % a == 0:
        c = random.randint(10, 50)

    question_text = f"將下面的敘述改寫成不等式。<br>${expr_str}$ {phrase} ${c}$"
    correct_answer = f"${expr_str} {symbol} {c}$"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_word_problem():
    """題型：依情境列出 x 的不等式。"""
    problem_subtype = random.choice(['shopping', 'combine'])

    if problem_subtype == 'shopping':
        total_money = random.randint(100, 500)
        num_items = random.randint(2, 8)
        # 避免 total_money 是 num_items 的倍數，讓題目更一般化
        while total_money % num_items == 0:
            total_money = random.randint(100, 500)
        
        scenario = random.choice(['not_enough', 'enough_with_change'])
        
        if scenario == 'not_enough':
            situation_text = "付錢時卻發現錢不夠"
            inequality = f"{num_items}x > {total_money}"
        else: # enough_with_change
            situation_text = "錢夠，還有剩下"
            inequality = f"{num_items}x < {total_money}"
            
        question_text = (
            f"依下列情境列出 $x$ 的不等式。（不需化簡）<br>"
            f"小翊帶了 ${total_money}$ 元到商店，買了 ${num_items}$ 個每個售價 $x$ 元的商品，{situation_text}。"
        )
        correct_answer = f"${inequality}$"

    else:  # combine
        person_b_money = random.randint(150, 400)
        item_price = random.randint(500, 1000)
        
        scenario = random.choice(['enough', 'not_enough'])
        
        if scenario == 'enough':
            situation_text = "就有足夠的錢購買"
            inequality = f"x + {person_b_money} \\ge {item_price}"
        else: # not_enough
            situation_text = "的錢仍然不夠買"
            inequality = f"x + {person_b_money} < {item_price}"
            
        question_text = (
            f"依下列情境列出 $x$ 的不等式。（不需化簡）<br>"
            f"小妍身上原有 $x$ 元，如果加上朋友的 ${person_b_money}$ 元後，兩人合買定價 ${item_price}$ 元的禮物，{situation_text}。"
        )
        correct_answer = f"${inequality}$"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_range_problem():
    """題型：用不等式表示一個範圍。"""
    contexts = [
        {
            "name": "空氣品質指標（AQI）",
            "unit": "",
            "var": "x",
            "levels": [
                {"label": "對敏感族群不健康（橘色）", "range": (101, 150)},
                {"label": "對所有族群不健康（紅色）", "range": (151, 200)},
                {"label": "非常不健康（紫色）", "range": (201, 300)}
            ]
        },
        {
            "name": "考試成績",
            "unit": "分",
            "var": "y",
            "levels": [
                {"label": "優等", "range": (90, 100)},
                {"label": "甲等", "range": (80, 89)},
                {"label": "乙等", "range": (70, 79)}
            ]
        }
    ]

    context = random.choice(contexts)
    level = random.choice(context['levels'])
    var = context['var']
    lower, upper = level['range']

    question_text = (
        f"已知「{context['name']}」的等級對照如下：<br>"
        f"{level['range'][0]}∼{level['range'][1]}: ${level['label']}<br>"
        f"若某次的{context['name']}為 ${var}${context['unit']}，且等級為「{level['label']}」，試以不等式表示 ${var}$ 的範圍。"
    )
    correct_answer = f"${lower} \\le {var} \\le {upper}$"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查一元一次不等式答案是否正確。
    """
    def normalize_inequality_string(s):
        # 移除前後空白、錢字號、並轉為小寫
        s = s.strip().lower().replace('$', '')
        # 移除所有內嵌空白字元
        s = "".join(s.split())
        # 標準化不等式符號，將 LaTeX 轉為 ASCII
        s = s.replace('\\le', '<=').replace('\\leq', '<=')
        s = s.replace('\\ge', '>=').replace('\\geq', '>=')
        s = s.replace('=<', '<=').replace('=>', '>=')
        return s

    user_normalized = normalize_inequality_string(user_answer)
    correct_normalized = normalize_inequality_string(correct_answer)

    is_correct = (user_normalized == correct_normalized)

    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}
