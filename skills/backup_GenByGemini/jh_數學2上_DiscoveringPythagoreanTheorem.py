import random
import math

def simplify_sqrt(n):
    """
    Simplifies the square root of an integer n.
    Returns a string representation, e.g., "10", "\\sqrt{13}", "4\\sqrt{2}".
    """
    if not isinstance(n, int) or n < 0:
        raise ValueError("Input must be a non-negative integer.")
    if n == 0:
        return "0"
    
    # Check if n is a perfect square
    isqrt = int(math.sqrt(n))
    if isqrt * isqrt == n:
        return str(isqrt)

    # Find the largest square factor of n
    # We want to write n as a^2 * b, where b is square-free
    a = 1  # The coefficient outside the square root
    b = n  # The radicand (the number inside the square root)
    
    # Iterate from the largest possible integer factor downwards
    for i in range(isqrt, 1, -1):
        if n % (i * i) == 0:
            a = i
            b = n // (i * i)
            break
            
    if a == 1:  # No perfect square factor found (other than 1)
        return f"\\sqrt{{{n}}}"
    else:
        return f"{a}\\sqrt{{{b}}}"

def generate_find_hypotenuse():
    """
    Generates a problem asking to find the hypotenuse given two legs.
    """
    # Use Pythagorean triples for cleaner, integer-based problems about 50% of the time.
    pythagorean_triples = [(3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25)]
    
    if random.random() < 0.6:  # 60% chance to use a Pythagorean triple
        base_a, base_b, base_c = random.choice(pythagorean_triples)
        k = random.randint(1, 4) # Scaling factor
        leg1, leg2, hypotenuse = base_a * k, base_b * k, base_c * k
        if random.random() < 0.5: # Randomly swap legs
            leg1, leg2 = leg2, leg1
        
        question_text = f"一個直角三角形的兩股長分別為 ${leg1}$ 和 ${leg2}$，請求出其斜邊長度。"
        correct_answer = str(hypotenuse)
    else: # Generate a problem that may result in a radical answer
        leg1 = random.randint(2, 10)
        leg2 = random.randint(2, 10)
        
        # Avoid accidentally creating a common triple
        while (leg1, leg2) in [(3,4), (4,3), (6,8), (8,6)]:
             leg1 = random.randint(2, 10)
             leg2 = random.randint(2, 10)

        hypotenuse_squared = leg1**2 + leg2**2
        correct_answer = simplify_sqrt(hypotenuse_squared)
        question_text = f"一個直角三角形的兩股長分別為 ${leg1}$ 和 ${leg2}$，請求出其斜邊長度。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_find_leg():
    """
    Generates a problem asking to find a leg given the other leg and the hypotenuse.
    """
    pythagorean_triples = [(3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25)]
    
    if random.random() < 0.6: # 60% chance to use a Pythagorean triple
        base_a, base_b, base_c = random.choice(pythagorean_triples)
        k = random.randint(1, 4)
        
        legs = [base_a * k, base_b * k]
        known_leg = random.choice(legs)
        unknown_leg = legs[0] if known_leg == legs[1] else legs[1]
        hypotenuse = base_c * k
        
        question_text = f"一個直角三角形中，已知一股長為 ${known_leg}$，斜邊長為 ${hypotenuse}$，請求出另一股的長度。"
        correct_answer = str(unknown_leg)
    else: # Generate a problem that may result in a radical answer
        known_leg = random.randint(3, 15)
        # Ensure hypotenuse is larger than the known leg
        hypotenuse = random.randint(known_leg + 1, known_leg + 10)

        unknown_leg_squared = hypotenuse**2 - known_leg**2
        correct_answer = simplify_sqrt(unknown_leg_squared)
        question_text = f"一個直角三角形中，已知一股長為 ${known_leg}$，斜邊長為 ${hypotenuse}$，請求出另一股的長度。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_quad_side():
    """
    Generates a multi-step problem involving a quadrilateral composed of two right triangles.
    """
    # We need to find a, b, c, d such that a^2 + b^2 = c^2 + d^2
    # We will generate a, b, c and find d.
    ab = random.randint(3, 9)
    ad = random.choice([x for x in range(3, 10) if x != ab])
    
    bd_sq = ab**2 + ad**2
    
    # Choose bc such that bc^2 < bd_sq
    bc_max = int(math.sqrt(bd_sq))
    # Ensure there's a valid range for bc
    if bc_max <= 3:
        # Regenerate if values are too small to make a good problem
        return generate_quad_side()
        
    bc = random.randint(3, bc_max -1)
    
    # Ensure we don't pick a side that makes the other side 0 or the same
    if bc in [ab, ad]:
        return generate_quad_side() # Retry for more varied problems

    cd_sq = bd_sq - bc**2

    ans_bd = simplify_sqrt(bd_sq)
    ans_cd = simplify_sqrt(cd_sq)
    
    question_text = (
        f"如一個四邊形 $ABCD$，其中 $\\angle A = 90^\\circ$ 且 $\\angle C = 90^\\circ$。"
        f"已知邊長 $\\overline{{AB}} = {ab}$，$\\overline{{BC}} = {bc}$，且 $\\overline{{AD}} = {ad}$。"
        f"\\n請依序回答下列問題：\\n"
        f" (1) 對角線 $\\overline{{BD}}$ 的長度為何？\\n"
        f" (2) 邊長 $\\overline{{CD}}$ 的長度為何？\\n"
        f"（請將兩個答案以逗號分隔，例如：5,\\sqrt{{41}}）"
    )
    correct_answer = f"{ans_bd},{ans_cd}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def generate(level=1):
    """
    生成畢氏定理相關題目。
    - find_hypotenuse: 已知兩股長，求斜邊長。
    - find_leg: 已知一股與斜邊長，求另一股長。
    - quad_side: 應用於四邊形的綜合問題。
    """
    problem_type = random.choice(['find_hypotenuse', 'find_leg', 'quad_side'])
    
    if problem_type == 'find_hypotenuse':
        return generate_find_hypotenuse()
    elif problem_type == 'find_leg':
        return generate_find_leg()
    else: # quad_side
        return generate_quad_side()

def check(user_answer, correct_answer):
    """
    檢查使用者答案是否正確。
    能處理單一答案以及逗號分隔的多重答案。
    """
    # Normalize by removing all spaces for robust comparison
    user_answer_norm = ''.join(user_answer.split())
    correct_answer_norm = ''.join(correct_answer.split())

    is_correct = (user_answer_norm == correct_answer_norm)
    
    # Format the feedback text based on the answer structure
    if ',' in correct_answer:
        parts = correct_answer.split(',')
        feedback_ans = f"$\\overline{{BD}} = {parts[0]}$ 且 $\\overline{{CD}} = {parts[1]}$"
    else:
        feedback_ans = f"${correct_answer}$"

    if is_correct:
        result_text = f"完全正確！答案是 {feedback_ans}。"
    else:
        result_text = f"答案不正確。正確答案應為：{feedback_ans}。"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}