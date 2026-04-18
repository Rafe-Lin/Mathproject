# -*- coding: utf-8 -*-

# Read the file
with open(r'd:\Python\Mathproject\core\code_generator.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix lines 115-117 where both parts became {{ (2 braces)
# We want the first part (CORRECT) to be {{{{ (4 braces)
# and the second part (WRONG) to be {{ (2 braces)

replacements = [
    ('* Exponents: f"$x^{{2}}$" NOT f"$x^{{2}}$"', '* Exponents: f"$x^{{{{2}}}}$" NOT f"$x^{{2}}$"'),
    ('* Subscripts: f"$a_{{1}}$" NOT f"$a_{{1}}$"', '* Subscripts: f"$a_{{{{1}}}}$" NOT f"$a_{{1}}$"'),
    ('* Fractions: f"$\\frac{{1}}{{2}}$" NOT f"$\\frac{{1}}{{2}}$"', '* Fractions: f"$\\frac{{{{1}}}}{{{{2}}}}$" NOT f"$\\frac{{1}}{{2}}$"')
]

# Note: The view showed `f"$x^{{2}}$"`. This means the file has `{{`.
# So my search string `f"$x^{{2}}$"` (which means `{{` in python string literal?)
# No, in python string literal `{{` is just `{{`.
# So I should search for `{{` in the file content.

for old, new in replacements:
    # We need to be careful with python string escaping in this script
    # The file content has `{{`.
    # My `old` string has `{{`.
    if old in content:
        content = content.replace(old, new)
        print(f"[OK] Fixed: {old[:30]}...")
    else:
        print(f"[WARN] Could not find: {old[:30]}...")
        # Debug: print what we found
        if "Exponents" in old:
            import re
            match = re.search(r'\* Exponents:.*', content)
            if match:
                print(f"Found instead: {match.group(0)}")

# Write back to file
with open(r'd:\Python\Mathproject\core\code_generator.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n[SUCCESS] Restored 4 braces in CORRECT examples!")
