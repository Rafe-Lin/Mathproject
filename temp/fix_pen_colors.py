import os

file_path = os.path.join('templates', 'index.html')
if not os.path.exists(file_path):
    print("Error: templates/index.html not found")
    exit()

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

print("Restoring pen color visibility...")

# CSS fix to specifically target the pen buttons based on their onclick attribute
# Since we cannot change HTML, we use attribute selectors.
# black: #2c3e50 (default in JS) or 'black'
# red: #e74c3c
# blue: #0066cc
# green: #009933

css_fix = """
    <style>
    /* === FIX: Restore Pen Colors === */
    /* Target buttons by their onclick content to avoid changing HTML */
    
    /* Black Pen */
    button.tool-btn[onclick*="'black'"] {
        color: black !important;
        border-color: #2c3e50 !important;
    }
    button.tool-btn[onclick*="'black'"]:hover,
    button.tool-btn[onclick*="'black'"].active {
        background-color: #2c3e50 !important;
        color: white !important;
    }

    /* Red Pen */
    button.tool-btn[onclick*="'#e74c3c'"] {
        color: #e74c3c !important;
        border-color: #e74c3c !important;
    }
    button.tool-btn[onclick*="'#e74c3c'"]:hover,
    button.tool-btn[onclick*="'#e74c3c'"].active {
        background-color: #e74c3c !important;
        color: white !important;
    }

    /* Blue Pen */
    button.tool-btn[onclick*="'#0066cc'"] {
        color: #0066cc !important;
        border-color: #0066cc !important;
    }
    button.tool-btn[onclick*="'#0066cc'"]:hover,
    button.tool-btn[onclick*="'#0066cc'"].active {
        background-color: #0066cc !important;
        color: white !important;
    }

    /* Green Pen */
    button.tool-btn[onclick*="'#009933'"] {
        color: #009933 !important;
        border-color: #009933 !important;
    }
    button.tool-btn[onclick*="'#009933'"]:hover,
    button.tool-btn[onclick*="'#009933'"].active {
        background-color: #009933 !important;
        color: white !important;
    }
    </style>
"""

# Append to the end of the file (after other styles)
if "</body>" in content:
    content = content.replace("</body>", css_fix + "\n</body>")
    print("Injected pen color CSS fix.")
else:
    content += css_fix
    print("Appended pen color CSS fix to end of file.")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Pen colors restored successfully.")
