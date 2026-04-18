import random
from fractions import Fraction

# Helper function to generate a random probability (Fraction)
def get_random_prob_fraction_simplified(cd_list=[2, 3, 4, 5, 6, 8, 9, 10, 12, 15, 20, 24, 30, 40, 60]):
    """Generates a random probability as a simplified Fraction.
    Ensures it's usually not 0 or 1, but allows for edge cases."""
    cd = random.choice(cd_list)
    num = random.randint(1, cd - 1)
    
    # Small chance to generate 0 or 1
    if random.random() < 0.05:
        num = random.choice([0, cd])

    return Fraction(num, cd).limit_denominator()

# Helper function to generate a consistent set for P(A), P(B), P(A intersect B)
def get_random_prob_set_for_union():
    """Generates a consistent set of P(A), P(B), P(A intersect B)
    such that all derived probabilities are between 0 and 1.
    Uses Venn diagram region generation (A_only, B_only, Both) to ensure consistency."""
    
    common_denominators = [12, 15, 20, 24, 30, 40, 60]
    cd = random.choice(common_denominators)

    while True:
        # Generate numerators for the disjoint regions:
        # n_a_only: number of elements in A but not B
        # n_b_only: number of elements in B but not A
        # n_both: number of elements in A and B
        
        # Ensure that these values leave enough room for each other and the 'neither' region
        # and result in non-trivial P(A) and P(B)
        
        # Max for each region is `cd`
        n_a_only = random.randint(0, cd)
        n_b_only = random.randint(0, cd)
        n_both = random.randint(0, cd)
        
        # Calculate derived numerators for P(A), P(B), P(A union B)
        n_a = n_a_only + n_both
        n_b = n_b_only + n_both
        n_union = n_a_only + n_b_only + n_both
        
        # Check consistency:
        # 1. Union must be <= total sample space (cd)
        # 2. P(A) must be > 0 and P(B) must be > 0 for a meaningful problem
        # 3. P(A) and P(B) must be <= cd
        if n_union <= cd and n_a > 0 and n_b > 0 and n_a <= cd and n_b <= cd:
            p_a = Fraction(n_a, cd).limit_denominator()
            p_b = Fraction(n_b, cd).limit_denominator()
            p_intersect = Fraction(n_both, cd).limit_denominator()
            return p_a, p_b, p_intersect

def generate_complement_prob_problem():
    """Generates a problem to find the probability of a complement event."""
    p_a = get_random_prob_fraction_simplified()
    p_a_prime = Fraction(1) - p_a

    question_text = (
        f"設 $A$ 為樣本空間的一個事件，且 $P(A) = {p_a}$，"
        f"求 $P(A')$。"
    )
    correct_answer = str(p_a_prime)
    solution_text = (
        f"利用機率的補集性質，得<br>"
        f"$P(A') = 1 - P(A) = 1 - {p_a} = {p_a_prime}$。"
    )
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "solution": solution_text
    }

def generate_union_prob_find_union_problem():
    """Generates a problem to find the probability of a union of two events."""
    p_a, p_b, p_intersect = get_random_prob_set_for_union()
    p_union = p_a + p_b - p_intersect
    
    question_text = (
        f"設 $A, B$ 為樣本空間的兩個事件，"
        f"且 $P(A) = {p_a}$, $P(B) = {p_b}$。"
        f"<br>已知 $P(A \\cap B) = {p_intersect}$，求 $P(A \\cup B)$。"
    )
    correct_answer = str(p_union)
    solution_text = (
        f"利用聯集機率公式 $P(A \\cup B) = P(A) + P(B) - P(A \\cap B)$，得<br>"
        f"$P(A \\cup B) = {p_a} + {p_b} - {p_intersect}$<br>"
        f"$= {p_union}$。"
    )
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "solution": solution_text
    }

def generate_union_prob_find_intersection_problem():
    """Generates a problem to find the probability of an intersection of two events."""
    p_a, p_b, p_intersect_actual = get_random_prob_set_for_union()
    p_union = p_a + p_b - p_intersect_actual
    
    question_text = (
        f"設 $A, B$ 為樣本空間的兩個事件，"
        f"且 $P(A) = {p_a}$, $P(B) = {p_b}$。"
        f"<br>已知 $P(A \\cup B) = {p_union}$，求 $P(A \\cap B)$。"
    )
    correct_answer = str(p_intersect_actual)
    solution_text = (
        f"因為 $P(A \\cup B) = P(A) + P(B) - P(A \\cap B)$，所以<br>"
        f"${p_union} = {p_a} + {p_b} - P(A \\cap B)$<br>"
        f"解得 $P(A \\cap B) = {p_a} + {p_b} - {p_union}$<br>"
        f"$= {p_intersect_actual}$。"
    )
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "solution": solution_text
    }

def generate_mutually_exclusive_union_problem():
    """Generates a problem to find the probability of a union of mutually exclusive events."""
    num_events = random.choice([2, 3])
    
    common_denominators = [12, 15, 20, 24, 30, 40, 60]
    cd = random.choice(common_denominators)

    if num_events == 2:
        # Generate two probabilities that sum up to at most 1, each non-zero.
        while True:
            n_a = random.randint(1, cd - 1) # P(A) must leave room for P(B)
            n_b = random.randint(1, cd - n_a) # P(B) must be at least 1 and sum up to at most cd
            if n_a + n_b <= cd: # Ensure sum <= cd
                break
        
        p_a = Fraction(n_a, cd).limit_denominator()
        p_b = Fraction(n_b, cd).limit_denominator()

        p_union = p_a + p_b
        
        question_text = (
            f"設 $A, B$ 為樣本空間的兩個互斥事件，"
            f"且 $P(A) = {p_a}$, $P(B) = {p_b}$，"
            f"求 $P(A \\cup B)$。"
        )
        correct_answer = str(p_union)
        solution_text = (
            f"因為 $A, B$ 為互斥事件，所以 $P(A \\cap B) = 0$。<br>"
            f"利用聯集機率公式 $P(A \\cup B) = P(A) + P(B) - P(A \\cap B)$，得<br>"
            f"$P(A \\cup B) = P(A) + P(B) = {p_a} + {p_b} = {p_union}$。"
        )

    else: # num_events == 3
        # Generate three probabilities that sum up to at most 1, each non-zero.
        while True:
            nums = []
            current_sum_n = 0
            # Generate numerators ensuring each is at least 1 and total sum <= cd
            for i in range(3):
                # Calculate max value for current numerator, leaving at least 1 for remaining events
                max_val_for_this_num = cd - current_sum_n - (3 - i - 1)
                if max_val_for_this_num < 1: # Should not happen with valid cd and 3 events
                    max_val_for_this_num = 1 
                n = random.randint(1, max_val_for_this_num)
                nums.append(n)
                current_sum_n += n
            
            if current_sum_n <= cd: # Final check
                break
        
        random.shuffle(nums) # Randomize which number corresponds to A, B, C
        p_events = [Fraction(n, cd).limit_denominator() for n in nums]
        sum_p = sum(p_events, Fraction(0))
        
        question_text = (
            f"設 $A, B, C$ 為樣本空間的三個互斥事件，"
            f"且 $P(A) = {p_events[0]}$, $P(B) = {p_events[1]}$, $P(C) = {p_events[2]}$，"
            f"求 $P(A \\cup B \\cup C)$。"
        )
        correct_answer = str(sum_p)
        solution_text = (
            f"因為 $A, B, C$ 為互斥事件，所以它們兩兩之間的交集機率均為 $0$。<br>"
            f"對於互斥事件，聯集機率公式可簡化為 $P(A \\cup B \\cup C) = P(A) + P(B) + P(C)$，得<br>"
            f"$P(A \\cup B \\cup C) = {p_events[0]} + {p_events[1]} + {p_events[2]} = {sum_p}$。"
        )
            
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "solution": solution_text
    }


def generate(level=1):
    """
    生成「機率的性質」相關題目。
    包括：
    1. 補集機率 P(A') = 1 - P(A)
    2. 聯集機率 P(A∪B) = P(A) + P(B) - P(A∩B) (求聯集)
    3. 聯集機率 P(A∪B) = P(A) + P(B) - P(A∩B) (求交集)
    4. 互斥事件聯集機率 P(A∪B) = P(A) + P(B) (兩事件或三事件)
    """
    problem_types = [
        'complement_prob',
        'union_prob_find_union',
        'union_prob_find_intersection',
        'mutually_exclusive_union',
    ]
    
    selected_type = random.choice(problem_types)

    if selected_type == 'complement_prob':
        return generate_complement_prob_problem()
    elif selected_type == 'union_prob_find_union':
        return generate_union_prob_find_union_problem()
    elif selected_type == 'union_prob_find_intersection':
        return generate_union_prob_find_intersection_problem()
    elif selected_type == 'mutually_exclusive_union':
        return generate_mutually_exclusive_union_problem()


def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    接受使用者輸入的分數或小數，並與正確答案（Fraction物件的字串形式）進行比較。
    """
    try:
        # Convert user's answer to a Fraction object for accurate comparison
        # This handles inputs like "1/2", "0.5", ".5"
        user_fraction = Fraction(user_answer.strip())
        correct_fraction = Fraction(correct_answer.strip())
        is_correct = (user_fraction == correct_fraction)
    except (ValueError, ZeroDivisionError):
        # Handle cases where user_answer is not a valid fraction or float representation
        is_correct = False

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}