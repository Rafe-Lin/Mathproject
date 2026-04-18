
import os
import re

file_path = os.path.join('templates', 'index.html')
if not os.path.exists(file_path):
    print(f"[Error] File not found: {file_path}")
    exit()

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

print("Removing button with id='clear-canvas-button'...")

# Regex to find the button by ID
# Use flexible matching for attributes around the ID
pattern = r'<button[^>]*id="clear-canvas-button"[^>]*>.*?<\/button>'

content, count = re.subn(pattern, '', content, flags=re.DOTALL | re.IGNORECASE)

if count > 0:
    print(f"[OK] Removed {count} 'clear-canvas-button'.")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("[Success] Button removed.")
else:
    print("[Warning] Could not find 'clear-canvas-button' by ID.")
    print("Checking for alternative quoted IDs...")
    # Try single quotes
    pattern_sq = r"<button[^>]*id='clear-canvas-button'[^>]*>.*?<\/button>"
    content, count = re.subn(pattern_sq, '', content, flags=re.DOTALL | re.IGNORECASE)
    if count > 0:
        print(f"[OK] Removed {count} 'clear-canvas-button' (single quotes).")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    else:
        print("[Error] Still could not find the button.")
