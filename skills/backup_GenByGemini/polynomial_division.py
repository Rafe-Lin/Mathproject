import random

def generate_polynomial_division_question():
    # Generate a simple quadratic polynomial and a linear divisor
    a = random.randint(1, 3)
    b = random.randint(-5, 5)
    c = random.randint(-9, 9)
    
    divisor_root = random.randint(-3, 3) # x - divisor_root
    
    # Polynomial: ax^2 + bx + c
    # Divisor: x - divisor_root
    
    # Using synthetic division or direct calculation
    # (ax^2 + bx + c) / (x - r) = (ax + (b+ar)) with remainder (c+r(b+ar))
    
    quotient_coeff_x = a
    quotient_constant = b + a * divisor_root
    remainder = c + divisor_root * (b + a * divisor_root)
    
    poly_text = f"{a}x^2 + {b}x + {c}" if b >= 0 and c >= 0 else f"{a}x^2 {b}x {c}" if b < 0 and c < 0 else f"{a}x^2 {b}x + {c}" if b < 0 else f"{a}x^2 + {b}x {c}"
    divisor_text = f"x - {abs(divisor_root)}" if divisor_root > 0 else f"x + {abs(divisor_root)}"
    
    question_text = f"求多項式 {poly_text} 除以 {divisor_text} 的餘式。"
    
    return {
        "text": question_text,
        "answer": str(remainder),
        "validation_function_name": None
    }
