
import os
import re

file_path = os.path.join('templates', 'index.html')
if not os.path.exists(file_path):
    print(f"[Error] File not found: {file_path}")
    exit()

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

print("Upgrading Navbar HTML...")

# Target the existing navbar block
# Current: <div class="navbar">...</div>
# New: 
# <div class="navbar">
#    <h1>📐 Kumon Math AI</h1>
#    <div class="user-info">
#        <span>Hi, Student</span>
#        <a href="/logout">登出</a>
#    </div>
# </div>

new_navbar = """<div class="navbar">
        <h1>📐 Kumon Math AI</h1>
        <div class="user-info">
            <span>Hi, Student</span>
            <a href="/logout">登出</a>
        </div>
    </div>"""

# Regex to find the div with class="navbar" and its content
# We use a non-greedy dot match, hoping the navbar isn't too complex or nested deeply with other divs
pattern = r'<div class="navbar">.*?</div>'
match = re.search(pattern, content, flags=re.DOTALL)

if match:
    content = re.sub(pattern, new_navbar, content, count=1, flags=re.DOTALL)
    print("[OK] Navbar upgraded.")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
else:
    print("[Warning] Could not find specific navbar block to replace.")
    # Fallback: check if we just need to inject if it's missing (though we detected it earlier)
