import random
import math
from fractions import Fraction

# Helper functions for permutations
def _factorial(n):
    """Calculates n!"""
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    if n == 0:
        return 1
    return math.factorial(n)

def _permutation(n, k):
    """Calculates P(n, k) = n! / (n-k)!"""
    if not (0 <= k <= n):
        raise ValueError("Invalid input for permutation: k must be between 0 and n")
    # For efficiency and to prevent overflow from large factorials before division
    # P(n, k) = n * (n-1) * ... * (n-k+1)
    result = 1
    for i in range(k):
        result *= (n - i)
    return result

def generate(level=1):
    """
    生成「直線排列」相關題目。
    包含：
    1. 全排列 (n!)
    2. 選取 k 個排列 (P(n, k))
    3. 特殊限制條件 (如數字0的百位數限制)
    4. 相鄰或不相鄰排列
    """
    problem_types = [
        'factorial_all',
        'permutation_nk',
        'zero_restriction',
        'grouping_together',
        'grouping_separated'
    ]
    
    # For level 1, select a problem type. Inclusion-Exclusion is usually for higher levels.
    problem_type = random.choice(problem_types)

    if problem_type == 'factorial_all':
        return _generate_factorial_all()
    elif problem_type == 'permutation_nk':
        return _generate_permutation_nk()
    elif problem_type == 'zero_restriction':
        return _generate_zero_restriction()
    elif problem_type == 'grouping_together':
        return _generate_grouping(condition='together')
    elif problem_type == 'grouping_separated':
        return _generate_grouping(condition='separated')

def _generate_factorial_all():
    """Generates a problem for simple n! permutation."""
    n = random.randint(4, 7) # Keep n smaller for typical contest scenarios
    items_name = random.choice(['同學', '參賽者', '書籍', '選手'])
    action = random.choice(['抽籤決定出場順序', '排成一列', '放入書架', '決定比賽順序'])

    question_text = f"共有 ${{n}}$ 位 ${{items_name}}$，如果他們要依序 ${{action}}$。請問共有多少種不同的排法？"
    correct_answer_val = _factorial(n)
    
    return {
        "question_text": question_text,
        "answer": str(correct_answer_val),
        "correct_answer": str(correct_answer_val)
    }

def _generate_permutation_nk():
    """Generates a problem for P(n, k) permutation."""
    n = random.randint(6, 10)
    k = random.randint(2, min(n - 1, 4)) # k should be smaller than n, and not too big
    
    # Ensure n is sufficiently larger than k for interesting P(n,k)
    while n - k < 2:
        n = random.randint(6, 10)
        k = random.randint(2, min(n - 1, 4))

    item_type = random.choice(['歌曲', '電影', '課程', '書籍'])
    action = random.choice(['依序表演', '連續播放', '依序選修', '排列'])
    
    question_text = f"某人想從 ${{n}}$ 首 ${{item_type}}$ 中，選出 ${{k}}$ 首 ${{action}}$。請問其安排的方案共有多少種？"
    correct_answer_val = _permutation(n, k)
    
    return {
        "question_text": question_text,
        "answer": str(correct_answer_val),
        "correct_answer": str(correct_answer_val)
    }

def _generate_zero_restriction():
    """Generates a problem with restriction (e.g., 0 cannot be in the highest place)."""
    n_total_digits = random.randint(4, 6) # e.g., 0, 1, 2, 3, 4 (n=5)
    k_digits_to_form = random.randint(3, n_total_digits - 1) # e.g., 3-digit number from 5 digits
    
    # Ensure k_digits_to_form is at least 3 for a "hundreds place" problem to make sense.
    if k_digits_to_form < 3:
        k_digits_to_form = 3 
        if n_total_digits < k_digits_to_form + 1: # Need at least k+1 digits total including 0
            n_total_digits = k_digits_to_form + random.randint(1, 2)
            
    digits_list = ", ".join(map(str, range(n_total_digits)))
    
    # Total permutations without considering the 0 restriction
    total_permutations = _permutation(n_total_digits, k_digits_to_form)
    # Invalid permutations where 0 is in the first (highest) place
    # This means 0 is fixed in the first place, and we arrange k-1 digits from the remaining n_total_digits-1 digits
    invalid_permutations = _permutation(n_total_digits - 1, k_digits_to_form - 1)
    
    correct_answer_val = total_permutations - invalid_permutations

    question_text = f"從 $0, {digits_list[3:]}$ 等 ${{n_total_digits}}$ 個數字中，任選 ${{k_digits_to_form}}$ 個相異數字，共可排出多少個 ${{k_digits_to_form}}$ 位數？"
    
    return {
        "question_text": question_text,
        "answer": str(correct_answer_val),
        "correct_answer": str(correct_answer_val)
    }

def _generate_grouping(condition):
    """Generates a problem where items must be grouped together or separated."""
    num_group1 = random.randint(3, 5) # e.g., 4 boys
    num_group2 = random.randint(2, 3) # e.g., 3 girls
    
    group1_name = random.choice(['男生', '成人', '工程師'])
    group2_name = random.choice(['女生', '小孩', '實習生'])
    
    # Ensure num_group1 is large enough for separation to be possible
    # We need at least num_group2 - 1 items in group 1 to create enough gaps for separation
    # (num_group1 items create num_group1 + 1 gaps)
    # So, num_group1 + 1 >= num_group2 --> num_group1 >= num_group2 - 1
    while condition == 'separated' and num_group1 < num_group2 - 1:
        num_group1 = random.randint(3, 5)

    if condition == 'together':
        # Treat the num_group2 items as one block. Total items to arrange: num_group1 + 1 (the block).
        # Internal arrangement of num_group2 items: num_group2!
        correct_answer_val = _factorial(num_group1 + 1) * _factorial(num_group2)
        question_text = f"${{group1_name}}$ ${{num_group1}}$ 人及 ${{group2_name}}$ ${{num_group2}}$ 人排成一列拍照。若 ${{group2_name}}$ ${{num_group2}}$ 人完全相鄰，請問共有多少種排法？"

    else: # condition == 'separated'
        # First arrange num_group1 items: num_group1!
        # This creates num_group1 + 1 gaps. Choose num_group2 gaps for num_group2 items: P(num_group1 + 1, num_group2)
        correct_answer_val = _factorial(num_group1) * _permutation(num_group1 + 1, num_group2)
        question_text = f"${{group1_name}}$ ${{num_group1}}$ 人及 ${{group2_name}}$ ${{num_group2}}$ 人排成一列拍照。若 ${{group2_name}}$ ${{num_group2}}$ 人完全分開，請問共有多少種排法？"

    return {
        "question_text": question_text,
        "answer": str(correct_answer_val),
        "correct_answer": str(correct_answer_val)
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
    
    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}