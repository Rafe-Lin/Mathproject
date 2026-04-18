from core.code_generator import fix_code_syntax, validate_python_code
import re

test_cases = [
    # Case 1: Negative exponent in f-string
    ('f"Ans: $10^{-2}$"', "Ans: $10^{-2}$"),
    # Case 2: Negative variable exponent
    ('f"Ans: $10^{-n}$"', "Ans: $10^{-n}$"),
    # Case 3: Invalid escape sequence
    ('f"result: \\frac{1}{2}"', "result: \\frac{1}{2}"),
    # Case 4: Single brace in f-string (User prompt mentions standard issue)
    ('f"Ans: $10^{2}$"', "Ans: $10^{{2}}"), # Expecting fix to double braces?
]

print("Testing fix_code_syntax logic...")
for inp, description in test_cases:
    print(f"\n--- Test Case: {description} ---")
    print(f"Input: {inp}")
    try:
        fixed = fix_code_syntax(inp, error_msg="SyntaxError: f-string: single '}' is not allowed")
        print(f"Fixed: {fixed}")
        
        # Check basic validity (mocking since we don't assume full environment)
        # But we can emulate specific regex checks
    except Exception as e:
        print(f"Error: {e}")
