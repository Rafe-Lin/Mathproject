import random
import math
from fractions import Fraction
import re
import uuid 

# --- Helper functions for formatting and solving ---

def format_polynomial(coeffs, var='x'):
    """
    Formats a list of coefficients [a_n, a_{n-1}, ..., a_1, a_0] into a polynomial string.
    Example: [1, -4, 3] -> x^2 - 4x + 3
    Example: [-1, 1, 3] -> -x^2 + x + 3
    """
    if not coeffs:
        return "0"
    
    terms = []
    degree = len(coeffs) - 1
    
    for i, coeff in enumerate(coeffs):
        if coeff == 0:
            continue
        
        current_degree = degree - i
        
        # Determine sign
        if coeff > 0 and terms: # If not the first term and positive, add '+'
            term_sign = "+"
        elif coeff < 0: # Always add '-' if negative
            term_sign = "-"
        else: # First term and positive, or coeff is 0 (already handled)
            term_sign = ""

        abs_coeff = abs(coeff)

        # Coefficient part
        coeff_str = ""
        if current_degree == 0: # Constant term
            coeff_str = str(abs_coeff)
        elif abs_coeff == 1: # For 1x or -1x, don't show the '1'
            coeff_str = ""
        else:
            coeff_str = str(abs_coeff)
        
        # Variable part
        var_str = ""
        if current_degree == 1:
            var_str = var
        elif current_degree > 1:
            var_str = f"{var}^{{{current_degree}}}"
        
        terms.append(f"{term_sign}{coeff_str}{var_str}")
            
    return " ".join(terms) if terms else "0"

def format_solution_intervals(intervals, is_strict=False):
    """
    Formats a list of (start, end) intervals into a string representation.
    intervals: list of (float or Fraction, float or Fraction) tuples, can include -math.inf or math.inf
    is_strict: boolean, true for < or >, false for <= or >=
    Example: ((-inf, 1), (2, inf)) -> x < 1 or x > 2
    Example: ([1, 3]) -> 1 <= x <= 3
    """
    if not intervals:
        return r"無實數解"
    
    # Handle the 'all real numbers' case explicitly after sorting.
    if len(intervals) == 1 and intervals[0][0] == -math.inf and intervals[0][1] == math.inf:
        return r"全體實數"

    parts = []
    
    for interval in intervals:
        start, end = interval
        
        # Handle special cases like x = a
        if start == end:
            parts.append(f"$x = {format_number(start)}$")
            continue
        
        if start == -math.inf:
            part = f"$x {r'<' if is_strict else r'\le'} {format_number(end)}$"
        elif end == math.inf:
            part = f"$x {r'>' if is_strict else r'\ge'} {format_number(start)}$"
        else:
            part = f"${format_number(start)} {r'<' if is_strict else r'\le'} x {r'<' if is_strict else r'\le'} {format_number(end)}$"
        
        parts.append(part)
            
    return r" 或 ".join(parts)


def format_solution_sets(intervals, is_strict=False):
    """
    Formats a list of (start, end) intervals into a set notation string.
    intervals: list of (float or Fraction, float or Fraction) tuples, can include -math.inf or math.inf
    is_strict: boolean, true for < or >, false for <= or >=
    Example: ((-inf, 1), (2, inf)) -> $(-\infty, 1) \cup (2, \infty)$
    Example: ([1, 3]) -> $[1, 3]$
    """
    if not intervals:
        return r"無實數解"
    
    if len(intervals) == 1 and intervals[0][0] == -math.inf and intervals[0][1] == math.inf:
        return r"全體實數"

    parts = []
    for interval in intervals:
        start, end = interval
        
        if start == end: # Single point solution
            parts.append(f"\\{{{format_number(start)}\\}}")
            continue

        left_bracket = '(' if is_strict else '['
        right_bracket = ')' if is_strict else ']'
        
        start_str = r"-\infty" if start == -math.inf else format_number(start)
        end_str = r"\infty" if end == math.inf else format_number(end)
        
        parts.append(f"{left_bracket}{start_str}, {end_str}{right_bracket}")
            
    return r"$ " + r" \cup ".join(parts) + r" $"


def format_number(num):
    """Formats a number, converting floats to integers if appropriate, or fractions."""
    if isinstance(num, (float, int, Fraction)):
        if isinstance(num, Fraction) and num.denominator == 1:
            return str(num.numerator)
        elif isinstance(num, float) and num == int(num):
            return str(int(num))
        elif isinstance(num, float) and (num == -math.inf or num == math.inf):
            return str(num).replace('-inf', r'-\infty').replace('inf', r'\infty')
        
        # Represent as a fraction if it's not a simple integer float
        if isinstance(num, float):
            frac = Fraction(num).limit_denominator(1000) # Limit denominator to avoid huge fractions
        else: # It's already a Fraction or int that needs formatting
            frac = Fraction(num)

        if frac.denominator == 1:
            return str(frac.numerator)
        else:
            # Check if negative, put sign outside fraction
            sign = "-" if frac.numerator * frac.denominator < 0 else ""
            abs_num = abs(frac.numerator)
            abs_den = abs(frac.denominator)
            return r"{}\\frac{{{}}}{{{}}}".format(sign, abs_num, abs_den)
    return str(num) # For -math.inf, math.inf if not caught above.

def solve_linear_inequality(a, b, c, d, relation):
    """
    Solves ax + b R cx + d
    Returns: (intervals, is_strict)
    """
    # ax + b R cx + d
    # (a-c)x R d-b
    
    coeff_x = a - c
    const_term = d - b
    
    is_strict = (relation == r'<' or relation == r'>')
    
    if coeff_x == 0:
        # 0 R const_term
        if (relation == r'>' and 0 > const_term) or \
           (relation == r'>=' and 0 >= const_term) or \
           (relation == r'<' and 0 < const_term) or \
           (relation == r'<=' and 0 <= const_term):
            return ([( -math.inf, math.inf)], is_strict)
        return ([], is_strict) # No solution
    
    x_bound = Fraction(const_term, coeff_x)
    
    if coeff_x > 0:
        if relation == r'>' or relation == r'>=':
            return ([(x_bound, math.inf)], is_strict)
        else: # < or <=
            return ([(-math.inf, x_bound)], is_strict)
    else: # coeff_x < 0, reverse inequality
        if relation == r'>' or relation == r'>=': # Original was > or >=, now becomes < or <=
            return ([(-math.inf, x_bound)], is_strict)
        else: # Original was < or <=, now becomes > or >=
            return ([(x_bound, math.inf)], is_strict)

def solve_polynomial_inequality(factors, relation, explicit_leading_coeff_sign=1):
    """
    Solves a polynomial inequality given in factored form.
    Factors: list of (root, power, type='simple'/'even'/'always_pos'/'always_neg')
             e.g., [(-1, 1, 'simple'), (2, 2, 'even')] for (x+1)(x-2)^2
    relation: '>', '<', '>=', '<='
    explicit_leading_coeff_sign: 1 or -1, for cases where the factored form has a negative sign outside.
    
    Returns: (list of solution intervals, is_strict)
    """
    
    roots_info = {} # {root: total_power_at_this_root}
    
    # Calculate the effective leading coefficient sign
    effective_leading_coeff_sign = explicit_leading_coeff_sign
    
    for factor_root, factor_power, factor_type in factors:
        if factor_type == 'always_pos':
            continue
        elif factor_type == 'always_neg':
            effective_leading_coeff_sign *= -1
            continue
        
        # For actual polynomial factors
        roots_info[factor_root] = roots_info.get(factor_root, 0) + factor_power
    
    is_strict = (relation == r'<' or relation == r'>')
    
    # If effective_leading_coeff_sign is -1, flip the relation effectively
    current_relation = relation
    if effective_leading_coeff_sign == -1:
        if relation == r'>': current_relation = r'<'
        elif relation == r'<': current_relation = r'>'
        elif relation == r'>=': current_relation = r'<='
        elif relation == r'<=': current_relation = r'>='
    
    # Determine the behavior of the polynomial based on roots
    # Sort distinct roots
    all_distinct_roots = sorted(list(roots_info.keys()))
    
    # Case: No real roots (or all factors were always_pos/neg)
    if not all_distinct_roots:
        poly_value_sign = effective_leading_coeff_sign
        
        is_solution_always = False
        if (current_relation == r'>' and poly_value_sign > 0) or \
           (current_relation == r'>=' and poly_value_sign >= 0) or \
           (current_relation == r'<' and poly_value_sign < 0) or \
           (current_relation == r'<=' and poly_value_sign <= 0):
            is_solution_always = True
        
        if is_solution_always:
            return ([( -math.inf, math.inf)], is_strict)
        else:
            return ([], is_strict)

    # Use a sign line (正負區間示意圖) approach
    solution_intervals = []
    
    # Calculate initial sign (sign in the interval (-inf, first_root))
    # This sign is determined by the effective leading coefficient sign
    # and the parity of the total degree (which we don't calculate explicitly, just test a point)
    
    # Instead of total degree parity, we can simulate testing a point at -infinity
    # Start with the sign determined by effective_leading_coeff_sign.
    # For each root (x-r), if x is much less than r, (x-r) is negative.
    # So if there are N roots, and all factors are simple (x-r), then at -inf the sign is effective_leading_coeff_sign * (-1)^num_roots.
    # Let's use `current_sign` initialized to effective_leading_coeff_sign, and flip it for each odd-powered factor.
    
    current_sign_val = effective_leading_coeff_sign # Starting sign (at +infinity)

    # To get sign for (-infinity, first_root), we need to flip `current_sign_val`
    # for each root with an odd power.
    # A simpler way: work from right to left (from +infinity).
    # The sign for (last_root, +infinity) is `effective_leading_coeff_sign`.
    
    # Initialize intervals with their signs from right to left
    intervals_with_signs_reversed = [] # (start, end, sign)
    
    # Last interval (all_distinct_roots[-1], +inf)
    intervals_with_signs_reversed.append((all_distinct_roots[-1], math.inf, current_sign_val))

    for i in range(len(all_distinct_roots) - 1, 0, -1):
        root_val = all_distinct_roots[i]
        power = roots_info[root_val]
        
        if power % 2 != 0: # Odd power, sign flips
            current_sign_val *= -1
        
        intervals_with_signs_reversed.append((all_distinct_roots[i-1], root_val, current_sign_val))
    
    # First interval (-inf, all_distinct_roots[0])
    root_val = all_distinct_roots[0]
    power = roots_info[root_val]
    if power % 2 != 0: # Odd power, sign flips
        current_sign_val *= -1
    intervals_with_signs_reversed.append((-math.inf, all_distinct_roots[0], current_sign_val))

    intervals_with_signs = list(reversed(intervals_with_signs_reversed)) # Now in correct order from left to right
    
    # Collect solution intervals based on `current_relation` and `is_strict`
    for start, end, interval_sign in intervals_with_signs:
        is_solution_interval = False
        if (current_relation == r'>' and interval_sign > 0) or \
           (current_relation == r'<' and interval_sign < 0) or \
           (current_relation == r'>=' and interval_sign >= 0) or \
           (current_relation == r'<=' and interval_sign <= 0):
            is_solution_interval = True
            
        if is_solution_interval:
            solution_intervals.append((start, end))

    # Add roots if non-strict
    if not is_strict:
        for root in all_distinct_roots:
            is_covered = False
            for s, e in solution_intervals:
                # Compare roots to interval boundaries with tolerance for floats
                if (isinstance(s, Fraction) and isinstance(root, Fraction) and s < root and root < e) or \
                   (isinstance(s, float) and isinstance(root, float) and s < root + 1e-9 and root < e - 1e-9): # For general float intervals
                    is_covered = True
                    break
            
            if not is_covered:
                solution_intervals.append((root, root)) # Add as a single point

    # Merge overlapping/adjacent intervals
    solution_intervals = sorted(solution_intervals)
    
    merged_intervals = []
    if not solution_intervals:
        return ([], is_strict)

    current_start, current_end = solution_intervals[0]
    for i in range(1, len(solution_intervals)):
        next_start, next_end = solution_intervals[i]
        
        # Check for overlap or adjacency (with float tolerance for floats, exact for Fractions)
        if (isinstance(current_end, Fraction) and isinstance(next_start, Fraction) and next_start <= current_end) or \
           (isinstance(current_end, float) and isinstance(next_start, float) and next_start <= current_end + 1e-9):
            current_end = max(current_end, next_end)
        else:
            merged_intervals.append((current_start, current_end))
            current_start, current_end = next_start, next_end
            
    merged_intervals.append((current_start, current_end))
    
    # Clean up single points that are absorbed by larger intervals
    final_intervals = []
    for s_check, e_check in merged_intervals:
        if s_check == e_check: # It's a single point
            is_absorbed = False
            for s_other, e_other in merged_intervals:
                if s_other != e_other: # Only check against continuous intervals
                    # Check for float/Fraction compatibility
                    s_other_f = float(s_other) if isinstance(s_other, Fraction) else s_other
                    e_other_f = float(e_other) if isinstance(e_other, Fraction) else e_other
                    s_check_f = float(s_check) if isinstance(s_check, Fraction) else s_check

                    if s_other_f <= s_check_f + 1e-9 and s_check_f <= e_other_f - 1e-9:
                        is_absorbed = True
                        break
            if not is_absorbed:
                final_intervals.append((s_check, e_check))
        else:
            final_intervals.append((s_check, e_check))
    
    # Sort again to ensure order for presentation
    final_intervals = sorted(final_intervals)
    return (final_intervals, is_strict)


# --- Problem Generation Functions ---

def generate_linear_inequality(level):
    a = random.randint(-10, 10)
    b = random.randint(-15, 15)
    c = random.randint(-10, 10)
    d = random.randint(-15, 15)

    # Ensure coeff_x is not 0 for interesting problems
    while a == c:
        c = random.randint(-10, 10)
    
    relation_symbols = [r'\le', r'\ge', r'<', r'>']
    relation = random.choice(relation_symbols)
    
    # Construct problem string
    poly1_coeffs = [a, b]
    poly2_coeffs = [c, d]
    
    poly1_str = format_polynomial(poly1_coeffs)
    poly2_str = format_polynomial(poly2_coeffs)
    
    question_text = f"解一次不等式 ${poly1_str} {relation} {poly2_str}$。"
    
    # Solve
    intervals, is_strict = solve_linear_inequality(a, b, c, d, relation)
    
    correct_answer = format_solution_intervals(intervals, is_strict)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_quadratic_inequality(level):
    problem_type = random.choice(['D_pos', 'D_zero', 'D_neg'])
    
    # Ensure variety with leading coefficient sign
    a_sign_for_display = random.choice([1, -1]) if level >= 2 else 1

    relation_symbols = [r'\le', r'\ge', r'<', r'>']
    relation = random.choice(relation_symbols)
    
    coeffs_for_display = []
    factors_for_solve = []
    explicit_leading_coeff_sign = 1 # For solve_polynomial_inequality

    if problem_type == 'D_pos':
        # Generate two distinct integer roots
        r1 = random.randint(-5, 5)
        r2 = random.randint(-5, 5)
        while r1 == r2:
            r2 = random.randint(-5, 5)
        
        if r1 > r2: r1, r2 = r2, r1

        # Internal calculation for x^2 - (r1+r2)x + r1*r2
        # Then apply `a_sign_for_display` for the actual coefficients
        coeffs_for_display = [a_sign_for_display * 1, a_sign_for_display * (-r1 - r2), a_sign_for_display * (r1 * r2)]
        
        factors_for_solve = [(r1, 1, 'simple'), (r2, 1, 'simple')]
        explicit_leading_coeff_sign = a_sign_for_display
        
    elif problem_type == 'D_zero':
        # Generate one integer root (repeated)
        r = random.randint(-5, 5)
        
        # Internal calculation for (x-r)^2 = x^2 - 2rx + r^2
        coeffs_for_display = [a_sign_for_display * 1, a_sign_for_display * (-2 * r), a_sign_for_display * (r * r)]
        
        factors_for_solve = [(r, 2, 'even')]
        explicit_leading_coeff_sign = a_sign_for_display

    else: # D_neg
        # Generate coeffs such that D < 0
        a_base = random.randint(1, 3) # Always positive for D check
        b_base = random.randint(-5, 5)
        c_base = random.randint(1, 5)
        
        attempts = 0
        while (b_base*b_base - 4*a_base*c_base) >= 0 and attempts < 5:
            b_base = random.randint(-5, 5)
            c_base = random.randint(1, 5)
            attempts += 1
            
        if attempts == 5: # Fallback to a guaranteed D<0 poly (e.g., x^2+x+1)
            a_base, b_base, c_base = 1, 1, 1
            
        coeffs_for_display = [a_sign_for_display * a_base, a_sign_for_display * b_base, a_sign_for_display * c_base]

        # Determine if it's always positive or always negative
        if a_sign_for_display > 0:
            factors_for_solve = [(None, None, 'always_pos')]
        else:
            factors_for_solve = [(None, None, 'always_neg')]
        explicit_leading_coeff_sign = 1 # The 'always_neg' factor will be handled in solve_polynomial_inequality

    # Format question text
    poly_str = format_polynomial(coeffs_for_display)
    question_text = f"解二次不等式 ${poly_str} {relation} 0$。"

    # Solve the inequality
    intervals, is_strict_solution = solve_polynomial_inequality(factors_for_solve, relation, explicit_leading_coeff_sign)
    
    # Correct answer for display
    correct_answer = format_solution_intervals(intervals, is_strict_solution)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_higher_order_inequality(level):
    problem_choice = random.choice([
        'simple_factored',         # (x-a)(x-b)(x-c) R 0
        'even_power_factor',       # (x-a)^2(x-b) R 0
        'always_pos_factor',       # (x^2+x+1)(x-a) R 0
        'mix_and_factor'           # e.g., (x^2-1)(x-2) R 0, requires internal factoring
    ])
    
    relation_symbols = [r'\le', r'\ge', r'<', r'>']
    relation = random.choice(relation_symbols)
    
    factors_for_solve = [] # List of (root, power, type)
    poly_terms_display = [] # List of strings for the question
    explicit_leading_coeff_sign = 1 # Tracks if we have an overall negative sign (e.g. from -(x-r1)(x-r2))
    
    # Decide on leading coefficient for the whole polynomial (for display)
    overall_display_leading_coeff_is_negative = (random.random() < 0.3 and level >= 2)
    
    def generate_unique_roots(count, min_val=-4, max_val=4):
        roots = random.sample(range(min_val, max_val + 1), count)
        roots.sort()
        return roots

    if problem_choice == 'simple_factored':
        num_factors = random.randint(3, 4)
        roots = generate_unique_roots(num_factors)
        
        # If overall display leading coeff is negative, make one factor (r-x)
        if overall_display_leading_coeff_is_negative:
            first_root = roots.pop(0) # Take the smallest root
            poly_terms_display.append(f"({first_root} - x)") # Invert to create negative leading coeff
            factors_for_solve.append((first_root, 1, 'simple'))
            explicit_leading_coeff_sign = -1 # This factor has effectively flipped the sign
        
        for r in roots:
            poly_terms_display.append(f"(x - {r})")
            factors_for_solve.append((r, 1, 'simple'))

    elif problem_choice == 'even_power_factor':
        r1, r2 = generate_unique_roots(2)
        
        # Decide which root gets the even power
        if random.random() < 0.5: # (x-r1)^2 * (x-r2)
            poly_terms_display.append(f"(x - {r1})^{{2}}")
            poly_terms_display.append(f"(x - {r2})")
            factors_for_solve.append((r1, 2, 'even'))
            factors_for_solve.append((r2, 1, 'simple'))
        else: # (x-r1) * (x-r2)^2
            poly_terms_display.append(f"(x - {r1})")
            poly_terms_display.append(f"(x - {r2})^{{2}}")
            factors_for_solve.append((r1, 1, 'simple'))
            factors_for_solve.append((r2, 2, 'even'))
            
        # Apply overall_display_leading_coeff_is_negative
        if overall_display_leading_coeff_is_negative:
            # Find a simple linear factor (power 1) and change to (r-x)
            found_linear_factor_for_flip = False
            for root, power, f_type in list(factors_for_solve): # Iterate copy
                if f_type == 'simple' and power == 1:
                    for j, term_str in enumerate(poly_terms_display):
                        if f"(x - {root})" in term_str:
                            poly_terms_display[j] = f"({root} - x)"
                            explicit_leading_coeff_sign *= -1
                            found_linear_factor_for_flip = True
                            break
                    if found_linear_factor_for_flip: break
            if not found_linear_factor_for_flip: # Fallback: just prepend '-'
                poly_terms_display[0] = f"-{poly_terms_display[0]}"
                explicit_leading_coeff_sign *= -1

    elif problem_choice == 'always_pos_factor':
        # (x^2+x+1) (D<0, a>0) as an always positive factor
        ap_coeffs = [1, 1, 1] # x^2+x+1
        ap_str = format_polynomial(ap_coeffs)
        factors_for_solve.append((None, None, 'always_pos'))
        
        # Add another linear or quadratic factor
        if random.random() < 0.5: # Linear factor
            r = random.randint(-5, 5)
            poly_terms_display.append(f"({ap_str})")
            poly_terms_display.append(f"(x - {r})")
            factors_for_solve.append((r, 1, 'simple'))
        else: # Quadratic factor D>0
            r1, r2 = generate_unique_roots(2)
            poly_terms_display.append(f"({ap_str})")
            poly_terms_display.append(f"(x - {r1})(x - {r2})")
            factors_for_solve.append((r1, 1, 'simple'))
            factors_for_solve.append((r2, 1, 'simple'))
        
        # Apply overall_display_leading_coeff_is_negative
        if overall_display_leading_coeff_is_negative:
            found_linear_factor_for_flip = False
            for root, power, f_type in list(factors_for_solve):
                if f_type == 'simple' and power == 1:
                    for j, term_str in enumerate(poly_terms_display):
                        if f"(x - {root})" in term_str:
                            poly_terms_display[j] = f"({root} - x)"
                            explicit_leading_coeff_sign *= -1
                            found_linear_factor_for_flip = True
                            break
                    if found_linear_factor_for_flip: break
            if not found_linear_factor_for_flip: # Fallback: prepend '-'
                poly_terms_display[0] = f"-{poly_terms_display[0]}"
                explicit_leading_coeff_sign *= -1

    else: # mix_and_factor - e.g. (x^2-1)(x-2) > 0 -> (x-1)(x+1)(x-2) > 0
        r1, r2, r3 = generate_unique_roots(3)
        
        choice_form = random.choice(['quad_lin', 'sq_lin']) # (x^2-S x+P)(x-R), or (x-R1)^2 (x-R2)
        
        if choice_form == 'quad_lin':
            # Create a quadratic factor (x-r1)(x-r2) and a linear (x-r3)
            q_coeffs = [1, -(r1+r2), r1*r2]
            q_str = format_polynomial(q_coeffs)
            
            poly_terms_display.append(f"({q_str})")
            poly_terms_display.append(f"(x - {r3})")
            
            factors_for_solve.append((r1, 1, 'simple'))
            factors_for_solve.append((r2, 1, 'simple'))
            factors_for_solve.append((r3, 1, 'simple'))
            
        else: # sq_lin - (x-r1)^2 (x-r2)
            # Create (x-r1)^2 and (x-r2)
            q_coeffs = [1, -2*r1, r1*r1]
            q_str = format_polynomial(q_coeffs)
            
            poly_terms_display.append(f"({q_str})")
            poly_terms_display.append(f"(x - {r2})")
            
            factors_for_solve.append((r1, 2, 'even'))
            factors_for_solve.append((r2, 1, 'simple'))
            
        # Apply overall_display_leading_coeff_is_negative
        if overall_display_leading_coeff_is_negative:
            found_linear_factor_for_flip = False
            for root, power, f_type in list(factors_for_solve):
                if f_type == 'simple' and power == 1:
                    for j, term_str in enumerate(poly_terms_display):
                        if f"(x - {root})" in term_str:
                            poly_terms_display[j] = f"({root} - x)"
                            explicit_leading_coeff_sign *= -1
                            found_linear_factor_for_flip = True
                            break
                    if found_linear_factor_for_flip: break
            if not found_linear_factor_for_flip: # Fallback: prepend '-'
                poly_terms_display[0] = f"-{poly_terms_display[0]}"
                explicit_leading_coeff_sign *= -1

    question_text = f"解不等式 ${''.join(poly_terms_display)} {relation} 0$。"

    # Solve the inequality
    intervals, is_strict_solution = solve_polynomial_inequality(factors_for_solve, relation, explicit_leading_coeff_sign)
    correct_answer = format_solution_intervals(intervals, is_strict_solution)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_reverse_problem(level):
    # Given solution, find coefficients for ax^2 + bx + c R 0
    
    relation = random.choice([r'>', r'<']) # Only strict for easier reverse mapping
    
    # Generate roots
    r1 = random.randint(-4, 4)
    r2 = random.randint(-4, 4)
    while r1 == r2: r2 = random.randint(-4, 4)
    
    if r1 > r2: r1, r2 = r2, r1 # Ensure r1 < r2
    
    a_display_coeff = random.choice([1, 2, 3, -1, -2, -3])
    
    target_solution_intervals = []
    
    # Check what the *effective* relation for (x-r1)(x-r2) would be
    effective_rel_for_pos_poly = relation
    if a_display_coeff < 0:
        if relation == r'>': effective_rel_for_pos_poly = r'<'
        elif relation == r'<': effective_rel_for_pos_poly = r'>'

    if effective_rel_for_pos_poly == r'<': # This means the solution is (r1, r2)
        target_solution_intervals.append((r1, r2))
    else: # This means the solution is (-inf, r1) U (r2, inf)
        target_solution_intervals.append((-math.inf, r1))
        target_solution_intervals.append((r2, math.inf))

    solution_str = format_solution_intervals(target_solution_intervals, is_strict=True)

    # Reconstruct polynomial: a_display_coeff * (x-r1)(x-r2)
    # = a_display_coeff * (x^2 - (r1+r2)x + r1r2)
    
    coeff_a = a_display_coeff
    coeff_b = -a_display_coeff * (r1 + r2)
    coeff_c = a_display_coeff * (r1 * r2)
    
    # Create the question
    question_text = f"已知二次不等式 $ax^{{2}} + bx + c {relation} 0$ 的解為 ${solution_str}$，求實數 $a, b, c$ 的值。"
    
    correct_answer = f"$a={format_number(coeff_a)}$, $b={format_number(coeff_b)}$, $c={format_number(coeff_c)}$"
    
    return {
        "question_text": question_text,
        "answer": correct_answer, # User enters "a=X, b=Y, c=Z"
        "correct_answer": correct_answer
    }

def generate_application_problem(level):
    # Rectangle area problem: x(L-x) >= Area
    # Leads to x^2 - Lx + Area <= 0
    
    # To get nice integer roots, choose roots r1, r2 first.
    while True:
        r1_int = random.randint(5, 15)
        r2_int = random.randint(r1_int + 10, 30)
        base_val = r1_int + r2_int
        min_area_val = r1_int * r2_int
        
        # Ensure min_area_val is plausible given base_val
        # Max possible area is at x = base_val/2, so (base_val/2)^2
        if min_area_val <= (base_val / 2.0)**2:
            break

    question_text = f"有一張底邊長與底邊上的高都是 ${base_val}$ 的三角形皮革。皮雕師傅想要從這皮革切下一塊面積至少 ${min_area_val}$ 的內接矩形。已知內接矩形在底邊上的邊長為 $x$（ $0 < x < {base_val}$ ），求 $x$ 的範圍。"
    
    # Solve x(base_val - x) >= min_area_val
    # -x^2 + base_val*x - min_area_val >= 0
    # x^2 - base_val*x + min_area_val <= 0
    
    # The roots of x^2 - base_val*x + min_area_val = 0 are r1_int and r2_int by construction.
    factors_for_solve = [(r1_int, 1, 'simple'), (r2_int, 1, 'simple')]
    
    # The inequality is x^2 - base_val*x + min_area_val <= 0, so relation is '<='
    intervals, is_strict_solution = solve_polynomial_inequality(factors_for_solve, r'\le', explicit_leading_coeff_sign=1)
    
    # Apply the initial constraint 0 < x < base_val
    constrained_intervals = []
    
    for s, e in intervals:
        # Intersection logic for (s, e) and (0, base_val)
        actual_start = max(s, 0)
        actual_end = min(e, base_val)
        
        # We need to explicitly check if the interval is valid after constraints
        # Using a small epsilon for float comparison
        if (isinstance(actual_start, Fraction) and isinstance(actual_end, Fraction) and actual_start < actual_end) or \
           (isinstance(actual_start, float) and isinstance(actual_end, float) and actual_start < actual_end - 1e-9):
            constrained_intervals.append((actual_start, actual_end))
        elif (actual_start == actual_end) and not is_strict_solution: # For single point solution
            if actual_start > 0 and actual_start < base_val: # Only include if strictly within bounds
                constrained_intervals.append((actual_start, actual_end))
    
    # The problem implies final solution is inclusive [r1, r2], which matches format_solution_intervals for <=
    correct_answer = format_solution_intervals(constrained_intervals, is_strict=False)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def generate(level=1):
    problem_types = {
        1: ['linear', 'quadratic_d_pos', 'quadratic_d_zero', 'quadratic_d_neg'],
        2: ['linear', 'quadratic_d_pos', 'quadratic_d_zero', 'quadratic_d_neg', 
            'higher_order_factored_simple', 'higher_order_even_power_factor'],
        3: ['linear', 'quadratic_d_pos', 'quadratic_d_zero', 'quadratic_d_neg', 
            'higher_order_factored_simple', 'higher_order_even_power_factor', 
            'higher_order_always_pos_factor', 'higher_order_mix_and_factor',
            'reverse_quadratic', 'application_quadratic']
    }
    
    # Ensure level is within valid range
    level = max(1, min(level, 3))
    
    chosen_type = random.choice(problem_types[level])

    if chosen_type == 'linear':
        return generate_linear_inequality(level)
    elif chosen_type.startswith('quadratic'):
        return generate_quadratic_inequality(level)
    elif chosen_type.startswith('higher_order'):
        return generate_higher_order_inequality(level)
    elif chosen_type == 'reverse_quadratic':
        return generate_reverse_problem(level)
    elif chosen_type == 'application_quadratic':
        return generate_application_problem(level)
    
    # Fallback in case of an unhandled choice (should not happen)
    return generate_linear_inequality(level)


def check(user_answer, correct_answer):
    """
    Checks if the user's answer for polynomial inequalities is correct.
    This function parses both user_answer and correct_answer into a canonical
    list of (start, end, is_strict_start, is_strict_end) tuples for comparison.
    """
    
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    
    # --- Helper for parsing numbers (including fractions and inf) ---
    def parse_float_or_fraction(num_str):
        num_str = num_str.strip()
        if num_str.lower() == r'-\infty' or num_str.lower() == '-inf':
            return -math.inf
        if num_str.lower() == r'\infty' or num_str.lower() == 'inf':
            return math.inf
        
        # Handle LaTeX fraction format: \\frac{{numerator}}{{denominator}}
        match_frac = re.match(r"(-?)\\frac{{(\d+)}}{{(\d+)}}", num_str)
        if match_frac:
            sign = -1 if match_frac.group(1) == '-' else 1
            numerator = int(match_frac.group(2))
            denominator = int(match_frac.group(3))
            if denominator == 0: raise ValueError("Denominator cannot be zero")
            return sign * Fraction(numerator, denominator)
        
        # Handle simple float/int
        try:
            return Fraction(num_str) # Use Fraction to avoid float comparison issues
        except ValueError:
            pass # Try to convert to float if Fraction fails (e.g., for 'inf' which Fraction doesn't handle)
        
        try:
            return float(num_str)
        except ValueError:
            raise ValueError(f"Could not parse number: '{num_str}'")

    # --- Helper for parsing the full solution string into canonical intervals ---
    def parse_solution_to_canonical_intervals(sol_str):
        sol_str = sol_str.replace(' ', '')
        sol_str = sol_str.strip('$') # Remove math delimiters
        
        # Handle "全體實數" and "無實數解"
        if sol_str == r"全體實數": return [(-math.inf, math.inf, False, False)]
        if sol_str == r"無實數解": return []
        
        # Handle 'a=X, b=Y, c=Z' for reverse problems
        if "a=" in sol_str and "b=" in sol_str and "c=" in sol_str:
            # For comparison, we will treat these as a single special "interval"
            return [("REVERSE_PROBLEM_ANSWER", sol_str, False, False)] # Special tag
        
        # Split by union or "或"
        parts = re.split(r'\\cup|或', sol_str)
        
        parsed_intervals_with_strictness = []
        for part in parts:
            part = part.strip()
            if not part: continue
            
            # Case 1: Single point {a}
            num_pattern_with_frac = r"(-?)\\frac\{\d+\}{\d+}|\-?[\d\.]+|[-\\]?inf|[-\\]?\infty"
            match_point = re.match(fr"\\{{({num_pattern_with_frac})\\}}", part)
            if match_point:
                val = parse_float_or_fraction(match_point.group(1))
                parsed_intervals_with_strictness.append((val, val, False, False))
                continue

            # Case 2: Interval notation (a,b) or [a,b]
            match_interval = re.match(fr"([\[\(])({num_pattern_with_frac}),({num_pattern_with_frac})([\]\)])", part)
            if match_interval:
                start_bracket = match_interval.group(1)
                start_val = parse_float_or_fraction(match_interval.group(2))
                end_val = parse_float_or_fraction(match_interval.group(4))
                end_bracket = match_interval.group(6) # Group 6 is the last bracket
                
                is_strict_start = (start_bracket == '(')
                is_strict_end = (end_bracket == ')')
                parsed_intervals_with_strictness.append((start_val, end_val, is_strict_start, is_strict_end))
                continue
            
            # Case 3: Inequality notation x < a, x <= a, a < x, a <= x, a < x < b, etc.
            # Convert LaTeX operators to common ones for regex: \le -> <=, \ge -> >=, \> -> >, \< -> <
            part_norm_ops = part.replace(r'\le', '<=').replace(r'\ge', '>=').replace(r'\>', '>').replace(r'\<', '<')
            
            # x <= a, x < a
            match_x_op_a = re.match(fr"x(<=|<)({num_pattern_with_frac})", part_norm_ops)
            if match_x_op_a:
                op = match_x_op_a.group(1)
                val = parse_float_or_fraction(match_x_op_a.group(2))
                is_strict_op = (op == '<')
                parsed_intervals_with_strictness.append((-math.inf, val, True, is_strict_op))
                continue

            # x >= a, x > a
            match_x_op_a_rev = re.match(fr"x(>=|>)({num_pattern_with_frac})", part_norm_ops)
            if match_x_op_a_rev:
                op = match_x_op_a_rev.group(1)
                val = parse_float_or_fraction(match_x_op_a_rev.group(2))
                is_strict_op = (op == '>')
                parsed_intervals_with_strictness.append((val, math.inf, is_strict_op, True))
                continue
            
            # a <= x <= b, a < x < b etc.
            match_double_ineq = re.match(fr"({num_pattern_with_frac})(<=|<)x(<=|<)({num_pattern_with_frac})", part_norm_ops)
            if match_double_ineq:
                val1 = parse_float_or_fraction(match_double_ineq.group(1))
                op1 = match_double_ineq.group(2)
                op2 = match_double_ineq.group(3)
                val2 = parse_float_or_fraction(match_double_ineq.group(4))
                is_strict_op1 = (op1 == '<')
                is_strict_op2 = (op2 == '<')
                parsed_intervals_with_strictness.append((val1, val2, is_strict_op1, is_strict_op2))
                continue

            raise ValueError(f"Could not parse solution part: '{part}'")
            
        return sorted(parsed_intervals_with_strictness)

    # --- Main check logic ---
    try:
        parsed_user = parse_solution_to_canonical_intervals(user_answer)
        parsed_correct = parse_solution_to_canonical_intervals(correct_answer)
    except ValueError as e:
        return {"correct": False, "result": f"您的答案格式不正確，請檢查輸入。錯誤: {e}", "next_question": True}

    # Handle reverse problem answers: a=X, b=Y, c=Z
    if parsed_correct and parsed_correct[0][0] == "REVERSE_PROBLEM_ANSWER":
        is_correct = (user_answer.replace(' ', '').lower() == correct_answer.replace(' ', '').lower())
        result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
        return {"correct": is_correct, "result": result_text, "next_question": True}

    # Compare lists of intervals
    if len(parsed_user) != len(parsed_correct):
        is_correct = False
    else:
        is_correct = True
        for i in range(len(parsed_user)):
            us, ue, uss, ues = parsed_user[i]
            cs, ce, css, ces = parsed_correct[i]
            
            points_match = False
            # Compare Fraction objects exactly, floats with tolerance
            if isinstance(us, Fraction) and isinstance(cs, Fraction):
                if us == cs and ue == ce:
                    points_match = True
            elif isinstance(us, float) and isinstance(cs, float): # For -math.inf, math.inf
                 if us == cs and ue == ce:
                    points_match = True
            else: # Mixed types or other floats, convert to float for comparison with tolerance
                if abs(float(us) - float(cs)) < 1e-9 and abs(float(ue) - float(ce)) < 1e-9:
                    points_match = True

            if not points_match:
                is_correct = False
                break
            # Compare strictness (exact match required for brackets)
            if not (uss == css and ues == ces):
                is_correct = False
                break
                
    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}