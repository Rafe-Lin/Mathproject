import sys
import os

# Add project root to path
sys.path.append(r"d:\Python\Mathproject")

try:
    from skills import jh_數學1上_GeometryProblems as geo
    print("Module imported successfully.")
    
    # Generate Type 2 specifically? The generate function chooses randomly.
    # Let's loop until we get Type 2
    type_2_found = False
    for i in range(20):
        problem = geo.generate()
        q_text = problem['question_text']
        
        if "長方形" in q_text:
            type_2_found = True
            print(f"Type 2 Problem Found (Iteration {i}):")
            print(f"Question: {q_text}")
            print(f"Answer: {problem['answer']}")
            print(f"Correct Answer: {problem['correct_answer']}")
            
            # Verify Constants in Text
            if r"\overline{AF} = 10" in q_text and r"\overline{AB} = 8" in q_text:
                print("PASS: Constants Verified.")
            else:
                print("FAIL: Constants Mismatch.")
            
            # Verify Image
            if len(problem['image_base64']) > 1000:
                print("PASS: Image Generated.")
            else:
                print("FAIL: Image Empty.")
                
            break
            
    if not type_2_found:
        print("WARNING: Type 2 not generated in 20 tries (unlucky or bug).")

except Exception as e:
    print(f"CRITICAL ERROR: {e}")
    import traceback
    traceback.print_exc()
