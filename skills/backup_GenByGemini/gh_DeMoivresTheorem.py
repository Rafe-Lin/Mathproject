import random
import math
from fractions import Fraction
import uuid

# --- Helper functions and classes for number formatting ---

class ComplexNumberFormatter:
    """Helper to format complex numbers, including those with square roots, into LaTeX strings."""

    def __init__(self, real_part, imag_part):
        # real_part and imag_part are (coefficient, radical_num, denominator) tuples
        self.real_c, self.real_r, self.real_d = real_part
        self.imag_c, self.imag_r, self.imag_d = imag_part
        self._simplify_parts()

    def _simplify_radical_component(self, coeff, rad, denom):
        # Simplify radical part (e.g., sqrt(12) -> 2*sqrt(3))
        # Simplify fraction part (e.g., 2/4 -> 1/2)
        
        if denom == 0:
            raise ValueError("Denominator cannot be zero.")

        # If numerator (coeff) is 0, the whole term is 0.
        if coeff == 0:
            return (0, 1, 1) # (0, 1, 1) represents 0
        
        new_coeff = coeff
        new_rad = rad
        
        if new_rad < 1: 
            raise ValueError("Radical part must be a positive integer.")
        
        if new_rad > 1: # Only simplify if it's not sqrt(1)
            i = 2
            while i * i <= new_rad:
                if new_rad % (i * i) == 0:
                    new_coeff *= i
                    new_rad //= (i * i)
                else:
                    i += 1
        
        # Simplify fraction (new_coeff / denom)
        common_divisor = math.gcd(abs(new_coeff), abs(denom))
        new_coeff //= common_divisor
        new_denom = denom // common_divisor

        return new_coeff, new_rad, new_denom

    def _simplify_parts(self):
        self.real_c, self.real_r, self.real_d = self._simplify_radical_component(self.real_c, self.real_r, self.real_d)
        self.imag_c, self.imag_r, self.imag_d = self._simplify_radical_component(self.imag_c, self.imag_r, self.imag_d)
        
    def _format_single_radical_term(self, coeff, rad, denom, is_imaginary=False):
        if coeff == 0:
            return "0"
        
        s = "" # Sign
        if coeff < 0:
            s = "-"
            abs_coeff = abs(coeff)
        else:
            abs_coeff = coeff
        
        num_str = "" # Numerator string

        if rad == 1: # No square root
            if abs_coeff == denom: # e.g. 1/1, -1/1. Format as '1' (or '-1' for signed)
                num_str = "1"
            else: # e.g. 2/1, 1/2. Format as '2' or '1'
                num_str = str(abs_coeff)
        else: # Has square root (rad > 1)
            if abs_coeff == denom: # e.g. sqrt(3), -sqrt(3) (if denom=1)
                num_str = r"\\sqrt{{{:d}}}".format(rad)
            elif abs_coeff == 1: # e.g. sqrt(3)/2 or 1*sqrt(3) (if denom=1)
                num_str = r"\\sqrt{{{:d}}}".format(rad)
            else: # e.g. 2*sqrt(3) or 2*sqrt(3)/5
                num_str = r"{:d}\\sqrt{{{:d}}}".format(abs_coeff, rad)
        
        # Handle denominator
        if denom == 1:
            term_str = num_str
        else:
            term_str = r"\\frac{{{}}}{{{:d}}}".format(num_str, denom)
            
        if is_imaginary:
            if term_str == "1": # 1i -> i
                term_str = r"\\mathrm{i}"
            elif term_str == "0": # 0i -> 0
                term_str = "0"
            else:
                term_str += r"\\mathrm{i}"
        
        return s + term_str

    def to_latex_string(self):
        real_str = self._format_single_radical_term(self.real_c, self.real_r, self.real_d, is_imaginary=False)
        imag_str = self._format_single_radical_term(self.imag_c, self.imag_r, self.imag_d, is_imaginary=True)

        if imag_str == "0":
            return real_str if real_str != "0" else "0"
        
        if real_str == "0":
            return imag_str
        
        # Determine sign for imaginary part in combined string
        # If imag_str starts with '-', it implies the sign is part of imag_str already
        if imag_str.startswith('-'):
            return f"{real_str}{imag_str}"
        else:
            return f"{real_str}+{imag_str}"

# Pre-computed values for common angles (degrees)
# (angle, cos_val, sin_val)
# cos_val, sin_val are (coefficient, radical_num, denominator) tuples
SPECIAL_ANGLE_VALUES = {
    0:      ((1, 1, 1), (0, 1, 1)),
    30:     ((1, 3, 2), (1, 1, 2)),
    45:     ((1, 2, 2), (1, 2, 2)),
    60:     ((1, 1, 2), (1, 3, 2)),
    90:     ((0, 1, 1), (1, 1, 1)),
    120:    ((-1, 1, 2), (1, 3, 2)),
    135:    ((-1, 2, 2), (1, 2, 2)),
    150:    ((-1, 3, 2), (1, 1, 2)),
    180:    ((-1, 1, 1), (0, 1, 1)),
    210:    ((-1, 3, 2), (-1, 1, 2)),
    225:    ((-1, 2, 2), (-1, 2, 2)),
    240:    ((-1, 1, 2), (-1, 3, 2)),
    270:    ((0, 1, 1), (-1, 1, 1)),
    300:    ((1, 1, 2), (-1, 3, 2)),
    315:    ((1, 2, 2), (-1, 2, 2)),
    330:    ((1, 3, 2), (-1, 1, 2)),
}

# Helper to calculate r_base^n for r_base represented as (r_coeff, r_radical, r_denom)
def power_r_component(r_coeff, r_radical, r_denom, power):
    # This specifically handles r_base where r_radical is 1 (rational) or 2 (sqrt(2))
    
    if r_radical == 1: # r_base is a rational number (r_coeff/r_denom)
        num = r_coeff**power
        den = r_denom**power
        return (num, 1, den)
    elif r_radical == 2: # r_base is of the form r_coeff*sqrt(2)/r_denom
        # For base_complex_candidates, r_coeff is 1 and r_denom is 1 for sqrt(2)
        if power % 2 == 0: # (sqrt(2))^even = 2^(power/2)
            final_c = r_coeff**power * (2**(power // 2))
            final_r = 1
        else: # (sqrt(2))^odd = 2^((power-1)/2) * sqrt(2)
            final_c = r_coeff**power * (2**((power - 1) // 2))
            final_r = 2
        return (final_c, final_r, r_denom**power)
    else:
        # Should not happen with current generation strategy
        raise ValueError(f"Unsupported r_base radical part for power calculation: {r_radical}")

# --- Main generation function ---
def generate(level=1):
    """
    生成「棣美弗定理」相關題目。
    """
    question_type = random.choice(['rectangular_to_power', 'polar_to_power_simple'])

    if question_type == 'rectangular_to_power':
        return generate_rectangular_to_power_problem()
    elif question_type == 'polar_to_power_simple':
        return generate_polar_to_power_problem_simple()

def generate_rectangular_to_power_problem():
    """生成 (a+bi)^n 形式的題目。"""
    
    # Choose a base complex number (a + bi) such that r and theta are 'nice'
    # List of (a, b, r_base_coeff, r_base_radical, r_base_denom, theta_degrees)
    # r_base_radical=1 means r is rational. r_base_radical=2 means r is sqrt(2).
    # This selection ensures r is either 1 or sqrt(2), and theta is a multiple of 45 or 90 degrees.
    base_complex_candidates = [
        (1, 0, 1, 1, 1, 0),       # 1 -> r=1, theta=0
        (-1, 0, 1, 1, 1, 180),    # -1 -> r=1, theta=180
        (0, 1, 1, 1, 1, 90),      # i -> r=1, theta=90
        (0, -1, 1, 1, 1, 270),    # -i -> r=1, theta=270
        (1, 1, 1, 2, 1, 45),      # 1+i -> r=sqrt(2), theta=45
        (1, -1, 1, 2, 1, 315),    # 1-i -> r=sqrt(2), theta=315
        (-1, 1, 1, 2, 1, 135),    # -1+i -> r=sqrt(2), theta=135
        (-1, -1, 1, 2, 1, 225),   # -1-i -> r=sqrt(2), theta=225
    ]
    
    a_base, b_base, r_base_c, r_base_r, r_base_d, theta_base_deg = random.choice(base_complex_candidates)

    # Choose power n
    n = random.choice([-3, -2, -1, 2, 3, 4]) # Avoid 0 and 1, keep magnitude small

    # --- Calculations ---
    
    # Format the base complex number for display
    base_formatter = ComplexNumberFormatter(
        (a_base, 1, 1), # a_base is rational
        (b_base, 1, 1)  # b_base is rational
    )
    base_complex_str = base_formatter.to_latex_string()
    
    # Apply De Moivre's Theorem
    # 1. Calculate r^n
    r_final_c, r_final_r, r_final_d = power_r_component(r_base_c, r_base_r, r_base_d, n)
    
    # 2. Calculate n*theta_base_deg and normalize
    theta_final_deg = n * theta_base_deg
    theta_final_deg = (theta_final_deg % 360 + 360) % 360

    # 3. Get cos(theta_final_deg) and sin(theta_final_deg) values
    cos_val_tuple, sin_val_tuple = SPECIAL_ANGLE_VALUES[theta_final_deg]

    # 4. Calculate final A + Bi
    
    # Real part = r_final * cos_val_tuple
    final_real_c = r_final_c * cos_val_tuple[0]
    final_real_r = r_final_r * cos_val_tuple[1]
    final_real_d = r_final_d * cos_val_tuple[2]

    # Imaginary part = r_final * sin_val_tuple
    final_imag_c = r_final_c * sin_val_tuple[0]
    final_imag_r = r_final_r * sin_val_tuple[1]
    final_imag_d = r_final_d * cos_val_tuple[2] # Corrected: should be sin_val_tuple[2] for denom

    # Corrected denominator for imaginary part calculation
    final_imag_d = r_final_d * sin_val_tuple[2]
    
    final_formatter = ComplexNumberFormatter(
        (final_real_c, final_real_r, final_real_d),
        (final_imag_c, final_imag_r, final_imag_d)
    )
    correct_answer_str = final_formatter.to_latex_string()

    question_text = f"求 $({base_complex_str})^{{{n}}}$ 的值。"
    
    return {
        "question_text": question_text,
        "answer": correct_answer_str,
        "correct_answer": correct_answer_str
    }

def generate_polar_to_power_problem_simple():
    """生成 r(cosθ + i sinθ)^n 形式的題目，r為整數或sqrt(2)，θ為特殊角度。"""
    
    # Choose r_base (integer or sqrt(2))
    # (coeff, radical, denom) for 1 and sqrt(2)
    r_options = [(1, 1, 1), (1, 2, 1)] 
    r_base_c, r_base_r, r_base_d = random.choice(r_options)

    # Choose theta_base (multiples of 15 degrees, to cover 30, 45, 60, etc.)
    theta_options = list(SPECIAL_ANGLE_VALUES.keys())
    theta_base_deg = random.choice(theta_options)

    # Choose power n
    n = random.choice([-3, -2, -1, 2, 3, 4])

    # --- Calculations ---
    
    # Format the base polar form for display
    r_base_display_formatter = ComplexNumberFormatter(
        (r_base_c, r_base_r, r_base_d),
        (0,1,1) # 0 imaginary part for r_base_display_formatter, as r is real.
    )
    r_base_str = r_base_display_formatter.to_latex_string()
    
    # Base polar form string for question_text
    base_polar_str = f"{r_base_str}({r'{\\cos}'}{theta_base_deg}^\\circ + {r'{\\mathrm{i}\\sin}'}{theta_base_deg}^\\circ)"
    if r_base_str == "1": # If r is 1, don't show the outer parentheses
        base_polar_str = f"({r'{\\cos}'}{theta_base_deg}^\\circ + {r'{\\mathrm{i}\\sin}'}{theta_base_deg}^\\circ)"

    # Apply De Moivre's Theorem
    # 1. Calculate r^n
    r_final_c, r_final_r, r_final_d = power_r_component(r_base_c, r_base_r, r_base_d, n)
    
    # 2. Calculate n*theta_base_deg and normalize
    theta_final_deg = n * theta_base_deg
    theta_final_deg = (theta_final_deg % 360 + 360) % 360

    # 3. Get cos(theta_final_deg) and sin(theta_final_deg) values
    cos_val_tuple, sin_val_tuple = SPECIAL_ANGLE_VALUES[theta_final_deg]

    # 4. Calculate final A + Bi
    final_real_c = r_final_c * cos_val_tuple[0]
    final_real_r = r_final_r * cos_val_tuple[1]
    final_real_d = r_final_d * cos_val_tuple[2]

    final_imag_c = r_final_c * sin_val_tuple[0]
    final_imag_r = r_final_r * sin_val_tuple[1]
    final_imag_d = r_final_d * sin_val_tuple[2]
    
    final_formatter = ComplexNumberFormatter(
        (final_real_c, final_real_r, final_real_d),
        (final_imag_c, final_imag_r, final_imag_d)
    )
    correct_answer_str = final_formatter.to_latex_string()

    question_text = f"求 $({base_polar_str})^{{{n}}}$ 的值。"
    
    return {
        "question_text": question_text,
        "answer": correct_answer_str,
        "correct_answer": correct_answer_str
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    This check function performs a direct string comparison after stripping whitespace
    and converting to lowercase. Due to the complexity of symbolic math parsing (e.g., square roots),
    the `generate` function provides a highly canonical LaTeX string. User input is expected to
    match this canonical format as closely as possible.
    
    It also attempts a float comparison for purely numerical/fractional answers (no sqrt).
    """
    user_answer_normalized = user_answer.strip().replace(' ', '').replace(r'\\ ', '').lower()
    correct_answer_normalized = correct_answer.strip().replace(' ', '').replace(r'\\ ', '').lower()
    
    is_correct = (user_answer_normalized == correct_answer_normalized)
    
    # Try to handle common variations for integers/fractions/simple complex numbers without sqrt
    if not is_correct:
        try:
            # Attempt to convert to complex float if no sqrt is present in correct_answer
            if r'\\sqrt' not in correct_answer_normalized:
                
                # Replace LaTeX fraction with Python fraction-like division
                # Example: \\frac{1}{2} -> Fraction(1,2)
                parsed_correct = correct_answer_normalized.replace(r'\\frac{{', 'Fraction(').replace(r'}}{{', ',').replace(r'}}', ')')
                parsed_user = user_answer_normalized.replace(r'\\frac{{', 'Fraction(').replace(r'}}{{', ',').replace(r'}}', ')')
                
                # Convert LaTeX \\mathrm{i} or plain 'i' to 'j' for Python's complex()
                # Ensure 'j' replacement does not affect 'sin', 'cos' etc.
                parsed_correct = parsed_correct.replace(r'\\mathrm{i}', 'j').replace('i', 'j') 
                parsed_user = parsed_user.replace(r'\\mathrm{i}', 'j').replace('i', 'j')
                
                # Handle cases like "j" or "-j" after replacement
                if parsed_correct == "j": parsed_correct = "1j"
                if parsed_correct == "-j": parsed_correct = "-1j"
                if parsed_user == "j": parsed_user = "1j"
                if parsed_user == "-j": parsed_user = "-1j"

                # If it still contains special math functions, skip
                if any(func in parsed_correct for func in ['cos', 'sin', 'tan', 'sqrt']):
                    raise ValueError("Cannot parse as simple complex number due to math functions.")

                # Use Python's Fraction for exact arithmetic when evaluating
                correct_complex_eval = eval(parsed_correct, {"Fraction": Fraction})
                user_complex_eval = eval(parsed_user, {"Fraction": Fraction})
                
                # Convert Fraction results to complex for comparison (or just float for real/imag)
                correct_complex = complex(correct_complex_eval) if isinstance(correct_complex_eval, (int, float, Fraction, complex)) else correct_complex_eval
                user_complex = complex(user_complex_eval) if isinstance(user_complex_eval, (int, float, Fraction, complex)) else user_complex_eval

                # Perform comparison using a tolerance for floats
                if isinstance(correct_complex, complex) and isinstance(user_complex, complex):
                    if math.isclose(correct_complex.real, user_complex.real, rel_tol=1e-9, abs_tol=1e-12) and \
                       math.isclose(correct_complex.imag, user_complex.imag, rel_tol=1e-9, abs_tol=1e-12):
                        is_correct = True
                else: # Fallback for non-complex numbers, compare directly as floats
                    if math.isclose(float(correct_complex), float(user_complex), rel_tol=1e-9, abs_tol=1e-12):
                        is_correct = True

        except (SyntaxError, NameError, ValueError, TypeError):
            # If parsing as complex/fraction fails, fall back to string comparison failure
            pass

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}