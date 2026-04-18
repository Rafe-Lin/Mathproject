import random
from fractions import Fraction
import math

class Interval:
    """
    Represents a mathematical interval (e.g., [a, b), (c, d]).
    Handles operations like intersection, union, difference, and complement.
    """
    def __init__(self, start, end, start_inclusive=False, end_inclusive=False):
        # Handle empty set representation
        if start is None:
            self.start = float('inf')
            self.end = float('-inf')
            self.start_inclusive = False
            self.end_inclusive = False
        else:
            self.start = start
            self.end = end
            self.start_inclusive = start_inclusive
            self.end_inclusive = end_inclusive
        
        # Normalize intervals: if start > end, or start == end and not both inclusive, it's empty
        if self.start > self.end:
            self.start = float('inf')
            self.end = float('-inf')
        elif self.start == self.end and (not self.start_inclusive or not self.end_inclusive):
            self.start = float('inf')
            self.end = float('-inf')

    def is_empty(self):
        """Checks if the interval represents an empty set."""
        return self.start > self.end

    def to_latex(self):
        """Converts the interval to its LaTeX string representation."""
        if self.is_empty():
            return r"\emptyset"

        start_bracket = "[" if self.start_inclusive else "("
        end_bracket = "]" if self.end_inclusive else ")"

        start_val = r"-\infty" if self.start == float('-inf') else str(self.start)
        end_val = r"\infty" if self.end == float('inf') else str(self.end)
        
        return f"{start_bracket}{start_val}, {end_val}{end_bracket}"

    def contains_point(self, x):
        """Checks if a point x is contained within the interval, considering inclusivity."""
        if self.is_empty():
            return False
        
        if x < self.start: return False
        if x == self.start and not self.start_inclusive: return False
        if x > self.end: return False
        if x == self.end and not self.end_inclusive: return False
        
        return True

    @staticmethod
    def intersection(int1, int2):
        """Computes the intersection of two intervals."""
        if int1.is_empty() or int2.is_empty():
            return Interval(None, None)

        new_start = max(int1.start, int2.start)
        new_end = min(int1.end, int2.end)

        if new_start > new_end: # No overlap
            return Interval(None, None)
        
        new_start_inclusive = int1.contains_point(new_start) and int2.contains_point(new_start)
        new_end_inclusive = int1.contains_point(new_end) and int2.contains_point(new_end)

        return Interval(new_start, new_end, new_start_inclusive, new_end_inclusive)

    @staticmethod
    def union(int1, int2):
        """
        Computes the union of two intervals. Returns a list of intervals,
        as the union might be disjoint (two separate intervals).
        """
        if int1.is_empty(): return [int2]
        if int2.is_empty(): return [int1]

        # Assume int1.start <= int2.start for simpler logic (swap if needed)
        if int1.start > int2.start:
            int1, int2 = int2, int1 

        # Check for overlap or adjacency (touching)
        overlap_or_adjacent = False
        if int1.end > int2.start: # Overlap
            overlap_or_adjacent = True
        elif int1.end == int2.start: # Adjacent
            if int1.end_inclusive or int2.start_inclusive: # They touch inclusively
                overlap_or_adjacent = True
            
        if overlap_or_adjacent:
            new_start = int1.start
            new_start_inclusive = int1.start_inclusive

            new_end = max(int1.end, int2.end)
            new_end_inclusive = False
            if int1.end == new_end:
                new_end_inclusive = int1.end_inclusive
            if int2.end == new_end:
                new_end_inclusive = new_end_inclusive or int2.end_inclusive # Union, so if either is inclusive, it is.

            return [Interval(new_start, new_end, new_start_inclusive, new_end_inclusive)]
        else:
            return [int1, int2] # Disjoint

def merge_intervals(intervals):
    """
    Merges a list of intervals, combining overlapping or adjacent ones.
    Useful for simplifying union and complement results.
    """
    if not intervals:
        return []

    intervals = [i for i in intervals if not i.is_empty()]
    if not intervals:
        return []

    # Sort intervals by their start point
    intervals.sort(key=lambda x: (x.start, not x.start_inclusive))

    merged = [intervals[0]]
    for current in intervals[1:]:
        last_merged = merged[-1]
        
        overlap_or_adjacent = False
        if last_merged.end > current.start:
            overlap_or_adjacent = True
        elif last_merged.end == current.start:
            if last_merged.end_inclusive or current.start_inclusive:
                overlap_or_adjacent = True

        if overlap_or_adjacent:
            # Merge the current interval into the last merged one
            new_end = max(last_merged.end, current.end)
            new_end_inclusive = False
            if last_merged.end == new_end:
                new_end_inclusive = last_merged.end_inclusive
            if current.end == new_end:
                new_end_inclusive = new_end_inclusive or current.end_inclusive
            
            merged[-1] = Interval(last_merged.start, new_end, last_merged.start_inclusive, new_end_inclusive)
        else:
            merged.append(current)
    return merged

def interval_complement(int_A, U_start=float('-inf'), U_end=float('inf')):
    """
    Computes the complement of an interval A relative to a universe [U_start, U_end].
    Assumes U_start <= U_end.
    """
    universe_interval = Interval(U_start, U_end, True, True)

    if int_A.is_empty():
        return [universe_interval]

    results = []

    # Part before A starts (within the universe)
    if int_A.start > U_start:
        results.append(Interval(U_start, int_A.start, True, not int_A.start_inclusive))
    elif int_A.start == U_start and not int_A.start_inclusive:
         results.append(Interval(U_start, int_A.start, True, not int_A.start_inclusive))

    # Part after A ends (within the universe)
    if int_A.end < U_end:
        results.append(Interval(int_A.end, U_end, not int_A.end_inclusive, True))
    elif int_A.end == U_end and not int_A.end_inclusive:
         results.append(Interval(int_A.end, U_end, not int_A.end_inclusive, True))

    # If A covers the whole universe, its complement is empty
    if int_A.start <= U_start and int_A.end >= U_end \
        and (int_A.start < U_start or int_A.start_inclusive) \
        and (int_A.end > U_end or int_A.end_inclusive):
        return [Interval(None, None)] # Return a list containing an empty interval

    return merge_intervals(results)

def calculate_difference(int_A, int_B, U_start=float('-inf'), U_end=float('inf')):
    """
    Computes the set difference A - B, which is equivalent to A ∩ B'.
    B' is calculated relative to the given universe [U_start, U_end].
    """
    b_complement_intervals = interval_complement(int_B, U_start, U_end)
    
    result_intervals = []
    for b_prime_int in b_complement_intervals:
        intersection_result = Interval.intersection(int_A, b_prime_int)
        if not intersection_result.is_empty():
            result_intervals.append(intersection_result)
            
    return merge_intervals(result_intervals)

def generate_logic_problem():
    """Generates a problem about logical propositions and their truth values."""
    proposition_pool = [
        {"statement": "長方形都是正方形", "value": False},
        {"statement": "正三角形都是等腰三角形", "value": True},
        {"statement": "$3 > 5$", "value": False},
        {"statement": "$2 + 2 = 4$", "value": True},
        {"statement": "所有偶數都能被 $2$ 整除", "value": True},
        {"statement": "所有的質數都是奇數", "value": False}, # 2 is prime and even
        {"statement": "三角形內角和為 $180$ 度", "value": True},
        {"statement": "平行四邊形都是菱形", "value": False},
        {"statement": r"若 $x=1$，則 $x^2=1$", "value": True},
        {"statement": r"若 $x^2=1$，則 $x=1$", "value": False} # x could be -1
    ]

    num_propositions = random.choice([2, 3])
    selected_propositions = random.sample(proposition_pool, num_propositions)
    
    p_info = selected_propositions[0]
    q_info = selected_propositions[1]
    r_info = selected_propositions[2] if num_propositions == 3 else None

    prop_vars = ['P', 'Q', 'R']
    prop_map = {'P': p_info}
    if q_info: prop_map['Q'] = q_info
    if r_info: prop_map['R'] = r_info

    prop_declarations = []
    for var, info in prop_map.items():
        prop_declarations.append(f"${var}$：{info['statement']}")
    
    compound_options = []
    compound_options.append({'formula': '$P$', 'eval': lambda p, q, r: p['value']})
    compound_options.append({'formula': '$Q$', 'eval': lambda p, q, r: q['value']})
    compound_options.append({'formula': '$P$ 且 $Q$', 'eval': lambda p, q, r: p['value'] and q['value']})
    compound_options.append({'formula': '$P$ 或 $Q$', 'eval': lambda p, q, r: p['value'] or q['value']})
    compound_options.append({'formula': r'$\neg P$', 'eval': lambda p, q, r: not p['value']})

    if num_propositions == 3:
        compound_options.append({'formula': '$Q$ 且 $R$', 'eval': lambda p, q, r: q['value'] and r['value']})
        compound_options.append({'formula': '$P$ 或 $R$', 'eval': lambda p, q, r: p['value'] or r['value']})
        compound_options.append({'formula': r'$\neg Q$', 'eval': lambda p, q, r: not q['value']})

    chosen_compound = random.choice(compound_options)
    
    correct_bool_value = chosen_compound['eval'](p_info, q_info, r_info)
    correct_answer = "真" if correct_bool_value else "假"

    question_text = f"設 {', '.join(prop_declarations)}。<br>請問命題 {chosen_compound['formula']} 的真假值為何？(請填入「真」或「假」)"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_set_operation_problem():
    """Generates a problem about set operations on intervals."""
    # Generate 4 distinct points, sorted, with a reasonable spread
    all_points_set = set()
    while len(all_points_set) < 4:
        all_points_set.add(random.randint(-15, 15))
    all_points = sorted(list(all_points_set))
    
    # Define A and B to ensure some interaction/overlap
    A = Interval(
        all_points[0], all_points[2], 
        random.choice([True, False]), random.choice([True, False])
    )
    B = Interval(
        all_points[1], all_points[3], 
        random.choice([True, False]), random.choice([True, False])
    )

    set_ops = ['intersection', 'union', 'difference_A_B', 'complement_A']
    chosen_op_type = random.choice(set_ops)

    result_intervals = []
    if chosen_op_type == 'intersection':
        result_intervals = [Interval.intersection(A, B)]
        operation_text = r"$A \cap B$"
    elif chosen_op_type == 'union':
        result_intervals = Interval.union(A, B)
        operation_text = r"$A \cup B$"
    elif chosen_op_type == 'difference_A_B':
        result_intervals = calculate_difference(A, B)
        operation_text = r"$A - B$"
    elif chosen_op_type == 'complement_A':
        result_intervals = interval_complement(A) # Universe is R by default
        operation_text = r"$A'$"
    
    merged_results = merge_intervals(result_intervals)
    if not merged_results or (len(merged_results) == 1 and merged_results[0].is_empty()):
        correct_answer = r"$\emptyset$"
    else:
        correct_answer_parts = [i.to_latex() for i in merged_results]
        correct_answer = " $\\cup$ ".join(correct_answer_parts)
    
    question_text = (
        f"已知宇集為實數 $\mathbb{{R}}$，設集合 $A = {A.to_latex()}$，$B = {B.to_latex()}$。<br>"
        f"求下列集合：{operation_text}"
    )

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    生成「邏輯與集合」相關題目。
    包含：
    1. 邏輯命題真假判斷
    2. 集合運算 (交集、聯集、差集、補集)
    """
    problem_type = random.choice(['logic', 'set_operations'])
    
    if problem_type == 'logic':
        return generate_logic_problem()
    elif problem_type == 'set_operations':
        return generate_set_operation_problem()

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    Handles common variations for truth values, empty set, and infinity symbols.
    """
    user_answer_raw = user_answer.strip()
    correct_answer_raw = correct_answer.strip()

    # Basic normalization: remove spaces, convert to lowercase for comparison
    user_answer_normalized = user_answer_raw.replace(" ", "").lower()
    correct_answer_normalized = correct_answer_raw.replace(" ", "").lower()
    
    is_correct = False

    # 1. Direct string comparison (case-insensitive, space-insensitive)
    if user_answer_normalized == correct_answer_normalized:
        is_correct = True
    
    # 2. Specific checks for logic truth values
    if correct_answer_normalized == "真" and user_answer_normalized in ["真", "t", "true", "yes"]:
        is_correct = True
    elif correct_answer_normalized == "假" and user_answer_normalized in ["假", "f", "false", "no"]:
        is_correct = True

    # 3. Handle common alternative spellings for empty set and infinity
    if not is_correct:
        # Standardize empty set representations
        user_normalized_for_sets = user_answer_normalized.replace(r"\emptyset", "empty").replace("{}", "empty").replace(r"\{\}", "empty")
        correct_normalized_for_sets = correct_answer_normalized.replace(r"\emptyset", "empty").replace("{}", "empty").replace(r"\{\}", "empty")
        
        # Standardize infinity representations
        user_normalized_for_sets = user_normalized_for_sets.replace("-inf", r"-\infty").replace("inf", r"\infty").replace("infinity", r"\infty")
        correct_normalized_for_sets = correct_normalized_for_sets.replace("-inf", r"-\infty").replace("inf", r"\infty").replace("infinity", r"\infty")

        # After standardization, compare
        if user_normalized_for_sets == correct_normalized_for_sets:
            is_correct = True

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}