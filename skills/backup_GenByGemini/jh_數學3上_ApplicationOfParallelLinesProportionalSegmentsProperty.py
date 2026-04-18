import random
from fractions import Fraction
import math

def _format_poly_compact(a, b, var='x'):
    """Formats a linear polynomial ax+b into a compact string like '2x-3'."""
    if a == 0:
        return str(b)
    
    term_x = ""
    if a == 1:
        term_x = var
    elif a == -1:
        term_x = f"-{var}"
    else:
        term_x = f"{a}{var}"
        
    if b == 0:
        return term_x
    elif b > 0:
        return f"{term_x}+{b}"
    else: # b < 0
        return f"{term_x}{b}" # b is already negative, so no operator needed

def _generate_simple_algebra_problem():
    """
    Generates a problem of the form (ax+b):(cx+d) = m:n.
    Example: AB=x+1, BC=3x-1, DE=5, EF=10. Find x.
    """
    x_sol = random.randint(2, 6)
    p, q = random.choice([(1, 2), (2, 3), (1, 3), (3, 4), (3, 5)])
    
    a = random.randint(1, 2)
    c = random.randint(1, 4)
    
    # Ensure the coefficient of x doesn't cancel out
    if q * a - p * c == 0:
        return _generate_simple_algebra_problem()
        
    qa_pc = q * a - p * c
    K = x_sol * qa_pc
    
    # Find suitable b and d for K = p*d - q*b
    b, d = None, None
    for b_trial in random.sample(range(-5, 6), 11):
        # We need p*d = K + q*b_trial, so K + q*b_trial must be divisible by p
        if (K + q * b_trial) % p == 0:
            d_trial = (K + q * b_trial) // p
            # Check if segment lengths are positive at the solution
            if (a * x_sol + b_trial > 0) and (c * x_sol + d_trial > 0):
                b, d = b_trial, d_trial
                break
    
    if b is None: # Fallback if no valid coefficients found
        return _generate_simple_algebra_problem()

    ab_expr = _format_poly_compact(a, b)
    bc_expr = _format_poly_compact(c, d)
    
    k = random.randint(2, 5)
    de = p * k
    ef = q * k
    
    question_text = f"如圖，三條平行線 $L_1, L_2, L_3$ 被兩條截線所截。<br>若 $\\overline{{AB}} = {ab_expr}$、$\\overline{{BC}} = {bc_expr}$、$\\overline{{DE}} = {de}$、$\\overline{{EF}} = {ef}$，則 $x$ 的值為多少？"
    
    return {
        "question_text": question_text,
        "answer": str(x_sol),
        "correct_answer": str(x_sol)
    }

def _generate_quadratic_algebra_problem():
    """
    Generates a problem leading to a quadratic equation, ensuring a unique valid solution.
    Example: AC:CE = BD:DF -> 4:(4x+2) = (3x+3):9
    """
    x_sol = random.randint(1, 4)
    
    b, d, c, e = 0,0,0,0
    # Loop to ensure segments are positive for x_sol and at least one is non-positive for the other root
    for _ in range(20):
        b = random.randint(1, 4)
        c = random.randint(-5, 5)
        d = random.randint(1, 3)
        e = random.randint(-5, 5)

        seg1_val = b * x_sol + c
        seg2_val = d * x_sol + e

        if seg1_val > 0 and seg2_val > 0:
            product = seg1_val * seg2_val
            # The quadratic is bdx^2 + (be+cd)x + (ce-product) = 0
            # Sum of roots = -(be+cd)/(bd)
            sum_roots = Fraction(-(b*e + c*d), b*d)
            other_root = sum_roots - x_sol

            # We need the other root to result in a non-positive length to be an invalid solution
            if other_root <= 0 or b * other_root + c <= 0 or d * other_root + e <= 0:
                break
    else: # If loop finishes without finding a valid case
        return _generate_quadratic_algebra_problem() # Retry

    product = (b * x_sol + c) * (d * x_sol + e)
    
    factors = []
    for i in range(1, int(math.sqrt(product)) + 1):
        if product % i == 0:
            factors.append((i, product // i))
    
    if not factors:
        return _generate_quadratic_algebra_problem()

    a, f = random.choice(factors)
    
    ce_expr = _format_poly_compact(b, c)
    bd_expr = _format_poly_compact(d, e)
    
    question_text = f"如圖，三條平行線 $L_1, L_2, L_3$ 被兩條截線所截。<br>若 $\\overline{{AC}}={a}$、$\\overline{{CE}}={ce_expr}$、$\\overline{{BD}}={bd_expr}$、$\\overline{{DF}}={f}$，則 $x$ 的值為多少？"
    
    return {
        "question_text": question_text,
        "answer": str(x_sol),
        "correct_answer": str(x_sol)
    }

def _generate_trapezoid_problem():
    """
    Generates a problem involving a trapezoid with a parallel segment.
    Can ask for the segment length (EF), the ratio (AE:EB), one of the bases, or a more advanced two-step problem.
    """
    sub_type = random.choice(['find_ef', 'find_ratio', 'find_base', 'advanced_ef'])
    
    m, n = random.sample(range(1, 6), 2)
    
    if sub_type == 'find_ef':
        d = math.gcd(m, n)
        divisor = (m + n) // d
        ad = random.randint(4, 10)
        k = random.randint(1, 4)
        bc = ad + k * divisor
        ef = (bc * m + ad * n) // (m + n)
        question_text = f"如圖，四邊形 $ABCD$ 中，$\\overline{{AD}} // \\overline{{EF}} // \\overline{{BC}}$。$E$、$F$ 分別在 $\\overline{{AB}}$、$\\overline{{CD}}$ 上。<br>若 $\\overline{{AE}}:\\overline{{EB}} = {m}:{n}$，且 $\\overline{{AD}}={ad}$、$\\overline{{BC}}={bc}$，則 $\\overline{{EF}}$ 的長度為何？"
        answer = str(ef)

    elif sub_type == 'find_ratio':
        ad = random.randint(4, 10)
        bc = ad + random.randint(3, 8)
        ef = random.randint(ad + 1, bc - 1) # EF must be strictly between AD and BC
        
        num = ef - ad
        den = bc - ef
        g = math.gcd(num, den)
        ans_m = num // g
        ans_n = den // g
        question_text = f"如圖，四邊形 $ABCD$ 中，$\\overline{{AD}} // \\overline{{EF}} // \\overline{{BC}}$。$E$、$F$ 分別在 $\\overline{{AB}}$、$\\overline{{CD}}$ 上。<br>若 $\\overline{{AD}}={ad}$、$\\overline{{BC}}={bc}$、$\\overline{{EF}}={ef}$，則 $\\overline{{AE}}:\\overline{{EB}}$ 的比為何？"
        answer = f"{ans_m}:{ans_n}"
    
    elif sub_type == 'advanced_ef':
        # Given AE:EB=m:n, BC, find EF. This implies finding AD first.
        bc = random.randint(n + 1, 20)
        while (bc * m) % n != 0: # Ensure AD = BC*m/n is an integer
            bc = random.randint(n + 1, 20)
        
        ad = (bc * m) // n
        ef = (bc * m + ad * n) // (m + n)
        
        question_text = f"如圖，梯形 $ABCD$ 中，$\\overline{{AD}} // \\overline{{BC}}$，且對角線 $\\overline{{AC}}$、$\\overline{{BD}}$ 相交於 $G$ 點。過 $G$ 點作一直線交 $\\overline{{AB}}$ 於 $E$ 點，交 $\\overline{{CD}}$ 於 $F$ 點，且 $\\overline{{EF}} // \\overline{{BC}}$。<br>若 $\\overline{{AE}}:\\overline{{EB}} = {m}:{n}$ 且 $\\overline{{BC}} = {bc}$，則 $\\overline{{EF}}$ 的長度為何？"
        answer = str(ef)
        
    else: # find_base
        if random.random() < 0.5: # Find BC
            d = math.gcd(n, m)
            divisor = m // d
            ad = random.randint(4, 10)
            k = random.randint(1, 4)
            ef = ad + k * divisor
            bc = ((m + n) * ef - n * ad) // m
            question_text = f"如圖，四邊形 $ABCD$ 中，$\\overline{{AD}} // \\overline{{EF}} // \\overline{{BC}}$。$E$、$F$ 分別在 $\\overline{{AB}}$、$\\overline{{CD}}$ 上。<br>若 $\\overline{{AE}}:\\overline{{EB}} = {m}:{n}$，且 $\\overline{{AD}}={ad}$、$\\overline{{EF}}={ef}$，則 $\\overline{{BC}}$ 的長度為何？"
            answer = str(bc)
        else: # Find AD
            d = math.gcd(m, n)
            divisor = n // d
            bc = random.randint(10, 20)
            k = random.randint(1, 4)
            ef = bc - k * divisor
            if ef <= 0: return _generate_trapezoid_problem()
            ad = ((m + n) * ef - m * bc) // n
            if ad <= 0: return _generate_trapezoid_problem()
            question_text = f"如圖，四邊形 $ABCD$ 中，$\\overline{{AD}} // \\overline{{EF}} // \\overline{{BC}}$。$E$、$F$ 分別在 $\\overline{{AB}}$、$\\overline{{CD}}$ 上。<br>若 $\\overline{{AE}}:\\overline{{EB}} = {m}:{n}$，且 $\\overline{{BC}}={bc}$、$\\overline{{EF}}={ef}$，則 $\\overline{{AD}}$ 的長度為何？"
            answer = str(ad)
    
    return {
        "question_text": question_text,
        "answer": answer,
        "correct_answer": answer
    }
    
def _generate_construction_concept_problem():
    """
    Generates a conceptual question about ruler-and-compass construction to divide a segment.
    """
    m, n = random.sample(range(1, 8), 2)
    p = m + n
    
    prob_type = random.choice(['part_part', 'part_whole_1', 'part_whole_2'])
    
    steps = [
        "通過 $A$ 點另作一條直線 $L$。",
        f"在 $L$ 上依序取 $D$、$E$ 兩點，使得 $\\overline{{AD}}:\\overline{{DE}} = {m}:{n}$。",
        "連接 $\\overline{{BE}}$。",
        "過 $D$ 點作 $\\overline{{BE}}$ 的平行線，與 $\\overline{{AB}}$ 相交於 $C$ 點。"
    ]
    
    if prob_type == 'part_part':
        question_text = f"已知一線段 $\\overline{{AB}}$，依照下列步驟作圖：<br>1. {steps[0]}<br>2. {steps[1]}<br>3. {steps[2]}<br>4. {steps[3]}<br>則 $\\overline{{AC}}:\\overline{{CB}}$ 的比為何？"
        answer = f"{m}:{n}"
    elif prob_type == 'part_whole_1':
        steps[1] = f"在 $L$ 上依序取 $D$、$E$ 兩點，使得 $\\overline{{AD}}:\\overline{{AE}} = {m}:{p}$。"
        question_text = f"已知一線段 $\\overline{{AB}}$，依照下列步驟作圖：<br>1. {steps[0]}<br>2. {steps[1]}<br>3. {steps[2]}<br>4. {steps[3]}<br>則 $\\overline{{AC}}:\\overline{{AB}}$ 的比為何？"
        answer = f"{m}:{p}"
    else: # part_whole_2
        question_text = f"已知一線段 $\\overline{{AB}}$，依照下列步驟作圖：<br>1. {steps[0]}<br>2. {steps[1]}<br>3. {steps[2]}<br>4. {steps[3]}<br>則 $\\overline{{AC}}:\\overline{{AB}}$ 的比為何？"
        g = math.gcd(m, p)
        answer = f"{m//g}:{p//g}"

    return {
        "question_text": question_text,
        "answer": answer,
        "correct_answer": answer
    }

def generate(level=1):
    """
    生成「平行線截比例線段性質」相關題目。
    """
    problem_type = random.choice([
        'simple_algebra', 
        'quadratic_algebra', 
        'trapezoid', 
        'construction_concept'
    ])
    
    if problem_type == 'simple_algebra':
        return _generate_simple_algebra_problem()
    elif problem_type == 'quadratic_algebra':
        return _generate_quadratic_algebra_problem()
    elif problem_type == 'trapezoid':
        return _generate_trapezoid_problem()
    else: # construction_concept
        return _generate_construction_concept_problem()

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。能處理數值與比例。
    """
    user_answer = user_answer.strip().replace(" ", "")
    correct_answer = correct_answer.strip().replace(" ", "")

    is_correct = False
    
    # Check for ratio type answer, e.g., "3:5"
    if ":" in correct_answer:
        try:
            user_parts = [float(p) for p in user_answer.split(':')]
            corr_parts = [float(p) for p in correct_answer.split(':')]
            
            if len(user_parts) == 2 and len(corr_parts) == 2:
                # Avoid division by zero, use cross-multiplication for comparison
                # This correctly handles cases like 1:2 vs 2:4
                if abs(user_parts[0] * corr_parts[1] - user_parts[1] * corr_parts[0]) < 1e-9:
                    is_correct = True
        except (ValueError, IndexError):
            # Error in parsing the ratio string
            pass
    else: # Check for numerical answer
        try:
            if abs(float(user_answer) - float(correct_answer)) < 1e-9:
                is_correct = True
        except ValueError:
            # User answer is not a valid number
            pass

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}