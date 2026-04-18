import random
from fractions import Fraction
import math

# Helper to convert Fraction or float (for infinity) to string for LaTeX display
def _fraction_to_string(f_or_float):
    if isinstance(f_or_float, Fraction):
        if f_or_float.denominator == 1:
            return str(f_or_float.numerator)
        return f"\\frac{{{f_or_float.numerator}}}{{{f_or_float.denominator}}}"
    elif isinstance(f_or_float, float):
        if math.isinf(f_or_float):
            return r"\\infty" if f_or_float > 0 else r"-\\infty"
        # Attempt to represent float as fraction if it's a simple decimal
        f = Fraction(f_or_float).limit_denominator(1000) 
        if f.denominator == 1:
            return str(f.numerator)
        # Only return frac if original float was not an integer and limit_denominator helped
        if f_or_float != round(f_or_float): # Check if original float was conceptually an integer
            return f"\\frac{{{f.numerator}}}{{{f.denominator}}}"
        return str(round(f_or_float)) # If it was like 2.0
    return str(f_or_float) # Fallback for unexpected types (should not happen for valid bounds)

# Helper to format a list of intervals into a LaTeX-ready string
def _format_interval_string(interval_list):
    if not interval_list:
        return r"\\emptyset" # Empty set
    
    formatted_parts = []
    # Sort intervals to ensure correct union representation (e.g., (-\infty,0) U (1,3))
    interval_list.sort(key=lambda x: x[0])

    for start, end, start_inclusive, end_inclusive in interval_list:
        start_char = '[' if start_inclusive else '('
        end_char = ']' if end_inclusive else ')'
        
        start_str = _fraction_to_string(start)
        end_str = _fraction_to_string(end)
        
        formatted_parts.append(f"{start_char}{start_str}, {end_str}{end_char}")
        
    if len(formatted_parts) > 1:
        return r" \\cup ".join(formatted_parts)
    elif formatted_parts:
        return formatted_parts[0]
    return r"\\emptyset" # Should not happen if interval_list is not empty

# Helper to solve basic absolute value inequalities like |ax+b| op c
# Returns a list of (start, end, start_inclusive, end_inclusive) tuples
def _solve_single_abs_ineq(a, b, c, op):
    # Assumes c is an integer. If c <= 0, special rules apply.
    # Current generation ensures c > 0 for simpler problem types.
    
    intervals = []
    
    if op in ['<', '<=']:
        # -c < ax+b < c  or  -c <= ax+b <= c
        # Valid only if c > 0. If c <= 0, solution is empty or a point.
        if c <= 0:
            if c == 0 and op == '<=': # |ax+b| <= 0 means ax+b = 0
                if a == 0: # |b| <= 0, only if b=0, then 0 <= 0 (all reals), else empty.
                    if b == 0: return [(float('-inf'), float('inf'), True, True)]
                    else: return []
                point = Fraction(-b, a)
                return [(point, point, True, True)] # Single point solution
            else: # |ax+b| < 0 or |ax+b| <= c (c < 0)
                return [] # No solution
        
        val_lower = Fraction(-c - b, a)
        val_upper = Fraction(c - b, a)
        
        start_inclusive = (op == '<=')
        end_inclusive = (op == '<=')
        
        if a > 0:
            intervals.append((val_lower, val_upper, start_inclusive, end_inclusive))
        else: # a < 0, bounds flip
            intervals.append((val_upper, val_lower, start_inclusive, end_inclusive))
            
    elif op in ['>', '>=']:
        # ax+b > c  or  ax+b < -c   (or with >=)
        # If c < 0: |ax+b| > c (e.g. |X| > -5) is always true (all real numbers).
        #           |ax+b| >= c is always true.
        if c < 0:
            return [(float('-inf'), float('inf'), True, True)]
        # If c = 0: |ax+b| > 0 means ax+b != 0. All reals except -b/a.
        #           |ax+b| >= 0 means all reals.
        elif c == 0:
            if op == '>':
                if a == 0: # |b| > 0
                    if b == 0: return [] # |0| > 0 is false
                    else: return [(float('-inf'), float('inf'), True, True)] # |non_zero| > 0 is true
                point = Fraction(-b, a)
                intervals.append((float('-inf'), point, False, False))
                intervals.append((point, float('inf'), False, False))
            else: # op == '>='
                intervals.append((float('-inf'), float('inf'), True, True))
            return intervals

        # Standard case for c > 0
        x_bound1 = Fraction(c - b, a)
        x_bound2 = Fraction(-c - b, a)
        
        start_inclusive = (op == '>=')
        end_inclusive = (op == '>=') # This is for the finite bound itself in the interval
        
        if a > 0:
            # x > x_bound1 OR x < x_bound2
            intervals.append((float('-inf'), x_bound2, False, end_inclusive))
            intervals.append((x_bound1, float('inf'), start_inclusive, False))
        else: # a < 0, inequalities flip
            # x < x_bound1 OR x > x_bound2
            intervals.append((float('-inf'), x_bound1, False, end_inclusive))
            intervals.append((x_bound2, float('inf'), start_inclusive, False))
            
    return intervals

# Helper to find the intersection of two lists of intervals
def _intersect_intervals(intervals1, intervals2):
    # intervals1 and intervals2 are lists of (start, end, start_inclusive, end_inclusive)
    # Assumes intervals within each list are sorted and non-overlapping.
    
    result = []
    
    for i1_s, i1_e, i1_si, i1_ei in intervals1:
        for i2_s, i2_e, i2_si, i2_ei in intervals2:
            
            # Find the intersection of two individual intervals
            int_s = max(i1_s, i2_s)
            int_e = min(i1_e, i2_e)
            
            # If no overlap, continue
            if int_s > int_e:
                continue
            
            # Determine start_inclusive for intersection
            new_si = False
            if int_s == i1_s and int_s == i2_s: 
                new_si = i1_si and i2_si
            elif int_s == i1_s: 
                new_si = i1_si
            elif int_s == i2_s: 
                new_si = i2_si
            else: 
                new_si = True
                
            # Determine end_inclusive for intersection
            new_ei = False
            if int_e == i1_e and int_e == i2_e: 
                new_ei = i1_ei and i2_ei
            elif int_e == i1_e: 
                new_ei = i1_ei
            elif int_e == i2_e: 
                new_ei = i2_ei
            else: 
                new_ei = True
            
            # Special case for single point intersection:
            if int_s == int_e:
                if new_si and new_ei: # Only include if both are inclusive
                    result.append((int_s, int_e, True, True))
            else:
                result.append((int_s, int_e, new_si, new_ei))
                
    # Merge overlapping/adjacent intervals in the result
    if not result:
        return []

    result.sort(key=lambda x: x[0])
    merged = [result[0]]

    for current in result[1:]:
        prev_s, prev_e, prev_si, prev_ei = merged[-1]
        curr_s, curr_e, curr_si, curr_ei = current

        # Check for overlap or adjacency (e.g., [0,1] and (1,2] should merge to [0,2])
        # prev_e >= curr_s (overlap) OR prev_e == curr_s AND (prev_ei OR curr_si) (adjacency)
        if prev_e > curr_s or (prev_e == curr_s and (prev_ei or curr_si)):
            # Merge
            new_s = prev_s
            new_si = prev_si # The start inclusiveness is determined by the first interval in the merged segment.
            
            # Determine new_e and new_ei
            if curr_e > prev_e:
                new_e = curr_e
                new_ei = curr_ei
            elif prev_e > curr_e:
                new_e = prev_e
                new_ei = prev_ei
            else: # prev_e == curr_e
                new_e = prev_e
                new_ei = prev_ei or curr_ei # If ends are same, inclusive if either was
            
            merged[-1] = (new_s, new_e, new_si, new_ei)
        else:
            merged.append(current)
            
    return merged

# Helper to solve compound absolute value inequalities like c1 < |ax+b| < c2
# Returns a list of (start, end, start_inclusive, end_inclusive) tuples
def _solve_compound_abs_ineq(a, b, c1, c2):
    # This is equivalent to (c1 < |ax+b|) AND (|ax+b| < c2)
    # Assumes 0 < c1 < c2
    
    # Solve |ax+b| < c2
    intervals_less_c2 = _solve_single_abs_ineq(a, b, c2, '<')
    
    # Solve |ax+b| > c1
    intervals_greater_c1 = _solve_single_abs_ineq(a, b, c1, '>')
    
    # Intersect the two solution sets
    final_intervals = _intersect_intervals(intervals_less_c2, intervals_greater_c1)
    
    return final_intervals

def generate(level=1):
    problem_type_choices = ['simple']
    if level >= 2:
        problem_type_choices.append('compound')
    
    problem_type = random.choice(problem_type_choices)

    a = random.choice([-3, -2, -1, 1, 2, 3]) # Coefficient of x, cannot be 0
    b = random.randint(-5, 5) # Constant term
    
    # Format the expression ax+b for display in LaTeX
    expr_str = ""
    if a == 1:
        expr_str += "x"
    elif a == -1:
        expr_str += "-x"
    else:
        expr_str += f"{a}x"
    
    if b > 0:
        expr_str += f"+{b}"
    elif b < 0:
        expr_str += f"-{-b}"

    question_text = ""
    correct_answer_str = ""

    if problem_type == 'simple':
        c = random.randint(1, 10) # c > 0 for standard problems
        op = random.choice(['<', '>', '<=', '>='])
        
        question_text = f"解不等式 $|{expr_str}| {op} {c}$。"
        
        intervals = _solve_single_abs_ineq(a, b, c, op)
        correct_answer_str = _format_interval_string(intervals)

    else: # 'compound'
        c1 = random.randint(1, 5)
        c2 = random.randint(c1 + 1, 10) # Ensure c1 < c2
        
        question_text = f"解不等式 ${c1} < |{expr_str}| < {c2}$。"
        
        intervals = _solve_compound_abs_ineq(a, b, c1, c2)
        correct_answer_str = _format_interval_string(intervals)
    
    return {
        "question_text": question_text,
        "answer": correct_answer_str,
        "correct_answer": correct_answer_str
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    def normalize_answer(ans_str):
        ans_str = ans_str.strip()
        ans_str = ans_str.replace(" ", "") # Remove all spaces
        ans_str = ans_str.replace("inf", r"\\infty") # Standardize infinity
        ans_str = ans_str.replace("Inf", r"\\infty")
        ans_str = ans_str.replace(r"U", r"\\cup") # Standardize union
        ans_str = ans_str.replace(r"u", r"\\cup")
        ans_str = ans_str.replace(r"\\cup", r"\\cup") # Ensure double backslash
        ans_str = ans_str.replace(r"\\infty", r"\\infty") # Ensure double backslash
        ans_str = ans_str.replace(r"\\emptyset", r"\\emptyset") # Ensure double backslash
        # For fractions, user might type "1/2" or LaTeX "frac{1}{2}"
        # This requires more complex parsing for a truly flexible check.
        # For now, expect the exact LaTeX format for fractions or integer forms.
        return ans_str

    normalized_user_answer = normalize_answer(user_answer)
    normalized_correct_answer = normalize_answer(correct_answer)
    
    is_correct = (normalized_user_answer == normalized_correct_answer)
    
    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}