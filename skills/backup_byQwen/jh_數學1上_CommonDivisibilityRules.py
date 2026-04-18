# ==============================================================================
# ID: jh_數學1上_CommonDivisibilityRules
# Model: qwen3-coder:30b | Strategy: General Math Pedagogy v7.6 (Expert 14B+)
# Duration: 220.74s | RAG: 8 examples
# Created At: 2025-12-31 23:37:33
# Fix Status: [Repaired]
# ==============================================================================

import random
from fractions import Fraction

def to_latex(num):
    if isinstance(num, int): return str(num)
    if isinstance(num, float): num = Fraction(str(num)).limit_denominator(100)
    if isinstance(num, Fraction):
        if num.denominator == 1: return str(num.numerator)
        if abs(num.numerator) > num.denominator:
            sign = "-" if num.numerator < 0 else ""
            rem = abs(num) - (abs(num).numerator // abs(num).denominator)
            return f"{sign}{abs(num).numerator // abs(num).denominator} \\frac{{{{rem.numerator}}}{{{rem.denominator}}}"
        return f"\\frac{{{{num.numerator}}}{{{num.denominator}}}"
    return str(num)

def fmt_num(num):
    """Formats negative numbers with parentheses for equations."""
    if num < 0: return f"({num})"
    return str(num)

def draw_number_line(points_map):
    """Generates aligned ASCII number line with HTML CSS (Scrollable)."""
    values = [int(v) if isinstance(v, (int, float)) else int(v.numerator/v.denominator) for v in points_map.values()]
    if not values: values = [0]
    r_min, r_max = min(min(values)-1, -5), max(max(values)+1, 5)
    if r_max - r_min > 12: c=sum(values)//len(values); r_min, r_max = c-6, c+6
    
    u_w = 5
    l_n, l_a, l_l = "", "", ""
    for i in range(r_min, r_max+1):
        l_n += f"{str(i):^{u_w}}"
        l_a += ("+" + " "*(u_w-1)) if i == r_max else ("+" + "-"*(u_w-1))
        lbls = [k for k,v in points_map.items() if (v==i if isinstance(v, int) else int(v)==i)]
        l_l += f"{lbls[0]:^{u_w}}" if lbls else " "*u_w
    
    content = f"{l_n}\n{l_a}\n{l_l}"
    return (f"<div style='width: 100%; overflow-x: auto; background: #f8f9fa; padding: 10px; border-radius: 5px; margin: 10px 0;'>"
            f"<pre style='font-family: Consolas, monospace; line-height: 1.1; display: inline-block; margin: 0;'>{content}</pre></div>")

def generate_calc_problem():
    # 生成一個判斷倍數的問題
    # 隨機選擇倍數判別法（2, 3, 4, 5, 9）
    divisor = random.choice([2, 3, 4, 5, 9])
    
    # 生成一個數字（根據倍數判別法的長度）
    if divisor == 2:
        # 生成一個偶數或奇數，並讓學生判斷是否為2的倍數
        num = random.randint(100, 999)
        is_multiple = num % 2 == 0
        return {
            'question_text': f'判斷 $ {num} $ 是否為 2 的倍數？',
            'answer': '是' if is_multiple else '不是',
            'correct_answer': '是' if is_multiple else '不是'
        }
    
    elif divisor == 3:
        # 生成一個數字，讓學生判斷是否為3的倍數
        num = random.randint(100, 999)
        digit_sum = sum(int(digit) for digit in str(num))
        is_multiple = digit_sum % 3 == 0
        return {
            'question_text': f'判斷 $ {num} $ 是否為 3 的倍數？',
            'answer': '是' if is_multiple else '不是',
            'correct_answer': '是' if is_multiple else '不是'
        }
    
    elif divisor == 4:
        # 生成一個四位數，讓學生判斷是否為4的倍數
        num = random.randint(1000, 9999)
        last_two_digits = num % 100
        is_multiple = last_two_digits % 4 == 0
        return {
            'question_text': f'判斷 $ {num} $ 是否為 4 的倍數？',
            'answer': '是' if is_multiple else '不是',
            'correct_answer': '是' if is_multiple else '不是'
        }
    
    elif divisor == 5:
        # 生成一個數字，讓學生判斷是否為5的倍數
        num = random.randint(100, 999)
        is_multiple = num % 5 == 0
        return {
            'question_text': f'判斷 $ {num} $ 是否為 5 的倍數？',
            'answer': '是' if is_multiple else '不是',
            'correct_answer': '是' if is_multiple else '不是'
        }
    
    elif divisor == 9:
        # 生成一個數字，讓學生判斷是否為9的倍數
        num = random.randint(100, 999)
        digit_sum = sum(int(digit) for digit in str(num))
        is_multiple = digit_sum % 9 == 0
        return {
            'question_text': f'判斷 $ {num} $ 是否為 9 的倍數？',
            'answer': '是' if is_multiple else '不是',
            'correct_answer': '是' if is_multiple else '不是'
        }

def generate_app_problem():
    # 生成一個應用題，例如填入數字使數字成為某個數的倍數
    divisor = random.choice([2, 3, 4, 5, 9])
    
    if divisor == 2:
        # 生成一個五位數，最後一位未知，讓學生找出可能的數字
        num = random.randint(10000, 99999)
        num_str = str(num)
        # 將最後一位設為未知數
        question_text = f'已知五位數 $ {num_str[:-1]}\\square $ 是 2 的倍數，則 $ \\square $ 中可填入的數為何？'
        possible_digits = [i for i in range(10) if (int(num_str[:-1] + str(i)) % 2 == 0)]
        answer = ', '.join(map(str, possible_digits))
        return {
            'question_text': question_text,
            'answer': answer,
            'correct_answer': answer
        }
    
    elif divisor == 3:
        # 生成一個六位數，最後一位未知，讓學生找出可能的數字
        num = random.randint(100000, 999999)
        num_str = str(num)
        # 將最後一位設為未知數
        question_text = f'已知六位數 $ {num_str[:-1]}\\square $ 是 3 的倍數，則 $ \\square $ 中可填入的數為何？'
        digit_sum = sum(int(digit) for digit in num_str[:-1])
        possible_digits = [i for i in range(10) if ((digit_sum + i) % 3 == 0)]
        answer = ', '.join(map(str, possible_digits))
        return {
            'question_text': question_text,
            'answer': answer,
            'correct_answer': answer
        }
    
    elif divisor == 4:
        # 生成一個六位數，最後兩位未知，讓學生找出可能的數字
        num = random.randint(100000, 999999)
        num_str = str(num)
        # 將最後兩位設為未知數
        question_text = f'已知六位數 $ {num_str[:-2]}\\square\\square $ 是 4 的倍數，則 $ \\square\\square $ 中可填入的數為何？'
        # 只考慮最後兩位數字
        last_two = int(num_str[-2:])
        possible_digits = [i for i in range(100) if (last_two * 100 + i) % 4 == 0]
        answer = ', '.join(map(str, possible_digits))
        return {
            'question_text': question_text,
            'answer': answer,
            'correct_answer': answer
        }
    
    elif divisor == 5:
        # 生成一個五位數，最後一位未知，讓學生找出可能的數字
        num = random.randint(10000, 99999)
        num_str = str(num)
        # 將最後一位設為未知數
        question_text = f'已知五位數 $ {num_str[:-1]}\\square $ 是 5 的倍數，則 $ \\square $ 中可填入的數為何？'
        possible_digits = [i for i in range(10) if (int(num_str[:-1] + str(i)) % 5 == 0)]
        answer = ', '.join(map(str, possible_digits))
        return {
            'question_text': question_text,
            'answer': answer,
            'correct_answer': answer
        }
    
    elif divisor == 9:
        # 生成一個六位數，最後一位未知，讓學生找出可能的數字
        num = random.randint(100000, 999999)
        num_str = str(num)
        # 將最後一位設為未知數
        question_text = f'已知六位數 $ {num_str[:-1]}\\square $ 是 9 的倍數，則 $ \\square $ 中可填入的數為何？'
        digit_sum = sum(int(digit) for digit in num_str[:-1])
        possible_digits = [i for i in range(10) if ((digit_sum + i) % 9 == 0)]
        answer = ', '.join(map(str, possible_digits))
        return {
            'question_text': question_text,
            'answer': answer,
            'correct_answer': answer
        }

def generate(level=1):
    type = random.choice(['calc', 'app'])
    if type == 'calc': 
        return generate_calc_problem()
    else: 
        return generate_app_problem()

# 測試
if __name__ == "__main__":