import random
import math
from fractions import Fraction

# Helper function to represent square roots in LaTeX
def format_sqrt_latex(coefficient, radicand):
    if coefficient == 0:
        return "0"
    if radicand == 1:
        return str(coefficient)
    if coefficient == 1:
        return f"\\sqrt{{{radicand}}}"
    if coefficient == -1:
        return f"-\\sqrt{{{radicand}}}"
    return f"{coefficient}\\sqrt{{{radicand}}}"

# Helper function to simplify a sqrt(N) to c*sqrt(r) and return (c, r)
def simplify_sqrt_tuple(n):
    if n < 0:
        # For real exponents, negative radicands are not directly handled as real numbers
        # If the problem needs it, it would be complex numbers. Stick to positive.
        raise ValueError("Radicand must be non-negative for real numbers.")
    if n == 0:
        return (0, 1) # Convention: 0*sqrt(1)
    if n == 1:
        return (1, 1)

    c = 1
    r = n
    i = 2
    while i * i <= r:
        if r % (i * i) == 0:
            c *= i
            r //= (i * i)
        else:
            i += 1
    return (c, r)

# Helper function to get an exponent in display string and value (tuple for sqrt, Fraction for rational, int for integer)
def get_exponent_display_and_value(level, allow_negative=False):
    exp_types = ['sqrt', 'fraction', 'integer']
    
    # Adjust types based on level and preference
    if level == 1:
        # For level 1, prefer simpler cases. Avoid complex sqrt(N) that simplifies to c*sqrt(r)
        exp_type = random.choice(['sqrt', 'fraction']) # Integers are often too simple for main exponent
    else:
        exp_type = random.choice(exp_types)

    if exp_type == 'sqrt':
        chosen_c = random.choice([1, 2]) # Coefficient for sqrt, e.g., 2 in 2*sqrt(3)
        chosen_r = random.choice([2, 3, 5, 7]) # Radicand for sqrt
        
        # The actual exponent value will be (chosen_c, chosen_r)
        
        # For display, we sometimes show it as sqrt(N) where N = c^2 * r
        display_radicand_calc = chosen_c**2 * chosen_r
        
        neg_sign = 1
        if allow_negative and random.random() < 0.3:
            neg_sign = -1

        if level >= 2 and random.random() < 0.7 and chosen_c > 1: # For level 2+, sometimes show sqrt(N) form
             exp_display = f"\\sqrt{{{display_radicand_calc}}}"
             return exp_display, (neg_sign * chosen_c, chosen_r), 'sqrt'
        else: # Show as c*sqrt(r) or just sqrt(r) if c=1
            exp_display = format_sqrt_latex(neg_sign * chosen_c, chosen_r)
            return exp_display, (neg_sign * chosen_c, chosen_r), 'sqrt'

    elif exp_type == 'fraction':
        numerator = random.randint(1, 5)
        denominator = random.randint(2, 5)
        
        val_fraction = Fraction(numerator, denominator)
        if allow_negative and random.random() < 0.3:
            val_fraction *= -1
        
        # Simplify fraction display if it's an integer
        if val_fraction.denominator == 1:
            exp_display = str(val_fraction.numerator)
            return exp_display, val_fraction.numerator, 'integer' # Convert to integer type if it simplifies
        
        exp_display = f"\\frac{{{val_fraction.numerator}}}{{{val_fraction.denominator}}}"
        return exp_display, val_fraction, 'fraction'
    else: # integer
        val_integer = random.randint(1, 5)
        if allow_negative and random.random() < 0.3:
            val_integer *= -1
        exp_display = str(val_integer)
        return exp_display, val_integer, 'integer'

# Function to combine two exponents (coeff, radicand) based on operation
def combine_sqrt_exponents(exp1_val, exp2_val, operation):
    c1, r1 = exp1_val
    c2, r2 = exp2_val
    
    if operation == 'add':
        if r1 != r2:
            # Cannot combine directly unless r1 == r2 for addition/subtraction
            # This implies problem generation should ensure same radicand for these ops
            return None # Indicate non-combinable, or a more complex sum
        return (c1 + c2, r1)
    elif operation == 'subtract':
        if r1 != r2:
            return None
        return (c1 - c2, r1)
    elif operation == 'multiply':
        # (c1*sqrt(r1)) * (c2*sqrt(r2)) = c1*c2*sqrt(r1*r2)
        new_c_simplified, new_r_simplified = simplify_sqrt_tuple(r1 * r2)
        return (c1 * c2 * new_c_simplified, new_r_simplified)
    return None

# Helper to get numeric answer for base^exponent
def solve_numerical_power(base, exp_val, exp_type):
    if exp_type == 'integer':
        return base**exp_val
    elif exp_type == 'fraction':
        # base^(num/den) = (den-th root of base)^num
        if base == 0: return 0
        
        # Check if base is a perfect root
        try:
            root = round(base**(1/exp_val.denominator))
            if abs(root**exp_val.denominator - base) < 1e-9: # Check for perfect root
                return int(root**exp_val.numerator)
        except OverflowError: # For very large numbers
            pass

        # If not a perfect root or rounding issues, return float
        return float(base**(exp_val.numerator / exp_val.denominator))
    elif exp_type == 'sqrt':
        # For sqrt exponents, only 0 exponent yields an integer result (1)
        c, r = exp_val
        if c == 0:
            return 1 # base^0 = 1
        return None # Cannot easily get exact numerical value for a^sqrt(b)

# --- Problem Type 1: Simplification of expressions with real exponents ---

def generate_simplify_product_same_base(level):
    base = random.choice([2, 3, 5])
    
    exp1_display, exp1_val, exp1_type = get_exponent_display_and_value(level, allow_negative=False)
    
    final_exp_val = None
    final_exp_type = None
    correct_answer = None

    if exp1_type == 'sqrt':
        c1, r1 = exp1_val
        
        if random.random() < 0.6: # Target integer exponent (e.g., 0 or 1)
            # Make exp2 related to exp1 to simplify to a common radicand
            # For simplicity, make exp2 also have radicand r1.
            target_sum_coeff = random.choice([0, 1]) # Target a sum of 0*sqrt(r1) or 1*sqrt(r1)
            c2 = target_sum_coeff - c1 # Calculate needed coefficient for exp2_val
            
            exp2_val = (c2, r1)
            exp2_display = format_sqrt_latex(*exp2_val)
            
            final_exp_val = (target_sum_coeff, r1)
            if final_exp_val[0] == 0:
                final_exp_type = 'integer'
                correct_answer = 1
            elif final_exp_val[1] == 1: # c*sqrt(1) -> c
                final_exp_type = 'integer'
                correct_answer = base**final_exp_val[0]
            else:
                final_exp_type = 'sqrt'
                correct_answer = f"${base}^{{{format_sqrt_latex(*final_exp_val)}}}"
        else: # Target a sqrt exponent result which is not necessarily 0 or an integer
            exp2_display_tmp, exp2_val_tmp, exp2_type_tmp = get_exponent_display_and_value(level, allow_negative=True)
            if exp2_type_tmp != 'sqrt' or exp2_val_tmp[1] != r1: # Ensure we can combine or just retry
                return generate_simplify_product_same_base(level)

            exp2_display = exp2_display_tmp
            exp2_val = exp2_val_tmp
            
            combined_exp = combine_sqrt_exponents(exp1_val, exp2_val, 'add')
            if combined_exp is None: # Should not happen with current generation logic (r1=r2)
                 return generate_simplify_product_same_base(level)
            
            final_exp_val = combined_exp
            final_exp_type = 'sqrt'
            if final_exp_val[0] == 0:
                correct_answer = 1
            elif final_exp_val[1] == 1:
                correct_answer = base**final_exp_val[0]
            else:
                correct_answer = f"${base}^{{{format_sqrt_latex(*final_exp_val)}}}"

    elif exp1_type == 'fraction':
        f1 = exp1_val
        
        if random.random() < 0.6: # Target integer exponent (e.g., 0 or 1)
            target_sum = random.choice([0, 1])
            f2 = Fraction(target_sum) - f1
            exp2_val = f2
            exp2_display = f"\\frac{{{exp2_val.numerator}}}{{{exp2_val.denominator}}}" if exp2_val.denominator != 1 else str(exp2_val.numerator)
            
            final_exp_val = target_sum
            final_exp_type = 'integer'
            correct_answer = base**final_exp_val
        else:
            exp2_display_tmp, exp2_val_tmp, exp2_type_tmp = get_exponent_display_and_value(level, allow_negative=True)
            if exp2_type_tmp != 'fraction': # Ensure fraction type for exp2 for easy combination
                return generate_simplify_product_same_base(level)
            
            exp2_display = exp2_display_tmp
            exp2_val = exp2_val_tmp
            
            final_exp_val = f1 + exp2_val
            final_exp_type = 'fraction'
            
            if final_exp_val.denominator == 1:
                final_exp_type = 'integer'
                correct_answer = base**final_exp_val.numerator
            else:
                val = solve_numerical_power(base, final_exp_val, final_exp_type)
                if val is not None and isinstance(val, int):
                    correct_answer = val
                else:
                    correct_answer = f"${base}^{{\\frac{{{final_exp_val.numerator}}}{{{final_exp_val.denominator}}}}}"
    else: # exp1_type == 'integer'
        i1 = exp1_val
        i2 = random.randint(-i1-2, -i1+2)
        if i1 + i2 == 0 and base == 0: # Avoid 0^0 if this path could lead to it
            i2 = random.randint(1, 3) # ensure non-zero sum
        
        exp2_val = i2
        exp2_display = str(i2)
        
        final_exp_val = i1 + i2
        final_exp_type = 'integer'
        correct_answer = base**final_exp_val
        
    question_text = f"利用指數律，求下列各式的值：<br> ${base}^{{{exp1_display}}} \\times {base}^{{{exp2_display}}}$"
    
    return {
        "question_text": question_text,
        "answer": str(correct_answer),
        "correct_answer": str(correct_answer)
    }

def generate_simplify_power_of_power(level):
    base = random.choice([2, 3, 5])
    
    exp1_display, exp1_val, exp1_type = get_exponent_display_and_value(level, allow_negative=False)
    
    final_exp_val = None
    final_exp_type = None
    correct_answer = None

    if exp1_type == 'sqrt':
        c1, r1 = exp1_val
        
        if random.random() < 0.7: # Aim for integer final exponent
            # Need exp2_val to be (k*sqrt(r1)) such that (c1*sqrt(r1)) * (k*sqrt(r1)) becomes integer
            k_coeff = random.choice([1, 2, 3])
            
            # To get an integer exponent as final product, the combined sqrt should be sqrt(1)
            # So, exp2_val = (k_coeff, r1)
            # Its product with exp1_val = (c1, r1) is (c1*k_coeff*r1, 1). This is integer.
            
            display_radicand_for_exp2 = k_coeff**2 * r1
            exp2_display = f"\\sqrt{{{display_radicand_for_exp2}}}"
            exp2_val = (k_coeff, r1) # Actual value
            
            combined_c, combined_r = combine_sqrt_exponents(exp1_val, exp2_val, 'multiply')
            
            final_exp_val = combined_c
            final_exp_type = 'integer'
            correct_answer = base**final_exp_val
        else: # Aim for a non-integer, simplified sqrt exponent
            exp2_display_tmp, exp2_val_tmp, exp2_type_tmp = get_exponent_display_and_value(level, allow_negative=True)
            if exp2_type_tmp != 'sqrt': # Ensure exp2 is also sqrt for simpler logic for now
                return generate_simplify_power_of_power(level)
            
            exp2_display = exp2_display_tmp
            exp2_val = exp2_val_tmp
            
            combined_c, combined_r = combine_sqrt_exponents(exp1_val, exp2_val, 'multiply')
            
            if combined_r == 1:
                final_exp_val = combined_c
                final_exp_type = 'integer'
                correct_answer = base**final_exp_val
            else:
                final_exp_val = (combined_c, combined_r)
                final_exp_type = 'sqrt'
                correct_answer = f"${base}^{{{format_sqrt_latex(*final_exp_val)}}}"
                
    elif exp1_type == 'fraction':
        f1 = exp1_val
        
        exp2_display_tmp, exp2_val_tmp, exp2_type_tmp = get_exponent_display_and_value(level, allow_negative=True)
        if exp2_type_tmp == 'sqrt': # If exp2 is sqrt, retry to keep simpler for now
            return generate_simplify_power_of_power(level)
        
        exp2_display = exp2_display_tmp
        exp2_val = exp2_val_tmp
        
        final_exp_val = f1 * exp2_val
        final_exp_type = 'fraction' if isinstance(final_exp_val, Fraction) else 'integer'
        
        if final_exp_type == 'fraction' and final_exp_val.denominator == 1:
            final_exp_val = final_exp_val.numerator
            final_exp_type = 'integer'
            
        correct_answer = solve_numerical_power(base, final_exp_val, final_exp_type)
        if final_exp_type == 'fraction' and correct_answer is None:
             correct_answer = f"${base}^{{\\frac{{{final_exp_val.numerator}}}{{{final_exp_val.denominator}}}}}"

    else: # exp1_type == 'integer'
        i1 = exp1_val
        exp2_display_tmp, exp2_val_tmp, exp2_type_tmp = get_exponent_display_and_value(level, allow_negative=True)
        
        exp2_display = exp2_display_tmp
        exp2_val = exp2_val_tmp
        exp2_type = exp2_type_tmp
        
        if exp2_type == 'sqrt':
            final_exp_val = combine_sqrt_exponents((i1, 1), exp2_val, 'multiply')
            final_exp_type = 'sqrt'
            if final_exp_val[0] == 0:
                correct_answer = 1
            else:
                correct_answer = f"${base}^{{{format_sqrt_latex(*final_exp_val)}}}"
        elif exp2_type == 'fraction':
            final_exp_val = i1 * exp2_val
            final_exp_type = 'fraction'
            if final_exp_val.denominator == 1:
                final_exp_val = final_exp_val.numerator
                final_exp_type = 'integer'
            correct_answer = solve_numerical_power(base, final_exp_val, final_exp_type)
            if final_exp_type == 'fraction' and correct_answer is None:
                 correct_answer = f"${base}^{{\\frac{{{final_exp_val.numerator}}}{{{final_exp_val.denominator}}}}}"
        else: # integer
            final_exp_val = i1 * exp2_val
            final_exp_type = 'integer'
            correct_answer = base**final_exp_val
            
    question_text = f"利用指數律，求下列各式的值：<br> $({base}^{{{exp1_display}}})^{{{exp2_display}}}$"
    
    return {
        "question_text": question_text,
        "answer": str(correct_answer),
        "correct_answer": str(correct_answer)
    }

def generate_simplify_product_same_exponent(level):
    base1 = random.choice([2, 3])
    base2 = random.choice([5, 7]) # base2 needs to be different from base1
    if base1 * base2 > 70: # Keep numbers manageable
        base2 = random.choice([3, 5])
        if base2 == base1: base2 = 5 if base1 == 3 else 3
        
    exp_display, exp_val, exp_type = get_exponent_display_and_value(level, allow_negative=False)
    
    final_base = base1 * base2
    
    # Decide if it's (a^x * b^x) or (a^x * b^x)^y
    if random.random() < 0.5: # Simple (a^x * b^x)
        if exp_type == 'sqrt':
            c, r = exp_val
            if c == 0:
                correct_answer = 1
            elif r == 1:
                correct_answer = final_base**c
            else:
                correct_answer = f"${final_base}^{{{format_sqrt_latex(c, r)}}}"
        elif exp_type == 'fraction':
            val = solve_numerical_power(final_base, exp_val, exp_type)
            if val is not None and isinstance(val, int):
                correct_answer = val
            elif val is not None: # float
                 correct_answer = round(val, 5) # For fractional exponents leading to float
            else: # Still an expression
                correct_answer = f"${final_base}^{{\\frac{{{exp_val.numerator}}}{{{exp_val.denominator}}}}}"
        else: # integer
            correct_answer = final_base**exp_val
            
        question_text = f"利用指數律，求下列各式的值：<br> ${base1}^{{{exp_display}}} \\times {base2}^{{{exp_display}}}$"
    
    else: # (a^x * b^x)^y
        y_display_tmp, y_val_tmp, y_type_tmp = get_exponent_display_and_value(level, allow_negative=True)
        # Avoid combining sqrt with fraction for y for simplicity
        if (exp_type == 'sqrt' and y_type_tmp == 'fraction') or (exp_type == 'fraction' and y_type_tmp == 'sqrt'):
            return generate_simplify_product_same_exponent(level)
            
        y_display = y_display_tmp
        y_val = y_val_tmp
        y_type = y_type_tmp

        combined_exp_val = None
        combined_exp_type = None
        
        if exp_type == 'sqrt' and y_type == 'sqrt':
            combined_c, combined_r = combine_sqrt_exponents(exp_val, y_val, 'multiply')
            if combined_r == 1:
                combined_exp_val = combined_c
                combined_exp_type = 'integer'
                correct_answer = final_base**combined_exp_val
            else:
                combined_exp_val = (combined_c, combined_r)
                combined_exp_type = 'sqrt'
                correct_answer = f"${final_base}^{{{format_sqrt_latex(*combined_exp_val)}}}"
        elif exp_type == 'fraction' and (y_type == 'fraction' or y_type == 'integer'):
            combined_exp_val = exp_val * y_val
            combined_exp_type = 'fraction' if isinstance(combined_exp_val, Fraction) else 'integer'
            
            if combined_exp_type == 'fraction' and combined_exp_val.denominator == 1:
                combined_exp_val = combined_exp_val.numerator
                combined_exp_type = 'integer'
            
            correct_answer = solve_numerical_power(final_base, combined_exp_val, combined_exp_type)
            if combined_exp_type == 'fraction' and correct_answer is None:
                correct_answer = f"${final_base}^{{\\frac{{{combined_exp_val.numerator}}}{{{combined_exp_val.denominator}}}}}"

        elif exp_type == 'integer' and (y_type == 'fraction' or y_type == 'integer'):
            combined_exp_val = exp_val * y_val
            combined_exp_type = 'fraction' if isinstance(combined_exp_val, Fraction) else 'integer'
            
            if combined_exp_type == 'fraction' and combined_exp_val.denominator == 1:
                combined_exp_val = combined_exp_val.numerator
                combined_exp_type = 'integer'
            
            correct_answer = solve_numerical_power(final_base, combined_exp_val, combined_exp_type)
            if combined_exp_type == 'fraction' and correct_answer is None:
                correct_answer = f"${final_base}^{{\\frac{{{combined_exp_val.numerator}}}{{{combined_exp_val.denominator}}}}}"
        else: # Should not happen due to retry logic above
            return generate_simplify_product_same_exponent(level)

        question_text = f"利用指數律，求下列各式的值：<br> $({base1}^{{{exp_display}}} \\times {base2}^{{{exp_display}}})^{{{y_display}}}$"
        
    return {
        "question_text": question_text,
        "answer": str(correct_answer),
        "correct_answer": str(correct_answer)
    }

def generate_simplify_division_same_base(level):
    base = random.choice([2, 3, 5])
    
    exp1_display, exp1_val, exp1_type = get_exponent_display_and_value(level, allow_negative=False)
    
    final_exp_val = None
    final_exp_type = None
    correct_answer = None

    if exp1_type == 'sqrt':
        c1, r1 = exp1_val
        
        if random.random() < 0.6: # Target integer exponent (e.g., 1 or 0)
            target_diff_coeff = random.choice([0, 1])
            c2 = c1 - target_diff_coeff
            
            exp2_val = (c2, r1)
            exp2_display = format_sqrt_latex(*exp2_val)
            
            final_exp_val = (target_diff_coeff, r1)
            if final_exp_val[0] == 0:
                final_exp_type = 'integer'
                correct_answer = 1
            elif final_exp_val[1] == 1:
                final_exp_type = 'integer'
                correct_answer = base**final_exp_val[0]
            else:
                final_exp_type = 'sqrt'
                correct_answer = f"${base}^{{{format_sqrt_latex(*final_exp_val)}}}"
        else: # Target a non-integer, simplified sqrt exponent
            exp2_display_tmp, exp2_val_tmp, exp2_type_tmp = get_exponent_display_and_value(level, allow_negative=True)
            if exp2_type_tmp != 'sqrt' or exp2_val_tmp[1] != r1: # Ensure compatible types and radicands
                return generate_simplify_division_same_base(level)
            
            exp2_display = exp2_display_tmp
            exp2_val = exp2_val_tmp
            
            combined_exp = combine_sqrt_exponents(exp1_val, exp2_val, 'subtract')
            if combined_exp is None: # Should not happen with current generation logic (r1=r2)
                 return generate_simplify_division_same_base(level)
            
            final_exp_val = combined_exp
            final_exp_type = 'sqrt'
            if final_exp_val[0] == 0:
                correct_answer = 1
            elif final_exp_val[1] == 1:
                correct_answer = base**final_exp_val[0]
            else:
                correct_answer = f"${base}^{{{format_sqrt_latex(*final_exp_val)}}}"

    elif exp1_type == 'fraction':
        f1 = exp1_val
        
        if random.random() < 0.6: # Target integer exponent (e.g., 0 or 1)
            target_diff = random.choice([0, 1])
            f2 = f1 - Fraction(target_diff)
            exp2_val = f2
            exp2_display = f"\\frac{{{exp2_val.numerator}}}{{{exp2_val.denominator}}}" if exp2_val.denominator != 1 else str(exp2_val.numerator)
            
            final_exp_val = target_diff
            final_exp_type = 'integer'
            correct_answer = base**final_exp_val
        else:
            exp2_display_tmp, exp2_val_tmp, exp2_type_tmp = get_exponent_display_and_value(level, allow_negative=True)
            if exp2_type_tmp != 'fraction': # Ensure fraction type for exp2
                return generate_simplify_division_same_base(level)
            
            exp2_display = exp2_display_tmp
            exp2_val = exp2_val_tmp
            
            final_exp_val = f1 - exp2_val
            final_exp_type = 'fraction'
            
            if final_exp_val.denominator == 1:
                final_exp_type = 'integer'
                correct_answer = base**final_exp_val.numerator
            else:
                val = solve_numerical_power(base, final_exp_val, final_exp_type)
                if val is not None and isinstance(val, int):
                    correct_answer = val
                else:
                    correct_answer = f"${base}^{{\\frac{{{final_exp_val.numerator}}}{{{final_exp_val.denominator}}}}}"
    else: # exp1_type == 'integer'
        i1 = exp1_val
        i2 = random.randint(i1-2, i1+2) # Try to make sum small
        if i1 - i2 == 0: i2 = i1 + random.choice([-1, 1]) # Avoid 0 exponent if base is 0, or trivial case
        
        exp2_val = i2
        exp2_display = str(i2)
        
        final_exp_val = i1 - i2
        final_exp_type = 'integer'
        correct_answer = base**final_exp_val
        
    question_text = f"利用指數律，求下列各式的值：<br> ${base}^{{{exp1_display}}} / {base}^{{{exp2_display}}}$"
    
    return {
        "question_text": question_text,
        "answer": str(correct_answer),
        "correct_answer": str(correct_answer)
    }

def generate_eval_given_base_power(level):
    # e.g., 4^x = 9. Here 4 = 2^2, 9 = 3^2. So (2^2)^x = 3^2 => (2^x)^2 = 3^2 => 2^x = 3.
    # The core relation we derive is `root_base_orig^variable = target_value_for_root_base`
    
    base_for_question = random.choice([4, 8, 9, 25])
    
    # Determine the "root" base and its exponent for base_for_question
    root_base_orig = 0
    root_power_orig = 0
    if base_for_question == 4:
        root_base_orig = 2
        root_power_orig = 2
    elif base_for_question == 8:
        root_base_orig = 2
        root_power_orig = 3
    elif base_for_question == 9:
        root_base_orig = 3
        root_power_orig = 2
    elif base_for_question == 25:
        root_base_orig = 5
        root_power_orig = 2
    
    target_value_for_root_base = random.choice([k for k in [2, 3, 5, 7] if k != root_base_orig])
    
    given_val = target_value_for_root_base ** root_power_orig
    
    # --- Part (1) --- Find `base_for_question^(x + k)`
    # e.g., `4^(x+1)`
    k_add = random.randint(1, 2)
    question1_text = f"${base_for_question}^{{x+{k_add}}}$"
    answer1_val = given_val * (base_for_question ** k_add)
    
    # --- Part (2) --- Find `(some_other_base)^x`
    # e.g., `8^x`
    other_base_power = random.choice([p for p in [2, 3] if p != root_power_orig])
    some_other_base = root_base_orig ** other_base_power
    question2_text = f"${some_other_base}^{{x}}$"
    
    answer2_val = target_value_for_root_base ** other_base_power
    
    question_text = f"已知 ${base_for_question}^{{x}} = {given_val}$ ，求下列各式的值：<br>(1) {question1_text}<br>(2) {question2_text}"
    correct_answer = f"(1) {answer1_val} (2) {answer2_val}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def generate(level=1):
    problem_types = []
    if level == 1:
        problem_types = [
            'simplify_product_same_base',
            'simplify_power_of_power',
            'simplify_product_same_exponent',
            'simplify_division_same_base'
        ]
    elif level == 2:
        problem_types = [
            'simplify_product_same_base',
            'simplify_power_of_power',
            'simplify_product_same_exponent',
            'simplify_division_same_base',
            'eval_given_base_power'
        ]
    else: # level 3+
        problem_types = [
            'simplify_product_same_base',
            'simplify_power_of_power',
            'simplify_product_same_exponent',
            'simplify_division_same_base',
            'eval_given_base_power'
        ]
    
    problem_choice = random.choice(problem_types)
    
    if problem_choice == 'simplify_product_same_base':
        return generate_simplify_product_same_base(level)
    elif problem_choice == 'simplify_power_of_power':
        return generate_simplify_power_of_power(level)
    elif problem_choice == 'simplify_product_same_exponent':
        return generate_simplify_product_same_exponent(level)
    elif problem_choice == 'simplify_division_same_base':
        return generate_simplify_division_same_base(level)
    elif problem_choice == 'eval_given_base_power':
        return generate_eval_given_base_power(level)
    
    return {
        "question_text": "Error: Could not generate problem.",
        "answer": "",
        "correct_answer": ""
    }


def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    Handles both single numerical answers and multiple-part answers like "(1) 36 (2) 27".
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()

    is_correct = False
    feedback = ""

    # Check for multi-part answers first
    if "(1)" in correct_answer and "(2)" in correct_answer:
        import re
        correct_parts = {}
        match_q1 = re.search(r"\(1\)\s*(\S+)", correct_answer)
        match_q2 = re.search(r"\(2\)\s*(\S+)", correct_answer)
        
        if match_q1: correct_parts[1] = match_q1.group(1).strip()
        if match_q2: correct_parts[2] = match_q2.group(1).strip()

        user_parts = {}
        user_match_q1 = re.search(r"\(1\)\s*(\S+)", user_answer)
        user_match_q2 = re.search(r"\(2\)\s*(\S+)", user_answer)

        if user_match_q1: user_parts[1] = user_match_q1.group(1).strip()
        if user_match_q2: user_parts[2] = user_match_q2.group(1).strip()
        
        part1_correct = False
        part2_correct = False

        if 1 in correct_parts and 1 in user_parts:
            try:
                # Compare as floats with tolerance
                if abs(float(user_parts[1]) - float(correct_parts[1])) < 1e-9:
                    part1_correct = True
            except ValueError:
                # Fallback to string comparison if not purely numeric
                part1_correct = (user_parts[1] == correct_parts[1])
        
        if 2 in correct_parts and 2 in user_parts:
            try:
                if abs(float(user_parts[2]) - float(correct_parts[2])) < 1e-9:
                    part2_correct = True
            except ValueError:
                part2_correct = (user_parts[2] == correct_parts[2])

        if part1_correct and part2_correct:
            is_correct = True
            feedback = f"完全正確！答案是 {correct_answer}。"
        else:
            feedback = f"答案不完全正確。正確答案應為：{correct_answer}"

    else: # Single numerical or LaTeX answer
        # Try numeric comparison first (for simple integer/float answers)
        try:
            if abs(float(user_answer) - float(correct_answer)) < 1e-9:
                is_correct = True
        except ValueError:
            # Fallback to string comparison
            # Normalize strings by removing whitespace and dollar signs for lenient LaTeX comparison
            normalized_user = user_answer.replace(' ', '').replace('$', '').replace('\\', '')
            normalized_correct = correct_answer.replace(' ', '').replace('$', '').replace('\\', '')
            
            if normalized_user == normalized_correct:
                is_correct = True
            elif normalized_user.lower() == normalized_correct.lower():
                is_correct = True

        if is_correct:
            feedback = f"完全正確！答案是 ${correct_answer}$。"
        else:
            feedback = f"答案不正確。正確答案應為：${correct_answer}$"
            
    return {"correct": is_correct, "result": feedback, "next_question": True}