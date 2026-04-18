import random
from fractions import Fraction
import math

def generate(level=1):
    """
    生成「古典機率定義」相關題目。
    包含：
    1. 擲單一骰子
    2. 擲兩枚硬幣
    3. 擲三枚硬幣
    4. 擲兩粒骰子的點數和
    5. 從袋中同時取球
    6. 從袋中取球不放回
    """
    problem_types = [
        'die_single',
        'coin_two',
        'coin_three',
        'dice_two_sum',
        'balls_simultaneous',
        'balls_no_replacement',
    ]
    problem_type = random.choice(problem_types)

    if problem_type == 'die_single':
        return generate_die_single_problem()
    elif problem_type == 'coin_two':
        return generate_coin_two_problem()
    elif problem_type == 'coin_three':
        return generate_coin_three_problem()
    elif problem_type == 'dice_two_sum':
        return generate_dice_two_sum_problem()
    elif problem_type == 'balls_simultaneous':
        return generate_balls_simultaneous_problem()
    elif problem_type == 'balls_no_replacement':
        return generate_balls_no_replacement_problem()

def generate_die_single_problem():
    """
    生成擲單一公正骰子的機率問題。
    樣本空間 S={1, 2, 3, 4, 5, 6}, n(S)=6。
    """
    n_S = 6
    events = [
        ("擲出 $1$ 點", 1),
        ("擲出 $6$ 點", 1),
        ("擲出偶數點", 3), # {2,4,6}
        ("擲出奇數點", 3), # {1,3,5}
        ("擲出質數", 3), # {2,3,5}
        ("擲出的點數大於 $4$", 2), # {5,6}
        ("擲出的點數小於 $3$", 2), # {1,2}
    ]
    
    event_desc, n_A = random.choice(events)
    
    question_text = f"擲一粒公正的骰子，觀察所出現的點數，求{event_desc}的機率。"
    probability = Fraction(n_A, n_S)
    
    return {
        "question_text": question_text,
        "answer": str(probability),
        "correct_answer": str(probability)
    }

def generate_coin_two_problem():
    """
    生成丟兩枚均勻硬幣的機率問題。
    樣本空間 S={(正,正),(正,反),(反,正),(反,反)}, n(S)=4。
    """
    n_S = 4
    events = [
        ("出現兩次正面", 1), # (H,H)
        ("出現一正面一反面", 2), # (H,T), (T,H)
        ("至少出現一次正面", 3), # (H,H), (H,T), (T,H)
        ("至少出現一次反面", 3), # (H,T), (T,H), (T,T)
        ("沒有出現正面", 1) # (T,T)
    ]
    
    event_desc, n_A = random.choice(events)
    
    question_text = f"丟兩枚均勻硬幣，觀察出現正面或反面的情形，求{event_desc}的機率。"
    probability = Fraction(n_A, n_S)
    
    return {
        "question_text": question_text,
        "answer": str(probability),
        "correct_answer": str(probability)
    }

def generate_coin_three_problem():
    """
    生成丟三枚均勻硬幣的機率問題。
    樣本空間 n(S)=2^3=8。
    """
    n_S = 8
    
    num_heads = random.randint(0, 3) # 恰出現 0, 1, 2, 3 次正面
    n_A = math.comb(3, num_heads) # C(3, num_heads)
    
    event_desc = f"恰出現 ${num_heads}$ 次正面"
    if num_heads == 0:
        event_desc = "沒有出現正面"
    elif num_heads == 3:
        event_desc = "全部為正面"

    question_text = f"丟三枚均勻硬幣，求{event_desc}的機率。"
    probability = Fraction(n_A, n_S)
    
    return {
        "question_text": question_text,
        "answer": str(probability),
        "correct_answer": str(probability)
    }

def generate_dice_two_sum_problem():
    """
    生成同時擲兩粒公正骰子，點數和的機率問題。
    樣本空間 n(S)=6*6=36。
    """
    n_S = 36
    
    # Mapping sum to number of outcomes
    sum_outcomes = {
        2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 7: 6,
        8: 5, 9: 4, 10: 3, 11: 2, 12: 1
    }
    
    target_sum = random.randint(2, 12)
    n_A = sum_outcomes[target_sum]
    
    question_text = f"同時擲兩粒公正骰子，觀察所出現的點數和，求點數和為 ${target_sum}$ 的機率。"
    probability = Fraction(n_A, n_S)
    
    return {
        "question_text": question_text,
        "answer": str(probability),
        "correct_answer": str(probability)
    }

def generate_balls_simultaneous_problem():
    """
    生成從袋中同時取出兩球的機率問題。
    n(S) 使用組合 C(N, k)。
    """
    num_red = random.randint(2, 5) # 紅球數量，至少2顆方便取兩紅球
    num_blue = random.randint(1, 4) # 藍球數量
    total_balls = num_red + num_blue
    
    k_draw = 2 # 同時取出2球
    n_S = math.comb(total_balls, k_draw)

    possible_events = []
    if num_red >= 2:
        possible_events.append(("兩球都是紅球", math.comb(num_red, 2)))
    if num_blue >= 2:
        possible_events.append(("兩球都是藍球", math.comb(num_blue, 2)))
    if num_red >= 1 and num_blue >= 1:
        possible_events.append(("一紅球一藍球", math.comb(num_red, 1) * math.comb(num_blue, 1)))
    
    # This ensures a valid event is always chosen given the ranges for num_red and num_blue.
    if not possible_events: 
        return generate_balls_simultaneous_problem()

    event_desc, n_A = random.choice(possible_events)
    
    question_text = (
        f"袋中有 ${num_red}$ 顆紅球，${num_blue}$ 顆藍球。設每球被取出的機會均等，"
        f"同時取出 ${k_draw}$ 球，求{event_desc}的機率。"
    )
    probability = Fraction(n_A, n_S)
    
    return {
        "question_text": question_text,
        "answer": str(probability),
        "correct_answer": str(probability)
    }

def generate_balls_no_replacement_problem():
    """
    生成從袋中取一球不放回，再取一球的機率問題。
    n(S) 使用排列 P(N, k)。
    """
    num_red = random.randint(2, 5) # 紅球數量，至少2顆方便取兩紅球
    num_blue = random.randint(1, 4) # 藍球數量
    total_balls = num_red + num_blue
    
    k_draw = 2 # 取2球不放回
    n_S = math.perm(total_balls, k_draw) # 樣本點考慮順序，如 (R1, R2) 與 (R2, R1) 為不同

    possible_events = []
    if num_red >= 2:
        possible_events.append(("兩球都是紅球", math.perm(num_red, 2))) # R*(R-1)
    if num_blue >= 2:
        possible_events.append(("兩球都是藍球", math.perm(num_blue, 2))) # B*(B-1)
    if num_red >= 1 and num_blue >= 1:
        # 一紅球一藍球 (指一紅一藍，不論順序)
        possible_events.append(("一紅球一藍球", num_red * num_blue + num_blue * num_red)) # (R,B) 或 (B,R)
    
    if not possible_events:
        return generate_balls_no_replacement_problem()

    event_desc, n_A = random.choice(possible_events)
    
    question_text = (
        f"袋中有 ${num_red}$ 顆紅球，${num_blue}$ 顆藍球。設每球被取出的機會均等，"
        f"取一球後不放回，再取一球，求{event_desc}的機率。"
    )
    probability = Fraction(n_A, n_S)
    
    return {
        "question_text": question_text,
        "answer": str(probability),
        "correct_answer": str(probability)
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    try:
        user_fraction = Fraction(user_answer.strip())
        correct_fraction = Fraction(correct_answer.strip())
        is_correct = (user_fraction == correct_fraction)
    except ValueError:
        is_correct = False # User input was not a valid fraction or number

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}