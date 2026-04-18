import random
from fractions import Fraction
import math

# --- Helper functions and class for internal use ---

def get_prime_factorization(n):
    """Computes the prime factorization of a positive integer."""
    factors = {}
    d = 2
    temp = n
    while d * d <= temp:
        while temp % d == 0:
            factors[d] = factors.get(d, 0) + 1
            temp //= d
        d += 1
    if temp > 1:
        factors[temp] = factors.get(temp, 0) + 1
    return factors

def simplify_radicand(n):
    """
    Simplifies a square root.
    Returns (coefficient, new_radicand) such that sqrt(n) = coefficient * sqrt(new_radicand).
    """
    if not isinstance(n, int) or n < 0:
        raise ValueError("Input must be a non-negative integer.")
    if n == 0:
        return 0, 1
    if n == 1:
        return 1, 1
    
    factors = get_prime_factorization(n)
    coeff = 1
    radicand = 1
    for p, exp in factors.items():
        coeff *= p**(exp // 2)
        radicand *= p**(exp % 2)
    return coeff, radicand

class Radical:
    """A class to represent and operate on radical expressions of the form a*sqrt(b)."""
    def __init__(self, coeff=1, radicand=1):
        if not isinstance(radicand, int) or radicand < 0:
            raise ValueError("Radicand must be a non-negative integer.")
            
        self.coeff = Fraction(coeff)
        
        if radicand > 1:
            c, r = simplify_radicand(radicand)
            self.coeff *= c
            self.radicand = r
        else:
            self.radicand = radicand
            
        if self.radicand == 1:
            self.radicand = 1

    def __mul__(self, other):
        if not isinstance(other, Radical):
            other = Radical(coeff=other)
        
        new_coeff = self.coeff * other.coeff
        new_radicand = self.radicand * other.radicand
        return Radical(new_coeff, new_radicand)

    def __truediv__(self, other):
        if not isinstance(other, Radical):
            other = Radical(coeff=other)
        
        if other.coeff == 0 or other.radicand == 0:
            raise ZeroDivisionError("Division by zero in radical expression.")

        # (a sqrt b) / (c sqrt d) = (a sqrt(bd)) / (c*d)
        new_coeff = self.coeff / (other.coeff * other.radicand)
        new_radicand = self.radicand * other.radicand
        return Radical(new_coeff, new_radicand)

    def to_latex(self):
        """Converts the radical expression to a LaTeX string."""
        if self.radicand == 0:
            return "0"

        coeff_frac = self.coeff
        num, den = coeff_frac.numerator, coeff_frac.denominator

        sign = ""
        if num < 0:
            sign = "-"
            num = abs(num)
        
        if self.radicand == 1:
            if den == 1:
                return f"{sign}{num}"
            else:
                return f"{sign}\\frac{{{num}}}{{{den}}}"
        
        sqrt_part = f"\\sqrt{{{self.radicand}}}"

        if num == 1 and den == 1:
            return f"{sign}{sqrt_part}"
        elif den == 1:
            return f"{sign}{num}{sqrt_part}"
        else:
            if num == 1:
                return f"{sign}\\frac{{{sqrt_part}}}{{{den}}}"
            else:
                return f"{sign}\\frac{{{num}{sqrt_part}}}{{{den}}}"

# --- Problem Generation Functions ---

def generate_multiplication_problem():
    """Generates a radical multiplication problem."""
    problem_subtype = random.choice(['rational_x_radical', 'radical_x_radical'])
    
    if problem_subtype == 'rational_x_radical':
        radicand = random.choice([2, 3, 5, 6, 7, 10, 11])
        a = random.randint(2, 5)
        
        if random.random() < 0.4:
            num = random.randint(1, 9)
            den = random.randint(2, 9)
            if den == num: den += 1
            common = math.gcd(num, den)
            rational = Fraction(num // common, den // common)
            term1_latex = f"\\frac{{{rational.numerator}}}{{{rational.denominator}}}"
        else:
            rational = random.randint(-9, 9)
            while rational in [0, 1, -1]:
                rational = random.randint(-9, 9)
            term1_latex = f"({rational})" if rational < 0 else str(rational)

        r_radical = Radical(a, radicand)
        r_rational = Radical(rational)

        if random.random() < 0.5:
            r1, r2 = r_rational, r_radical
            t1_latex, t2_latex = term1_latex, r_radical.to_latex()
        else:
            r1, r2 = r_radical, r_rational
            t1_latex, t2_latex = r_radical.to_latex(), term1_latex
        
        question_text = f"計算 ${t1_latex} \\times {t2_latex}$ 的值。"
        answer_radical = r1 * r2
        correct_answer = answer_radical.to_latex()
        
    else: # radical_x_radical
        radicand_primes = [2, 3, 5, 6, 7, 10, 11]
        
        b = d = random.choice(radicand_primes) if random.random() < 0.3 else (random.choice(radicand_primes), random.choice(radicand_primes))
        if isinstance(b, tuple): b,d = b

        a = random.randint(-5, 5) or (random.choice([-1,1]) * Fraction(random.randint(1,5), random.randint(2,5))) if random.random() < 0.3 else random.randint(-5, 5)
        while a == 0: a = random.randint(-5, 5)
        c = random.randint(-5, 5) or (random.choice([-1,1]) * Fraction(random.randint(1,5), random.randint(2,5))) if random.random() < 0.3 else random.randint(-5, 5)
        while c == 0: c = random.randint(-5, 5)
            
        r1, r2 = Radical(a, b), Radical(c, d)

        term1_latex = r1.to_latex()
        if r1.coeff < 0: term1_latex = f"({term1_latex})"
            
        term2_latex = r2.to_latex()
        if r2.coeff < 0: term2_latex = f"({term2_latex})"
        
        question_text = f"計算 ${term1_latex} \\times {term2_latex}$ 的值。"
        answer_radical = r1 * r2
        correct_answer = answer_radical.to_latex()

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": correct_answer}

def generate_division_problem():
    """Generates a radical division problem."""
    c = random.randint(2, 9)
    d = random.choice([2, 3, 5, 7])
    divisor = Radical(c, d)
    
    k = random.randint(2, 5)
    b = d * k
    
    a_over_c = Fraction(random.randint(1, 5), random.randint(1, 3))
    a_candidate = c * a_over_c
    a = a_candidate.numerator if a_candidate.denominator == 1 else random.randint(1, 10) * c
        
    if random.random() < 0.3: a *= -1
    
    dividend = Radical(a, b)
    
    term1_latex = dividend.to_latex()
    if dividend.coeff < 0: term1_latex = f"({term1_latex})"
    
    term2_latex = divisor.to_latex()
    
    question_text = f"計算 ${term1_latex} \\div {term2_latex}$ 的值。"
    answer_radical = dividend / divisor
    correct_answer = answer_radical.to_latex()
    
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": correct_answer}

def generate_simplify_problem():
    """Generates a problem asking to simplify a single radical."""
    square_part_coeff = random.choice([2, 3, 4, 5, 6])
    square_free_part = random.choice([2, 3, 5, 6, 7, 10])
    original_radicand = square_part_coeff**2 * square_free_part
    
    question_text = f"將 $\\sqrt{{{original_radicand}}}$ 化為最簡根式。"
    answer_radical = Radical(1, original_radicand)
    correct_answer = answer_radical.to_latex()
    
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": correct_answer}

def generate_rationalize_denominator_problem():
    """Generates a problem asking to rationalize the denominator."""
    num = random.randint(2, 10)
    
    if random.random() < 0.6: # c / sqrt(b)
        radicand = random.choice([2, 3, 5, 6, 7, 10, 11, 13, 15])
        while math.gcd(num, radicand) == radicand:
             radicand = random.choice([2, 3, 5, 6, 7, 10, 11, 13, 15])
        question_text = f"將 $\\frac{{{num}}}{{\\sqrt{{{radicand}}}}}$ 化為最簡根式。"
        answer_radical = Radical(Fraction(num, radicand), radicand)
    else: # c / (a * sqrt(b')) or c / sqrt(b')
        perfect_square = random.choice([4, 9])
        square_free = random.choice([2, 3, 5])
        radicand = perfect_square * square_free
        question_text = f"將 $\\frac{{{num}}}{{\\sqrt{{{radicand}}}}}$ 化為最簡根式。"
        simplified_coeff, simplified_rad = simplify_radicand(radicand)
        final_den = simplified_coeff * simplified_rad
        answer_radical = Radical(Fraction(num, final_den), simplified_rad)

    correct_answer = answer_radical.to_latex()
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": correct_answer}

def generate_simplify_fraction_decimal_radicand_problem():
    """Generates a problem with a fraction or decimal inside the radical."""
    if random.random() < 0.5: # Decimal
        den = random.choice([10, 100])
        num = random.randint(2, 80)
        while num % 10 == 0: num = random.randint(2, 80)
        dec_val = Fraction(num, den)
        dec_str = str(num/den)
        question_text = f"將 $\\sqrt{{{dec_str}}}$ 化為最簡根式。"
        num, den = dec_val.numerator, dec_val.denominator
    else: # Fraction
        den = random.choice([3, 5, 6, 7, 8, 12, 18, 20, 27, 28, 32])
        num = random.randint(1, 10)
        common = math.gcd(num, den)
        num //= common
        den //= common
        question_text = f"將 $\\sqrt{{\\frac{{{num}}}{{{den}}}}}$ 化為最簡根式。"
        
    answer_radical = Radical(Fraction(1, den), num * den)
    correct_answer = answer_radical.to_latex()
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": correct_answer}
    
def generate_identify_simplest_form_problem():
    """Generates a problem asking to identify simplest radical forms."""
    options = []
    correct_options_set = set()
    
    for _ in range(random.randint(2, 3)):
        radicand = random.choice([21, 26, 30, 33, 34, 35, 38, 39, 42, 46, 51])
        form_type = random.choice(['sqrt(n)', 'sqrt(n)/c'])
        if form_type == 'sqrt(n)':
            opt = f"{random.choice(['-', ''])}\\sqrt{{{radicand}}}"
        else: # 'sqrt(n)/c'
            den = random.randint(2, 9)
            opt = f"\\frac{{\\sqrt{{{radicand}}}}}{{{den}}}"
        options.append(f"${opt}$")
        correct_options_set.add(opt)
            
    num_incorrect = random.randint(3, 4)
    for _ in range(num_incorrect):
        incorrect_type = random.choice(['perfect_square', 'rad_in_den', 'fraction_in_rad', 'decimal_in_rad'])
        if incorrect_type == 'perfect_square':
            radicand = random.choice([4, 9, 25]) * random.choice([2, 3, 5])
            options.append(f"$\\sqrt{{{radicand}}}$")
        elif incorrect_type == 'rad_in_den':
            # FIX: Pre-calculate values to avoid complex nested f-strings
            n = random.randint(1, 9)
            coeff = random.randint(2, 5)
            r = random.choice([2, 3, 5, 7, 11])
            options.append(f"$\\frac{{{n}}}{{{coeff}\\sqrt{{{r}}}}}$")
        elif incorrect_type == 'fraction_in_rad':
            # FIX: Pre-calculate values
            n = random.randint(2, 10)
            d = random.randint(3, 15)
            options.append(f"$\\sqrt{{\\frac{{{n}}}{{{d}}}}}$")
        else: # decimal_in_rad
            # FIX: Pre-calculate values
            val = random.randint(2, 98) / 10.0
            options.append(f"$\\sqrt{{{val}}}$")

    random.shuffle(options)
    
    question_text = f"下列哪些是最簡根式？ (請將所有答案以半形逗號 , 分隔)<br>" + ", ".join(options)
    correct_answer = ", ".join(sorted(list(correct_options_set)))
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": correct_answer}

# --- Main Functions ---

def generate(level=1):
    """
    Generates a problem on basic properties of radical operations.
    """
    problem_types = [
        'multiplication', 'division', 'simplify', 'rationalize', 
        'simplify_frac_dec', 'identify'
    ]
    # Adjust weights based on importance or complexity if needed
    weights = [20, 15, 20, 20, 15, 10]
    problem_type = random.choices(problem_types, weights=weights, k=1)[0]

    if problem_type == 'multiplication':
        return generate_multiplication_problem()
    elif problem_type == 'division':
        return generate_division_problem()
    elif problem_type == 'simplify':
        return generate_simplify_problem()
    elif problem_type == 'rationalize':
        return generate_rationalize_denominator_problem()
    elif problem_type == 'simplify_frac_dec':
        return generate_simplify_fraction_decimal_radicand_problem()
    else: # 'identify'
        return generate_identify_simplest_form_problem()

def check(user_answer, correct_answer):
    """
    Checks the user's answer for radical expressions.
    """
    def normalize(s):
        return s.strip().replace('$', '').replace(' ', '')
    
    # Heuristic to detect multi-answer questions
    if ',' in correct_answer:
        # Sort parts to handle order difference
        user_parts = sorted([normalize(part) for part in user_answer.split(',')])
        correct_parts = sorted([normalize(part) for part in correct_answer.split(',')])
        is_correct = (user_parts == correct_parts)
    else:
        is_correct = (normalize(user_answer) == normalize(correct_answer))

    if is_correct:
        result_text = f"完全正確！答案是 ${correct_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer}$"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}