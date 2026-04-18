import random
import math
from fractions import Fraction

def generate(level=1):
    """
    生成「組合」相關題目。
    包含：
    1. 直接計算 C(n, k)
    2. 簡單的選取問題
    3. 多類別的選取問題 (例如：從男生女生中選取特定數量)
    4. 將物品分配到不同的組別/容器中
    5. 帶有條件的選取問題 (例如：特定人選或不選，至少一人)
    """
    
    problem_types = []
    if level == 1:
        problem_types = [
            'direct_calculation',
            'simple_selection_word_problem',
            'multi_category_selection_problem_lvl1' # Simplified version for level 1
        ]
    elif level == 2:
        problem_types = [
            'direct_calculation',
            'simple_selection_word_problem',
            'multi_category_selection_problem_lvl2',
            'distinct_group_partition_problem_lvl1',
            'constrained_selection_word_problem'
        ]
    else: # level >= 3, or default for other levels, make it more complex
        problem_types = [
            'direct_calculation',
            'simple_selection_word_problem',
            'multi_category_selection_problem_lvl2',
            'distinct_group_partition_problem_lvl2',
            'constrained_selection_word_problem'
        ]

    chosen_problem_type = random.choice(problem_types)
    
    if chosen_problem_type == 'direct_calculation':
        return generate_direct_combination_problem()
    elif chosen_problem_type == 'simple_selection_word_problem':
        return generate_simple_selection_problem()
    elif chosen_problem_type == 'multi_category_selection_problem_lvl1':
        return generate_multi_category_selection_problem(level=1)
    elif chosen_problem_type == 'multi_category_selection_problem_lvl2':
        return generate_multi_category_selection_problem(level=2)
    elif chosen_problem_type == 'distinct_group_partition_problem_lvl1':
        return generate_distinct_group_partition_problem(level=1)
    elif chosen_problem_type == 'distinct_group_partition_problem_lvl2':
        return generate_distinct_group_partition_problem(level=2)
    elif chosen_problem_type == 'constrained_selection_word_problem':
        return generate_constrained_selection_problem()
    
    # Fallback, should not happen
    return generate_direct_combination_problem()

def generate_direct_combination_problem():
    n = random.randint(7, 18)
    k_raw = random.randint(0, n)
    
    # For variety, sometimes ask for C(n,k) where k is small, sometimes where k is large (closer to n).
    # This implicitly tests C(n, k) = C(n, n-k)
    k = k_raw
    if random.random() < 0.5:
        k = min(k_raw, n - k_raw)
    else:
        k = max(k_raw, n - k_raw)

    # Ensure k is within bounds [0, n] and non-trivial for n > 1
    if n > 1:
        if k == 0 and random.random() < 0.5: k = 1 # make it 1 some of the time
        if k == n and random.random() < 0.5: k = n - 1 # make it n-1 some of the time
    k = max(0, min(k, n)) # Final bounds check
    
    question_text = f"求 $C_{{{n}}}^{{{k}}}$ 的值。"
    correct_answer = str(math.comb(n, k))
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_simple_selection_problem():
    n_total = random.randint(8, 20)
    
    # k should be between 1 and n-1 for non-trivial selection, or 0/n for specific cases.
    # To avoid ValueError in randint(start, end) if start > end, ensure n_total - 1 >= 1
    if n_total < 2:
        k_select = n_total
    else:
        k_select = random.randint(1, n_total - 1)
    
    objects = random.choice([
        ('不同的書', '本'),
        ('手球選手', '人'),
        ('花色不同的撲克牌', '張'),
        ('球隊成員', '人'),
        ('候選人', '人')
    ])
    
    item_type, unit = objects
    
    question_text = (
        f"從 ${n_total}$ {item_type} 中選取 ${k_select}$ {unit}，<br>"
        f"共有多少種選法？"
    )
    correct_answer = str(math.comb(n_total, k_select))
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_multi_category_selection_problem(level):
    if level == 1:
        # e.g., select X boys and Y girls
        n1 = random.randint(3, 6) # e.g., num boys
        n2 = random.randint(3, 6) # e.g., num girls
        
        k1 = random.randint(1, min(n1, 3))
        k2 = random.randint(1, min(n2, 3))
        
        categories = random.choice([
            ('男生', '女生'),
            ('紅球', '白球'),
            ('數學書', '英文書'),
            ('蘋果', '香蕉')
        ])
        cat1_name, cat2_name = categories
        
        question_text = (
            f"某群體有 ${n1}$ 位 {cat1_name} 和 ${n2}$ 位 {cat2_name}。<br>"
            f"現在要選出 ${k1}$ 位 {cat1_name} 和 ${k2}$ 位 {cat2_name}，<br>"
            f"共有多少種選法？"
        )
        
        correct_answer = str(math.comb(n1, k1) * math.comb(n2, k2))

    else: # level >= 2, can add more categories
        n1 = random.randint(4, 8)
        n2 = random.randint(4, 8)
        n3 = random.randint(2, 5) 
        
        k1 = random.randint(1, min(n1, 3))
        k2 = random.randint(1, min(n2, 3))
        k3 = random.randint(1, min(n3, 2)) if n3 > 0 else 0 # k3 can be 0 if n3 is 0 or 1.
        
        categories = random.choice([
            ('資深員工', '普通員工', '實習生'),
            ('紅球', '藍球', '綠球')
        ])
        cat1_name, cat2_name, cat3_name = categories
        
        question_text = (
            f"一個團隊有 ${n1}$ 位 {cat1_name}、${n2}$ 位 {cat2_name} 和 ${n3}$ 位 {cat3_name}。<br>"
            f"若要從中選出 ${k1}$ 位 {cat1_name}、${k2}$ 位 {cat2_name} 和 ${k3}$ 位 {cat3_name} 參與專案，<br>"
            f"共有多少種選法？"
        )
        correct_answer = str(math.comb(n1, k1) * math.comb(n2, k2) * math.comb(n3, k3))
            
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_distinct_group_partition_problem(level):
    n_total = random.randint(6, 12)
    
    if level == 1:
        # Simplest case: split into two distinct groups, or choose for one group and the rest for another.
        # E.g., A room takes k1, B room takes (n-k1).
        # Ensure k1 is valid (at least 1, and leaves at least 1 for k2)
        if n_total < 2: 
            k1 = n_total
            k2 = 0
        else:
            k1 = random.randint(1, n_total - 1) 
            k2 = n_total - k1
        
        objects = random.choice([
            ('人', '間房間'),
            ('書', '位學生'),
            ('隊員', '組')
        ])
        item_unit, container_unit = objects
        
        if container_unit == '間房間':
            question_text = (
                f"將 ${n_total}$ 位 {item_unit} 分配住進 $A$, $B$ 兩{container_unit}，<br>"
                f"$A$ 房住 ${k1}$ {item_unit}，$B$ 房住 ${k2}$ {item_unit}，<br>"
                f"共有多少種分配方案？"
            )
            correct_answer = str(math.comb(n_total, k1)) 
        elif container_unit == '位學生':
             question_text = (
                f"將 ${n_total}$ 本不同的 {item_unit} 分給甲、乙兩{container_unit}。<br>"
                f"甲得 ${k1}$ 本，乙得 ${k2}$ 本，<br>"
                f"共有多少種分法？"
            )
             correct_answer = str(math.comb(n_total, k1))
        else: 
            group_name = random.choice(['隊', '小組'])
            question_text = (
                f"將 ${n_total}$ 位 {item_unit} 分配到兩個不同的 {group_name}，<br>"
                f"第一{group_name}有 ${k1}$ {item_unit}，第二{group_name}有 ${k2}$ {item_unit}，<br>"
                f"共有多少種分法？"
            )
            correct_answer = str(math.comb(n_total, k1))
            
    else: # level >= 2, more groups
        # Split into three distinct groups k1, k2, k3
        if n_total < 3: n_total = random.randint(6, 12) # Ensure n_total >= 3 for 3 groups.
        
        # Iteratively try to find valid k1, k2, k3 such that k1,k2,k3 >= 1 and sum to n_total
        k1, k2, k3 = 0, 0, 0
        attempts = 0
        while (k1 + k2 + k3 != n_total or k1 <= 0 or k2 <= 0 or k3 <= 0) and attempts < 100:
            k1 = random.randint(1, n_total - 2)
            k2 = random.randint(1, n_total - k1 - 1)
            k3 = n_total - k1 - k2
            attempts += 1
        
        # Fallback if the loop struggles (e.g., extremely small n_total after loop)
        if k1 <=0 or k2 <=0 or k3 <=0:
            k1 = n_total // 3
            k2 = (n_total - k1) // 2
            k3 = n_total - k1 - k2
            if k1 == 0: k1 = 1
            if k2 == 0: k2 = 1
            if k3 == 0: k3 = 1
            while k1+k2+k3 > n_total: # Adjust if sum is over
                if k3 > 1: k3 -= 1
                elif k2 > 1: k2 -= 1
                elif k1 > 1: k1 -= 1
                else: break
            while k1+k2+k3 < n_total: # Adjust if sum is under
                if k1 > 0 and k1 < n_total: k1 += 1
                elif k2 > 0 and k2 < n_total: k2 += 1
                elif k3 > 0 and k3 < n_total: k3 += 1
                else: break

        objects = random.choice([
            ('球', '箱'),
            ('員工', '小組'),
            ('書籍', '學生')
        ])
        item_unit, container_unit = objects
        
        if item_unit == '球':
            group_labels = ('第一', '第二', '第三')
            question_text = (
                f"將 ${n_total}$ 顆不同的 {item_unit} 分別裝入三個不同的{container_unit}中。<br>"
                f"{group_labels[0]}{container_unit}裝 ${k1}$ 顆，{group_labels[1]}{container_unit}裝 ${k2}$ 顆，{group_labels[2]}{container_unit}裝 ${k3}$ 顆，<br>"
                f"共有多少種分法？"
            )
        else:
            group_labels = ('甲', '乙', '丙')
            question_text = (
                f"將 ${n_total}$ 位 {item_unit} 分給 {group_labels[0]}、{group_labels[1]}、{group_labels[2]} 三位{container_unit}。<br>"
                f"{group_labels[0]}得 ${k1}$ {item_unit}，{group_labels[1]}得 ${k2}$ {item_unit}，{group_labels[2]}得 ${k3}$ {item_unit}，<br>"
                f"共有多少種分法？"
            )
        
        correct_answer = str(math.comb(n_total, k1) * math.comb(n_total - k1, k2) * math.comb(n_total - k1 - k2, k3))

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_constrained_selection_problem():
    n_total = random.randint(8, 15) # Total people
    k_select = random.randint(4, n_total - 2) # Number of people to select
    
    # Ensure k_select is not too small or too large for meaningful constraints
    if k_select <= 1: k_select = 2
    if k_select >= n_total - 1: k_select = n_total - 2
    
    scenario = random.choice([
        'fixed_selection',          # A must be chosen, B must not be chosen
        'exactly_one_from_pair',    # From A, B, exactly one must be chosen
        'at_least_one_from_group'   # From a special group, at least one must be chosen
    ])
    
    if scenario == 'fixed_selection':
        # E.g., A must be chosen, B must not be chosen
        # Total remaining = n_total - 2
        # Need to select k_select - 1 from n_total - 2 (since A is chosen, B excluded)
        
        # Ensure k_select - 1 is valid for remaining
        if k_select - 1 < 0 or k_select - 1 > n_total - 2:
            return generate_constrained_selection_problem() # Retry if invalid constraints
            
        correct_answer = str(math.comb(n_total - 2, k_select - 1))
        question_text = (
            f"從 ${n_total}$ 位 {random.choice(['選手', '員工', '學生'])} 中選取 ${k_select}$ 人。<br>"
            f"已知其中特定兩人甲、乙，規定甲必須被選中，乙一定不能被選中，<br>"
            f"共有多少種選法？"
        )
        
    elif scenario == 'exactly_one_from_pair':
        # E.g., from A and B, exactly one must be chosen.
        # This implies choosing (A and (k-1 from n-2)) OR (B and (k-1 from n-2))
        # Total = C(1,1)*C(n_total-2, k_select-1) + C(1,1)*C(n_total-2, k_select-1) = 2 * C(n_total-2, k_select-1)
        
        # Ensure k_select - 1 is valid for remaining
        if k_select - 1 < 0 or k_select - 1 > n_total - 2:
            return generate_constrained_selection_problem() # Retry if invalid constraints

        correct_answer = str(2 * math.comb(n_total - 2, k_select - 1))
        question_text = (
            f"從 ${n_total}$ 位 {random.choice(['朋友', '候選人', '組員'])} 中選取 ${k_select}$ 人。<br>"
            f"已知其中特定兩人甲、乙，規定恰好一人被選中，<br>"
            f"共有多少種選法？"
        )
        
    elif scenario == 'at_least_one_from_group':
        # E.g., From n_special special items and n_normal normal items, select k items, at least one special item.
        # Total ways = C(n_total, k_select) - C(n_normal, k_select)
        n_special = random.randint(3, min(5, n_total - 3)) 
        n_normal = n_total - n_special 
        
        # Ensure that it's actually possible to select *only* normal items, otherwise the "at least one" is guaranteed.
        # Also ensure k_select is valid overall.
        if n_special <= 0 or n_normal <= 0 or k_select > n_total or k_select < 1:
            return generate_constrained_selection_problem() # Retry if invalid setup
        
        special_items = random.choice(['女生', '資深員工', '有經驗者'])
        normal_items = random.choice(['男生', '普通員工', '新手'])

        if k_select > n_normal: # If k_select > n_normal, it's impossible to select only normal, so at least one special is guaranteed.
             correct_answer = str(math.comb(n_total, k_select))
             question_text = (
                f"一個團隊有 ${n_special}$ 位 {special_items} 和 ${n_normal}$ 位 {normal_items}。<br>"
                f"要從中選出 ${k_select}$ 人組成小組。<br>"
                f"由於選取人數 (${k_select}$) 超過 {normal_items} 的人數 (${n_normal}$)，<br>"
                f"所以{special_items}一定會被選中至少一位。<br>"
                f"共有多少種選法？"
            )
             
        else: # k_select <= n_normal, calculate total ways - ways to select only normal.
            total_ways = math.comb(n_total, k_select)
            ways_only_normal = math.comb(n_normal, k_select)
            correct_answer = str(total_ways - ways_only_normal)
            
            question_text = (
                f"一個團隊有 ${n_special}$ 位 {special_items} 和 ${n_normal}$ 位 {normal_items}。<br>"
                f"若要從中選出 ${k_select}$ 人組成小組，且小組中至少要有一位 {special_items}，<br>"
                f"共有多少種選法？"
            )
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    try:
        user_ans_int = int(user_answer.strip())
        correct_ans_int = int(correct_answer.strip())
        is_correct = (user_ans_int == correct_ans_int)
    except ValueError:
        is_correct = False

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$。"
    return {"correct": is_correct, "result": result_text, "next_question": True}