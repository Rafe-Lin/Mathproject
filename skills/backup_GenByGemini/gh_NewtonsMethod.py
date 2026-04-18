import random
import math

# Use a small constant for floating point comparisons during iteration
EPSILON_CONVERGENCE = 1e-10
MAX_ITERATIONS = 100

def generate(level=1):
    """
    生成「牛頓法」相關題目。
    """
    problem_type = random.choice(['cubic_equation', 'square_root_approximation'])
    
    if problem_type == 'cubic_equation':
        return generate_cubic_equation_problem(level)
    else: # square_root_approximation
        return generate_square_root_problem(level)

def solve_newton_method(f, f_prime, x0, precision_digits, max_iter=MAX_ITERATIONS):
    """
    Applies Newton's method to find a root.
    f: the function
    f_prime: the derivative of the function
    x0: initial guess
    precision_digits: number of decimal places for the final answer
    """
    x_current = float(x0)
    
    for _ in range(max_iter):
        f_val = f(x_current)
        f_prime_val = f_prime(x_current)

        # Handle division by zero or very small derivative, which leads to instability
        if abs(f_prime_val) < EPSILON_CONVERGENCE * 100: 
            return None # Indicate failure to converge reliably

        x_next = x_current - f_val / f_prime_val

        # Check for convergence
        if abs(x_next - x_current) < EPSILON_CONVERGENCE:
            break
        
        x_current = x_next
    else: # Loop finished without breaking, likely did not converge within max_iter
        return None 

    # Determine the answer based on the example's floor-like logic for "accurate to N decimal places"
    N = precision_digits
    factor = 10**N
    
    # Calculate the lower bound of the N-decimal interval
    candidate_lower = math.floor(x_current * factor) / factor
    
    # Calculate the upper bound of the N-decimal interval
    candidate_upper = candidate_lower + (1.0 / factor) 
    
    # Evaluate the function at the candidate bounds
    f_lower = f(candidate_lower)
    f_upper = f(candidate_upper)
    
    # If the lower candidate is essentially the root (f(x) is very close to 0)
    if math.isclose(f_lower, 0.0, abs_tol=EPSILON_CONVERGENCE):
        return "{:.{}f}".format(candidate_lower, N)
    
    # Following the example: "因 f(1.3646) < 0 且 f(1.3647) > 0，故實根介於1.3646與1.3647之間。所求近似值準確到小數點以下第四位為1.3646。"
    # This implies that if the root lies between candidate_lower and candidate_upper, and f changes sign,
    # then candidate_lower is the chosen approximation. This works for monotonic functions.
    if f_lower * f_upper < 0:
        return "{:.{}f}".format(candidate_lower, N)
    else:
        # This branch should ideally not be hit with well-behaved problems and good convergence.
        # It implies the root isn't strictly between candidate_lower and candidate_upper in the expected way.
        # As a robust fallback, if bracketing fails, we return the converged value rounded.
        # This might deviate from the exact example logic in very rare edge cases but is numerically sound.
        return "{:.{}f}".format(x_current, N)

def find_root_interval(f, start_range, end_range, step=0.5):
    """
    Finds an interval [L, R] where f(L) and f(R) have opposite signs, guaranteeing a root.
    """
    current_x = start_range
    while current_x <= end_range:
        next_x = current_x + step
        # Ensure next_x doesn't overshoot end_range for precise boundary checks
        if next_x > end_range:
            next_x = end_range
        
        # Check for sign change
        if f(current_x) * f(next_x) < 0:
            return current_x, next_x
        
        # Break loop if current_x reaches end_range to prevent potential infinite loop if step is tiny
        if current_x == end_range: 
            break
        current_x = next_x
    return None, None # No sign change found in range

def generate_cubic_equation_problem(level):
    # Equation form: f(x) = x^3 + b x + c = 0
    # Derivative form: f'(x) = 3x^2 + b
    
    a = 1
    # 'b' coefficient chosen to ensure f'(x) > 0 for all real x, guaranteeing monotonicity and single real root.
    b = random.randint(2, 6) 
    c = random.randint(-10, 10)
    
    # Avoid trivial cases like c=0 (x(x^2+b)=0 -> x=0 is a root)
    # Also, add a simple heuristic to avoid integer roots, making approximation non-trivial.
    while c == 0 or (abs(c) % (a + b + 1) == 0 and abs(a+b+c) < 20):
        c = random.randint(-10, 10)

    # Define the function and its derivative using lambda expressions
    f = lambda x: a*x**3 + b*x + c
    f_prime = lambda x: 3*a*x**2 + b

    # Find an initial guess x0 by searching for a sign change in f(x)
    # Search in a reasonable range (e.g., -3 to 3)
    x_lower, x_upper = find_root_interval(f, -3.0, 3.0, step=0.5)

    if x_lower is None:
        # If no root interval found (e.g., all roots outside range or problem design leads to no real root), regenerate.
        return generate_cubic_equation_problem(level)
    
    x0 = (x_lower + x_upper) / 2.0 # Midpoint of the interval as initial guess

    # Set precision based on level, default to 4 decimal places
    precision_digits = 4 if level == 1 else random.choice([3, 4, 5])

    correct_ans_str = solve_newton_method(f, f_prime, x0, precision_digits)

    if correct_ans_str is None:
        # If Newton's method failed to converge reliably for this setup, retry.
        return generate_cubic_equation_problem(level)

    # Construct the question text with proper LaTeX formatting and variable substitution
    if c < 0:
        question_text = (
            f"試以牛頓法求方程式 $r{{x}}^{{3}} + {b}r{{x}} - {abs(c)} = 0$ 實根的近似值，"
            f"並準確到小數點以下第{precision_digits}位。"
        )
    else: # c > 0
        question_text = (
            f"試以牛頓法求方程式 $r{{x}}^{{3}} + {b}r{{x}} + {c} = 0$ 實根的近似值，"
            f"並準確到小數點以下第{precision_digits}位。"
        )
    
    return {
        "question_text": question_text,
        "answer": correct_ans_str, # Store the answer as a string
        "correct_answer": correct_ans_str # Store the correct answer as a string
    }

def generate_square_root_problem(level):
    # Equation form: f(x) = x^2 - k = 0 (to find sqrt(k))
    # Derivative form: f'(x) = 2x
    
    k = random.randint(2, 20)
    # Avoid perfect squares for k, so the root is irrational and requires approximation.
    while int(math.sqrt(k))**2 == k:
        k = random.randint(2, 20)

    f = lambda x: x**2 - k
    f_prime = lambda x: 2*x

    # Determine an initial guess x0.
    # The positive square root of k is between floor(sqrt(k)) and ceil(sqrt(k)).
    lower_int_sqrt = math.floor(math.sqrt(k))
    
    # Ensure initial guess x0 is positive, as f_prime(0) is zero and causes division by zero.
    # x0 is chosen within a reasonable interval around the root.
    x0_start = max(0.1, lower_int_sqrt - 0.5) 
    x0_end = lower_int_sqrt + 1.5
    
    # Ensure x0_start <= x0_end for random.uniform
    if x0_start >= x0_end:
        x0_end = x0_start + 1.0 # Adjust if necessary, for very small k
    
    x0 = random.uniform(x0_start, x0_end) 
    
    # Set precision based on level, default to 4 decimal places
    precision_digits = 4 if level == 1 else random.choice([3, 4, 5])

    correct_ans_str = solve_newton_method(f, f_prime, x0, precision_digits)

    if correct_ans_str is None:
        # If Newton's method failed to converge for this setup, retry.
        return generate_square_root_problem(level)
    
    question_text = (
        f"試以牛頓法求方程式 $r{{x}}^{{2}} = {k}$ 實根的近似值，"
        f"並準確到小數點以下第{precision_digits}位。"
    )
    
    return {
        "question_text": question_text,
        "answer": correct_ans_str,
        "correct_answer": correct_ans_str
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    
    is_correct = False
    result_text = ""

    try:
        user_float = float(user_answer)
        correct_float = float(correct_answer)
        
        # Determine the required precision from the format of the correct_answer string
        if '.' in correct_answer:
            precision_digits = len(correct_answer.split('.')[-1])
        else:
            precision_digits = 0 # If correct_answer is an integer (e.g., "2"), precision is 0
        
        # Format the user's answer to the *exact* required precision for comparison.
        # This ensures the user's answer not only is numerically correct but also formatted as expected.
        user_answer_formatted = "{:.{}f}".format(user_float, precision_digits)
        
        if user_answer_formatted == correct_answer:
            is_correct = True
    except ValueError:
        # If the user's answer cannot be converted to a float, it's incorrect.
        pass

    if is_correct:
        result_text = f"完全正確！答案是 ${correct_answer}$。"
    else:
        result_text = f"答案不正確。正確答案應為：${correct_answer}$"
    
    return {"correct": is_correct, "result": result_text, "next_question": True}