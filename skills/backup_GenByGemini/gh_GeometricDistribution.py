import random
from fractions import Fraction
import re

def generate(level=1):
    """
    生成幾何分布相關題目。
    包含：
    1. 直接給定成功機率 p，計算 P(X=k)。
    2. 從情境題（骰子、硬幣、猜拳）中推導 p，再計算 P(X=k)。
    """
    problem_type = random.choice([
        'direct_probability',
        'scenario_probability_dice',
        'scenario_probability_coins',
        'scenario_probability_rock_paper_scissors'
    ])
    
    if problem_type == 'direct_probability':
        return generate_direct_probability_problem(level)
    elif problem_type == 'scenario_probability_dice':
        return generate_scenario_probability_dice_problem(level)
    elif problem_type == 'scenario_probability_coins':
        return generate_scenario_probability_coins_problem(level)
    else: # scenario_probability_rock_paper_scissors
        return generate_scenario_probability_rock_paper_scissors_problem(level)

def _format_fraction(frac):
    """
    將分數物件格式化為 LaTeX 字串。
    """
    if frac.denominator == 1:
        return str(frac.numerator)
    return r"\\frac{{{}}}{{{}}}".format(frac.numerator, frac.denominator)

def generate_direct_probability_problem(level):
    """
    生成直接給定成功機率 p，計算 P(X=k) 的題目。
    """
    # 選擇成功機率 p
    denominators = [2, 3, 4, 5, 6, 8, 10]
    denominator = random.choice(denominators)
    numerator = random.randint(1, denominator - 1) # 確保 0 < p < 1
    p_frac = Fraction(numerator, denominator)

    # 選擇試驗次數 k
    k = random.randint(2, 6) if level == 1 else random.randint(3, 8)
    
    # 計算機率 P(X=k) = (1-p)^(k-1) * p
    if k == 1:
        correct_answer_frac = p_frac
        question_text = (
            f"某事件成功的機率為 ${_format_fraction(p_frac)}$。若此事件是重複的獨立伯努力試驗，"
            f"請問在第 $1$ 次試驗就首次成功的機率為何？"
        )
    else:
        one_minus_p_frac = Fraction(1) - p_frac
        correct_answer_frac = (one_minus_p_frac ** (k - 1)) * p_frac
        question_text = (
            f"某事件成功的機率為 ${_format_fraction(p_frac)}$。若此事件是重複的獨立伯努力試驗，"
            f"請問直到第 ${k}$ 次試驗才首次成功的機率為何？"
        )
        
    return {
        "question_text": question_text,
        "answer": _format_fraction(correct_answer_frac),
        "correct_answer": _format_fraction(correct_answer_frac)
    }

def generate_scenario_probability_dice_problem(level):
    """
    生成丟擲骰子情境題，推導 p 後計算 P(X=k)。
    """
    num_dice = random.choice([1, 2])
    target_event_choices = []

    if num_dice == 1:
        target_event_choices.extend([
            {"desc": "出現偶數點", "p": Fraction(3, 6)}, # 2, 4, 6
            {"desc": "出現質數點", "p": Fraction(3, 6)}, # 2, 3, 5
            {"desc": "出現點數大於4", "p": Fraction(2, 6)}, # 5, 6
            {"desc": "出現點數為3的倍數", "p": Fraction(2, 6)}, # 3, 6
            {"desc": "出現點數小於等於2", "p": Fraction(2, 6)} # 1, 2
        ])
    else: # num_dice == 2
        # 總共 6*6 = 36 種結果
        target_event_choices.extend([
            {"desc": "點數和為7", "p": Fraction(6, 36)}, # (1,6),(2,5),(3,4),(4,3),(5,2),(6,1)
            {"desc": "點數和為偶數", "p": Fraction(18, 36)},
            {"desc": "兩枚骰子點數相同", "p": Fraction(6, 36)}, # (1,1)...(6,6)
            {"desc": "兩枚骰子點數和為10以上 (含10)", "p": Fraction(6, 36)}, # (4,6), (5,5), (5,6), (6,4), (6,5), (6,6)
            {"desc": "兩枚骰子點數不同", "p": Fraction(30, 36)}
        ])

    event = random.choice(target_event_choices)
    p_frac = event["p"].limit_denominator() # 簡化分數
    k = random.randint(2, 5) if level == 1 else random.randint(3, 7)

    # 計算機率 P(X=k) = (1-p)^(k-1) * p
    if k == 1:
        correct_answer_frac = p_frac
        question_text = (
            f"同時丟擲 ${num_dice}$ 枚均勻骰子，直到首次出現「{event['desc']}」。"
            f"請問在第 $1$ 次丟擲就出現此情況的機率為何？"
        )
    else:
        one_minus_p_frac = Fraction(1) - p_frac
        correct_answer_frac = (one_minus_p_frac ** (k - 1)) * p_frac
        question_text = (
            f"同時丟擲 ${num_dice}$ 枚均勻骰子，直到首次出現「{event['desc']}」。"
            f"請問直到第 ${k}$ 次丟擲才首次出現此情況的機率為何？"
        )

    return {
        "question_text": question_text,
        "answer": _format_fraction(correct_answer_frac),
        "correct_answer": _format_fraction(correct_answer_frac)
    }

def generate_scenario_probability_coins_problem(level):
    """
    生成丟擲硬幣情境題，推導 p 後計算 P(X=k)。
    """
    num_coins = random.choice([2, 3])
    
    if num_coins == 2:
        total_outcomes = 4 # HH, HT, TH, TT
        target_event_choices = [
            {"desc": "兩枚硬幣皆出現正面", "p": Fraction(1, total_outcomes)}, # HH
            {"desc": "兩枚硬幣皆出現反面", "p": Fraction(1, total_outcomes)}, # TT
            {"desc": "兩枚硬幣皆同一面", "p": Fraction(2, total_outcomes)}, # HH, TT
            {"desc": "一枚正面一枚反面", "p": Fraction(2, total_outcomes)}, # HT, TH
            {"desc": "至少一枚正面", "p": Fraction(3, total_outcomes)} # HH, HT, TH
        ]
    else: # num_coins == 3
        total_outcomes = 8 # HHH, HHT, HTH, THH, HTT, THT, TTH, TTT
        target_event_choices = [
            {"desc": "三枚硬幣皆同一面", "p": Fraction(2, total_outcomes)}, # HHH, TTT
            {"desc": "三枚硬幣皆出現正面", "p": Fraction(1, total_outcomes)}, # HHH
            {"desc": "三枚硬幣皆出現反面", "p": Fraction(1, total_outcomes)}, # TTT
            {"desc": "恰好一枚正面", "p": Fraction(3, total_outcomes)}, # HTT, THT, TTH
            {"desc": "恰好兩枚正面", "p": Fraction(3, total_outcomes)}, # HHT, HTH, THH
            {"desc": "至少一枚正面", "p": Fraction(7, total_outcomes)} # 除了 TTT 之外所有情況
        ]

    event = random.choice(target_event_choices)
    p_frac = event["p"].limit_denominator()
    k = random.randint(2, 5) if level == 1 else random.randint(3, 7)

    # 計算機率 P(X=k) = (1-p)^(k-1) * p
    if k == 1:
        correct_answer_frac = p_frac
        question_text = (
            f"同時丟擲 ${num_coins}$ 枚均勻硬幣，觀察出現正面或反面的情形，直到首次出現「{event['desc']}」。"
            f"請問在第 $1$ 次丟擲就出現此情況的機率為何？"
        )
    else:
        one_minus_p_frac = Fraction(1) - p_frac
        correct_answer_frac = (one_minus_p_frac ** (k - 1)) * p_frac
        question_text = (
            f"同時丟擲 ${num_coins}$ 枚均勻硬幣，觀察出現正面或反面的情形，直到首次出現「{event['desc']}」。"
            f"請問直到第 ${k}$ 次丟擲才首次出現此情況的機率為何？"
        )
    
    return {
        "question_text": question_text,
        "answer": _format_fraction(correct_answer_frac),
        "correct_answer": _format_fraction(correct_answer_frac)
    }

def generate_scenario_probability_rock_paper_scissors_problem(level):
    """
    生成剪刀、石頭、布情境題，推導 p 後計算 P(X=k)。
    參考例題：甲、乙兩人猜拳。
    分出勝負的機率 p = 6/9 = 2/3。
    平手的機率 1-p = 3/9 = 1/3。
    """
    p_success_frac = Fraction(6, 9).limit_denominator() # 分出勝負的機率，應為 2/3
    one_minus_p_success_frac = Fraction(3, 9).limit_denominator() # 平手的機率，應為 1/3
    
    k = random.randint(2, 5) if level == 1 else random.randint(3, 7)
    
    # 計算機率 P(X=k) = (1-p)^(k-1) * p
    if k == 1:
        correct_answer_frac = p_success_frac
        question_text = (
            f"甲、乙兩人進行「剪刀、石頭、布」的猜拳遊戲。已知兩人出拳都是隨機的，"
            f"且每次出拳都為獨立事件。請問在第 $1$ 次猜拳就分出勝負的機率為何？"
        )
    else:
        correct_answer_frac = (one_minus_p_success_frac ** (k - 1)) * p_success_frac
        question_text = (
            f"甲、乙兩人進行「剪刀、石頭、布」的猜拳遊戲。已知兩人出拳都是隨機的，"
            f"且每次出拳都為獨立事件。請問直到第 ${k}$ 次猜拳才分出勝負的機率為何？"
        )
    
    return {
        "question_text": question_text,
        "answer": _format_fraction(correct_answer_frac),
        "correct_answer": _format_fraction(correct_answer_frac)
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    user_answer 為使用者輸入的字串，correct_answer 為系統計算的正確答案（LaTeX 格式字串）。
    """
    user_answer = user_answer.strip()
    is_correct = False
    
    try:
        # 將使用者答案解析為 Fraction 物件
        if '/' in user_answer:
            user_frac = Fraction(user_answer)
        elif '.' in user_answer:
            user_frac = Fraction(float(user_answer)).limit_denominator(1000000) # 限制浮點數精度
        else:
            user_frac = Fraction(int(user_answer))
        
        # 將正確答案（LaTeX 格式字串）解析為 Fraction 物件
        match_latex_frac = re.match(r"\\frac\{(\d+)\}\{(\d+)\}", correct_answer)
        if match_latex_frac:
            num = int(match_latex_frac.group(1))
            den = int(match_latex_frac.group(2))
            correct_frac = Fraction(num, den)
        else: # 如果不是 LaTeX 分數格式，則假定為整數字串 (e.g., "1")
            correct_frac = Fraction(int(correct_answer))

        if user_frac == correct_frac:
            is_correct = True
            
    except (ValueError, ZeroDivisionError, TypeError):
        # 處理使用者輸入無效的情況 (非數字、非分數等)
        is_correct = False

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}