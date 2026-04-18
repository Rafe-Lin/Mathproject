
import sys
import os

# Add the skills directory to path
sys.path.append(r"c:\Mathproject\skills")

try:
    import jh_數學1下_WordProblems
    print("Import successful.")
    
    # Run generate multiple times to hit all branches
    for i in range(20):
        print(f"Iteration {i}")
        res = jh_數學1下_WordProblems.generate()
        # print(res['question_text'])
        
    print("Reference check:")
    jh_數學1下_WordProblems.check("10", "10")
    
    print("All good.")

except Exception as e:
    print(f"CRASH DETECTED: {e}")
    import traceback
    traceback.print_exc()
