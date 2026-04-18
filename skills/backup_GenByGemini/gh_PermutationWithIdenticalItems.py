import random
import math
from fractions import Fraction

# Helper function for factorial (using math.factorial for efficiency and accuracy)
def _factorial(n):
    return math.factorial(n)

# Helper function for permutations with identical items
def _combinations_with_repetition(total_items, item_counts):
    # total_items is n
    # item_counts is a list [n1, n2, ..., nk]
    numerator = _factorial(total_items)
    denominator = 1
    for count in item_counts:
        denominator *= _factorial(count)
    return numerator // denominator # Use integer division as result must be an integer

def generate_simple_arrangement_problem():
    """
    生成關於「N個事物中，有k種不同種類，第i類有n_i個事物」的排列問題。
    例如：甲乙值班、車廂圖樣、物品排列等。
    """
    num_types = random.choice([2, 3]) # 2 或 3 種不同種類的事物
    
    if num_types == 2:
        # 產生兩種事物的數量，確保數量合理且總數不為零
        counts = [random.randint(2, 5), random.randint(2, 5)] # 例如：[4, 3]
        total_items = sum(counts)
        
        # 選擇情境和標籤，確保情境描述自然且標籤不同
        possible_item_groups = [
            (['甲', '乙'], '值班'),
            (['無尾熊', '貓熊'], '圖樣'),
            (['紅球', '藍球'], '排列'),
            (['黑棋', '白棋'], '排成一列')
        ]
        chosen_group_labels, action_verb = random.choice(possible_item_groups)
        label1, label2 = chosen_group_labels
        
        scenarios = [
            f"{label1}、{label2}兩人負責在{total_items}天年假期間到公司{action_verb}，其中{label1}{action_verb}{counts[0]}天，{label2}{action_verb}{counts[1]}天。",
            f"開往動物園的電聯車有{total_items}節車廂。若打算將其中{counts[0]}節車廂漆上相同的{label1}圖樣，{counts[1]}節車廂漆上相同的{label2}圖樣，則此{total_items}節車廂圖樣的安排共有多少種？",
            f"某個盒子中有{counts[0]}個{label1}和{counts[1]}個{label2}。將這{total_items}個物品排成一列，共有多少種不同的{action_verb}方式？"
        ]
        question_scenario = random.choice(scenarios)
        question_text = f"{question_scenario}請問安排方式共有多少種？"

    else: # num_types == 3
        # 產生三種事物的數量
        counts = [random.randint(2, 4), random.randint(2, 4), random.randint(2, 4)]
        total_items = sum(counts)
        
        # 使用通用物品標籤以避免情境過於複雜
        item_labels_pool = ['紅球', '黃球', '藍球', '綠球', '白球']
        chosen_labels = random.sample(item_labels_pool, 3)
        label1, label2, label3 = chosen_labels
        
        question_text = (
            f"有{counts[0]}個{label1}、{counts[1]}個{label2}和{counts[2]}個{label3}。"
            f"將這{total_items}個物品排成一列，共有多少種不同的排列方式？"
        )

    correct_answer = str(_combinations_with_repetition(total_items, counts))
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_grid_path_basic_problem():
    """
    生成關於棋盤街道捷徑問題的基本款。
    例如：從A到B走捷徑，問總共有多少種走法。
    """
    # 網格尺寸 (向右和向上的步數)
    width = random.randint(3, 7)  # 向右的步數 (x方向)
    height = random.randint(2, 5) # 向上的步數 (y方向)
    
    total_moves = width + height
    
    # 通用的起點和終點標籤
    start_point = 'A'
    end_point = 'B'
    
    question_text = (
        f"在一個棋盤街道中，從${start_point}$點到${end_point}$點走捷徑"
        f"（只能向右或向上走的路徑）。"
        f"若從${start_point}$到${end_point}$必須向右走${width}$步，向上走${height}$步，"
        f"請問共有多少種不同的捷徑走法？"
    )
    
    correct_answer = str(_combinations_with_repetition(total_moves, [width, height]))
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_number_formation_problem():
    """
    生成由特定數字組成的N位數問題，考慮數字0不能排首位的限制。
    """
    num_digits = random.randint(4, 6) # N位數的長度
    
    digits_raw = []
    
    # 確保至少有一個0以應用排除原則，且0的數量不會使問題無效
    # 0的數量至少1個，最多不超過總位數減1 (因為至少需要一個非0數字作首位)
    # 且為避免題目過於複雜，限制0的數量最多為3個
    max_zeros_allowed = num_digits - 1
    num_zeros = random.randint(1, min(max_zeros_allowed, 3)) 
    
    for _ in range(num_zeros):
        digits_raw.append(0)
            
    # 用非零數字 (1-4) 填補剩餘的位數
    for _ in range(num_digits - num_zeros):
        digits_raw.append(random.randint(1, 4))
            
    random.shuffle(digits_raw) # 打亂數字順序，使初始池隨機
    
    # 計算每個數字的出現次數
    digit_counts = {}
    for digit in digits_raw:
        digit_counts[digit] = digit_counts.get(digit, 0) + 1
    
    # 計算所有數字的任意排列總數，不考慮0不能排首位的限制
    all_digit_counts_list = list(digit_counts.values())
    total_permutations = _combinations_with_repetition(num_digits, all_digit_counts_list)
    
    # 計算0排在首位時的排列數
    permutations_with_zero_first = 0
    if 0 in digit_counts and digit_counts[0] > 0:
        # 當0固定在首位時，排列剩餘的 num_digits-1 個數字
        remaining_digits_length = num_digits - 1
        
        # 複製數字計數，並將0的計數減1
        zero_first_counts = digit_counts.copy()
        zero_first_counts[0] -= 1 
        
        # 過濾掉計數為0的數字，並取得剩餘數字的計數列表
        remaining_counts_list = [v for v in zero_first_counts.values() if v > 0]
        
        # 如果剩餘位數大於0，則進行排列計算
        if remaining_digits_length > 0:
            permutations_with_zero_first = _combinations_with_repetition(remaining_digits_length, remaining_counts_list)
            
    # 最終答案 = (所有排列數) - (0排首位的排列數)
    correct_answer = str(total_permutations - permutations_with_zero_first)
    
    # 格式化數字列表用於題目文字，排序後更清晰
    digits_str = ", ".join(map(str, sorted(digits_raw)))
    
    question_text = (
        f"由${num_digits}$個數字 ${digits_str}$ 排成的${num_digits}$位數，共有多少個？"
    )
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    生成「含有相同事物的排列方法」相關題目。
    根據level調整題目類型和難度。
    目前level=1主要涵蓋基礎題型。
    """
    problem_type_choices = ['simple_arrangement', 'grid_path_basic', 'number_formation']
    
    # 針對level 1，可以調整不同題型的出現權重
    if level == 1:
        problem_type = random.choices(problem_type_choices, weights=[0.5, 0.3, 0.2], k=1)[0]
    else: # 未來可針對更高難度設計更複雜的題型或權重
        problem_type = random.choice(problem_type_choices)

    if problem_type == 'simple_arrangement':
        return generate_simple_arrangement_problem()
    elif problem_type == 'grid_path_basic':
        return generate_grid_path_basic_problem()
    elif problem_type == 'number_formation':
        return generate_number_formation_problem()

def check(user_answer, correct_answer):
    """
    檢查使用者答案是否正確。
    支援數字字串的比較。
    """
    # 清理使用者和正確答案的字串（移除空白）
    user_answer_cleaned = user_answer.strip().replace(' ', '')
    correct_answer_cleaned = correct_answer.strip().replace(' ', '')
    
    is_correct = False
    try:
        # 嘗試將答案轉換為浮點數進行數值比較
        if float(user_answer_cleaned) == float(correct_answer_cleaned):
            is_correct = True
    except ValueError:
        # 如果轉換失敗，表示答案不是有效數字，則直接視為不正確
        pass

    result_text = f"完全正確！答案是 ${correct_answer_cleaned}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer_cleaned}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}