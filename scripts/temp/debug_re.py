import re

def fix(match):
    # Mimic the logic
    content = match.group(1) # "Fraction: \frac" (literal backslash)
    # Return with replace logic
    # Try 1: replace \ with \\
    res = f'f"{content}"'.replace('\\', '\\\\')
    return res

code = r'f"Fraction: \frac"'
# Pattern
res = re.sub(r'f"(.*?)"', fix, code)

print(f"Original: {repr(code)}")
print(f"Result:   {repr(res)}")

# Test what happens if we return just \\f
def fix_raw(m): return r'\\frac'
res2 = re.sub(r'f"(.*?)"', fix_raw, code)
print(f"Result2:  {repr(res2)}")
