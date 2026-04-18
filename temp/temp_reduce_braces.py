# -*- coding: utf-8 -*-

# Read the file
with open(r'd:\Python\Mathproject\core\code_generator.py', 'r', encoding='utf-8') as f:
    content = f.read()

# The user wants us to use {{{{ }}}} (4 braces) in the CORRECT examples
# Currently we have {{{{{{{{ }}}}}}}} (8 braces) because I doubled them in the last step.

# Let's replace 8 braces with 4 braces in the specific lines.
# We can just do a global replace of 8 braces with 4 braces, 
# assuming 8 braces don't appear elsewhere (they shouldn't).

if '{{{{{{{{' in content:
    content = content.replace('{{{{{{{{', '{{{{')
    content = content.replace('}}}}}}}}', '}}}}')
    print("[OK] Replaced 8 braces with 4 braces")
else:
    print("[WARN] Could not find 8 braces. Checking for 4 braces...")
    if '{{{{' in content:
        print("[INFO] Found 4 braces. Maybe already correct?")
    else:
        print("[WARN] Found neither 8 nor 4 braces.")

# Also check for the specific example the user mentioned
# ❌ WRONG (What NOT to write): f"Ans: $x^{{2}}$"
# In source this should be: f"Ans: $x^{{{{2}}}}$" (4 braces -> 2 braces output)
# Currently it is probably: f"Ans: $x^{{{{2}}}}$" (4 braces) -> 2 braces output
# Wait, my previous script doubled EVERYTHING.
# So "WRONG" example `f"Ans: $x^{{2}}$"` (2 braces) became `f"Ans: $x^{{{{2}}}}$" (4 braces).
# This renders to `f"Ans: $x^{{2}}$"`. (SyntaxError).
# This seems correct for "WRONG" example.

# The user says:
# ❌ WRONG (What NOT to write): f"Ans: $x^{{2}}$"
# This implies they want the "WRONG" example to show 2 braces to AI.
# So source should have 4 braces.
# My file has 4 braces for WRONG example.
# So "WRONG" example is fine.

# The "CORRECT" example:
# ✅ CORRECT (What to write): f"Ans: $x^{{{{2}}}}$"
# User wants 4 braces in source.
# My file has 8 braces.
# So I need to reduce 8 to 4.

# Write back to file
with open(r'd:\Python\Mathproject\core\code_generator.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n[SUCCESS] Updated prompt braces according to user instruction!")
