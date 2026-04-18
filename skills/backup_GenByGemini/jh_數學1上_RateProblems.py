import random
from fractions import Fraction
import math

def generate(level=1):
    """
    生成「速率問題」相關題目。
    包含：
    1. 追趕問題 (同向)
    2. 往返問題 (上山下山)
    3. 相遇問題 (相向)
    4. 順流逆流問題
    """
    problem_generators = [
        generate_chase_problem,
        generate_round_trip_problem,
        generate_meeting_problem,
        generate_river_current_problem
    ]
    
    return random.choice(problem_generators)()

def generate_chase_problem():
    """
    題型：追趕問題 (例題1變體)
    兩人同地、同向、同時出發，快者到終點時，慢者還差一段距離。求全長。
    """
    # 設定參數
    v_fast = random.randint(9, 15)  # 快者的速度 (公里/小時)
    v_slow = random.randint(5, v_fast - 2) # 慢者的速度
    time = random.choice([2, 3, 4, 5]) # 花費時間 (小時)，選整數讓題目數字漂亮
    
    # 計算衍生數值
    total_dist = v_fast * time  # 全長
    gap = (v_fast - v_slow) * time # 兩人差距
    
    # 產生題目文字
    names = [('小明', '小華'), ('小翊', '小妍'), ('阿飛', '小珍')]
    name1, name2 = random.choice(names)
    location = random.choice(['操場', '環湖公路', '環島公路'])
    
    question_text = f"{name1}與{name2}約定於某地同時同方向沿著{location}路跑。"\
                    f"已知{name1}每小時跑 {v_fast} 公里，{name2}每小時跑 {v_slow} 公里。"\
                    f"當{name1}跑完一圈回到終點時，{name2}還離終點 {gap} 公里，求{location}全長多少公里？"

    correct_answer = str(total_dist)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "input_type": "text"
    }

def generate_round_trip_problem():
    """
    題型：往返問題 (例題2)
    上山、下山走相同路徑，速度不同，給定總時間，求山路長度。
    """
    # 設定參數
    v_up = random.randint(2, 4) # 上山速度
    v_down = random.randint(v_up + 2, v_up + 5) # 下山速度
    total_time = random.randint(4, 10) # 總時間 (小時)
    
    # 計算答案
    # x/v_up + x/v_down = total_time  => x * (1/v_up + 1/v_down) = total_time
    # x = total_time / (1/v_up + 1/v_down) = total_time * (v_up * v_down) / (v_up + v_down)
    numerator = total_time * v_up * v_down
    denominator = v_up + v_down
    
    answer_frac = Fraction(numerator, denominator)
    correct_answer = str(answer_frac)
    
    # 產生題目文字
    name = random.choice(['宗彥', '志明', '山友'])
    question_text = f"{name}沿著相同的路徑上山、下山共需要 {total_time} 小時。"\
                    f"如果{name}上山每小時可走 {v_up} 公里，下山每小時可走 {v_down} 公里，則這條山路長多少公里？"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "input_type": "handwriting" # 答案可能是分數
    }

def generate_meeting_problem():
    """
    題型：相遇問題
    兩人從兩地相向而行，求相遇地點。
    """
    # 設定參數
    v_a = random.randint(4, 8) # A 的速度
    v_b = random.randint(3, 7) # B 的速度
    time = random.choice([2, 2.5, 3, 3.5, 4]) # 相遇時間 (小時)
    
    # 計算衍生數值
    total_dist = (v_a + v_b) * time
    dist_from_A = v_a * time
    
    # 處理小數點，讓顯示更自然
    total_dist_str = str(int(total_dist)) if total_dist % 1 == 0 else str(total_dist)
    
    # 產生題目文字
    question_text = f"甲、乙兩地相距 {total_dist_str} 公里。"\
                    f"小明從甲地以時速 {v_a} 公里走向乙地，同時小華從乙地以時速 {v_b} 公里走向甲地。"\
                    f"請問兩人相遇的地點距離甲地多少公里？"
                    
    correct_answer = str(int(dist_from_A)) if dist_from_A % 1 == 0 else str(dist_from_A)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "input_type": "text"
    }

def generate_river_current_problem():
    """
    題型：順流逆流問題
    給定船速、水速、距離，求來回總時間。
    """
    # 設定參數
    v_boat = random.randint(10, 20) # 靜水船速
    v_current = random.randint(2, v_boat - 5) # 水流速度
    dist = random.randint(20, 60) # 單程距離
    
    # 計算答案
    # t_total = dist / (v_boat + v_current) + dist / (v_boat - v_current)
    t_total_frac = Fraction(dist, v_boat + v_current) + Fraction(dist, v_boat - v_current)
    correct_answer = str(t_total_frac)

    # 產生題目文字
    question_text = f"一艘船在靜水中的時速為 {v_boat} 公里，水流的時速為 {v_current} 公里。"\
                    f"此船在一條河上，從甲地順流航行至乙地，再從乙地逆流返回甲地。"\
                    f"若甲、乙兩地相距 {dist} 公里，請問來回一趟共需多少小時？"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "input_type": "handwriting" # 答案可能是分數
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。能處理整數、小數、分數。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()

    try:
        # 使用 Fraction 進行比較，可以同時處理整數、小數和分數形式的答案
        # 例如 '7/2', '3.5', '3.50' 都會被視為相等
        user_frac = Fraction(user_answer).limit_denominator()
        correct_frac = Fraction(correct_answer).limit_denominator()
        
        is_correct = (user_frac == correct_frac)
    except (ValueError, ZeroDivisionError):
        # 如果使用者輸入無法轉換為數字，則視為錯誤
        is_correct = False

    if is_correct:
        frac = Fraction(correct_answer)
        if frac.denominator == 1:
            answer_str = str(frac.numerator)
        else:
            answer_str = f"\\frac{{{frac.numerator}}}{{{frac.denominator}}}"
        result_text = f"完全正確！答案是 ${answer_str}$。"
    else:
        try:
            frac = Fraction(correct_answer)
            if frac.denominator == 1:
                answer_str = str(frac.numerator)
            else:
                answer_str = f"\\frac{{{frac.numerator}}}{{{frac.denominator}}}"
        except ValueError:
            answer_str = correct_answer # Fallback for non-fractional strings
        
        result_text = f"答案不正確。正確答案應為：${answer_str}$"

    return {"correct": is_correct, "result": result_text, "next_question": True}
