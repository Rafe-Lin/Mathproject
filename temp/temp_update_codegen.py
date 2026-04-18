import re

# Read the original file
with open(r'd:\Python\Mathproject\core\code_generator.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Define the new section to insert
new_section = '''
    [CRITICAL PYTHON SYNTAX RULES - HIGHEST PRIORITY]
    4. **F-String LaTeX Escaping**:
       - When using f-strings (f"..."), you MUST double the curly braces for any LaTeX syntax.
       - BAD: f"The area is $x^{{2}}$" → Python SyntaxError: f-string: single '}}' is not allowed
       - GOOD: f"The area is $x^{{{{2}}}}$" → Correct
       - BAD: f"Solve $\\frac{{{{a}}}}{{{{b}}}}$" → SyntaxError
       - GOOD: f"Solve $\\frac{{{{{{a}}}}}}{{{{{{b}}}}}}$" → Correct
       
    5. **LaTeX Backslash Escaping**:
       - For LaTeX backslashes, ALWAYS use double backslashes (\\) in regular strings.
       - BAD: "\\circ", "\\triangle", "\\frac" → SyntaxWarning: invalid escape sequence
       - GOOD: "\\\\circ", "\\\\triangle", "\\\\frac" → Correct
       - In f-strings with LaTeX: Use quadruple backslashes for commands.
       - Example: f"Angle $\\\\\\\\angle ABC$" → Renders as $\\angle ABC$
       
    6. **No Full-Width Characters**:
       - Do NOT use full-width symbols like ？, ＋, ，, ： inside variable names or logic flow.
       - Full-width characters are ONLY allowed in Chinese comments or display strings.
       - BAD: if x ？ 0: → SyntaxError: invalid character
       - GOOD: if x > 0: → Correct

'''

# Insert before [SYNTAX GUARDRAILS] and renumber
updated = content.replace(
    '    [SYNTAX GUARDRAILS]\n    4. Template Markers:',
    new_section + '    [SYNTAX GUARDRAILS]\n    7. Template Markers:'
)

# Renumber subsequent items
updated = updated.replace('\n    5. CRITICAL LATEX', '\n    8. CRITICAL LATEX')
updated = updated.replace('\n    6. F-STRING', '\n    9. F-STRING')
updated = updated.replace('\n    7. NO NEWLINES', '\n    10. NO NEWLINES')
updated = updated.replace('\n    8. RANDOM RANGE', '\n    11. RANDOM RANGE')
updated = updated.replace('\n    9. NO EXTERNAL', '\n    12. NO EXTERNAL')

# Write back
with open(r'd:\Python\Mathproject\core\code_generator.py', 'w', encoding='utf-8') as f:
    f.write(updated)

print("Successfully updated code_generator.py with critical syntax rules!")
