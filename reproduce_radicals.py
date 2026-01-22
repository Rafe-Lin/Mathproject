import sys
import os

# Add project root to path
sys.path.append(r"c:\Mathproject")

from skills.jh_數學2上_FourOperationsOfRadicals import generate

print("--- Generating 20 Questions ---")
for i in range(20):
    try:
        q = generate()
        print(f"[{i+1}] {q['question_text']}")
        if "1\sqrt" in q['question_text']:
            print("ERROR: Found explicit 1 before sqrt")
        if "$" in q['question_text']:
            # Check for multiple $ blocks that might split \times
            parts = q['question_text'].split('$')
            if len(parts) > 3: # means more than one pair of $...$ usually
                # Need to be careful. "$...$ ... $...$" is 3 parts (empty, math, text, math, empty) -> 5 parts
                # If we have "... $term1$ \times $term2$ ...", that's 2 pairs.
                pass
            
            # primitive check for \times outside
            if r"$\times" not in q['question_text'] and r"\times" in q['question_text'] and r"\times$" not in q['question_text']:
                 if r" \times " in q['question_text']: # Check if it is outside
                     # It's hard to parse regex for $..$ \times $..$ reliably without a parser, 
                     # but visually inspecting the output is best.
                     pass
    except Exception as e:
        print(f"ERROR: {e}")
