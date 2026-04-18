import random
import math
from fractions import Fraction

def generate(level=1):
    """
    生成「離散型隨機變數」相關題目。
    根據 `level` 參數調整題目難度。
    """
    problem_type_choices = []
    if level == 1:
        # 基本概念：隨機變數的可能取值、事件描述、簡單機率計算 (硬幣)
        problem_type_choices = ['coin_possible_values', 'coin_describe_event', 'coin_calculate_probability']
    elif level == 2:
        # 稍複雜的概念：隨機變數的可能取值、事件描述、機率計算 (從袋中取球，不放回)
        problem_type_choices = ['ball_draw_possible_values', 'ball_draw_describe_event', 'ball_draw_calculate_probability']
    elif level == 3:
        # 進階概念：機率分布表、多個機率的總和 (從袋中取球，直到特定條件，不放回)
        problem_type_choices = ['ball_until_red_distribution_table', 'ball_until_red_calculate_probability']
    else: # Default for level >= 3
        problem_type_choices = [
            'coin_possible_values', 'coin_describe_event', 'coin_calculate_probability',
            'ball_draw_possible_values', 'ball_draw_describe_event', 'ball_draw_calculate_probability',
            'ball_until_red_distribution_table', 'ball_until_red_calculate_probability'
        ]
        
    problem_type = random.choice(problem_type_choices)

    if problem_type == 'coin_possible_values':
        return _generate_coin_possible_values_problem()
    elif problem_type == 'coin_describe_event':
        return _generate_coin_describe_event_problem()
    elif problem_type == 'coin_calculate_probability':
        return _generate_coin_calculate_probability_problem()
    elif problem_type == 'ball_draw_possible_values':
        return _generate_ball_draw_possible_values_problem()
    elif problem_type == 'ball_draw_describe_event':
        return _generate_ball_draw_describe_event_problem()
    elif problem_type == 'ball_draw_calculate_probability':
        return _generate_ball_draw_calculate_probability_problem()
    elif problem_type == 'ball_until_red_distribution_table':
        return _generate_ball_until_red_distribution_table_problem()
    elif problem_type == 'ball_until_red_calculate_probability':
        return _generate_ball_until_red_calculate_probability_problem()

def _generate_coin_possible_values_problem():
    """
    丟擲硬幣 N 次，X 表示正面次數，寫出所有可能取值。
    """
    num_flips = random.randint(3, 5) # 3 to 5 coin flips
    
    question_text = f"丟擲一枚均勻硬幣 ${num_flips}$ 次，並令隨機變數 $X$ 表示正面出現的次數。寫出 $X$ 所有可能的取值。"
    possible_values = sorted(list(range(num_flips + 1)))
    correct_answer = ", ".join(map(str, possible_values))
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def _generate_coin_describe_event_problem():
    """
    丟擲硬幣 N 次，X 表示正面次數，描述 X=k 的事件。
    """
    num_flips = random.randint(3, 5)
    target_value = random.randint(0, num_flips)
    
    question_text = f"丟擲一枚均勻硬幣 ${num_flips}$ 次，並令隨機變數 $X$ 表示正面出現的次數。描述 $X={target_value}$ 所表示的事件。"
    correct_answer = f"正面出現 ${target_value}$ 次的事件"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def _generate_coin_calculate_probability_problem():
    """
    丟擲硬幣 N 次，X 表示正面次數，求 P(X=k)。
    """
    num_flips = random.randint(3, 5)
    target_value = random.randint(0, num_flips)
    
    total_outcomes = 2**num_flips
    favorable_outcomes = math.comb(num_flips, target_value)
    
    probability = Fraction(favorable_outcomes, total_outcomes)
    
    question_text = f"丟擲一枚均勻硬幣 ${num_flips}$ 次，並令隨機變數 $X$ 表示正面出現的次數。求機率 $P(X={target_value})$ 的值。"
    correct_answer = str(probability) # Fraction automatically handles simplification
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def _generate_ball_draw_possible_values_problem():
    """
    從袋中取球 (不放回)，X 表示某顏色球的顆數，寫出所有可能取值。
    """
    num_red = random.randint(2, 4)
    num_white = random.randint(3, 5)
    
    num_total = num_red + num_white
    num_draw = random.randint(2, min(num_total, 5)) 
    
    # 確保抽球數允許至少兩種隨機變數值，避免題目過於單一
    if num_draw == 1 and (num_red > 0 and num_white > 0):
        # Allow X=0 or X=1, which is fine
        pass
    elif num_draw == 1: # If only one color, force more draws to make it interesting
        num_draw = 2 
    
    random_variable_desc_choices = [
        f"取得紅球的顆數",
        f"取得白球的顆數"
    ]
    random_variable_desc = random.choice(random_variable_desc_choices)
    
    question_text = (f"袋中裝有大小相同的紅球 ${num_red}$ 顆，白球 ${num_white}$ 顆。從袋中任取 ${num_draw}$ 顆球，"
                     f"並令隨機變數 $X$ 表示{random_variable_desc}。寫出 $X$ 所有可能的取值。")
    
    if "紅球" in random_variable_desc:
        min_x = max(0, num_draw - num_white)
        max_x = min(num_draw, num_red)
    else: # "白球" in random_variable_desc
        min_x = max(0, num_draw - num_red)
        max_x = min(num_draw, num_white)
        
    possible_values = sorted(list(range(min_x, max_x + 1)))
    correct_answer = ", ".join(map(str, possible_values))
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def _generate_ball_draw_describe_event_problem():
    """
    從袋中取球 (不放回)，X 表示某顏色球的顆數，描述 X=k 的事件。
    """
    num_red = random.randint(2, 4)
    num_white = random.randint(3, 5)
    num_total = num_red + num_white
    num_draw = random.randint(2, min(num_total, 5))
    
    random_variable_desc_choices = [
        f"取得紅球的顆數",
        f"取得白球的顆數"
    ]
    random_variable_desc = random.choice(random_variable_desc_choices)
    
    if "紅球" in random_variable_desc:
        min_x = max(0, num_draw - num_white)
        max_x = min(num_draw, num_red)
        target_value = random.randint(min_x, max_x)
        correct_answer = f"取到 ${target_value}$ 顆紅球的事件"
    else:
        min_x = max(0, num_draw - num_red)
        max_x = min(num_draw, num_white)
        target_value = random.randint(min_x, max_x)
        correct_answer = f"取到 ${target_value}$ 顆白球的事件"
        
    question_text = (f"袋中裝有大小相同的紅球 ${num_red}$ 顆，白球 ${num_white}$ 顆。從袋中任取 ${num_draw}$ 顆球，"
                     f"並令隨機變數 $X$ 表示{random_variable_desc}。描述 $X={target_value}$ 所表示的事件。")
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def _generate_ball_draw_calculate_probability_problem():
    """
    從袋中取球 (不放回)，X 表示某顏色球的顆數，求 P(X=k)。
    """
    num_red = random.randint(2, 4)
    num_white = random.randint(3, 5)
    num_total = num_red + num_white
    num_draw = random.randint(2, min(num_total, 5))
    
    random_variable_desc_choices = [
        f"取得紅球的顆數",
        f"取得白球的顆數"
    ]
    random_variable_desc = random.choice(random_variable_desc_choices)
    
    if "紅球" in random_variable_desc:
        min_x = max(0, num_draw - num_white)
        max_x = min(num_draw, num_red)
        target_value = random.randint(min_x, max_x)
        
        # 計算機率 (超幾何分佈)
        ways_red = math.comb(num_red, target_value)
        ways_white = math.comb(num_white, num_draw - target_value)
        
        favorable_outcomes = ways_red * ways_white
        total_outcomes = math.comb(num_total, num_draw)
        
    else: # 白球
        min_x = max(0, num_draw - num_red)
        max_x = min(num_draw, num_white)
        target_value = random.randint(min_x, max_x)
        
        ways_white = math.comb(num_white, target_value)
        ways_red = math.comb(num_red, num_draw - target_value)
        
        favorable_outcomes = ways_white * ways_red
        total_outcomes = math.comb(num_total, num_draw)
        
    probability = Fraction(favorable_outcomes, total_outcomes)
    
    question_text = (f"袋中裝有大小相同的紅球 ${num_red}$ 顆，白球 ${num_white}$ 顆。從袋中任取 ${num_draw}$ 顆球，"
                     f"並令隨機變數 $X$ 表示{random_variable_desc}。求機率 $P(X={target_value})$ 的值。")
    correct_answer = str(probability)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def _calculate_prob_until_red(num_red, num_white, x_value):
    """
    計算「取球直到紅球」情境下 P(X=x_value) 的機率。
    X=x_value 表示總共取出 x_value 顆球。
    這意味著前 x_value-1 顆是白球，第 x_value 顆是紅球。
    """
    num_total = num_red + num_white
    
    if x_value == 1:
        return Fraction(num_red, num_total)
    
    if x_value > num_white + 1: # 取出球數不能超過所有白球數 + 1顆紅球
        return Fraction(0)
    
    numerator_prod = 1
    denominator_prod = 1
    
    current_red = num_red
    current_white = num_white
    current_total = num_total
    
    # 依序取出 x_value - 1 顆白球
    for _ in range(x_value - 1):
        if current_white == 0: # 白球不足
            return Fraction(0)
        numerator_prod *= current_white
        denominator_prod *= current_total
        current_white -= 1
        current_total -= 1
        
    # 接著取出第 x_value 顆紅球
    if current_red == 0: # 紅球不足
        return Fraction(0)
    numerator_prod *= current_red
    denominator_prod *= current_total
    
    return Fraction(numerator_prod, denominator_prod)


def _generate_ball_until_red_distribution_table_problem():
    """
    從袋中取球 (不放回，直到紅球)，X 表示總球數，要求寫出機率分布表。
    """
    num_red = random.randint(2, 3) # 保持數字小，方便計算和顯示
    num_white = random.randint(2, 3)
    
    # X 的可能取值範圍為 1 到 num_white + 1
    possible_x_values = list(range(1, num_white + 2))
    
    probabilities = {}
    for x in possible_x_values:
        probabilities[x] = _calculate_prob_until_red(num_red, num_white, x)
    
    question_text = (f"袋中有大小相同的白球 ${num_white}$ 顆、紅球 ${num_red}$ 顆，"
                     f"每次從袋中任取一球，取後不放回，直到取到紅球才停止。"
                     f"令隨機變數 $X$ 表示一輪操作中所取出的總球數。寫出隨機變數 $X$ 的機率分布表。")
    
    # 格式化為 Markdown 表格字串
    x_header = r"| 取出的球數 $x$ | " + r" | ".join(map(str, possible_x_values)) + r" |"
    separator = r"|" + r"---|"* (len(possible_x_values) + 1)
    p_row = r"| $P(X=x)$ | " + r" | ".join(str(probabilities[x]) for x in possible_x_values) + r" |"
    
    correct_answer = f"{x_header}\n{separator}\n{p_row}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def _generate_ball_until_red_calculate_probability_problem():
    """
    從袋中取球 (不放回，直到紅球)，X 表示總球數，要求計算 P(X<k), P(X>k) 等機率。
    """
    num_red = random.randint(2, 3)
    num_white = random.randint(2, 3)
    
    possible_x_values = list(range(1, num_white + 2))
    probabilities = {}
    for x in possible_x_values:
        probabilities[x] = _calculate_prob_until_red(num_red, num_white, x)

    query_type = random.choice(['<', '>', '<=', '>='])
    
    # 選擇一個目標 k 值，確保其在合理範圍內
    if len(possible_x_values) == 1:
        target_k = possible_x_values[0]
    else:
        # 讓 k 有可能落在取值範圍內、邊界或範圍外一格
        min_val = min(possible_x_values)
        max_val = max(possible_x_values)
        target_k = random.randint(min_val, max_val + 1) 
    
    calculated_prob_sum = Fraction(0)
    for x_val in possible_x_values:
        if query_type == '<' and x_val < target_k:
            calculated_prob_sum += probabilities[x_val]
        elif query_type == '>' and x_val > target_k:
            calculated_prob_sum += probabilities[x_val]
        elif query_type == '<=' and x_val <= target_k:
            calculated_prob_sum += probabilities[x_val]
        elif query_type == '>=' and x_val >= target_k:
            calculated_prob_sum += probabilities[x_val]
            
    question_text = (f"袋中有大小相同的白球 ${num_white}$ 顆、紅球 ${num_red}$ 顆，"
                     f"每次從袋中任取一球，取後不放回，直到取到紅球才停止。"
                     f"令隨機變數 $X$ 表示一輪操作中所取出的總球數。求機率 $P(X{query_type}{target_k})$ 的值。")
    correct_answer = str(calculated_prob_sum)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查使用者答案是否正確。
    支援分數、逗號分隔數字列表和字串的比較。
    """
    user_answer_stripped = user_answer.strip()
    correct_answer_stripped = correct_answer.strip()
    
    is_correct = False
    
    # 1. 嘗試將答案解析為分數
    try:
        user_fraction = Fraction(user_answer_stripped)
        correct_fraction = Fraction(correct_answer_stripped)
        if user_fraction == correct_fraction:
            is_correct = True
    except ValueError:
        pass # 不是分數格式，繼續嘗試其他比較方式

    if not is_correct:
        # 2. 嘗試將答案解析為逗號分隔的數字列表 (用於可能取值)
        try:
            user_parts = [p.strip() for p in user_answer_stripped.replace(' ', '').split(',') if p.strip()]
            correct_parts = [p.strip() for p in correct_answer_stripped.replace(' ', '').split(',') if p.strip()]
            
            # 確保內容相同且順序不計 (但長度必須相同)
            if sorted(user_parts) == sorted(correct_parts) and len(user_parts) == len(correct_parts):
                is_correct = True
        except Exception:
            pass # 不是數字列表格式，繼續嘗試字串比較

    if not is_correct:
        # 3. 直接進行字串比較 (用於事件描述、表格等)
        # 允許大小寫不敏感的比較，但對於表格等嚴格格式，仍需要精確匹配
        if user_answer_stripped == correct_answer_stripped:
            is_correct = True
        elif user_answer_stripped.lower() == correct_answer_stripped.lower():
            is_correct = True

    result_text = f"完全正確！答案是 ${correct_answer_stripped}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer_stripped}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}