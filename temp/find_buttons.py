
import os
import re

file_path = os.path.join('templates', 'index.html')
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

print("Scanning for buttons...")
buttons = re.findall(r'(<button.*?>.*?<\/button>)', content, re.DOTALL | re.IGNORECASE)

for i, btn in enumerate(buttons):
    # Normalize whitespace for printing
    display = ' '.join(btn.split()) 
    if len(display) > 100: display = display[:100] + "..."
    # Safe print
    try:
        print(f"{i}: {display}")
    except:
        print(f"{i}: [Complex Button]")
