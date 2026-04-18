import random
from fractions import Fraction
import re

def generate(level=1):
    """
    生成「以文字符號列式」相關題目 (標準 LaTeX 範本)。
    包含：
    1. 簡單情境列式 (加減乘除)
    2. 代數式簡記
    3. 複合應用問題列式
    """
    # 增加應用問題的比重
    problem_type = random.choice([
        'simple_word_problem', 'simple_word_problem',
        'simplification',
        'complex_word_problem', 'complex_word_problem', 'complex_word_problem'
    ])
    
    if problem_type == 'simple_word_problem':
        return generate_simple_word_problem()
    elif problem_type == 'simplification':
        return generate_simplification_problem()
    else: # complex_word_problem
        return generate_complex_word_problem()

def generate_simple_word_problem():
    """生成簡單的文字轉代數式問題。"""
    sub_type = random.choice(['add_sub', 'mul_div'])
    var = random.choice(['a', 'b', 'x', 'y'])
    val = random.randint(5, 25)

    if sub_type == 'add_sub':
        item1 = random.choice(['汽水', '奶茶', '鉛筆', '書'])
        item2 = random.choice(['果汁', '紅茶', '原子筆', '筆記本'])
        is_direct = random.choice([True, False])
        is_more = random.choice([True, False])
        
        if is_direct:
            relation = "貴" if is_more else "便宜"
            question_text = f"一瓶{item1}為 ${var}$ 元，{item2}比{item1}{relation} ${val}$ 元，則一瓶{item2}為 ______ 元。"
            correct_answer = f"{var}+{val}" if is_more else f"{var}-{val}"
        else: # Indirect
            relation = "貴" if is_more else "便宜"
            question_text = f"一杯{item1}為 ${var}$ 元，{item1}比{item2}{relation} ${val}$ 元，則一杯{item2}為 ______ 元。"
            correct_answer = f"{var}-{val}" if is_more else f"{var}+{val}"

    else: # mul_div
        op_type = random.choice(['mul', 'div'])
        if op_type == 'mul':
            action = random.choice(['背英文單字', '看書', '存錢'])
            unit = random.choice(['個', '頁', '元'])
            question_text = f"每天{action} ${val}$ {unit}，連續{action} ${var}$ 天，總共{action}了 ______ {unit}。"
            correct_answer = f"{val} \\times {var}"
        else: # div
            item = random.choice(['簽字筆', '棒棒糖', '蘋果'])
            unit = random.choice(['枝', '根', '顆'])
            question_text = f"{item}每{unit} ${val}$ 元，花 ${var}$ 元買{item}，總共買了 ______ {unit}。"
            correct_answer = f"{var} \\div {val}"
            
    return {
        "question_text": "在下列空格中，填入合於題意的代數式。<br>" + question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_simplification_problem():
    """生成代數式簡記問題。"""
    sub_type = random.choice(['simple_mul', 'complex_op'])
    var = random.choice(['a', 'b', 'x', 'y'])
    
    if sub_type == 'simple_mul':
        coeff_type = random.choice(['int', 'neg_int', 'decimal', 'fraction', 'neg_one'])
        
        if coeff_type == 'int':
            c = random.randint(2, 25)
            expr = f"{c} \\times {var}"
            answer = f"{c}{var}"
        elif coeff_type == 'neg_int':
            c = random.randint(-25, -2)
            expr = f"({c}) \\times {var}"
            answer = f"{c}{var}"
        elif coeff_type == 'decimal':
            c = round(random.uniform(1.1, 9.9), 1)
            expr = f"{c} \\times {var}"
            answer = f"{c}{var}"
        elif coeff_type == 'fraction':
            den = random.randint(3, 11)
            num = random.randint(1, den - 1)
            if random.random() < 0.5:
                expr = f"{var} \\times \\frac{{{num}}}{{{den}}}"
            else:
                expr = f"\\frac{{{num}}}{{{den}}} \\times {var}"
            answer = f"\\frac{{{num}}}{{{den}}} {var}"
        else: # neg_one
            expr = f"(-1) \\times {var}"
            answer = f"-{var}"
        question_text = f"簡記下列各代數式。<br>${expr}$"
        correct_answer = answer
    else: # complex_op
        c_num = random.randint(-9, 9)
        while c_num == 0: c_num = random.randint(-9, 9)
        d = random.randint(1, 20)
        op = random.choice(['+', '-'])
        
        if random.random() < 0.5:
            expr = f"{var} \\times ({c_num}) {op} {d}"
            answer = f"{c_num}{var}{op}{d}"
        else:
            den = random.randint(2, 7)
            num = random.randint(1, den - 1)
            sign = random.choice([-1, 1])
            frac = Fraction(num, den) * sign
            
            frac_latex = f"\\frac{{{abs(frac.numerator)}}}{{{abs(frac.denominator)}}}"
            if frac.numerator < 0:
                frac_latex = f"(-\\frac{{{abs(frac.numerator)}}}{{{abs(frac.denominator)}}})"
            
            recip_frac = 1 / frac
            if recip_frac.denominator == 1:
                recip_latex = f"{recip_frac.numerator}"
            else:
                recip_latex = f"\\frac{{{recip_frac.numerator}}}{{{recip_frac.denominator}}}"
                if recip_frac < 0:
                   recip_latex = f"-\\frac{{{abs(recip_frac.numerator)}}}{{{abs(recip_frac.denominator)}}}"
            
            expr = f"{var} \\div {frac_latex} {op} {d}"
            answer = f"{recip_latex} {var} {op} {d}"
        question_text = f"簡記下列各代數式。<br>${expr}$"
        correct_answer = answer

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_complex_word_problem():
    """生成複合應用問題列式。"""
    sub_type = random.choice(['linear_combo', 'parentheses', 'geometry', 'distribution', 'discount'])
    var = random.choice(['x', 'y'])
    
    if sub_type == 'linear_combo':
        n = random.randint(2, 5)
        m = random.randint(1, 15)
        relation = random.choice(['多', '少'])
        op = '+' if relation == '多' else '-'
        person1, person2 = random.sample(['爸爸', '哥哥', '老師', '小翊', '弟弟', '學生'], 2)
        unit = random.choice(['公斤', '元', '歲'])
        question_text = f"已知{person2}的體重是 ${var}$ {unit}，若{person1}的體重是{person2}體重的 ${n}$ 倍{relation} ${m}$ {unit}，則{person1}的體重是多少{unit}？"
        correct_answer = f"{n}{var}{op}{m}"
    elif sub_type == 'parentheses':
        n = random.randint(2, 5)
        k = random.randint(5, 30)
        item1, item2 = random.sample(['鉛筆', '原子筆', '橡皮擦', '尺'], 2)
        question_text = f"已知一枝{item1}賣 ${var}$ 元，若一枝{item2}比一枝{item1}貴 ${k}$ 元，則買 ${n}$ 枝{item2}要多少元？"
        correct_answer = f"{n}({var}+{k})"
    elif sub_type == 'geometry':
        sides_map = {'正方形': 4, '正三角形': 3, '正五邊形': 5}
        shape = random.choice(list(sides_map.keys()))
        sides = sides_map[shape]
        question_text = f"已知一{shape}周長為 ${var}$，則此{shape}邊長為何？"
        correct_answer = f"\\frac{{{var}}}{{{sides}}}"
    elif sub_type == 'distribution':
        m = random.randint(3, 8)
        n = random.randint(5, 20)
        relation = random.choice(['增加', '拿走'])
        op = '+' if relation == '增加' else '-'
        item = random.choice(['套圈', '糖果', '彈珠'])
        question_text = f"小翊和朋友一共 ${m}$ 人，遊戲每次有 ${var}$ 個{item}，若再{relation} ${n}$ 個{item}，就能完全平分給所有人，這樣每人可分得多少個{item}？"
        correct_answer = f"\\frac{{({var}{op}{n})}}{{{m}}}"
    else: # sub_type == 'discount'
        discount_val = random.randint(6, 9)
        discount_text = {6: "六", 7: "七", 8: "八", 9: "九"}[discount_val]
        question_text = f"小明以 {discount_text} 折優待的價錢買了一些文具，共花了 ${var}$ 元。若沒有此優待，則小明原本應付多少元？"
        correct_answer = f"\\frac{{10{var}}}{{{discount_val}}}"

    return {
        "question_text": "根據下列各題的題意列出代數式。<br>" + question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。對代數式進行基本正規化處理。
    """
    def normalize(s):
        s = s.strip().lower().replace(' ', '')
        s = s.replace('（', '(').replace('）', ')')
        s = s.replace('＋', '+').replace('－', '-')
        s = s.replace('×', '*').replace('÷', '/')
        s = s.replace('\\times', '*').replace('\\div', '/')
        
        # Replace LaTeX frac with standard division notation
        while '\\frac' in s:
            match = re.search(r'\\frac{{(.+?)}}{{(.+?)}}', s)
            if match:
                num_content = match.group(1)
                den_content = match.group(2)
                s = s.replace(match.group(0), f"({num_content})/({den_content})", 1)
            else:
                break
        return s

    user_norm = normalize(user_answer)
    correct_norm = normalize(correct_answer)
    
    user_variations = {user_norm, user_norm.replace('*', '')}
    correct_variations = {correct_norm, correct_norm.replace('*', '')}
    
    is_correct = bool(user_variations.intersection(correct_variations))
    
    if not is_correct:
        match = re.fullmatch(r'([^()]+)\+([^()]+)', correct_norm)
        if match:
            p1, p2 = match.groups()
            rev_correct = f"{p2}+{p1}"
            rev_variations = {rev_correct, rev_correct.replace('*', '')}
            if user_variations.intersection(rev_variations):
                is_correct = True
                
    if not is_correct:
        match = re.fullmatch(r'([a-z0-9])\*\((.+)\)', correct_norm)
        if match:
             p1, p2 = match.groups()
             rev_correct = f"({p2})*{p1}"
             rev_variations = {rev_correct, rev_correct.replace('*', '')}
             if user_variations.intersection(rev_variations):
                is_correct = True

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}
