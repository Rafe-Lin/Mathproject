# -*- coding: utf-8 -*-

# Read the file
with open(r'd:\Python\Mathproject\core\code_generator.py', 'r', encoding='utf-8') as f:
    content = f.read()

# We need to reduce the braces in WRONG examples from 4 to 2.
# This ensures WRONG renders as { } and CORRECT renders as {{ }}.

# 1. Fix Line 110: ❌ WRONG: f"Area is $x^{{{{2}}}}$"
if '❌ WRONG: f"Area is $x^{{{{2}}}}$"' in content:
    content = content.replace('❌ WRONG: f"Area is $x^{{{{2}}}}$"', '❌ WRONG: f"Area is $x^{{2}}$"')
    print("[OK] Fixed Line 110 WRONG example")

# 2. Fix Line 112: ❌ WRONG: f"Solve $\frac{{{{a}}}}{{{{b}}}}$"
# Note: regex might be safer but exact string match is fine if we are careful
if '❌ WRONG: f"Solve $\\frac{{{{a}}}}{{{{b}}}}$"' in content: # Check escaping
    # Try with single backslash in string literal
    pass

# Let's try a more generic replace for WRONG lines
lines = content.split('\n')
new_lines = []
for line in lines:
    if '❌ WRONG:' in line or 'NOT f"' in line:
        # Replace {{{{ with {{ and }}}} with }}
        # But only if it has 4 braces
        if '{{{{' in line:
            line = line.replace('{{{{', '{{').replace('}}}}', '}}')
            print("[OK] Reduced braces in a WRONG example line")
    new_lines.append(line)

content = '\n'.join(new_lines)

# Write back to file
with open(r'd:\Python\Mathproject\core\code_generator.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n[SUCCESS] Distinguished WRONG vs CORRECT examples!")
