
import sys
import os
import io
import contextlib
import random

# Add skills directory to path
sys.path.append(r"c:\Mathproject\skills")

try:
    import jh_數學2上_FactoringQuadraticsWithLeadingCoefficientNotOne as skill_lib
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)
except SyntaxError as e:
    print(f"Syntax Error in Module: {e}")
    sys.exit(1)

def run_verification():
    print("--- Verifying Generation ---")
    try:
        data = skill_lib.generate()
        print(f"Question: {data.get('question_text')}")
        print(f"Correct Answer: {data.get('correct_answer')}")
        
        # Verify A * C != 1 (Indirectly by checking A and C if possible, or just trusting the logic)
        # But we can verify format.
        
        print("\n--- Verifying Check Function ---")
        correct_ans = data.get('correct_answer')
        
        # Test 1: Exact Match
        res1 = skill_lib.check(correct_ans, correct_ans)
        print(f"Test 1 (Exact): {res1}")
        
        # Test 2: Commutative Match (if format allows)
        # We need to manually swap factors to test this.
        # Assuming format (ax+b)(cx+d)
        import re
        factors = re.findall(r'\(([^)]+)\)', correct_ans)
        if len(factors) == 2:
            swapped_ans = f"({factors[1]})({factors[0]})"
            res2 = skill_lib.check(swapped_ans, correct_ans)
            print(f"Test 2 (Swapped '{swapped_ans}'): {res2}")
        
        # Test 3: Wrong Answer
        res3 = skill_lib.check("(x+1)(x+1)", correct_ans)
        print(f"Test 3 (Wrong): {res3}")

    except Exception as e:
        print(f"Runtime Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_verification()
