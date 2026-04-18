import random
import re

def generate(level=1):
    """
    生成「二元一次聯立方程式應用題」相關題目。
    包含：
    1. 總價與總數問題
    2. 數量對調問題
    3. 分裝剩餘與不足問題
    4. 年齡問題 (可能無解)
    """
    problem_type = random.choice(['cost_total', 'swapped_order', 'grouping', 'age'])
    
    if problem_type == 'cost_total':
        return generate_cost_total_problem()
    elif problem_type == 'swapped_order':
        return generate_swapped_order_problem()
    elif problem_type == 'grouping':
        return generate_grouping_problem()
    else: # age
        return generate_age_problem()

def generate_cost_total_problem():
    """題型：總價與總數問題 (壽司例題)"""
    item_choices = [("壽司", "盤"), ("原子筆", "枝"), ("麵包", "個"), ("飲料", "瓶")]
    (item_name, unit) = random.choice(item_choices)

    price1 = random.randint(2, 5) * 10
    price2 = price1 + random.randint(1, 4) * 10
    
    x = random.randint(3, 8)
    y = random.randint(3, 8)

    total_items = x + y
    total_cost = price1 * x + price2 * y

    question_text = f"某商店舉辦優惠，{price1} 元的{item_name}與 {price2} 元的{item_name}兩種商品熱賣中。小翊只記得一共買了 {total_items} {unit}，且花費 {total_cost} 元。<br>試問小翊各買了幾{unit} {price1} 元及 {price2} 元的商品？(請依價格順序回答數量)"
    
    answer_text = f"{price1} 元的商品 {x} {unit}，{price2} 元的商品 {y} {unit}。"
    
    return {
        "question_text": question_text,
        "answer": answer_text,
        "correct_answer": answer_text
    }

def generate_swapped_order_problem():
    """題型：數量對調問題 (炸雞披薩例題)"""
    item1_name, item2_name = random.choice([("炸雞", "披薩"), ("漢堡", "薯條"), ("小說", "漫畫")])
    unit1 = "桶" if item1_name == "炸雞" else "個" if item1_name == "漢堡" else "本"
    unit2 = "個" if item2_name == "披薩" else "份" if item2_name == "薯條" else "本"

    while True:
        x = random.randint(10, 50) * 10
        y = random.randint(10, 50) * 10
        if x == y: continue
        
        c = random.randint(2, 4)
        d = random.randint(2, 4)
        if c == d: continue

        total_cost1 = x + y
        difference = (d - c) * (x - y)
        
        if difference != 0: break

    direction = "多花了" if difference > 0 else "少花了"
    abs_diff = abs(difference)

    question_text = f"阿賢之前在快餐店買 1 {unit1}{item1_name}與 1 {unit2}{item2_name}共要 {total_cost1} 元。某天阿賢在同家店點了 {c} {unit1}{item1_name}與 {d} {unit2}{item2_name}，但店員將數量聽反了，送來 {d} {unit1}{item1_name}與 {c} {unit2}{item2_name}，使阿賢{direction} {abs_diff} 元。<br>試問 1 {unit1}{item1_name}與 1 {unit2}{item2_name}各是多少元？(請依序回答{item1_name}、{item2_name}的價格)"
    answer_text = f"1 {unit1}{item1_name} {x} 元，1 {unit2}{item2_name} {y} 元。"

    return {
        "question_text": question_text,
        "answer": answer_text,
        "correct_answer": answer_text
    }

def generate_grouping_problem():
    """題型：分裝剩餘與不足問題 (蘋果禮盒例題)"""
    item_name, container_name = random.choice([("蘋果", "禮盒"), ("學生", "帳篷"), ("果凍", "盤子"), ("餅乾", "袋子")])
    unit_item = "顆" if item_name == "蘋果" else "位" if item_name == "學生" else "個"
    unit_container = "個"

    while True:
        y = random.randint(4, 10)
        n1 = random.randint(5, 9)
        n2 = n1 + random.randint(2, 4)
        total_rem = (n2 - n1) * y
        
        r1_max = min(n1 - 1, total_rem - 1)
        if r1_max < 1: continue
        
        r1 = random.randint(1, r1_max)
        r2 = total_rem - r1
        
        if 1 <= r2 < n2:
            break
            
    x = n1 * y + r1
    
    question_text = f"好吃水果行買進一批{item_name}，老闆想用{container_name}分裝銷售。<br>若每{unit_container}{container_name}裝 {n1} {unit_item}，則會剩下 {r1} {unit_item}沒有{container_name}裝；<br>若每{unit_container}{container_name}都裝滿 {n2} {unit_item}，則會不足 {r2} {unit_item}。<br>試問這批{item_name}共有多少{unit_item}？{container_name}共有多少{unit_container}？(請依序回答{item_name}數量、{container_name}數量)"
    answer_text = f"{item_name}共有 {x} {unit_item}，{container_name}共有 {y} {unit_container}。"
    
    return {
        "question_text": question_text,
        "answer": answer_text,
        "correct_answer": answer_text
    }

def generate_age_problem():
    """題型：年齡問題 (可能無解)"""
    if random.random() < 0.25:
        return generate_age_problem_unsolvable()
    else:
        return generate_age_problem_solvable()

def generate_age_problem_solvable():
    """生成有解的年齡問題"""
    while True:
        y = random.randint(8, 15)
        x = y + random.randint(3, 20)
        
        t1_options = []
        for t1_cand in range(1, 12):
            if (x + t1_cand) % (y + t1_cand) == 0:
                k1 = (x + t1_cand) // (y + t1_cand)
                if 1 < k1 < 10: t1_options.append((t1_cand, k1))
        
        t2_options = []
        for t2_cand in range(1, y - 2):
            if (x - t2_cand) > 0 and (y-t2_cand) > 0 and (x - t2_cand) % (y - t2_cand) == 0:
                k2 = (x - t2_cand) // (y - t2_cand)
                if 1 < k2 < 10: t2_options.append((t2_cand, k2))
        
        if t1_options and t2_options:
            t1, k1 = random.choice(t1_options)
            t2, k2 = random.choice(t2_options)
            if k1 != k2: break
    
    person1, person2 = random.choice([("姐姐", "小翊"), ("老師", "學生"), ("父親", "兒子")])

    question_text = f"{person1}跟{person2}說：「{t1} 年後，我的年齡是你年齡的 {k1} 倍；而 {t2} 年前，我的年齡是你年齡的 {k2} 倍。」<br>試問{person1}與{person2}現在各是幾歲？(請依序回答{person1}、{person2}的年齡)"
    answer_text = f"{person1}現在 {x} 歲，{person2}現在 {y} 歲。"
    
    return {
        "question_text": question_text,
        "answer": answer_text,
        "correct_answer": answer_text
    }

def generate_age_problem_unsolvable():
    """生成無解(年齡為負)的年齡問題"""
    while True:
        t1 = random.randint(5, 12)
        k1 = random.randint(2, 4)
        t2 = random.randint(2, 5)
        a = random.randint(3, 5)
        b = random.randint(2, 4)
        c = random.randint(40, 80)
        
        # System: x - k1*y = C1 and ax - by = C2
        det = a * k1 - b
        if det == 0: continue
        
        C1 = t1 * (k1 - 1)
        C2 = (a - b) * t2 + c
        
        x_sol = (k1 * C2 - b * C1) / det
        y_sol = (C2 - a * C1) / det
        
        if y_sol < 0 and -5 < y_sol and x_sol > 5:
            person1, person2 = random.choice([("姐姐", "小翊"), ("老師", "學生"), ("父親", "兒子")])
            question_text = f"{person1}跟{person2}說：「{t1} 年後，我的年齡會是你年齡的 {k1} 倍；但 {t2} 年前，我年齡的 {a} 倍比你年齡的 {b} 倍還多 {c} 歲」。<br>試問{person2}現在幾歲？"
            answer_text = "此題無解。"
            return {
                "question_text": question_text,
                "answer": answer_text,
                "correct_answer": answer_text
            }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    可以處理 "無解" 或包含多個數值的答案。
    """
    is_correct = False
    user_answer_clean = user_answer.strip().replace(" ", "")
    correct_answer_clean = correct_answer.strip().replace(" ", "")

    if "無解" in correct_answer_clean:
        if "無解" in user_answer_clean or "no" in user_answer_clean.lower():
            is_correct = True
    else:
        try:
            user_nums = sorted(map(float, re.findall(r'-?\d+\.?\d*', user_answer_clean)))
            correct_nums = sorted(map(float, re.findall(r'-?\d+\.?\d*', correct_answer_clean)))
            
            if user_nums and user_nums == correct_nums:
                is_correct = True
        except (ValueError, IndexError):
            is_correct = False

    if is_correct:
        result_text = f"完全正確！答案是 {correct_answer}"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer}"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}
