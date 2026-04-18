import random
import cmath # for complex numbers, especially cmath.sqrt
import math
from fractions import Fraction # Included as per template, though not explicitly used.

# --- Helper Classes and Functions ---

class Root:
    """
    Represents a root of a polynomial, storing its complex value and a formatted string representation.
    This allows preserving 'sqrt(k)' notation and distinguishing it from its float approximation.
    """
    def __init__(self, value, display_string=None):
        self.value = complex(value) # Always store as complex for calculations
        if display_string is None:
            self.display_string = self._format_default()
        else:
            self.display_string = display_string

    def _format_default(self):
        c = self.value
        # If purely real
        if c.imag == 0:
            if c.real == int(c.real):
                return str(int(c.real))
            else:
                # Fallback for real floats. For sqrt(k) roots, display_string should be provided during init.
                return str(c.real)
        
        # If complex
        real_part_str = ""
        if c.real != 0:
            if c.real == int(c.real):
                real_part_str = str(int(c.real))
            else:
                real_part_str = str(c.real) # Fallback for real float part
        
        imag_val = c.imag
        imag_part_str = ""
        if imag_val == 1:
            imag_part_str = "i"
        elif imag_val == -1:
            imag_part_str = "-i"
        elif imag_val == int(imag_val):
            imag_part_str = f"{int(imag_val)}i"
        else:
            imag_part_str = f"{imag_val}i" # Fallback for imag float part
        
        if real_part_str and imag_part_str:
            if imag_val > 0:
                return f"{real_part_str}+{imag_part_str}"
            else: # imag_val < 0, '-' is part of imag_part_str
                return f"{real_part_str}{imag_part_str}"
        elif real_part_str:
            return real_part_str
        elif imag_part_str: # If real_part is 0
            return imag_part_str
        return "0" # Should only happen if value is 0+0i

    def __eq__(self, other):
        if isinstance(other, Root):
            return abs(self.value.real - other.value.real) < 1e-9 and abs(self.value.imag - other.value.imag) < 1e-9
        try: # Allow comparison with complex/int/float directly
            other_complex = complex(other)
            return abs(self.value.real - other_complex.real) < 1e-9 and abs(self.value.imag - other_complex.imag) < 1e-9
        except (TypeError, ValueError):
            return False
    
    def __hash__(self):
        # Hash based on numerical value to ensure set comparisons work regardless of display string
        return hash((self.value.real, self.value.imag))
    
    def __str__(self):
        return self.display_string
    
    def __repr__(self):
        return f"Root(value={self.value}, display_string='{self.display_string}')"

def _multiply_polynomials(coeffs1, coeffs2):
    """
    Multiplies two polynomials represented by lists of coefficients (highest degree first).
    Returns a new list of coefficients.
    e.g., [1, -1] * [1, -2] represents (x-1)(x-2)
    """
    n = len(coeffs1) - 1
    m = len(coeffs2) - 1
    result_coeffs = [0] * (n + m + 1)

    for i in range(n + 1):
        for j in range(m + 1):
            result_coeffs[i + j] += coeffs1[i] * coeffs2[j]
    return result_coeffs

def _format_polynomial(coeffs, var='x', unknown_coeff_idx=None, unknown_symbol='a', constant_unknown_symbol=None):
    """
    Formats a list of coefficients into a LaTeX polynomial string.
    `coeffs`: List of coefficients from highest degree down.
    `unknown_coeff_idx`: Index of the coefficient to replace with `unknown_symbol`.
                        (e.g., 0 for highest degree, 1 for next, etc.).
    `constant_unknown_symbol`: Symbol for the constant term if it's the unknown,
                               used if `unknown_coeff_idx` points to the constant term.
    """
    terms = []
    degree = len(coeffs) - 1
    
    # Create a mutable copy of coefficients to allow modification
    coeffs_working = list(coeffs)

    # Remove leading zeros unless it's just the constant term 0
    while len(coeffs_working) > 1 and coeffs_working[0] == 0:
        coeffs_working.pop(0)
        degree -= 1
        # Adjust unknown_coeff_idx if coefficients were removed
        if unknown_coeff_idx is not None:
            unknown_coeff_idx -= 1
        
    for i, coeff_val in enumerate(coeffs_working):
        current_degree = degree - i
        
        # Determine symbol for this coefficient
        current_coeff_symbol = None
        if unknown_coeff_idx is not None and i == unknown_coeff_idx:
            current_coeff_symbol = unknown_symbol
            if current_degree == 0 and constant_unknown_symbol: # For constant term specifically
                 current_coeff_symbol = constant_unknown_symbol
        
        if coeff_val == 0 and current_coeff_symbol is None: # Skip zero terms unless it's an unknown
            continue
        
        term_str = ""
        
        # Add sign for terms after the first one
        if i > 0 and (coeff_val > 0 or (current_coeff_symbol and current_coeff_symbol != 'a' and current_coeff_symbol != 'b')):
            term_str += "+"
        
        # Coefficient part
        if current_coeff_symbol:
            term_str += current_coeff_symbol
        else: # Regular numeric coefficient
            abs_coeff = abs(coeff_val)
            if abs_coeff == 1:
                if coeff_val == -1:
                    term_str += "-"
                # For +1, nothing is prefixed before the variable
            else:
                if coeff_val == int(coeff_val):
                    term_str += str(int(coeff_val))
                else:
                    term_str += str(coeff_val)
        
        # Variable part
        if current_degree > 0:
            if current_coeff_symbol is None and abs(coeff_val) != 1: # Add dot for non-1 coefficients
                 term_str += r" \\cdot "
            elif current_coeff_symbol and current_coeff_symbol != 'a' and current_coeff_symbol != 'b': # If 'a' or 'b' are coefficients themselves, don't add dot
                 term_str += r" \\cdot "
            term_str += var
            if current_degree > 1:
                term_str += f"^{{{current_degree}}}"
        # For constant term (current_degree == 0), its value or symbol is already added.

        terms.append(term_str)
    
    # Handle potential leading "++" or "+-" after cleanup
    final_poly_str = "".join(terms).replace('+-', '-')
    if final_poly_str.startswith("+"): # Remove leading plus if it exists
        final_poly_str = final_poly_str[1:]
    
    # Clean up `+ \\cdot` or `- \\cdot`
    final_poly_str = final_poly_str.replace('+ \\cdot ', '+').replace('- \\cdot ', '-')

    if not final_poly_str:
        return "0"
    
    return final_poly_str

def _solve_quadratic(a, b, c):
    """Solves ax^2 + bx + c = 0 and returns a list of Root objects."""
    if a == 0: # Linear equation
        if b == 0: return []
        return [Root(-c / b)]
    
    discriminant = b**2 - 4*a*c
    if discriminant >= 0:
        root1 = (-b + math.sqrt(discriminant)) / (2*a)
        root2 = (-b - math.sqrt(discriminant)) / (2*a)
        
        roots = []
        for r_val in [root1, root2]:
            if r_val == int(r_val):
                roots.append(Root(r_val))
            else:
                # Try to represent as +/-sqrt(k)
                is_sqrt_k = False
                for k in [2, 3, 5, 6, 7]: # Check common small non-square integers
                    if abs(r_val - math.sqrt(k)) < 1e-9:
                        roots.append(Root(math.sqrt(k), display_string=f"sqrt({k})"))
                        is_sqrt_k = True
                        break
                    elif abs(r_val - (-math.sqrt(k))) < 1e-9:
                        roots.append(Root(-math.sqrt(k), display_string=f"-sqrt({k})"))
                        is_sqrt_k = True
                        break
                if not is_sqrt_k:
                    roots.append(Root(r_val)) # Fallback to float string
        return roots
    else:
        # Complex roots
        root1 = (-b + cmath.sqrt(discriminant)) / (2*a)
        root2 = (-b - cmath.sqrt(discriminant)) / (2*a)
        return [Root(root1), Root(root2)]

def _roots_to_string(roots):
    """Converts a list of Root objects to a comma-separated string, sorted for consistency."""
    return ",".join(str(r) for r in sorted(roots, key=lambda r: (r.value.real, r.value.imag)))

def _parse_roots_string(s):
    """Parses a comma-separated string of roots into a list of Root objects."""
    parts = [p.strip() for p in s.split(',')]
    parsed_roots = []
    for p in parts:
        p = p.replace(' ', '') # Remove spaces for easier parsing
        try:
            # Try parsing as complex number directly (e.g., "1+3i", "5", "2j")
            parsed_roots.append(Root(complex(p)))
        except ValueError:
            # Handle sqrt(k) forms
            if p.startswith('sqrt(') and p.endswith(')'):
                k = float(p[5:-1])
                parsed_roots.append(Root(math.sqrt(k), display_string=p))
            elif p.startswith('-sqrt(') and p.endswith(')'):
                k = float(p[6:-1])
                parsed_roots.append(Root(-math.sqrt(k), display_string=p))
            else:
                # Fallback, try parsing as float
                try:
                    parsed_roots.append(Root(float(p)))
                except ValueError:
                    raise ValueError(f"無法解析根的值: '{p}'")
    return parsed_roots

# --- Problem Generation Functions ---

def _generate_real_root_cubic_problem():
    """
    Generates a cubic polynomial problem where one real root is given,
    asking for an unknown coefficient or all roots.
    """
    # 1. Generate roots: one integer root, and two other real roots (integers or +/-sqrt(k))
    r1_val = random.choice([-3, -2, 1, 2, 3]) # Avoid 0 to simplify constant term cases
    r1 = Root(r1_val)

    remaining_roots_type = random.choice(['two_integers', 'sqrt_pair'])
    all_roots = [r1]

    if remaining_roots_type == 'two_integers':
        # Generate two distinct integers, also distinct from r1
        available_integers = [i for i in range(-4, 5) if i != r1_val]
        if len(available_integers) < 2: # Fallback if not enough distinct integers
            available_integers = [i for i in range(-5, 6) if i != r1_val]
        r2_val, r3_val = random.sample(available_integers, 2)
        all_roots.extend([Root(r2_val), Root(r3_val)])
    else: # sqrt_pair
        k_val = random.choice([2, 3, 5, 6, 7]) # Small non-square integers
        while r1_val**2 == k_val: # Ensure integer root is not +/-sqrt(k_val)
            r1_val = random.choice([-3, -2, 1, 2, 3])
            r1 = Root(r1_val)
        
        all_roots.extend([Root(math.sqrt(k_val), display_string=f"sqrt({k_val})"),
                          Root(-math.sqrt(k_val), display_string=f"-sqrt({k_val})")])
    
    # 2. Form the polynomial coefficients
    poly_coeffs = [1] # Start with [1] for x^0, then iterate factors
    for root in all_roots:
        poly_coeffs = _multiply_polynomials(poly_coeffs, [1, -root.value])
    
    poly_coeffs = [round(c) for c in poly_coeffs] # Ensure integer coefficients

    # 3. Choose which part to ask
    question_part = random.choice(['find_coeff', 'find_roots'])
    
    given_root = random.choice(all_roots) # Provide one of the generated roots

    if question_part == 'find_coeff':
        # Choose which coefficient to make unknown: C_2 (x^2), C_1 (x), or C_0 (constant)
        # For cubic: C3, C2, C1, C0 (indices 0, 1, 2, 3)
        # Avoid making C3 (leading coeff) unknown.
        unknown_idx_in_coeffs = random.choice([1, 2, 3]) # index 1 for C2, 2 for C1, 3 for C0
        unknown_symbol = 'a'
        
        correct_coeff_value = poly_coeffs[unknown_idx_in_coeffs]
        
        formatted_poly = _format_polynomial(poly_coeffs, 
                                            unknown_coeff_idx=unknown_idx_in_coeffs,
                                            unknown_symbol=unknown_symbol)
        
        question_text = (f"題目: 已知 ${given_root}$ 為實係數方程式 $${formatted_poly} = 0$$ 的一個根。<br>"
                         f"(1)求 $a$ 的值。")
        correct_answer = f"a={correct_coeff_value}"
        
    else: # find_roots
        formatted_poly = _format_polynomial(poly_coeffs)
        
        question_text = (f"題目: 已知 ${given_root}$ 為實係數方程式 $${formatted_poly} = 0$$ 的一個根。<br>"
                         f"(1)求所有的根。")
        correct_answer = f"roots={_roots_to_string(all_roots)}"
        
    return {
        "question_text": question_text,
        "answer": correct_answer, # Store the answer in a parsable string format
        "correct_answer": correct_answer
    }

def _generate_complex_root_quartic_problem():
    """
    Generates a quartic polynomial problem where one complex root is given,
    asking for unknown coefficients or all roots.
    """
    # 1. Generate roots: a complex conjugate pair and two real roots (integers or +/-sqrt(k))
    p = random.choice([-1, 0, 1]) # Real part for complex root
    q = random.choice([1, 2])     # Imaginary part, must be non-zero
    
    complex_root = Root(complex(p, q))
    conjugate_root = Root(complex(p, -q))

    # Factor for complex roots: (x - (p+qi))(x - (p-qi)) = x^2 - 2px + (p^2+q^2)
    complex_factor_coeffs = [1, -2*p, p**2 + q**2]

    remaining_roots_type = random.choice(['two_integers', 'sqrt_pair'])
    real_roots = []
    
    if remaining_roots_type == 'two_integers':
        # Generate two distinct integers, avoiding p (real part of complex root)
        r_vals = random.sample([i for i in range(-3, 4) if i != p], 2)
        real_roots = [Root(r) for r in r_vals]
    else: # sqrt_pair
        k_val = random.choice([2, 3, 5])
        # Ensure +/-sqrt(k) are not equal to p
        while p**2 == k_val: # Regenerate p if it clashes with sqrt(k_val)
            p = random.choice([-1, 0, 1])
        real_roots = [Root(math.sqrt(k_val), display_string=f"sqrt({k_val})"),
                      Root(-math.sqrt(k_val), display_string=f"-sqrt({k_val})")]
    
    all_roots = [complex_root, conjugate_root] + real_roots

    # 2. Form the polynomial coefficients
    poly_coeffs = list(complex_factor_coeffs)
    for root in real_roots:
        poly_coeffs = _multiply_polynomials(poly_coeffs, [1, -root.value])
    
    poly_coeffs = [round(c) for c in poly_coeffs] # Ensure integer coefficients

    # 3. Choose which part to ask
    question_part = random.choice(['find_coeffs', 'find_roots'])
    
    if question_part == 'find_coeffs':
        # Example form: $x^4 - 3x^3 + 6x^2 + ax + b = 0$
        # This implies 'a' is the coefficient of x, and 'b' is the constant term.
        # Quartic: C4, C3, C2, C1, C0 (indices 0, 1, 2, 3, 4)
        
        # Identify C1 (x term, index 3 for a 4th degree poly) and C0 (constant term, index 4)
        correct_a = poly_coeffs[3]
        correct_b = poly_coeffs[4]

        # Format polynomial with a, b as placeholder for the last two terms
        poly_prefix_coeffs = poly_coeffs[:-2] # Coefficients up to x^2
        poly_prefix_str = _format_polynomial(poly_prefix_coeffs)

        question_text = (f"題目: 已知 ${complex_root}$ 為實係數方程式 $${poly_prefix_str} + ax + b = 0$$ 的一個根。<br>"
                         f"(1)求 $a$ 與 $b$ 的值。")
        correct_answer = f"a={correct_a};b={correct_b}"

    else: # find_roots
        formatted_poly = _format_polynomial(poly_coeffs)
        question_text = (f"題目: 已知 ${complex_root}$ 為實係數方程式 $${formatted_poly} = 0$$ 的一個根。<br>"
                         f"(1)求所有的根。")
        correct_answer = f"roots={_roots_to_string(all_roots)}"
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def _generate_conjugate_id_problem():
    """
    Generates a cubic polynomial problem where two partially specified complex roots
    (A+i, 1+Bi) are given, testing understanding of conjugate roots,
    then asking for A, B or polynomial coefficients or all roots.
    """
    # From example, roots are A+i and 1+Bi. For them to be conjugates and coefficients real:
    # A+i must be the conjugate of 1+Bi. So A+i = 1-Bi  => A=1, B=-1
    # This implies the actual complex roots are 1+i and 1-i.
    known_complex_root = Root(complex(1, 1), display_string="1+i")
    known_conjugate_root = Root(complex(1, -1), display_string="1-i")
    
    # Generate one real root, distinct from 1 (the real part of the complex roots)
    r3_val = random.choice([-4, -3, -2, 3, 4]) 
    r3 = Root(r3_val)

    all_roots = [known_complex_root, known_conjugate_root, r3]

    # Form the polynomial (x^2 - 2x + 2)(x-r3)
    complex_factor_coeffs = [1, -2, 2] # (x-1)^2 + 1^2 = x^2 - 2x + 2
    
    poly_coeffs = _multiply_polynomials(complex_factor_coeffs, [1, -r3.value])
    poly_coeffs = [round(c) for c in poly_coeffs] # Ensure integer coefficients

    # Determine which part to ask
    question_part = random.choice(['find_root_params', 'find_coeffs', 'find_roots'])
    
    # For a cubic: x^3 + C2 x^2 + C1 x + C0 = 0 (indices 0, 1, 2, 3)
    # The example uses `x^3 + ax^2 + cx + d = 0` so (a,c,d) correspond to (C2, C1, C0)
    C2 = poly_coeffs[1]
    C1 = poly_coeffs[2]
    C0 = poly_coeffs[3]

    if question_part == 'find_root_params':
        question_text = (f"題目: 已知 $A+i$ 與 $1+Bi$ (其中 $A,B$ 為實數，且 $B \\ne 0$) "
                         f"為實係數三次方程式 $x^3 + ax^2 + cx + d = 0$ 的兩個根。<br>"
                         f"(1)求 $A$ 與 $B$ 的值。")
        correct_answer = f"A=1;B=-1"
    elif question_part == 'find_coeffs':
         question_text = (f"題目: 已知 $A+i$ 與 $1+Bi$ (其中 $A,B$ 為實數，且 $B \\ne 0$) "
                         f"為實係數三次方程式 $x^3 + ax^2 + cx + d = 0$ 的兩個根。<br>"
                         f"(1)求 $a, c, d$ 的值。")
         correct_answer = f"a={C2};c={C1};d={C0}"
    else: # find_roots
        formatted_poly = _format_polynomial(poly_coeffs)
        question_text = (f"題目: 已知 $A+i$ 與 $1+Bi$ (其中 $A,B$ 為實數，且 $B \\ne 0$) "
                         f"為實係數三次方程式 $${formatted_poly} = 0$$ 的兩個根。<br>"
                         f"(1)求所有的根。")
        correct_answer = f"roots={_roots_to_string(all_roots)}"
        
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def _generate_conceptual_problem():
    """
    Generates a multiple-choice conceptual problem based on root properties.
    """
    statements = []
    correct_flags = [] # True if statement is correct, False otherwise
    
    # 1. Odd degree real coefficient polynomial must have at least one real root.
    statements.append("實係數奇數次方程式至少有一個實根。")
    correct_flags.append(True)

    # 2. Even degree real coefficient polynomial must have at least one real root. (False)
    statements.append("實係數偶數次方程式不一定有實根。") # Rephrased to be true if they select "doesn't have to"
    correct_flags.append(True) # This statement itself is true

    # 3. Complex roots come in conjugate pairs for real coefficients. (True)
    p = random.randint(1, 3)
    q = random.randint(1, 3)
    statements.append(f"若 ${p}+{q}i$ 是實係數方程式的根，則 ${p}-{q}i$ 也是其根。")
    correct_flags.append(True)

    # 4. A polynomial of degree n has n *distinct* roots. (False)
    n_val = random.randint(3, 5)
    statements.append(f"一個 $n$ 次方程式恰有 $n$ 個相異複數根。") 
    correct_flags.append(False) # False: could be repeated roots

    # 5. If f(a+bi)=0, then f(other complex number) != 0 (True, if other complex number is not a root)
    # The example uses f(2+2i) for a cubic with 1+i, 1-i, real_root. 2+2i is not a root.
    statements.append(f"若 $f(x)=0$ 為實係數三次方程式，且 $f(1+i)=0$，則 $f(2+2i) \\ne 0$。")
    correct_flags.append(True)

    # Shuffle statements and assign options
    statement_data = list(zip(statements, correct_flags))
    random.shuffle(statement_data)
    
    question_options = []
    final_correct_options_nums = []

    for i, (statement, is_correct) in enumerate(statement_data):
        option_num = i + 1
        question_options.append(f"({option_num}){statement}")
        if is_correct:
            final_correct_options_nums.append(option_num)
    
    question_text = "題目: 設 $f(x) = 0$ 為實係數三次方程式，選出所有正確的選項。<br>" + "<br>".join(question_options)
    
    correct_answer = f"options={','.join(map(str, sorted(final_correct_options_nums)))}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def generate(level=1):
    """
    生成「gh_RootsOfNthDegreeEquations」相關題目。
    """
    problem_type = random.choice([
        'real_root_cubic',
        'complex_root_quartic',
        'conjugate_id',
        'conceptual'
    ])
    
    if problem_type == 'real_root_cubic':
        return _generate_real_root_cubic_problem()
    elif problem_type == 'complex_root_quartic':
        return _generate_complex_root_quartic_problem()
    elif problem_type == 'conjugate_id':
        return _generate_conjugate_id_problem()
    else: # conceptual
        return _generate_conceptual_problem()

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    Handles multiple answer types: single value, a=X;b=Y, roots=R1,R2,..., options=O1,O2,...
    """
    def _parse_answer_parts_for_check(ans_string):
        parts = {}
        items = [item.strip() for item in ans_string.split(';') if item.strip()]
        if not items: # Empty string, no answer
            return None
        
        for item in items:
            if '=' in item:
                key, val = item.split('=', 1)
                key = key.strip()
                val = val.strip()
                if key == 'roots':
                    try:
                        parts[key] = set(_parse_roots_string(val))
                    except ValueError:
                        return None # Indicate parsing error
                elif key == 'options': # For multiple choice
                    try:
                        parts[key] = set(map(int, val.split(',')))
                    except ValueError:
                        return None
                else: # For single value like 'a', 'b', 'A', 'B', 'c', 'd'
                    try:
                        parts[key] = float(val)
                    except ValueError:
                        return None
            else:
                # If the string contains only roots or a single value without a key=
                # This needs careful handling to distinguish. Assuming roots is more likely.
                if 'roots' not in parts and 'options' not in parts and len(items) == 1:
                    try:
                        # Try parsing as roots first
                        parts['roots'] = set(_parse_roots_string(item))
                    except ValueError:
                        try:
                            # If not roots, try as a single numeric value (e.g., for 'a' only)
                            parts['value'] = float(item)
                        except ValueError:
                            return None
                else:
                    return None # Malformed if no key and multiple items, or key already present
        return parts

    parsed_user = _parse_answer_parts_for_check(user_answer)
    parsed_correct = _parse_answer_parts_for_check(correct_answer)

    if parsed_user is None or parsed_correct is None:
        return {"correct": False, "result": "無法解析您的答案格式。請確認格式正確。", "next_question": False}

    is_correct = True
    feedback_parts = []

    for key, correct_val in parsed_correct.items():
        if key not in parsed_user:
            is_correct = False
            feedback_parts.append(f"缺少 {key} 的答案。")
            continue

        user_val = parsed_user[key]

        if key == 'roots':
            if user_val != correct_val: # Set comparison of Root objects
                is_correct = False
                feedback_parts.append(f"根的答案不正確。")
        elif key == 'options':
            if user_val != correct_val:
                is_correct = False
                feedback_parts.append(f"選項選擇不正確。")
        else: # Numeric values like 'a', 'b', 'A', 'B', 'c', 'd', 'value'
            if abs(user_val - correct_val) > 1e-6: # Float comparison tolerance
                is_correct = False
                feedback_parts.append(f"$\{key}$ 的值不正確。您的答案為 ${user_val}$，正確答案為 ${correct_val}$。")

    if not is_correct:
        result_text = "答案不正確。" + " ".join(feedback_parts)
        if not feedback_parts: # Generic message if no specific part failed (e.g., overall structure mismatch)
             result_text += "請檢查您的輸入。"
    else:
        result_text = f"完全正確！正確答案為：${correct_answer}$。"
    
    return {"correct": is_correct, "result": result_text, "next_question": True}