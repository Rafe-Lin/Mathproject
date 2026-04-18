import random
import math
from fractions import Fraction
import re

# --- Exact Number Representation for LaTeX Output ---
class ExactNum:
    """
    Represents numbers exactly as a rational coefficient multiplied by sqrt(1), sqrt(2), or sqrt(3).
    Format: (rational_coeff, sqrt_val) where sqrt_val in {1, 2, 3}
    e.g., 2 -> (Fraction(2,1), 1)
          sqrt(2) -> (Fraction(1,1), 2)
          -sqrt(3)/2 -> (Fraction(-1,2), 3)
          2*sqrt(3) -> (Fraction(2,1), 3)
    """
    def __init__(self, val, sqrt_val=1):
        if isinstance(val, (int, Fraction)):
            self.rational_coeff = Fraction(val)
            self.sqrt_val = 1
        elif isinstance(val, tuple) and len(val) == 2: # (rational_coeff, sqrt_val)
            self.rational_coeff = Fraction(val[0])
            self.sqrt_val = val[1]
        elif isinstance(val, ExactNum):
            self.rational_coeff = val.rational_coeff
            self.sqrt_val = val.sqrt_val
        else:
            raise ValueError(f"Unsupported type for ExactNum init: {type(val)}")
        
        if self.sqrt_val not in [1, 2, 3]:
            raise ValueError(f"Unsupported sqrt_val for ExactNum: {self.sqrt_val}. Must be 1, 2, or 3.")
        
        # If rational_coeff is 0, the whole number is 0, so sqrt_val should be 1
        if self.rational_coeff == 0:
            self.sqrt_val = 1
            
    def _ensure_exactnum(self, other):
        if isinstance(other, (int, Fraction)):
            return ExactNum(other)
        elif isinstance(other, ExactNum):
            return other
        raise ValueError(f"Operation with unsupported type: {type(other)}")

    def __mul__(self, other):
        other = self._ensure_exactnum(other)
        
        if self.sqrt_val == 1 and other.sqrt_val == 1:
            return ExactNum(self.rational_coeff * other.rational_coeff)
        elif self.sqrt_val == 1: # self is rational, other has sqrt
            return ExactNum((self.rational_coeff * other.rational_coeff, other.sqrt_val))
        elif other.sqrt_val == 1: # self has sqrt, other is rational
            return ExactNum((self.rational_coeff * other.rational_coeff, self.sqrt_val))
        elif self.sqrt_val == other.sqrt_val: # both have same sqrt, e.g., sqrt(2)*sqrt(2)
            new_rational = self.rational_coeff * other.rational_coeff * self.sqrt_val
            return ExactNum(new_rational)
        else: # Different sqrt bases, e.g., sqrt(2)*sqrt(3).
            # For this context, these products are not typically expected as simple ExactNum results.
            # E.g., sqrt(2)*sqrt(3) = sqrt(6) is not in our ExactNum type {1,2,3}
            # So, raising an error or returning a float approximation might be necessary if it occurs.
            # But with careful problem generation, it should be avoided.
            raise NotImplementedError(f"Multiplication of ExactNum with different sqrt_val not supported: {self}, {other}")

    def __rmul__(self, other):
        return self.__mul__(other)
    
    def __add__(self, other):
        other = self._ensure_exactnum(other)
        
        if self.sqrt_val == other.sqrt_val:
            return ExactNum((self.rational_coeff + other.rational_coeff, self.sqrt_val))
        elif self.rational_coeff == 0: # Adding 0 + x
            return other
        elif other.rational_coeff == 0: # Adding x + 0
            return self
        else:
            # Addition of terms with different sqrt_val (e.g., 2 + sqrt(3))
            # cannot be simplified into a single ExactNum.
            # For problem generation, we should avoid these as direct answers.
            # If they occur in intermediate steps, they must combine to a single ExactNum
            # or be handled by an outer structure that can represent sums.
            raise NotImplementedError(f"Addition of ExactNum with different sqrt_val not supported: {self}, {other}")

    def __radd__(self, other):
        return self.__add__(other)

    def __neg__(self):
        return ExactNum((-self.rational_coeff, self.sqrt_val))
    
    def __sub__(self, other):
        return self + (-self._ensure_exactnum(other))

    def __truediv__(self, other):
        other = self._ensure_exactnum(other)
        
        if other.rational_coeff == 0:
            raise ZeroDivisionError("Cannot divide by zero ExactNum")
        
        if self.sqrt_val == 1 and other.sqrt_val == 1: # rational / rational
            return ExactNum(self.rational_coeff / other.rational_coeff)
        elif self.sqrt_val == other.sqrt_val: # (a*sqrt_b) / (c*sqrt_b) = a/c
            return ExactNum(self.rational_coeff / other.rational_coeff)
        elif self.sqrt_val == 1 and other.sqrt_val in [2,3]: # rational / (c*sqrt_b) -> rationalize
            new_rational_coeff = self.rational_coeff / other.rational_coeff / other.sqrt_val
            return ExactNum((new_rational_coeff, other.sqrt_val)) # e.g., 1 / sqrt(2) = sqrt(2)/2
        elif self.sqrt_val in [2,3] and other.sqrt_val == 1: # (a*sqrt_b) / c
            new_rational_coeff = self.rational_coeff / other.rational_coeff
            return ExactNum((new_rational_coeff, self.sqrt_val))
        else:
            raise NotImplementedError(f"Division of ExactNum with different sqrt_val not supported: {self}, {other}")

    def __pow__(self, power):
        if not isinstance(power, int):
            raise NotImplementedError("Only integer powers are supported for ExactNum")
        
        if power == 0: return ExactNum(1)
        if power == 1: return self
        
        result = ExactNum(1)
        temp = self
        if power < 0:
            temp = ExactNum(1) / self
            power = -power
        
        for _ in range(power):
            result *= temp
        return result

    def to_latex(self):
        if self.rational_coeff == 0:
            return "0"

        sign = ""
        abs_rational = abs(self.rational_coeff)
        
        if self.rational_coeff < 0:
            sign = "-"
        
        rational_str = ""
        if abs_rational == 1 and self.sqrt_val != 1: # For \\sqrt{2} instead of 1\\sqrt{2}
            rational_str = ""
        elif abs_rational.denominator == 1:
            rational_str = str(abs_rational.numerator)
        else:
            rational_str = fr"\\frac{{{abs_rational.numerator}}}{{{abs_rational.denominator}}}"
        
        sqrt_str = ""
        if self.sqrt_val == 2:
            sqrt_str = r"\\sqrt{{2}}"
        elif self.sqrt_val == 3:
            sqrt_str = r"\\sqrt{{3}}"
        elif self.sqrt_val == 1: # No sqrt part
            sqrt_str = ""
            
        if sqrt_str == "":
            return f"{sign}{rational_str}"
        elif rational_str == "": # Just sqrt, like \\sqrt{2}
            return f"{sign}{sqrt_str}"
        else:
            return f"{sign}{rational_str}{sqrt_str}"

    def to_float(self):
        base_val = 1.0
        if self.sqrt_val == 2: base_val = math.sqrt(2.0)
        elif self.sqrt_val == 3: base_val = math.sqrt(3.0)
        
        return float(self.rational_coeff) * base_val

    def __eq__(self, other):
        if isinstance(other, (int, float, Fraction)):
            return abs(self.to_float() - float(other)) < 1e-9
        elif isinstance(other, ExactNum):
            return abs(self.to_float() - other.to_float()) < 1e-9
        return False

    def __lt__(self, other):
        if isinstance(other, (int, float, Fraction)):
            return self.to_float() < float(other)
        elif isinstance(other, ExactNum):
            return self.to_float() < other.to_float()
        return False

    def __gt__(self, other):
        return not (self == other or self < other)

    def __le__(self, other):
        return self < other or self == other

    def __ge__(self, other):
        return self > other or self == other

    def __str__(self):
        return self.to_latex()
    
    def __repr__(self):
        return f"ExactNum({self.rational_coeff}, sqrt_val={self.sqrt_val})"


# Lookup table for (cos_theta, sin_theta) as ExactNum
# Key: angle in degrees
# Value: (ExactNum(cos_val), ExactNum(sin_val))
ANGLE_TRIG_VALUES = {
    0:    (ExactNum(1),                   ExactNum(0)),
    30:   (ExactNum(Fraction(1,2), 3),    ExactNum(Fraction(1,2), 1)), # (\\sqrt{3}/2, 1/2)
    45:   (ExactNum(Fraction(1,2), 2),    ExactNum(Fraction(1,2), 2)), # (\\sqrt{2}/2, \\sqrt{2}/2)
    60:   (ExactNum(Fraction(1,2), 1),    ExactNum(Fraction(1,2), 3)), # (1/2, \\sqrt{3}/2)
    90:   (ExactNum(0),                   ExactNum(1)),
    120:  (ExactNum(Fraction(-1,2), 1),   ExactNum(Fraction(1,2), 3)), # (-1/2, \\sqrt{3}/2)
    135:  (ExactNum(Fraction(-1,2), 2),   ExactNum(Fraction(1,2), 2)), # (-\\sqrt{2}/2, \\sqrt{2}/2)
    150:  (ExactNum(Fraction(-1,2), 3),   ExactNum(Fraction(1,2), 1)), # (-\\sqrt{3}/2, 1/2)
    180:  (ExactNum(-1),                  ExactNum(0)),
    210:  (ExactNum(Fraction(-1,2), 3),   ExactNum(Fraction(-1,2), 1)), # (-\\sqrt{3}/2, -1/2)
    225:  (ExactNum(Fraction(-1,2), 2),   ExactNum(Fraction(-1,2), 2)), # (-\\sqrt{2}/2, -\\sqrt{2}/2)
    240:  (ExactNum(Fraction(-1,2), 1),   ExactNum(Fraction(-1,2), 3)), # (-1/2, -\\sqrt{3}/2)
    270:  (ExactNum(0),                   ExactNum(-1)),
    300:  (ExactNum(Fraction(1,2), 1),    ExactNum(Fraction(-1,2), 3)), # (1/2, -\\sqrt{3}/2)
    315:  (ExactNum(Fraction(1,2), 2),    ExactNum(Fraction(-1,2), 2)), # (\\sqrt{2}/2, -\\sqrt{2}/2)
    330:  (ExactNum(Fraction(1,2), 3),    ExactNum(Fraction(-1,2), 1)), # (\\sqrt{3}/2, -1/2)
}

def generate_polar_to_rectangular():
    """
    生成「極坐標轉直角坐標」題目。
    給定 [r, theta]，求 (x, y)。
    """
    # Choose r to be an even integer for nicer fractions with 1/2 or sqrt(3)/2
    r_val = random.choice([2, 4, 6, 8])
    theta_deg = random.choice(list(ANGLE_TRIG_VALUES.keys()))

    cos_theta_exact, sin_theta_exact = ANGLE_TRIG_VALUES[theta_deg]

    x_exact = ExactNum(r_val) * cos_theta_exact
    y_exact = ExactNum(r_val) * sin_theta_exact

    question_text = fr"已知 $P$ 點的極坐標為 $[{r_val}, {theta_deg}°]$，求其直角坐標。"
    correct_answer = fr"$({x_exact.to_latex()}, {y_exact.to_latex()})$"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "problem_type": "polar_to_rectangular"
    }

def generate_rectangular_to_polar():
    """
    生成「直角坐標轉極坐標」題目。
    給定 (x, y)，求 [r, theta]。
    為了確保答案「漂亮」，我們反向生成：先選一個 r 和 theta，計算出 (x, y)，然後用 (x, y) 作為題目。
    """
    r_base = random.choice([1, 2, 3, 4, 5])
    theta_deg_base = random.choice(list(ANGLE_TRIG_VALUES.keys()))

    cos_theta_exact, sin_theta_exact = ANGLE_TRIG_VALUES[theta_deg_base]

    x_exact = ExactNum(r_base) * cos_theta_exact
    y_exact = ExactNum(r_base) * sin_theta_exact

    # Format x_exact and y_exact for the question
    x_latex = x_exact.to_latex()
    y_latex = y_exact.to_latex()

    question_text = fr"已知 $P$ 點的直角坐標為 $({x_latex}, {y_latex})$，求其極坐標。"
    correct_answer = fr"$[{r_base}, {theta_deg_base}°]$"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "problem_type": "rectangular_to_polar"
    }

def generate(level=1):
    """
    生成「直角坐標與極坐標轉換」相關題目。
    """
    problem_type = random.choice(['polar_to_rectangular', 'rectangular_to_polar'])
    
    if problem_type == 'polar_to_rectangular':
        return generate_polar_to_rectangular()
    else:
        return generate_rectangular_to_polar()


def _str_to_float_heuristic(s):
    """
    Helper function to convert a string representing a number (possibly with sqrt2/sqrt3 or fractions) to float.
    This is a basic heuristic and not a full math parser.
    """
    s = s.strip().replace(" ", "") # Remove spaces
    if r"\\sqrt{2}" in s:
        coeff_str = s.replace(r"\\sqrt{2}", "")
        if coeff_str == "" or coeff_str == "+": coeff_val = 1
        elif coeff_str == "-": coeff_val = -1
        else: coeff_val = float(Fraction(coeff_str))
        return coeff_val * math.sqrt(2)
    elif r"\\sqrt{3}" in s:
        coeff_str = s.replace(r"\\sqrt{3}", "")
        if coeff_str == "" or coeff_str == "+": coeff_val = 1
        elif coeff_str == "-": coeff_val = -1
        else: coeff_val = float(Fraction(coeff_str))
        return coeff_val * math.sqrt(3)
    else:
        # Handles integers and simple fractions like "1/2" or "-3"
        return float(Fraction(s)) 

def parse_rectangular_answer(answer_str):
    """Parses a string like "(2, -2\\sqrt{3})" into (float_x, float_y)"""
    answer_str = answer_str.strip().replace('$', '').replace('(', '').replace(')', '')
    # Replace LaTeX sqrt format with simplified string for heuristic parsing
    
    parts = answer_str.split(',')
    if len(parts) != 2:
        return None, None
    
    try:
        user_x = _str_to_float_heuristic(parts[0])
        user_y = _str_to_float_heuristic(parts[1])
        return user_x, user_y
    except (ValueError, ZeroDivisionError, TypeError):
        return None, None

def parse_polar_answer(answer_str):
    """Parses a string like "[2, 225°]" into (float_r, float_theta)"""
    answer_str = answer_str.strip().replace('$', '').replace('[', '').replace(']', '').replace('°', '')
    parts = answer_str.split(',')
    if len(parts) != 2:
        return None, None
    
    try:
        user_r = float(Fraction(parts[0].strip()))
        user_theta = float(Fraction(parts[1].strip()))
        return user_r, user_theta
    except (ValueError, ZeroDivisionError, TypeError):
        return None, None

def check(user_answer, correct_answer_dict):
    """
    檢查答案是否正確。
    correct_answer_dict 包含 'correct_answer' (string) 和 'problem_type'.
    """
    problem_type = correct_answer_dict['problem_type']
    correct_answer_str = correct_answer_dict['correct_answer']
    is_correct = False
    feedback = ""
    tolerance = 1e-6 # For float comparisons

    if problem_type == "polar_to_rectangular":
        # Correct answer is like $(x, y)$
        # Extract x and y from the correct_answer_str using _str_to_float_heuristic
        correct_x_float, correct_y_float = parse_rectangular_answer(correct_answer_str)
        user_x, user_y = parse_rectangular_answer(user_answer)
        
        if user_x is not None and user_y is not None and correct_x_float is not None and correct_y_float is not None:
            if abs(user_x - correct_x_float) < tolerance and abs(user_y - correct_y_float) < tolerance:
                is_correct = True
        
        if is_correct:
            feedback = fr"完全正確！答案是 {correct_answer_str}。"
        else:
            feedback = fr"答案不正確。正確答案應為：{correct_answer_str}"

    elif problem_type == "rectangular_to_polar":
        # Correct answer is like $[r, theta°]$
        correct_r, correct_theta = parse_polar_answer(correct_answer_str)
        user_r, user_theta = parse_polar_answer(user_answer)

        if user_r is not None and user_theta is not None and correct_r is not None and correct_theta is not None:
            # Check r value
            r_match = abs(user_r - correct_r) < tolerance
            
            # Check theta value, considering equivalence (e.g., theta + 360n)
            # Normalize angles to [0, 360) for comparison
            user_theta_norm = (user_theta % 360 + 360) % 360
            correct_theta_norm = (correct_theta % 360 + 360) % 360
            
            theta_match_primary = abs(user_theta_norm - correct_theta_norm) < tolerance

            # Check for [-r, theta+180] equivalence if r values are opposite
            # The problem example implies r >= 0. For simplicity, assume user answers with r >= 0.
            theta_match_secondary = False
            if abs(user_r + correct_r) < tolerance: # if user_r is approx -correct_r
                user_theta_shifted = (user_theta_norm + 180) % 360
                theta_match_secondary = abs(user_theta_shifted - correct_theta_norm) < tolerance
                # If a negative r was entered and the angle matches with a 180-degree shift,
                # then consider the magnitude of r correct.
                if theta_match_secondary:
                    r_match = True # The magnitude of r is considered correct for the context.
            
            if r_match and (theta_match_primary or theta_match_secondary):
                 is_correct = True
        
        if is_correct:
            feedback = fr"完全正確！答案是 {correct_answer_str}。"
        else:
            feedback = fr"答案不正確。正確答案應為：{correct_answer_str}"
    
    return {"correct": is_correct, "result": feedback, "next_question": True}